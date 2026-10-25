# Autonomy matrix

Place each action by how easily it can be reversed and how much a mistake would cost. The cell gives the default level.

| | Easy to reverse | Reversible with effort | Irreversible |
| --- | --- | --- | --- |
| **Low impact** (only the user, small cost) | Act | Act and tell | Preview and confirm |
| **Medium impact** (time, mild embarrassment, small money) | Act and tell | Preview and confirm | Explicit approval |
| **High impact** (money, others see it, data loss, legal, health) | Preview and confirm | Explicit approval | Explicit approval |

## What each level looks like

**Act.** No interruption. The action appears in the activity log with the agent marked as the actor.

**Act and tell.** A notice after the fact that names the change and offers undo for a sensible window: "Archived 12 newsletters. Undo."

**Preview and confirm.** Before acting, show the exact result: the message text and recipients, the files and their destination, the calendar change. One clear button naming the action. Cancel leaves nothing changed.

**Explicit approval.** Everything in preview, plus the consequences in plain words ("This can't be undone", "This charges your card $412"), no default selection, and a deliberate action such as typing a confirmation or re-authenticating for the highest stakes. Never batch these with low-stakes approvals.

## Adjusting

- **Trust grows.** Offer to lower a level after the person has approved the same kind of action several times without changes. Ask once; don't nag.
- **Context raises stakes.** Sending to one colleague and sending to a whole company list are different cells.
- **Batch size raises stakes.** Deleting one file is low; deleting 400 is high, even if each is reversible.
- **Confirmation fatigue.** If people approve without reading, approvals stop protecting them. Fewer, better approvals beat many.

## Common actions, default levels

| Action | Default |
| --- | --- |
| Search, read, summarise the user's own data | Act (scope shown at setup) |
| Draft a message | Act ("Drafted, not sent") |
| Send a message as the user | Preview and confirm; explicit approval for new or many recipients |
| Archive, label, sort | Act and tell |
| Delete | Preview and confirm; explicit approval if permanent or in bulk |
| Create or move calendar events with others | Preview and confirm |
| Spend money, sign, submit legal or official forms | Explicit approval |
| Change permissions or share data externally | Explicit approval |
