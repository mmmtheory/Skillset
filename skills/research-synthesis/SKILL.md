---
name: research-synthesis
description: Synthesises user research into evidence-linked findings a team can trust. Use when someone shares interview transcripts, usability test notes, open-text survey answers, support tickets or field notes and asks for themes, insights, an affinity map, a synthesis, a readout or what was learned. Every insight is traced to verbatim quotes and participant counts, with confidence rated. Not for planning a study or writing an interview guide.
license: MIT
metadata:
  author: Matthias Schmutz
  version: "0.1.0"
---

# Research synthesis

Synthesis turns what people said and did into a small number of claims a team can act on, each one honest about how strong its evidence is.

Without this skill, agents tend to:

- summarise each interview in turn instead of finding patterns across them
- name topics ("Pricing", "Onboarding") and call them insights
- paraphrase and then present it as a quote, or blend two people into one quote
- turn one vivid participant into "users want"
- report solutions people suggested as needs ("users want dark mode")
- confirm the hypothesis the requester mentioned and drop what contradicts it
- produce twelve themes of equal weight

The work below prevents each of these.

## Workflow

### 1. Take stock

List every source you were given and give each participant a stable ID (P1, P2 and so on, or the IDs already in the files). Note:

- the research questions, if stated; if not, infer two or three from the material and state them at the top of your output as inferred
- the participant mix (role, segment, experience) only as far as the sources say
- gaps: missing transcripts, notes that are summaries rather than verbatim, sessions that ended early

If the material is notes rather than transcripts, say so in the method note. Notes carry the note-taker's interpretation, so quotes from them are weaker.

### 2. Index the quotes

When sources are text files, build a quote index first:

```bash
python scripts/quote_index.py index <source files> --out quotes.json
```

This splits each file into utterances, labels each with a participant and quote ID (P3-Q12), and leaves moderator lines out. Survey exports in CSV give one quote per row, keyed by the respondent ID. Check the participant mapping it prints, and pass `--moderator "Name"` if a moderator is labelled by name. Work from the index so every claim can point back to a real line. If you cannot run scripts, keep the same discipline by hand: copy quotes exactly, with their participant ID.

### 3. Code observations

Read across all sources and pull out atomic observations: one behaviour, goal, pain, workaround or reaction per observation, each tied to a quote ID. Keep observation separate from interpretation. "P4 exported to a spreadsheet every Friday" is an observation. "P4 does not trust the in-app numbers" is an interpretation and needs its own evidence.

Coding conventions and examples are in [references/coding-guide.md](references/coding-guide.md).

### 4. Cluster across participants

Group observations by what they mean, not by which part of the product they mention. A cluster that only one participant feeds is a signal, not a theme. Aim for three to six insights. If you have more, the lower ones become a short list of signals worth watching.

Actively look for counter-evidence for each cluster: participants who did the opposite, or who did not mention it when they had the chance. Record it.

If the person named a hypothesis, test it like any other cluster. Report it as supported, not supported or unclear. Do not lead with it unless the evidence earns that.

### 5. Write insights, not topics

Each insight is a full sentence a designer could act on:

> **[Who]** [does or feels what] **because** [why], **so** [what that means for the design].

"Onboarding" is a topic. "First-time admins skip the setup checklist because it asks for data they do not have yet, so they reach the main screen with an empty account and assume the product is broken" is an insight.

### 6. Rate the evidence

For every insight give the participant count as "n of N" and a strength rating using [references/evidence-rubric.md](references/evidence-rubric.md). With small qualitative samples, never convert counts to percentages.

### 7. Separate findings from implications

Findings describe what is true of these participants. Implications say what it could mean for the design, framed as opportunities ("How might we..."). Recommend specific solutions only if the person asked for recommendations, and label them as yours.

When a participant suggests a feature, report the need behind it and note the suggestion as their idea.

### 8. Verify every quote

Before you hand over a report built from text files, check it:

```bash
python scripts/quote_index.py verify report.md --sources <source files>
```

Any quote that does not appear verbatim in the sources, or is attributed to the wrong participant, must be fixed or cut. Ellipses and [square bracket clarifications] are allowed; the parts between them must match exactly.

## Output

Use [references/report-template.md](references/report-template.md) unless the person asked for another format. Lead with the three findings that matter most in plain sentences. Then one card per insight, then signals, then what this research could not tell you.

Quote at most three times per insight. Pick the quotes that show the reason, not just the feeling.

Write plainly. No em dashes, no hype, no closing summary. Match the language of the sources unless asked otherwise, and keep quotes in their original language with a translation beside them if the report is in another.

## Care with people's words

Participant quotes are personal. Keep IDs, not names, unless the person explicitly asks for names. Leave out details that identify someone (employer, exact location, health details) unless they are essential to the finding.
