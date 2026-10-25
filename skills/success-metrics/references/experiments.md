# Choosing a method

| Method | Use when | Watch for |
| --- | --- | --- |
| A/B test | Enough traffic to detect the effect in a few weeks; the change can run side by side | Sample size, novelty effects, randomising by user, interference between groups |
| Holdout | Shipping to most people while keeping a small group on the old version to measure long-term effect | Keep the holdout long enough; it costs that group the improvement |
| Staged rollout | Risky changes; low traffic; you mainly need to catch harm | Not a clean comparison; watch guardrails at each stage |
| Before and after | No way to run both versions; low traffic | Seasonality, other launches, marketing; use a comparable period and a control metric that should not change |
| Qualitative | Very low traffic or early work | Report as evidence of problems found, not of size of effect |

## Sample size and duration

- Size the test before launch with `sample_size.py size`. If the duration is unrealistic, change the plan, not the maths.
- Run whole weeks. Weekday and weekend behaviour differ.
- With more than two variants, the script divides alpha across the comparisons with control (Bonferroni), which needs more traffic per variant.
- Randomise by the unit the metric uses (users for per-user metrics).

## Peeking

Checking results daily and stopping when they look significant inflates false positives far above 5%. Either commit to the full duration and look once, or use a sequential method designed for repeated looks. Stopping early for a broken guardrail is fine and should be in the rule.

## Reading results

- Report the difference with its 95% interval: "+1.5 points (+0.1 to +2.9)".
- Not significant means the test could not detect an effect this size, not that there is none. Say what effect sizes are ruled out by the interval.
- Check guardrails before calling a win.
- Check sample ratio: if the split was meant to be 50/50 and came out 52/48 with large numbers, something is wrong with assignment; investigate before trusting anything.
- Segments: look for harm in key segments (new users, assistive technology users, a platform), but treat segment wins found after the fact as hypotheses for the next test.

## Novelty and learning effects

New designs can win early because they are new, or lose early because people must relearn. For changes to familiar flows, run at least two weeks and compare the first and second halves.
