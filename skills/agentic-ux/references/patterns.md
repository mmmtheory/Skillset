# Patterns

Each pattern: what it solves, how it looks, and the mistake to avoid.

## Before the agent acts

**Scope and permissions.** Show what the agent can read and do, in plain words, at setup and wherever it is used. "Can read your inbox and draft replies. Can't send without asking." Let people narrow scope. Mistake: a one-time OAuth screen as the only explanation.

**Intent echo.** Restate what the agent understood before a task that matters: "Find flights to Sydney, 14 to 18 March, under $600, morning departures." Editable in place. Mistake: echoing back the prompt word for word, which confirms nothing.

**Plan preview.** For multi-step work, show the steps before starting, with the risky ones marked. People can remove or reorder steps. Mistake: plans so long nobody reads them; keep to the steps that change something.

## While it works

**Real progress.** Show the current step, completed steps, and an honest sense of time for anything over a few seconds. "Checked 40 of 120 invoices." Mistake: an indeterminate spinner labelled "Thinking..." for minutes.

**Stop.** A stop control that is always visible during work. Stopping leaves things in a known state and says what was done before it stopped. Mistake: a stop that silently leaves half-applied changes.

**Interruptible questions.** When the agent needs a decision, ask one specific question with options and a default, and keep working on the parts that don't depend on it.

## After it acts

**Receipt.** A summary of what changed that people can check: items affected, where they went, what was sent. Each item links to the real thing.

**Undo.** Offer undo for reversible actions for a window that fits the action. Say how long it lasts. For actions with effects outside the product (an email sent), say what undo can and can't do.

**Activity log.** A durable, searchable history of agent actions, marked as the agent's, with who asked and when. Mistake: actions that look identical to the user's own in shared spaces.

## When unsure or wrong

**Calibrated uncertainty.** Say when the agent is unsure and why, in words tied to the reason, not percentages. Show sources for factual claims. Mistake: identical confident tone whether right or guessing.

**Partial completion.** "Moved 37 files. 3 failed because they're open in another app. Nothing else changed." List the failures with a retry for each. Mistake: an all-or-nothing error message that hides what did happen.

**Failure states.** What happened, what state things are in, whether anything was lost, what to do next. Same three questions as any good error.

**Correction.** Let people fix the output directly and, where it makes sense, tell the agent why, so the next run improves. Show when a correction has been remembered.

## Leaving the agent

**Handoff to a person.** Offer it whenever the agent can't help, the person asks, or stakes are high. Pass the conversation and what was tried, and tell the person what happens next and roughly when.

**Memory controls.** Show what the agent remembers about the person, let them edit or delete it, and make it easy to use the product without memory.

## Words

| Instead of | Write |
| --- | --- |
| "Proceed" | "Send 3 replies" |
| "Done!" | "Archived 12 newsletters. Undo" |
| "Something went wrong" | "Couldn't reach your calendar. No events were changed. Try again" |
| "I'd be happy to help with that!" | (nothing; just do it or ask the question) |
| "I think this might possibly be..." | "This matches 2 of 3 details. The amount differs: $120 on the invoice, $112 in the order." |
