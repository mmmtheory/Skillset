#!/usr/bin/env python3
"""Derive the states a screen or component needs, and check a finished inventory.

  Derive a starting list from traits:
    python state_matrix.py "Order history: remote, list, filter, paged" "Refund: action, money, irreversible"
    python state_matrix.py --traits

  Check an inventory written as Markdown tables:
    python state_matrix.py --check states.md

Each subject is "Name: trait, trait, ...". The output is a Markdown table per
subject with one row per derived state and its cause, and empty columns to fill
in. The list is a floor: remove states that cannot happen and add domain states.

--check reads every Markdown table whose header has a State column and flags:
rows with no Copy or no Way out (Copy may be empty for Note rows; Message and
Action are accepted as column names), missing or
unknown Priority, and copy that uses vague phrases such as "Something went wrong".

Exit status: 0 when the check passes or derivation succeeds, 1 when the check
finds problems, 2 on bad input. Uses only the Python standard library.
"""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

TRAITS: dict[str, list[tuple[str, str]]] = {
    "remote": [
        ("Loading, first time", "data is fetched before anything can show"),
        ("Loading, slow", "the request takes longer than a few seconds"),
        ("Failed to load", "network or server error on fetch"),
        ("Stale", "showing cached data that may be out of date"),
        ("Refreshing", "updating while old data is visible"),
    ],
    "list": [
        ("Empty, first use", "nothing has been created yet"),
        ("One item", "layouts built for many often break with one"),
        ("Many items", "the normal busy case"),
        ("Overflow", "long names, large numbers, translated text"),
    ],
    "filter": [
        ("No results", "the search or filters match nothing"),
        ("Filtered", "filters applied; people need to see that and clear them"),
    ],
    "paged": [
        ("Loading more", "the next page is being fetched"),
        ("End of list", "there is nothing more to load"),
        ("Next page failed", "the first page loaded but a later one did not"),
    ],
    "input": [
        ("Untouched", "the form before any interaction"),
        ("Invalid field", "a value fails validation"),
        ("Partly filled", "the person leaves before finishing"),
        ("Submitting", "waiting for the server after submit"),
        ("Rejected by server", "the server refuses values that passed the client checks"),
    ],
    "action": [
        ("In progress", "the action has started and is not finished"),
        ("Succeeded", "the action worked; people need to know what changed"),
        ("Failed", "the action did not happen"),
        ("Unavailable", "the action cannot be used right now; say why"),
    ],
    "irreversible": [
        ("Confirming", "the person is about to do something that cannot be undone"),
        ("Done, with receipt", "proof of what happened, for later"),
    ],
    "money": [
        ("Pending", "money is committed but not settled"),
        ("Declined", "the bank or provider refused"),
        ("Unknown outcome", "a timeout after the request was sent; it may have gone through"),
        ("Duplicate attempt", "a double tap or a retry after a timeout"),
        ("Refunded or reversed", "money moved back, fully or in part"),
    ],
    "external": [
        ("Third party slow", "a provider outside our control is slow"),
        ("Third party unavailable", "a provider outside our control is down"),
    ],
    "permission": [
        ("No access", "the person cannot see this; say why and who can help"),
        ("Read only", "the person can see but not change"),
        ("Access removed mid-session", "permissions change while the screen is open"),
    ],
    "shared": [
        ("Edited by someone else", "a conflict with another person's change"),
        ("Deleted by someone else", "the thing disappears while open"),
    ],
    "time": [
        ("Scheduled", "set to happen later"),
        ("Expiring soon", "a deadline is near"),
        ("Expired", "the deadline passed"),
    ],
    "auth": [
        ("Signed out", "the person is not signed in"),
        ("Session expired", "the session ends mid-task; what happens to unsaved work"),
        ("Unverified", "the account exists but is not verified"),
    ],
    "upload": [
        ("Uploading", "progress for a file in transit"),
        ("Upload failed", "network drop or server refusal"),
        ("Not accepted", "too large or the wrong type"),
        ("Processing", "uploaded but not ready to use"),
    ],
    "offline": [
        ("Offline", "no connection; what still works"),
        ("Back online", "queued changes sync, or fail to"),
    ],
    "ai": [
        ("Generating", "output is being produced"),
        ("Stopped", "the person stopped it part way"),
        ("Low confidence", "the system is unsure; say so plainly"),
        ("Refused", "the request is outside what it will do"),
        ("Rate limited", "out of requests or credits"),
    ],
    "quota": [
        ("Near limit", "usage close to a plan or storage limit"),
        ("At limit", "the limit is reached; what is blocked and how to lift it"),
    ],
    "first-run": [
        ("First visit", "nothing known about the person yet"),
        ("Returning", "what changes once they have been here before"),
    ],
    "media": [
        ("Image failed", "an image or avatar does not load"),
        ("No image", "the optional image was never provided"),
    ],
    "notify": [
        ("Unread", "new since the person last looked"),
        ("Target gone", "the thing it points to was deleted or access was removed"),
        ("Delivery failed", "email bounced or push is turned off"),
    ],
}

