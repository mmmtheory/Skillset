#!/usr/bin/env python3
"""Check a brand portfolio map for structural and naming problems.

  python portfolio_check.py portfolio.json
  python portfolio_check.py portfolio.yaml --json

The map format is described in references/portfolio-map.md. JSON always
works; YAML needs PyYAML.

Checks:
  missing-parent     an entry names a parent that is not in the map
  masterbrand        there is not exactly one masterbrand
  cycle              parents loop back on themselves
  depth              more than three levels below the masterbrand
  duplicate          two entries share a name
  similar            two names are easy to confuse (spelling or containment)
  pattern            a sub-brand or branded-house entry doesn't carry its parent's name
  hidden-parent      a house-of-brands entry uses the parent's name
  endorsement        an endorsed entry has no endorsement naming its parent
  named-feature      a feature carries a proper name instead of a description

Exit status: 0 when clean, 1 when any problem is found, 2 on bad input.
Uses only the Python standard library (plus PyYAML for .yaml files).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

MAX_DEPTH = 3


def load(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError:
            raise ValueError("reading YAML needs PyYAML: pip install pyyaml, or use JSON")
        return yaml.safe_load(text) or {}
    return json.loads(text)


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def words(name: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9À-ɏ']+", name)


def distance(a: str, b: str) -> int:
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def check(data: dict) -> list[dict]:
    problems: list[dict] = []

    def add(code: str, names, msg: str) -> None:
        problems.append({"check": code, "names": list(names), "message": msg})

    brands = data.get("brands") or []
    if not isinstance(brands, list) or not brands:
        raise ValueError("the map needs a non-empty 'brands' list")
    by_name: dict[str, dict] = {}
    for b in brands:
        if "name" not in b:
            raise ValueError(f"entry without a name: {b}")
        key = b["name"].strip().lower()
        if key in by_name:
            add("duplicate", [b["name"]], f"'{b['name']}' appears more than once")
        by_name[key] = b

    masters = [b for b in brands if b.get("tier") == "masterbrand"]
    if len(masters) != 1:
        add("masterbrand", [m["name"] for m in masters], f"expected one masterbrand, found {len(masters)}")
    master = (data.get("masterbrand") or (masters[0]["name"] if masters else "")).strip()

    def parent_of(b):
        p = b.get("parent")
        return by_name.get(p.strip().lower()) if p else None

    for b in brands:
        if b.get("parent") and not parent_of(b):
            add("missing-parent", [b["name"]], f"'{b['name']}' names parent '{b['parent']}', which is not in the map")

    for b in brands:
        seen, node, depth = [], b, 0
        while node is not None and node.get("parent"):
            if node["name"] in seen:
                add("cycle", seen, f"parents loop: {' -> '.join(seen + [node['name']])}")
                break
            seen.append(node["name"])
            node = parent_of(node)
            depth += 1
        else:
            if depth > MAX_DEPTH:
                add("depth", [b["name"]], f"'{b['name']}' sits {depth} levels below the top; keep it to {MAX_DEPTH} or fewer")

    def stripped(name: str) -> str:
        n = name
        if master and n.lower().startswith(master.lower() + " "):
            n = n[len(master) + 1:]
        return norm(n)

    named = [b for b in brands if b.get("tier") != "feature" and b.get("tier") != "masterbrand"]
    for i, a in enumerate(named):
        for b in named[i + 1:]:
            sa, sb = stripped(a["name"]), stripped(b["name"])
            if len(sa) < 3 or len(sb) < 3 or sa == sb and a["name"].lower() == b["name"].lower():
                continue
            limit = 1 if min(len(sa), len(sb)) <= 5 else 2
            close = distance(sa, sb) <= limit
            contains = min(len(sa), len(sb)) >= 4 and (sa in sb or sb in sa)
            if close or contains:
                why = "differ by only a letter or two" if close else "one contains the other"
                add("similar", [a["name"], b["name"]], f"'{a['name']}' and '{b['name']}' {why}, so people will mix them up")

    for b in brands:
        rel, parent = b.get("relationship"), parent_of(b)
        pname = parent["name"] if parent else master
        lower = b["name"].lower()
        if rel in ("sub-brand", "branded-house") and pname:
            heads = {pname.lower(), master.lower()} - {""}
            if not any(lower.startswith(h + " ") or lower == h for h in heads):
                add("pattern", [b["name"]], f"'{b['name']}' is a {rel} but doesn't start with '{pname}'")
        if rel == "house-of-brands" and master:
            if master.lower() in [w.lower() for w in words(b["name"])]:
                add("hidden-parent", [b["name"]], f"'{b['name']}' is meant to stand alone but uses the name '{master}'")
        if rel == "endorsed":
            end = (b.get("endorsement") or "").lower()
            if not end or (pname and pname.lower() not in end and master.lower() not in end):
                add("endorsement", [b["name"]], f"'{b['name']}' is endorsed but has no endorsement naming '{pname or master}'")
        if b.get("tier") == "feature" or rel == "feature":
            proper = [w for w in words(b["name"]) if w[:1].isupper() and w.lower() not in {master.lower(), (pname or "").lower()}]
            if proper:
                add("named-feature", [b["name"]], f"feature '{b['name']}' carries a name ({', '.join(proper)}); describe it in plain words instead")
    return problems


def selftest() -> int:
    good = {
        "masterbrand": "Acme",
        "brands": [
            {"name": "Acme", "tier": "masterbrand"},
            {"name": "Acme Ledger", "tier": "sub-brand", "parent": "Acme", "relationship": "sub-brand"},
            {"name": "Acme Payroll", "tier": "sub-brand", "parent": "Acme", "relationship": "branded-house"},
            {"name": "Tally", "tier": "brand", "parent": "Acme", "relationship": "endorsed", "endorsement": "Tally, by Acme"},
            {"name": "Nimbus", "tier": "brand", "parent": "Acme", "relationship": "house-of-brands"},
            {"name": "automatic tax filing", "tier": "feature", "parent": "Acme Ledger"},
        ],
    }
    assert check(good) == [], check(good)

    bad = {
        "masterbrand": "Acme",
        "brands": [
            {"name": "Acme", "tier": "masterbrand"},
            {"name": "Acme Ledger", "tier": "sub-brand", "parent": "Acme", "relationship": "sub-brand"},
            {"name": "Acme Leger", "tier": "sub-brand", "parent": "Acme", "relationship": "sub-brand"},
            {"name": "Paystream", "tier": "sub-brand", "parent": "Acme", "relationship": "sub-brand"},
            {"name": "Tally", "tier": "brand", "parent": "Acme", "relationship": "endorsed"},
            {"name": "Acme Cloud Nimbus", "tier": "brand", "parent": "Acme", "relationship": "house-of-brands"},
            {"name": "TaxBot", "tier": "feature", "parent": "Acme Ledger"},
            {"name": "Orphan", "tier": "product", "parent": "Missing Co"},
        ],
    }
    codes = sorted(p["check"] for p in check(bad))
    for expected in ("similar", "pattern", "endorsement", "hidden-parent", "named-feature", "missing-parent"):
        assert expected in codes, (expected, codes)

    deep = {"brands": [
        {"name": "A", "tier": "masterbrand"}, {"name": "A B", "parent": "A"}, {"name": "A C", "parent": "A B"},
        {"name": "A D", "parent": "A C"}, {"name": "A E", "parent": "A D"}]}
    assert any(p["check"] == "depth" for p in check(deep))
    loop = {"brands": [{"name": "Top", "tier": "masterbrand"}, {"name": "X", "parent": "Y"}, {"name": "Y", "parent": "X"}]}
    assert any(p["check"] == "cycle" for p in check(loop))

    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "p.json"
        f.write_text(json.dumps(good), encoding="utf-8")
        assert check(load(f)) == []
    print("selftest passed")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("map", type=Path)
    ap.add_argument("--json", action="store_true", help="print problems as JSON")
    args = ap.parse_args(argv)
    if not args.map.is_file():
        print(f"not found: {args.map}", file=sys.stderr)
        return 2
    try:
        problems = check(load(args.map))
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(problems, indent=2, ensure_ascii=False))
    else:
        count = len(load(args.map).get("brands", []))
        print(f"Checked {count} entries; {len(problems)} problem(s).")
        for p in problems:
            print(f"  [{p['check']}] {p['message']}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
