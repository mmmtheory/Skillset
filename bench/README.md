# Skill Bench

Every skill in this repository is measured the same way, and the results live in `results.json` so anyone can check them.

## Method

1. Run each skill's eval cases with and without the skill loaded, three times per case, on more than one agent.
2. A separate agent grades every run against the case's written assertions. The agent that did the work never grades it.
3. Run the four held-out cases, which are kept outside this repository.
4. Test triggering on 20 realistic requests, half of which should not load the skill.
5. For design-critique, human-copy and the brand skills, two designers compare outputs blind and pick the better one in three comparisons.

With Claude Code, step 1 is one command from inside a skill folder:

```bash
claude plugin eval . --allow-tools Write,Edit,Bash --scaffold
```

These are real, billed model runs.

## Recording a run

```bash
python tools/bench.py add design-critique --with 91 --without 52 --heldout 86 --trigger 95 \
  --agents claude-code,cursor,codex --blind 2/3 --report https://link-to-full-report
python tools/bench.py report
```

`add` stores the run with the skill's current version and prints whether it clears the ship bar. `report` prints the latest run for every skill as a table.

## Ship bar

| Measure | Threshold |
| --- | --- |
| Pass rate with the skill | 85% or higher |
| Lift over the no-skill baseline | +25 points or more |
| Held-out pass rate | Within 10 points of the main set |
| Trigger accuracy | 90% or higher |
| Blind review (critique, copy and brand skills) | Preferred in 2 of 3 |

A skill that misses the bar stays "In evaluation" until it clears it, or is narrowed or cut.
