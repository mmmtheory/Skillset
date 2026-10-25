#!/usr/bin/env python3
"""Structure and style checks for every skill in skills/.

Run from the repository root:  python tools/validate.py
Exits with status 1 if any check fails.
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
PROMPT_KEYS = {"tags", "max_turns", "timeout_seconds", "allowed_tools"}
RESERVED_CASES = {"results", "mocks", "node_modules", "files", "true", "false", "null"}
MIN_CASES = 12
MAX_BODY_LINES = 500

# Characters and phrases that read as machine-written copy.
BANNED_CHARS = {"—": "em dash", "–": "en dash"}
BANNED_PHRASES = [
    "delve", "tapestry", "it's worth noting", "it is worth noting",
    "in today's fast-paced", "game-changer", "game changer",
    "elevate your", "unlock the power", "seamlessly", "in conclusion",
]
STYLE_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".sh", ".txt"}

errors: list[str] = []


def fail(path: Path, msg: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {msg}")


def split_frontmatter(text: str):
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 4:].lstrip("\n")


def check_skill(skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        fail(skill_dir, "missing SKILL.md")
        return
    for extra in ("README.md", "CHANGELOG.md"):
        if (skill_dir / extra).exists():
            fail(skill_dir / extra, "skills hold no README or CHANGELOG; put notes in the repo root")

    raw, body = split_frontmatter(skill_md.read_text(encoding="utf-8"))
    if raw is None:
        fail(skill_md, "no YAML frontmatter")
        return
    try:
        meta = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        fail(skill_md, f"frontmatter is not valid YAML: {exc}")
        return

    unknown = set(meta) - SPEC_KEYS
    if unknown:
        fail(skill_md, f"frontmatter keys outside the open spec: {sorted(unknown)}")

    name = meta.get("name", "")
    if name != skill_dir.name:
        fail(skill_md, f"name '{name}' must match folder '{skill_dir.name}'")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", str(name)) or len(str(name)) > 64:
        fail(skill_md, "name must be lowercase kebab-case, 64 characters at most")
    if any(word in str(name) for word in ("claude", "anthropic")):
        fail(skill_md, "name must not contain 'claude' or 'anthropic'")

    desc = str(meta.get("description", ""))
    if not desc:
        fail(skill_md, "description is empty")
    if len(desc) > 1024:
        fail(skill_md, f"description is {len(desc)} characters; limit is 1024")
    if "<" in desc or ">" in desc:
        fail(skill_md, "description must not contain angle brackets")

    body_lines = body.count("\n") + 1
    if body_lines >= MAX_BODY_LINES:
        fail(skill_md, f"body is {body_lines} lines; keep it under {MAX_BODY_LINES}")

    for ref in sorted(set(re.findall(r"\b((?:references|scripts|assets)/[\w./-]+\w)", body))):
        if not (skill_dir / ref).exists():
            fail(skill_md, f"links to {ref}, which does not exist")

    for ref_file in (skill_dir / "references").glob("**/*"):
        if ref_file.is_file() and ref_file.parent != skill_dir / "references":
            fail(ref_file, "keep references one level deep")

    check_evals(skill_dir)


def check_evals(skill_dir: Path) -> None:
    evals = skill_dir / "evals"
    if not evals.is_dir():
        fail(skill_dir, "missing evals/")
        return
    cases = [p for p in sorted(evals.iterdir()) if p.is_dir() and p.name not in {"results", "files"}]
    if len(cases) < MIN_CASES:
        fail(evals, f"{len(cases)} cases; need at least {MIN_CASES}")
    for case in cases:
        check_case(case)


def check_case(case: Path) -> None:
    if case.name in RESERVED_CASES or not re.fullmatch(r"[a-z][a-z0-9-]*", case.name):
        fail(case, "case names are lowercase letters, digits and hyphens, starting with a letter")

    prompt = case / "prompt.md"
    if not prompt.exists():
        fail(case, "missing prompt.md")
    else:
        raw, body = split_frontmatter(prompt.read_text(encoding="utf-8"))
        if raw is None:
            fail(prompt, "missing settings block")
        else:
            settings = yaml.safe_load(raw) or {}
            unknown = set(settings) - PROMPT_KEYS
            if unknown:
                fail(prompt, f"unknown settings keys {sorted(unknown)} make the case fail to load")
        if not body.strip():
            fail(prompt, "prompt is empty")

    case_yaml = case / "case.yaml"
    if not case_yaml.exists():
        fail(case, "missing case.yaml")
    else:
        text = case_yaml.read_text(encoding="utf-8")
        data = yaml.safe_load(text) or {}
        if not re.search(r'^schema_version:\s*["\']', text, re.M):
            fail(case_yaml, "schema_version must be a quoted string")
        if data.get("name") != case.name:
            fail(case_yaml, "name must match the folder")
        if not str(data.get("expected_outcome", "")).strip():
            fail(case_yaml, "expected_outcome is empty")
        if (case / "files").is_dir():
            script = (data.get("context") or {}).get("scaffold_script")
            if script != "place-files.sh" or not (case / "place-files.sh").exists():
                fail(case, "cases with files/ need place-files.sh named in case.yaml context")

    graders = sorted((case / "graders").glob("*.md")) if (case / "graders").is_dir() else []
    if not graders:
        fail(case, "needs at least one grader")
    for grader in graders:
        if not re.fullmatch(r"\d{2}-[a-z0-9-]+\.md", grader.name):
            fail(grader, "grader files are named NN-few-words.md")
        raw, body = split_frontmatter(grader.read_text(encoding="utf-8"))
        if raw is None or "type:" not in raw:
            fail(grader, "missing grader block; the CLI ignores it")
        if not body.strip():
            fail(grader, "grader statement is empty")


def check_style() -> None:
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in STYLE_SUFFIXES:
            continue
        if any(part.startswith(".") and part != ".github" for part in path.relative_to(ROOT).parts):
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8")
        # Eval input files may plant the very patterns a skill is meant to fix.
        planted = "evals" in path.parts and "files" in path.parts
        for char, label in ({} if planted else BANNED_CHARS).items():
            if char in text:
                line = text[: text.index(char)].count("\n") + 1
                fail(path, f"line {line}: {label}; rewrite the sentence")
        if path.suffix == ".md" and "evals" not in path.parts:
            # Phrases quoted as code (`like this`) are examples, not copy.
            prose = re.sub(r"```.*?```", "", text, flags=re.S)
            prose = re.sub(r"`[^`\n]*`", "", prose)
            lower = prose.lower()
            for phrase in BANNED_PHRASES:
                if phrase in lower:
                    fail(path, f"stock phrase '{phrase}'")


def main() -> int:
    if not SKILLS.is_dir():
        sys.exit("no skills/ directory found")
    skill_dirs = [p for p in sorted(SKILLS.iterdir()) if p.is_dir()]
    for skill_dir in skill_dirs:
        check_skill(skill_dir)
    check_style()

    if errors:
        print(f"{len(errors)} problem(s):")
        for err in errors:
            print(f"  {err}")
        return 1
    print(f"OK: {len(skill_dirs)} skills pass structure and style checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
