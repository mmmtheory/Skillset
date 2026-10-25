# Metric patterns by feature type

Starting points, not answers. Each pattern needs the full definition before use.

## Onboarding and activation

- Primary: activation rate, the share of new sign-ups who complete the action that predicts retention (first payment sent, first project shared) within N days
- Guardrails: sign-up completion, support contacts from new users, 30 day retention
- Diagnostic: step completion, time to activation, drop-off by step

## Checkout and payments

- Primary: checkout completion (completed out of started) or payment success rate
- Guardrails: refund and chargeback rate, duplicate payments, payment errors by type, average order value, support contacts about payments
- Diagnostic: completion per step, declines by reason, saved method use
- Watch for: rates that improve because fewer people start

## Search and navigation

- Primary: successful search rate (search followed by a result click or task completion within a time window), or task success in a tree test
- Guardrails: zero-result searches, use of support or contact, time to first meaningful action
- Avoid: number of searches or page views as a success measure

## Content and help

- Primary: self-service resolution (help sessions with no support contact within 24 hours)
- Guardrails: support contact rate overall, article feedback ("did this help") ratio
- Diagnostic: scroll depth, search refinements, exits to contact

## Settings and preferences

- Primary: share of people who complete the change they started without a support contact
- Guardrails: accidental changes reversed within a day, errors
- Often too low traffic for an A/B test; use task-based testing and watch guardrails after release

## Notifications and engagement

- Primary: the action the notification exists to drive (payment made after reminder), not opens
- Guardrails: opt-outs, uninstalls, complaints
- Avoid: open rate as the primary metric; it can rise while people get annoyed

## AI features

- Primary: task completion with the feature versus without, or the share of outputs accepted without major edits
- Guardrails: undo or revert rate, error reports, escalation to a human, time to complete, cost per task
- Diagnostic: use rate, stop rate, retries, edits per output
- Avoid: usage alone; novelty inflates it for weeks

## Design system adoption

- Primary: share of UI built from system components (by screen or by component instance), or time to ship a standard screen
- Guardrails: accessibility defects, visual QA defects, number of detached or overridden components
- Diagnostic: token drift counts from code scans, adoption by team

## Error reduction

- Primary: rate of the specific error per attempt (failed transfers per transfer started)
- Guardrails: completion rate, the next most common error (problems move rather than disappear), support contacts
- Diagnostic: errors by type and platform, recovery rate after an error

## HEART as a checklist

Happiness, Engagement, Adoption, Retention, Task success. Use it to check you have not missed a category, not to fill five boxes. Most design changes need one of these as primary and one or two as guardrails.
