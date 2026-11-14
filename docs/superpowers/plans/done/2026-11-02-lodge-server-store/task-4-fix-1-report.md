# Task 4 fix round 1 report

Addressed C1, C2, C3, P1, P2, P3, P4, and D1.
P5 is addressed by the location and expression columns below.

## Changes

- `ts/tests/app/reads-checks.test.ts`: all four unreadable-file cases now require the appropriate `no record named` or `no area named` prefix; the missing-file case checks `NotFound` and the exact message on one promise; draft pairs use `as const` and throw when their source file is missing.
- `ts/tests/app/message-space.test.ts`: three new regression cases cover every input in C2, including publication and the minted ID for U+FEFF.
- `ts/src/app/threads.ts`: use core `strip` for role and location validation; move `close` into `MessageOptions`.
- `ts/src/app/lodge.ts`: declare the return types of every Task 4 method, name the reply and close parameter `thread`, and pass the closing flag in the options object.
- `ts/src/app/reads.ts`: declare tuple return types for `waitingAll` and `check`; report a missing decision by ID instead of passing an empty date to `instant`.
- `ts/tests/structure/calls.ts`: recognise computed template-literal `ok` keys with `isStringLiteralLike`.
- `ts/tests/structure/core-rules.test.ts`: add the template-key fixture and require the specific check-result diagnostic in the app fixtures.
- `ts/tests/parity.json`: attribute the writes port to Tasks 3 and 4.

## Failing runs before fixes

Each mutation was reverted immediately after its run.
Locations refer to the finished source; expressions state exactly what changed.
C1 assertions and C2 cases were written before their failing runs.

| Finding and test | file:line | Mutation or original expression | First failing result |
|---|---|---|---|
| C1, show unreadable record | `ts/src/app/state.ts:101` | Remove `no ${what}; ` from the unreadable message | Expected full prefix, received `lodge could not read …` |
| C1, draft unreadable record | `ts/src/app/state.ts:101` | Same mutation, same run | Expected full prefix, received `lodge could not read …` |
| C1, spec unreadable area | `ts/src/app/state.ts:101` | Same mutation, same run | Expected full prefix, received `lodge could not read …` |
| C1, draft unreadable area | `ts/src/app/state.ts:101` | Same mutation, same run | Expected full prefix, received `lodge could not read …` |
| C2, by U+001C, where null | `ts/src/app/threads.ts:47` | Original `!by.trim()` | Expected non-empty-role error, received U+001C header error |
| C2, by author, where U+0085 | `ts/src/app/threads.ts:52` | Original `!where.trim()` | Expected needs-where error, received U+0085 header error |
| C2, by U+FEFF, where null | `ts/src/app/threads.ts:47` | Original `!by.trim()` | Expected publication, received non-empty-role error |
| C3, missing file | `ts/src/app/state.ts:99` | Replace `new NotFound` with `new LodgeError` | Expected NotFound, received LodgeError |
| P1, computed template key | `ts/tests/structure/calls.ts:103` | Original `ts.isStringLiteral(name.expression)` | Expected refusal, received false |

C1 command: `cd ts && bun test tests/app/reads-checks.test.ts -t not_found_names`, 0 pass, 4 fail.
C2 command: `cd ts && bun test tests/app/message-space.test.ts`, 0 pass, 3 fail.
C3 command: `cd ts && bun test tests/app/reads-checks.test.ts -t not_found_does_not`, 0 pass, 1 fail.
P1 command: `cd ts && bun test tests/structure/core-rules.test.ts`, 35 pass, 1 fail.

## Verification

`uv run --frozen --quiet lodge waiting`: nothing waiting for an agent or the author.
`cd ts && bun test tests/app tests/structure`: 302 pass, 0 fail after the validation and structure fixes.
Biome formatted the changed TypeScript files, and `tsc --noEmit -p .` passed after the interface changes.
Final `sh scripts/check-ts.sh`: exit 0, 1022 pass, 0 fail across 72 files; formatting, types, dependency rules, and knip passed.
All changed modules remain below 300 lines.
No test cannot hold in TypeScript, and no concerns remain.
Earlier briefs, reports, and reviews are unchanged.
