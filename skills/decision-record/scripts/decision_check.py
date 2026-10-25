#!/usr/bin/env python3
"""Check a design decision record against the template.

  python decision_check.py decisions/0007-single-page-checkout.md
  python decision_check.py decisions/*.md

Errors (exit 1):
  missing sections, fewer than two options, unknown status, date not
  YYYY-MM-DD, no decider or a group as decider, a vague or missing revisit
  trigger, Superseded with no link to the new record.

Warnings (printed, exit 0 if no errors):
  evidence items without a type label, decider "not stated",
  more than 600 words.

A record with Status: Proposed is checked as a decision request: it needs
Question, Context, Options and Decide by instead of Decision, Trade-offs,
Dissent and Consequences.

Exit status: 0 when every file passes, 1 when any has errors, 2 on bad input.
Uses only the Python standard library.
"""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

ACCEPTED_SECTIONS = ["decision", "context", "options", "evidence", "trade-offs", "dissent", "consequences", "revisit when"]
PROPOSED_SECTIONS = ["question", "context", "options", "evidence", "decide by", "revisit when"]
STATUSES = ("proposed", "accepted", "superseded by", "deprecated", "rejected")
GROUP_DECIDERS = {"team", "the team", "we", "us", "everyone", "the group", "all", "design team", "leadership", "stakeholders"}
VAGUE_TRIGGERS = ["if needed", "as needed", "when needed", "later", "when appropriate", "tbd", "tbc",
                  "periodically", "from time to time", "if necessary", "as required", "in the future", "at some point"]
EVIDENCE_TYPES = re.compile(r"\b(data|research|standard|precedent|judgement|judgment)\b", re.I)
MAX_WORDS = 600


