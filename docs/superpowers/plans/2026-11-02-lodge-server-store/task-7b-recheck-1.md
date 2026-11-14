# Task 7b recheck 1

Rechecker: `rechecker` agent, fix diff `7809f42..8c75e13`, run in a detached scratch worktree at 8c75e13 (since removed).
`sh scripts/check-ts.sh` there: Biome, `tsc`, dependency-cruiser (156 modules), knip, and `bun test` 1045 pass, 0 fail.

## Findings

- C-1: answered. `events.message` is a `blob` (`ts/src/store/schema.ts:13,43`), written through `encodeUtf8` (`ts/src/store/events.ts:27`); the `Store` port keeps `message: string`; `event_message_bytes_survive_exactly` (`ts/tests/store/sqlite-store.test.ts:112-121`) covers `"t\uDC80 tail"` and a leading U+FEFF. Mutation: passing the string through unencoded fails 3 store tests.
- C-2: answered. `ts/tests/store/projects.test.ts:33-46` uses `other` for the person cases and asserts the plan's messages. M1 (delete the owner check in `create`) now fails 2 tests.
- C-3: answered. One loop per phase (`ts/src/store/sqlite-store.ts:56-87`); `refusals_follow_phases_across_all_paths` (`ts/tests/store/sqlite-store-refusals.test.ts:82-119`) pins the order.
- C-4: answered. The encoding refusal asserts `lodge/a: cannot encode lone surrogate '\ud800'` (`sqlite-store-refusals.test.ts:38`). M5 (replace the message with `"x"`) now fails 1 test.
- P-1: answered. `headOf` and `touchHead` in `ts/src/store/read-tree.ts:5-25`, used by `readTree`, `members`, `addMember`, `publish`.
- P-2: answered. `attachmentTexts` filters in SQL by a `path` range (`ts/src/store/sqlite-store.ts:33-34`).
- P-3: answered. `PROJECT_NAME` and `PERSON_NAME` constants passed to `checkName` (`ts/src/store/projects.ts:15-22`).
- P-4: answered. The astral path is asserted after the loop body without a branch (`sqlite-store-refusals.test.ts:41-54`).
- D-2: answered. `ts/tests/store/write-first.test.ts` records the first statement of `create`, `addMember`, and `publish` through a Kysely plugin. M6 (a `members` select before the write in `addMember`) now fails 1 test.
- D-1, m-2: deliberately not fixed, as the brief says.

## New problems

None Blocking or Important.
The test and source diff were compared: no assertion was weakened (the `LodgeError` import was dropped only because the message assertions replace it).
Nothing else in `ts/src` reads `events.message`, so the type change reaches no other consumer.

Verdict: 0 Blocking, 0 Important, 0 Minor
