---
tags: [design-brief]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Design brief for adding saved addresses to checkout in our grocery delivery app. Primary users are repeat customers on mobile. 38% of orders go to a different address from the customer's last order (our data). We have to use the existing address API. Launch by end of Q1. Success means repeat orders get through checkout faster; median checkout time for repeat orders is 2m40s today. Don't touch the payment step.
