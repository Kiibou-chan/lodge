# Plan fix round 4: plan 4, the importer, the export, and the design's records

Planner, fix round 4, on `server-import` from cbedab8, answering the preflight scan `preflight.md` (79 rows, mismatches M1 to M19), with plan 2 pinned at `origin/server-store` 0244e79 and plan 3 at `origin/server-api` 9ac93ac.
Status: done.

## Ruling recorded

- d-s83a6e: Task 8 extends plan 3's code by names only, the exports start in `main.ts`'s `listen`, and Task 10 runs over `world.ts` (M1 to M4, M10, M15, M16).

## Findings

- M1 (fixed, d-s83a6e): Task 8 adds `tomlTable(text): Readonly<Record<string, unknown>>` to `ts/src/cli/settings.ts`, factored out of `readSettings`, which calls it and answers as before (plan 3's `settings.test.ts` passing unchanged shows it); `zeroTwoCoreTable` builds on it; `RULE-TOML` is dropped; Task 8's Files list `settings.ts`.
- M2 (fixed, d-s83a6e): `world.ts`'s object gains `exporters: Exporters` and `targets: ExportTargets`; the script `ts/scripts/round-trip.ts` makes its one export with `exportFiles` and `exportStore` and needs no `Exporters`.
- M3 (fixed, d-s83a6e): `world.ts` gains `asPerson(operation, body): Promise<Response>`, which registers a `SoftAuthenticator` passkey with a code from `issueSetupCode` and sends the session cookie and `Origin`, and `createProject(project, settings)`, which creates the test project directly through the wrapped `Projects`, so no test depends on whether a session may call `project-create`.
- M4 (fixed, d-s83a6e): Task 10's round trip moves to `ts/tests/api/round-trip.test.ts` over `world.ts` (person `ada`, `FixedClock`); the e2e `server.ts` is no longer modified or used; the script's own `Clock` is stated.
- M5 (fixed): `zeroTwoRepository(layout, extra = new Map())` writes each extra text through `encodeUtf8`; Task 2's `undecodable_attachment_keeps_its_bytes` and Task 10 pass `lodge/attachments/d-q59cdf/raw.bin` with U+DCFF U+DCFE, the bytes `ff fe` (lodge 0.2's `check_change` from an empty state finds no problem with that file added, run in this round).
- M6 (fixed): the "Exports" constraint says each task names its readers and does not export a type only its own module uses; `GitDone`, `StoreRead`, `HookOutput`, `PreparedImport`, and `Imported` are no longer exported; Tasks 2, 4, 5, 6, 7, and 8 name the tests or modules that read each export.
- M7 (fixed): Task 6's Consumes names Task 1's `ZERO_TWO_STORE`; `export_files_hold_the_store_and_kept` publishes the eight files into a `MemoryStore()`, since its constructor takes records only.
- M8 (fixed): `export-target` answers an unknown project `no-project` before the store, as `import` does, with `unknown_project_is_no_project` in `export-target.test.ts`; Task 7's `NotFound` is the store's guard.
- M9 (fixed): Task 7's `setTarget` opens its transaction with `update heads set rev = rev where project = :project` (d-thvvzx), no row being `NotFound`, then appends.
- M10 (fixed, d-s83a6e): `main.ts`'s `listen` starts the exports, from the `Exporters` and `Projects` its last `open` kept; `setup` never listens, so it starts none; no plan 3 shape changes.
- M11 (fixed): "Aligned against" and the ledger name one pin per plan, plan 2 at 0244e79 and plan 3 at 9ac93ac.
- M12 (fixed): the table is "Names this plan consumes from plans 1, 2, and 3"; `START` is in the fakes row; the TOML row names `readSettings`' steps that Task 8 factors into `tomlTable`; the `ApiOptions` row names `log`, `toWire`, `issueSetupCode`, `register-options`, `register`, and the 422 body; a row for `SoftAuthenticator`; `world.ts`'s row replaces the e2e server's.
- M13 (fixed): the lanes' merge list names `ts/package.json` (Tasks 2 and 4), `ts/tests/parity.json` (Tasks 2, 4, and 9), and `ts/src/cli/settings.ts` (Tasks 8 and 9).
- M14 (fixed): Task 11c edits both lines of `CLAUDE.md` that name the frozen design documents, lines 8 and 33.
- M15 (fixed, d-s83a6e): `ApiOptions.moving` is optional, and without it both operations throw `LodgeError("this server was started without import and export")`.
- M16 (fixed, d-s83a6e): `person.ts` dispatches `import` and `export-target` as it dispatches `approve`, to `importOperation` and `exportTargetOperation` of `moving.ts`, each answering `{ checkFailed, result }`; a `checkFailed` answer is answered 422 as `approve`'s `CHECK_FAILED` is; field checks use plan 3's sentences, with `unknown_field_is_usage`.
- M17 (fixed in part): Task 6 adds `exportFailedLine(project, error)`, tested by `failed_line_names_the_project`, which `main.ts` and `world.ts` use for `failed`; the `start` call in `main.ts`'s `listen` stays without a test, as Task 8 says, since no test imports `main.ts`.
- M18 (fixed): `moved_record_edit_names_the_server` asserts the absence of `do not edit it by hand` and `as a draft outside`, the two phrases of lodge 0.2's `RECORD_TEXT` (`src/lodge/hook/post_tool_use.py:26-27`).
- M19 (fixed): `import-store.test.ts`'s `MemoryStore` is built with `people` `{ana}`.

## Preconditions

- d-d0vca9's write rule lands in plan 1's fix wave, which is in progress; the Global Constraints already say plan 4 builds after it, and Tasks 6, 8, and 9 cannot pass `check-ts.sh` before (preflight C12).

## Plan 3 shape changes needed

None. Every addition is a new name in plan 3's files: `tomlTable`, the two dispatched operations, the optional `ApiOptions.moving`, and four members of the object `world.ts` returns. Two places depend on plan 3's merged code, and the coordinator names them in Task 8's brief: the file that declares `ApiOptions`, and the way `person.ts` dispatches `approve` and answers its 422.

## Re-pinned during the round

- Plan 3 at `origin/server-api` 9a25b93 rather than 9ac93ac (the coordinator: nothing plan 4 consumes changed, `world.ts` and `testServer()` unchanged); "Aligned against" and the ledger say so.
- Plan 3's Task 4 now adds `MIGRATIONS[2]` (`user_version` 2 to 3), so Task 7 says a later migration of this plan would be `MIGRATIONS[3]` or later; plan 4 still adds none.
