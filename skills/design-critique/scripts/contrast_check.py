#!/usr/bin/env python3
"""WCAG 2.2 contrast checker.

  One pair:
    python contrast_check.py "#6b7280" "#ffffff"
    python contrast_check.py "rgba(0,0,0,0.6)" "#f9fafb" --size 14 --bold

  Many pairs from a file, one per line: foreground background [label]
    python contrast_check.py --pairs pairs.txt

Colours: #rgb, #rrggbb, #rrggbbaa, rgb(), rgba(), hsl(), hsla() and CSS
named colours black, white and transparent. A translucent foreground is
blended over the background before measuring.

Size: --size in CSS px. Large text is 24 px and up, or 18.66 px and up
when --bold is set. Without --size, both normal and large results print.

Exit status: 0 when every pair passes for its text size (or for normal
text when no size is given), 1 when any fails, 2 on bad input.
Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import colorsys
import re
import sys
from pathlib import Path

NAMED = {"black": (0, 0, 0, 1.0), "white": (255, 255, 255, 1.0), "transparent": (0, 0, 0, 0.0)}


def parse_colour(value: str) -> tuple[float, float, float, float]:
    text = value.strip().lower()
    if text in NAMED:
        return NAMED[text]
    if text.startswith("#"):
        hexes = text[1:]
        if len(hexes) in (3, 4):
            hexes = "".join(ch * 2 for ch in hexes)
        if len(hexes) not in (6, 8) or not re.fullmatch(r"[0-9a-f]+", hexes):
            raise ValueError(f"bad hex colour: {value}")
        r, g, b = (int(hexes[i:i + 2], 16) for i in (0, 2, 4))
        a = int(hexes[6:8], 16) / 255 if len(hexes) == 8 else 1.0
        return r, g, b, a
    match = re.fullmatch(r"(rgba?|hsla?)\((.*)\)", text)
    if not match:
        raise ValueError(f"unrecognised colour: {value}")
    kind, inner = match.groups()
    parts = [p for p in re.split(r"[\s,/]+", inner.strip()) if p]
    if len(parts) not in (3, 4):
        raise ValueError(f"expected 3 or 4 components: {value}")
    alpha = 1.0
    if len(parts) == 4:
        alpha = float(parts[3].rstrip("%")) / (100 if parts[3].endswith("%") else 1)
    if kind.startswith("rgb"):
        channels = []
        for part in parts[:3]:
            channels.append(float(part.rstrip("%")) * 2.55 if part.endswith("%") else float(part))
        r, g, b = channels
    else:
        hue = float(parts[0].replace("deg", "")) % 360 / 360
        sat = float(parts[1].rstrip("%")) / 100
        light = float(parts[2].rstrip("%")) / 100
        rf, gf, bf = colorsys.hls_to_rgb(hue, light, sat)
        r, g, b = rf * 255, gf * 255, bf * 255
    return r, g, b, max(0.0, min(1.0, alpha))


def blend(fg, bg):
    r, g, b, a = fg
    br, bgc, bb, _ = bg
    return (r * a + br * (1 - a), g * a + bgc * (1 - a), b * a + bb * (1 - a))


def luminance(rgb) -> float:
    def channel(c: float) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg_text: str, bg_text: str) -> float:
    bg = parse_colour(bg_text)
    if bg[3] < 1:
        raise ValueError(f"background must be opaque to measure reliably: {bg_text}")
    fg = blend(parse_colour(fg_text), bg)
    l1, l2 = sorted((luminance(fg), luminance(bg[:3])), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def is_large(size: float | None, bold: bool) -> bool | None:
    if size is None:
        return None
    return size >= 24 or (bold and size >= 18.66)


def report(fg: str, bg: str, size: float | None, bold: bool, label: str = "") -> bool:
    ratio = contrast(fg, bg)
    shown = int(ratio * 100) / 100  # truncate so 4.499 never displays as 4.5
    large = is_large(size, bold)
    name = f"{label}: " if label else ""
    head = f"{name}{fg} on {bg}  {shown:.2f}:1"
    verdicts = []
    if large is None:
        verdicts.append(f"normal text AA {'pass' if ratio >= 4.5 else 'FAIL'}")
        verdicts.append(f"large text AA {'pass' if ratio >= 3 else 'FAIL'}")
        verdicts.append(f"non-text AA {'pass' if ratio >= 3 else 'FAIL'}")
        verdicts.append(f"normal text AAA {'pass' if ratio >= 7 else 'fail'}")
        ok = ratio >= 4.5
    else:
        need, need_aaa = (3.0, 4.5) if large else (4.5, 7.0)
        kind = "large text" if large else "normal text"
        verdicts.append(f"{kind} ({size:g} px{' bold' if bold else ''}) AA {'pass' if ratio >= need else 'FAIL'}")
        verdicts.append(f"AAA {'pass' if ratio >= need_aaa else 'fail'}")
        ok = ratio >= need
    print(f"{head}  |  " + "  |  ".join(verdicts))
    return ok


def selftest() -> int:
    assert abs(contrast("#000", "#fff") - 21) < 1e-9
    assert contrast("#767676", "#ffffff") >= 4.5
    assert contrast("#777777", "#ffffff") < 4.5
    assert abs(contrast("#ffffff", "#ffffff") - 1) < 1e-9
    assert abs(contrast("rgb(0, 0, 0)", "white") - 21) < 1e-9
    assert abs(contrast("hsl(0, 0%, 0%)", "#fff") - 21) < 1e-9
    # 50% black over white blends to about #808080, ratio about 3.95
    assert 3.9 < contrast("rgba(0,0,0,0.5)", "#ffffff") < 4.0
    assert abs(contrast("#00000080", "#ffffff") - contrast("rgba(0,0,0,0.502)", "#ffffff")) < 0.01
    assert is_large(24, False) and is_large(18.66, True) and not is_large(18, True) and not is_large(16, False)
    try:
        contrast("#000", "rgba(0,0,0,0.5)")
    except ValueError:
        pass
    else:
        raise AssertionError("translucent background should be rejected")
    print("selftest passed")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("foreground", nargs="?")
    parser.add_argument("background", nargs="?")
    parser.add_argument("--pairs", type=Path, help="file with one 'foreground background [label]' per line")
    parser.add_argument("--size", type=float, help="text size in CSS px")
    parser.add_argument("--bold", action="store_true", help="text is bold (700 or heavier)")
    args = parser.parse_args(argv)

    jobs: list[tuple[str, str, str]] = []
    if args.pairs:
        for number, line in enumerate(args.pairs.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith(("# ", "//")):
                continue
            tokens = re.findall(r"(?:rgba?|hsla?)\([^)]*\)|\S+", line)
            if not tokens:
                continue
            if len(tokens) < 2:
                print(f"line {number}: need a foreground and a background", file=sys.stderr)
                return 2
            jobs.append((tokens[0], tokens[1], " ".join(tokens[2:])))
    elif args.foreground and args.background:
        jobs.append((args.foreground, args.background, ""))
    else:
        parser.print_usage()
        return 2

    all_ok = True
    for fg, bg, label in jobs:
        try:
            all_ok &= report(fg, bg, args.size, args.bold, label)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
