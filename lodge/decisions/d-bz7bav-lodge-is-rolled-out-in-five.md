---
id: d-bz7bav
kind: decision
title: "lodge is rolled out in five steps, evaluated on the first user's past before a pilot"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:24+01:00
changes:
  - {entry: s-5gmxyx, action: create}
  - {entry: s-awc4kb, action: create}
  - {entry: s-x84e3h, action: create}
  - {entry: s-t7qz74, action: create}
---

lodge is built, then holds its own decisions, then is evaluated on the first user's past in a scratch copy, then piloted with the old files frozen, then replaces the old files.
The build provides only what the importer needs.

## Reasoning

The order was agreed with the author.

The sample size and replay method for the evaluation go in their own plan once lodge exists, because they set most of the cost, and that plan also owns the importer and all measurement; this was the specification author's call.

This build therefore provides only what the importer needs: `imported_from`, explicit past dates, so that `core` stays clock-free because the date is data, and the exemptions in the author-quote and entry-needs-decision checks.

An imported author decision without a recoverable quote shows as imported, unquoted, at Level 1, so that it does not read as more settled than it is, which answers the first must-not.

Measurement is counted from the session transcripts the first user already keeps and its cost logs, so lodge itself writes no telemetry.
