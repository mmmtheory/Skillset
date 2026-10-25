# skillset

Agent skills for designing with AI.

Each skill targets a point where agents reliably fall short of a senior designer: framing the problem, making sense of research, judging their own work, following a real design system, designing for agents, writing like a person, and deciding what a brand stands for. Each one ships with the eval set used to prove it helps, so you can check the claim yourself.

Built to the open [Agent Skills](https://agentskills.io) format, so the same folder works in Claude, Claude Code, Cursor, Codex and other agents that read `SKILL.md`.

## Skills

| Skill | Use it when | Status |
| --- | --- | --- |
| [design-brief](skills/design-brief/SKILL.md) | A request is vague and you want a sharp brief before anyone designs | In evaluation |
| [research-synthesis](skills/research-synthesis/SKILL.md) | You have interview notes or transcripts and need findings a team will trust | In evaluation |
| [design-critique](skills/design-critique/SKILL.md) | You want an honest, rubric-based review of a screen, flow or page | In evaluation |
| [design-system-bridge](skills/design-system-bridge/SKILL.md) | You want agents to build with your real design system, or your Figma, tokens and CSS have drifted apart | In evaluation |
| [agentic-ux](skills/agentic-ux/SKILL.md) | You're designing or reviewing an AI feature that acts on someone's behalf | In evaluation |
| [human-copy](skills/human-copy/SKILL.md) | You need interface copy in your brand's voice, without the tells of generated text | In evaluation |
| [brand-strategy](skills/brand-strategy/SKILL.md) | You need positioning, a brand platform or a tone of voice, written as a BRAND.md other tools can read | In evaluation |
| [brand-architecture](skills/brand-architecture/SKILL.md) | You're deciding whether something gets its own brand, or your product names have become a mess | In evaluation |

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

## Skills that work together

- **brand-strategy** writes a `BRAND.md`. **human-copy** reads its voice rules and avoid list, and its linter enforces them.
- **design-system-bridge** writes a `DESIGN.md`. **design-critique** checks screens against it.

[DESIGN.md Studio](https://matthiasschmutz.com/#studio) builds a starting DESIGN.md in the browser from your tokens.

## How the skills are tested

Every skill is run on its eval cases with and without the skill loaded, three times each, across more than one agent. A separate grader scores both runs against written assertions. A skill ships only when it clears the thresholds in [CONTRIBUTING.md](CONTRIBUTING.md), including a lift of at least 25 points over the baseline.

Results are recorded in the [Skill Bench](bench/README.md). `python tools/bench.py report` prints the latest run for every skill and whether it clears the bar.

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
bench/
  results.json       Skill Bench results, one entry per skill
tools/
  validate.py        structure and style checks, run in CI
  bench.py           records runs and checks them against the ship bar
```

## License

MIT. Fork it, adapt it for your team, and tell me what breaks.

Made by [Matthias Schmutz](https://matthiasschmutz.com).
