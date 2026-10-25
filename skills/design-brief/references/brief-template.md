# Brief template

Use these headings in this order. Cut any section that has nothing real in it, except the five marked *required*.

```markdown
# <Project name>: brief

**Problem** (required)
One or two sentences. Who struggles, with what, in which moment, and what it costs them. No solution in it.

**Why now**
The trigger: a deadline, a metric moving, a competitor, a complaint pattern. Skip if there is none.

**Audience** (required)
- Primary: who, described by situation and goal, not demographics.
- Secondary: anyone else affected (support, partners, admins).

**What we know**
- Fact, with its source.
- *Assumption:* belief we are acting on without evidence.

**Success** (required)
| Measure | Baseline | Target or direction |
| --- | --- | --- |
| Primary outcome | value or "unknown, measure first" | value or direction |
| Guardrail: must not get worse | value or "unknown" | hold |

**Scope** (required)
- In: what this project covers.
- Out: what it will not touch, even if related.

**Constraints**
Technical, brand, legal or regulatory, accessibility, time, budget, team. Only real ones.

**Anti-goals** (required)
What the design must not optimise for, even where it would be easy.

**Tensions decided**
- We favour X over Y because Z.

**Riskiest assumption**
The belief that sinks the work if wrong, and the cheapest test that would expose it.

**Deliverables and checkpoints**
What gets made, in what fidelity, reviewed by whom, by when.

**Open questions**
- Question (owner)
```

## Field notes

**Problem.** Test: if you delete the audience or the moment, does the sentence still make sense? Then it is too vague. "Users find checkout confusing" fails. "First-time buyers on mobile abandon at the delivery step because they cannot see total cost until after entering an address" passes.

**Audience by situation.** "Busy parents" is a demographic. "Someone reordering the same groceries on a phone while doing something else" is a situation a designer can design for.

**Success.** Prefer behaviour you can observe over sentiment. If the only honest measure is qualitative, say how you will collect it ("five task-based sessions, 4 of 5 complete without help").

**Guardrails.** Pick the thing the team would be most tempted to sacrifice: accuracy, trust, accessibility, support volume, revenue, load time.

**Anti-goals versus out of scope.** Out of scope is about territory ("no changes to the payment provider"). Anti-goals are about values ("not maximising sign-ups at the cost of qualified sign-ups").

**Tensions.** Real tensions have a credible case on both sides: speed versus flexibility, guidance versus control, consistency with the system versus fit for this context. If nobody would argue the other side, it is not a tension.
