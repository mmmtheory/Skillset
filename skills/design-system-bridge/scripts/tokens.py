#!/usr/bin/env python3
"""Convert, lint and compare design tokens across DESIGN.md, DTCG JSON, CSS and Figma exports.

  lint     python tokens.py lint DESIGN.md
           Broken references, missing sections, invalid values, and contrast
           of every component's text on its background.

  to-dtcg  python tokens.py to-dtcg DESIGN.md --out tokens.json
           DESIGN.md front matter to DTCG 2025.10 JSON (colors as objects
           with colorSpace, components and hex; dimensions as value and unit).

  to-md    python tokens.py to-md tokens.json --out DESIGN.md [--name Acme]
           DTCG JSON to a DESIGN.md with front matter and the prescribed
           section headings, ready for rationale to be written in.

  drift    python tokens.py drift DESIGN.md tokens.json styles.css figma.json
           Compare two or more sources. Reports tokens missing from a source
           and values that disagree. Colors compare as hex, dimensions in px
           (1rem = 16px). CSS custom properties and flat Figma exports
           ({"color/primary": "#1a3a52"}) are matched by category and name.

Exit status: 0 when clean, 1 when problems or drift are found, 2 on bad input.
Uses only the Python standard library. PyYAML is used if installed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

CATEGORIES = ("colors", "typography", "rounded", "spacing", "components")
SECTIONS = ["Overview", "Colors", "Typography", "Layout", "Elevation & Depth", "Shapes", "Components", "Do's and Don'ts"]
REF = re.compile(r"^\{([a-z]+)\.([^}]+)\}$")
HEX = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
DIM = re.compile(r"^(-?\d*\.?\d+)\s*(px|rem|em)?$")
TYPE_DIMS = ("fontSize", "letterSpacing")


# ---------- reading ----------

def _scalar(v: str):
    v = v.strip()
    if not v:
        return None
    if v[0] in "\"'" and v[-1] == v[0]:
        return v[1:-1]
    if v.startswith("[") and v.endswith("]"):
        return [_scalar(x) for x in v[1:-1].split(",") if x.strip()]
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d*\.\d+", v):
        return float(v)
    if v in ("true", "false"):
        return v == "true"
    return v


def mini_yaml(text: str) -> dict:
    """Enough YAML for DESIGN.md front matter: nested maps, scalars, flow lists."""
    root: dict = {}
    stack = [(-1, root)]
    for raw in text.splitlines():
        line = re.sub(r"\s+#.*$", "", raw) if "#" in raw and not re.search(r"[\"'][^\"']*#", raw) else raw
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, _, rest = line.strip().partition(":")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if rest.strip():
            parent[key.strip().strip("\"'")] = _scalar(rest)
        else:
            child: dict = {}
            parent[key.strip().strip("\"'")] = child
            stack.append((indent, child))
    return root


def split_front_matter(text: str):
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    return text[3:end].strip("\n"), text[end + 4:]


def read_design_md(path: Path) -> tuple[dict, str]:
    raw, body = split_front_matter(path.read_text(encoding="utf-8"))
    if raw is None:
        raise ValueError(f"{path} has no front matter")
    try:
        import yaml
        data = yaml.safe_load(raw) or {}
    except ImportError:
        data = mini_yaml(raw)
    return data, body


# ---------- values ----------

def hex6(value) -> str | None:
    if not isinstance(value, str):
        return None
    v = value.strip()
    m = HEX.match(v)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return "#" + h[:6].lower()
    m = re.match(r"rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)", v)
    if m:
        return "#" + "".join(f"{int(x):02x}" for x in m.groups())
    return None


def px(value) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, dict) and "value" in value:
        return float(value["value"]) * (16 if value.get("unit") == "rem" else 1)
    if isinstance(value, str):
        m = DIM.match(value.strip())
        if m:
            return float(m.group(1)) * (16 if m.group(2) in ("rem", "em") else 1)
    return None


def dim_obj(value) -> dict | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return {"value": value, "unit": "px"}
    if isinstance(value, str):
        m = DIM.match(value.strip())
        if m:
            n = float(m.group(1))
            return {"value": int(n) if n.is_integer() else n, "unit": "rem" if m.group(2) in ("rem", "em") else "px"}
    return None


def lum(h: str) -> float:
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a: str, b: str) -> float:
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def resolve(data: dict, value, depth=0):
    if isinstance(value, str) and depth < 8:
        m = REF.match(value.strip())
        if m:
            cat, name = m.groups()
            target = (data.get(cat) or {}).get(name)
            return None if target is None else resolve(data, target, depth + 1)
    return value


# ---------- lint ----------

def lint(data: dict, body: str) -> list[str]:
    out = []
    for key in data:
        if key not in CATEGORIES and key not in ("name", "description", "version"):
            out.append(f"unknown top-level key '{key}' (allowed, but check it is intended)")
    for name, v in (data.get("colors") or {}).items():
        if not hex6(resolve(data, v)):
            out.append(f"colors.{name}: '{v}' is not a hex or rgb colour this tool can read")
    for cat in ("rounded", "spacing"):
        for name, v in (data.get(cat) or {}).items():
            vals = v if isinstance(v, list) else [v]
            if any(px(resolve(data, x)) is None for x in vals):
                out.append(f"{cat}.{name}: '{v}' is not a dimension")
    for style, props in (data.get("typography") or {}).items():
        if not isinstance(props, dict):
            out.append(f"typography.{style}: expected fontFamily, fontSize and friends")
            continue
        for need in ("fontFamily", "fontSize"):
            if need not in props:
                out.append(f"typography.{style}: missing {need}")
    for comp, props in (data.get("components") or {}).items():
        if not isinstance(props, dict):
            continue
        for prop, v in props.items():
            if isinstance(v, str) and REF.match(v.strip()) and resolve(data, v) is None:
                out.append(f"components.{comp}.{prop}: reference {v} does not resolve")
        bg, fg = hex6(resolve(data, props.get("backgroundColor"))), hex6(resolve(data, props.get("textColor")))
        if bg and fg:
            r = contrast(bg, fg)
            if r < 4.5:
                out.append(f"components.{comp}: text {fg} on {bg} is {r:.2f}:1, under 4.5:1 (WCAG 1.4.3)")
    present = [h.strip() for h in re.findall(r"^##\s+(.+)$", body, re.M)]
    missing = [s for s in SECTIONS if s.lower() not in [p.lower() for p in present]]
    if missing:
        out.append("missing sections: " + ", ".join(missing))
    order = [s for s in [p for p in present] if s.lower() in [x.lower() for x in SECTIONS]]
    expected = [s for s in SECTIONS if s.lower() in [o.lower() for o in order]]
    if [o.lower() for o in order] != [e.lower() for e in expected]:
        out.append("sections are out of the prescribed order: " + ", ".join(SECTIONS))
    return out


# ---------- DTCG ----------

def to_dtcg(data: dict) -> dict:
    out: dict = {}
    if data.get("colors"):
        out["colors"] = {}
        for name, v in data["colors"].items():
            if isinstance(v, str) and REF.match(v.strip()):
                out["colors"][name] = {"$type": "color", "$value": v.strip()}
                continue
            h = hex6(v)
            if not h:
                continue
            comps = [round(int(h[i:i + 2], 16) / 255, 4) for i in (1, 3, 5)]
            out["colors"][name] = {"$type": "color", "$value": {"colorSpace": "srgb", "components": comps, "alpha": 1, "hex": h}}
    for cat in ("rounded", "spacing"):
        for name, v in (data.get(cat) or {}).items():
            if isinstance(v, list):
                for i, x in enumerate(v):
                    d = dim_obj(x)
                    if d:
                        out.setdefault(cat, {})[f"{name}-{i}"] = {"$type": "dimension", "$value": d}
                continue
            d = v.strip() if isinstance(v, str) and REF.match(v.strip()) else dim_obj(v)
            if d:
                out.setdefault(cat, {})[name] = {"$type": "dimension", "$value": d}
    for style, props in (data.get("typography") or {}).items():
        if not isinstance(props, dict):
            continue
        val = {}
        for k, v in props.items():
            if k in TYPE_DIMS:
                val[k] = dim_obj(v) or v
            elif k == "fontFamily":
                val[k] = [s.strip().strip("\"'") for s in str(v).split(",")] if "," in str(v) else str(v)
            elif k == "lineHeight" and isinstance(v, str) and v.endswith("px") and px(props.get("fontSize")):
                val[k] = round(px(v) / px(props["fontSize"]), 3)
            else:
                val[k] = v
        out.setdefault("typography", {})[style] = {"$type": "typography", "$value": val}
    for comp, props in (data.get("components") or {}).items():
        if not isinstance(props, dict):
            continue
        group = {}
        for k, v in props.items():
            if isinstance(v, str) and REF.match(v.strip()):
                group[k] = {"$value": v.strip()}
            elif hex6(v):
                group[k] = {"$type": "color", "$value": {"colorSpace": "srgb", "components": [round(int(hex6(v)[i:i + 2], 16) / 255, 4) for i in (1, 3, 5)], "alpha": 1, "hex": hex6(v)}}
            elif dim_obj(v):
                group[k] = {"$type": "dimension", "$value": dim_obj(v)}
            else:
                group[k] = {"$value": v}
        out.setdefault("components", {})[comp] = group
    return out


def from_dtcg(tokens: dict) -> dict:
    data: dict = {}

    def val(node):
        v = node.get("$value")
        if isinstance(v, dict) and "hex" in v:
            return v["hex"]
        if isinstance(v, dict) and "colorSpace" in v and v.get("colorSpace") == "srgb":
            return "#" + "".join(f"{round(c * 255):02x}" for c in v["components"])
        if isinstance(v, dict) and "unit" in v:
            n = v["value"]
            return f"{n}{v['unit']}"
        return v

    for cat in CATEGORIES:
        group = tokens.get(cat) or {}
        for name, node in group.items():
            if not isinstance(node, dict):
                continue
            if "$value" in node:
                v = val(node)
                if cat == "typography" and isinstance(v, dict):
                    v = {k: (f"{x['value']}{x['unit']}" if isinstance(x, dict) and "unit" in x else (", ".join(x) if isinstance(x, list) else x)) for k, x in v.items()}
                data.setdefault(cat, {})[name] = v
            elif cat == "components":
                data.setdefault(cat, {})[name] = {k: val(n) for k, n in node.items() if isinstance(n, dict)}
    return data


def dump_yaml(data: dict, indent=0) -> str:
    lines = []
    for k, v in data.items():
        pad = "  " * indent
        if isinstance(v, dict):
            lines.append(f"{pad}{k}:")
            lines.append(dump_yaml(v, indent + 1))
        else:
            if isinstance(v, str) and (v.startswith(("#", "{")) or ":" in v or v.strip() != v):
                v = json.dumps(v)
            elif isinstance(v, list):
                v = "[" + ", ".join(json.dumps(x) if isinstance(x, str) else str(x) for x in v) + "]"
            lines.append(f"{pad}{k}: {v}")
    return "\n".join(l for l in lines if l)


def to_md(tokens: dict, name: str) -> str:
    data = {"name": name, **from_dtcg(tokens)}
    body = "\n\n".join(f"## {s}\n\nTo write: the reasoning behind these choices." for s in SECTIONS)
    return f"---\n{dump_yaml(data)}\n---\n\n# {name}\n\n{body}\n"


# ---------- drift ----------

PREFIXES = {
    "colors": ("colors-", "color-", "colour-", "c-"),
    "rounded": ("rounded-", "radius-", "radii-", "r-", "border-radius-"),
    "spacing": ("spacing-", "space-", "gap-", "s-"),
}


def short(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def classify(name: str, value) -> tuple[str, str, object] | None:
    n = short(name)
    for cat, pre in PREFIXES.items():
        for p in pre:
            if n.startswith(p):
                n2 = n[len(p):]
                if cat == "colors" and hex6(value):
                    return cat, n2, hex6(value)
                if cat != "colors" and px(value) is not None:
                    return cat, n2, px(value)
    if hex6(value):
        return "colors", n, hex6(value)
    if px(value) is not None:
        return "dimension", n, px(value)
    return None


def typo_norm(props: dict) -> dict:
    out = {}
    fs = px(props.get("fontSize"))
    for k, v in props.items():
        if k in TYPE_DIMS:
            out[k] = px(v)
        elif k == "lineHeight":
            if isinstance(v, str) and v.strip().endswith(("px", "rem")) and fs:
                out[k] = round(px(v) / fs, 3)
            else:
                try:
                    out[k] = round(float(v), 3)
                except (TypeError, ValueError):
                    out[k] = str(v).lower()
        elif k == "fontFamily":
            out[k] = ", ".join(v).lower() if isinstance(v, list) else str(v).lower()
        else:
            out[k] = str(v).lower() if isinstance(v, str) else v
    return out


def flatten(path: Path) -> dict:
    """name -> normalised value, keyed 'category/name' (typography as 'typography/style.prop')."""
    out: dict = {}
    suffix = path.suffix.lower()
    if suffix == ".md":
        data, _ = read_design_md(path)
        for cat in ("colors", "rounded", "spacing"):
            for name, v in (data.get(cat) or {}).items():
                r = resolve(data, v)
                if isinstance(r, list):
                    continue
                norm = hex6(r) if cat == "colors" else px(r)
                if norm is not None:
                    out[f"{cat}/{short(name)}"] = norm
        for style, props in (data.get("typography") or {}).items():
            if isinstance(props, dict):
                for k, v in typo_norm(props).items():
                    out[f"typography/{short(style)}.{k}"] = v
        return out
    if suffix == ".css":
        for name, v in re.findall(r"--([A-Za-z0-9_-]+)\s*:\s*([^;]+);", path.read_text(encoding="utf-8")):
            c = classify(name, v.strip())
            if c:
                out.setdefault(f"{c[0]}/{c[1]}", c[2])
        return out
    tokens = json.loads(path.read_text(encoding="utf-8"))
    if any(k in tokens for k in CATEGORIES) and any(isinstance(v, dict) for v in tokens.values()):
        data = from_dtcg(tokens)
        tmp = {}
        for cat in ("colors", "rounded", "spacing"):
            for name, v in (data.get(cat) or {}).items():
                r = resolve(data, v)
                norm = hex6(r) if cat == "colors" else px(r)
                if norm is not None:
                    tmp[f"{cat}/{short(name)}"] = norm
        for style, props in (data.get("typography") or {}).items():
            if isinstance(props, dict):
                for k, v in typo_norm(props).items():
                    tmp[f"typography/{short(style)}.{k}"] = v
        return tmp
    for name, v in tokens.items():  # flat export, such as Figma variables
        c = classify(name.replace("/", "-"), v if not isinstance(v, (int, float)) else f"{v}px")
        if c:
            out.setdefault(f"{c[0]}/{c[1]}", c[2])
    return out


def drift(paths: list[Path]) -> list[str]:
    flats = {p.name: flatten(p) for p in paths}
    names = list(flats)
    out = []

    def bucket(key: str) -> str:
        return key.split("/", 1)[0]

    # Dimensions from CSS or flat exports may be rounded or spacing; let them match either.
    def lookup(flat: dict, key: str):
        if key in flat:
            return flat[key]
        cat, n = key.split("/", 1)
        if cat in ("rounded", "spacing"):
            return flat.get(f"dimension/{n}")
        if cat == "dimension":
            return flat.get(f"rounded/{n}", flat.get(f"spacing/{n}"))
        return None

    comparable = lambda f, k: not (bucket(k) == "typography" and not any(x.startswith("typography/") for x in f))
    all_keys = sorted({k for f in flats.values() for k in f})
    for key in all_keys:
        vals = {n: lookup(flats[n], key) for n in names if comparable(flats[n], key)}
        have = {n: v for n, v in vals.items() if v is not None}
        if len(vals) < 2:
            continue
        missing = [n for n, v in vals.items() if v is None]
        if bucket(key) == "dimension" and any(lookup(flats[n], key.replace("dimension/", c + "/")) is not None for n in names for c in ("rounded", "spacing")):
            continue
        if missing and have:
            out.append(f"{key}: missing from {', '.join(missing)}")
        distinct = {json.dumps(v) for v in have.values()}
        if len(distinct) > 1:
            def show(v):
                if isinstance(v, float) and (bucket(key) in ("rounded", "spacing", "dimension") or key.endswith(TYPE_DIMS)):
                    return f"{v:g}px"
                return f"{v:g}" if isinstance(v, float) else str(v)
            out.append(f"{key}: " + "; ".join(f"{n} = {show(v)}" for n, v in have.items()))
    return out


# ---------- cli ----------

SAMPLE = """---
name: Sample
colors:
  primary: "#c62418"
  on-primary: "#ffffff"
  ink: "#0f0f10"
  muted: "#9ca3af"
  surface: "#f7f7f5"