def sections(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    current = None
    buf: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m and not line.startswith("###"):
            if current:
                found[current] = "\n".join(buf).strip()
            current = normalise(m.group(1))
            buf = []
        elif current:
            buf.append(line)
    if current:
        found[current] = "\n".join(buf).strip()
    return found


def normalise(heading: str) -> str:
    h = heading.lower().strip().rstrip(":")
    h = h.replace("tradeoffs", "trade-offs").replace("trade offs", "trade-offs")
    h = h.replace("revisit if", "revisit when").replace("revisit", "revisit when") if h.startswith("revisit") else h
    h = re.sub(r"revisit when( when)+", "revisit when", h)
    return h


def field(text: str, name: str) -> str | None:
    m = re.search(rf"^\**{name}:?\**:?\s*(.*)$", text, re.I | re.M)
    return m.group(1).strip().strip("*").strip() if m else None


def count_options(body: str) -> int:
    subheads = re.findall(r"^###\s+\S", body, re.M)
    if subheads:
        return len(subheads)
    items = re.findall(r"^\s*(?:[-*]|\d+[.)]|[A-Z][.)])\s+\S", body, re.M)
    return len(items)


def check(text: str) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    status = (field(text, "status") or "").strip()
    status_l = status.lower()
    if not status:
        errors.append("no Status line")
    elif not status_l.startswith(STATUSES):
        errors.append(f"status '{status}' is not one of Proposed, Accepted, Superseded by, Deprecated, Rejected")
    elif status_l.startswith("superseded") and not re.search(r"(DR-\d+|\[.+\]\(.+\)|\.md)", status):
        errors.append("Superseded status needs a link or ID for the new record")

    date = field(text, "date")
    if not date or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        errors.append("Date must be YYYY-MM-DD")

    decider = (field(text, "decider") or "").strip()
    decider_l = decider.lower().rstrip(".")
    if not decider:
        errors.append("no Decider line")
    elif decider_l in GROUP_DECIDERS:
        errors.append(f"decider '{decider}' is a group; name one person or role")
    elif decider_l.startswith("not stated"):
        warnings.append("decider not stated; make sure it is listed as an open question")
    elif re.search(r"\b(and|&)\b|,", decider):
        errors.append(f"decider '{decider}' names more than one; one person decides, others are consulted")

    found = sections(text)
    required = PROPOSED_SECTIONS if status_l.startswith("proposed") else ACCEPTED_SECTIONS
    for name in required:
        if name not in found:
            alt = {"dissent": "positions so far"}.get(name)
            if alt and alt in found:
                continue
            errors.append(f"missing section '## {name[0].upper() + name[1:]}'")
        elif not found[name].strip() and name != "dissent":
            errors.append(f"section '{name[0].upper() + name[1:]}' is empty")

    if "options" in found and count_options(found["options"]) < 2:
        errors.append("fewer than two options; include the realistic alternatives, such as keeping what exists")

    trigger = found.get("revisit when", "")
    plain = re.sub(r"^\s*[-*]\s*", "", trigger, flags=re.M).strip().lower()
    if "revisit when" in found:
        if not plain:
            errors.append("revisit trigger is empty")
        else:
            lines = [l.strip(" .") for l in plain.splitlines() if l.strip()]
            vague = [l for l in lines if any(v == l or l.startswith(v) for v in VAGUE_TRIGGERS) or len(l.split()) < 3]
            if len(vague) == len(lines):
                errors.append("revisit trigger is vague; name an observable condition, threshold or date")

    if "evidence" in found:
        items = [l for l in found["evidence"].splitlines() if re.match(r"^\s*[-*]\s+\S", l)]
        untyped = [l.strip() for l in items if not EVIDENCE_TYPES.search(l.split(":")[0])]
        if untyped:
            warnings.append(f"{len(untyped)} evidence item(s) without a type label (Data, Research, Standard, Precedent, Judgement)")

    words = len(re.sub(r"```.*?```", "", text, flags=re.S).split())
    if words > MAX_WORDS:
        warnings.append(f"{words} words; aim for under {MAX_WORDS} and link out for detail")
    return errors, warnings


GOOD = """# DR-0003: Bottom tab bar

**Status:** Accepted
**Date:** 2026-10-26
**Decider:** Head of Product
**Consulted:** iOS lead, Android lead

## Decision
The app uses a bottom tab bar with four tabs.

## Context
Rewards is hard to find.

## Options
### A. Tab bar (chosen)
For: one tap to every main area.
### B. Keep the menu
For: no re-learning.

## Evidence
- **Research:** 4 of 5 found Rewards with tabs. [Test, Oct]
- Someone said it looks nicer.

## Trade-offs
Low-traffic settings move into Account.

## Dissent
Android lead preferred a drawer; committed.

## Consequences
- Design updates frames (Ana, Nov 3)

## Revisit when
- Account tab visits rise above 30% of sessions
"""

BAD = """# Navigation

**Status:** Done
**Date:** 26/10/2026
**Decider:** The team

## Decision
We aligned on tabs.

## Options
- Tabs

## Revisit when
- If needed
"""

PROPOSED = """# DR-0004: Saved cards

**Status:** Proposed
**Date:** 2026-10-26
**Decider:** not stated

## Question
Should checkout offer saved cards?

## Context
Asked by support.

## Options
- Offer saved cards
- Keep entering card details each time

## Evidence
- **Research:** 12 support tickets in September asked for it. [Zendesk]

## Decide by
Before the November release, by the Head of Product.

## Revisit when
- Card entry errors exceed 5% of checkout attempts
"""


def selftest() -> int:
    failures = []
    errors, warnings = check(GOOD)
    if errors:
        failures.append(f"good record flagged: {errors}")
    if not any("type label" in w for w in warnings):
        failures.append("untyped evidence was not warned")
    errors, _ = check(BAD)
    joined = " ".join(errors)
    for expected in ("status 'Done'", "YYYY-MM-DD", "is a group", "missing section '## Context'",
                     "fewer than two options", "vague"):
        if expected not in joined:
            failures.append(f"bad record: missed '{expected}'")
    errors, warnings = check(PROPOSED)
    if errors:
        failures.append(f"decision request flagged: {errors}")
    if not any("not stated" in w for w in warnings):
        failures.append("decider not stated was not warned")
    e2, _ = check(GOOD.replace("Head of Product", "Head of Product and CTO"))
    if not any("more than one" in e for e in e2):
        failures.append("two deciders not flagged")
    e3, _ = check(GOOD.replace("Accepted", "Superseded by"))
    if not any("needs a link" in e for e in e3):
        failures.append("superseded without link not flagged")
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "bad.md"
        p.write_text(BAD)
        if run([str(p)]) != 1:
            failures.append("exit status should be 1 for a bad record")
    if failures:
        print("selftest failed:")
        for f in failures:
            print("  " + f)
        return 1
    print("selftest passed")
    return 0


def run(paths: list[str]) -> int:
    status = 0
    for name in paths:
        path = Path(name)
        if not path.is_file():
            print(f"error: {name} not found", file=sys.stderr)
            return 2
        errors, warnings = check(path.read_text(encoding="utf-8"))
        label = "OK" if not errors else "FAIL"
        print(f"{label}: {path}")
        for e in errors:
            print(f"  error: {e}")
        for w in warnings:
            print(f"  warning: {w}")
        if errors:
            status = 1
    return status


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2
    if argv[0] == "--selftest":
        return selftest()
    return run(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
