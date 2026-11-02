# Task 3 fix round 1 report

Status: DONE.
All requested findings are addressed.
No commit, push, installation, or network command was run.
Task 4's committed `ts/src/core/*.ts` files were not edited, and the repository structure test passes with them.
The reviewer-owned `task-4-review.md` was not edited.

## Changes and evidence per finding

### B1

Replaced the per-package front-door rules with two group-matching rules, covering every relative import leaving a source package, including imports of loose source files.
The companion rule covers `tests`, `scripts`, and `src/main.ts`.
`layoutViolations` now rejects a loose TypeScript source other than `main.ts`.
`relative_import_to_loose_source_is_refused` expects exactly `front-door: src/core/a.ts -> src/util.ts`.
`loose_source_is_an_unknown_package` expects exactly `src/util.ts: unknown package util`.
Against the original configuration the former received `[]`; against the original call/layout module the latter received `[]`.
The `original-config` and `original-layout` runs below give the failing output.

### I1

Added `edges.test.ts`, with one planted tree and cruise for all package alias edges, including `main`, and another for every cross-package private relative edge.
The expected alias refusals come from `PACKAGES`, so permitted edges are also checked for false reports.
`allowed_edges_match_the_table` fails separately when each of the seven package rules is removed, when `app -> core` is forbidden, and when `store -> app` is forbidden.
`every_package_uses_front_doors` fails when `app` is omitted from the group rule.
The mutation runs below name each failure and its last output lines.

### I2

Added `cycles_and_missing_imports_bind` for both `tests` and `scripts`, checking exact lists containing a cycle and an unresolved dependency.
Narrowing either rule to `^src/` loses the corresponding expected line and fails both cases.
See `no-circular-source-only` and `not-to-unresolvable-source-only` below.

### I3

All import and call refusal assertions now compare entire lists, including the source, line, package, and message.
Where two independent import rules apply, the assertion names both rather than silently discarding one.
Removed duplicate `Date.now` and `Date` reports by handling the property read once, skipping the overlapping core clock-call check, and leaving ordinary core `Date` identifiers to the identifier check.
The original implementation fails the exact Date assertions, with two extra reports for `Date.now()` and one for `new Date()`.
The wrong-package mutation fails thirteen cases.
Injecting an extra report fails all 126 call tests and all 24 import tests, including every strengthened refusal assertion.
Those runs below show every failing title, so changed assertions that already passed against the original implementation also have mutation evidence.

### I4

In `app`, every call of `Date` without `new` is refused regardless of its arguments; only a one-argument constructor is exempt.
Core still refuses every use of `Date`.
Added `Date("x")` cases to `core_disallowed_global`.
The original implementation returns `[]` for the app case instead of `src/app/a.ts:1: app may not use Date`.
The existing allowed stamp-constructor case still passes.
This implements ruling `d-mfskz3`.

### I5

Added the named write, writev, link, mkdtemp, and createWriteStream forms, their Sync forms, unsafe open/openSync flags, and write/writer/delete calls on a Bun.file receiver.
Open flags are unsafe when absent, non-literal, or containing `w`, `a`, or `+`.
`file_writing_outside_git` has an exact-list refusal case for each added form.
The original implementation returns `[]` for these new forms, instead of the single `file writing outside git` diagnostic.
`confined_calls_are_allowed_where_ruled` now also checks these forms in `git`, and `openSync("p", "r")` in `cli`.
The extra-report mutation fails that strengthened allowed test too.
This implements ruling `d-mfskz3`.

### m1

Added socket reports for `fetch` and constructed `WebSocket` in both `store` and `git`.
Added WebSocket to the pure-package ban so both `core` and `app` retain their own refusal diagnostic.
`api`, `cli`, and `hook` are checked as permitted for both network forms.
The four adapter refusal cases return `[]` against the original module and fail exact-list assertions.
The two new pure WebSocket cases were also run before adding the ban: `124 pass`, `2 fail`, `126 expect() calls`.
The adapter and pure failures appear in `original-calls` below.
The allowed cases are included in the extra-report mutation run.
This implements ruling `d-s5s2c3`.

