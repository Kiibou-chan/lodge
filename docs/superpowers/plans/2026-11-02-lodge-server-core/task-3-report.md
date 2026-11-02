# Task 3 report

Implemented the structure rules and parity table on the current branch.
No dependency was added, and nothing was staged, committed, or pushed.

## Changes by file

- `ts/.dependency-cruiser.cjs`: Adds the allowed edges, front doors, cycles, purity, process, SQLite, file, network, and resolution rules, with source-only I/O restrictions and symlink preservation.
- `ts/package.json`: Adds `test:structure` for the task’s targeted test command, keeping all dependency versions unchanged.
- `ts/tests/structure/table.ts`: Defines PACKAGES, CORE_NPM, and MAX_LINES with the brief’s values.
- `ts/tests/structure/plant.ts`: Plants isolated trees with package aliases, compiler options, dependencies, and a node_modules symlink; cruises in process with baseDir and preserveSymlinks, and removes its temporary trees after the tests.
- `ts/tests/structure/calls.ts`: Parses source with TypeScript for purity, local-time, dynamic-code, and I/O rules; also checks sizes and package layout.
- `ts/tests/structure/imports.test.ts`: Tests forbidden edges and allowed imports, including both fs spellings, Bun modules, tests, scripts, and the composition root; shares one allowed-tree cruise between two tests.
- `ts/tests/structure/calls.test.ts`: Tests every required global and local-time name, stamp parsing, clock ports, dynamic code, and confined calls.
- `ts/tests/structure/layout.test.ts`: Tests unknown packages, missing front doors, nested folders, imports mappings, and both sides of the line limit.
- `ts/tests/structure/repository.test.ts`: Checks the actual TypeScript tree against all four checkers.
- `ts/tests/parity.json`: Transcribes all 126 parity-table rows, including individual counterpart paths, plan 1 tasks, and reasons; the seven structure rows are changed from the start, and the remaining plan 1 rows remain planned for later tasks.
- `ts/tests/parity-names.ts`: Reads Python test definitions and TypeScript test titles, detects todos, and reports missing names through the shared missingNames helper.
- `ts/tests/parity.test.ts`: Checks complete file coverage, metadata, counterpart existence, names, todos, and the name readers themselves.

No file needed splitting, and no existing test was edited.

## Test-first evidence

All required tests were written before the helper modules, configuration rules, and parity data were implemented.
The first targeted run exited 1 with `0 pass`, `5 fail`, and `5 errors`.
The brief explicitly accepts missing modules as first failures.
Every title below, including all parameter cases in its source file, was present in that run unless marked as a later regression.

### `ts/tests/parity.test.ts`

First failure: `error: Cannot find module './parity.json'` when loading this file.

- `every_python_test_file_is_in_the_table`: the initial missing-module failure above.
- `statuses_are_known`: the initial missing-module failure above.
- `changed_and_later_give_a_why`: the initial missing-module failure above.
- `planned_rows_name_a_plan`: the initial missing-module failure above.
- `ported_files_exist`: the initial missing-module failure above.
- `ported_files_keep_every_python_test_name`: the initial missing-module failure above.
- `ported_files_hold_no_todo`: the initial missing-module failure above.
- `a_ported_file_losing_a_name_fails`: the initial missing-module failure above.
- `a`: the initial missing-module failure above.
- `parity_names_read_both_languages`: the initial missing-module failure above.
- `c %p`: the initial missing-module failure above.
- `no`: the initial missing-module failure above.
- `parity_names_ignore_non_test_calls`: added later, failed because the received list included `not a title` and `not a test`, with `9 pass / 1 fail`, before restricting title recognition to direct tests, todos, and invoked each calls.
- `real %p`: the initial missing-module failure above.
### `ts/tests/structure/calls.test.ts`

First failure: `error: Cannot find module './plant.ts'` when loading this file.

- `core_disallowed_global %p %p`: the initial missing-module failure above.
- `local_time_in_core_and_app %p %p`: the initial missing-module failure above.
- `core_may_not_use_date %p %p`: the initial missing-module failure above.
- `core_names_the_clock_on_any_receiver %p %p`: the initial missing-module failure above.
- `dynamic_code_anywhere %p %p`: the initial missing-module failure above.
- `spawn_outside_git %p %p`: the initial missing-module failure above.
- `file_reading_outside_git_and_cli %p %p`: the initial missing-module failure above.
- `file_writing_outside_git %p %p`: the initial missing-module failure above.
- `sockets_outside_api %p %p`: the initial missing-module failure above.
- `clock_port_call_is_not_a_clock_read`: the initial missing-module failure above.
- `app_may_parse_a_stamp`: the initial missing-module failure above.
- `confined_calls_are_allowed_where_ruled`: the initial missing-module failure above.
### `ts/tests/structure/imports.test.ts`

