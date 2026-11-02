---
id: d-bwb1tt
kind: decision
title: "The carried command tests run in process against the handler, and through the binary on a socket"
scope: process
decided_by: planner
date: 2026-11-02T19:16:34+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Global Constraints"}
  - {value: "80", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, line 80"}
  - {value: "5", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md, item 5"}
---

The carried command tests run the command in process against a server's handler over an in-memory store, the person signed in through a software authenticator.
A hand edit is a store write bypassing the operations, git reads are store reads, `staged` is `published`, and a held add (d-znagqe) is approved through the person's session.
With `LODGE_E2E_BINARY` set, the coordinator runs them with the compiled binary over a loopback socket.

## Reasoning

The builders' sandbox refuses sockets (plan 1, Global Constraints), and a handler answers a `Request` with no socket (plan 1, probe 1; d-sry12f).
lodge 0.2's tests edit files under `lodge/` by hand to make a broken or ambiguous store (`tests/e2e/test_search_shows_unparsable_file.py`, `tests/e2e/test_show_ambiguous_code_one_line.py`, `tests/e2e/test_broken_agent_decision_warns_above_show.py`, `tests/e2e/test_check_and_gate.py`); on the server such a store comes from an import or damage, and a direct write stands in for either.
A record is current from the moment it is written (design line 80), so lodge 0.2's `staged` is the server's `published`.
Plan 1 ends this plan when "the compiled binary runs them" (plan 1, "The rest of build step 1"), and a compiled client reaches `Bun.serve` in the same process when it is started with an awaited `Bun.spawn` (the plan's probe 5).
lodge 0.2's tests add decisions `decided_by: author` (`tests/e2e/support.py`, `decision_text`), which plan 2 holds for the person `author` (d-kj59bz); approving them is the model change, and the carried test asserts the held add's lines and then the approval's.
Cost if wrong: the in-process run misses a fault of the real transport, which the binary run catches.
