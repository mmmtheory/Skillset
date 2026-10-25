#!/usr/bin/env python3
"""Find design values written as literals instead of design tokens.

  python token_drift.py --tokens DESIGN.md src/
  python token_drift.py --tokens tokens.json --tokens theme.css src/components --json

Tokens come from any mix of:
  DESIGN.md        YAML front matter (colors, typography, rounded, spacing, components)
  *.css, *.scss    CSS custom properties (--name: value)
  *.json           DTCG tokens ($value, $type) or Style Dictionary (value)

Scanned files: .css .scss .less .html .jsx .tsx .js .ts .vue .svelte .astro
Literals checked: colours (hex, rgb, hsl), spacing, radius, font size and
line height in px or rem, and font families.

Each literal is labelled:
  hard-coded token  exact value of a token, typed instead of referenced
  near token        close to a token (colour within Delta E 5, length within 2 px)
  off-system        nothing close in the token set
  unknown token     var(--name) that no CSS token file defines (only when
                    a CSS token file was given)

Lines that define custom properties are token definitions and are skipped,
as are the token files themselves.

Exit status: 0 when nothing is found, 1 when anything is, 2 on bad input.
Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import tempfile
from pathlib import Path

SCAN_SUFFIXES = {".css", ".scss", ".less", ".html", ".jsx", ".tsx", ".js", ".ts", ".vue", ".svelte", ".astro"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "coverage", "vendor"}
GENERIC_FONTS = {"inherit", "initial", "unset", "sans-serif", "serif", "monospace", "system-ui",
                 "ui-sans-serif", "ui-serif", "ui-monospace", "cursive", "-apple-system",
                 "blinkmacsystemfont", "emoji", "math", "fangsong"}
NEAR_COLOUR = 5.0   # CIE76 Delta E
NEAR_PX = 2.0
REM_PX = 16.0

# ---------------------------------------------------------------- colours

HEX_RE = re.compile(r"(?<![\w&/-])#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b")
FUNC_RE = re.compile(r"\b(rgba?|hsla?)\(([^)]*)\)")


def parse_colour(text: str):
    text = text.strip().lower().strip("'\"")
    if text.startswith("#"):
        h = text[1:]
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        if len(h) not in (6, 8) or not re.fullmatch(r"[0-9a-f]+", h):
            return None
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        a = round(int(h[6:8], 16) / 255, 3) if len(h) == 8 else 1.0
        return (r, g, b, a)
    m = re.fullmatch(r"(rgba?|hsla?)\((.*)\)", text)
    if not m:
        return None
    kind, inner = m.groups()
    parts = [p for p in re.split(r"[\s,/]+", inner.strip()) if p]
    if len(parts) not in (3, 4) or any("var(" in p for p in parts):
        return None
    try:
        a = 1.0
        if len(parts) == 4:
            a = float(parts[3].rstrip("%")) / (100 if parts[3].endswith("%") else 1)
        if kind.startswith("rgb"):
            ch = [float(p.rstrip("%")) * 2.55 if p.endswith("%") else float(p) for p in parts[:3]]
            return (round(ch[0]), round(ch[1]), round(ch[2]), round(a, 3))
        hue = float(parts[0].rstrip("deg")) / 360 % 1
        sat, light = (float(p.rstrip("%")) / 100 for p in parts[1:3])
        import colorsys
        r, g, b = colorsys.hls_to_rgb(hue, light, sat)
        return (round(r * 255), round(g * 255), round(b * 255), round(a, 3))
    except ValueError:
        return None


def to_lab(rgb):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb[:3])
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def delta_e(c1, c2):
    d = math.dist(to_lab(c1), to_lab(c2))
    return d + abs(c1[3] - c2[3]) * 100  # alpha difference counts heavily


# ---------------------------------------------------------------- lengths

LEN_RE = re.compile(r"(?<![\w.#-])(-?\d*\.?\d+)(px|rem)\b")


def parse_length(text: str):
    m = re.fullmatch(r"\s*(-?\d*\.?\d+)(px|rem)?\s*", str(text).strip("'\""))
    if not m:
        return None
    value = float(m.group(1))
    return value * REM_PX if m.group(2) == "rem" else value


def length_category(name: str):
    n = name.lower().replace("_", "-")
    if "line-height" in n or "lineheight" in n or "leading" in n:
        return "line-height"
    if "font-size" in n or "fontsize" in n or re.search(r"(^|[.-])text-", n) or n.startswith("text"):
        return "font-size"
    if "radius" in n or "rounded" in n or "round" in n:
        return "radius"
    if "spac" in n or "gap" in n or "space" in n or re.search(r"(^|[.-])(margin|padding|inset)", n):
        return "spacing"
    return None


PROP_CATEGORY = [
    (re.compile(r"^(margin|padding|gap|row-gap|column-gap|inset|space)", re.I), "spacing"),
    (re.compile(r"^(m|p|mt|mb|ml|mr|mx|my|pt|pb|pl|pr|px|py|gap|space-x|space-y)$"), "spacing"),
    (re.compile(r"^(border-radius|borderradius|rounded)", re.I), "radius"),
    (re.compile(r"^(font-size|fontsize|text)$", re.I), "font-size"),
    (re.compile(r"^(line-height|lineheight|leading)$", re.I), "line-height"),
]


def prop_category(prop: str):
    p = prop.replace("_", "-")
    p_flat = re.sub(r"-([a-z])", lambda m: m.group(1).upper(), p) if "-" in p and not p.startswith("-") else p
    for candidate in (p, p_flat.lower(), re.sub(r"([A-Z])", r"-\1", p).lower()):
        for pattern, cat in PROP_CATEGORY:
            if pattern.search(candidate):
                return cat
    return None


# ---------------------------------------------------------------- token loading

class Tokens:
    def __init__(self):
        self.colours: list[tuple[str, tuple]] = []
        self.lengths: dict[str, list[tuple[str, float]]] = {}
        self.fonts: list[tuple[str, str]] = []
        self.css_names: set[str] = set()
        self.has_css = False
        self.files: set[Path] = set()

    def add(self, name: str, value, hint: str = ""):
        if isinstance(value, dict):  # DTCG dimension object
            if "value" in value and "unit" in value:
                value = f"{value['value']}{value['unit']}"
            else:
                return
        if isinstance(value, (int, float)):
            value = f"{value}px" if hint in ("dimension", "spacing") else str(value)
        if not isinstance(value, str) or "{" in value or "var(" in value:
            return
        lname = name.lower()
        if "fontfamily" in lname.replace("-", "") or hint == "fontFamily":
            first = value.split(",")[0].strip().strip("'\"")
            if first:
                self.fonts.append((name, first))
            return
        colour = parse_colour(value)
        if colour:
            self.colours.append((name, colour))
            return
        px = parse_length(value)
        cat = length_category(name)
        if px is not None and cat:
            self.lengths.setdefault(cat, []).append((name, px))

    def count(self):
        return len(self.colours) + sum(len(v) for v in self.lengths.values()) + len(self.fonts)


def simple_yaml(text: str) -> dict:
    """Parse the nested key: value maps used by DESIGN.md front matter."""
    root: dict = {}
    stack = [(-1, root)]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        if ":" not in line or line.startswith("- "):
            continue
        key, _, value = line.partition(":")
        key = key.strip().strip("'\"")
        value = value.strip()
        if value and not value.startswith(("'", '"')) and " #" in value:
            value = value.split(" #", 1)[0].strip()
        value = value.strip("'\"")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value == "":
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = value
    return root


def walk(prefix: str, node, out: list):
    if isinstance(node, dict):
        if "$value" in node or ("value" in node and not isinstance(node.get("value"), dict)):
            out.append((prefix, node.get("$value", node.get("value")), node.get("$type", node.get("type", ""))))
            return
        for k, v in node.items():
            if k.startswith("$"):
                continue
            walk(f"{prefix}.{k}" if prefix else k, v, out)
    else:
        out.append((prefix, node, ""))


def load_tokens(paths: list[Path]) -> Tokens:
    tokens = Tokens()
    for path in paths:
        text = path.read_text(encoding="utf-8")
        tokens.files.add(path.resolve())
        if path.suffix.lower() == ".md":
            if not text.startswith("---"):
                raise ValueError(f"{path}: no front matter found")
            end = text.find("\n---", 3)
            data = simple_yaml(text[3:end])
            leaves: list = []
            for cat in ("colors", "typography", "rounded", "spacing", "components"):
                if cat in data:
                    walk(cat, data[cat], leaves)
            for name, value, hint in leaves:
                if name.startswith("typography.") and name.split(".")[-1] in ("fontSize", "lineHeight"):
                    name = name  # category comes from the key name
                elif name.startswith("rounded."):
                    name = "radius." + name.split(".", 1)[1]
                elif name.startswith("components."):
                    key = name.split(".")[-1]
                    if key in ("rounded",):
                        name = name.replace(".rounded", ".radius")
                    elif key == "padding":
                        name = name.replace(".padding", ".spacing")
                tokens.add(name, value, hint)
        elif path.suffix.lower() == ".json":
            leaves = []
            walk("", json.loads(text), leaves)
            for name, value, hint in leaves:
                tokens.add(name, value, hint)
        else:
            tokens.has_css = True
            for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;{}]+);", text):
                tokens.css_names.add(m.group(1))
                tokens.add(m.group(1), m.group(2).strip())
    return tokens


# ---------------------------------------------------------------- scanning

PROP_BEFORE = re.compile(r"([A-Za-z][\w-]*)\s*[:=]\s*[\"'{\[(]?[^;:{}]*$")
TW_BEFORE = re.compile(r"(?:^|[\s\"'`])([a-z][a-z-]*?)-\[$")


def property_at(line: str, start: int) -> str:
    before = line[:start]
    tw = TW_BEFORE.search(before)
    if tw:
        return tw.group(1)
    m = PROP_BEFORE.search(before)
    return m.group(1) if m else ""


def find_files(targets: list[Path]):
    for target in targets:
        if target.is_file():
            yield target
        elif target.is_dir():
            for path in sorted(target.rglob("*")):
                if path.is_file() and path.suffix.lower() in SCAN_SUFFIXES and not (SKIP_DIRS & set(path.parts)):
                    yield path


def judge_colour(found, tokens: Tokens):
    if not tokens.colours:
        return None
    exact = [n for n, c in tokens.colours if c == found]
    if exact:
        return "hard-coded token", f"use {exact[0]}"
    name, best = min(tokens.colours, key=lambda t: delta_e(found, t[1]))
    d = delta_e(found, best)
    if d <= NEAR_COLOUR:
        return "near token", f"probably {name} (Delta E {d:.1f})"
    return "off-system", f"nearest is {name} (Delta E {d:.0f})"


def judge_length(px: float, cat: str, tokens: Tokens):
    scale = tokens.lengths.get(cat)
    if not scale:
        return None
    exact = [n for n, v in scale if abs(v - px) < 0.01]
    if exact:
        return "hard-coded token", f"use {exact[0]}"
    name, best = min(scale, key=lambda t: abs(t[1] - px))
    if abs(best - px) <= NEAR_PX:
        return "near token", f"probably {name} ({best:g}px)"
    return "off-system", f"not on the {cat} scale; nearest is {name} ({best:g}px)"


def scan(files, tokens: Tokens):
    findings = []
    font_names = {f.lower(): n for n, f in tokens.fonts}
    for path in files:
        if path.resolve() in tokens.files:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith(("//", "/*", "*", "<!--")):
                continue
            line = re.sub(r"--[\w-]+\s*:\s*[^;{}]*;?", "", line)  # token definitions
            if not line.strip():
                continue

            def add(found, prop, verdict):
                if verdict:
                    findings.append({"file": str(path), "line": number, "found": found,
                                     "property": prop, "label": verdict[0], "suggestion": verdict[1]})

            for m in HEX_RE.finditer(line):
                if re.search(r"(href|xlink:href|url\()\s*=?\s*[\"']?$", line[:m.start()]):
                    continue
                colour = parse_colour(m.group(0))
                if colour:
                    add(m.group(0), property_at(line, m.start()), judge_colour(colour, tokens))
            for m in FUNC_RE.finditer(line):
                colour = parse_colour(m.group(0))
                if colour:
                    add(m.group(0), property_at(line, m.start()), judge_colour(colour, tokens))
            for m in LEN_RE.finditer(line):
                prop = property_at(line, m.start())
                cat = prop_category(prop) if prop else None
                value = float(m.group(1))
                if not cat or value == 0:
                    continue
                px = value * REM_PX if m.group(2) == "rem" else value
                add(m.group(0), prop, judge_length(abs(px), cat, tokens))
            fm = re.search(r"(font-family|fontFamily)\s*[:=]\s*[\"'{]?\s*([^;,\"'}]+)", line)
            if fm and tokens.fonts and "var(" not in fm.group(2):
                first = fm.group(2).strip().strip("'\"")
                if first and first.lower() not in GENERIC_FONTS:
                    if first.lower() in font_names:
                        add(first, fm.group(1), ("hard-coded token", f"use {font_names[first.lower()]}"))
                    else:
                        add(first, fm.group(1), ("off-system", "font family not in the tokens"))
            if tokens.has_css:
                for vm in re.finditer(r"var\(\s*(--[\w-]+)", line):
                    if vm.group(1) not in tokens.css_names:
                        add(vm.group(0) + ")", property_at(line, vm.start()),
                            ("unknown token", "no token by this name; check for a typo"))
    return findings


def render(findings, tokens: Tokens) -> str:
    counts: dict[str, int] = {}
    for f in findings:
        counts[f["label"]] = counts.get(f["label"], 0) + 1
    out = [f"Tokens loaded: {len(tokens.colours)} colours, "
           + ", ".join(f"{len(v)} {k}" for k, v in sorted(tokens.lengths.items()))
           + f", {len(tokens.fonts)} font families"]
    if not findings:
        out.append("No drift found.")
        return "\n".join(out)
    out.append("Found: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    out.append("")
    out.append("| Where | Found | Property | Label | Suggestion |")
    out.append("| --- | --- | --- | --- | --- |")
    order = {"unknown token": 0, "off-system": 1, "near token": 2, "hard-coded token": 3}
    for f in sorted(findings, key=lambda f: (order.get(f["label"], 9), f["file"], f["line"])):
        out.append(f"| {f['file']}:{f['line']} | `{f['found']}` | {f['property'] or '?'} | {f['label']} | {f['suggestion']} |")
    return "\n".join(out)


# ---------------------------------------------------------------- self-test

def selftest() -> int:
    design_md = """---
