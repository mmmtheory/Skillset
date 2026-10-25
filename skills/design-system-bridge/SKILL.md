---
name: design-system-bridge
description: Creates, updates and checks a DESIGN.md so agents build with a real design system instead of guessing, and keeps it in sync with Figma variables, DTCG token files and CSS. Use when someone asks to write or update a DESIGN.md, extract a design system from Figma, a codebase or a site, convert tokens to or from DTCG JSON, check tokens for drift, or make agents follow their design system. Not for designing a new visual identity from scratch or reviewing a single screen.
license: MIT
metadata:
  author: Matthias Schmutz
  version: "0.1.0"
---

# Design system bridge

A design system lives in three places at once: the design file, the code, and whatever the agent reads. When they disagree, the agent guesses, and the product drifts. This skill makes one DESIGN.md the readable source for agents and keeps it honest against the other two.

Without this skill, agents tend to:

- invent tokens that sound plausible ("primary-600", "spacing-lg") instead of reading the real ones
- copy hex values from a screenshot and call them the system
- write a DESIGN.md that lists tokens but never says when to use them
- fill sections with confident rules nobody decided
- convert to DTCG in a shape that no tool reads, such as colours as bare strings
- update one source and leave the others behind without saying so

This skill exists to stop those six things.

## Workflow

### 1. Find every source

Look for each of these and note which exist:

- **Design file.** With the Figma MCP server connected, use `get_variable_defs` on the relevant frames or the library page, and `get_screenshot` to see components in use. Without it, ask for an export or screenshots.
- **Code.** CSS custom properties, a Tailwind config, a theme file, a tokens folder, component styles.
- **Tokens file.** DTCG JSON, Style Dictionary or Tokens Studio output.
- **An existing DESIGN.md.**

Treat the source the team actually ships from as the truth for values, usually the code or the tokens file. Treat the design file as the truth for intent. When they disagree, report it; don't pick a winner silently.

### 2. Extract, never invent

Take token names and values exactly as they appear. Keep the team's names, even odd ones. If a category has no tokens (no spacing scale, say), write that it is undefined. Don't make one up. If the person asks you to propose missing tokens, put proposals in a clearly marked list under Do's and Don'ts, separate from the real system.

### 3. Write DESIGN.md

Use the format in [references/design-md.md](references/design-md.md): YAML front matter for tokens (`colors`, `typography`, `rounded`, `spacing`, `components`, with `{category.token}` references), then the prescribed `##` sections in order: Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts.

The body is where judgement goes. For each section, say when to use what and what to avoid, using the team's own words where they exist. Mark anything you inferred rather than read as *Inferred*, so the team can confirm it. The most useful sections for agents are Components (which component for which job) and Do's and Don'ts (the mistakes this system keeps seeing).

Keep it under about 1,500 words. An agent reads the whole file every time.

### 4. Check it

```bash
python scripts/tokens.py lint DESIGN.md
```

This catches broken references, invalid values, missing or out-of-order sections, and components whose text fails contrast on their own background (WCAG 1.4.3). Fix each problem, or explain it in Do's and Don'ts if it is a known, deliberate exception. If Google's DESIGN.md CLI is installed, run its linter too; the format is still changing.

### 5. Convert when asked

```bash
python scripts/tokens.py to-dtcg DESIGN.md --out tokens.json
python scripts/tokens.py to-md tokens.json --out DESIGN.md --name "Acme"
```

`to-dtcg` writes the DTCG 2025.10 format: colours as objects with `colorSpace`, `components` and `hex`, dimensions as `value` and `unit`, typography as composite tokens, references kept as `{colors.primary}`. Details in [references/dtcg.md](references/dtcg.md). `to-md` gives a DESIGN.md skeleton; its sections still need writing.

### 6. Report drift

```bash
python scripts/tokens.py drift DESIGN.md tokens.json src/styles/tokens.css figma-variables.json
```

The report lists tokens missing from a source and values that disagree, with each source's value. Present it as a table: token, each source's value, and a recommended fix with which source should change. Never edit the code or the design file to resolve drift unless the person asked you to; the drift report is the deliverable.

Save Figma variables as flat JSON (`{"color/primary": "#1a3a52"}`) before running drift, so they can be compared.

## Output

Deliver the DESIGN.md (or the converted file), then a short note listing: sources read, anything inferred, lint results, and drift found. No closing summary.

Write plainly. No em dashes, no marketing language about the system.
