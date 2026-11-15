# Task 5, fix round 1 report

Added nine behavioural cases in three API test files.
All nine were written after the production code existed, before applying the mutations below.
Each mutation was applied separately, its named test was observed failing, and the original source was restored in a `finally` block before the next mutation.
No real defect was found, and no production code was changed.
The earlier report's missing-module failures and broad throw mutation remain thin evidence, as review I-3 states; this report supplies targeted evidence for the new cases only.

## Tests and mutation evidence

| Item | Test with file:line | Mutation killed | Observed result |
|---|---|---|---|
| I-1 | `json_content_type_is_accepted application/json; charset=utf-8`, `ts/tests/api/handler.test.ts:49` | Removed `split(";")[0]` from the content-type check, comparing the whole trimmed header. | Expected 200, received 400; 9 pass, 1 fail. |
| I-1, folded M-2 | `json_content_type_is_accepted Application/JSON`, `ts/tests/api/handler.test.ts:49` | Removed `.toLowerCase()` from the content-type check. | Expected 200, received 400; 9 pass, 1 fail. |
| I-2 | `arguments_are_checked`, fractional limit, `ts/tests/api/operations.test.ts:31` | Removed `!Number.isInteger(v)` from `Args.limit`. | Expected 400, received 200; 40 pass, 1 fail. |
| I-2 | `arguments_are_checked`, invalid kind, `ts/tests/api/operations.test.ts:33` | Replaced the `filters.kind` value-check condition with `false`. | Expected 400, received 200; 40 pass, 1 fail. |
| I-2 | `arguments_are_checked`, invalid scope, `ts/tests/api/operations.test.ts:34` | Replaced the `filters.scope` value-check condition with `false`. | Expected 400, received 200; 40 pass, 1 fail. |
| I-2 | `arguments_are_checked`, invalid status, `ts/tests/api/operations.test.ts:35` | Replaced the `filters.status` value-check condition with `false`. | Expected 400, received 200; 40 pass, 1 fail. |
| I-2 | `arguments_are_checked`, three-element draft pair, `ts/tests/api/operations.test.ts:47` | Removed `p.length === 2` from `Args.pairs`. | Status remained 400, but the expected pair-shape sentence was replaced by a draft-header error; 40 pass, 1 fail. |
| I-2 | `arguments_are_checked`, non-string draft text, `ts/tests/api/operations.test.ts:48` | Replaced the pair element string check with `true`. | Expected 400, received 500; 40 pass, 1 fail. |
| Requested minor | `other_authorization_scheme_is_unauthorised`, `ts/tests/api/bearer.test.ts:15` | Replaced the literal `Bearer` scheme in the regex with `\S+`, accepting `Basic` with a valid token. | Expected 401, received 200; 7 pass, 1 fail. |

Every invalid-argument row also asserts the complete `usage` response with the plan's sentence.
The scheme test asserts the complete `unauthorised` response and uses a valid secret so that scheme validation determines the result.
Other parked minors remain untouched.

## Validation

- `uv run --frozen --quiet lodge waiting`: nothing waiting for an agent or the author.
- `cd ts && bunx biome check --write tests/api/handler.test.ts tests/api/operations.test.ts tests/api/bearer.test.ts`: checked three files, formatted one.
- `cd ts && bun test tests/api`: 94 pass, 0 fail, 222 assertions, across seven files.
- Nine separate mutation runs against the relevant test file: each exited 1 with exactly one failing case, as listed above.
- `sh scripts/check-ts.sh`: exit 0; 1489 pass, 2 todo, 0 fail, 3814 assertions, across 119 files.
- `git diff -- ts/src/api`: empty after restoration.

The gate passed with all existing tests, including structure checks.
No dependency was added, no test opened a socket, and no historical brief, report, or review was edited.
The existing final-output text files were left unstaged.
No deviations or unresolved concerns remain within this fix brief's scope.
