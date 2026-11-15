# Task 8 report

The composition root is `ts/src/main.ts`, and `bun run build` compiles the command and server into `dist/lodge`.
The API exports `listen` and `withoutYamlLogging`.
Knip checks entry exports and reports nothing.

## Changes per file

| File | Change |
|---|---|
| `ts/src/main.ts` | Clears YAML logging first, imports the package version, wires the real clock and eight-byte ID entropy, awaits database opening, builds the shared API options, dispatches server or client commands, writes exact output streams, and sets the returned exit code. |
| `ts/src/api/serve.ts` | Deletes both YAML logging variables and serves through Bun with the requested hostname and port, resolving after signal-triggered shutdown. |
| `ts/src/api/index.ts` | Exports both new functions and tags the protected setup re-export statement. |
| `ts/package.json` | Adds the exact compile build script. |
| `ts/knip.json` | Adds `src/main.ts` to entries and enables `includeEntryExports`. |
| `.gitignore` | Ignores `ts/dist/`. |
| `ts/tests/e2e/binary.test.ts` | Builds once asynchronously, runs version and guide from a separate temporary directory with PATH alone, and removes both temporary directories. |
| `ts/tests/api/environment.test.ts` | Tests both variable deletions and parses main with TypeScript to require the clearing call first after imports. |
| `ts/tests/parity.json` | Marks the entry point ported and the wheel changed, with `installed_wheel_runs` dropped because the compiled-binary test replaces wheel installation and resource inspection. |
| `ts/src/core/confirmation.ts` | Tags `MINUTE_FORMAT` public. |
| `ts/src/core/threads.ts` | Tags `THREADS` public. |
| `ts/src/core/views.ts` | Tags `headParts` public. |
| `ts/src/core/model.ts` | Tags `Imported`, `NumberHandle`, and `Quote` public. |
| `ts/src/core/order.ts` | Tags `Placement` public. |
| `ts/src/core/render.ts` | Tags `Placed` public. |
| `ts/src/core/snapshot.ts` | Tags `Files` public. |
| `ts/src/core/index.ts` | Tags the five explicit re-export statements containing the reported protected names. |
| `ts/src/app/ports.ts` | Tags `HeldMessage` public. |
| `ts/src/api/setup.ts` | Tags `ServerParts` public for plan 4. |
| `ts/src/cli/index.ts` | Removes four unused type re-exports. |
| `ts/src/store/index.ts` | Removes the unused `Tables` re-export. |
| `ts/tests/core/thread-files.test.ts` | Removes `export` from `EXAMPLE`. |
| `docs/superpowers/plans/2026-11-02-lodge-server-api/task-8-report.md` | Records changes, failing evidence, rulings, and verification. |

## Test-first evidence

Before production changes, the exact required command was run:
`cd ts && bun test tests/e2e/binary.test.ts tests/api/environment.test.ts`.
It exited 1 with `0 pass`, `2 fail`, and `1 error`.

| Test | First failing output |
|---|---|
| `version` | The shared build hook failed: `error: ModuleNotFound resolving "src/main.ts" (entry point)`, received instead of empty stderr. |
| `compiled_binary_runs` | The same shared build hook failed before either compiled-binary assertion could run. |
| `yaml_logging_variables_are_cleared` | Module loading failed: `SyntaxError: Export named 'withoutYamlLogging' not found`. |
| `main_clears_yaml_logging_first` | The same missing-export module error prevented execution. |

After implementation, the same command passed all four tests.
The ordering mutation moved the clearing call below the existing clock declaration, an import-time statement.
`main_clears_yaml_logging_first` then failed with `Expected: true, Received: false` at the expression-statement assertion: `0 pass`, `1 fail`.
An earlier equivalent mutation inserted a declaration before the call and failed identically.
The second mutation removed only the LOG_STREAM deletion.
`yaml_logging_variables_are_cleared` failed because the received object still held `"LOG_STREAM": "1"`: `0 pass`, `1 fail`.
Both mutations were reverted.

## Knip findings

The three required kinds are listed below.
All definition tags are exactly `/** @public */`.

| Kind | Names and action |
|---|---|
| Removed exports | `Exit`, `ThreadCommand`, `ProjectSettings`, and `ServerPlace` from `#cli`; `Tables` from `#store`. Their internal definitions and readers remain. |
| Tagged public definitions | `MINUTE_FORMAT`, `THREADS`, `headParts`, `Imported`, `NumberHandle`, `Quote`, `Placement`, `Placed`, `Files`, and `HeldMessage` preserve the core/app front-door contract; `ServerParts` preserves plan 4's consumed name. |
| Test export losing export | `EXAMPLE` in `ts/tests/core/thread-files.test.ts`. |

A fourth kind was explicitly approved by the coordinator after definition tags alone left knip findings on explicit re-exports.
The protected re-export names are `MINUTE_FORMAT`, `headParts`, `Imported`, `NumberHandle`, `Quote`, `Placement`, and `Placed` in `#core`, and `ServerParts` in `#api`.
Their containing re-export statements also receive `/** @public */`, retaining the explicit front-door lists and all definition tags.
The next knip run exited 0 with no output.
No consumed name was removed or renamed, and `lodgesOver` retains its name and signature.

## Rulings and verification

The coordinator confirmed sole-builder, test-first work because the plan header's superpowers skill is unavailable.
The coordinator selected SIGINT/SIGTERM shutdown: await `server.stop()`, remove both handlers, and resolve `listen`.
A repeated signal cannot start a second shutdown.
A stop rejection removes the handlers and rejects the promise.
The coordinator also confirmed that the pasted table's `tomlTable` factoring belongs to plan 4 Task 8, so `settings.ts` stays unchanged.

Initial gate attempts exposed strict TypeScript index-signature access and assertion typing, followed by a formatting error.
These were fixed in the new files.
The first successful `sh scripts/check-ts.sh` exited 0 with `1808 pass`, `0 fail`, and `5218 expect() calls` across 161 files.
That gate included Biome with `--error-on-warnings`, TypeScript, dependency-cruiser, knip with no findings, and all tests, including the unchanged structure checks.
Biome's literal-key diagnostics are informational.
The parity rows were then flipped, and the complete gate exited 0 again with `1808 pass`, `0 fail`, no skips, and `5225 expect() calls` across 161 files.
Knip again reported nothing.
`bun run build` also exited 0, bundling 725 modules and compiling `dist/lodge`.

No test opened a socket.
`LODGE_E2E_BINARY` was unset, and neither S1 nor `scripts/check.sh` was run.
No dependency was installed, and no earlier brief, report, review, or structure rule was edited.
