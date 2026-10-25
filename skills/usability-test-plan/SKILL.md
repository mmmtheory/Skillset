---
name: usability-test-plan
description: Plans a usability test or interview study that will answer a real product decision. Writes the research questions, picks the method, defines who to recruit with a screener, writes realistic task scenarios without leading wording, a moderator script with neutral probes, success measures per task and a note sheet ready for synthesis. Use when someone asks to plan a usability test, test a prototype or flow with users, write test tasks, a discussion or interview guide, a screener, or set up an unmoderated study in a tool like Maze, Lyssna or UserTesting. Not for analysing sessions that already happened (research-synthesis).
license: MIT
metadata:
  author: Matthias Schmutz
  version: "0.1.0"
---

# Usability test plan

A good test plan starts from the decision the team has to make and works backwards to the fewest sessions and tasks that will inform it. It produces behaviour to observe, not opinions to collect.

Without this skill, agents tend to:

- jump to tasks without saying what the team will decide with the results
- write tasks that give the answer away by using the interface's own labels ("Go to Settings and change your plan")
- ask for opinions and predictions ("Would you use this?", "How much would you pay?") and treat the answers as evidence
- ask leading or double-barrelled questions ("How easy and useful was that?")
- recruit "users" instead of people defined by what they actually do
- write screeners that reveal what the study is looking for
- pack ten tasks into a 45 minute session
- leave out success criteria, so every session ends with "they seemed to get it"
- claim percentages or statistical confidence from five sessions

## Workflow

### 1. Start from the decision

Ask what the team will do differently depending on what they learn. Write two to four research questions, each tied to that decision:

> **Decision:** whether to ship the new transfer flow in November or keep iterating. **Question:** can first-time users send money to a new recipient without help, and where do they hesitate?

If the request is about demand, willingness to pay or which concept people "like", say that a usability test cannot answer it reliably, and suggest a method that can (see [references/methods.md](references/methods.md)). Plan what can be tested and be clear about the rest.

### 2. Choose the method

Pick from [references/methods.md](references/methods.md) and say why in one or two sentences: moderated or unmoderated, remote or in person, prototype fidelity, task-based test or interview, and whether a quick method (first-click test, tree test, five-second test) answers the question more cheaply.

Sample size: five to eight participants per distinct group is enough to find most usability problems in a flow. It is not enough to estimate rates or compare designs with confidence; say so if the person wants numbers, and size a quantitative study separately.

### 3. Define who to recruit

Describe participants by behaviour and context, not demographics: "has sent money to someone overseas in the last three months, using any app" rather than "25 to 40, tech-savvy". Include the mix you need (new and existing customers, mobile and desktop, an accessibility need) and who to exclude (employees, people in UX or market research, competitors' staff).

Write the screener using [references/screener.md](references/screener.md): behavioural questions with multiple choice answers, plausible distractors, and no question that reveals the product or the right answer.

### 4. Write the tasks

Each task is a short scenario with a goal and a reason, in the person's words, ending at a point both of you will recognise:

> Your sister in Fiji needs NZ$200 for her rent by Friday. You haven't sent her money before. Send it to her.

Not: "Use the Send button to add a new recipient." Rules and rewrites are in [references/task-writing.md](references/task-writing.md).

For every task, record: the research question it serves, the starting screen, what success looks like, what to watch for, and a time budget. Order tasks the way people would do them in real life, and put the most important task early in case sessions run long.

Check the tasks before you go on:

```bash
python scripts/task_lint.py plan.md --ui-terms "Send, Add recipient, Payees, Settings" --session 45
```

The script flags tasks that use interface labels, start with interface verbs (click, tap, navigate), and questions that lead, double up or ask people to predict. It adds up the time budgets against the session length. Fix every flag, or say why one should stay.

### 5. Write the script

Follow [references/script-template.md](references/script-template.md): welcome and consent, a few warm-up questions about past behaviour, the tasks with neutral probes, a short question after each task, wrap-up, and thanks. Write probes in advance ("What are you looking for?", "What did you expect to happen?") so the moderator is not tempted to explain the interface.

For unmoderated tests, the script is the instructions on screen: shorter tasks, an explicit "I'm done" or "I'm stuck" signal, and a post-task question after each, because nobody can probe.

### 6. Make the prototype ready

List the paths the prototype must support for each task, the data it must show (realistic names, amounts and dates, not lorem ipsum), and what happens on a dead end. Plan one pilot session with a colleague to catch broken links and unclear tasks before real participants.

### 7. Prepare to capture

Provide a note sheet: one row per participant per task, with completion (success, success with help, failure, gave up), time if relevant, the path taken, observations, and quotes word for word. Use participant IDs (P1, P2), never names. This sheet feeds straight into synthesis.

## Output

```markdown
# Usability test plan: <what is being tested>

**Decision this informs:** ...
**Research questions:** numbered
**Method:** and why
**Participants:** criteria, mix, exclusions, number
**Session:** length, format, tools, recording and consent

## Screener
## Tasks
| # | Scenario | Serves | Start | Success looks like | Watch for | Minutes |
## Script
## Prototype checklist
## Note sheet
## What this study will not tell us
```

Keep the plan as long as the study needs and no longer. A two-task guerrilla test does not need a twelve-question screener.

## Tone

Plain, friendly to participants, exact for the team. Scenarios and questions are written in the participants' language, which may differ from the team's. If the request is in another language, write the plan in that language.
