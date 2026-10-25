#!/usr/bin/env python3
"""Check usability test tasks and questions for wording that skews results.

  python task_lint.py plan.md --ui-terms "Send, Add recipient, Payees" --session 45
  python task_lint.py plan.md --overhead 15

Tasks are read from a Markdown table with a Scenario (or Task) column, or
from numbered items under a heading that contains "Tasks". Time budgets come
from a Minutes (or Min, Time) column.

Flags on tasks:
  ui-term      uses a label from the interface (pass them with --ui-terms)
  ui-verb      tells people how to operate the interface (click, tap, go to)
  ui-noun      names interface parts (button, tab, menu, link, icon, page)
  signals      "try to", "explore", "see if you can": hints that it is hard
  two-goals    "and then" or several goals in one task (warning)

Flags on questions (any line ending in "?" outside the task list):
  prediction   asks people to predict their behaviour or what they would pay
  leading      suggests the answer
  double       asks two things at once (warning)

Session check: the sum of task minutes plus --overhead (intro, warm-up and
wrap-up, default 15) must leave at least 10 minutes of buffer in --session.

Exit status: 0 when nothing but warnings, 1 when any flag is an error,
2 on bad input. Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

UI_VERBS = re.compile(r"\b(click|clicking|tap|tapping|press the|select the|navigate|scroll|swipe|"
                      r"go to|open the|use the|hover)\b", re.I)
UI_NOUNS = re.compile(r"\b(button|tab|menu|dropdown|drop-down|link|icon|page|screen|toggle|checkbox|"
                      r"modal|sidebar|navbar|nav bar|field)\b", re.I)
SIGNALS = re.compile(r"\b(try to|try and|explore|see if you can|attempt to|figure out how)\b", re.I)
TWO_GOALS = re.compile(r"\b(and then|then also|after that,? (also )?)\b", re.I)

PREDICTION = re.compile(
    r"\b(would you (use|buy|pay|recommend|like|want|switch|prefer|sign up|subscribe|download)|"
    r"will you (use|buy|pay)|how likely (are you|would you|is it)|how much would you (pay|spend)|"
    r"would this (help|be useful)|do you think you('d| would))\b", re.I)
LEADING = re.compile(
    r"\b(don't you|didn't you|isn't it|wasn't (it|that)|aren't you|wouldn't you|"
    r"how (easy|great|helpful|intuitive|simple|clear) (was|is|did)|did you (like|love|enjoy)|"
    r"do you (like|love|agree)|how much did you (like|enjoy)|was (it|that) (easy|confusing|clear|helpful)|"
    r"(you|they) (liked|loved|preferred))\b", re.I)
DOUBLE = re.compile(r"\bhow (\w+) (and|or) (\w+) (was|is|were|did)\b|\b(\w+ly|\w+) and (\w+) (was|is) (it|that|this)\b", re.I)
SAFE_PROBES = re.compile(r"what would you do if|if i weren't here|on your own|how easy or difficult", re.I)


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def read_plan(text: str):
    lines = text.splitlines()
    tasks: list[dict] = []
    task_lines: set[int] = set()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\|?\s*:?-{3,}", lines[i + 1].strip()):
            header = [h.lower() for h in split_row(line)]
            col = next((n for n, h in enumerate(header) if h in ("scenario", "task", "tasks", "task scenario")), None)
            mins = next((n for n, h in enumerate(header) if h in ("minutes", "min", "mins", "time", "time (min)")), None)
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                if col is not None:
                    cells = split_row(lines[j])
                    cells += [""] * (len(header) - len(cells))
                    minutes = None
                    if mins is not None:
                        m = re.search(r"\d+(\.\d+)?", cells[mins])
                        minutes = float(m.group(0)) if m else None
                    tasks.append({"line": j + 1, "text": cells[col], "minutes": minutes})
                    task_lines.add(j + 1)
                j += 1
            i = j
            continue
        i += 1
    if not tasks:
        in_tasks = False
        for n, line in enumerate(lines, 1):
            if re.match(r"^#+\s", line):
                in_tasks = "task" in line.lower()
                continue
            m = re.match(r"^\s*(\d+)[.)]\s+(.*)", line)
            if in_tasks and m:
                mm = re.search(r"\((\d+)\s*min", line)
                tasks.append({"line": n, "text": m.group(2), "minutes": float(mm.group(1)) if mm else None})
                task_lines.add(n)
    questions = []
    for n, line in enumerate(lines, 1):
        if n in task_lines:
            continue
        for q in re.findall(r"[^.!?>\"]*\?", line):
            q = q.strip(" -*>\"'|")
            if len(q.split()) >= 3:
                questions.append({"line": n, "text": q})
    return tasks, questions


def lint(text: str, ui_terms: list[str], session: float | None, overhead: float):
    errors, warnings = [], []
    tasks, questions = read_plan(text)
    if not tasks:
        errors.append("no tasks found; use a table with a Scenario column or a numbered list under a Tasks heading")
    terms = [t for t in (u.strip() for u in ui_terms) if t]
    for t in tasks:
        where = f"line {t['line']}"
        body = t["text"]
        quoted = re.findall(r"[\"'“‘]([^\"'”’]+)[\"'”’]", body)
        for term in terms:
            if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", body, re.I):
                errors.append(f"{where}: ui-term '{term}' gives the answer away; describe the goal in the participant's words")
        m = UI_VERBS.search(body)
        if m:
            errors.append(f"{where}: ui-verb '{m.group(0)}' tells people how to operate the interface")
        m = UI_NOUNS.search(body)
        if m:
            errors.append(f"{where}: ui-noun '{m.group(0)}' names part of the interface")
        m = SIGNALS.search(body)
        if m:
            errors.append(f"{where}: signals '{m.group(0)}' hints that the task is hard or has no clear end")
        if TWO_GOALS.search(body):
            warnings.append(f"{where}: two-goals; consider splitting into separate tasks")
        if quoted and not terms:
            warnings.append(f"{where}: quoted text {quoted}; check it is not an interface label")
    for q in questions:
        if SAFE_PROBES.search(q["text"]):
            continue
        where = f"line {q['line']}"
        m = PREDICTION.search(q["text"])
        if m:
            errors.append(f"{where}: prediction '{m.group(0)}'; ask about past behaviour instead")
        m = LEADING.search(q["text"])
        if m:
            errors.append(f"{where}: leading '{m.group(0)}'; ask neutrally (what did you expect?)")
        if DOUBLE.search(q["text"]):
            warnings.append(f"{where}: double; ask one thing at a time: '{q['text']}'")
    total = sum(t["minutes"] for t in tasks if t["minutes"])
    summary = f"{len(tasks)} task(s), {len(questions)} question(s)"
    if any(t["minutes"] for t in tasks):
        summary += f", {total:g} task minutes + {overhead:g} overhead = {total + overhead:g}"
    if session is not None:
        missing = [t for t in tasks if not t["minutes"]]
        if missing:
            warnings.append(f"{len(missing)} task(s) without a time budget")
        if total + overhead > session - 10:
            errors.append(f"session over budget: {total + overhead:g} min planned in a {session:g} min session; "
                          f"leave 10 min buffer, so cut or shorten tasks")
        summary += f" of {session:g}"
    return errors, warnings, summary


SAMPLE_BAD = """# Plan

