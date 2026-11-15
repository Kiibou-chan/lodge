# Task 10 report

Implemented the round-trip proof and scratch-clone scripts on `server-import-roundtrip`.
No dependency was added, no historical brief or report was changed, and no export targeted this repository.

## Files changed

| File | Change |
|---|---|
| `ts/tests/api/round-trip.test.ts` | Exercises the handler through `world()` for checkout and branch layouts, with explicit branch settings, an isolated bare export target, the `ada` mapping, every original path and byte, both `.gitkeep` files, and the binary attachment `ff fe`.
| `ts/tests/api/round-trip.test.ts` | Confirms that notifying the exporter again leaves the branch tip unchanged.
| `ts/scripts/round-trip.ts` | Reads a revision and optional settings revision, imports once into an in-memory SQLite project owned by `ana`, exports once into a temporary bare repository, compares every path, prints counts and first differing lines, and exits unsuccessfully on other differences.
| `ts/scripts/round-trip.ts` | Exposes `compareStores` for direct tests, with decision mapping confined to front matter and thread mapping confined to message metadata headings.
| `scripts/round-trip.sh` | Clones with `git clone --no-local --quiet` into `mktemp -d`, runs the TypeScript script against the clone's `HEAD`, and removes the scratch folder on exit.
| `ts/tests/api/round-trip-script.test.ts` | Adds seven comparison cases, a missing-and-extra-path case, and two subprocess integration cases using synthetic stores and `Bun.spawnSync`.
| `ts/tests/parity.test.ts` | Includes plan 4 changed rows in held rows and file existence checks, adds a regression for held plan 4 rows, and checks their Python names with the hook row restricted to `post-tool-use.test.ts` alone.
| `ts/tests/hook/post-tool-use.test.ts` | Removes the colon between the Python name and placeholder in two existing parametrised titles, preserving every case and assertion.
| `docs/superpowers/plans/2026-11-02-lodge-server-import/task-10-report.md` | Records implementation, failing evidence, validation, deviations, and remaining coordinator work.

The script's `compareStores` export is read by `round-trip-script.test.ts`.
Existing knip entries already include `scripts/*.ts`, and the TypeScript and dependency checks already include `scripts`, so no configuration change was needed.

## Test-first evidence

All temporary mutations were restored before final validation.
Line handles below identify the finished test or the mutated implementation.
The missing script module was observed before its implementation was created, so it prevented discovery of every script test listed below.

