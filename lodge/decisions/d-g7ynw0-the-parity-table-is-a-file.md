---
id: d-g7ynw0
kind: decision
title: "The parity table is a file that a test checks"
scope: process
decided_by: planner
date: 2026-11-02T14:10:35+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "0.2", handle: "grep ^version pyproject.toml"}
  - {value: "126", handle: "find tests -type f | wc -l"}
---

The parity table is `ts/tests/parity.json`, mapping each of lodge 0.2's 126 test files to its TypeScript files, or to "changed" with the design's line, or to "later" with the build step; a test in the TypeScript gate checks that every Python test of a file marked ported has a TypeScript test of the same name.

## Reasoning

`tests/` holds 126 files (`find tests -type f | wc -l`), and the design makes them the specification (design, "Constraints"); a table only in the plan would drift as tasks port files.
A test that reads the Python files' `def test_` names and the TypeScript files' test names turns "carried over" into a check the gate runs, so a skipped test fails the gate rather than a review.
Each later plan flips its files from "later" to "ported" or "changed", so the table states at every point how far the port has come.
Cost if wrong: one JSON file and one test of about a hundred lines.