### m2

Skip identifiers used as static property names in assignments, signatures, declarations, methods, and binding property names.
Actual value identifiers remain checked.
`property_names_are_not_globals` covers both pure packages, object keys, interface properties and methods, class fields and methods, and a renamed destructuring property.
Both cases fail against the original module, which reports the field names as forbidden global uses.
See `original-calls` below.

### m3

`oversized_module` now uses only `src/core/a.ts`.
`oversized_test` covers both `tests/core/a.ts` and `scripts/a.ts`, with complete expected diagnostics.
`unknown_package` covers both `wrong` and the forbidden `main` folder.
Removing source sizing, removing scripts sizing, or accepting the main folder fails the corresponding case.
See `oversized-source-unchecked`, `scripts-size-unchecked`, and `main-folder-accepted` below.

### m4

Removed `test:structure` from `ts/package.json`.
This is a script deletion with no new test; the ordinary gate still runs every test.

### m5 and m9

Bun can load `tests/structure/table.ts` directly from the CommonJS configuration without a build step.
Verified with `cd ts && bun -e 'console.log(require("./tests/structure/table.ts").CORE_NPM)'`, whose output is `[ "yaml", "@noble/hashes" ]`.
The configuration now requires that table, generates allowed-import rules from `PACKAGES`, and builds the npm exception pattern from `CORE_NPM`.
The two generic front-door rules use group matching instead of a duplicated list of packages; they apply to every package without maintaining another table.
Formatted the CommonJS file with Biome via a JavaScript stdin filename, using the repository's formatting settings.
Every line of the configuration is at most 100 characters.
The table-driven allowed-edge test checks all entries.
The existing confined tree imports every `CORE_NPM` member, and the exact third-party-package refusal remains checked.
Removing yaml from the npm exceptions fails three allowed tests; adding typescript fails `core_importing_other_npm_package`.
See the npm mutation runs below.

### m6

Replaced the duplicate builtin and filesystem test declarations with `test.each` cases carrying both path and module in their titles.
Both forms retain exact diagnostic assertions.
All four cases fail against the injected extra import report, as shown below.

### m7

Extracted `rowMissing(root, pythonPath, row)` into `parity-names.ts`.
Both the production parity row loop and the synthetic missing-name regression call it.
The synthetic case writes a Python file and TypeScript counterpart with `plant`, then reads them through the same paths as a real row.
It expects only `b`, proving that `a` was found in the TypeScript file.
Before the helper existed the test failed to load because `rowMissing` was not exported.
A mutation discarding the TypeScript file contents makes the synthetic case receive `["a", "b"]` instead of `["b"]` and fails the real-row test too.
See both row-missing runs below.

### m8

Removed `a`, `c %p`, `no`, and `real %p` from the old report's list of test titles.
They are fixture strings inside reader tests, not additional tests.
No code test was needed for this report correction.

## Commands and last output

Read the requirements, `CLAUDE.md`, the Task 3 brief, and its review before implementation.
`uv run --frozen --quiet lodge waiting` reported `nothing` for both agent and author queues.
`uv run --frozen --quiet lodge show d-mfskz3 --reasoning` confirmed the Date and file-write ruling.
`uv run --frozen --quiet lodge show d-s5s2c3 --reasoning` confirmed the network permissions.
The cloud runtime skill was read; no environment-status tool was exposed, and no network work was needed.

- Initial `cd ts && bun test tests/structure/calls.test.ts tests/structure/layout.test.ts`: exit 1; `105 pass`, `29 fail`, `134 expect() calls`.
- Initial `cd ts && bun test tests/structure/edges.test.ts tests/parity.test.ts`: exit 1; `4 pass`, `2 fail`, `1 error`, including the absent `rowMissing` export.
- The first exact-import run caught an incorrect test expectation of `typescript.d.ts`; dependency-cruiser resolves `typescript.js`, and the assertion was corrected: `23 pass`, `1 fail` before the correction.
- `cd ts && bunx --no-install biome check --write tests/structure tests/parity.test.ts tests/parity-names.ts`: exit 0; formatting applied before verification.
- `cd ts && bunx --no-install biome format --stdin-file-path=config.js < .dependency-cruiser.cjs`: exit 0; formatted CommonJS output copied back.
- `cd ts && bun --bun run check` after the WebSocket fix: exit 0; `259 pass`, `0 fail`, `759 expect() calls`, across 11 files.
- `git diff --check`: exit 0; no output.

