# Task 12b recheck 1

Rechecked fix d34be5b against `task-12b-review.md` (I-1, M-1 to M-5), in a scratch worktree at that commit (removed after).
Gate `sh scripts/check-ts.sh` there: exit 0, 1271 pass, 2 todo, 0 fail.
Diff read: `ts/src/app/{held,writes}.ts` and the tests `held.test.ts`, `held-approve.test.ts`, and the new `held-payload.test.ts`; the test diff only adds assertions and tests, and deletes none.

## Findings

- I-1: answered, `ts/tests/app/held-payload.test.ts:7-31` (run with importing false and true; checks `held()` attachments, importing, and message against a direct publication, then the approved attachment path, text, and message).
- M-1: answered, `ts/tests/app/held.test.ts:73-83` (two holds in `seq` order, and the literal `"held for approval"`).
- M-2: answered, `ts/tests/app/held-approve.test.ts:87-88` (wrong actor, blank reason, `Forbidden`) and `ts/tests/app/held.test.ts:24` (`by: "bo"`).
- M-3: answered, `ts/tests/app/held-approve.test.ts:113-123` (settled after the first rejection, one attempt); `writes.ts:74` keeps only the open-check and drops the re-parse.
- M-4: answered, the clause is gone at `ts/src/app/writes.ts:168`.
- M-5: answered, `held.ts:29` passes `w`, and the `person` import is removed (knip and biome pass).

## Mutations re-run at d34be5b

Each was applied alone to `ts/src`, run with `bun test tests/app tests/store`, and reverted.
- M16 (`attachments: []` in the hold): 2 fail, killed.
- M17 (`importing: false` in the hold): 1 fail, killed.
- M18 (`message: ""` in the hold): 2 fail, killed.
- M26 (`held()` reversed): 1 fail, killed.
- M30 (`HELD` text `"held"`): 1 fail, killed.
- N03 (reason checked before `authorised`): 1 fail, killed.
- N05 (`by` always `"agent"`): 1 fail, killed.
- M15 (in-loop refresh removed): 2 fail, killed.

## New problems

None.
`writes.ts` is 254 lines, the largest changed module; the new and changed test files are under 130 lines.
No em-dash in the added lines; the report and tests use British English.
No dependency added.
M-6 and M-7 stay open for plan 3 as the brief says.

Verdict: 0 Blocking, 0 Important, 0 Minor
