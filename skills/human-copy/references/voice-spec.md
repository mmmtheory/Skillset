# Voice note

When a BRAND.md exists, its front matter is the voice. This note is a short working summary for the session, or a stand-in when there is no BRAND.md.

```markdown
## Voice note: <brand>

Source: BRAND.md v<n> | style guide | existing copy | default (plain and calm)

Sounds like: <two or three traits, each with its limit>
Principles:
- <principle>: "<a line that does it>" / not "<a line that breaks it>"
Use: <words and phrases>
Avoid: <words and phrases>
Temperature by moment:
- Errors and money: <calm, specific, no humour>
- Success: <brief, factual>
- Onboarding and empty states: <warmer, one step at a time>
Formality: <you / we, contractions yes or no, sentence case or title case>
```

## Reading BRAND.md

```yaml
personality:
  - trait: Direct
    limit: never curt
voice:
  - principle: Say the number
    do: "Roasted Tuesday. At your door by Friday."
    dont: "Freshly roasted and shipped fast!"
words:
  use: [roasted on, farm]
  avoid: [artisan, premium, passion]
```

- Each `voice` entry is a rule with a tested example. Imitate the `do` line's length and rhythm, not just its meaning.
- Each `limit` is where the trait must stop. It decides tone in hard moments.
- `words.avoid` is enforced by the linter with `--brand BRAND.md`.

## Default voice when nothing is given

Plain and calm. Sentence case. Contractions. Second person. No exclamation marks. Short sentences. Numbers as digits. State outcomes, not feelings.
