# Defining a metric

## The format

| Field | Example |
| --- | --- |
| Name | Mobile checkout completion |
| Counts | Sessions with a `checkout_completed` event |
| Out of | Sessions with a `checkout_started` event |
| Population | Signed-in customers on iOS and Android app version 5.2 and later, excluding staff accounts |
| Window | Completion within 30 minutes of starting, measured per session; reported weekly |
| Source | Product analytics events `checkout_started`, `checkout_completed` |
| Good direction | Up |
| Baseline | 61.4% (four weeks to 20 Oct, app 5.2+) |
| Target | 63.0% or higher, with the reason |

Every rate needs a numerator and a denominator from the same population. Every count needs a time window. Every average needs to say what it averages over (per user, per session, per order).

## Weak and better

| Weak | Better | Problem |
| --- | --- | --- |
| Engagement | Weekly active savers: customers who add to a savings goal at least once in a 7 day window, out of customers with a goal | Undefined |
| Conversion up 20% | Trial to paid within 14 days, from 8.2% to 9.0% (the smallest effect worth the engineering cost) | No baseline, no reason for the target |
| Time on page | Share of help-article sessions that do not contact support within 24 hours | Direction is ambiguous: long can mean engaged or lost |
| Clicks on the new button | Share of orders that use saved cards | Measures the design, not the outcome |
| NPS | Task success and ease (SEQ) in the new flow; NPS as a slow, separate signal | Too far from the change, moves for many reasons |
| Number of searches | Share of searches followed by a result click within 60 seconds | More searches can mean failure |

## Direction checks

Before accepting a metric, ask: if this went up, could it mean things got worse? If yes, either pair it with a metric that resolves the ambiguity or choose another.

## Ratio and count traps

- Rates can rise because the denominator fell (fewer people start checkout, so a higher share completes). Report both the rate and the counts.
- Averages hide shifts in the mix (more new users lowers the average order value without anyone spending less). Segment by the obvious mix variables.
- Per-user metrics in A/B tests should randomise by user, not by session.

## Baselines

Use at least two full weeks, ideally four, ending before any related change. Note seasonality (paydays, holidays, end of month) and whether the period is comparable to the test period. When there is no data, the baseline is "to measure from launch of the events, for two weeks before the change ships".