name: Acme
colors:
  primary: "#1a3a52"
  ink: "#141414"
  surface: "#f7f3ec"
typography:
  body:
    fontFamily: Public Sans
    fontSize: 16px
    lineHeight: 24px
rounded:
  sm: 4px
  md: 8px
spacing:
  sm: 8px
  md: 16px
  lg: 24px
---
# Acme
"""
    css = """.card {
  color: #141414;
  background: #1b3b53;
  border-color: #ff00ff;
  padding: 15px;
  gap: 16px;
  border-radius: 20px;
  font-family: Inter, sans-serif;
  margin: 0;
  width: 37px;
}
:root { --brand-extra: #ff00ff; }
.title { font-family: "Public Sans"; color: var(--ink); line-height: 1.5rem; }
"""
    tsx = """<a href="#abc">x</a>
<div className="p-[7px] text-[#141414]" style={{ paddingTop: '24px', borderRadius: 8 }} />
"""
    tokens_css = ":root { --ink: #141414; --space-md: 16px; --radius-md: 8px; }\n"
    use_css = ".x { color: var(--ink); gap: var(--spcae-md); }\n"
    dtcg = {"color": {"brand": {"$value": "#0055ff", "$type": "color"}},
            "spacing": {"md": {"$value": {"value": 16, "unit": "px"}, "$type": "dimension"}}}
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "DESIGN.md").write_text(design_md)
        (t / "src").mkdir()
        (t / "src" / "card.css").write_text(css)
        (t / "src" / "Card.tsx").write_text(tsx)
        tokens = load_tokens([t / "DESIGN.md"])
        found = scan(find_files([t / "src"]), tokens)
        by = {(Path(f["file"]).name, f["found"]): f["label"] for f in found}

        def expect(key, label):
            if by.get(key) != label:
                failures.append(f"{key}: expected {label}, got {by.get(key)}")

        expect(("card.css", "#141414"), "hard-coded token")
        expect(("card.css", "#1b3b53"), "near token")
        expect(("card.css", "#ff00ff"), "off-system")
        expect(("card.css", "15px"), "near token")
        expect(("card.css", "16px"), "hard-coded token")
        expect(("card.css", "20px"), "off-system")
        expect(("card.css", "Inter"), "off-system")
        expect(("card.css", "Public Sans"), "hard-coded token")
        expect(("card.css", "1.5rem"), "hard-coded token")
        expect(("Card.tsx", "7px"), "near token")
        expect(("Card.tsx", "#141414"), "hard-coded token")
        expect(("Card.tsx", "24px"), "hard-coded token")
        if ("Card.tsx", "#abc") in by:
            failures.append("href anchor was treated as a colour")
        if ("card.css", "37px") in by:
            failures.append("width was treated as spacing")
        if sum(1 for f in found if f["found"] == "#ff00ff") != 1:
            failures.append("token definition line was scanned")

        (t / "tokens.css").write_text(tokens_css)
        (t / "use.css").write_text(use_css)
        found = scan([t / "use.css"], load_tokens([t / "tokens.css"]))
        if not any(f["label"] == "unknown token" and "--spcae-md" in f["found"] for f in found):
            failures.append("misspelt var() was not reported")
        if any("--ink" in f["found"] for f in found):
            failures.append("known var() was reported")

        (t / "tokens.json").write_text(json.dumps(dtcg))
        dt = load_tokens([t / "tokens.json"])
        if not dt.colours or dt.lengths.get("spacing", [(None, 0)])[0][1] != 16:
            failures.append(f"DTCG tokens not loaded: {dt.colours} {dt.lengths}")

    if failures:
        print("selftest failed:")
        for f in failures:
            print("  " + f)
        return 1
    print("selftest passed")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("targets", nargs="+", type=Path, help="files or folders to scan")
    parser.add_argument("--tokens", action="append", type=Path, required=True,
                        help="DESIGN.md, CSS or DTCG JSON token file; repeat for several")
    parser.add_argument("--json", action="store_true", help="print findings as JSON")
    args = parser.parse_args(argv)
    try:
        for p in args.tokens + args.targets:
            if not p.exists():
                raise ValueError(f"{p} does not exist")
        tokens = load_tokens(args.tokens)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if tokens.count() == 0 and not tokens.has_css:
        print("error: no tokens found in the token files", file=sys.stderr)
        return 2
    findings = scan(find_files(args.targets), tokens)
    print(json.dumps(findings, indent=2) if args.json else render(findings, tokens))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