All mutation commands use `bun test` in `ts`, with only the named production/helper/config mutation applied, then restore the exact original bytes in a `finally` block.
`original-*` restores the respective file from `git show HEAD:<path>` temporarily, without changing the index or Task 4 files.
The mutation harnesses were temporary files outside the repository.
Their outputs below are captured output, with timing omitted from failing-title lines.

### original-calls

`cd ts && bun test tests/structure/calls.test.ts`: exit 1.

```text
(fail) core_disallowed_global "core" "Date.now()"
(fail) core_disallowed_global "core" "new Date()"
(fail) core_disallowed_global "core" "Date()"
(fail) core_disallowed_global "core" "new WebSocket(x)"
(fail) core_disallowed_global "app" "Date(\"x\")"
(fail) core_disallowed_global "app" "new WebSocket(x)"
(fail) local_time_in_core_and_app "core" "new Date(2026, 2, 29)"
(fail) file_writing_outside_git "cli" "createWriteStream(\"p\")"
(fail) file_writing_outside_git "cli" "write(x)"
(fail) file_writing_outside_git "cli" "writeSync(x)"
(fail) file_writing_outside_git "cli" "writev(x)"
(fail) file_writing_outside_git "cli" "writevSync(x)"
(fail) file_writing_outside_git "cli" "link(x)"
(fail) file_writing_outside_git "cli" "linkSync(x)"
(fail) file_writing_outside_git "cli" "mkdtemp(x)"
(fail) file_writing_outside_git "cli" "mkdtempSync(x)"
(fail) file_writing_outside_git "cli" "open(\"p\")"
(fail) file_writing_outside_git "cli" "openSync(\"p\", flags)"
(fail) file_writing_outside_git "cli" "fs.promises.open(\"p\", \"w\")"
(fail) file_writing_outside_git "cli" "openSync(\"p\", \"a\")"
(fail) file_writing_outside_git "cli" "openSync(\"p\", \"r+\")"
(fail) file_writing_outside_git "cli" "Bun.file(\"p\").write(\"x\")"
(fail) file_writing_outside_git "cli" "Bun.file(\"p\").writer()"
(fail) file_writing_outside_git "cli" "Bun.file(\"p\").delete()"
(fail) sockets_outside_api "store" "fetch(x)"
(fail) sockets_outside_api "git" "new WebSocket(x)"
(fail) sockets_outside_api "git" "fetch(x)"
(fail) sockets_outside_api "store" "new WebSocket(x)"
(fail) property_names_are_not_globals "core"
(fail) property_names_are_not_globals "app"
96 pass
 30 fail
 126 expect() calls
Ran 126 tests across 1 file. [240.00ms]
```

### original-layout

`cd ts && bun test tests/structure/layout.test.ts`: exit 1.

```text
(fail) loose_source_is_an_unknown_package
9 pass
 1 fail
 10 expect() calls
Ran 10 tests across 1 file. [199.00ms]
```

### original-config

`cd ts && bun test tests/structure/edges.test.ts`: exit 1.

```text
(fail) relative_import_to_loose_source_is_refused
4 pass
 1 fail
 5 expect() calls
Ran 5 tests across 1 file. [394.00ms]
```

### allowed-delete-core

`cd ts && bun test tests/structure/edges.test.ts`: exit 1.

```text
(fail) allowed_edges_match_the_table
4 pass
 1 fail
 5 expect() calls
Ran 5 tests across 1 file. [344.00ms]
```

### allowed-delete-app

`cd ts && bun test tests/structure/edges.test.ts`: exit 1.

```text
(fail) allowed_edges_match_the_table
4 pass
 1 fail
 5 expect() calls
Ran 5 tests across 1 file. [378.00ms]
```

### allowed-delete-store

