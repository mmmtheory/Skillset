# Severity and tolerances

## Scale

| Severity | Use when | Examples |
| --- | --- | --- |
| Blocker | A task breaks, data is lost or shown wrongly, or an accessibility minimum fails | Pay button unreachable by keyboard; amount shows the wrong currency; error state never appears; text at 2.1:1 contrast |
| Must fix | Users will notice it, or it puts drift into shared code | Wrong component or variant; missing hover or focus state that was designed; layout breaks at a defined breakpoint; any hard-coded token or off-system value in a shared component |
| Should fix | Visible drift from the design that does not hurt the task | Spacing off by one step of the scale; wrong weight on a secondary label; icon 2 px too large; hard-coded value in a one-off page |
| Nit | Sub-pixel or taste-level | 1 px misalignment not on a shared edge; easing slightly different |

Raise one level when the issue repeats across many screens or sits in a shared component, because the fix pays off everywhere. Lower one level when the screen is behind a flag or internal only, and say so.

## Tolerances

Some difference between a frame and a browser is normal. These are within tolerance and not worth reporting on their own:

- 1 px differences from font rendering or sub-pixel rounding, unless they break an alignment the design makes on purpose (a shared left edge, a baseline)
- Line breaks that differ only because of real versus placeholder text
- Anti-aliasing and shadow rendering differences between tools

These are never within tolerance:

- a value that is not a token, even when it looks identical
- a different component, variant or icon
- a missing state
- any difference in what the interface says (copy, numbers, status)

## Classifying differences

| Type | Meaning | Action |
| --- | --- | --- |
| Build bug | The design is clear and the build differs | Fix the code |
| Design gap | The design does not cover this case | Report what the build does; ask design to decide |
| Stale design | The frame is out of date or breaks a system rule | Keep the build; ask design to update the frame |
| Intentional | A documented decision changed it | Note the reference; no action |

When unsure between build bug and stale design, check the frame's last edit date, the ticket, and whether the build matches the design system. Say which way you leaned and why.
