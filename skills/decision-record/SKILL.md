---
name: decision-record
description: Writes a design decision record that states what was decided, the real options that were weighed, the evidence behind the choice, the trade-offs accepted, who decided, and the trigger that would reopen it. Turns meeting notes, critique feedback or a long thread into a short record, or into a decision request when nothing was actually decided. Use when someone asks to document or write up a design decision, record why we chose something, capture the outcome of a design review or critique, write a DDR or ADR for design, log a trade-off, or stop a debate that keeps coming back. Not for framing work before it starts (design-brief) or reviewing a design (design-critique).
license: MIT
metadata:
  author: Matthias Schmutz
  version: "0.1.0"
---

# Decision record

A decision record lets someone who was not in the room understand what was chosen, why, and when it would be right to change it. It stops the same debate returning every quarter. It also makes it safe to change course later, because everyone can see what the original call rested on.

Without this skill, agents tend to:

- retell the meeting in order instead of stating the decision
- record only the winning option, or set up weak alternatives to knock down
- mix evidence and opinion, and fill gaps with plausible numbers nobody measured
- write "the team decided" with no owner and no date
- leave out what was given up, so the trade-off looks free
- skip the condition for revisiting, so the decision is either permanent or always open
- write a confident record of a decision that the source shows was never made

## Workflow

### 1. Check that a decision was made

Read everything you were given. Look for a clear choice and someone with the authority to make it.

- If the source shows a decision, write the record.
- If it shows a discussion that ended without a decision, do not invent one. Write a **decision request** instead: the question, the options, a recommendation if you were asked for one, who should decide, and by when. Say plainly that no decision was found.
- If it shows a decision that some people still dispute, record the decision and the dissent. Do not smooth it over.

### 2. State the decision first

One or two sentences, present tense, specific enough to act on: "Checkout uses a single page with collapsible sections on all screen sizes." Not "We aligned on an approach to checkout."

### 3. Give the context

Why this had to be decided now, and the constraints that shaped it (deadlines, platforms, regulation, budget, the design system). Keep it to a short paragraph. Link the brief, research or tickets rather than restating them.

### 4. Lay out the options fairly

At least two real options, and include "keep what we have" when it was possible. For each: what it is in one line, what speaks for it, what speaks against it. Write each option the way its strongest supporter would. If the source shows only one option was ever considered, say so; that is a finding.

### 5. Separate evidence from judgement

Label each piece of support with its type:

- **Data**: analytics, experiment results, measured performance
- **Research**: usability tests, interviews, support tickets
- **Standard**: accessibility criteria, platform guidelines, regulation, the design system
- **Precedent**: what the team or others did before and how it went
- **Judgement**: an informed opinion, with whose it is

Give a source for every item. Never add numbers, quotes or findings that are not in what you were given; if evidence would help and is missing, list it under unknowns.

### 6. Name the trade-offs

What is being given up, and who pays for it. Every real decision costs something. A record with no trade-offs usually means the alternatives were not taken seriously.

### 7. Record ownership and dissent

- **Decider**: one named person or role. A group can be consulted; one person decides.
- **Consulted** and **Informed**: names or roles, if known.
- **Dissent**: who disagreed and why, in their strongest form, and whether they agreed to commit.

If the source does not name a decider, write "Decider: not stated" and add it to the questions. Do not make one up.

### 8. Set the trigger to revisit

One or more observable conditions: a metric crossing a threshold, a date, an event ("if the payment provider supports saved cards in-app"). "If needed" and "later" are not triggers. The trigger is what lets people disagree without reopening the decision every week.

### 9. Check and file

Write the record using [references/template.md](references/template.md), then check it:

```bash
python scripts/decision_check.py decisions/0007-single-page-checkout.md
```

The check confirms the required sections, at least two options, a valid status and date, a single decider, and a revisit trigger that is not vague. Fix every problem it reports.

If the project keeps decision records in a folder, follow its numbering and naming, and update its index. When a new decision replaces an old one, set the old one's status to "Superseded by" with a link, and keep the old record. Examples of strong and weak records are in [references/examples.md](references/examples.md).

## Length

Aim for one screen. The record is read by people deciding whether to trust it, usually in a hurry. Link out for detail. If it runs past 600 words, cut the context and the option descriptions first, never the trade-offs or the trigger.

## Tone

Plain and neutral. Describe positions, not personalities. Write in the language of the request, keeping names, product terms and quotes as they appear in the source.
