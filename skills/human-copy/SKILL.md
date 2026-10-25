---
name: human-copy
description: Writes and edits interface and product copy so it sounds like a specific brand written by a person, not like generated text. Use when someone asks for microcopy, UX writing, button labels, error messages, empty states, onboarding, notifications, consent or permission text, or asks to make copy sound more human, on brand or less like AI. Reads the brand's BRAND.md voice rules when one exists. Not for long-form marketing articles or legal drafting.
license: MIT
metadata:
  author: Matthias Schmutz
  version: "0.1.0"
---

# Human copy

Interface copy is read in a hurry, by someone in the middle of a task. It works when it says what is happening and what to do, in words that sound like this brand and nobody else.

Without this skill, agents tend to:

- reach for the same stock phrases and rhythms that mark text as generated
- add cheerfulness the moment calls against: exclamation marks on errors, "Oops!" when money failed to move
- write buttons that don't say what they do ("Submit", "Continue", "OK")
- write errors that say something went wrong but not what, or what to do
- ignore the brand's voice, so every product sounds the same
- write long sentences for a screen where people read three words

This skill exists to stop those six things.

## Workflow

### 1. Find the voice

Look for a `BRAND.md` (written by the brand-strategy skill, or by hand). Read its front matter: `voice` principles with their do and don't lines, `personality` traits with their limits, and `words.use` and `words.avoid`. These override the defaults below.

If there is no BRAND.md, look for a style guide or existing copy the team likes. If there is nothing, ask one question with a proposed default: "Should this sound plain and calm, like a good bank, or warmer and more casual?" If the person can't be asked, use plain and calm and say so.

Keep a short voice note for the session in the format in [references/voice-spec.md](references/voice-spec.md).

### 2. Know the moment

Before writing, note for each string: where it appears, what the person was trying to do, how they feel at that moment, and what they need to do next. Copy for a failed payment and copy for a completed profile need different temperatures even in the same brand. Patterns for each type of copy are in [references/patterns.md](references/patterns.md).

### 3. Write

- Lead with what matters to the person. Put the action or the outcome first.
- Buttons name the action and, where it helps, the object and count: "Send 3 invoices".
- Errors say what happened, what it means for the person, and what to do. No blame, no apology spiral, no "Oops".
- Empty states say why it's empty and give the first step.
- Use the person's words for things, not the system's.
- Keep sentences short. Most interface sentences need fewer than 15 words.
- One idea per string.
- Use the brand's words; never use its avoid list.

### 4. Remove the fingerprints

Check the draft against [references/fingerprints.md](references/fingerprints.md), then run the linter on any file of strings:

```bash
python scripts/copy_lint.py strings.md --brand BRAND.md
```

It flags em and en dashes, stock phrases, "not X, it's Y" framing, exclamation marks, emoji, vague errors and buttons, long sentences, and words on the brand's avoid list. Fix every flag or say why it stays (a quoted user review, a product name).

### 5. Show the work

For edits, show before and after side by side with a one-line reason for each change. For new copy, give each string with its location, and note any string whose length might break the layout (translations run 30 to 40 percent longer).

## When to push back

Say so briefly, then still deliver:

- the requested tone fights the moment (jokes in a data loss error)
- the copy is being asked to hide something people need to know (a fee, a data use, a consequence)
- the brand's voice rules contradict each other; name the conflict and which rule you followed

## Output

A table or list of strings: location, copy, and a note where useful. For JSON or other string files, return the file in the same format with keys unchanged.

Match the language of the product. In languages other than English, follow that language's own conventions for punctuation and formality rather than translating English rules.
