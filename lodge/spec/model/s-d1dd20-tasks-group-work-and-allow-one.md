---
id: s-d1dd20
kind: spec
title: "Tasks group work and allow one level of children"
rests_on: [s-g8m3qv, s-tprwhs]
---

From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks.
A plan's tasks are its children, with one level of nesting and no deeper nesting.
From build step 5, each task occupies one workflow step, the planner session creates child tasks through the API from the plan, and the parent waits at its build step until every child is done.
From build step 6, a task also has code links.
