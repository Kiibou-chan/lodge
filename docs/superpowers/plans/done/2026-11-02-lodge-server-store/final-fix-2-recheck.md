# Final fix 2, recheck of 7452afe

Method: scratch worktree detached at 7452afe, mutation of each fix, `sh scripts/check.sh`, a probe, `git diff 4ee6cf4 7452afe`.

## B-1: answered (`ts/src/core/confirmation.ts:16-31`, `ts/src/app/confirm.ts:45,65`, `ts/src/app/reads.ts:57`)
`confirmableIds` takes the person and drops a decision only when that person's non-imported confirmation names it, matching `confirmedByPeople` (`derive-flags.ts:30`).
Mutation: removing the `decidedBy === person` condition fails both new tests (`ts/tests/app/people.test.ts`, `confirmations_remain_available_to_each_person_both` and `_ada`).
Both tests go through `Lodge.confirm`, check `derive(...).awaiting` after each step and at the end (empty), and `Shown.confirmable` per person.
Ruling d-8v05kt is followed as written.
One-person behaviour through a person actor is unchanged: `confirm.test.ts` and `show_marks_confirmable` pass unmodified.

## A-1: answered (`ts/src/store/sqlite-store.ts:93`)
Guard restored exactly as briefed.
Mutation: deleting the line fails `stale_base_is_rejected_and_writes_nothing`, whose loop now includes `${live.rev}.0` and ` ${live.rev}` read after the first publish (`ts/tests/store/sqlite-store.test.ts:58-59`).

## A-2: answered (`ts/src/app/lodge.ts:80-84,92-96`)
`ask` and `reply` forward `where`, `when`, `commit` only.
Mutation: passing `options` through fails `reply_ignores_a_runtime_close_option` (`ts/tests/app/message-options.test.ts:20`).

## B-2: answered (`ts/tests/parity.json:566`)
Row is `changed`.
Reverting it fails no test, as the finding itself said (`held()` accepts both); not a defect of the fix.

## Gate
`sh scripts/check.sh` at 7452afe in the scratch worktree: exit 0 (1304 bun tests, 2 todo, 0 fail; differential 0 differences).

## New problems

### N-1 (Minor) · Agent reads now report already-confirmed decisions as confirmable
Handle: `ts/src/app/reads.ts:57` and `ts/src/app/confirm.ts:27` pass `null` for a non-person actor, and `confirmableIds` (`confirmation.ts:21-24`) then matches `decidedBy === null`, so no confirmation is ever counted.
Verified by probe (removed): one-person store, the person confirms `d-aaaaaa`, then an `agent("coord")` calls `show` and `behindArea("storage")`; result `confirmable` true and one row, where 4ee6cf4 gave false and none.
So one-person behaviour is unchanged for person actors only; for agent reads the list regrows with decisions already confirmed.
Scenario: plan 3 or 4 serves a read-only agent endpoint and the agent sees confirmed decisions still behind the area.
Fix: for a null person, count a confirmation by any member of `s.people` (the `confirmedByPeople` reading), or state in the brief that agent reads are meant to show them and add a test pinning it.
Minor because an agent cannot confirm (`Forbidden`, `confirm.ts:63`) and no test or caller reads it.

No Blocking or Important problems found.

Verdict: 0 Blocking, 0 Important, 1 Minor
