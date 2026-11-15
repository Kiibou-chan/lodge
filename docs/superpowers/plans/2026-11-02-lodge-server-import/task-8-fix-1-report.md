# Task 8 fix round 1 report

All six review items are addressed.

## Changes

- `ts/tests/api/export-target.test.ts`: observe `exporters.written` in `bad_target_is_usage`, preventing any real export while retaining the 400 response, exact usage message, and empty-target assertions.
- `ts/tests/api/import.test.ts`: test an omitted `settingsRev` against an older checkout-layout revision while HEAD has empty import sources, test both non-absolute repository cases before any read, and use the shared session cookie.
- `ts/src/api/moving.ts`: reject non-absolute import repositories with the requested usage sentence before reading, and remove both outer field checks duplicated by `person.ts`, retaining the nested target field check and the existing validation order.
- `ts/tests/api/person.test.ts`: add both operations to the agent-token refusal table and check each operation's unauthenticated 401 and wrong-Origin 403 responses, including the generic error bodies.
- `ts/tests/api/world.ts`: export `SESSION_COOKIE`, derived from the same synthetic secret used to start the session, for the world's requests and tests.
- `ts/src/main.ts`: report startup failure as `lodge: starting exports failed: <error>` with a trailing newline through the same stderr logger supplied as `ApiOptions.log`, without inventing a project name.
- `ts/src/api/options.ts`: merge the two `#app` imports.

## Test-first evidence

Line handles refer to the final files.
Every mutation below was restored immediately after its probe.

| Test | file:line | First failure or mutation |
|---|---|---|
| `bad_target_is_usage` | `ts/tests/api/export-target.test.ts:39` | Replaced `exportTargetProblem(target)` with `null`; exit 1, notification assertion expected `[]`, received `["moved"]`, completing in 270 ms without hanging. |
| `omitted_settings_revision_uses_the_older_store_revision` | `ts/tests/api/import.test.ts:159` | Changed the `settingsRev` default from `rev` to `"HEAD"`; exit 1, expected status 200, received 422. |
| `repository_must_be_absolute`, both cases | `ts/tests/api/import.test.ts:171` | Before implementation, both `""` and `"relative/dir"` failed with expected reads 0, received 1. |
| `person_operations_refuse_an_agent_token`, both added cases | `ts/tests/api/person.test.ts:41` | Exempted both operations from the non-person guard; exit 1, both expected 403, received 400. |
| `moving_operations_require_a_session_and_origin`, unauthenticated cases | `ts/tests/api/person.test.ts:151` | Changed the generic missing-credentials refusal from unauthorised to forbidden; exit 1, both expected 401, received 403. |
| `moving_operations_require_a_session_and_origin`, wrong-Origin cases | `ts/tests/api/person.test.ts:151` | Disabled the Origin guard; exit 1, both expected 403, received 400. |

An initial unauthenticated probe bypassed only the early missing-credentials guard for these operations and still passed because the later authentication path returns the same generic refusal.
The subsequent mutation above changed that refusal and failed both cases.
The existing `server_without_moving_refuses` cases retain their assertions, now using the shared cookie, and pass in the focused suite.
The import consolidation, duplicate-check removal, and startup logging sentence were reviewed directly, as the plan requires for `main.ts` composition.
No test imports `main.ts`.

## Commands and results

- `uv run --frozen --quiet lodge waiting`: nothing waiting for an agent or the author.
- `cd ts && bun test tests/api/import.test.ts tests/api/person.test.ts tests/api/export-target.test.ts`, before the repository validation: 50 pass, 2 fail, 169 assertions.
- Mutation probes used `cd ts && bun test <test-file> -t <test-name>`: target validation 1 fail; settings default 1 fail; agent guard 8 pass and 2 fail; missing-credentials refusal 2 fail; Origin guard 2 fail.
- `cd ts && bunx --no-install biome check --write src/api/moving.ts src/api/options.ts src/main.ts tests/api/import.test.ts tests/api/export-target.test.ts tests/api/person.test.ts tests/api/world.ts`: checked seven files, fixed formatting in three, and reported four informational diagnostics.
- Focused suite after implementation: 52 pass, 0 fail, 173 assertions.
- First `sh scripts/check-ts.sh`: exit 2 because the new test accessed a property on `Response.json()`'s `unknown` result; corrected it to the existing `response.text().then(JSON.parse)` convention.
- Final `sh scripts/check-ts.sh`: exit 0; 2,052 pass, 0 fail, 7,111 assertions, 185 test files; no dependency violations.
- `git diff --check`: exit 0.

## Deviations and concerns

None.
The startup sentence is the explicit change requested by this fix brief to the plan's earlier project-style failure line.
The accepted test-world composition remains in place.
