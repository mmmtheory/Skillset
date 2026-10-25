---
name: brand-architecture
description: Designs or repairs how a company's brands, sub-brands, products and features relate, and the naming rules that keep them in order. Use when someone asks whether a new product or acquisition needs its own brand, how to organise or rationalise a brand portfolio, branded house versus house of brands, endorsed brands, sub-brand or product naming conventions, or why their product names feel like a mess. Not for positioning a single brand or inventing one-off names.
license: MIT
metadata:
  author: Matthias Schmutz
  version: "0.1.0"
---

# Brand architecture

Brand architecture decides how much each offer borrows from the parent brand, and how much it stands on its own. Every separate brand costs money and attention to build, so a new one has to earn its place. Every merged brand shares risk, so merging has to be safe.

Without this skill, agents tend to:

- pick a model by taste ("house of brands feels premium") instead of by criteria
- give features their own names until nobody knows what the product is called
- recommend a separate brand without counting what it costs to build and run
- merge brands that serve audiences who would be put off by each other
- write naming rules that the current portfolio already breaks
- skip the migration, so the target looks good on paper and never happens

This skill exists to stop those six things.

## Workflow

### 1. Map the portfolio

List every brand, sub-brand, product and named feature, with its tier, its parent and its audience. Use the format in [references/portfolio-map.md](references/portfolio-map.md). Ask for what is missing, at most five questions, each with a proposed default. If the person says not to ask, mark gaps as assumptions.

When the map is a file, check it:

```bash
python scripts/portfolio_check.py portfolio.json
```

The script flags names that are confusingly similar, sub-brands whose names don't follow their relationship, endorsed brands with no endorsement, children of a house-of-brands parent that use the parent's name, missing parents, cycles, and hierarchies deeper than three levels. Fix or explain every flag.

### 2. Decide each relationship with criteria

For each offer, or each decision the person is facing, run the decision tree in [references/decision-tree.md](references/decision-tree.md). The questions, in order:

1. **Risk.** Could a failure or scandal here damage the parent, or the reverse? If yes, keep them apart.
2. **Audience fit.** Would the parent's customers and this offer's customers be put off by each other? If yes, keep them apart.
3. **Equity transfer.** Does the parent's name help this offer sell? If not, borrowing it adds nothing.
4. **Distinct promise.** Does this offer make a promise the parent cannot? If not, it does not need its own brand.
5. **Investment.** Is there budget and attention to build and run a separate brand for years? If not, a separate brand will starve.

The answers point to one of five relationships: **branded house** (the parent name with a descriptor), **sub-brand** (parent name plus a product name), **endorsed** (own name, with "by" or "from" the parent), **house of brands** (separate, the parent stays out of sight), or **feature** (no brand name at all, just a plain description).

Definitions, examples and trade-offs are in [references/models.md](references/models.md). Most real portfolios are hybrids; that is fine as long as each relationship has a reason.

### 3. Write the naming system

Define one pattern per tier, with examples, using [references/naming-rules.md](references/naming-rules.md):

- the masterbrand
- product or sub-brand names: pattern, length, language, what they may and may not describe
- descriptors: plain words that say what the thing is
- features: described, never named, unless they pass the five questions above

Test the rules against the current portfolio. Any existing name that breaks a rule gets a decision: change it, grandfather it with a reason, or change the rule.

### 4. Set the gate for new offers

Write the short checklist a team runs before creating any new name. Default to no new brand. The checklist is the five questions above plus who approves.

### 5. Plan the migration

When the target differs from today, plan the move in stages:

- what changes first, and what the customer sees at each stage (endorsement often comes before a full merge)
- what must not break: search, app store listings, contracts, signage, legal entities
- how long each stage runs and what signal means it is safe to move on

Do not claim costs or timings you were not given. Mark them as estimates to confirm.

### 6. Check before handing it over

- Does every relationship trace to the decision questions, with the answer written down?
- Does the current portfolio pass the naming rules, or is every exception listed?
- Did the script run clean on the target portfolio, or is every remaining flag explained?
- Could a product manager decide whether their next feature gets a name, using only this document?

## Output

Lead with the recommendation in two or three sentences: the model, and the one or two decisions that matter most. Then the portfolio map (current and target), the reasoning per relationship, the naming system, the gate, and the migration.

A simple tree diagram helps (indented list or Mermaid). Keep it to the brands that matter.

## When to push back

Say so plainly, then still deliver:

- the person wants a new brand for something that is a feature
- the person wants a separate brand but has no budget to build it
- the person wants to merge brands whose audiences or risks clash

Write plainly: short sentences, concrete nouns, no em dashes, no filler. Match the person's language.
