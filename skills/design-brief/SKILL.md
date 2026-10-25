---
name: design-brief
description: Turns a vague design request into a sharp one-page brief before any design work starts. Use when someone asks to design, redesign or build a screen, feature, flow, product, campaign or brand asset and the problem, audience, constraints or measure of success is unclear, or when they ask for a brief, problem statement, project framing or kickoff doc. Not for critiquing finished work or synthesising research.
license: MIT
metadata:
  author: Matthias Schmutz
  version: "0.1.0"
---

# Design brief

A brief decides what problem the work solves, for whom, and how anyone will know it worked. Most weak design starts from a weak brief, so get this right before pixels.

Agents fail at briefs in predictable ways. Without this skill they tend to:

- treat the requested solution as the problem ("add a dashboard")
- invent facts, numbers and user insights, then present them as known
- ask fifteen questions at once, or none at all
- write success as "improve the experience"
- skip what is out of scope and what the work must not do
- pad the brief with boilerplate nobody reads

This skill exists to stop those six things.

## Workflow

### 1. Read everything you were given

Read attached files, linked docs and earlier messages before asking anything. Never ask for something already provided.

Classify the request. It changes which questions matter (see [references/question-bank.md](references/question-bank.md)):

- **New** product or feature
- **Redesign** of something that exists
- **Optimisation** of a metric on an existing flow
- **Brand or campaign** asset
- **Fix** for a known defect or complaint

### 2. Separate the ask from the problem

Restate the request as the person framed it. Then find the outcome underneath it by asking "so that what?" until you reach something a user or the business would notice.

If the request names a solution ("a dashboard", "a redesign", "a chatbot"), keep it as a candidate, not a given. Write the problem statement without it. If the solution may well be right, say so; the point is to make it earn its place.

### 3. Ask the few questions that change the brief

Check the request against the fields in [references/brief-template.md](references/brief-template.md). For each gap, decide: would a different answer change the design direction? Only those gaps become questions.

- Ask **at most five**, ordered by how much the answer would change the work.
- Pair every question with a **proposed default** so the person can reply "yes" or correct it.
- Ask in one message, then stop and wait.

Skip the questions and go straight to the brief when the person has said to, when they are not around to answer, or when the request is already specific. In those cases, every gap becomes a marked assumption in the brief.

### 4. Write the brief

Use the template in [references/brief-template.md](references/brief-template.md). Rules that matter most:

- **One page.** 350 to 650 words. A section with nothing real to say is cut, not filled.
- **Known versus assumed.** Every factual claim is either sourced ("from the support log, Oct") or tagged *Assumption*. Never invent a statistic, a quote or a research finding. If a number would help and you do not have it, write the measurement you need instead.
- **Problem statement without a solution in it.** Who struggles, with what, in which moment, and what it costs them.
- **Success you could check.** Each measure names a metric or observable behaviour, a baseline (or "baseline unknown, measure first") and a direction or target. Include at least one guardrail: something that must not get worse.
- **Out of scope and anti-goals.** Out of scope says what this project will not touch. Anti-goals say what the design must not optimise for, even if it would be easy ("not more time in app").
- **Tensions decided.** Name two or three real trade-offs and which way this project leans, so designers do not relitigate them.
- **Riskiest assumption.** The belief that would sink the work if wrong, and the cheapest way to test it.

See [references/examples.md](references/examples.md) for a weak and a strong brief built from the same request.

### 5. Check before you hand it over

Read the brief once as a sceptical design lead would:

- Could a designer start tomorrow without asking you anything?
- Does any sentence claim a fact you did not get from the person or their files?
- Would two designers working from this brief build roughly the same kind of thing for the same reason?
- Is there a word that could be cut from every section? Cut it.

## When to push back

Say so plainly, in one or two sentences before the brief, when:

- the constraints contradict each other (fixed date, fixed scope and a quality bar that cannot all hold)
- the stated solution clearly does not serve the stated goal
- there is no user problem at all, only an internal preference, and the person seems to think otherwise

Then still deliver the best brief you can, with the conflict listed under open questions. Pushing back is part of the brief, not a replacement for it.

## Output

Deliver the brief in the format the person asked for. Default to clean Markdown with the template headings. Do not add a summary after it, a list of next steps they did not ask for, or a sign-off.

If the person writes in a particular voice or language, match it. Write plainly: short sentences, concrete nouns, no em dashes, no marketing filler.
