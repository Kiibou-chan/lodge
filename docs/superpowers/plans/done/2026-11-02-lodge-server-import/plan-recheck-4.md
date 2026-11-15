# Plan recheck 4: plan 4, the importer, the export, and the design's records

Rechecked: fix round cbedab8..484f69c on `server-import` (62238a0 and 484f69c), against `preflight.md` (M1 to M19), `plan-fix-4.md`, and d-s83a6e.
Plan 3 read at `origin/server-api` 9a25b93 (its tip 8f02776 adds only `plan-recheck-5.md`); plan 2 at 0244e79 (the tip of `origin/server-store`), whose changes since a035344 touch no name plan 4 consumes (citations, Task 12c's waiting rule, a test split).
Status: done.

Counts: 19 of 19 resolved as claimed (M17 in part, as claimed); new: 0 Blocking, 0 Important, 1 Minor.

## Additions to plan 3's code

### `tomlTable` in `ts/src/cli/settings.ts` (M1) · Resolved, names only

Plan 3 at 9a25b93 declares `readSettings(root: string): ProjectSettings` (line 264) and does the parsing inline: smol-toml with `integersAsBigInt: true`, a `bigint` to a number, a float (`inf` and `nan` included) or a date or time to `null`, a text that is not TOML `.lodge.toml: ` and smol-toml's first line (lines 273 to 276).
Plan 4's `tomlTable(text)` (plan lines 445 to 448) is exactly those steps on text, `readSettings` calling it, with plan 3's `settings.test.ts` passing unchanged as the check that nothing moved (Step 4).
Reading the file strictly stays in `readSettings`; `zeroTwoCoreTable` refuses U+DC80 to U+DCFF before `tomlTable`, so the text paths agree.
`settings.ts` is now in Task 8's Modify and in the shared-files merge list with Task 9 (plan line 108).

### `importOperation` and `exportTargetOperation` in `ts/src/api/moving.ts`, dispatched from `person.ts` (M16) · Resolved, names only

Plan 3's person operations live in `ts/src/api/person.ts` (Task 6 Files, plan 3 line 416), each `forbidden` with `only the signed-in person may <operation>` for a token, and `approve` answers a `CHECK_FAILED` with 422 "as `add` does" (plan 3 line 445), the body `{"error": {"kind": "check-failed", "message": "the check failed"}, "result": …}` (plan 3 line 394).
Plan 4 dispatches the two operations as `approve` is and answers `checkFailed` with that body (plan lines 463 to 466); the field sentences are plan 3's (`<operation>: <field> must be <what>`, `<operation>: unknown field <name>`); `unknown_field_is_usage` is new.
Plan 3 names no table or helper for that dispatch, which d-s83a6e records and leaves to the coordinator's brief from the merged code (plan line 433).
Structure: `moving.ts` is in `src/api`, importing `#app` (`importStore`, `exportTargetProblem`, `coreSettings`, `person`, `Exporters`, `ExportTargets`, `ZeroTwoCopy`) by alias, which the `allowed-imports` and `front-door` rules of `ts/.dependency-cruiser.cjs` on `server-core` (lines 13 to 38) permit for `api`; its import of the file declaring `ApiOptions` is one `person.ts` already makes, so `no-circular` sees no new cycle.

### Optional `ApiOptions.moving` (M15) · Resolved, names only

`ApiOptions` at 9a25b93 is `{ accounts, projects, lodgeFor, clock, random, version, log }` (plan 3 lines 370 to 378); plan 4 adds `readonly moving?: Moving` (plan line 461), so plan 3's literals (`server.ts`, `setup.test.ts`'s `open`, `main.ts`) compile unchanged, and both operations without it throw `LodgeError("this server was started without import and export")`.

### `world.ts`'s four members (M2, M3, M4) · Resolved, names only

Plan 3 gives `world.ts` a handler over `openDatabase(":memory:")`, `FixedClock` at 2026-10-29T09:30:00+01:00, the person `ada`, the project `work`, a token, and a `log` array (plan 3 line 400), with no declared return shape, so `exporters`, `targets`, `createProject`, and `asPerson` (plan lines 471 to 477) are additions.
`asPerson` uses only plan 3's names: `issueSetupCode(options): Promise<string>` (plan 3 line 431, `#api`), `register-options` and `register` with `setupCode` (lines 434 and 435, `register` starting a session), the cookie `lodge_session` (line 442), the `Origin` rule (line 440), and `SoftAuthenticator` of `ts/tests/api/authenticator.ts` (lines 417 and 455).
Plan 3's `TestServer` at 9a25b93 has no `asPerson` (lines 520 to 530), so the name does not collide; the e2e `server.ts` is untouched and unused by plan 4 (plan line 478).
The clock arithmetic holds: the challenge lives 5 minutes and the setup code 15 by `options.clock` (plan 3 lines 441 and 452), and the `FixedClock` moves only by `sleep`, so a sign-in after the five-day `sleep(432000)` issues its code at the moved time.

### Exports start in `main.ts`'s `listen` (M10) · Resolved