`cd ts && bun test tests/structure/edges.test.ts`: exit 1.

```text
(fail) allowed_edges_match_the_table
4 pass
 1 fail
 5 expect() calls
Ran 5 tests across 1 file. [384.00ms]
```

### allowed-delete-git

`cd ts && bun test tests/structure/edges.test.ts`: exit 1.

```text
(fail) allowed_edges_match_the_table
4 pass
 1 fail
 5 expect() calls
Ran 5 tests across 1 file. [385.00ms]
```

### allowed-delete-api

`cd ts && bun test tests/structure/edges.test.ts`: exit 1.

```text
(fail) allowed_edges_match_the_table
4 pass
 1 fail
 5 expect() calls
Ran 5 tests across 1 file. [403.00ms]
```

### allowed-delete-cli

`cd ts && bun test tests/structure/edges.test.ts`: exit 1.

```text
(fail) allowed_edges_match_the_table
4 pass
 1 fail
 5 expect() calls
Ran 5 tests across 1 file. [405.00ms]
```

### allowed-delete-hook

`cd ts && bun test tests/structure/edges.test.ts`: exit 1.

```text
(fail) allowed_edges_match_the_table
4 pass
 1 fail
 5 expect() calls
Ran 5 tests across 1 file. [366.00ms]
```

### allowed-invert-app

`cd ts && bun test tests/structure/edges.test.ts`: exit 1.

```text
(fail) allowed_edges_match_the_table
4 pass
 1 fail
 5 expect() calls
Ran 5 tests across 1 file. [403.00ms]
```

### allowed-invert-store

`cd ts && bun test tests/structure/edges.test.ts`: exit 1.

```text
(fail) allowed_edges_match_the_table
4 pass
 1 fail
 5 expect() calls
Ran 5 tests across 1 file. [405.00ms]
```

### no-circular-source-only

`cd ts && bun test tests/structure/edges.test.ts`: exit 1.

```text
(fail) cycles_and_missing_imports_bind "tests"
(fail) cycles_and_missing_imports_bind "scripts"
3 pass
 2 fail
 5 expect() calls
Ran 5 tests across 1 file. [353.00ms]
```

### not-to-unresolvable-source-only

`cd ts && bun test tests/structure/edges.test.ts`: exit 1.

```text
(fail) cycles_and_missing_imports_bind "tests"
(fail) cycles_and_missing_imports_bind "scripts"
3 pass
 2 fail
 5 expect() calls
Ran 5 tests across 1 file. [365.00ms]
```

### wrong-pure-package-message

`cd ts && bun test tests/structure/calls.test.ts`: exit 1.

```text
(fail) core_disallowed_global "app" "Intl"
(fail) core_disallowed_global "app" "performance"
(fail) core_disallowed_global "app" "crypto"
(fail) core_disallowed_global "app" "process"
(fail) core_disallowed_global "app" "Bun"
(fail) core_disallowed_global "app" "fetch"
(fail) core_disallowed_global "app" "new WebSocket(x)"
(fail) core_disallowed_global "app" "console"
(fail) core_disallowed_global "app" "setTimeout"
(fail) core_disallowed_global "app" "setInterval"
(fail) core_disallowed_global "app" "queueMicrotask"
(fail) core_disallowed_global "app" "navigator"
(fail) core_disallowed_global "app" "globalThis"
113 pass
 13 fail
 126 expect() calls
Ran 126 tests across 1 file. [233.00ms]
```

### calls-extra-false-positive

`cd ts && bun test tests/structure/calls.test.ts`: exit 1.

