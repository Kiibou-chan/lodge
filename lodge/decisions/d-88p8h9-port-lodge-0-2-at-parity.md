---
id: d-88p8h9
kind: decision
title: "Port lodge 0.2 at parity first, then make the design's changes as tasks of their own"
scope: process
decided_by: planner
date: 2026-11-02T14:10:33+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "0.2", handle: "grep ^version pyproject.toml"}
---

Each part of lodge 0.2 is first ported at parity, every carried test keeping its Python name without `test_`, and only then do separate tasks make the design's changes (people in `decided_by`, drafted decisions awaiting a person, the check on every write), each with new tests.
TypeScript code names things in camelCase, and the record file format keeps its keys as they are.

## Reasoning

lodge 0.2's tests are the specification of the behaviour that carries over (design, "Constraints"; brief), and a carried test only proves parity while it asserts what the Python test asserts.
Changing the model during the port would edit tests and code in one step, and a reviewer could no longer tell a porting slip from an intended change.
The design's changes are listed in "The model" and touch `decided_by`, the review flag, and when the check runs, all in code the port has by then proved.
A test keeping its Python name lets a script match every Python test to its TypeScript counterpart (the parity table, its own decision).
camelCase is the language's convention and Biome's default; the file keys (`decided_by`, `rests_on`, `work_item`) are the format the export must write unchanged (design, "Export to git").
Cost if wrong: a model change made after the port touches code a second time, which the port's tests then guard.
