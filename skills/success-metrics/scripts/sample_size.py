#!/usr/bin/env python3
"""Sample size, detectable effect and readout for A/B tests on design changes.

  How many people and days to detect an effect:
    python sample_size.py size --baseline 0.12 --mde 0.01 --daily 4000
    python sample_size.py size --baseline 12% --mde 10% --relative --daily 4000
    python sample_size.py size --baseline 42.5 --sd 30 --mde 2 --daily 900      (a mean, such as order value)

  Smallest effect detectable in a fixed time:
    python sample_size.py mde --baseline 0.12 --daily 4000 --days 14

  Read out a finished test (conversions/visitors):
    python sample_size.py readout --control 480/4000 --variant 540/4000

Options: --alpha (default 0.05, two-sided), --power (default 0.8),
--variants (arms including control, default 2; alpha is split across the
comparisons with control). --daily is eligible people per day across all arms.
Rates can be written 0.12, 12% or 12.

Readout gives the difference, relative change, 95% interval, p-value
(two-proportion z-test) and a sample ratio check against --split (default 0.5).

Exit status: 0 on success, 2 on bad input. Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import math
import sys
from statistics import NormalDist

Z = NormalDist()


def rate(text: str) -> float:
    t = str(text).strip()
    value = float(t.rstrip("%"))
    if t.endswith("%") or value > 1:
        value /= 100
    if not 0 < value < 1:
        raise ValueError(f"rate {text} must be between 0 and 1 (or 0% and 100%)")
    return value


def z_values(alpha: float, power: float, variants: int) -> tuple[float, float]:
    comparisons = max(1, variants - 1)
    return Z.inv_cdf(1 - alpha / comparisons / 2), Z.inv_cdf(power)


def n_proportions(p1: float, p2: float, za: float, zb: float) -> float:
    pbar = (p1 + p2) / 2
    num = za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    return num ** 2 / (p2 - p1) ** 2


def n_means(sd: float, delta: float, za: float, zb: float) -> float:
    return 2 * (za + zb) ** 2 * sd ** 2 / delta ** 2


def days_for(n_per_arm: float, variants: int, daily: float | None):
    if not daily:
        return None, None
    days = math.ceil(n_per_arm * variants / daily)
    return days, math.ceil(days / 7)


def cmd_size(a) -> str:
    za, zb = z_values(a.alpha, a.power, a.variants)
    if a.sd is not None:
        base = float(a.baseline)
        delta = float(a.mde) * (base if a.relative else 1)
        if a.relative and float(a.mde) > 1:
            delta = base * float(a.mde) / 100
        n = math.ceil(n_means(a.sd, delta, za, zb))
        effect = f"a change in the mean of {delta:g} (from {base:g}, sd {a.sd:g})"
    else:
        p1 = rate(a.baseline)
        if a.relative:
            rel = float(str(a.mde).rstrip("%"))
            rel = rel / 100 if (str(a.mde).endswith("%") or rel > 1) else rel
            p2 = p1 * (1 + rel)
        else:
            p2 = p1 + rate(a.mde) if not str(a.mde).startswith("-") else p1 - rate(str(a.mde)[1:])
        if not 0 < p2 < 1:
            raise ValueError("baseline plus effect must stay between 0 and 1")
        n = math.ceil(n_proportions(p1, p2, za, zb))
        effect = f"{p1:.2%} to {p2:.2%} ({(p2 - p1) * 100:+.2f} points, {(p2 / p1 - 1):+.1%} relative)"
    days, weeks = days_for(n, a.variants, a.daily)
    lines = [f"Effect: {effect}",
             f"Alpha {a.alpha:g} two-sided" + (f", split over {a.variants - 1} comparisons" if a.variants > 2 else "")
             + f", power {a.power:g}",
             f"Needed: {n:,} per arm, {n * a.variants:,} in total across {a.variants} arms"]
    if days:
        lines.append(f"At {a.daily:,.0f} eligible per day: {days} days; run {weeks} full week(s) ({weeks * 7} days)")
        if weeks > 8:
            lines.append("That is longer than most teams can hold a test. Consider a bigger change, a higher-traffic "
                         "metric, or a staged rollout watched against guardrails.")
    return "\n".join(lines)


def cmd_mde(a) -> str:
    za, zb = z_values(a.alpha, a.power, a.variants)
    n = a.daily * a.days / a.variants
    if a.sd is not None:
        delta = math.sqrt(2 * (za + zb) ** 2 * a.sd ** 2 / n)
        return (f"{n:,.0f} per arm over {a.days} days\n"
                f"Smallest detectable change in the mean: {delta:.3g} (from {float(a.baseline):g}, sd {a.sd:g})")
    p1 = rate(a.baseline)
    lo, hi = 1e-6, 1 - p1 - 1e-9
    if n_proportions(p1, p1 + hi, za, zb) > n:
        return f"{n:,.0f} per arm over {a.days} days is too few to detect any realistic change from {p1:.2%}."
    for _ in range(100):
        mid = (lo + hi) / 2
        if n_proportions(p1, p1 + mid, za, zb) > n:
            lo = mid
        else:
            hi = mid
    return (f"{n:,.0f} per arm over {a.days} days\n"
            f"Smallest detectable change: {hi * 100:.2f} points ({p1:.2%} to {p1 + hi:.2%}, {hi / p1:+.1%} relative)")


def parse_counts(text: str) -> tuple[int, int]:
    x, _, n = text.partition("/")
    x, n = int(x.replace(",", "")), int(n.replace(",", ""))
    if n <= 0 or not 0 <= x <= n:
        raise ValueError(f"counts {text} must be conversions/visitors with 0 <= conversions <= visitors")
    return x, n


def readout(control: str, variant: str, split: float = 0.5, alpha: float = 0.05) -> dict:
    x1, n1 = parse_counts(control)
    x2, n2 = parse_counts(variant)
    p1, p2 = x1 / n1, x2 / n2
    diff = p2 - p1
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    z_ci = Z.inv_cdf(1 - alpha / 2)
    pooled = (x1 + x2) / (n1 + n2)
    se0 = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    z = diff / se0 if se0 else 0.0
    p = 2 * (1 - Z.cdf(abs(z)))
    total = n1 + n2
    expected1 = total * split
    chi = (n1 - expected1) ** 2 / expected1 + (n2 - (total - expected1)) ** 2 / (total - expected1)
    srm_p = 2 * (1 - Z.cdf(math.sqrt(chi)))
    return {"p1": p1, "p2": p2, "diff": diff, "rel": diff / p1 if p1 else float("nan"),
            "lo": diff - z_ci * se, "hi": diff + z_ci * se, "p": p, "srm_p": srm_p, "n1": n1, "n2": n2}


def cmd_readout(a) -> str:
    r = readout(a.control, a.variant, a.split, a.alpha)
    sig = r["p"] < a.alpha
    lines = [f"Control {r['p1']:.2%} (n={r['n1']:,}), variant {r['p2']:.2%} (n={r['n2']:,})",
             f"Difference {r['diff'] * 100:+.2f} points ({r['rel']:+.1%} relative), "
             f"{1 - a.alpha:.0%} interval {r['lo'] * 100:+.2f} to {r['hi'] * 100:+.2f} points",
             f"p = {r['p']:.3f}"]
    if r["srm_p"] < 0.001:
        lines.append(f"Sample ratio mismatch (p = {r['srm_p']:.1e}): the split is not what was planned. "
                     "Check assignment before trusting this result.")
    if sig:
        lines.append("The interval excludes zero. Check guardrails and the planned duration before calling it.")
    else:
        lines.append("No detectable effect at this sample size. The interval shows which effects are still possible; "
                     "this is not evidence of no effect.")
    return "\n".join(lines)


def selftest() -> int:
    failures = []
    za, zb = z_values(0.05, 0.8, 2)
    n = math.ceil(n_proportions(0.10, 0.12, za, zb))
    if n != 3841:
        failures.append(f"10% to 12%: expected 3841 per arm, got {n}")
    n = math.ceil(n_means(30, 2, za, zb))
    if not 3530 <= n <= 3534:
        failures.append(f"means: expected about 3532, got {n}")
    za3, _ = z_values(0.05, 0.8, 3)
    if not abs(za3 - 2.2414) < 0.001:
        failures.append(f"three arms should split alpha: z {za3}")
    r = readout("480/4000", "540/4000")
    if not (abs(r["diff"] - 0.015) < 1e-9 and 0.04 < r["p"] < 0.05):
        failures.append(f"readout: diff {r['diff']} p {r['p']}")
    r = readout("500/5000", "500/5600")
    if r["srm_p"] >= 0.001:
        failures.append("sample ratio mismatch not detected")

    class A:  # noqa: N801
        pass
    a = A()
    a.alpha, a.power, a.variants, a.daily, a.days, a.sd, a.baseline = 0.05, 0.8, 2, 4000, 14, None, "0.12"
    out = cmd_mde(a)
    if "Smallest detectable change" not in out:
        failures.append(f"mde output: {out}")
    a.mde, a.relative = "10%", True
    out = cmd_size(a)
    if "12.00% to 13.20%" not in out:
        failures.append(f"relative size: {out}")
    for bad in ("150", "0", "-3%"):
        try:
            rate(bad)
            failures.append(f"rate({bad}) should fail")
        except ValueError:
            pass
    if failures:
        print("selftest failed:")
        for f in failures:
            print("  " + f)
        return 1
    print("selftest passed")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--alpha", type=float, default=0.05)
    common.add_argument("--power", type=float, default=0.8)
    common.add_argument("--variants", type=int, default=2)
    s = sub.add_parser("size", parents=[common])
    s.add_argument("--baseline", required=True)
    s.add_argument("--mde", required=True, help="absolute effect, or relative with --relative")
    s.add_argument("--relative", action="store_true")
    s.add_argument("--sd", type=float, help="standard deviation, for a mean metric")
    s.add_argument("--daily", type=float, help="eligible people per day across all arms")
    m = sub.add_parser("mde", parents=[common])
    m.add_argument("--baseline", required=True)
    m.add_argument("--daily", type=float, required=True)
    m.add_argument("--days", type=int, required=True)
    m.add_argument("--sd", type=float)
    r = sub.add_parser("readout")
    r.add_argument("--control", required=True, help="conversions/visitors")
    r.add_argument("--variant", required=True, help="conversions/visitors")
    r.add_argument("--split", type=float, default=0.5, help="planned share in control")
    r.add_argument("--alpha", type=float, default=0.05)
    args = parser.parse_args(argv)
    try:
        if getattr(args, "variants", 2) < 2:
            raise ValueError("--variants counts arms including control, so at least 2")
        print({"size": cmd_size, "mde": cmd_mde, "readout": cmd_readout}[args.cmd](args))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
