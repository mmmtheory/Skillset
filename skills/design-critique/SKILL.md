---
name: design-critique
description: Gives an honest, rubric-based critique of a UI design such as a screen, flow, page, component, prototype or Figma frame, including a design the agent just made. Use when someone asks for a design review, critique, feedback, a UX or accessibility audit, whether a design is good or ready to ship, or what to improve. Looks at the rendered result, measures contrast, and returns severity-ranked findings with concrete fixes. Not for code style review, copy-only edits or writing a brief.
license: MIT
metadata:
  author: Matthias Schmutz
  version: "0.1.0"
---

# Design critique

A good critique tells the designer what will hurt users most, why, and what to do about it, in that order. It is specific enough to act on and honest enough to be worth asking for.

Without this skill, agents tend to:

- open with praise, bury the problems, and close with more praise
- review the code or a description instead of looking at the rendered design
- list thirty issues at equal weight, so nothing gets fixed
- state taste as if it were a rule, and rules as if they were taste
- guess at contrast instead of measuring it
- miss the states nobody drew: empty, loading, error, long content
- judge their own output generously

## Workflow

### 1. Establish what the design is for

Pull from the conversation and files: what it is, who uses it, the job it must do, and the stage.

- **Exploration**: critique direction, structure and fit to the goal. Skip pixel polish.
- **Refinement**: everything, weighted toward hierarchy, flow and states.
- **Pre-ship**: everything, with accessibility and states weighted highest.

If the project has a `DESIGN.md` (written by the design-system-bridge skill or by hand), read it first and score System consistency against its tokens and component rules.

If the goal or stage is not stated, assume from context, say your assumption in one line at the top, and carry on. Do not stop to ask unless the design could serve two very different goals and the critique would flip between them.

### 2. Look at it

Critique what users will see. In order of preference:

1. a screenshot or image the person supplied
2. the frame itself, through a connected design tool (with the Figma MCP server, `get_screenshot` on the node)
3. the live page in a browser tool, at a phone width (about 390 px) and a desktop width (about 1440 px)
4. render the code yourself if you can run it

If you cannot see the design at all, say so in the first line, critique what you can from the code or description, and mark visual findings as unconfirmed.

Look at it twice: once at a glance, as a user arriving cold (what draws the eye first, second, third?), then slowly, region by region.

### 3. Measure what can be measured

Do not eyeball numbers that a tool can give you.

```bash
python scripts/contrast_check.py "#6b7280" "#ffffff" --size 14
python scripts/contrast_check.py --pairs pairs.txt
```

The script reports the WCAG 2.2 contrast ratio and pass or fail for normal text, large text and non-text elements. Use colours from the CSS, tokens or design file. If you only have an image, sample the colours you can read and say they are sampled.

Measure tap target sizes, body text size and line length when you have dimensions. Thresholds are in [references/checks.md](references/checks.md).

### 4. Score against the rubric

Score each dimension in [references/rubric.md](references/rubric.md) from 1 to 4 using its anchors. The anchors exist so scores mean the same thing every time. A 4 is rare and has to be earned; most solid professional work scores 3 on most dimensions.

Mark a dimension "not assessed" when you could not see enough to judge it. Never fill it in with a guess.

### 5. Write the findings

Each finding has:

- **Severity**: Blocker, Major, Minor or Polish (definitions in the rubric)
- **Where**: the screen region or element, precise enough to find in five seconds
- **Problem**: what is wrong, observed rather than inferred
- **Why it matters**: the effect on the user, or the principle or standard it breaks (cite the WCAG criterion number for accessibility)
- **Fix**: a concrete change. "Increase contrast" is not a fix. "Darken the helper text to #4b5563 (7.5:1)" is.

Rank findings by severity, then by how many users they affect. Report up to ten in full. Put the rest in a one-line-each polish list.

Separate rules from judgement. A WCAG failure is a fact. "The hero feels crowded" is a judgement: say it, give the reason, and label it as your view.

Check the states nobody drew. If the design shows only the happy path, list the missing states that matter for this screen as findings, using the state checklist in [references/checks.md](references/checks.md).

### 6. Name what to keep

List two or three specific things that work and should survive the next iteration, each with the reason. Only include strengths that are real. "Clean design" is not a strength. "The single primary action per step keeps the flow obvious" is.

## Output

```markdown
**Verdict:** Ready / Ready after fixes / Needs another pass / Rethink the approach
One or two sentences on why.

**Assumed:** goal, audience, stage (only if not given)

| Dimension | Score | Note |
| --- | --- | --- |

### Findings
1. **[Severity] Where:** Problem. Why it matters. **Fix:** ...

### Polish
- one line each

### Keep
- strength, and why it works
```

Lead with the verdict, not with compliments. Do not close with a summary or encouragement.

## Reviewing your own work

When the design is one you just produced, review it with the same rubric and the same severity bar, and do not soften it. Fix Blockers and Majors before showing it, then show the critique of the revised version. If you would not ship it, say so.

## Tone

Direct, specific and respectful. Critique the design, never the designer. Plain words, no em dashes, no filler. If the person writes in another language, critique in that language.
