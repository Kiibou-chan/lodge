# Task 8 correctness review

Reviewed `372b49d..65030ce` against the complete Task 8 section, the plan's global constraints and calls, probes 4 and 5, the report, `ts/knip.json`, `ts/tests/parity.json`, and plan 4's consumed-name table in `task-8-brief.md`.
There are no Important findings and one Minor finding.
All implementation probes and mutations ran in a detached temporary worktree at `65030ce`; the original worktree's only new review change is this file.

## Minor M8-1: four definition tags suppress exports that knip does not report

Locations: `ts/src/core/model.ts:7` (`Quote`), `ts/src/core/model.ts:26` (`NumberHandle`), `ts/src/core/model.ts:31` (`Imported`), and `ts/src/core/order.ts:6` (`Placement`).
The four definition-level `/** @public */` tags are unnecessary under Task 8's instruction to tag the exports knip reports.
`Imported` and `Quote` have import readers in `headers.ts:25-26`, `Imported` in `fileformat.ts:14`, and all three model types in `views.ts:6-9`.
`Placement` is used within its defining module and exposed through `derivedOrder`'s return type; its definition is likewise not a knip finding.
The tags conceal a future loss of these readers from unused-export detection.
Their protected front-door re-exports should retain their tags.

Probe: remove every `/** @public */` line under `ts/src` in the scratch worktree, then run `cd ts && bun --bun node_modules/knip/bin/knip.js`.
Knip exits 1 with five unused exports and ten unused exported types, including these four names only at their `core/index.ts` re-exports, never at their definitions.
Restore the source, remove only these four definition tags, and run the same command: exit 0, no findings.
This distinguishes the unnecessary tags from the required re-export tags and leaves the front-door contract intact.

The coordinator selected option A, one Minor finding, through `coord.ask_coordinator` during this review.
The ruling states that the earlier instruction to retain all definition tags relied on the build run's claim that they were needed, which this differential probe disproves.
Remove only these four definition tags in a subsequent fix.

## Checked and sound

- `main.ts:7` clears YAML logging as the first statement after imports, and `serve.ts:1-4` deletes both variables without deleting another variable.
  Moving the call below the clock declaration makes `main_clears_yaml_logging_first` fail at `environment.test.ts:29` with `Expected: true, Received: false`.
  Separately removing the `LOG_STREAM` deletion makes `yaml_logging_variables_are_cleared` fail at line 14 because `LOG_STREAM` remains.
  Both mutations were restored.
- `main.ts:9-14,28-40` uses the exact prescribed clock, local offset, seconds-to-milliseconds timer, eight-byte ID entropy, shared clock and projects, package version, and stderr logger, and awaits `openDatabase(data)`.
  A scratch preload probe mocked `#api`, `#store`, and `#cli`, delayed database opening, and asserted database readiness before adapter construction, object identity through `lodgesOver` and `ApiOptions`, entropy lengths, clock values, timer completion, and `listen` identity.
  Both the server and client paths passed.
- `serve.ts:6-35` supplies the requested hostname, port, and handler to `Bun.serve`.
  The scratch `review-shutdown.test.ts` replaced `Bun.serve` with a fake server and controlled the promise returned by `stop()`; no socket was opened.
  Success and rejection cases both passed, with 15 assertions across two tests: both signal handlers are installed, repeated SIGINT/SIGTERM calls start shutdown once, the returned promise remains pending until stop settles, both handlers return to their previous counts, and rejection preserves the original error.
- `main.ts:15-21,46-52` forwards output without adding or removing bytes, passes cwd, environment, global fetch, and package version to `run`, and assigns its returned status to `process.exitCode`.
  The preload probe verified separate stdout and stderr strings containing newlines and `é😀`, client exit 1, server exit 2, and YAML-variable clearing on both paths.
  Direct child-process comparisons of `main.ts` with lodge 0.2 from a scratch folder matched the exit code and both complete streams for `id x`, `search x --status gone`, `id d` outside a repository, `show` without its argument, and `--version`, allowing only the planned version substitution from 0.2.0 to 0.3.0.
- Knip has `src/main.ts` as an entry and `includeEntryExports: true`; the unmodified range reports no findings.
  The remaining newly tagged definitions are required by the core/app front-door tests or, for `ServerParts`, plan 4's table.
  All tagged core names occur in Python core's `__all__`, and `HeldMessage` is an allowed app addition.
  The required explicit re-export tags follow the reported coordinator ruling and preserve those front doors.
  Removed exports (`Exit`, `ThreadCommand`, `ProjectSettings`, `ServerPlace`, and `Tables`) are absent from plan 4's consumed-name table; the consumed exports remain, including `Command`, `Io`, `readSettings`, `ServerParts`, and the unchanged `lodgesOver` signature.
  The unread test constant `EXAMPLE` correctly loses only its export.
- The parity row for `tests/test_entry_point.py` is `ported`; the wheel row is `changed`, names `installed_wheel_runs` in `dropped`, and explains replacement of the wheel with the compiled binary.
  The binary assertions preserve the Python version and guide expectations with the planned version change.
- `binary.test.ts:7-35` builds once with asynchronous `Bun.spawn`, awaits completion, invokes the compiled binary from a separate folder with only `PATH` supplied as its environment, and removes both temporary folders through `afterAll`.
  Running the binary and environment tests with a dedicated scratch `TMPDIR` passed all four tests, and a subsequent directory walk found no remaining entries.
  The build script and `ts/dist/` ignore entry match the plan.
- No structure check or gate script changes in the reviewed range.
  The only executable test socket path found is the existing `LODGE_E2E_BINARY` branch in `tests/e2e/project.ts:98-104`; the variable was unset for this review's gate.
  The new binary test invokes only version and guide, and no gate test calls the new `listen`.

## Validation and limits

`sh scripts/check-ts.sh` at the unmodified range head exited 0: Biome with `--error-on-warnings`, TypeScript, dependency-cruiser, knip with no findings, and 1,808 passing tests across 161 files, with zero failures and 5,225 assertions.
The separate unmodified binary/environment run passed four tests with ten assertions.
The scratch mutations were restored, and the scratch worktree and its containing temporary folder were removed after review.
The socket-based S1 binary integration run and the coordinator's `scripts/check.sh` were not run; the direct main probes above establish composition and stream forwarding without claiming full socket-based command parity.