| Test or cases | file:line | First failing output or mutation detected |
|---|---|---|
| `made_up_store_survives_import_and_export checkout` | `ts/tests/api/round-trip.test.ts:33` | Appended a newline to each exported record in `ts/src/app/exporting.ts:37`; byte equality failed with an extra `10` in the received byte array.
| `made_up_store_survives_import_and_export branch` | `ts/tests/api/round-trip.test.ts:33` | The same newline mutation failed byte equality for the branch layout too.
| `export_of_an_export_is_unchanged` | `ts/tests/api/round-trip.test.ts:63` | Replaced the unchanged-tree condition in `ts/src/git/export.ts:108` with `false`; expected and received branch tips differed.
| `comparison equal_bytes` | `ts/tests/api/round-trip-script.test.ts:13` | `Cannot find module '../../scripts/round-trip.ts'`.
| `comparison mapped_decision` | `ts/tests/api/round-trip-script.test.ts:14` | The same missing-module failure before implementation.
| `comparison mapped_reply` | `ts/tests/api/round-trip-script.test.ts:15` | The same missing-module failure before implementation.
| `comparison body_change` | `ts/tests/api/round-trip-script.test.ts:16` | The same missing-module failure before implementation.
| `comparison body_author_is_not_metadata` | `ts/tests/api/round-trip-script.test.ts:25` | The same missing-module failure before implementation.
| `comparison attachment_is_not_metadata` | `ts/tests/api/round-trip-script.test.ts:34` | The same missing-module failure before implementation.
| `comparison binary_bytes` | `ts/tests/api/round-trip-script.test.ts:43` | The same missing-module failure before implementation.
| `comparison_reports_missing_and_extra_paths` | `ts/tests/api/round-trip-script.test.ts:53` | The same missing-module failure before implementation.
| `script_round_trip checkout` | `ts/tests/api/round-trip-script.test.ts:67` | The same missing-module failure before implementation.
| `script_round_trip branch` | `ts/tests/api/round-trip-script.test.ts:67` | The same missing-module failure before implementation.
| `a_changed_plan_4_file_is_held` | `ts/tests/parity.test.ts:105` | `Expected: true`, `Received: false` with the original `[2, 3]` default.
| `plan_4_changed_rows_keep_every_python_test_name` | `ts/tests/parity.test.ts:108` | Expected `[]`, received `bad_payload_exit_0_silent` and `bad_settings_are_one_sentence` before correcting the hook titles.
| Extended `ported_files_exist` | `ts/tests/parity.test.ts:42` | Temporarily named a nonexistent TypeScript file in the plan 4 hand-edits row; `Expected: true`, `Received: false`.
| Extended `ported_files_keep_every_python_test_name` | `ts/tests/parity.test.ts:46` | Restored the colon in the bad-payload hook title temporarily; the missing-name list contained `bad_payload_exit_0_silent`.
| Extended `ported_files_hold_no_todo` | `ts/tests/parity.test.ts:49` | Added a temporary `test.todo` to the plan 4 hook file; expected `[]`, received `synthetic_missing_behaviour`.
| Existing bad-payload and bad-settings hook cases | `ts/tests/hook/post-tool-use.test.ts:79` | Cases and assertions are unchanged; the parity failure above proves why the title-only correction was required.

The first combined run after implementing the script found two mistakes in the new comparison fixtures.
The body-change fixture initially left the author unmapped and expected a line one too high, while the body-metadata fixture also expected a line one too high.
The fixtures now include the expected owner mapping and assert lines 6 and 7 respectively.
The initial type check also found readonly expected arrays and an untyped JSON response; the tests now spread the expected differences and use the existing response parsing convention.

## Commands and outcomes

Commands ran from the repository root unless prefixed with `cd ts`.
Repeated inspection commands are grouped by purpose.