ALIASES = {
    "async": "remote", "api": "remote", "fetch": "remote", "network": "remote",
    "search": "filter", "pagination": "paged", "infinite": "paged",
    "form": "input", "payment": "money", "payments": "money", "pay": "money",
    "destructive": "irreversible", "delete": "irreversible", "third-party": "external",
    "permissions": "permission", "roles": "permission", "collab": "shared",
    "collaborative": "shared", "multiplayer": "shared", "deadline": "time",
    "schedule": "time", "expiry": "time", "login": "auth", "session": "auth",
    "file": "upload", "files": "upload", "agent": "ai", "llm": "ai", "limit": "quota",
    "onboarding": "first-run", "image": "media", "images": "media",
    "notification": "notify", "notifications": "notify",
}

VAGUE = ["something went wrong", "oops", "uh oh", "an error occurred", "invalid input",
         "unknown error", "error occurred", "try again later"]
PRIORITIES = {"design", "pattern", "note"}


def resolve(trait: str) -> str | None:
    t = trait.strip().lower()
    return t if t in TRAITS else ALIASES.get(t)


def derive(subjects: list[str]) -> tuple[str, list[str]]:
    out, unknown = [], []
    for subject in subjects:
        name, _, traits_text = subject.partition(":")
        traits = [t for t in re.split(r"[,\s]+", traits_text) if t]
        if not traits:
            unknown.append(f"{name.strip()}: no traits given")
            continue
        states: list[tuple[str, str, str]] = [("Default", "the expected, populated case", "")]
        seen = {"Default"}
        for raw in traits:
            key = resolve(raw)
            if not key:
                unknown.append(raw)
                continue
            for state, cause in TRAITS[key]:
                if state not in seen:
                    seen.add(state)
                    states.append((state, cause, key))
        out.append(f"## States: {name.strip()}\n")
        out.append("| State | Cause | Likelihood | Impact | Seen as | Copy | Way out | Priority |")
        out.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for state, cause, key in states:
            origin = f" ({key})" if key else ""
            out.append(f"| {state} | {cause}{origin} |  |  |  |  |  |  |")
        out.append("")
    return "\n".join(out), unknown


