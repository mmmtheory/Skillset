# Weak and strong briefs from the same request

**Request:** "We need a dashboard for our small business customers so they can see how they're doing. Can you brief it?"

Context given: a bookkeeping app for sole traders; support says customers ask "am I making money?"; the team has six weeks.

## Weak

> **Project: Customer Dashboard**
>
> **Overview:** We will create a modern, intuitive dashboard that empowers small business owners to gain valuable insights into their business performance.
>
> **Goals:** Improve user engagement and satisfaction. Increase retention by 20%.
>
> **Target users:** Small business owners aged 25 to 55 who are tech-savvy.
>
> **Features:** Revenue charts, expense breakdown, profit and loss, cash flow forecast, KPI widgets, customisable layout.
>
> **Success metrics:** Positive user feedback, increased daily active users.

What is wrong with it:

- The solution (dashboard, six features) is the brief. The problem never appears.
- "Increase retention by 20%" is invented. Nothing given supports it.
- The audience is a demographic with an invented age range.
- "Increased daily active users" rewards the wrong thing for a bookkeeping tool. Sole traders should not need to check daily.
- No scope, no constraints, no anti-goals, no risk. Six weeks is ignored.

## Strong

> # Money check: brief
>
> **Problem**
> Sole traders can record income and expenses in the app but cannot answer "am I making money this month?" without exporting to a spreadsheet. They ask support instead, or guess.
>
> **Audience**
> - Primary: a sole trader opening the app between jobs, on a phone, wanting a yes or no and a reason.
> - Secondary: support, who currently answer this question by hand.
>
> **What we know**
> - "Am I making money?" is a recurring support question (support team).
> - The app already holds categorised income and expenses.
> - *Assumption:* most users check monthly or less, not daily.
> - *Assumption:* GST and tax estimates are out of reach for six weeks.
>
> **Success**
>
> | Measure | Baseline | Target or direction |
> | --- | --- | --- |
> | Support tickets asking about profit | unknown, tag tickets from week 1 | down |
> | Users who can state this month's profit in a 5-person test | unknown | 4 of 5 |
> | Guardrail: wrong or misleading figures reported | 0 | hold at 0 |
>
> **Scope**
> - In: a single view answering profit so far this month and compared with last month, with the biggest drivers.
> - Out: forecasting, custom layouts, tax estimates, desktop-specific layouts.
>
> **Anti-goals**
> - Not designed to increase daily visits.
> - No figure shown without the period and basis it covers.
>
> **Tensions decided**
> - Clarity over completeness: one honest number beats six charts.
> - Plain language over accounting terms, with the formal term available on tap.
>
> **Riskiest assumption**
> That users trust a profit figure the app calculates. Test with five users and a clickable prototype in week 2, before building.
>
> **Open questions**
> - Do we treat uncategorised transactions as expenses, income or exclude them? (product lead)

Why it works: the dashboard has disappeared as a given, the brief fits six weeks, every number is either sourced or marked as unknown, and the guardrail protects the one thing a money tool cannot get wrong.
