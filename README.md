# skillset

Agent skills for designing with AI.

Each skill targets a point where agents reliably fall short of a senior designer: framing the problem, making sense of research, and judging their own work. Each one ships with the eval set used to prove it helps, so you can check the claim yourself.

Built to the open [Agent Skills](https://agentskills.io) format, so the same folder works in Claude, Claude Code, Cursor, Codex and other agents that read `SKILL.md`.

## Skills

| Skill | Use it when | Status |
| --- | --- | --- |
| [design-brief](skills/design-brief/SKILL.md) | A request is vague and you want a sharp brief before anyone designs | In evaluation |
| [research-synthesis](skills/research-synthesis/SKILL.md) | You have interview notes or transcripts and need findings a team will trust | In evaluation |
| [design-critique](skills/design-critique/SKILL.md) | You want an honest, rubric-based review of a screen, flow or page | In evaluation |

"In evaluation" means the skill is complete and its eval set is written, but lift against the no-skill baseline has not been published yet. Results will appear on each skill's page at [matthiasschmutz.com/labs](https://matthiasschmutz.com/labs).

## Install

With the skills CLI:

```bash
npx skills add mmmtheory/skillset --skill design-critique
```

By hand, copy a skill folder into your agent's skills directory:

- Claude Code: `~/.claude/skills/` (all projects) or `.claude/skills/` (one project)
- Cross-agent convention: `.agents/skills/`
- Claude apps: zip the skill folder and upload it in your skills settings

Skills load on their own when a request matches their description. You can also ask for one by name.

## How the skills are tested

Every skill is run on its eval cases with and without the skill loaded, three times each, across more than one agent. A separate grader scores both runs against written assertions. A skill ships only when it clears the thresholds in [CONTRIBUTING.md](CONTRIBUTING.md), including a lift of at least 25 points over the baseline.

Run the cases yourself with Claude Code, from inside a skill folder:

```bash
claude plugin eval . --allow-tools Write,Edit,Bash --scaffold
```

These are real, billed model runs.

## Structure

```
skills/
  <skill-name>/
    SKILL.md         instructions the agent reads when the skill triggers
    references/      detail loaded only when needed
    scripts/         deterministic helpers (run, not read)
    evals/           one folder per test case
tools/
  validate.py        structure and style checks, run in CI
```

## License

MIT. Fork it, adapt it for your team, and tell me what breaks.

Made by [Matthias Schmutz](https://matthiasschmutz.com).