## Tasks
| # | Scenario | Minutes |
| --- | --- | --- |
| 1 | Click Send and add a new recipient in Payees. | 10 |
| 2 | Try to explore the Rewards tab and then change your card. | 15 |
| 3 | You need to pay your flatmate back $40 for groceries. Pay them. | 12 |

## Questions
- Would you use this feature every week?
- Didn't you find that confusing?
- How easy and useful was that?
- What would you do if I weren't here?
"""

SAMPLE_GOOD = """## Tasks
1. Your sister in Fiji needs $200 for rent by Friday. You haven't sent her money before. Send it to her. (8 min)
2. You think you were charged twice for a coffee yesterday. Check whether you were. (6 min)

## After each task
- Overall, how easy or difficult was that task?
- What were you expecting to happen at that point?
"""


def selftest() -> int:
    failures = []
    errors, warnings, summary = lint(SAMPLE_BAD, ["Send", "Payees", "Rewards"], 45, 15)
    joined = " ".join(errors + warnings)
    for expected in ("ui-term 'Send'", "ui-term 'Payees'", "ui-verb 'Click'", "ui-noun 'tab'", "signals",
                     "two-goals", "prediction", "leading", "double", "over budget"):
        if expected not in joined:
            failures.append(f"bad plan: missed {expected}")
    if any("line 8" in e for e in errors):
        failures.append("good task 3 was flagged")
    if any("weren't here" in e for e in errors):
        failures.append("safe probe was flagged")
    errors, warnings, summary = lint(SAMPLE_GOOD, ["Send money", "Transactions"], 45, 15)
    if errors:
        failures.append(f"good plan flagged: {errors}")
    if "2 task(s)" not in summary or "14 task minutes" not in summary:
        failures.append(f"numbered tasks not read: {summary}")
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "plan.md"
        p.write_text(SAMPLE_BAD)
        if main([str(p), "--ui-terms", "Send", "--session", "45"]) != 1:
            failures.append("exit status should be 1")
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
    parser.add_argument("plan", type=Path)
    parser.add_argument("--ui-terms", default="", help="comma-separated interface labels participants must find")
    parser.add_argument("--session", type=float, help="session length in minutes")
    parser.add_argument("--overhead", type=float, default=15, help="minutes for intro, warm-up and wrap-up")
    args = parser.parse_args(argv)
    if not args.plan.is_file():
        print(f"error: {args.plan} not found", file=sys.stderr)
        return 2
    errors, warnings, summary = lint(args.plan.read_text(encoding="utf-8"), args.ui_terms.split(","),
                                     args.session, args.overhead)
    print(summary)
    for e in errors:
        print(f"  error: {e}")
    for w in warnings:
        print(f"  warning: {w}")
    if not errors:
        print("OK: no errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
