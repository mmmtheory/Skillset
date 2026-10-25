# Contributing

This collection stays small on purpose. A skill earns its place by making an agent measurably better at a design task, not by covering a topic.

## Authoring rules

1. **Start from a failure.** Run the task without any skill first. Write down what the agent got wrong. Every instruction in a skill should trace back to one of those failures.
2. **Keep SKILL.md lean.** Under 500 lines. It routes; `references/` holds the detail, linked one level deep.
3. **Write the description for real requests.** Name and description are all an agent sees before deciding to load a skill. Use the words people actually type, say when to use it, and say what it is not for.
4. **Script what is deterministic.** Contrast ratios, counts and file checks belong in `scripts/`, with a `--selftest` flag.
5. **Open spec only.** Use the frontmatter fields in the [Agent Skills spec](https://agentskills.io). Agent-specific notes go in a reference file.
6. **Write like a person.** No em dashes, no stock AI phrasing, no closing summaries. `tools/validate.py` checks the first two.

## Eval cases

Each case is a folder under `evals/` in the layout `claude plugin eval` reads:

```
evals/<case-name>/
  prompt.md          settings block, then the prompt exactly as a user would type it
  case.yaml          schema version, name, expected outcome
  graders/
    01-<check>.md    one checkable statement per file
  files/             optional inputs, copied in by place-files.sh
```

Good cases are ones the agent fails without the skill. Mix typical requests, edge cases and at least one prompt where the skill should hold back or push back. Each skill needs at least 12 cases.

Graders state one observable fact each ("The brief lists at least two anti-goals"), never a judgement call ("The brief is good"). Taste goes to the blind review below.

### Held-out cases

Four cases per skill are written by designers outside the authoring loop and kept out of this repository, so the skill cannot be tuned to them. They run in the same harness at release time.

## Ship thresholds

| Measure | Threshold |
| --- | --- |
| Grader pass rate, with skill | 85% or higher |
| Lift over the no-skill baseline | +25 points or more |
| Held-out pass rate | Within 10 points of the main set |
| Trigger accuracy on 20 test queries | 90% or higher, no false triggers on adjacent tasks |
| Blind review preference (critique, copy and brand skills) | Preferred in at least 2 of 3 comparisons |
| SKILL.md size | Under 500 lines |

Every run uses an independent grader. The agent that produced the output never grades it.

A skill with near-zero lift is cut or narrowed. A short skill that works beats a long one that restates what the model already knows.

## Before you open a pull request

```bash
pip install pyyaml
python tools/validate.py
```

CI runs the same check, plus each script's self-test.