First failure: `error: Cannot find module './plant.ts'` when loading this file.

- `core_importing_app`: the initial missing-module failure above.
- `adapter_importing_adapter`: the initial missing-module failure above.
- `import_past_front_door`: the initial missing-module failure above.
- `relative_import_leaving_its_package`: the initial missing-module failure above.
- `test_importing_past_front_door`: the initial missing-module failure above.
- `cycle_between_modules`: the initial missing-module failure above.
- `cycle_within_a_package`: the initial missing-module failure above.
- `core_importing_node_builtin`: the initial missing-module failure above.
- `core_importing_bun_builtin`: the initial missing-module failure above.
- `core_importing_other_npm_package`: the initial missing-module failure above.
- `app_importing_builtin`: the initial missing-module failure above.
- `child_process_outside_git`: the initial missing-module failure above.
- `sqlite_outside_store`: the initial missing-module failure above.
- `fs_outside_git_and_cli`: the initial missing-module failure above.
- `http_outside_api`: the initial missing-module failure above.
- `unresolvable_import`: the initial missing-module failure above.
- `confined_io_is_allowed_where_ruled`: the initial missing-module failure above.
- `main_may_import_every_package`: the initial missing-module failure above.
- `core_may_import_yaml_and_noble_hashes`: the initial missing-module failure above.
- `tests_and_scripts_may_use_files`: the initial missing-module failure above.
- `source_cannot_escape_to_tests`: added later, failed with `Expected to contain: "front-door: src/core/a.ts -> tests/helper.ts"`, `Received: []`, and `23 pass / 1 fail` before rejecting source imports into tests or scripts.
- `package_may_not_import_main`: added later, failed with `Expected: true`, `Received: false`, and `22 pass / 1 fail` before fixing allowed-imports to include `src/main.ts` as a forbidden target.
### `ts/tests/structure/layout.test.ts`

First failure: `error: Cannot find module './plant.ts'` when loading this file.

- `unknown_package`: the initial missing-module failure above.
- `missing_front_door`: the initial missing-module failure above.
- `nested_folder`: the initial missing-module failure above.
- `imports_must_match_packages`: the initial missing-module failure above.
- `oversized_module %p`: the initial missing-module failure above.
- `oversized_test`: the initial missing-module failure above.
- `module_at_the_limit_passes`: the initial missing-module failure above.
### `ts/tests/structure/repository.test.ts`

First failure: `error: Cannot find module './plant.ts'` when loading this file.

- `repository_has_no_violations`: the initial missing-module failure above.

No mutation was required for an earlier task’s implementation.
The existing `bun_runs_typescript_tests` test remained unchanged and passed.

## Python forms that do not carry over

The structure rows are deliberately changed, rather than ported test by test, as required by design line 58 and the brief.
The following Python tests cannot hold literally in TypeScript.
Their applicable rule is tested in the TypeScript forms specified by the brief.