def tables(text: str):
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?\s*:?-{3,}", lines[i + 1].strip()):
            header = [c.strip().lower() for c in line.strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append((j + 1, [c.strip() for c in lines[j].strip().strip("|").split("|")]))
                j += 1
            yield header, rows
            i = j
        else:
            i += 1


def check(text: str) -> list[str]:
    problems = []
    found_table = False
    for header, rows in tables(text):
        if "state" not in header:
            continue
        found_table = True
        col = {name: idx for idx, name in enumerate(header)}
        copy_i = next((col[k] for k in ("copy", "message", "text") if k in col), None)
        out_i = next((col[k] for k in ("way out", "action", "next step", "recovery") if k in col), None)
        pri_i = col.get("priority")
        if copy_i is None or out_i is None:
            problems.append("a state table has no Copy (or Message) column, or no Way out (or Action) column")
            continue
        for number, cells in rows:
            cells += [""] * (len(header) - len(cells))
            state = cells[col["state"]]
            cause = cells[col["cause"]] if "cause" in col else ""
            copy, way_out = cells[copy_i], cells[out_i]
            priority = cells[pri_i].strip().lower() if pri_i is not None else ""
            where = f"line {number} ({state or 'unnamed'})"
            if pri_i is None:
                pass
            elif priority not in PRIORITIES:
                problems.append(f"{where}: priority must be Design, Pattern or Note")
            if not copy and priority != "note" and state.lower() != "default":
                problems.append(f"{where}: no copy")
            if not way_out and state.lower() != "default":
                problems.append(f"{where}: no way out")
            if copy:
                for phrase in VAGUE:
                    if re.search(rf"\b{re.escape(phrase)}\b", copy.lower()):
                        problems.append(f"{where}: vague copy '{phrase}'; say what happened and what to do")
                        break
        if pri_i is None:
            problems.append("a state table has no Priority column")
    if not found_table:
        problems.append("no Markdown table with a State column found")
    return problems


def selftest() -> int:
    failures = []
    table, unknown = derive(["Checkout: remote, money, input, irreversible", "Feed: list, search, nonsense"])
    for expected in ("Unknown outcome", "Duplicate attempt", "Confirming", "No results", "Failed to load", "Rejected by server"):
        if expected not in table:
            failures.append(f"derive: missing {expected}")
    if unknown != ["nonsense"]:
        failures.append(f"derive: unknown traits {unknown}")
    if table.count("| Default |") != 2:
        failures.append("derive: each subject should start with Default")

    good = """
| State | Cause | Likelihood | Impact | Seen as | Copy | Way out | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Default | populated | common | low | list | | | Design |
| Declined | bank refused | occasional | high | inline banner | Your bank declined this payment. You haven't been charged. | Try another card | Design |
| Stale | cache | rare | low | timestamp | | Pull to refresh | Note |
"""
    bad = """
| State | Cause | Copy | Way out | Priority |
| --- | --- | --- | --- | --- |
| Failed to load | server error | Oops! Something went wrong. | Retry | Design |
| Empty | first use | | Create one | Maybe |
| Timeout | unknown outcome | We're checking with your bank. | | Pattern |
"""
    if check(good):
        failures.append(f"check flagged a good inventory: {check(good)}")
    flagged = " ".join(check(bad))
    for expected in ("vague copy", "no copy", "priority must be", "no way out"):
        if expected not in flagged:
            failures.append(f"check missed: {expected}")
    legacy = """
| State | Copy | Action | Priority |
| --- | --- | --- | --- |
| Timeout | An error occurred. | Retry | Design |
"""
    if not any("vague copy" in p for p in check(legacy)):
        failures.append("check did not read Action as the way out column")
    if "no Markdown table" not in " ".join(check("no tables here")):
        failures.append("check accepted a file without tables")

    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "states.md"
        p.write_text(bad)
        if main(["--check", str(p)]) != 1:
            failures.append("check exit status should be 1 on problems")

    if failures:
        print("selftest failed:")
        for f in failures:
            print("  " + f)
        return 1
    print("selftest passed")
    return 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2
    if argv[0] == "--selftest":
        return selftest()
    if argv[0] == "--traits":
        for key, states in TRAITS.items():
            aliases = sorted(a for a, k in ALIASES.items() if k == key)
            extra = f" (also: {', '.join(aliases)})" if aliases else ""
            print(f"{key}{extra}: " + ", ".join(s for s, _ in states))
        return 0
    if argv[0] == "--check":
        if len(argv) < 2 or not Path(argv[1]).exists():
            print("error: --check needs a Markdown file", file=sys.stderr)
            return 2
        problems = check(Path(argv[1]).read_text(encoding="utf-8"))
        if problems:
            print(f"{len(problems)} problem(s):")
            for p in problems:
                print("  " + p)
            return 1
        print("OK: every state has copy, a way out and a priority")
        return 0
    text, unknown = derive(argv)
    print(text)
    if unknown:
        print("Unknown traits: " + ", ".join(unknown) + ". Run --traits to see the list.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