`ServerIo` keeps `open(data): Promise<ServerParts>` and `listen(fetch, host, port)` (plan 3 lines 424 to 428), `ServerParts` only `options`; plan 4 keeps the `Exporters` and wrapped `Projects` of the last `open` in a closure of the `ServerIo` `main.ts` builds and runs `void exporters.start(await projects.names())` in its `listen` (plan lines 469 and 470); `serve` opens and then listens (plan 3 line 453), and `setup` opens without listening, so `setup` starts none; no shape changes.
The `start` call is left to review (M17, in part, as claimed).

### Task 10 over `world.ts` (M4) · Resolved

`ts/tests/api/round-trip.test.ts` over Task 8's `world.ts` (plan lines around 512 to 514), person `ada`, `FixedClock` moved past the store's dates; the script `ts/scripts/round-trip.ts` imports through `#…` names only, as the `front-door` rule for `scripts/` demands (`.dependency-cruiser.cjs` lines 33 to 38), with its own `Clock`, `importStore`, and one `exportStore` call.

## The other mismatches

- M5: `zeroTwoRepository(layout, extra = new Map())` writes extra texts through `encodeUtf8`; Tasks 2 and 10 pass `lodge/attachments/d-q59cdf/raw.bin` with U+DCFF U+DCFE. Resolved.
- M6: the Exports constraint names each task's readers; `GitDone`, `StoreRead`, `HookOutput`, `PreparedImport`, and `Imported` are module-local, each only the return or parameter type of an exported function, which `tsc` accepts without declaration output. Resolved.
- M7: Task 6's Consumes names `ZERO_TWO_STORE`, and the test publishes the eight files into `MemoryStore()`, whose constructor takes records (plan 2, Task 2). Resolved.
- M8: `export-target` answers an unknown project `no-project` first, with `unknown_project_is_no_project`. Resolved.
- M9: `setTarget` opens with `update heads set rev = rev where project = :project` (d-thvvzx), no row `NotFound`. Resolved.
- M11: "Aligned against" (plan line 17) and the ledger's alignment line (`…-progress.md:20`) both name plan 2 at 0244e79 and plan 3 at 9a25b93. Resolved.
- M12: the table is "from plans 1, 2, and 3", with `START`, the TOML steps, `log`, `toWire`, `issueSetupCode`, the ceremonies, the 422 body, `SoftAuthenticator`, and `world.ts`'s row. Resolved.
- M13: the merge list names `ts/package.json`, `ts/tests/parity.json`, and `ts/src/cli/settings.ts` (plan line 108). Resolved.
- M14: Task 11c edits `CLAUDE.md` lines 8 and 33, both of which name the frozen design documents in this worktree. Resolved.
- M17: `exportFailedLine` with `failed_line_names_the_project`; the `start` call untested, as stated. Resolved in part, as claimed.
- M18: `moved_record_edit_names_the_server` asserts the absence of the two phrases of `RECORD_TEXT`. Resolved.
- M19: `import-store.test.ts`'s `MemoryStore` has `people` `{ana}`. Resolved.
- Task 7's migration note now says `MIGRATIONS[3]`, since plan 3's Task 4 adds `MIGRATIONS[2]` (plan 3 line 346). Holds.

## Lane waits

Task 6 now reads Task 1's store (waits for Task 1); Task 8 reads Task 6's `exportFailedLine` (waits for Task 6) and plan 3's `SoftAuthenticator` and `issueSetupCode` (waits for plan 3); Task 10 reads Task 8's `world.ts` members (waits for Tasks 8 and 9). Each wait in the lanes table covers its reads.

## d-s83a6e

Its handles hold: `preflight.md` M1 to M4, M10, M15, and M16 say what it cites; plan 3 at 9ac93ac (and at 9a25b93) has no `asPerson` on `TestServer`, which it had at 7dfdf40, and names no table or helper for the person's 422; `ServerParts` has only `options`.
Its handles cite plan 3 at 9ac93ac rather than the pin 9a25b93, and the diff between them changes nothing it argues from (line references, `MIGRATIONS[2]`, `project-create`'s key check, and plan 2's schema tests).

## New findings

### N4-M1 · Minor · the round trip imports both layouts into one project `moved`

Handle: plan Task 10, `made_up_store_survives_import_and_export` ("for each layout … the person imports it … into a project made with `createProject("moved", …)`"); plan 2's `create` is "an insert that does nothing on an existing name" (plan 2, "Interfaces for plans 3 and 4"); Task 5's `importStore` refuses a project holding records with `Conflict`.
Failure: if both layouts run in one world, the second `createProject("moved", …)` creates nothing, and the second import answers `conflict`, so the test fails for a reason outside the code under test.
Fix: a fresh world per layout, or the projects `moved-checkout` and `moved-branch`.

## Files read

`plan-fix-4.md`; `preflight.md` (the mismatch list and the rows cited); `git diff cbedab8 484f69c` of the plan and ledger; d-s83a6e through `lodge show --reasoning --provenance`; plan 3 at 9a25b93 (Tasks 3, 4, 5, 6, 7a, and 8 by grep and excerpt) and `git diff 9ac93ac 9a25b93` of it; `git diff a035344 0244e79` of plan 2's plan; `ts/.dependency-cruiser.cjs` on `server-core`; `CLAUDE.md` lines 8 and 33.
