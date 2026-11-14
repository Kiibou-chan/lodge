# Task 4 recheck 1

Fix diff `9f47e33..d3ba49c`, scratch worktree at d3ba49c (removed).
`sh scripts/check-ts.sh`: exit 0, 1022 pass, 0 fail.

## Findings

- C1: answered (`ts/tests/app/reads-checks.test.ts:111-115`); with `no ${what}; ` removed at `ts/src/app/state.ts:101`, `bun test tests/app` gives 80 pass, 4 fail.
- C2: answered (`ts/src/app/threads.ts:47`, `:52`; `ts/tests/app/message-space.test.ts`); with `strip` put back to `trim`, the three rows fail (0 pass, 3 fail).
- C3: answered (`ts/tests/app/reads-checks.test.ts:136-138`), `raises(call, NotFound, …)` on one promise.
- P1: answered (`ts/tests/structure/calls.ts:103`, template fixture and message assertion at `core-rules.test.ts:67-76`); with `isStringLiteral` put back, 1 fail.
- P2: answered (`ts/tests/parity.json:51`, `["3", "4"]`).
- P3: answered (`ts/src/app/lodge.ts:32-93`, `reads.ts:62,93`); every method annotated, parameters named `thread`.
- P4: answered (`ts/src/app/reads.ts:147-152` throws naming the ID; `reads-checks.test.ts:74-80` fails on a missing file).
- D1: answered (`ts/src/app/threads.ts:63-74`, `lodge.ts:81-84`), `close` in `MessageOptions`.
- P5: answered differently but adequately, the fix report has file:line and expression columns.

## New problems

None.

Verdict: 0 Blocking, 0 Important, 0 Minor
