---
id: d-3ywdhq
kind: decision
title: "The API wire keeps TypeScript names, tags maps, answers a failed check whole, carries the version"
scope: process
decided_by: planner
date: 2026-11-02T19:16:29+01:00
narrows: [d-sry12f]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "422", handle: "lodge show d-sry12f (check-failed)"}
---

On the API's wire a field keeps its TypeScript name, so `dryRun` where d-sry12f writes `dry_run`; a `Map` or a `Set` is tagged, `api` encodes, and the command decodes; a write whose check fails answers 422 with its whole result; an unknown project answers the kind `no-project`, and an unexpected error the kind `internal`; every answer carries `Lodge-Version`, which the command requires to equal its own.

## Reasoning

The command prints what lodge 0.2 prints from `app`'s results (`src/lodge/cli/output.py`), so it needs them whole, and `Read.statuses`, `ThreadList.titles`, and `ThreadsWaiting.titles` are mappings (`src/lodge/app/results.py`), which `JSON.stringify` writes as an empty object; the TypeScript results keep the camelCase names of plan 1's Global Constraints, so the wire keeps them too.
lodge 0.2 prints a failed add's feedback, notes, problems, and outcome, then exits 1 (`src/lodge/cli/output.py`, `added_lines`; `src/lodge/cli/commands.py:107`), which needs the whole `Added`, the "check's problems and the feedback" of d-sry12f and more.
lodge 0.2 says `lodge has no data in this repository yet; run \`lodge init\`` before `init` (`tests/e2e/test_before_init_one_sentence_exit_2.py`), and only a kind of its own tells a missing project from a missing record.
The command treats a decoded answer as `app`'s result type, which holds only when the server and the command are the same build.
Cost if wrong: a field renamed in the command's client and in the API's argument checks.
