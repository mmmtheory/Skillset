#!/usr/bin/env python3
"""Index participant quotes in research transcripts, and verify quotes in a report.

  index   Split transcripts into utterances with participant and quote IDs.
          python quote_index.py index p01.txt p02.txt --out quotes.json

  verify  Check every quote in a report appears verbatim in the sources,
          spoken by the participant it is attributed to.
          python quote_index.py verify report.md --sources p01.txt p02.txt

Transcripts can be plain text or Markdown. Speaker labels such as
"Interviewer:", "P3:", "Sam:" or "[00:12:03] P3:" are recognised.
Moderator lines are excluded from the index. Files without any speaker
labels are treated as one participant's words, split by blank lines.

Participant IDs come from a speaker label like P3 or T1, else from the file
name (p03-interview.txt becomes P3), else they are assigned in file order.
CSV files (survey exports) give one quote per row, using an ID column such
as "respondent" and a text column such as "answer" when present.

Exit status: 0 when all quotes verify, 1 when any fail, 2 on usage errors.
Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import tempfile
from pathlib import Path

MODERATOR_LABELS = {
    "interviewer", "moderator", "researcher", "facilitator", "host",
    "int", "mod", "i", "q", "r", "me", "team",
    "interviewerin", "moderatorin", "forscher", "forscherin",
    "intervieweur", "intervieweuse", "entrevistador", "entrevistadora",
    "intervistatore", "intervistatrice",
}
TIMESTAMP = re.compile(r"^\s*\[?\(?\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\)?\]?\s*[-:]?\s*")
SPEAKER = re.compile(r"^\s*(?:\*\*)?([A-Za-z][\w .'\-]{0,30}?)(?:\*\*)?\s*:\s*(?:\*\*)?\s*(.*)$")
PID_LABEL = re.compile(r"^([a-z]{1,3})[-_ ]?(\d+)$", re.I)
PID_FILE = re.compile(r"(?:^|[^a-z])p[-_ ]?(\d+)(?:[^0-9]|$)", re.I)
QUOTE = re.compile(r"[\"“]([^\"“”]+?)[\"”]")
ATTRIBUTION = re.compile(r"^[\s,.;:)\]’'*_-]{0,6}(?:\(|\[)?\s*(P\d+)(?:-Q(\d+))?\b", re.I)
SPLIT_FRAGMENTS = re.compile(r"\.\.\.|…|\[[^\]]*\]")


def normalise(text: str) -> str:
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def trim_fragment(text: str) -> str:
    return normalise(text).strip(" .,;:!?\"'()-")


def label_id(match: re.Match) -> str:
    return f"{match.group(1).upper()}{int(match.group(2))}"


def sort_key(pid: str):
    match = re.match(r"([A-Z]+)(\d+)$", pid)
    return (match.group(1), int(match.group(2))) if match else (pid, 0)


ID_COLUMNS = ("respondent", "participant", "id", "respondent_id", "participant_id", "user", "user_id")
TEXT_COLUMNS = ("answer", "response", "comment", "text", "feedback", "verbatim", "quote")


def parse_csv(path: Path, fallback_pid: str) -> list[dict]:
    """One utterance per row. Picks an ID column and a free-text column by name, else guesses."""
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return []
    columns = list(rows[0].keys())
    lower = {c.lower().strip(): c for c in columns if c}
    id_col = next((lower[c] for c in ID_COLUMNS if c in lower), None)
    text_col = next((lower[c] for c in TEXT_COLUMNS if c in lower), None)
    if text_col is None:
        text_col = max(columns, key=lambda c: sum(len(r.get(c) or "") for r in rows))
    utterances = []
    for number, row in enumerate(rows, 2):
        text = (row.get(text_col) or "").strip()
        if not text:
            continue
        raw_id = (row.get(id_col) or "").strip() if id_col else ""
        match = PID_LABEL.match(raw_id)
        pid = label_id(match) if match else (f"R{number - 1}" if not raw_id else raw_id)
        utterances.append({"participant": pid, "speaker": pid, "moderator": False,
                           "line": number, "text": text})
    return utterances


def participant_from_file(path: Path) -> str | None:
    match = PID_FILE.search(path.stem)
    return f"P{int(match.group(1))}" if match else None


def parse_file(path: Path, fallback_pid: str, moderators: set[str]) -> list[dict]:
    """Return utterances as dicts: participant, speaker, moderator, line, text."""
    if path.suffix.lower() == ".csv":
        return parse_csv(path, fallback_pid)
    lines = path.read_text(encoding="utf-8").splitlines()
    file_pid = participant_from_file(path) or fallback_pid
    labelled = any(SPEAKER.match(TIMESTAMP.sub("", ln)) for ln in lines if ln.strip())

    utterances: list[dict] = []
    if not labelled:
        buffer: list[str] = []
        start = 0
        for number, line in enumerate(lines + [""], 1):
            if line.strip() and not line.lstrip().startswith("#"):
                if not buffer:
                    start = number
                buffer.append(line.strip())
            elif buffer:
                utterances.append({"participant": file_pid, "speaker": file_pid,
                                   "moderator": False, "line": start, "text": " ".join(buffer)})
                buffer = []
        return utterances

    current = None
    for number, raw in enumerate(lines, 1):
        line = TIMESTAMP.sub("", raw)
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = SPEAKER.match(line)
        if match:
            label, rest = match.group(1).strip(), match.group(2).strip()
            is_mod = label.lower() in moderators
            pid_match = PID_LABEL.match(label)
            pid = label_id(pid_match) if pid_match else file_pid
            current = {"participant": None if is_mod else pid, "speaker": label,
                       "moderator": is_mod, "line": number, "text": rest}
            utterances.append(current)
        elif current is not None:
            current["text"] = (current["text"] + " " + line.strip()).strip()
    return [u for u in utterances if u["text"]]


def build_index(paths: list[Path], moderators: set[str]) -> dict:
    quotes: list[dict] = []
    counters: dict[str, int] = {}
    used_ids = {pid for pid in (participant_from_file(p) for p in paths) if pid}
    next_auto = 1
    for path in paths:
        fallback = None
        if not participant_from_file(path):
            while f"P{next_auto}" in used_ids:
                next_auto += 1
            fallback = f"P{next_auto}"
            used_ids.add(fallback)
        for utt in parse_file(path, fallback or "P0", moderators):
            entry = {"source": str(path), "line": utt["line"], "speaker": utt["speaker"],
                     "moderator": utt["moderator"], "text": utt["text"]}
            if not utt["moderator"]:
                pid = utt["participant"]
                counters[pid] = counters.get(pid, 0) + 1
                entry["participant"] = pid
                entry["id"] = f"{pid}-Q{counters[pid]}"
            quotes.append(entry)
    return {"participants": sorted(counters, key=sort_key),
            "counts": counters, "quotes": quotes}


def find_in_order(fragments: list[str], haystack: str) -> bool:
    position = 0
    for fragment in fragments:
        found = haystack.find(fragment, position)
        if found == -1:
            return False
        position = found + len(fragment)
    return True


def extract_report_quotes(report: str, min_words: int) -> list[dict]:
    report = re.sub(r"```.*?```", "", report, flags=re.S)
    found = []
    for match in QUOTE.finditer(report):
        text = match.group(1)
        if len(text.split()) < min_words:
            continue
        tail = report[match.end(): match.end() + 40]
        attr = ATTRIBUTION.match(tail)
        found.append({
            "text": text,
            "participant": label_id(PID_LABEL.match(attr.group(1))) if attr else None,
            "quote_number": int(attr.group(2)) if attr and attr.group(2) else None,
            "line": report[: match.start()].count("\n") + 1,
        })
    return found


def verify(report_path: Path, index: dict, min_words: int) -> list[str]:
    by_participant: dict[str, str] = {}
    by_id: dict[str, str] = {}
    moderator_text = []
    for q in index["quotes"]:
        norm = normalise(q["text"])
        if q["moderator"]:
            moderator_text.append(norm)
            continue
        by_participant[q["participant"]] = by_participant.get(q["participant"], "") + " ‖ " + norm
        by_id[q["id"]] = norm
    everyone = " ‖ ".join(by_participant.values())
    moderators = " ‖ ".join(moderator_text)

    problems = []
    quotes = extract_report_quotes(report_path.read_text(encoding="utf-8"), min_words)
    for q in quotes:
        fragments = [f for f in (trim_fragment(x) for x in SPLIT_FRAGMENTS.split(q["text"])) if f]
        if not fragments:
            continue
        where = f"line {q['line']}: \"{q['text'][:60]}{'...' if len(q['text']) > 60 else ''}\""
        if q["participant"] and q["quote_number"]:
            qid = f"{q['participant']}-Q{q['quote_number']}"
            if qid in by_id and find_in_order(fragments, by_id[qid]):
                continue
            if find_in_order(fragments, by_participant.get(q["participant"], "")):
                problems.append(f"{where} is {q['participant']}'s words but not from {qid}")
                continue
        elif q["participant"]:
            if find_in_order(fragments, by_participant.get(q["participant"], "")):
                continue
        elif find_in_order(fragments, everyone):
            continue

        if q["participant"] and find_in_order(fragments, everyone):
            problems.append(f"{where} is attributed to {q['participant']} but someone else said it")
        elif find_in_order(fragments, moderators):
            problems.append(f"{where} comes from the moderator, not a participant")
        else:
            problems.append(f"{where} does not appear verbatim in the sources")
    print(f"Checked {len(quotes)} quote(s) of {min_words}+ words; {len(problems)} problem(s).")
    return problems


def selftest() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "p01-call.txt").write_text(
            "Interviewer: How do you track invoices?\n"
            "P1: Honestly I keep a paper list on the fridge.\n"
            "It's the only thing I trust.\n"
            "Interviewer: Why the fridge?\n"
            "P1: Because I walk past it every single morning before work.\n", encoding="utf-8")
        (d / "notes-sam.md").write_text(
            "# Session notes\n\nSam said the export button is impossible to find on mobile.\n\n"
            "He gave up and emailed support instead.\n", encoding="utf-8")
        index = build_index([d / "p01-call.txt", d / "notes-sam.md"], MODERATOR_LABELS)
        ids = [q.get("id") for q in index["quotes"] if not q["moderator"]]
        assert index["participants"] == ["P1", "P2"], index["participants"]
        assert ids == ["P1-Q1", "P1-Q2", "P2-Q1", "P2-Q2"], ids
        assert "It's the only thing I trust." in index["quotes"][1]["text"]

        good = d / "good.md"
        good.write_text(
            "> “I keep a paper list on the fridge. It’s the only thing I trust.” (P1-Q1)\n\n"
            "> \"I walk past it every single morning\" (P1)\n\n"
            "> \"Honestly I keep a paper list ... the only thing I trust\" (P1-Q1)\n\n"
            "Short \"quote here\" is ignored.\n", encoding="utf-8")
        assert verify(good, index, 4) == [], "good report should pass"

        bad = d / "bad.md"
        bad.write_text(
            "> \"I keep a spreadsheet on my laptop for everything\" (P1)\n\n"
            "> \"the export button is impossible to find\" (P1)\n\n"
            "> \"How do you track invoices\" (P2)\n\n"
            "> \"I walk past it every single morning\" (P1-Q1)\n", encoding="utf-8")
        problems = verify(bad, index, 4)
        assert len(problems) == 4, problems
        assert "does not appear verbatim" in problems[0]
        assert "someone else said it" in problems[1]
        assert "moderator" in problems[2]
        assert "not from P1-Q1" in problems[3]

        (d / "survey.csv").write_text(
            "respondent,plan,answer\nR1,free,I never know which plan I am on\n"
            "R2,pro,Calendar sync drops out and I lose a day\n", encoding="utf-8")
        (d / "t1.txt").write_text(
            "Interviewerin: Wie oft passiert das?\nT1: Vielleicht jede zweite Woche, ehrlich gesagt.\n",
            encoding="utf-8")
        index2 = build_index([d / "survey.csv", d / "t1.txt"], MODERATOR_LABELS)
        ids2 = [q["id"] for q in index2["quotes"] if not q["moderator"]]
        assert ids2 == ["R1-Q1", "R2-Q1", "T1-Q1"], ids2
        mixed = d / "mixed.md"
        mixed.write_text(
            "> \"Calendar sync drops out and I lose a day\" (R2)\n\n"
            "> \"Vielleicht jede zweite Woche\" (T1)\n", encoding="utf-8")
        assert verify(mixed, index2, 4) == [], "csv and labelled IDs should verify"
    print("selftest passed")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="build a quote index from transcripts")
    p_index.add_argument("sources", nargs="+", type=Path)
    p_index.add_argument("--out", type=Path, default=Path("quotes.json"))
    p_index.add_argument("--moderator", default="", help="extra moderator labels, comma separated")

    p_verify = sub.add_parser("verify", help="check quotes in a report against the sources")
    p_verify.add_argument("report", type=Path)
    p_verify.add_argument("--sources", nargs="+", type=Path, required=True)
    p_verify.add_argument("--moderator", default="", help="extra moderator labels, comma separated")
    p_verify.add_argument("--min-words", type=int, default=4, help="ignore quoted strings shorter than this")

    args = parser.parse_args(argv)
    moderators = MODERATOR_LABELS | {m.strip().lower() for m in args.moderator.split(",") if m.strip()}
    sources = args.sources
    missing = [str(p) for p in sources if not p.is_file()]
    if missing:
        print(f"not found: {', '.join(missing)}", file=sys.stderr)
        return 2
    index = build_index(sources, moderators)

    if args.command == "index":
        args.out.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
        counts = ", ".join(f"{p}: {index['counts'][p]}" for p in index["participants"])
        print(f"Indexed {len(index['participants'])} participant(s) ({counts}) into {args.out}")
        mapping = {}
        for q in index["quotes"]:
            if not q["moderator"]:
                mapping.setdefault(q["source"], set()).add(q["participant"])
        for source, pids in mapping.items():
            print(f"  {source} -> {', '.join(sorted(pids, key=sort_key))}")
        return 0

    if not args.report.is_file():
        print(f"not found: {args.report}", file=sys.stderr)
        return 2
    problems = verify(args.report, index, args.min_words)
    for problem in problems:
        print(f"  {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
