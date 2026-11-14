# Plan recheck 2: plan 2, the events store and the operations

Rechecker, on `server-store`, fix round d3ce2fd..c3541fc, against N-1 to N-5 of `plan-recheck-1.md` and the answers in `plan-fix-2.md`.
Line numbers are of the plan at c3541fc (`docs/superpowers/plans/2026-11-02-lodge-server-store.md`) and of its ledger at c3541fc.
No probe was needed: the cycle rule was probed in recheck 1.
Status: done.

## Findings of recheck 1

- N-1 · Resolved.
  `ts/src/app/awaits.ts` is under Create and imports nothing of `writes.ts` or `held.ts` (line 599); `writes.ts` holds where `awaits.ts` says (line 600); the Interfaces state the edges `held.ts → writes.ts → awaits.ts` and cite `no-circular` at `ts/.dependency-cruiser.cjs:40-44` (line 605), which is where the rule stands at `origin/server-core` 9e133ea.
  The three edges form no cycle, `held.ts` alone calls `add`'s attempts, and `awaits.ts`'s exports are read by `writes.ts` in the same task, so knip needs no `entry` row.
- N-2 · Resolved.
  d-j28rp0 replaces d-pmaw3a (`lodge show d-pmaw3a`: `replaced by d-j28rp0`), narrows its claim to "no write of `app` changes a decision's fields", and names the re-render case with its cost.
  Its handles hold: `src/lodge/core/check_immutable.py:49-52` compares parsed fields, `src/lodge/core/apply.py:188` writes `write_record(record)`, and `src/lodge/app/writes.py:90` keeps every path whose text differs; the earlier handles (`plumbing.py:14-25`, `trees.py:32`, probes 1 and 6) are d-pmaw3a's, checked in recheck 1.
  The plan cites d-j28rp0 at every place d-pmaw3a stood (Calls made 10, Review Focus 4, line 181, Task 7b's two citations at line 412, Task 9's lead at line 481); `a_published_decision_is_never_rewritten` now covers the re-render (line 424), and `rebuild_gives_the_same_tables` rewrites an entry (line 426).
  Two citations of the lineage are left, Minor R-1 and R-2 below.
- N-3 · Resolved: `an_agent_cannot_write_as_a_person` gives each call `where: "chat"` (line 559).
- N-4 · Resolved: ledger line 18 is rewritten in place to name STORE-1.
- N-5 · Resolved: Task 10's Step 3 names the four definitions as the only lines without `people` (line 537).

## New findings

### R-1 · Minor · the ledger's plan 3 alignment line still cites the replaced d-pmaw3a

Handle: ledger line 28 ("`publish` refuses a changed decision file (d-pmaw3a)"), while ledger line 21 and the plan cite d-j28rp0.
Failure: plan 3's alignment round, which reads this line, follows a decision `lodge show` reports as replaced and misses d-j28rp0's accepted re-render refusal.
Fix: write d-j28rp0 in place of d-pmaw3a on line 28.

### R-2 · Minor · line 181 says d-j28rp0 replaces d-pprhpz

Handle: plan line 181 ("(d-j28rp0, replacing d-pprhpz)"); d-j28rp0's provenance gives `replaces: d-pmaw3a`, and Calls made 10 states the chain correctly ("replacing d-pmaw3a, which replaced d-pprhpz").
Failure: a reader following line 181 looks for a link `lodge` does not hold.
Fix: "(d-j28rp0, replacing d-pmaw3a)".

## Checked, no finding

- The diff touches only the plan, the ledger, `plan-fix-2.md`, and the new decision; no task's waits, Files, or interfaces change outside Task 12b's two module lines, so the lane check of recheck 1 stands.

## Counts

Recheck 1's findings: 5 of 5 resolved (N-1 Important, N-2 to N-5 Minor).
New: 0 Blocking, 0 Important, 2 Minor (R-1, R-2).
