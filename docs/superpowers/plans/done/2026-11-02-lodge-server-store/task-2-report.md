# Task 2 report

Implemented the Task 2 app foundation on `server-store-a`.

## Changes per file

| File | Change |
| --- | --- |
| `ts/src/app/errors.ts` | Ported the error hierarchy, class names, exit codes, and settings-error translation, rethrowing unrelated errors. |
| `ts/src/app/ports.ts` | Added asynchronous store methods, clock and entropy ports, outcomes, default builders, actors, roles, and projects. |
| `ts/src/app/results.ts` | Ported all Task 2 result interfaces and their default builders, with readonly fields and collections. |
| `ts/src/app/time.ts` | Added second and minute formatting using explicit offsets and UTC date methods. |
| `ts/src/app/index.ts` | Exported the Task 2 app front door. |
| `ts/tests/app/fakes.ts` | Carried MemoryStore, FixedClock, CountingIds, and START, adding attachment enumeration and asynchronous port methods. |
| `ts/tests/app/time.test.ts` | Added the five specified time tests. |
| `ts/tests/app/ports.test.ts` | Added actor text and all seven default-builder checks in the specified two tests. |
| `ts/tests/app/errors.test.ts` | Added error inheritance, names, exit codes, and bad-settings checks. |
| `ts/package.json` | Added the `#app` import alias without dependencies. |
| `ts/knip.json` | Added the fakes entry for exports first consumed in Task 3. |
| `ts/tests/parity.json` | Marked `tests/app/fakes.py` ported with task `["2"]`. |

## First failing evidence

All three test files were written before implementation and run together with `cd ts && bun test tests/app`.
Each file failed to load with `error: Cannot find package '#app'`, giving `0 pass`, `3 fail`, and `3 errors`.
A missing module counts as a failure under the brief.

| Test | First failure |
| --- | --- |
| `stamp_keeps_the_offset` | Missing `#app` in time.test.ts. |
| `stamp_drops_the_fraction` | Missing `#app` in time.test.ts. |
| `negative_and_zero_offsets` | Missing `#app` in time.test.ts. |
| `minute_is_local_to_the_offset` | Missing `#app` in time.test.ts. |
| `minute_crosses_midnight` | Missing `#app` in time.test.ts. |
| `actor_text_names_the_person_or_the_role` | Missing `#app` in ports.test.ts. |
| `default_filling_functions_fill_python_defaults` | Missing `#app` in ports.test.ts. |
| `exit_codes_follow_lodge_0_2` | Missing `#app` in errors.test.ts. |
| `core_settings_reports_a_bad_table_as_a_lodge_error` | Missing `#app` in errors.test.ts. |

The carried `tests/app/fakes.py` contains helpers, not test functions, so there are no carried test titles or mutations for it.
No tests were omitted or changed because they cannot hold in TypeScript.
Existing tests were left unchanged.

## Commands and results

| Command | Result or last lines |
| --- | --- |
| `cat .../task-2-brief.md` | Read the brief first, as requested by the user. |
| `cat CLAUDE.md` and source/configuration inspection with `cat`, `head`, and `rg` | Read Python ports, results, errors, fakes, TypeScript builders, settings, exports, and configuration. |
| `uv run --frozen --quiet lodge waiting` | Both waiting lists: `nothing`. |
| `git status --short` and `git branch --show-current` | Branch `server-store-a`; existing untracked task log left untouched. |
| `cd ts && bun test tests/app` before implementation | `Ran 3 tests across 3 files. [13.00ms]`, with the missing-module failures above. |
| `cd ts && bunx biome check --write src/app tests/app package.json knip.json && bun test tests/app` | Fixed formatting in eight files; `9 pass`, `0 fail`, `36 expect() calls`. |
| `sh scripts/check-ts.sh` first run | TypeScript caught the test's wrong `checkResult` call: `Expected 2 arguments, but got 1`. |
| `sh scripts/check-ts.sh` after correcting the test to `checkResult([], [])` | No dependency violations; `941 pass`, `0 fail`, `2326 expect() calls`. |
| `sh scripts/check-ts.sh` immediately after parity update | Biome rejected JSON array formatting; corrected with `cd ts && bunx biome check --write tests/parity.json` (`Fixed 1 file`). |
| Final `sh scripts/check-ts.sh`, after formatting and this report | Exit 0; `941 pass`, `0 fail`; expectation totals varied between 2326 and 2328 across full runs. |

No packages were installed or added.
No Python implementation or tests were edited.
The coordinator's whole gate, merge, and ledger update remain with the coordinator.

## Concerns and interpretation

The brief's opening explicitly authorises committing and pushing this worktree with a Codex trailer, overriding the repeated sandbox-era builder restriction and the general Claude trailer.
The report and implementation are included in that commit with explicit paths.
There are no implementation concerns.
