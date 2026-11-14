---
id: d-kj59bz
kind: decision
title: "A person is a member of the project, and lodge 0.2's words stay for a person named author"
scope: process
decided_by: planner
date: 2026-11-02T19:05:33+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "0.2", handle: "grep -n '^version' pyproject.toml (0.2.0)"}
  - {value: "7", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, 'Build order', item 7"}
---

`decided_by` names a person when it names a member of the project; the core reads the project's people from `Tree.people`, which the default-filling `tree()` sets to `author` alone and the SQLite store to the project's members, owners and members alike; each message and flag that says "the author" keeps lodge 0.2's words when the person is `author` and names the person otherwise; `Lodge` takes the actor, and only a person confirms.

## Reasoning

The design has `decided_by` name a person or an agent role, "the author" becoming the person who decided (design, "The model").
With `author` as the default person, the core's carried tests and the differential run on this repository's records (d-0qmd10), whose one person is `author`, keep proving parity unedited.
Every reader of `is_author` already takes a snapshot (`grep -n is_author src/lodge/core/*.py`: `derive`, `check_state`, `check_immutable`, `views`, `feedback`, and `confirmation`), so the people reach them through the tree and `load` with no new parameter on `derive` or `check_state`; `parse_thread` and `write_thread` gain one.
Owners and members both count as people until roles arrive, since one person signs in until the design's step 7 (design, "Build order").
A confirmation is the confirming person's decision, as lodge 0.2's is the author's (s-bhew59), so an agent cannot confirm.
Cost if wrong: the people move to another carrier, which touches the same call sites.
