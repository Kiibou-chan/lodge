Read `CLAUDE.md` in this worktree first, then the plan header, "Global Constraints", "Exports read in a later task", "Calls made", and "### Task 8" in full in `docs/superpowers/plans/done/2026-11-02-lodge-server-api.md` (your requirements, with the exact values to use verbatim), and `docs/superpowers/plans/done/2026-11-02-lodge-server-api/task-6-report.md` and `task-7a-report.md` for what `#api` and `#cli` provide.

Outcome: `ts/src/main.ts` is the composition root, `lodge` builds as one binary (`bun build --compile`), `listen` and `withoutYamlLogging` are exported through `#api`, and knip runs with `includeEntryExports` and reports nothing.

Scope: the files of the plan's Task 8 "Files" list; `ts/src/core/*.ts`, `ts/src/app/*.ts`, `ts/src/store/*.ts`, `ts/src/cli/*.ts`, `ts/src/api/*.ts`, and the test files knip names change only to remove, or to tag `/** @public */`, the exports knip then reports (d-amxk94); the structure checks in `ts/tests/structure/` are never loosened.
`openDatabase` is async: `main.ts` awaits it.
`lodgesOver` is shared with the tests; keep its name and signature.
The sandbox rule holds: no test in the gate opens a socket; the compiled-binary end-to-end run (`LODGE_E2E_BINARY`) and S1 are the coordinator's.
Modules stay at 300 lines or fewer; Biome runs with `--error-on-warnings`; never `bun add`; never edit earlier briefs, reports, or reviews.

Evidence: the plan's Task 8 bullets; plan 4 (`origin/server-import`) consumes names this plan produces, so none of them is renamed, removed, or untagged: those in the table below get `/** @public */` in the module that defines them where nothing in this branch reads them (probe 4 of `probes.md`), and the report lists the three kinds of knip finding (removed, tagged public, test export losing `export`).
Plan 4's "Names consumed", as it stands now (names that live in plan 3's tasks matter here; the rest need no change):

| Name | From | Used by |
|---|---|---|
| `Clock` (`now()` giving `Now { epochMs, offsetMinutes }`, `sleep(seconds)`), `stampOf(now)` | plan 2, Task 2, `#app` | 5, 6, 7, 8 |
| `Store` (`trees()` as `[current, published]`, `attachmentTexts()`, `publish(base, writes, message, approves?)`, `hold`, `held`, `decline`, `commit`, `freshness`, `gate`), `PublishOutcome`; `publish` refusing a path holding a surrogate and a changed decision file (d-j28rp0) | plan 2, Tasks 2, 7b, and 12a, `#app` | 5, 6 |
| `Actor`, `person(name)`, `agent(role)`, `Role`, `Projects` (`members(project)` in code-point order, `storeFor(project, actor)`, `create`, `addMember`) | plan 2, Task 2, `#app` | 5, 6, 8 |
| `ts/tests/app/front-door.test.ts`'s `front_door_exports_nothing_else` and its list of allowed additions | plan 2, Task 6 | 4, 5, 6 |
| `Projects.create(project, owner, settings)`, `Projects.settings(project)` (null for an unknown project), `Projects.names()` | plan 3, Task 4, `#app` and `#store` | 8 |
| `LodgeError`, `NotFound`, `Conflict`, `Forbidden`, `coreSettings(table)` | plan 2, Tasks 2 and 11, `#app` | 2 to 9 |
| `decodeUtf8`, `encodeUtf8` | plan 2, Task 7a, `#core` (`text.ts`) | 2, 3 |
| `Tree.people` (the project's owners), `tree()` defaulting `people` to `{author}`, `parseThread(path, text, people?)` and `writeThread(thread, people?)` with `people` defaulting to `{author}` (d-vwsnz5) | plan 2, Task 10, `#core` | 5 |
| `checkChange(published, after, settings, now)`, `checkState`, `load`, `tree`, `parseCoreSettings` | plan 1, `#core` | 1, 5 |
| `LodgeDatabase`, `openDatabase`, `SqliteProjects`, `applyEvent`'s cases in `ts/src/store/events.ts` | plan 2, Tasks 7a and 7b, `#store` | 7, 8 |
| `FixedClock` (`slept`), `START` (2026-10-29T09:30:00+01:00), `MemoryStore(items, { staged, people })` (`publishes`), `CountingIds` | plan 2, Tasks 2 and 11, `ts/tests/app/fakes.ts` | 5, 6 |
| `ApiOptions` (`projects`, `lodgeFor`, `clock`, `log`), `lodgesOver(projects, clock, ids)`, `handler`, `toWire`, `issueSetupCode(options)`, the `register-options` and `register` operations, the person's operations of `ts/src/api/person.ts` and their `forbidden` sentence, the session cookie `lodge_session` with the server's `Origin`, the 422 body `{"error": {"kind": "check-failed", "message": "the check failed"}, "result": …}` | plan 3, Tasks 5 and 6, `#api` | 8 |
| `SoftAuthenticator` of `ts/tests/api/authenticator.ts` | plan 3, Task 6, tests | 8 |
| `Accounts` (`setup()` with `person`), `project-create` making the person the project's owner through `Projects.create` | plan 3, Tasks 4 and 5 | 8 |
| `world.ts` (the API's test world: person `ada`, `FixedClock`, `log`, building `ApiOptions`) | plan 3, Task 5, tests | 8, 10 |
| `Io`, `run(argv, io)`, `parse`, `Command`, `readSettings`, `CliError`, `settings.test.ts`'s `hook_is_left_alone`; `readSettings`' parsing and conversion steps (smol-toml with `integersAsBigInt`, a `bigint` made a number, a float or a date made `null`), which Task 8 factors into `tomlTable` in the same file | plan 3, Tasks 2, 3, and 7a, `#cli` | 8, 9 |
| `ts/src/main.ts` (`serverCommand`'s `open(data)` and `listen`, the command's `Io`), `ServerIo`, `ServerParts { options }` | plan 3, Tasks 6 and 8 | 8, 9 |
| `grammar.test.ts`'s `help_lists_every_command` and `every_command_has_help`, `ts/tests/e2e/help-lists-every-command.test.ts`, and `parity.json`'s `dropped` | plan 3, Tasks 2 and 7a | 9 |


Test-first: write `ts/tests/e2e/binary.test.ts` and `ts/tests/api/environment.test.ts` as the plan's Step 1 names them; run `cd ts && bun test tests/e2e/binary.test.ts tests/api/environment.test.ts` and see them fail before the code.
See `main_clears_yaml_logging_first` fail against a mutation that moves the call below an import-time statement, and `yaml_logging_variables_are_cleared` against one that clears only one variable; revert.

Done when `sh scripts/check-ts.sh` exits 0 with knip reporting nothing, the parity rows flipped (`tests/test_entry_point.py` ported, `tests/test_wheel.py` changed with its `dropped`) and green again; write `docs/superpowers/plans/done/2026-11-02-lodge-server-api/task-8-report.md` (per file what changed, each test with its first failing output, the three kinds of knip finding with their names); commit with explicit paths as `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, and push `server-api-c`; do not run the Coordinator step (S1 and the gate of `scripts/check.sh`).
Unsettled design goes to the ask tool.
