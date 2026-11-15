# Task 10, fix round 1

Changes are limited to I-1, the difference diagnostics, and the missing Bun guard.

- `ts/scripts/round-trip.ts`: exported `comparisonExitCode`, used it for the script's final exit, and changed difference details to the first differing source and export lines, with an explicit end-of-file marker when needed.
  A lone path now says `missing from the export` or `extra in the export`.
- `ts/tests/api/round-trip-script.test.ts`: asserted the exit decision in every comparison-table row, updated the diagnostic expectations, added shorter and longer exports, and added subprocess cases for bad argument counts, a refused import, a repository without `lodge/`, and missing Bun.
  All repositories and the restricted shell PATH use cleaned temporary folders with isolated git settings.
- `scripts/round-trip.sh`: added the same `command -v bun` guard as `scripts/check-ts.sh`, before creating a temporary folder or cloning.
- This report records the changes and verification.

`plan_4_changed_rows_keep_every_python_test_name` and both mapping forms are unchanged, as requested.

## Test-first evidence

Handles below refer to `ts/tests/api/round-trip-script.test.ts`.
Each mutation was restored before continuing.

| Test | file:line | First failure or mutation rejected |
|---|---|---|
| Comparison table: `equal_bytes`, `mapped_decision`, `mapped_reply`, and `binary_bytes` | `ts/tests/api/round-trip-script.test.ts:14` | Initially the missing `comparisonExitCode` export failed module loading; changing its clean exit from 0 to 1 then gave 4 failures, expected 0, received 1. |
| Comparison table: `body_change`, `body_author_is_not_metadata`, and `attachment_is_not_metadata` | `ts/tests/api/round-trip-script.test.ts:18` | Changing `differences.length ? 1 : 0` to `? 0 : 0` gave 3 failures before the diagnostic changes; the old numeric-line diagnostics also failed the new text expectations. |
| Comparison table: `shorter_export` and `longer_export` | `ts/tests/api/round-trip-script.test.ts:45` | Both first failed against the old numeric-line diagnostics; the repeated `? 0 : 0` mutation then failed all 5 differing table rows, including these two. |
| `comparison_reports_missing_and_extra_paths` | `ts/tests/api/round-trip-script.test.ts:75` | The old `{ line: 1 }` results failed both explicit side expectations. |
| `script_rejects_wrong_argument_count`, all three cases | `ts/tests/api/round-trip-script.test.ts:118` | Changing the usage branch's `process.exitCode = 1` to 0 gave 3 failures, expected 1, received 0. |
| `script_exits_one_when_import_is_refused` | `ts/tests/api/round-trip-script.test.ts:130` | Changing the return after the import refusal diagnostic from 1 to 0 gave 1 failure, expected 1, received 0. |
| `script_exits_one_without_a_lodge_folder` | `ts/tests/api/round-trip-script.test.ts:144` | Changing the catch branch's `process.exitCode = 1` to 0 gave 1 failure, expected 1, received 0. |
| `shell_reports_missing_bun_before_cloning` | `ts/tests/api/round-trip-script.test.ts:153` | Without the guard, the restricted PATH produced exit 127 rather than the required exit 2 and clear message. |

The two existing `script_round_trip` layout cases remain unchanged and pass.

## Commands and results

- `uv run --frozen --quiet lodge waiting`: nothing waiting for either agent or author.
- `git branch --show-current`: `server-import-roundtrip`.
- `bun test tests/api/round-trip-script.test.ts` in `ts/`: first failed on the missing export, then showed the guard failure, then showed 7 diagnostic and guard failures before their fixes.
- Mutation probes used a temporary Python harness to change one expression at a time, run `bun test tests/api/round-trip-script.test.ts --test-name-pattern PATTERN` in `ts/`, assert exit 1, and restore the original file in `finally`.
  Patterns were `comparison `, `script_rejects_wrong_argument_count`, `script_exits_one_when_import_is_refused`, and `script_exits_one_without_a_lodge_folder`.
  Final comparison probes gave 5 failures for always-zero and 4 failures for always-one.
- `bunx --no-install biome check --write --error-on-warnings scripts/round-trip.ts tests/api/round-trip-script.test.ts` in `ts/`: checked 2 files, fixed 1 file.
- `bun test tests/api/round-trip-script.test.ts tests/api/round-trip.test.ts tests/parity.test.ts` in `ts/`: 36 pass, 0 fail, 597 assertions.
- `git diff --check`: no output.
- `git status --short lodge/`: no output.
- Final gate: `sh scripts/check-ts.sh`: exit 0; 2,137 pass, 0 fail, 7,364 assertions across 191 test files; dependency-cruiser reported no dependency violations.
- Delivery: staged the four changed files by explicit path, committed with the required identity and Codex trailer, and pushed with `git push origin server-import-roundtrip`.

The coordinator confirmed that this report belongs beside the original Task 10 report.
There are no other deviations, unresolved questions, or concerns.
