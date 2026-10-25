---
name: state-inventory
description: Maps every state a screen, component or flow can be in before it is designed or built, beyond the happy path. Derives states from what the feature actually does (async data, money, permissions, other people, time), then gives each one its cause, how likely and how costly it is, what the person sees, the copy, and the way out. Use when someone asks for edge cases, states, unhappy paths, error or empty states, what could go wrong, a state matrix, or wants a feature specified before design or build. Not for reviewing a finished design (design-critique) or checking a build against its design (design-qa).
license: MIT
metadata:
  author: Matthias Schmutz
  version: "0.1.0"
---

# State inventory

Most of a product's quality lives in the states nobody drew. A state inventory lists them before they become bugs, support tickets or a developer's guess, and says what each one should look like and how people get out of it.

Without this skill, agents tend to:

- paste the same template (empty, loading, error) onto every screen, whatever the screen does
- miss the states that matter most for this domain: pending, held, partly failed, expired, changed by someone else
- treat "error" as one state, when a timeout, a decline and a lost connection need different answers
- describe a state without saying what the person sees, what it says, and how they get out
- write vague copy ("Something went wrong") that leaves people unsure whether their action happened
- forget the other people involved (the merchant, the admin, the recipient) and what happens over time
- list eighty states at equal weight, so none get designed properly

## Workflow

### 1. Model the thing first

Before listing any state, write a short model of the screen, component or flow:

- **Data**: where it comes from (local, our server, a third party), whether it can be slow, stale or missing
- **Actions**: what people can do, which actions change things, and which cannot be undone
- **People**: everyone who sees or is affected by this, not only the main user
- **Time**: what happens after a minute, a day, thirty days; anything scheduled, expiring or retried
- **Limits**: quotas, permissions, plan tiers, regions, devices

If the request leaves something important out, assume the most common case, say the assumption, and carry on.

### 2. Derive states from causes

States come from what the thing does. Feed the model to the script to get a starting list with the reason for each state:

```bash
python scripts/state_matrix.py "Order history: remote, list, filter, paged" "Refund button: action, money, irreversible, external"
python scripts/state_matrix.py --traits
```

`--traits` lists the traits it understands (remote, list, input, action, money, irreversible, external, permission, shared, time, upload, offline, ai and more) and the states each one brings. Treat the output as a floor, not the answer. Remove states that cannot happen here, and say why.

### 3. Add the domain states

Generic traits miss what the business knows and the interface does not show. For each domain in play, work through the pack in [references/domain-packs.md](references/domain-packs.md): payments and commerce, accounts and sign-in, collaboration, booking and scheduling, AI features, forms and onboarding, files and media, notifications.

Ask one question per actor: "What can be true for this person that the screen does not currently say?"

### 4. Specify each state

For every state that survives, give:

- **Cause**: what makes it happen, specific enough for an engineer to reproduce
- **Likelihood**: common, occasional or rare
- **Impact**: what it costs the person if handled badly (confusion, wasted time, lost data, lost money, lost trust)
- **Seen as**: what is on screen, and what stays the same (keep layout and entered data where you can)
- **Copy**: headline, one line of explanation, and the action label
- **Way out**: the next step, and what the system does on its own (retries, saves a draft, notifies someone)
- **Others**: what any other person sees, if anyone

Copy for problem states answers three questions: what happened, what happened to my data or money, and what can I do now. Patterns and rewrites are in [references/copy-patterns.md](references/copy-patterns.md). Never leave a person guessing whether an action went through. If the system cannot know (a timeout after a payment request was sent), the state says so and tells them how they will find out.

### 5. Prioritise

Rank by likelihood and impact:

- **Design**: common, or rare with a serious cost. Needs its own considered design.
- **Pattern**: covered by a shared pattern from the design system (a standard inline error, the default skeleton). Name the pattern.
- **Note**: rare and low cost. A line in the spec is enough.

Group states that share one design ("all three loading states use the list skeleton") so the count reflects real design work.

### 6. Map the transitions that need design

Most bugs live between states. List the transitions that need explicit design: pending to failed after the person has left the screen, success that is later reversed, offline to online with queued changes, a session that expires mid-form. For flows with more than five states, add a Mermaid state diagram.

### 7. Check the inventory

Write the inventory to a Markdown file and check it:

```bash
python scripts/state_matrix.py --check states.md
```

The check flags rows with no copy or no way out, copy that uses vague phrases ("Something went wrong", "Oops", "Invalid input"), and missing priority. Fix every flag before handing it over.

## Output

```markdown
## Model
Short description: data, actions, people, time, limits. Assumptions marked.

## States: <screen or component>
| State | Cause | Likelihood | Impact | Seen as | Copy | Way out | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Transitions to design
- from, to, trigger, what the person sees

## Questions for engineering
- unknowns that change the design (timeouts, retry rules, what the API returns)
```

One table per screen or component. Lead with the states marked Design. Put pure notes at the end of each table.

When the person asks for less (a quick list for a ticket), keep the same thinking and cut columns, not states that matter.

## Tone

Plain and concrete. Write copy as it would appear in the product, in the product's language. If the request is in another language, write the inventory in that language.