```text
(fail) core_disallowed_global "core" "Date.now()"
(fail) core_disallowed_global "core" "new Date()"
(fail) core_disallowed_global "core" "Date()"
(fail) core_disallowed_global "core" "Intl"
(fail) core_disallowed_global "core" "performance"
(fail) core_disallowed_global "core" "Math.random()"
(fail) core_disallowed_global "core" "crypto"
(fail) core_disallowed_global "core" "process"
(fail) core_disallowed_global "core" "Bun"
(fail) core_disallowed_global "core" "fetch"
(fail) core_disallowed_global "core" "new WebSocket(x)"
(fail) core_disallowed_global "core" "console"
(fail) core_disallowed_global "core" "setTimeout"
(fail) core_disallowed_global "core" "setInterval"
(fail) core_disallowed_global "core" "queueMicrotask"
(fail) core_disallowed_global "core" "navigator"
(fail) core_disallowed_global "core" "globalThis"
(fail) core_disallowed_global "app" "Date.now()"
(fail) core_disallowed_global "app" "new Date()"
(fail) core_disallowed_global "app" "Date()"
(fail) core_disallowed_global "app" "Date(\"x\")"
(fail) core_disallowed_global "core" "Date(\"x\")"
(fail) core_disallowed_global "app" "Intl"
(fail) core_disallowed_global "app" "performance"
(fail) core_disallowed_global "app" "Math.random()"
(fail) core_disallowed_global "app" "crypto"
(fail) core_disallowed_global "app" "process"
(fail) core_disallowed_global "app" "Bun"
(fail) core_disallowed_global "app" "fetch"
(fail) core_disallowed_global "app" "new WebSocket(x)"
(fail) core_disallowed_global "app" "console"
(fail) core_disallowed_global "app" "setTimeout"
(fail) core_disallowed_global "app" "setInterval"
(fail) core_disallowed_global "app" "queueMicrotask"
(fail) core_disallowed_global "app" "navigator"
(fail) core_disallowed_global "app" "globalThis"
(fail) local_time_in_core_and_app "core" "d.getTimezoneOffset()"
(fail) local_time_in_core_and_app "core" "d.toLocaleString()"
(fail) local_time_in_core_and_app "core" "d.toLocaleDateString()"
(fail) local_time_in_core_and_app "core" "d.toLocaleTimeString()"
(fail) local_time_in_core_and_app "core" "d.toDateString()"
(fail) local_time_in_core_and_app "core" "d.toTimeString()"
(fail) local_time_in_core_and_app "core" "d.getFullYear()"
(fail) local_time_in_core_and_app "core" "d.getMonth()"
(fail) local_time_in_core_and_app "core" "d.getDate()"
(fail) local_time_in_core_and_app "core" "d.getDay()"
(fail) local_time_in_core_and_app "core" "d.getHours()"
(fail) local_time_in_core_and_app "core" "d.getMinutes()"
(fail) local_time_in_core_and_app "core" "d.getSeconds()"
(fail) local_time_in_core_and_app "core" "d.getMilliseconds()"
(fail) local_time_in_core_and_app "core" "d.setFullYear()"
(fail) local_time_in_core_and_app "core" "d.setMonth()"
(fail) local_time_in_core_and_app "core" "d.setDate()"
(fail) local_time_in_core_and_app "core" "d.setDay()"
(fail) local_time_in_core_and_app "core" "d.setHours()"
(fail) local_time_in_core_and_app "core" "d.setMinutes()"
(fail) local_time_in_core_and_app "core" "d.setSeconds()"
(fail) local_time_in_core_and_app "core" "d.setMilliseconds()"
(fail) local_time_in_core_and_app "core" "new Date(2026, 2, 29)"
(fail) local_time_in_core_and_app "app" "d.getTimezoneOffset()"
(fail) local_time_in_core_and_app "app" "d.toLocaleString()"
(fail) local_time_in_core_and_app "app" "d.toLocaleDateString()"
(fail) local_time_in_core_and_app "app" "d.toLocaleTimeString()"
(fail) local_time_in_core_and_app "app" "d.toDateString()"
(fail) local_time_in_core_and_app "app" "d.toTimeString()"
(fail) local_time_in_core_and_app "app" "d.getFullYear()"
(fail) local_time_in_core_and_app "app" "d.getMonth()"
(fail) local_time_in_core_and_app "app" "d.getDate()"
(fail) local_time_in_core_and_app "app" "d.getDay()"
(fail) local_time_in_core_and_app "app" "d.getHours()"
(fail) local_time_in_core_and_app "app" "d.getMinutes()"
(fail) local_time_in_core_and_app "app" "d.getSeconds()"
(fail) local_time_in_core_and_app "app" "d.getMilliseconds()"
(fail) local_time_in_core_and_app "app" "d.setFullYear()"
(fail) local_time_in_core_and_app "app" "d.setMonth()"
(fail) local_time_in_core_and_app "app" "d.setDate()"
(fail) local_time_in_core_and_app "app" "d.setDay()"
(fail) local_time_in_core_and_app "app" "d.setHours()"
(fail) local_time_in_core_and_app "app" "d.setMinutes()"
(fail) local_time_in_core_and_app "app" "d.setSeconds()"
(fail) local_time_in_core_and_app "app" "d.setMilliseconds()"
(fail) local_time_in_core_and_app "app" "new Date(2026, 2, 29)"
(fail) core_may_not_use_date "core" "new Date(\"2026-10-29T12:00:00+01:00\")"
(fail) core_may_not_use_date "core" "Date.UTC(2026,9,29)"
(fail) core_names_the_clock_on_any_receiver "core" "d.now()"
(fail) core_names_the_clock_on_any_receiver "core" "d.today()"
(fail) core_names_the_clock_on_any_receiver "core" "d.utcnow()"
(fail) dynamic_code_anywhere "cli" "eval(x)"
(fail) dynamic_code_anywhere "cli" "new Function(x)"
(fail) dynamic_code_anywhere "cli" "import(x)"
(fail) dynamic_code_anywhere "cli" "require(x)"
(fail) spawn_outside_git "cli" "Bun.spawn(x)"
(fail) spawn_outside_git "cli" "Bun.spawnSync(x)"
(fail) spawn_outside_git "cli" "Bun.$`x`"
(fail) file_reading_outside_git_and_cli "store" "Bun.file(x)"
(fail) file_writing_outside_git "cli" "Bun.write(x)"
(fail) file_writing_outside_git "cli" "writeFileSync(x)"
(fail) file_writing_outside_git "cli" "createWriteStream(\"p\")"
(fail) file_writing_outside_git "cli" "write(x)"
(fail) file_writing_outside_git "cli" "writeSync(x)"
(fail) file_writing_outside_git "cli" "writev(x)"
(fail) file_writing_outside_git "cli" "writevSync(x)"
(fail) file_writing_outside_git "cli" "link(x)"
(fail) file_writing_outside_git "cli" "linkSync(x)"
(fail) file_writing_outside_git "cli" "mkdtemp(x)"
(fail) file_writing_outside_git "cli" "mkdtempSync(x)"
(fail) file_writing_outside_git "cli" "open(\"p\")"
(fail) file_writing_outside_git "cli" "openSync(\"p\", flags)"
(fail) file_writing_outside_git "cli" "fs.promises.open(\"p\", \"w\")"
(fail) file_writing_outside_git "cli" "openSync(\"p\", \"a\")"
(fail) file_writing_outside_git "cli" "openSync(\"p\", \"r+\")"
(fail) file_writing_outside_git "cli" "Bun.file(\"p\").write(\"x\")"
(fail) file_writing_outside_git "cli" "Bun.file(\"p\").writer()"
(fail) file_writing_outside_git "cli" "Bun.file(\"p\").delete()"
(fail) sockets_outside_api "cli" "Bun.serve(x)"
(fail) sockets_outside_api "cli" "Bun.listen(x)"
(fail) sockets_outside_api "cli" "Bun.connect(x)"
(fail) sockets_outside_api "store" "fetch(x)"
(fail) sockets_outside_api "git" "new WebSocket(x)"
(fail) sockets_outside_api "git" "fetch(x)"
(fail) sockets_outside_api "store" "new WebSocket(x)"
(fail) clock_port_call_is_not_a_clock_read
(fail) app_may_parse_a_stamp
(fail) confined_calls_are_allowed_where_ruled
(fail) property_names_are_not_globals "core"
(fail) property_names_are_not_globals "app"
0 pass
 126 fail
 126 expect() calls
Ran 126 tests across 1 file. [328.00ms]
```

