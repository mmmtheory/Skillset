# Template

Use these headings in this order. The checker looks for them by name.

```markdown
# DR-0007: Single-page checkout on all screen sizes

**Status:** Accepted
**Date:** 2026-10-26
**Decider:** Head of Design
**Consulted:** Checkout PM, Payments engineering lead, Support lead
**Informed:** Growth team, Brand

## Decision
Checkout uses one page with collapsible sections on all screen sizes, replacing the four-step flow.

## Context
Why now, and the constraints. Links to the brief, research and tickets.

## Options
### A. Single page with collapsible sections (chosen)
For: ...
Against: ...
### B. Keep the four-step flow
For: ...
Against: ...
### C. Steps on mobile, single page on desktop
For: ...
Against: ...

## Evidence
- **Research:** 5 of 6 test participants lost track of their total between steps 2 and 3. [Test readout, Sept]
- **Data:** 31% of mobile sessions exit on step 3. [Analytics dashboard]
- **Standard:** WCAG 2.2 3.3.7 Redundant Entry; the step flow asks for the email twice.
- **Judgement:** Payments engineering expects the single page to add 60 ms to first render. (Engineering lead)

Unknowns: how the change affects saved-card users; no data yet.

## Trade-offs
What we give up and who pays for it.

## Dissent
Who disagreed, their strongest argument, and whether they committed.

## Consequences
What changes now, with owners:
- Design: update checkout frames and the DESIGN.md form rules (owner, date)
- Engineering: ...

## Revisit when
- Mobile checkout completion does not improve by at least 2 points within 6 weeks of full rollout
- The payment provider ships in-page card authentication
```

## Status values

- **Proposed**: written, not yet decided (use this for a decision request)
- **Accepted**: decided and in effect
- **Superseded by DR-0012**: replaced; keep the record and link the new one
- **Deprecated**: no longer applies, not replaced
- **Rejected**: considered and turned down; worth keeping so the idea is not re-proposed blind

## Decision request

When no decision was made, use the same template with these changes:

- Status: Proposed
- Replace "Decision" with "Question": the decision that needs to be made, as a question
- Add "Recommendation" after Options only if the person asked for one, and label it as yours
- Replace "Dissent" with "Positions so far": who favours which option, as the source shows
- Add "Decide by": a date or event, and who decides
- Keep "Revisit when" as the trigger that would apply once decided