| Command | Last relevant output and exit |
|---|---|
| `cat CLAUDE.md`, plan section reads with `sed`, and source/configuration reads with `cat`, `rg`, and `nl -ba` | Read the required guidance, requirements, merged names, parity rows, and script configuration.
| `uv run --frozen --quiet lodge waiting` | `nothing` for both agent and author queues; exit 0.
| `git status --short` and `git branch --show-current` | Initially clean on `server-import-roundtrip`; exit 0.
| Early exploratory `cat` calls for guessed implementation filenames | Reported missing files; the implementations were then located as `importing.ts` and `exporting.ts`.
| `cd ts && bun test tests/parity.test.ts` before implementation | `13 pass`, `2 fail`, `498 expect() calls`; exit 1.
| `cd ts && bun test tests/api/round-trip.test.ts -t made_up_store_survives_import_and_export` with newline mutation | `0 pass`, `2 fail`, `18 expect() calls`; exit 1.
| `cd ts && bun test tests/api/round-trip.test.ts -t export_of_an_export_is_unchanged` with unchanged-tree mutation | `0 pass`, `1 fail`, `6 expect() calls`; exit 1.
| `cd ts && bun test tests/api/round-trip-script.test.ts` before script implementation | `0 pass`, `1 fail`, `1 error`, missing module; exit 1.
| `cd ts && bun test tests/api/round-trip.test.ts tests/api/round-trip-script.test.ts tests/parity.test.ts` on the first script implementation | `26 pass`, `2 fail`, `569 expect() calls`; exit 1 from the two fixture mistakes described above.
| `cd ts && bunx --no-install biome check --write --error-on-warnings scripts/round-trip.ts tests/api/round-trip.test.ts tests/api/round-trip-script.test.ts tests/parity.test.ts tests/hook/post-tool-use.test.ts` | Fixed formatting; two informational template suggestions were subsequently resolved; exit 0.
| `cd ts && bun test tests/api/round-trip.test.ts tests/api/round-trip-script.test.ts tests/parity.test.ts` after fixture corrections | `28 pass`, `0 fail`, `569 expect() calls`; exit 0.
| `sh scripts/round-trip.sh` | `Other differences: 0`; exit 0, with counts below.
| Initial `cd ts && bunx --no-install tsc --noEmit -p .` | TS2769 for readonly expectations and TS2571 for unknown JSON; exit 2, corrected in tests.
| `cd ts && bunx --no-install biome check --write --error-on-warnings scripts tests/api/round-trip.test.ts tests/api/round-trip-script.test.ts tests/parity.test.ts` | `Checked 7 files`, `No fixes applied`; exit 0.
| `cd ts && bunx --no-install tsc --noEmit -p .` after corrections | No output; exit 0.
| `cd ts && bunx --no-install depcruise src tests scripts --config .dependency-cruiser.cjs` | No dependency violations, 364 modules and 1,384 dependencies; exit 0.
| `cd ts && bunx --no-install knip` | No output; exit 0.
| `cd ts && bun test tests/structure` | `225 pass`, `0 fail`, `291 expect() calls`; exit 0.
| `cd ts && bun test tests/parity.test.ts -t ported_files_exist` with missing-path mutation | `0 pass`, `1 fail`, `80 expect() calls`; exit 1.
| `cd ts && bun test tests/parity.test.ts -t 'ported_files_keep_every_python_test_name\|ported_files_hold_no_todo'` with title and TODO mutations | `0 pass`, `2 fail`, `184 expect() calls`; exit 1.
| `git diff --check` | No output; exit 0.
| `git diff -- ts/src` | No output after restoring production mutations; exit 0.
| `git status --short lodge/` | No output after the scratch-clone run and mutation checks; exit 0.
| `sh scripts/check-ts.sh` | `2129 pass`, `0 fail`, `7336 expect() calls`; exit 0.

The optional builder run on a scratch clone printed:

```text
Files compared: 431
Files equal: 379
Files differing only in decided_by or a message's by: 52
Other differences: 0
```

The synthetic script integration cases each print 11 compared, seven equal, four differing only in author metadata, and zero other differences.

## Deviations, rulings, and uncertainties

Added `ts/tests/api/round-trip-script.test.ts` beyond the plan's file list so the script's comparison logic and both command-line layouts have direct failing-first coverage.
No configuration changes were needed because scripts were already included.
The two hook test title corrections are outside the original file list and were explicitly authorised through `coord.ask_coordinator` after the required parity test failed.
The coordinator ruled to correct the titles, retain all cases and assertions, and leave `parity-names.ts` alone.
The question initially described the titles incorrectly as concatenated expressions; inspection showed literal titles with a colon, and the implemented correction removes only that colon.
No other Python names were lost, including in the plan 4 repository-helper row, and no parity row was weakened or changed.

Used the brief's merged names and full-access commit instructions in place of the plan's sandbox-era names and coordinator-only git instructions.
Ran the single optional builder scratch-clone proof allowed by the brief.
Coordinator Steps 3 and 4 remain for the coordinator, including its own scratch-clone run and the whole Python gate `sh scripts/check.sh`.
No further unresolved implementation questions remain.

## Final gate

`sh scripts/check-ts.sh` exited 0.
Biome checked 347 files without changing them, reporting 43 informational diagnostics in existing code.
TypeScript, dependency-cruiser, knip, and the complete Bun suite passed, including the structure tests.
The final lines were:

```text
2129 pass
0 fail
7336 expect() calls
Ran 2129 tests across 191 files. [10.92s]
```

The delivery commands stage and commit the seven paths in the file table explicitly, using the brief's specified identity and `Co-Authored-By: Codex <noreply@openai.com>` trailer, then run `git push origin server-import-roundtrip`.
No command runs against `main`.
