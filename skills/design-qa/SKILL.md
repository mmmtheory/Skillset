---
name: design-qa
description: Checks a built interface against its design before release. Compares the running page or app to the Figma frame, mockup or DESIGN.md, finds values hard-coded outside the design system, missing states, broken breakpoints and interaction gaps, and returns a ranked punch list with exact fixes in the code. Use when someone asks for design QA, visual QA, a design sign-off, an implementation review, whether the build matches the design, or to check UI that a developer or agent just built. Not for judging whether the design itself is good (use design-critique) or for code style review.
license: MIT
metadata:
  author: Matthias Schmutz
  version: "0.1.0"
---

# Design QA

Design QA answers one question: does what we built match what we meant, everywhere people will meet it? The output is a punch list a developer can work through in an afternoon, and a list of gaps to send back to design.

Without this skill, agents tend to:

- read the code, see the right class names, and declare that it matches without ever rendering it
- check one viewport in the default state and call it done
- miss values that look right but are hard-coded (`#111827` typed in place of the `ink` token), which break the next time the theme changes
- report a 1 px nudge with the same weight as the wrong component
- "fix" the build toward a design that is itself stale or wrong
- write "adjust the spacing" instead of naming the file, the line and the value
- check their own build generously

## Workflow

### 1. Find the source of truth

QA needs something to compare against. In order of authority:

1. the design frame for this screen (with the Figma MCP server: `get_screenshot` and `get_design_context` on the node, `get_variable_defs` for its tokens)
2. the project's `DESIGN.md`, token files or design system docs
3. a mockup image, spec or ticket with acceptance criteria
4. the existing product, when the work is meant to extend it consistently

Say in one line which sources you used. If there is no design for a screen, QA it against the system only and say so. If two sources disagree (the frame uses a colour the tokens do not have), that is a finding in itself, not something to resolve silently.

### 2. Render the build

Look at what users will get, not at the code. Use a browser tool, Playwright or the app itself. Capture each screen at the breakpoints the design defines, or at 390, 768 and 1440 px wide if it defines none. Setup notes are in [references/capture.md](references/capture.md).

Compare like with like. Load the same content the design shows (names, numbers, list lengths) so differences come from the build, not from the data. Then load realistic worst cases: long names, large numbers, empty lists, translated strings.

If you cannot run the build, say so in the first line, review the code against the source, and mark every visual finding as unconfirmed.

### 3. Compare, one pass at a time

Work through the passes in [references/qa-checklist.md](references/qa-checklist.md): layout and spacing, typography, colour, components, content, icons and images, states, interaction, motion, responsive behaviour and accessibility basics. One pass at a time catches more than one long look, because each pass asks the eye a single question.

Measure rather than estimate. Read computed styles in the browser, measure spacing from the DOM, and run the contrast script from design-critique if it is installed, or calculate the ratio.

### 4. Scan the code for drift

```bash
python scripts/token_drift.py --tokens DESIGN.md src/
python scripts/token_drift.py --tokens tokens.json --tokens theme.css src/components --json
```

The script reads tokens from a DESIGN.md front matter, CSS custom properties or a DTCG JSON file, then finds colours, sizes, radii, spacing and font families written as literals. Each one is labelled:

- **hard-coded token**: the exact value of a token, typed instead of referencing it. Looks right today, breaks on the next theme change.
- **near token**: within a small distance of a token. Usually a typo or an eyeballed value.
- **off-system**: nothing close in the system. Either a real gap in the tokens or a mistake.

Treat the script's output as leads. A literal inside a token definition, a third-party override or an SVG path is often fine; say why you dismissed it.

### 5. Classify each difference

Before you call anything a bug, decide what kind of difference it is:

- **Build bug**: the design is clear and the build differs. Fix the code.
- **Design gap**: the design never specified this (a hover state, a long-name case, the tablet layout). The developer guessed. Report the guess and send the question to design.
- **Design is stale or wrong**: the build is better or the frame breaks a system rule. Do not change the code to match. Flag it for design to update.
- **Intentional**: a documented change (ticket, comment, decision record). Note it and move on.

### 6. Rate severity

Use the scale and tolerances in [references/severity.md](references/severity.md):

- **Blocker**: breaks a task, loses data, fails an accessibility minimum, or shows something false (wrong amount, wrong state).
- **Must fix**: visibly wrong component, state or layout that users will notice, or any hard-coded or off-system value in shared code.
- **Should fix**: noticeable drift from the design that does not hurt the task.
- **Nit**: sub-pixel or taste-level differences. Batch these into one line each.

A token mismatch is at least Should fix even when the pixels look identical, because it is the difference that will show up later.

### 7. Write the punch list

Each item has:

- **Where**: screen, viewport, state, and element, precise enough to find in five seconds
- **Expected**: what the source says, and which source
- **Actual**: what the build does, measured
- **Fix**: file and line, and the exact change (`padding: 12px` to `padding: var(--space-md)`)
- **Type**: build bug, design gap, stale design, or intentional

Order by severity, then by how many screens or users each affects. When one root cause produces many symptoms (a wrong base font size shifts every line), report the cause once and list the symptoms under it.

### 8. Re-check what you fix

If you were asked to fix the issues, fix Blockers and Must fixes first, then render again and confirm each one at every viewport you checked. Never mark something fixed from the diff alone.

## Output

```markdown
**Verdict:** Ready to ship / Ship after must-fixes / Not ready
One or two sentences on why.

**Compared against:** sources used, and anything missing
**Checked:** viewports x states actually rendered; anything not checked

### Punch list
1. **[Blocker] Where:** ... **Expected:** ... (source) **Actual:** ... **Fix:** `file:line` change. *Build bug*

### Drift
Summary of token_drift.py results: counts by label, the worst offenders, and dismissed items with reasons.

### Questions for design
- design gaps and stale frames, each with the decision needed

### Nits
- one line each
```

Do not pad the verdict with praise and do not close with a summary.

## QA of your own build

When you built the interface yourself, run the same passes, the same script and the same severity scale before you present it. Fix Blockers and Must fixes, render again, then show the QA of the revised build. If parts went unchecked, list them rather than implying they pass.

## Tone

Neutral and exact. Name the element and the value, not the person who built it. If the request is in another language, write the punch list in that language and keep code, file names and token names as they are.
