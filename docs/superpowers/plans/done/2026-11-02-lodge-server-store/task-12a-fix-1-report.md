# Task 12a, fix round 1 report

Completed I-1 to I-4 and P-M1 to P-M3 on `server-store`.

- Settled-hold decline checks assert both `NotFound` and its message.
- Rebuild runs over the populated `held` table, exercising its own deletion.
- A two-project test checks isolated listings, foreign decline and approval refusals, and unchanged events after each refusal.
- Write-first checks include decline and approval with a held sequence. Missing-project hold and decline check the error class, message and unchanged events.
- `MemoryStore.hold` uses `stampOf(START)`. Successful declines record `[seq, reason]`; the fake test also checks refused declines leave no record.
- Both SQLite settlement operations use `openHold(tx, project, seq)` in `read-tree.ts`.

## Test-first evidence

Before changing implementation, the changed fake test failed against the old fake because `declined` was undefined. Each temporary source mutation below was tested separately and restored immediately; every targeted test failed.

| Mutation | Failing regression |
| --- | --- |
| M3: remove decline's typed open-hold refusal | `a_settled_hold_cannot_be_declined` |
| M6: remove rebuild's held-table deletion | `holds_rebuild` |
| M8: remove listing's project filter | `holds_belong_to_their_project` |
| M9: remove decline lookup's project filter | `holds_belong_to_their_project` |
| M10: remove approval lookup's project filter | `holds_belong_to_their_project` |
| M15: remove decline's opening head write | `transaction_writes_heads_first: decline` |
| Remove hold's opening project guard | `missing_project: hold` |
| Remove decline's opening project guard | `missing_project: decline` |
| Remove approval's opening compare-and-set | `transaction_writes_heads_first: approve` |

## Validation

`sh scripts/check-ts.sh` passed: formatting, TypeScript, dependency checks, unused-code checks and the full suite, with 1,253 pass, 2 todo and 0 fail. The three targeted test modules passed all 17 tests. An initial formatting failure in `write-first.test.ts` was corrected before the successful full run.

All changed modules remain below 300 lines. No dependency was added. No subagents were used.