### imports-extra-false-positive

`cd ts && bun test tests/structure/imports.test.ts`: exit 1.

```text
(fail) core_importing_app
(fail) adapter_importing_adapter
(fail) import_past_front_door
(fail) relative_import_leaving_its_package
(fail) test_importing_past_front_door
(fail) cycle_between_modules
(fail) cycle_within_a_package
(fail) core_importing_node_builtin "src/core/a.ts" "node:fs"
(fail) core_importing_node_builtin "src/core/a.ts" "fs"
(fail) core_importing_bun_builtin
(fail) core_importing_other_npm_package
(fail) app_importing_builtin
(fail) child_process_outside_git
(fail) sqlite_outside_store
(fail) fs_outside_git_and_cli "src/store/a.ts" "node:fs"
(fail) fs_outside_git_and_cli "src/api/a.ts" "fs/promises"
(fail) http_outside_api
(fail) unresolvable_import
(fail) confined_io_is_allowed_where_ruled
(fail) main_may_import_every_package
(fail) core_may_import_yaml_and_noble_hashes
(fail) tests_and_scripts_may_use_files
(fail) package_may_not_import_main
(fail) source_cannot_escape_to_tests
0 pass
 24 fail
 24 expect() calls
Ran 24 tests across 1 file. [617.00ms]
```

