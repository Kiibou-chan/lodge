# Task 5, recheck 1

Scope: `git diff f97beb2 81964d1`; no production file changed (`git diff --stat f97beb2 81964d1 -- ts/src` is empty).
Each mutation was applied in a detached scratch worktree at 81964d1 and the named test file run with `bun test`.
Every mutation applied (checked by `cmp`) and the source was restored each time.

## Findings

| Finding | Verdict | Handle |
|---|---|---|
| I-1 charset parameter | Resolved | Test `ts/tests/api/handler.test.ts:49`. Removing `?.split(";")[0]` at `ts/src/api/http.ts:25`: 400 instead of 200, 9 pass, 1 fail. Removing `.toLowerCase()`: the `Application/JSON` case fails, 9 pass, 1 fail. |
| I-2 `filters.kind` | Resolved | `ts/tests/api/operations.test.ts:33`. Condition at `ts/src/api/operations.ts:46` replaced by `false`: 200 instead of 400, 40 pass, 1 fail. |
| I-2 `filters.scope` | Resolved | `operations.test.ts:34`. Condition at `operations.ts:48` replaced by `false`: fails the same way. |
| I-2 `filters.status` | Resolved | `operations.test.ts:35`. Condition at `operations.ts:51` replaced by `false`: fails the same way. |
| I-2 non-integer `limit` | Resolved | `operations.test.ts:31`. `!Number.isInteger(v)` removed at `ts/src/api/args.ts:35`: 200 instead of 400. |
| I-2 pair shape | Resolved | `operations.test.ts:47` kills removal of `p.length === 2` (the usage sentence changes to a draft-header error, and the test asserts the full body); `operations.test.ts:48` kills replacing the string check with `true` (500 instead of 400). |
| Authorization scheme | Resolved | `ts/tests/api/bearer.test.ts:15`. Regex at `ts/src/api/auth.ts:12` changed to `^\S+ (\S+)$`: 200 instead of 401, 7 pass, 1 fail. |
| I-3 provenance note | Resolved | `task-5-fix-1-report.md` lines 3 to 4 say plainly that all nine cases were written after the production code, and that the earlier evidence stays thin. |

Notes on the evidence:
- The pair-shape three-element mutation fails only through the message assertion, not the status; this is adequate because the test asserts the whole `usage` body.
- The report's "nine" cases: counting the table, rows give 10 distinct cases (two content-type values, five value checks plus limit, two pair cases, scheme).
This is a counting slip in prose, not a coverage gap.

## New problems

Blocking: none.
Important: none.
Minor: none beyond the count slip above.

Checks: tests only, no production change, no new dependency, no real network.
`biome check tests/api`: clean.
The largest touched test file is 105 lines, so the 300-line limit holds.
Fixtures are synthetic.
The only untracked files in lane C are the pre-existing `*-codex-final.txt` outputs.
The scratch worktree was removed.
