#!/usr/bin/env python3
"""Lint product copy for machine-written tells and brand voice rules.

  python copy_lint.py strings.md
  python copy_lint.py en.json --brand BRAND.md
  echo "Oops! Something went wrong." | python copy_lint.py -

Reads Markdown, plain text, JSON string files (values are checked) or stdin.
With --brand, the words in BRAND.md's front matter under words.avoid are
flagged too.

Checks:
  dash          em or en dashes used as punctuation
  stock         stock phrases that mark copy as generated
  frame         "not just X, it's Y" and "it's not X, it's Y" framing
  exclaim       exclamation marks
  emoji         emoji in interface copy
  vague-error   errors that don't say what happened ("Something went wrong")
  vague-action  buttons that don't name the action ("Submit", "Click here")
  long          sentences over 25 words
  brand-avoid   words BRAND.md says the brand never uses

Exit status: 0 when clean, 1 when anything is flagged, 2 on bad input.
Uses only the Python standard library (PyYAML is used for BRAND.md if installed).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

STOCK = [
    "delve", "tapestry", "testament to", "it's worth noting", "it is worth noting", "in today's fast-paced",
    "game-changer", "game changer", "elevate your", "unlock the power", "unlock your", "seamless", "seamlessly",
    "embark on", "navigate the complexities", "in the realm of", "harness the power", "supercharge",
    "look no further", "rest assured", "we're thrilled", "we are thrilled", "we're excited to", "revolutionize",
    "revolutionise", "cutting-edge", "best-in-class", "world-class", "effortlessly", "empower you",
    "at your fingertips", "take it to the next level", "the future of", "in conclusion", "furthermore",
    "moreover", "a myriad of", "plethora", "robust solution", "leverage", "synergy", "holistic",
]
VAGUE_ERRORS = ["something went wrong", "an error occurred", "an error has occurred", "oops", "uh oh", "whoops",
                "unknown error", "please try again later", "invalid input"]
VAGUE_ACTIONS = {"submit", "click here", "ok", "okay", "proceed", "continue", "yes", "no", "go", "learn more", "click"}
FRAME = re.compile(r"\b(?:it'?s|this is|isn'?t)\s+not\s+(?:just\s+)?[^.,;]{1,40}[,;]\s*(?:it'?s|but)\b|\bnot just\s+[^.,;]{1,40}[,;]?\s*(?:but|it'?s)\b|\bmore than just\b", re.I)
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐✨]")
SENT = re.compile(r"[^.!?]+[.!?]?")


def brand_avoid(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return []
    fm = text[3:text.find("\n---", 3)]
    try:
        import yaml
        data = yaml.safe_load(fm) or {}
        words = (data.get("words") or {}).get("avoid") or []
    except ImportError:
        m = re.search(r"^\s*avoid:\s*\[(.*?)\]", fm, re.M)
        words = [w.strip().strip("\"'") for w in m.group(1).split(",")] if m else []
    return [str(w).lower() for w in words if str(w).strip()]


def units(path: str, text: str):
    """Yield (location, string) pairs to check."""
    if path.endswith(".json"):
        def walk(node, key=""):
            if isinstance(node, dict):
                for k, v in node.items():
                    yield from walk(v, f"{key}.{k}" if key else k)
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    yield from walk(v, f"{key}[{i}]")
            elif isinstance(node, str):
                yield key, node
        yield from walk(json.loads(text))
        return
    in_code = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or not line.strip():
            continue
        yield f"line {n}", line


def is_button(loc: str, s: str) -> bool:
    key = loc.lower()
    bare = re.sub(r"^[\s>*-]*(?:\w+\s*:\s*)?[\"“']?", "", s).strip().strip("\"'”.").lower()
    return (any(k in key for k in ("button", "cta", "action", "label")) or re.search(r"\b(button|cta)\b", s, re.I)) and bare in VAGUE_ACTIONS \
        or s.strip().strip("\"'[]").lower() in VAGUE_ACTIONS


def lint(path: str, text: str, avoid: list[str]) -> list[str]:
    out = []
    for loc, s in units(path, text):
        low = s.lower()
        if re.search("\u2014|\u2013| -- | - (?=[a-z])", s):
            out.append(f"{loc}: dash: rewrite as two sentences or use a comma")
        for p in STOCK:
            if re.search(r"(?<![a-z])" + re.escape(p) + r"(?![a-z])", low):
                out.append(f"{loc}: stock: \"{p}\"")
        if FRAME.search(s):
            out.append(f"{loc}: frame: \"not X, it's Y\" framing; say the thing directly")
        if "!" in s:
            out.append(f"{loc}: exclaim: drop the exclamation mark")
        if EMOJI.search(s):
            out.append(f"{loc}: emoji: remove from interface copy")
        for e in VAGUE_ERRORS:
            if re.search(r"(?<![a-z])" + re.escape(e) + r"(?![a-z])", low):
                out.append(f"{loc}: vague-error: \"{e}\" doesn't say what happened or what to do")
                break
        if is_button(loc, s) or re.search(r"\bclick here\b", low):
            out.append(f"{loc}: vague-action: name what the button does")
        for sent in SENT.findall(s):
            if len(sent.split()) > 25:
                out.append(f"{loc}: long: {len(sent.split())}-word sentence; split it")
        for w in avoid:
            if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low):
                out.append(f"{loc}: brand-avoid: \"{w}\" is on BRAND.md's avoid list")
    return out


def selftest() -> int:
    bad = ("Oops! Something went wrong.\n"
           "Unlock the power of seamless invoicing \u2014 effortlessly.\n"
           "It's not just an app, it's a movement.\n"
           "Button: Submit\n"
           "Your coffee, perfected ✨\n"
           "Our artisan beans are roasted with passion.\n")
    found = lint("copy.md", bad, ["artisan", "passion"])
    for code in ("vague-error", "exclaim", "dash", "stock", "frame", "vague-action", "emoji", "brand-avoid"):
        assert any(f": {code}:" in f for f in found), (code, found)
    good = ("Couldn't save your changes. Check your connection and try again.\n"
            "Roasted Tuesday. At your door by Friday.\n"
            "Button: Send 3 invoices\n")
    assert lint("copy.md", good, []) == [], lint("copy.md", good, [])
    j = json.dumps({"checkout": {"error": "An error occurred", "cta": "Pay $24.50"}, "empty": "No invoices yet. Create your first one."})
    fj = lint("en.json", j, [])
    assert any("checkout.error" in f and "vague-error" in f for f in fj) and len(fj) == 1, fj
    with tempfile.TemporaryDirectory() as tmp:
        b = Path(tmp) / "BRAND.md"
        b.write_text("---\nbrand: K\nwords:\n  use: [roasted on]\n  avoid: [artisan, premium]\n---\n# K\n", encoding="utf-8")
        assert brand_avoid(b) == ["artisan", "premium"]
    print("selftest passed")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="files to check, or - for stdin")
    ap.add_argument("--brand", type=Path, help="BRAND.md whose words.avoid list should be enforced")
    args = ap.parse_args(argv)
    avoid = brand_avoid(args.brand) if args.brand and args.brand.is_file() else []
    if args.brand and not args.brand.is_file():
        print(f"not found: {args.brand}", file=sys.stderr)
        return 2
    total = 0
    for f in args.files:
        try:
            text = sys.stdin.read() if f == "-" else Path(f).read_text(encoding="utf-8")
            found = lint(f, text, avoid)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: {f}: {exc}", file=sys.stderr)
            return 2
        total += len(found)
        print(f"{f}: {len(found)} flag(s)")
        for x in found:
            print(f"  {x}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