- `tests/test_structure.py:test_submodule_through_front_door`: Python from-import submodule discovery has no corresponding static TypeScript form; front-door checks operate on resolved module targets.
- `tests/test_structure.py:test_from_lodge_import_package`: Python from-package syntax has no TypeScript counterpart; adapter_importing_adapter tests the prohibited edge through # aliases.
- `tests/test_structure.py:test_import_statement_form`: Python dotted import aliases have no TypeScript syntax; the import graph checks the resolved package instead.
- `tests/test_structure.py:test_relative_import`: The Python rule rejects every relative import, whereas the brief allows relative imports within a package and rejects those leaving it.
- `tests/test_structure.py:test_import_inside_function`: Static TypeScript imports are top-level syntax, and dynamic imports anywhere are rejected separately.
- `tests/test_structure.py:test_dynamic_import`: Python importlib, __import__, and getattr forms do not exist; dynamic_code_anywhere checks import() and require().
- `tests/test_structure.py:test_own_front_door_import`: The TypeScript brief does not forbid importing one’s own front door; cycles remain forbidden.
- `tests/test_structure.py:test_root_imports_nothing`: There is no Python package root __init__.py; src/main.ts is explicitly allowed to import every package.
- `tests/test_structure.py:test_package_directory_without_init`: TypeScript has no __init__.py; nested_folder enforces the specified replacement rule.
- `tests/test_structure.py:test_source_that_is_not_utf8_names_the_file`: The specified TypeScript checkers read strings and do not define a UTF-8 decoding violation; this Python decoding assertion is not claimed as carried.
- `tests/test_structure.py:test_syntax_error_is_reported`: TypeScript compilation reports syntax errors in the gate; callViolations uses the recovering TypeScript parser and has no cannot-parse diagnostic contract.
- `tests/test_structure_io.py:test_core_disallowed_module`: Python standard-library module names differ; core/app builtin and npm prohibitions replace this allow-list test.
- `tests/test_structure_io.py:test_core_banned_name`: Python datetime aliases, open, input, and print differ; core_disallowed_global and the clock/local-time tests use the specified TypeScript names.
- `tests/test_structure_io.py:test_subprocess_outside_gitstore`: Python subprocess is replaced by child_process confinement outside git.
- `tests/test_structure_io.py:test_process_spawning_outside_gitstore`: Python os, asyncio, multiprocessing, and pty forms do not exist; Bun spawning and child_process are checked instead.
- `tests/test_structure_io.py:test_file_writing_outside_gitstore`: Python pathlib, os, shutil, and tempfile APIs differ; named writes and Bun.write are confined outside git.
- `tests/test_structure_io.py:test_pure_packages_do_not_write_files`: Python write methods differ; source package purity and TypeScript write-call restrictions enforce this rule.
- `tests/test_structure_io.py:test_open_for_writing_outside_gitstore`: Python open modes and FileIO do not exist; the TypeScript brief instead confines named writing functions and Bun.write.
- `tests/test_structure_io.py:test_open_outside_gitstore_and_cli`: Python open, pathlib, and pkgutil forms differ; fs imports and Bun.file are confined as specified.
- `tests/test_structure_io.py:test_package_data_may_be_read_through_importlib_resources`: Python importlib.resources and the viewer package are absent from this TypeScript package table.
- `tests/test_structure_io.py:test_plain_path_read_outside_cli_still_fails`: Python pathlib operations and viewer fixtures have no literal counterpart; fs and Bun.file rules cover the specified TypeScript reads.
- `tests/test_structure_io.py:test_package_data_read_in_hook_still_fails`: Python importlib.resources does not exist in TypeScript; the brief has no separate resource API rule.
- `tests/test_structure_io.py:test_webbrowser_open_is_not_a_file_open`: Python webbrowser.open does not exist, and the TypeScript brief does not classify arbitrary open calls as file access.
- `tests/test_structure_io.py:test_resources_outside_cli_and_viewer`: Python importlib.resources and the viewer package do not exist in the TypeScript structure.

Other Python rule scenarios are represented by the explicit replacement tests in the brief.
The frozen parity table’s seven structure rows retain their reasons and counterpart paths verbatim.

## Commands and results

Read-only inspection used `cat`, `rg`, `sed`, `awk`, `wc`, and `git status` or `git diff`; temporary Python helpers generated the new task files.
No install, network operation, real-repository test, Python source edit, or whole Python gate was attempted.

| Command | Result and last lines |
|---|---|
| `uv run --frozen --quiet lodge waiting` | Exit 0; `waiting for the author` / `nothing`. |
| `cd ts && bun test tests/structure tests/parity.test.ts` before implementation | Exit 1; `0 pass`, `5 fail`, `5 errors`. |
| `cd ts && bun --bun x biome check --write .` | Exit 0; formatted the new files; final invocation reports no remaining diagnostics. |
| `cd ts && bun --bun run check` during implementation | First failed in tsc with `TS2769`, because a planned row’s optional plan was passed to toContain; corrected the assertion to reject missing plans explicitly. |
| `cd ts && bun test tests/structure/imports.test.ts` with the new main regression | Exit 1; `22 pass`, `1 fail`, `23 expect() calls`. |
| `cd ts && bun test tests/parity.test.ts` with the new title regression | Exit 1; `9 pass`, `1 fail`, `269 expect() calls`. |
| `cd ts && bun test tests/structure/imports.test.ts` with the source escape regression | Exit 1; `23 pass`, `1 fail`, `24 expect() calls`. |
| Temporary `bun -e` title-inventory probe | Exit 1; `Expected ";" but found ")"`; a malformed probe expression, with no repository change, replaced by a local Python report inventory. |
| `cd ts && bun run test:structure` after implementation | Exit 0; `141 pass`, `0 fail`, `403 expect() calls`, across 5 files. |
| `cd ts && bun --bun run check` after implementation | Exit 0; no dependency violations, `142 pass`, `0 fail`, `404 expect() calls`, across 6 files. |
| `sh scripts/check-ts.sh` as the final gate | Exit 0; Biome, tsc, dependency-cruiser, knip, and Bun tests pass; `143 pass`, `0 fail`, `405 expect() calls`, across 6 files. |

## Concerns and uncertainty

No unresolved implementation concern.
Knip prints two non-failing hints because the pre-existing scripts entry and project globs have no matching files yet.
The coordinator’s whole-repository gate remains outside this task’s sandbox and scope.
The script in package.json is a convenience for the brief’s exact targeted command; no dependency or lockfile change was needed.
