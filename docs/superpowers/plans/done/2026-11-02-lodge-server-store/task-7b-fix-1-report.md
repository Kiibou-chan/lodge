# Task 7b fix round 1 report

Implemented C-1, C-2, C-3, C-4, P-1, P-2, P-3, P-4, and D-2.
D-1 remains as ruled, and m-2 remains for Task 8.
Read `CLAUDE.md`, the review, the brief, and coordinator decision d-gxbbnf through `lodge show --reasoning` in the main worktree.
`lodge waiting` reported nothing waiting for an agent or the author.

## Changes

- `ts/src/store/schema.ts`: changed `MIGRATIONS[0]` in place to `message blob`, and typed event messages as nullable bytes, per d-gxbbnf.
- `ts/src/store/events.ts`: encodes non-null event messages with `encodeUtf8`; the store port and event input keep strings.
- `ts/src/store/read-tree.ts`: shared `headOf` and `touchHead`, preserving missing-project errors and optional compare-and-set revision matching.
- `ts/src/store/projects.ts`: uses the shared helpers and named pattern/noun rules rather than a boolean name-check flag.
- `ts/src/store/sqlite-store.ts`: checks all paths in successive refusal phases, uses `touchHead` as the first transaction statement, and selects attachments using SQL's case-sensitive path range.
- `ts/tests/store/projects.test.ts`: person-name cases use the absent project `other`; all name cases assert the exact noun and pattern.
- `ts/tests/store/sqlite-store.test.ts`: decodes event messages with `decodeUtf8`, and checks both escaped-byte and leading-BOM messages round-trip from byte storage.
- `ts/tests/store/sqlite-store-refusals.test.ts`: asserts the complete encoding error, removes the astral acceptance branch, and checks refusal precedence across paths with no events written.
- `ts/tests/store/write-first.test.ts`: a Kysely plugin observes each transaction's first query, requiring an insert or update on `heads` for `create`, `addMember`, and `publish`.

## Test-first evidence

The first focused run after writing regression tests had 42 pass and 4 fail.
Both message cases failed at the byte assertion, with stored values `t𰀠tail` and `lead`.
The phase test expected `notes/x is outside lodge/, which is all the store writes` but received the published-decision refusal.
The fourth failure was an initially incorrect expected surrogate diagnostic; reading the codec corrected it to `lodge/a: cannot encode lone surrogate '\ud800'` before implementation.
The next focused run had 46 pass and 3 fail, consisting only of the two message cases and the phase regression.
After implementation, all 49 focused tests passed.
The write-first, tightened name, encoding-message, and astral acceptance cases were checked against targeted mutations.

Every mutation was reverted immediately after its run.
The initial four mutation runs occurred while the three new implementation regressions still failed, so the table records both the additional targeted failures and each total.

| Run | Mutation | Targeted failing test or group | Result |
| --- | --- | --- | --- |
| Initial M1 | Delete `checkName(owner)` | Both person cases of `names_are_checked` resolved instead of rejecting | 44 pass, 5 fail |
| Initial M5 | Replace the encoding error text with `x` | `lone_surrogate_outside_the_escapes_is_refused` | 45 pass, 4 fail |
| Initial M6 | Select members before the first write in `addMember` | `transaction_writes_heads_first: addMember` saw `SelectQueryNode` | 45 pass, 4 fail |
| Initial create probe | Select members before the first write in `create` | `transaction_writes_heads_first: create` saw `SelectQueryNode` | 45 pass, 4 fail |
| Final M1 | Delete `checkName(owner, PERSON_NAME)` | Both person cases of `names_are_checked` resolved instead of rejecting | 47 pass, 2 fail |
| Final M5 | Replace the encoding error text with `x` | Expected the path and codec's surrogate message, received `x` | 48 pass, 1 fail |
| Final M6 | Select members before the first write in `addMember` | Expected `UpdateQueryNode`, received `SelectQueryNode` | 48 pass, 1 fail |
| Final create probe | Select members before the first write in `create` | Expected `InsertQueryNode`, received `SelectQueryNode` | 48 pass, 1 fail |
| Publish probe | Select members before the first write in `publish` | Expected `UpdateQueryNode`, received `SelectQueryNode` | 48 pass, 1 fail |
| Astral probe | Replace the Unicode surrogate test with a UTF-16 code-unit range | Both surrogate-refusal cases failed at their following astral acceptance assertion | 47 pass, 2 fail |

## Validation

`cd ts && bun test tests/store`: 49 pass, 0 fail, 125 assertions.
Biome formatting was applied to the changed TypeScript files.
The first full gate found one remaining formatting change; formatting that file again resolved it.
`sh scripts/check-ts.sh`: Biome clean, TypeScript clean, dependency-cruiser clean (156 modules), knip clean, 1045 pass, 0 fail, 2575 assertions across 75 files.
All touched modules are below 300 lines.
No test was omitted as impossible in TypeScript.
No new packages, earlier reports, briefs, reviews, Python files, or record files were changed.
No unresolved concerns beyond the explicitly deferred D-1 and m-2.
