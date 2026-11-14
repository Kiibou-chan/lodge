---
id: d-ae1vn5
kind: decision
title: "The Store port keeps lodge 0.2's methods, and the SQLite store gives one state"
scope: process
decided_by: planner
date: 2026-11-02T19:05:28+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "0.2", handle: "grep -n '^version' pyproject.toml (0.2.0)"}
---

The `Store` port keeps `commit`, `trees`, `freshness`, `gate`, and `publish` with lodge 0.2's outcomes, so the carried app tests run over the in-memory fakes unchanged; the SQLite store gives one tree as both the current and the published state, compares the current state with itself in `gate`, never stages, answers `commit` with `FAILED`, and reports no freshness.

## Reasoning

The parity table marks only `tests/app/test_reads_published.py` and `tests/app/test_writes_retry.py` as changed (`ts/tests/parity.json`), while carried files test staging, commits, and the labelled gate through the fake store: `test_check_gate_compares_with_the_published_state` in `tests/app/test_reads.py`, `test_commit_after_staged` in `tests/app/test_confirm.py`, `test_commit_after_staged_when_asked` in `tests/app/test_thread_ops.py`, `test_staged_second_edit_builds_on_first` in `tests/app/test_writes.py`, and `test_two_adds_in_one_second_are_dated_a_second_apart` in `tests/app/test_writes_dates.py`.
Narrowing the port would change those files too, against the table, and against the brief's rule that `app`'s public names stay those of `src/lodge/app` (`docs/superpowers/plans/2026-11-02-lodge-server-store/planner-brief.md`, Scope).
The design makes the published state the server's current state (design, "The model"), which the adapter gives without a change to the port.
Cost if wrong: a later narrowing removes staging, `commit`, and the gate's labels from `app` and from those tests, which then say what changed.
