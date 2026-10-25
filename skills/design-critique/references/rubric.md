# Critique rubric

Score each dimension 1 to 4. Use the anchors; do not average your impressions.

| Score | Meaning |
| --- | --- |
| 4 | Exemplary. Nothing worth changing at this stage. Rare. |
| 3 | Solid. Small issues only. |
| 2 | Works, with problems users will notice. |
| 1 | Fails its job or blocks some users. |

## Dimensions

**Goal fit.** Does the design help this user do this job?
- 4: the primary task is obvious within three seconds and nothing competes with it
- 3: primary task clear; some secondary content competes
- 2: primary task findable but not obvious; the design serves a different goal as much as the stated one
- 1: the primary task is hidden, missing or contradicted

**Hierarchy and scanning.** Does the eye land in the right order?
- 4: one clear entry point; order of attention matches order of importance
- 3: clear entry point; one or two elements out of order
- 2: several elements compete for first look
- 1: no discernible order, or the wrong thing dominates

**Layout and spacing.** Is there a consistent structure and rhythm?
- 4: consistent grid and spacing scale; grouping explains relationships without lines or boxes
- 3: mostly consistent; a few one-off gaps
- 2: spacing varies without reason; grouping unclear in places
- 1: elements placed arbitrarily; related items far apart or unrelated ones touching

**Typography.** Is text legible and does type carry the hierarchy?
- 4: limited, purposeful scale; body text 16 px or more on web; line length 45 to 80 characters
- 3: legible; scale slightly crowded or one awkward size
- 2: too many sizes or weights; small or low-contrast body text
- 1: illegible text, or hierarchy fights the content

**Colour and contrast.** Does colour carry meaning and meet contrast minimums?
- 4: all text and controls pass WCAG AA; colour never the only signal; restrained palette with clear roles
- 3: passes AA; colour roles mostly clear
- 2: some failures on secondary text or controls, or colour used decoratively where it implies meaning
- 1: body text or key controls fail contrast, or meaning relies on colour alone

**States and edge cases.** Are the unhappy paths designed?
- 4: empty, loading, error, partial and overflow states handled and helpful
- 3: most relevant states handled
- 2: happy path only, but the design would accommodate states without rework
- 1: missing states would break the layout or leave users stuck

**Interaction and feedback.** Do controls look like what they do, and does the system respond?
- 4: affordances clear; every action has visible feedback; destructive actions guarded and reversible
- 3: clear in general; one weak affordance or silent action
- 2: several controls ambiguous; feedback inconsistent
- 1: users cannot tell what is interactive or whether an action worked

**Accessibility.** Beyond contrast: keyboard, focus, targets, structure, motion. See checks.md.
- 4: meets WCAG 2.2 AA in every respect you could check
- 3: minor gaps that do not block anyone
- 2: gaps that make tasks hard for some users
- 1: a task is impossible for keyboard, screen reader or low-vision users

**Content and copy.** Is the language clear, specific and in the user's words?
- 4: labels say what happens; errors say what to do next; no jargon or filler
- 3: clear with a few vague labels
- 2: generic copy ("Submit", "Something went wrong") or internal jargon in key places
- 1: copy misleads or is missing where users need it

**System consistency.** Does it follow its own design system and platform conventions?
- 4: uses existing components and tokens; deviations are deliberate and justified
- 3: mostly consistent; a few one-offs
- 2: several components reinvented or tokens ignored
- 1: reads as a different product

## Severity

| Severity | Definition |
| --- | --- |
| **Blocker** | Stops some users completing the task, breaks a legal or accessibility requirement, or risks harm (money, data, safety). Must fix before shipping. |
| **Major** | Users will struggle, make errors or lose trust. Fix before shipping unless there is a strong reason. |
| **Minor** | Noticeable friction or inconsistency. Fix in the next iteration. |
| **Polish** | Craft detail. Fix when convenient. |

## Stage weighting

| Dimension | Exploration | Refinement | Pre-ship |
| --- | --- | --- | --- |
| Goal fit, hierarchy | High | High | Medium |
| Layout, typography, colour | Low | Medium | High |
| States, interaction | Low | High | High |
| Accessibility | Medium | High | Highest |
| Content, system | Low | Medium | High |

Low weight means mention only Blockers and Majors for that dimension.
