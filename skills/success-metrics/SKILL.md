---
name: success-metrics
description: Defines how a design change will be judged before it ships. Traces the change to the behaviour and outcome it should move, picks one primary metric with an exact definition and baseline, adds guardrails that must not get worse, sets a target the traffic can actually detect, and writes the decision rule, events to track and readout plan, including A/B test sample size and duration. Also reads out a finished test honestly. Use when someone asks for success metrics, KPIs or OKRs for a feature or redesign, how to measure a design, what to track, an experiment or A/B test plan, HEART metrics, or whether a test result is real. Not for building dashboards or general data analysis.
license: MIT
metadata:
  author: Matthias Schmutz
  version: "0.1.0"
---

# Success metrics

A success metric is a promise made before launch: this is the change in behaviour we expect, this is how we will know, and this is what we will do if it does not happen. Written afterwards, metrics only describe what happened to go up.

Without this skill, agents tend to:

- list ten metrics with no primary one, so any result can be called a win
- choose measures that are easy to move but mean little (page views, clicks, time on page)
- name a metric without defining it: no numerator, denominator, population or time window
- invent baselines and targets ("increase conversion by 20%") with nothing behind them
- forget guardrails, so a gain in sign-ups hides a rise in refunds or support contacts
- plan an A/B test the traffic cannot power, then call a winner after three days
- read a noisy result as a real one, or a flat result as proof of no effect

## Workflow

### 1. Write the outcome chain

Before naming any metric, write the chain in one line each:

- **Change**: what is being shipped
- **Behaviour**: what people will do differently
- **User outcome**: what is better for them
- **Business outcome**: what that is worth to the organisation

If a link in the chain is a guess, say so. The metric belongs as close to the user outcome as you can measure within the time you have.

### 2. Pick one primary metric

One metric decides success. Choose it with three tests:

- **Sensitive**: this change can plausibly move it within the measurement window
- **Meaningful**: if it moves, the user outcome really improved
- **Measurable**: the events exist or can be added before launch

Define it exactly, using the format in [references/definitions.md](references/definitions.md): name, what is counted, out of what, for which people, over what window, from which events, and which direction is good. Ambiguous directions (time on page, number of searches) need a stated reason for which way is better, or a different metric.

Patterns by type of feature (onboarding, checkout, search, content, settings, AI features, design system adoption, error reduction) are in [references/metric-patterns.md](references/metric-patterns.md).

### 3. Add guardrails

Two to four things that must not get worse, each with a threshold. Look for the cost of the change: other steps of the funnel, errors and support contacts, refunds and cancellations, speed, accessibility, revenue per user, and effects on other people (merchants, admins, recipients). A change that wins the primary metric and breaks a guardrail does not ship as is.

### 4. Add diagnostic signals

Step-level measures that explain why the primary metric moved or did not: completion of each step, error rates by type, use of the new element. These are for understanding, not for deciding.

### 5. Establish the baseline

Use real numbers from what you were given. If the baseline is unknown, write "to measure" with how and over what period, and never fill the gap with a plausible figure. If historical data has seasonality or a recent change, say which period is comparable.

### 6. Set a target the data can detect

A target needs a reason: the effect needed for the change to be worth it, a comparable past result, or the smallest effect the traffic can detect. Check detectability before promising anything:

```bash
python scripts/sample_size.py size --baseline 0.12 --mde 0.01 --daily 4000
python scripts/sample_size.py mde --baseline 0.12 --daily 4000 --days 14
```

`size` gives participants per variant and days needed for an absolute (or `--relative`) effect. `mde` gives the smallest effect detectable in a fixed time. Round the duration up to whole weeks so every weekday is counted equally.

If the effect the team hopes for would take months to detect, say so, and offer alternatives: a bigger change, a metric with more traffic higher in the funnel, a longer test, a staged rollout watched against guardrails, or qualitative evidence with honest limits.

### 7. Choose the method and write the decision rule

Pick the method using [references/experiments.md](references/experiments.md): A/B test, holdout, staged rollout, before and after comparison, or qualitative. Then write the rule in advance:

> Ship if the primary metric improves and the 95% interval excludes zero, and no guardrail worsens past its threshold. Stop early only if a guardrail is clearly broken. Otherwise run the full 14 days without deciding on interim looks.

### 8. Specify instrumentation

List the events and properties needed, named the way the team's analytics already names them, with when each fires. Note any event that does not exist yet; launching without it means losing the baseline.

### 9. Read out honestly

When results come in, use the readout mode:

```bash
python scripts/sample_size.py readout --control 480/4000 --variant 540/4000
```

It gives the difference, the relative change, a 95% interval and a p-value. Report the interval, not only the point estimate. A result that is not significant is "no detectable effect at this sample size", not "no effect". Check guardrails before celebrating, and say if the test ran shorter than planned or was looked at early.

## Output

```markdown
## Outcome chain
Change, behaviour, user outcome, business outcome

## Primary metric
| Name | Definition | Population | Window | Source | Good direction | Baseline | Target |

## Guardrails
| Metric | Threshold | Why it could move |

## Diagnostic signals
## Method and decision rule
Including sample size, duration and the rule written before launch
## Instrumentation
| Event | Fires when | Properties | Exists? |
## Readout
Who, when, and what decisions each result leads to
```

If the person wants a short answer (three metrics for a ticket), give the primary metric with its definition and two guardrails, and still refuse to invent baselines.

## Tone

Clear and unhyped. Use numbers only when they come from the source or the script. Write in the language of the request, keeping metric and event names as the team writes them.
