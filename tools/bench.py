#!/usr/bin/env python3
"""Skill Bench: record eval results and decide which skills meet the ship bar.

  python tools/bench.py check
      Validate bench/results.json and confirm every skill has an entry.

  python tools/bench.py add design-critique --with 91 --without 52 --heldout 86 \\
      --trigger 95 --agents "claude-code,cursor,codex" [--blind 2/3] [--report URL]
      Record a benchmark run. Scores are pass rates in percent.

  python tools/bench.py report
      Print a Markdown table of the latest run per skill, with a ship decision.

Run from the repository root. Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "bench" / "results.json"
SKILLS = ROOT / "skills"

THRESHOLDS = {"pass_rate": 85, "lift": 25, "heldout_gap": 10, "trigger": 90}
VISUAL = {"design-critique", "brand-strategy", "brand-architecture"}  # judged partly by blind review


def load() -> dict:
    return json.loads(RESULTS.read_text(encoding="utf-8"))


def save(data: dict) -> None:
    RESULTS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def skill_versions() -> dict:
    out = {}
    for d in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        text = (d / "SKILL.md").read_text(encoding="utf-8")
        version = "0.0.0"
        for line in text.splitlines():
            if line.strip().startswith("version:"):
                version = line.split(":", 1)[1].strip().strip('"\'')
                break
        out[d.name] = version
    return out


def decide(skill: str, run: dict) -> tuple[str, list[str]]:
    misses = []
    lift = run["with"] - run["without"]
    if run["with"] < THRESHOLDS["pass_rate"]:
        misses.append(f"pass rate {run['with']:g}% < {THRESHOLDS['pass_rate']}%")
    if lift < THRESHOLDS["lift"]:
        misses.append(f"lift {lift:+g} < +{THRESHOLDS['lift']}")
    if run.get("heldout") is None:
        misses.append("no held-out result")
    elif run["with"] - run["heldout"] > THRESHOLDS["heldout_gap"]:
        misses.append(f"held-out gap {run['with'] - run['heldout']:g} > {THRESHOLDS['heldout_gap']}")
    if run.get("trigger") is None:
        misses.append("no trigger result")
    elif run["trigger"] < THRESHOLDS["trigger"]:
        misses.append(f"trigger {run['trigger']:g}% < {THRESHOLDS['trigger']}%")
    if skill in VISUAL:
        blind = run.get("blind")
        if not blind:
            misses.append("no blind review")
        else:
            won, total = (int(x) for x in blind.split("/"))
            if won < 2:
                misses.append(f"blind review {blind}, needs 2 of 3")
    return ("ships" if not misses else "below bar"), misses


def cmd_check(_args) -> int:
    data, versions, errors = load(), skill_versions(), []
    for name in versions:
        if name not in data.get("skills", {}):
            errors.append(f"{name}: no entry in bench/results.json")
    for name, entry in data.get("skills", {}).items():
        if name not in versions:
            errors.append(f"{name}: in results.json but not in skills/")
        for run in entry.get("runs", []):
            for key in ("date", "skill_version", "with", "without", "agents"):
                if key not in run:
                    errors.append(f"{name}: run missing '{key}'")
            for key in ("with", "without", "heldout", "trigger"):
                v = run.get(key)
                if v is not None and not (0 <= v <= 100):
                    errors.append(f"{name}: {key} must be 0 to 100")
    if errors:
        print("\n".join(errors))
        return 1
    measured = sum(1 for e in data["skills"].values() if e.get("runs"))
    print(f"OK: {len(versions)} skills in the bench, {measured} with results")
    return 0


def cmd_add(args) -> int:
    data, versions = load(), skill_versions()
    if args.skill not in versions:
        print(f"unknown skill: {args.skill}", file=sys.stderr)
        return 2
    run = {
        "date": args.date or dt.date.today().isoformat(),
        "skill_version": versions[args.skill],
        "agents": [a.strip() for a in args.agents.split(",") if a.strip()],
        "runs_per_case": args.runs,
        "with": args.with_, "without": args.without,
        "heldout": args.heldout, "trigger": args.trigger, "blind": args.blind,
        "report": args.report,
    }
    entry = data["skills"].setdefault(args.skill, {"runs": []})
    entry["runs"].append(run)
    data["updated"] = run["date"]
    save(data)
    status, misses = decide(args.skill, run)
    print(f"Recorded {args.skill} {run['skill_version']}: {status}" + (f" ({'; '.join(misses)})" if misses else ""))
    return 0


def cmd_report(_args) -> int:
    data = load()
    print("| Skill | Version | With | Without | Lift | Held-out | Trigger | Blind | Status |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for name, entry in sorted(data["skills"].items()):
        runs = entry.get("runs") or []
        if not runs:
            print(f"| {name} | | | | | | | | Awaiting first run |")
            continue
        r = runs[-1]
        status, misses = decide(name, r)
        fmt = lambda v: "" if v is None else f"{v:g}%"
        note = "Ships" if status == "ships" else "Below bar: " + "; ".join(misses)
        print(f"| {name} | {r['skill_version']} | {fmt(r['with'])} | {fmt(r['without'])} | {r['with'] - r['without']:+g} | {fmt(r.get('heldout'))} | {fmt(r.get('trigger'))} | {r.get('blind') or ''} | {note} |")
    print(f"\nThresholds: pass rate of {THRESHOLDS['pass_rate']}% or more, lift of +{THRESHOLDS['lift']} or more, held-out within {THRESHOLDS['heldout_gap']} points, trigger accuracy of {THRESHOLDS['trigger']}% or more, blind review 2 of 3 for visual and brand skills.")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("report")
    a = sub.add_parser("add")
    a.add_argument("skill")
    a.add_argument("--with", dest="with_", type=float, required=True)
    a.add_argument("--without", type=float, required=True)
    a.add_argument("--heldout", type=float)
    a.add_argument("--trigger", type=float)
    a.add_argument("--blind", help="blind review wins, such as 2/3")
    a.add_argument("--agents", required=True, help="comma separated, such as claude-code,cursor,codex")
    a.add_argument("--runs", type=int, default=3)
    a.add_argument("--date")
    a.add_argument("--report", help="link to the full run report")
    args = ap.parse_args(argv)
    return {"check": cmd_check, "add": cmd_add, "report": cmd_report}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