### main-folder-accepted

`cd ts && bun test tests/structure/layout.test.ts`: exit 1.

```text
(fail) unknown_package "main"
9 pass
 1 fail
 10 expect() calls
Ran 10 tests across 1 file. [198.00ms]
```

### scripts-size-unchecked

`cd ts && bun test tests/structure/layout.test.ts`: exit 1.

```text
(fail) oversized_test "scripts/a.ts"
9 pass
 1 fail
 10 expect() calls
Ran 10 tests across 1 file. [186.00ms]
```

### row-missing-ignores-typescript

`cd ts && bun test tests/parity.test.ts`: exit 1.

```text
(fail) ported_files_keep_every_python_test_name
(fail) a_ported_file_losing_a_name_fails
8 pass
 2 fail
 273 expect() calls
Ran 10 tests across 1 file. [213.00ms]
```

### npm-allowlist-broadened

`cd ts && bun test tests/structure/imports.test.ts`: exit 1.

```text
(fail) core_importing_other_npm_package
23 pass
 1 fail
 24 expect() calls
Ran 24 tests across 1 file. [459.00ms]
```

### npm-allowlist-removed

`cd ts && bun test tests/structure/imports.test.ts`: exit 1.

```text
(fail) confined_io_is_allowed_where_ruled
(fail) main_may_import_every_package
(fail) core_may_import_yaml_and_noble_hashes
21 pass
 3 fail
 24 expect() calls
Ran 24 tests across 1 file. [510.00ms]
```

### front-door-app-omitted

`cd ts && bun test tests/structure/edges.test.ts`: exit 1.

```text
(fail) every_package_uses_front_doors
4 pass
 1 fail
 5 expect() calls
Ran 5 tests across 1 file. [387.00ms]
```

### oversized-source-unchecked

`cd ts && bun test tests/structure/layout.test.ts`: exit 1.

```text
(fail) oversized_module "src/core/a.ts"
9 pass
 1 fail
 10 expect() calls
Ran 10 tests across 1 file. [209.00ms]
```

### row-missing-original-module

`cd ts && bun test tests/parity.test.ts`: exit 1.

```text
SyntaxError: Export named 'rowMissing' not found in module parity-names.ts
0 pass
 1 fail
 1 error
Ran 1 test across 1 file. [189.00ms]
```

## Final gate

`sh scripts/check-ts.sh` was the last validation command and exited 0.
Biome checked 28 files without changes, TypeScript passed, dependency-cruiser found no violations across 32 modules and 57 dependencies, and knip passed with the existing configuration hints.
The final test output was:

```text
 259 pass
 0 fail
 759 expect() calls
Ran 259 tests across 11 files. [913.00ms]
```

## Concerns

No unresolved finding or TypeScript parity exception was introduced.
Knip reports its existing two configuration hints for absent future `scripts` paths; they do not fail the gate.
