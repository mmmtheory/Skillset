---
name: agentic-ux
description: Designs and reviews product experiences where an AI agent acts on someone's behalf, so people stay in control, can see what happened, and can recover when it goes wrong. Use when someone is designing or reviewing an AI agent, assistant, copilot or automation feature, deciding what an agent may do without asking, designing approvals, undo, progress, failure or handoff states, or writing the interface copy for an AI feature. Not for general chatbot prompt writing or model evaluation.
license: MIT
metadata:
  author: Matthias Schmutz
  version: "0.1.0"
---

# Agentic UX

When software acts for someone, the design question changes from "can they do it?" to "can they trust it, see it, stop it and undo it?" Trust is earned in the moments the agent is unsure, wrong or about to do something that can't be taken back.

Without this skill, agents designing AI features tend to:

- design only the happy path, where the agent understood and succeeded
- treat every action the same: confirm everything until people stop reading, or confirm nothing
- hide that an action was taken by the agent, or what it touched
- forget undo, partial failure and the half-finished task
- show "Thinking..." for a task that takes minutes, with no way to stop it
- give the agent a chirpy personality that over-promises ("I've got this!")
- leave no route to a person when the agent can't help

This skill exists to stop those seven things.

## Workflow

### 1. List what the agent can do

Make an action inventory before designing screens. For every action the agent can take, record:

| Action | What it touches | Reversible? | Who is affected | Cost of a mistake |
| --- | --- | --- | --- | --- |

Include reading actions (searching mail, viewing files) as well as writing ones. People care what an agent can see.

### 2. Set the autonomy for each action

Place each action on the matrix in [references/autonomy.md](references/autonomy.md), using reversibility and impact:

- **Act**: low impact, easy to reverse. The agent just does it and shows it in the activity log.
- **Act and tell**: low or medium impact, reversible. Do it, then show a clear notice with undo.
- **Preview and confirm**: medium impact, or hard to reverse. Show exactly what will happen, then one confirmation.
- **Explicit approval**: high impact or irreversible: money, messages sent as the person, deleting data, legal or medical consequences, anything others will see. Full details, a deliberate action to approve, never a default.

Let people raise or lower these levels per action where the stakes allow, and remember their choice. Count confirmations in a typical session; if people would approve more than a few routine ones, move those down a level.

### 3. Design the whole loop

Work through each stage using the patterns in [references/patterns.md](references/patterns.md):

1. **Before.** What the agent can access (scope), what it understood (intent echo), and for multi-step work, the plan before it starts.
2. **During.** Real progress for anything over a few seconds: which step it is on, what it has done so far, and a stop button that leaves things in a known state.
3. **After.** What changed, in a receipt people can check, with undo where possible and a durable activity log.
4. **When unsure.** Say so, show sources or reasons, and ask one specific question instead of guessing.
5. **When it fails.** What worked, what didn't, what state things are in now, and the next step. Partial completion is a state to design, not an error to hide.
6. **When it can't help.** A route to a person, with the context handed over so nobody repeats themselves.

### 4. Write the words

- Name actions by what they do: "Send 3 replies", not "Proceed".
- Say what the agent did, and what it did not do: "Drafted a reply. Not sent."
- State uncertainty in plain terms, tied to the reason: "I couldn't find a matching invoice, so I haven't paid it."
- No fake feelings, no exclamation marks on outcomes, no "I'd be happy to". The agent is a tool that reports clearly.
- Label agent actions so people can tell them from their own, everywhere they appear: inbox, history, shared documents.

### 5. Review

Run the checklist in [references/review-checklist.md](references/review-checklist.md). For a review of an existing design, report findings ranked by severity (Blocker, Major, Minor), each with the stage it belongs to and a concrete fix. An irreversible action without explicit approval, or no way to stop a running task, is always a Blocker.

## Output

For a design request: the action inventory with autonomy levels, then the loop for the main task as states (screens or written descriptions), then the copy for the key moments. For a review: a verdict, ranked findings, then what to keep.

Diagrams help for the loop. Keep them to the states that matter.

Write plainly. No em dashes, no hype about AI.