typography:
  body:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: 400
    lineHeight: 24px
rounded:
  sm: 4px
  md: 8px
spacing:
  md: 16px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
  caption:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.muted}"
  card:
    backgroundColor: "{colors.raised}"
---

# Sample

## Overview
## Colors
## Typography
## Layout
## Elevation & Depth
## Shapes
## Components
## Do's and Don'ts
"""


def selftest() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        md = d / "DESIGN.md"
        md.write_text(SAMPLE, encoding="utf-8")
        data, body = read_design_md(md)
        assert mini_yaml(split_front_matter(SAMPLE)[0])["components"]["button-primary"]["rounded"] == "{rounded.md}"
        problems = lint(data, body)
        assert any("caption" in p and "4.5:1" in p for p in problems), problems
        assert any("card.backgroundColor" in p and "does not resolve" in p for p in problems), problems
        assert not any("button-primary" in p for p in problems), problems
        assert not any("missing sections" in p for p in problems), problems

        tokens = to_dtcg(data)
        assert tokens["colors"]["primary"]["$value"] == {"colorSpace": "srgb", "components": [0.7765, 0.1412, 0.0941], "alpha": 1, "hex": "#c62418"}
        assert tokens["rounded"]["md"]["$value"] == {"value": 8, "unit": "px"}
        assert tokens["typography"]["body"]["$value"]["lineHeight"] == 1.5
        assert tokens["components"]["button-primary"]["backgroundColor"]["$value"] == "{colors.primary}"
        js = d / "tokens.json"
        js.write_text(json.dumps(tokens), encoding="utf-8")

        back = from_dtcg(tokens)
        assert back["colors"]["primary"] == "#c62418" and back["rounded"]["md"] == "8px"
        md2 = d / "ROUND.md"
        md2.write_text(to_md(tokens, "Sample"), encoding="utf-8")
        d2, b2 = read_design_md(md2)
        assert d2["colors"]["ink"] == "#0f0f10" and "## Do's and Don'ts" in b2

        css = d / "styles.css"
        css.write_text(":root { --color-primary: #c62418; --color-ink: #111111; --radius-md: 0.5rem; --space-md: 16px; --color-extra: #00ff00; }", encoding="utf-8")
        fig = d / "figma.json"
        fig.write_text(json.dumps({"color/primary": "#C62418", "color/ink": "#0f0f10", "radius/md": 8}), encoding="utf-8")
        report = drift([md, js, css, fig])
        assert not any(r.startswith("colors/primary") for r in report), report
        assert any(r.startswith("colors/ink") and "styles.css = #111111" in r for r in report), report
        assert any(r.startswith("colors/extra") and "missing from" in r for r in report), report
        assert not any(r.startswith("rounded/md") for r in report), report
        assert drift([md, js]) == [], drift([md, js])
    print("selftest passed")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("lint"); p.add_argument("file", type=Path)
    p = sub.add_parser("to-dtcg"); p.add_argument("file", type=Path); p.add_argument("--out", type=Path)
    p = sub.add_parser("to-md"); p.add_argument("file", type=Path); p.add_argument("--out", type=Path); p.add_argument("--name", default="Design system")
    p = sub.add_parser("drift"); p.add_argument("files", type=Path, nargs="+")
    args = ap.parse_args(argv)
    files = getattr(args, "files", None) or [args.file]
    missing = [str(f) for f in files if not f.is_file()]
    if missing:
        print(f"not found: {', '.join(missing)}", file=sys.stderr)
        return 2
    try:
        if args.cmd == "lint":
            data, body = read_design_md(args.file)
            problems = lint(data, body)
            print(f"{args.file}: {len(problems)} problem(s)")
            for x in problems:
                print(f"  {x}")
            return 1 if problems else 0
        if args.cmd == "to-dtcg":
            data, _ = read_design_md(args.file)
            text = json.dumps(to_dtcg(data), indent=2, ensure_ascii=False) + "\n"
        elif args.cmd == "to-md":
            text = to_md(json.loads(args.file.read_text(encoding="utf-8")), args.name)
        else:
            if len(args.files) < 2:
                print("drift needs at least two files", file=sys.stderr)
                return 2
            report = drift(args.files)
            print(f"Compared {len(args.files)} sources; {len(report)} difference(s).")
            for x in report:
                print(f"  {x}")
            return 1 if report else 0
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
