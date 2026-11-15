---
id: s-h4x7bx
kind: spec
title: "The planner creates children and the parent waits"
rests_on: [s-d1dd20]
---

The planner session creates child tasks through the API from the plan.
The parent waits at its build step until every child is done.
