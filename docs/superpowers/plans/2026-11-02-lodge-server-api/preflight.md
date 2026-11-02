# Preflight scan of plan 3 (the API, sign-in, and the command)

Scanned: plan `docs/superpowers/plans/2026-11-02-lodge-server-api.md` at `9ac93ac` (branch `server-api`).
Plan 1: code at `/var/tmp/lodge-server-core/ts/src`, branch `server-core` at `7d5ecbc`.
Plan 2: text at `/var/tmp/lodge-server-store/docs/superpowers/plans/2026-11-02-lodge-server-store.md`, `origin/server-store` at `0244e79` (cited below as "plan 2 line N").
Plan line numbers are those of plan 3 unless a row says otherwise.
Verdicts: **match**, **mismatch** (numbered M-n, collected at the end), or **note** (a match with something a brief must say).
Not run: the builds themselves (nothing of tasks 1 to 9 exists yet); every claim below is read from text and code, and the library checks name the installed copy they read.

## Part 1: pairs of tasks sharing a file or an interface

| # | Earlier produces | Later consumes | Found |
|---|---|---|---|
| 1 | Task 1: `bunfig.toml`, `@simplewebauthn/server` 14.0.3 and `smol-toml` 1.9.1 in `ts/package.json`, `"version": "0.3.0"`, both names in `ts/knip.json` `ignoreDependencies` (181-182) | Task 3 takes `smol-toml` out of `ignoreDependencies` (246, 288); Task 6 takes `@simplewebauthn/server` out (414, 461); Task 7a's `project.ts` and Task 8's `--version` read the version (536, 588) | match. `ignoreDependencies` exists as `[]` in `ts/knip.json` at 7d5ecbc. The probe's `@simplewebauthn/server` 14.0.3 typings accept `expectedChallenge` as a function and `requireUserVerification` |
| 2 | Task 2: `ts/src/cli/index.ts`, `"#cli"` in `imports` (193-194) | Task 3 modifies the same two files from lane B (246) | note, M-2. Lane B starts without `index.ts`, and `layoutViolations` (`ts/tests/structure/calls.ts:175`) fails a package without a front door, or `imports` that differ from the folders in `src`. Line 95 says the second to merge keeps both entries, which settles the merge but not Task 3's Files line ("Modify") |
| 3 | Task 2: `parse(argv, version): Command \| Exit`, `Command`, `ThreadCommand`, `Exit {kind, code, out, err}` (201-219) | Task 7a's `run` prints an `Exit` as it is and gives `ThreadCommand` to `runThread` (485-491) | match. Field names agree: `Command.add` has `files, importing, dryRun, attachments`, and Task 5's `add` body has `drafts, attachments, importing, dryRun`. `search` has `filters, limit` against Task 5's `query, filters, limit`. `ask` has `raises` against Task 5's `raises` |
| 4 | Task 2: `reply` and `close` carry `ref` (216-217) | Task 5's `reply` and `close` bodies name the field `thread` (390) | note. Task 7a (494) says only "as commands.py and threads.py run them"; the brief for 7a must say `thread: command.ref`. `Lodge.reply(thread, …)` takes a thread (plan 2 line 166), so Task 5 is right |
| 5 | Task 3: `CliError(message, exitCode 1\|2 = 2)`, `readSettings`, `repositoryRoot`, `serverOf`, `tokenOf`, `NO_SERVER`, `ProjectSettings {server, core, coreSettings}`, `readDraft`, `readExact` (253-268) | Task 7a's `run` and `client.ts` (491-496): root, settings, server, token, drafts read before settings for `add` | match on names and types. `ProjectSettings.core` is what `init` sends as `settings` to `project-create` (494, 393). M-3: `serverOf` and `NO_SERVER` have no test in Task 3 (285-286) and no carried test asserts the sentence (every `project()` writes `[server]`, 534) |
| 6 | Task 3: `CliError` exit codes 1 and 2 | Task 7a's client table (496, 545): `conflict` is `CliError(message, 1)`, every other kind exit 2, `check-failed` exit 1 by the command | match. lodge 0.2's `Conflict` is exit 1 and `LodgeError` 2 (plan 2 line 252) |
| 7 | Task 4: `Accounts`, `ServerSetup`, `Passkey`, `AgentToken`, `Projects.create(…, settings?)`, `settings`, `names`, `SqliteAccounts(database, clock)` (303-343) | Task 5: `ApiOptions.accounts`, `projects`; `world.ts` builds `SqliteAccounts`, `accounts.setUp({origin, person, at})`, `projects.create("work", "ada")`, `settings` null for an unknown project (371, 394, 398) | match. `tokenId` is named by Task 4 (312) as "from tokenId (Task 5)"; the Task 4 tests write their own id strings, so no forward dependency |
| 8 | Task 4: the nine account event kinds, a migration after plan 2's last, `user_version` raised (344-345) | Plan 2's `ts/tests/store/database.test.ts` (`schema_is_created_once` expects `user_version` 2, `schema_1_is_migrated_to_2` opens at 2; plan 2 lines 599, 601) | **mismatch M-1.** Plan 2's last migration is `MIGRATIONS[1]` (plan 2 line 589), so Task 4's is `[2]` and `user_version` 3. Both plan 2 tests fail after Task 4, and its Modify line (294-297) does not list `database.test.ts` |
| 9 | Task 4: `Projects` gains `settings` and `names`; the `project` event body becomes `{ owner, settings }` (344) | Plan 2's `projects.test.ts` `create_writes_the_project_and_its_owner` ("two events in order", plan 2 line 433) and `rebuild.test.ts` | note. Plan 2 does not say whether the first asserts the body; if it asserts `{ owner }`, the added `settings: {}` breaks it. The brief for Task 4 should say "settings default `{}` and the carried assertion is adjusted if it reads the body" |
| 10 | Task 4: `appendEvents(tx, project, actor, at, events)` and `json` of `store/events.ts` (plan 2 lines 393-395), `applyEvent` module-internal | Task 4's own `store/accounts.ts` and `events.ts` (295-296, 300) | match. "Consumes `applyEvent`" (300) is an edit to the same module, which Task 4 may do. `NewEvent` is not exported, so `accounts.ts` builds its events as literals |
| 11 | Task 4: `Accounts` methods | Task 6: `setupCodeValid`, `spendSetupCode`, `issueSetupCode`, `passkeys`, `addPasskey`, `usePasskey`, `startSession`, `sessionExpiry`, `endSession`, `setUp`, `setup` (431-451) | match: every method Task 6 calls is in Task 4's interface, with the argument types it needs (hashes and stamps as `string`) |
| 12 | Task 5: `handler`, `ApiOptions`, `auth.ts`, `http.ts`, `operations.ts`, `index.ts`, `issueToken`, `hashSecret`, `tokenId`, `toWire`, `lodgesOver` (368-383) | Task 6 modifies `auth.ts`, `http.ts`, `operations.ts`, `index.ts` and uses `options.random`, `options.clock`, `options.accounts`, `options.log` (414, 431-441) | match. Every file Task 6 modifies is created by Task 5. Task 5 (395-396) already words the session branch "from Task 6", so its tests do not need it |
| 13 | Task 5: `toWire`, the error kinds, `Lodge-Version`, 422 body `{error, result}` (386-392) | Task 7a's `client.ts` and `fromWire` (495-499), `wire.test.ts` through `toWire` of `#api` | match. Kinds: usage 400, unauthorised 401, forbidden 403, not-found 404, no-project 404, conflict 409, check-failed 422, internal 500, against Task 7a's table (545) |
| 14 | Task 5: routing "POST /api/v1/<operation>"; "any other path is `not-found` (`nothing here`) until Task 9" (385) | Task 9: "any other `GET` stays `not-found`" (607) | note. Task 5 does not say whether the method check or the path check comes first for a `GET` outside `/api/v1/`. Task 9's "stays" needs path first (not-found), method second only under `/api/v1/` |
| 15 | Task 5: `world.ts` (398), the `FixedClock` handler world | Task 9's `page.test.ts` (613) and Task 6's tests | match. `world.ts` is a helper in `ts/tests/api/`; Task 9 is in lane D and needs 6, which needs 5 |
| 16 | Task 6: `issueSetupCode(options)`, `serverCommand`, `ServerIo`, `ServerParts`, `SoftAuthenticator` (`ts/tests/api/authenticator.ts`), the ceremonies and `token-issue`, `approve`, `held` (419-453) | Task 7a's `server.ts` (530): registers a passkey with `issueSetupCode` and `SoftAuthenticator`, issues a token through `token-issue`, approves through the session | match. `register-options` takes `setupCode` (432), the session cookie needs `Origin` equal to `https://lodge.test` (441), which `server.ts` must send. `me.setUp` means "a passkey exists" (437), as S1 expects (108) |
| 17 | Task 6: `serverCommand(argv, io)`, `ServerIo {out, err, open, listen}` (421-428) | Task 8's `main.ts` (583) and `listen` of `serve.ts` (579) | match. `listen(fetch, host, port): Promise<void>` has the same shape in both. `main` builds `ServerParts` as `{ options }` |
| 18 | Task 6: operations `me`, `register-options`, `register`, `sign-in-options`, `sign-in`, `sign-out`, `tokens`, `token-issue`, `token-revoke`, `projects`, `held`, `approve`, `decline`, `confirm` | Task 9's `page.js` (611) calls the first thirteen | match. `held` answers `{seq, at, by, kind, …}` with `drafts` as `{name, kind, title, statement, quote}` or `{name, problem, text}`, and Task 9's page (610) reads exactly those. M-5: the `text` of an entry or area draft (443) is not pinned |
| 19 | Task 7a: `run`, `Io`, `fromWire`, `Call`, `runThread` through `#cli`; `test server`, `project.ts`, `support.ts` | Task 7b: "as 7a"; the carried writing tests use `seed`, `approve`, `handEdit`, `stored`, `paths`, `standStill` (555-563) | match. `TestServer.approve` returns the IDs of the approval, which `threads.test.ts` and `add-import.test.ts` read (561, 563) |
| 20 | Task 7a: `ts/knip.json` `entry` gains `tests/e2e/support.ts` (469); parity rows for the 7a files | Task 7b takes it out (554); the table of late-read exports (43-45) | match. `document`, `entryText`, `areaText` are first read in 7b. At 7a they are read inside `support.ts` only, which `entry` covers. A probe at the scan showed that knip 6.42.0 does not report the exports of a file reached through `package.json` `imports` (such as `#cli`) without `includeEntryExports`, so the barrels need no entry line before Task 8 |
| 21 | Task 7a: `parity.test.ts` widened to a `changed` row of plan 2 or 3, a `dropped` list, `test_wheel.py` set back to `planned` (512-514) | Task 8 flips `test_entry_point.py` to `ported` and `test_wheel.py` to `changed` with `dropped installed_wheel_runs` (595) | match. At 7d5ecbc `parity.test.ts` checks `changed` rows of plan 1 only (`ts/tests/parity.test.ts`, `ported_files_exist`), `test_wheel.py` is `changed` with plan 3 and `ts/tests/e2e/binary.test.ts`, so the widening would read a file two tasks away; the plan's reset to `planned` is needed and correct |
| 22 | Task 7a: `ts/tests/parity.json` rows, 16 e2e test files and `project.ts`, `support.ts` | Plan 1's `parity.json`: 30 rows of plan 3, plus `test_thread_fix_paths.py` (plan 2 sets it to 3) | match. All 31 rows of plan 3's table (134-166) are in `parity.json` with the same `ts` paths; none missing, none extra. Python test names named by the plan (`check_and_gate`, `guide_says_waiting_first`, `version_works_anywhere`, `author_words_are_recorded_exactly`, the six `dropped` names, and the others) all exist in the Python files |
| 23 | Task 7a: `cli` front door and `Io`, `run` (477-491) | Task 8's `main.ts` calls `run(argv, io)` with `cwd`, `env`, `fetch`, `out`, `err`, `version` (584) | match: the six fields of `Io` are the six Task 8 passes |
| 24 | Task 8: `includeEntryExports` and `src/main.ts` in knip `entry` (590) | Task 9, rebased onto `server-api` after Task 8 (96, 617) | match. Task 9's own exports (`PAGE`, `SCRIPT`) are read by `http.ts`, and `index.ts` gains none (601, 617) |
| 25 | Task 5 and Task 9: `http.ts` | Task 9 adds two `GET` routes reading `PAGE` and `SCRIPT` of `page.ts` (602-607) | match. Task 9 is the only task that adds `GET`; Task 6 modifies `http.ts` for the cookie, and Task 9 (lane D, after 6) rebases on it |

## Part 2: each task against itself

| Task | Tests against code | Files created against files touched | Lane waits against what its tests import | Found |
|---|---|---|---|---|
| 1 | none (a check list, 186-188) | creates `bunfig.toml`; modifies `package.json`, `bun.lock`, `knip.json`; step 3 commits all four | none | match. Kysely 0.29.7 (plan 2) is 16 days old on 2026-11-02, `knip` 6.42.0 15 days, so `minimumReleaseAge = 1209600` does not refuse an already pinned package |
| 2 | `args.test.ts` goes through `parse` only (the `args.ts` API is not in Produces, 222), so it needs nothing beyond `#cli`; every message in the tests is one probe 6 shows | creates `args.ts`, `grammar.ts`, `index.ts`; modifies `package.json` `imports` | imports `#cli` and `#core` types; needs 1 only for the shared files | match |
| 3 | all 17 listed `settings.test.ts` tests and 5 `files.test.ts` tests have code in 253-282; `serverOf`, `NO_SERVER`, `ProjectSettings.coreSettings` are untested | modifies `src/cli/index.ts` and `#cli` as if they existed (246), while lane B runs beside Task 2 | imports `#cli`, `smol-toml` (1) | **M-2 (Files line), M-3 (untested `serverOf`)**. Otherwise match: `integer_forms_are_read` includes `99999999999999999999`, which `parseCoreSettings` accepts as the number 1e20 (`ts/src/core/settings.ts:49`) |
| 4 | 12 `accounts.test.ts` and 5 `project-settings.test.ts` tests against 303-347; `setup_code_is_spent_once` needs `Promise.all` over a store whose transaction opens with a write (347), which plan 2 line 191 gives | creates `app/accounts.ts`, `store/accounts.ts`; modifies `ports.ts`, `app/index.ts`, `projects.ts`, `events.ts`, `schema.ts`, `store/index.ts`, `front-door.test.ts` | imports `#store`, `#app`, plan 2's `FixedClock` (`ts/tests/app/fakes.ts`); waits for 1 and plan 2 | **M-1**: the migration changes `user_version` and plan 2's `database.test.ts` is not in Modify. |
| 5 | 8 + 5 + 13 + 7 tests against 368-404. `project_create_before_setup_is_usage` needs a world with no setup, but `world.ts` (398) sets the server up unconditionally and takes no option; `token_id_is_spelled_as_an_id`: bytes `0,31,32,33,255,10` give `0z01za` by `ids.ts:3,8-11`, as the test says | creates 8 files in `src/api`; modifies `package.json` `imports`; the tests add `world.ts` | imports `#api`, `#store`, `#app`, `ts/tests/app/fakes.ts`; needs 4 | note. `world.ts` needs an option (`setUp: false`) or the test builds its own handler; the brief should say which |
| 6 | 13 + 7 + 14 + 9 tests against 419-452. `challenge_lasts_5_minutes` and the 15-minute test move time with `FixedClock.sleep` (456), which exists (plan 2 line 265) | creates `passkeys.ts`, `session.ts`, `person.ts`, `setup.ts`, tests and `authenticator.ts`; modifies `auth.ts`, `http.ts`, `operations.ts`, `index.ts`, `knip.json` | imports `#api`, `#store`, `#app`, `@simplewebauthn/server` (1); needs 5 | match. `setup.test.ts` builds its own `open` (`ServerParts` is `{ options }`, 421); `setup_refuses_a_bad_origin` lists `http://127.0.0.1:8787`, `http://[::1]:8787`, which Task 3's `server.url` accepts for the command (277) and Task 6 refuses for the server (445), as it says. M-5: the `text` of an entry draft in `held` is not pinned |
| 7a | tests of 7a: 16 carried files, `client.test.ts` (8 tests), `wire.test.ts`, the parity test of `dropped`; the plan gives `seed`, `server.ts`, `project.ts` fully | creates 8 files in `src/cli` and `guide.md`/`text.d.ts`; modifies `index.ts`, `parity.json`, `parity.test.ts`, `parity-names.ts`, `thread-fix-paths.test.ts`, `knip.json`. Guide edits: the plan's line numbers 7, 19, 20, 24, 26, 29, 33, 34, 50, 55 name the right lines of `src/lodge/cli/guide.md` (checked), and the guide stays at 60 lines (+1 after line 7, -1 for line 20); the carried guide tests (`test_guide.py:16-62`) still find their phrases | imports `#cli` (2, 3), `#api` and `authenticator.ts` (5, 6), `#store`, `#app`; "Needs 2, 3, 6" (91) | match. `check_prints_unreadable_files_and_fails` is a third test of `test_check_and_gate.py` that the plan does not describe; it writes a new file (`d-zzzzzz-broken.md`), so a `handEdit` carries it. `thread-fix-paths.test.ts` `orphaned_thread_outputs` needs the `MemoryStore` itself (`store.files[…]`, `tests/app/test_thread_fix_paths.py:15-17`) and `wired(project())` (539) does not give it; the test writes `const store = project(); wired(store)` |
| 7b | `held.test.ts` and the ten carried files against 560-563; mutations named for each | modifies `parity.json`, `knip.json` (takes `support.ts` out), 7a's modules | as 7a, needs 7a | match |
| 8 | `binary.test.ts` (2 tests) and `environment.test.ts` (2) against 579-590; `main_clears_yaml_logging_first` reads `src/main.ts` | creates `main.ts`, `serve.ts`, tests; modifies `index.ts`, `package.json` (`build`), `knip.json`, `.gitignore`, `parity.json` and "for the names knip then reports" most of `src` | imports every package; needs 7b | note. `main.ts` writes through `process.stdout.write` and `process.stderr.write` (584), which `calls.ts:147` reports ("file writing outside git", `write` in `writes`) until plan 1's fix wave lands d-d0vca9; the plan's header (22) states that precondition and it is not yet true at 7d5ecbc (`docs/superpowers/plans/2026-11-02-lodge-server-core-progress.md:90`) |
| 9 | 7 tests against 609-612; `every_operation_the_script_names_exists` needs the operation names of Task 6 | creates 4 files; modifies `http.ts` only; `index.ts` gains none | imports `#api`, `world.ts` (5); "Needs 6" (93) | match. See pair 14 for the `GET` order |

## Part 3a: names consumed from plan 1 (`/var/tmp/lodge-server-core/ts`, 7d5ecbc)

All paths below are under `ts/`.

| # | Plan 3 line and name | Found in plan 1 | Verdict |
|---|---|---|---|
| 1 | 199, 231: `filters`, `Filters` (kind, scope, status default `current`, area, decidedBy) | `src/core/search.ts:18-27`; exported by `src/core/index.ts` (`type Filters`, `filters`). `filters(value: Partial<Filters> = {})` defaults status to `current` | match |
| 2 | 199: `Scope` | `src/core/model.ts:3-4` (const object and type) | match |
| 3 | 199, 215: `Raises` | `src/core/model.ts:127-128`, `"doubt" \| "question"` | match |
| 4 | 199, 226: `pyRepr` | `src/core/text.ts:76`, `pyRepr(s: string): string`, through `export *` | match |
| 5 | 249, 365: `parseCoreSettings(table)` | `src/core/settings.ts:35`; its first loop accepts only `store`, `hook`, `length`, `import` (line 37), so Task 3 passes it the two core tables alone (279) and checks `server` and unknown names itself (276), as written | match. M-6: it also accepts `store` and `hook` in a body sent to `project-create`, which Task 5 (393) passes to it unchanged |
| 6 | 249: `SettingsError` | `src/core/settings.ts:2` | match |
| 7 | 249, 371: `CoreSettings` | `src/core/settings.ts:20-23` (`length`, `importSources`) | match |
| 8 | 249: float and date refused "with lodge 0.2's sentence" | `settings.ts:47-48` (`typeof value !== "number" \|\| !Number.isInteger(value) \|\| value < 1`, message `length.<key> must be a positive whole number`); `settings.ts:56-58` (`import.sources must be a list of file names`) | match: a `null` from Task 3's conversion fails both checks with those sentences |
| 9 | 300, 365: `compareStamps` | `src/core/stamps.ts:45`, `(a, b) => number` | match |
| 10 | 418: `parseDraft(source, text)` | `src/core/drafts.ts:28`, `Draft \| Problem` | match |
| 11 | 418, 443: `recordFromDraft(draft, id, date, area)` | `src/core/drafts.ts:42-47`, `(Draft, string, string \| null, string \| null)`, `Record \| Area \| Problem`. `withId` (`drafts.ts:65`) throws when the header's `id` differs from the given one, `withDate` (`:73`) refuses a header `date` unless `imported_from` is there, `name()` (`:82`) takes the header's `area`/`name` when none is given and throws `a new <kind> draft needs a '<key>' key` when neither exists | match. The plan's placeholders (`d-000000`, `s-000000`, area `held`, area `null` for decision and area) fit: `isId` accepts `0` (`ids.ts:3-7`); an area draft needs its own `name` (`:82-90`), which the plan's `null` leaves to the header |
| 12 | 443: `headers.ts:56,61` | `src/core/headers.ts:56` (`readId(requireField(header, "id"))`), `:61` (`readDate(requireField(header, "date"), …)`) | match |
| 13 | 443: `Problem` and its message | `src/core/model.ts:113-119`, field `message` | match |
| 14 | 443: decision fields `title`, `statement`, `quote {text, where, when}` | `src/core/model.ts:24-43` (`statement`, `reasoning` separate, `quote: Quote \| null`), `:7-11` | match. `SpecEntry` (`:77-85`) has `statement` and no `text`, `Area` (`:98-105`) has `intro`; see M-5 |
| 15 | 474: `formatLevel1`, `formatLevel3`, `WORD_CLASS` | `src/core/views.ts:124`, `:127`; `src/core/text.ts:1` (`"[\\p{L}\\p{N}_]"`) | match |
| 16 | 474 and ports of `output.py`: `CheckResult`, `Level1`, `Problem`, `Thread`, `ThreadState`, `Raises` (the `lodge.core` imports of `output.py:7`, `thread_output.py:5`, `threads.py:11`) | `check-state.ts:7`, `views.ts:13`, `model.ts:113,143,129,127`, all through the front door | match |
| 17 | 563: `load`, `tree` | `src/core/snapshot.ts:44`, `:17` | match |
| 18 | 397, 404: `mintId` "each byte modulo 32", alphabet `0123456789abcdefghjkmnpqrstvwxyz`, prefix `d`, `s`, `q` | `src/core/ids.ts:3`, `:8-11` (`mintId(prefix: "d" \| "s" \| "q", entropy)`, reads six bytes). `tokenId` of `0,31,32,33,255,10` is `t-0z01za` as the test says (checked by hand against the alphabet) | match |
| 19 | 22, 29, 31: structure rules, `layoutViolations`, one file at the root of `src` | `tests/structure/calls.ts:175-191` (`src/main.ts` allowed; `imports` must equal the package folders, one `#<pkg>` each); `tests/structure/table.ts` lists `api`, `cli` with `app` and `core` | match. No rule stops `api` or `cli` using `node:crypto` or `smol-toml`; `network-confinement` (`.dependency-cruiser.cjs`) limits `node:net`, `http`, `https`, `tls`, `dgram` to `api`, and `Bun.serve` is limited to `api` (`calls.ts:151-155`) |
| 20 | 22: "plan 1's fix wave lands d-d0vca9 in `calls.ts`" | not yet: `calls.ts:147` still reports every `write`, so `process.stdout.write` in `main.ts` and `ApiOptions.log` would be reported "file writing outside git". The ruling is in plan 1's ledger (`docs/superpowers/plans/2026-11-02-lodge-server-core-progress.md:90`) | precondition, not a mismatch: Task 8's gate cannot be green until the fix wave has merged |
| 21 | 16, 20, 453, 590: plan 1's files "under `docs/superpowers/plans/done/`" | `docs/superpowers/plans/done/` holds `2026-10-29-lodge*` only; plan 1 is still open at `docs/superpowers/plans/2026-11-02-lodge-server-core*` | precondition, as line 16 says ("where plan 1's last task moves them before this plan builds") |
| 22 | 453: `SoftAuthenticator` of plan 1's probe 2 and the `ArrayBuffer` typing of probe 20 | `docs/superpowers/plans/2026-11-02-lodge-server-core/probes/tests/passkey.test.ts:18` (`class SoftAuthenticator`, flag bytes `0x45` and `0x05`, which include UV, so the "clear UV" option is a one-byte change); probes 1, 2, 11, 20 of `probes.md` are the items the plan cites | match |
| 23 | 63, 205, 546: `ts/knip.json`, `ts/package.json`, `ts/tests/parity.json`, `parity.test.ts`, `parity-names.ts`, `scripts/check-ts.sh`, `scripts/check.sh` | all present; `knip.json` has `"ignoreDependencies": []` and `"entry": ["tests/**/*.test.ts", "scripts/*.ts"]`; `parity.test.ts` has no `dropped` and checks `changed` rows of plan 1 only | match; `dropped` and the widening are Task 7a's work (512-514) |
| 24 | 258, 586: `ts/package.json` `"version"`, `import pkg from "../package.json" with { type: "json" }` | `tsconfig.json`: `module` `Preserve`, `moduleResolution` `bundler`, which resolve JSON imports; `include` is `src`, `tests`, `scripts` | match |
| 25 | 11: smol-toml 1.9.1 `integersAsBigInt` | installed copy at 1.9.1 (`/var/tmp/lodge-core-finalrev/ts/node_modules/smol-toml/dist/parse.d.ts:46`) has the option | match |
| 26 | 432, 435: @simplewebauthn/server 14.0.3 | installed copy (14.0.3): `expectedChallenge: string \| ((challenge) => boolean \| Promise<boolean>)`, `requireUserVerification`, `userID?`, `attestationType`, `excludeCredentials`, `authenticatorSelection`; counter rule `verifyAuthenticationResponse.js:186-192` throws when either counter is above 0 and the new one is not above the stored one | match. Note: the library also refuses an equal non-zero counter, which the plan words as "go back" (435); harmless |

## Part 3b: names consumed from plan 2 (text of `origin/server-store` at `0244e79`)

| # | Plan 3 line and name | Defined in plan 2 | Verdict |
|---|---|---|---|
| 1 | 116: `new Lodge(store, clock, ids, settings, actor)` | plan 2 line 154 | match |
| 2 | 116, 390: `search(query, filters, options?: {limit})`, `show(ref, {reasoning, provenance})`, `waitingAll()`, `timeline({limit})`, `spec({area})`, `problems()`, `check(gate)`, `draft(ref)`, `mint(prefix)` | lines 155-163 | match, each defaulted parameter in an options object (line 88); `check(gate: boolean)` positional as plan 3 says (390) |
| 3 | 390: `add(drafts, {importing, dryRun, attachments})`, `ask(ref, raises, by, text, {where, when})`, `reply(thread, by, text, {where, when})`, `close(thread, by, {text, where, when})` | lines 164-167 | match. `commit` is an option plan 3 never sends, as lodge 0.2's `run_thread` does not (`src/lodge/cli/threads.py:97-103`) |
| 4 | 390, 443: `threads()`, `thread(ref)`, `threadsWaiting()`, `confirm(ids, words, {area})`, `behindArea(name)`, `held()`, `approve(seq)`, `decline(seq, reason)` | lines 168-175 | match |
| 5 | 116: `LodgeError`, `NotFound`, `Conflict`, `StaleList`, `Forbidden` | lines 140-144; exit codes 2, 2, 1, 1, 2 (line 252, 559) | match |
| 6 | 116, 389: `coreSettings(table)` words a bad table as `.lodge.toml: …` | lines 145, 253 | match. It shares its name with `#core`'s `coreSettings` (`settings.ts:24`); Task 5 imports only the `#app` one and `CoreSettings`, `parseCoreSettings` from `#core`, so no alias is needed |
| 7 | 116, 124: `Added` with `awaits`, `held`; `AddOutcome.HELD` = `"held for approval"`; `Written` with `awaits`, `held`; `Held`, `Approved` | lines 147-150, 137, 618, 645 | match. Results are those of `results.py` (`ids`, `outcome`, `check` first), so Task 7a's `approve` helper reading `added.ids` or `written.ids` fits (`results.py:46-62`) |
| 8 | 116: `Clock` (`now(): Now`, `{epochMs, offsetMinutes}`, `sleep(seconds)`), `IdSource`, `Store`, `Projects` (`create`, `members`, `addMember`, `storeFor(project, actor)`) | lines 92-94, 101-111, 117-122 | match. `storeFor` is synchronous, as Task 7a's `handEdit` uses it (532) |
| 9 | 116: `Actor`, `person(name)`, `agent(role)`, `actorText`, `stampOf(now)` | lines 112-115, 123 | match. `agent(role?: string \| null)` takes the token's `role: string \| null` (Task 4, 316) |
| 10 | 116, 119: `Store.trees()` (one tree twice), `Store.attachmentTexts()`, `Store.publish` refusing a changed decision, running no other check | lines 103-104, 107, 190, 192, 422-424 | match |
| 11 | 117: `FixedClock(start: Now = START, stepMs = 0)` with `calls`, `slept`, `now()`, `async sleep(seconds)` that moves the clock; `CountingIds`; `START` at `2026-10-29T09:30:00+01:00` | lines 262-266 | match. `START` is 09:30 at +01:00, as `world.ts` (398) says |
| 12 | 117, 539: `project()` and `wired(store, clock, ids, actor = person("author"))` of `ts/tests/app/support.ts` | line 296 (`project({ staged = false } = {})`), line 560 (`wired` with the actor) | match. `project()` returns `MemoryStore`, whose `files` is a `Map` (line 264), which `orphaned_thread_outputs` edits |
| 13 | 118: `openDatabase(path)` (`":memory:"` or a file), `SqliteProjects(database, clock)`, `SqliteStore`, `rebuild`, `applyEvent` cases | lines 180-183, 187-189, 385, 397 | match. `openDatabase` is `async` (line 180), so `world.ts` and `main.ts` must `await` it; Task 5 (398) and Task 8 (583) do not say so, which is a reading, not a mismatch |
| 14 | 118: `applyEvent` inserts `heads` only for a `project` event and never upserts, so account events of project `""` add no row | line 189, 397; plan 2's test `an_event_of_no_project_adds_no_head` (line 403) | match |
| 15 | 118, 347: a store transaction that reads before it writes opens with a write (d-thvvzx), a racing `create` throws `Conflict` | line 191, 426 | match. For account events (project `""`) the opening write `update heads … where project = ''` matches no row; Task 4's note (347) leaves the form of the opening write to the builder |
| 16 | 120: held relay (Task 12c): `ask`, `reply`, `close` by an agent with `by` naming a person are held; `Written` `HELD`, `awaits`, `held`, `ids`; a held message changes no waiting state | lines 647, 651 | match |
| 17 | 121: `HeldAdd` fields (`kind`, `person`, `by`, `drafts`, `attachments`, `importing`, `message`), `HeldMessage` fields (`operation`, `ref`, `raises`, `text`, `where`, `when`), `Held = HeldDraft & {seq, at}`, `approve` answers `{kind, added \| written}`, `NotFound("nothing is held under number <seq>")`, `Forbidden("only <person> approves this; nothing was written")` | lines 126-137, 625 | match |
| 18 | 122: `Tree.people` is the owners; `confirm` refuses a non-owner | lines 561, 566 | match |
| 19 | 123: name patterns, `author` as a person keeps lodge 0.2's words | lines 193, 563 | match |
| 20 | 124: an agent's add of a decision `decided_by` a person is held whole; a dry run names who approves | lines 619-621 | match. Plan 3's note line (498) `note: <awaits> approves this add before it is current` reads `Added.awaits` on a `DRY_RUN` outcome, which plan 2 provides (621) |
| 21 | 125: `thread-fix-paths.test.ts` with two `test.todo`s, row plan 3 | lines 62, 340 | match |
| 22 | 126: "what this plan adds to plan 2's packages is Task 4's" | `Projects` in line 117 has four methods; `SqliteProjects` line 425-430; no other implementor of `Projects` exists in plan 2 (searched), so adding `settings` and `names` to the interface breaks no other class | match |
| 23 | 114: "Aligned against plan 2 at `61f87ad`" | plan 2 is at `0244e79`; the ledger (33-35) records the later changes (a035344, R3-1), the header does not | mismatch M-4 (citation only; the body of 116-126 agrees with `0244e79`) |
| 24 | 625: `decline(seq, reason)` with an empty reason refused, `LodgeError("a reason is required; nothing was written")` | line 626 | match. Task 6's `decline` (443) and the page's "asks for a reason" (610) agree; no Task 6 test names the empty reason |
| 25 | 456, 458: `approval_runs_the_check_again` of plan 2's Task 12b | line 628 | match |
| 26 | 119 and 532: a hand edit may not rewrite a decision file, may add one | lines 190, 422, 434 | match. `handEdit` of a new `lodge/decisions/<id>-….md` file passes `publish`'s refusals (path under `lodge/`, not an existing decision file) |

## Count

Part 1: 25 rows.
Part 2: 10 rows.
Part 3a: 26 rows.
Part 3b: 26 rows.
Total: 87 rows, 7 mismatches (1 Important, 6 Minor), 5 notes for the briefs, 2 preconditions.

## Mismatches

**M-1 (Important). Task 4 changes `user_version` and breaks two plan 2 tests it does not list.**
Plan 3 lines 292-297 (Task 4 Files), 344-345 (the migration "raising `user_version`").
Plan 2's migrations are `MIGRATIONS[0]` (plan 2 line 387) and `MIGRATIONS[1]` (line 589), so plan 2 ends at `user_version` 2.
Plan 2's `ts/tests/store/database.test.ts` has `schema_is_created_once`, which expects 2 (plan 2 line 601), and `schema_1_is_migrated_to_2`, which opens a version-1 file and expects 2 (line 599).
Task 4 adds `MIGRATIONS[2]`, so both fail after it, and the gate of Task 4 fails with them.
Fix: add `ts/tests/store/database.test.ts` to Task 4's Modify list, say the expected version is 3 and that `schema_1_is_migrated_to_2` gains a case (or a sibling test) ending at 3 with the account tables present.

**M-2 (Minor). Task 3's Files line says "Modify `ts/src/cli/index.ts`" for a file its lane does not have.**
Plan 3 lines 243-247 against 85-95 (lane B beside Task 2) and `ts/tests/structure/calls.ts:175-191` (a package without `index.ts`, or `imports` that differ from the folders, fails the structure test).
Fix: "Create or modify `ts/src/cli/index.ts` and `package.json`'s `imports`" in Task 3, so the brief tells the builder to create both when Task 2 has not merged.

**M-3 (Minor). `serverOf` and `NO_SERVER` are produced and untested.**
Plan 3 lines 261-262 and 280 against the tests at 285-286: no test calls `serverOf` on a settings value without a server, and no carried test does either (`project()` always writes `[server]`, line 534).
The sentence of d-1zmfdr is therefore unpinned, against the test-first rule of `CLAUDE.md`.
Fix: add `server_is_needed` to `settings.test.ts` (a `ProjectSettings` with `server: null`: `serverOf` throws `CliError` with `NO_SERVER`, exit 2).

**M-4 (Minor). The plan 2 alignment hash is stale.**
Plan 3 line 114 says "Aligned against plan 2 at `61f87ad`"; `origin/server-store` is at `0244e79`, and the ledger (33-35) records the changes since (a035344, R3-1) that the header does not.
The names of lines 116-126 agree with `0244e79`.
Fix: cite `0244e79` in line 114 and in the ledger's alignment line.

**M-5 (Minor). The `text` of an entry or area draft in `held` is not pinned.**
Plan 3 line 443 gives an entry's or area's draft as `{name, kind, title, text}` with "`text` the draft's text", and a problem draft as `{name, problem, text}` with the raw file text.
A `SpecEntry` has `statement` and no `text` (`ts/src/core/model.ts:77-85`), an `Area` has `intro` (`:98-105`), and `Draft.body` is the draft's body (`drafts.ts:21-27`).
The test `held_shows_the_drafts_as_core_reads_them` (458) checks that the entry "answers its `title` and `text`" without a value, and Task 9's page prints it (610).
Fix: state which (`Draft.body`, the entry's `statement` or the area's `intro`, or the raw file) and give the test its expected value.

**M-6 (Minor). `project-create` stores whatever `parseCoreSettings` accepts.**
Plan 3 line 393 passes the body's `settings` to `parseCoreSettings` and stores it unchanged; `ts/src/core/settings.ts:37` accepts the names `store` and `hook` without checking them, so a body `{"store": {...}}` is stored, though Task 3 (276) makes `[store]` an unknown section on the command's side.
No behaviour reads it, so the cost is a stored table nothing uses.
Fix: Task 5 keeps only `length` and `import` from the body (and `project_create_checks_the_settings` gains a case for a `store` key), or says the server stores the table as sent.

**M-7 (Minor). Python line handles that do not match this tree (`src/lodge`, bf22731, unchanged since).**
- Plan 229: `src/lodge/cli/parser.py:137` for `isdecimal`; it is at `:153`.
- Plan 586: `src/lodge/main.py:31-32` for `datetime.now().astimezone()`; it is at `:29-30`. `src/lodge/main.py:39` for `secrets.token_bytes(8)`; it is at `:38`.
- Plan 443: `src/lodge/core/apply.py:136` for the entry's area taken from the tree; the assignment is `:137` (`:127-137` is the block).
- Plan 492: `src/lodge/cli/commands.py:73-75` for the drafts read before the settings; it is `:71-73`.
- Plan 496: `commands.py:107` for exit 1 on a failed check is `:104-105`; `threads.py:103-105` is `:104-106`; plan 494's `commands.py:111-119` is `:115-122`.
- Plan 230: `src/lodge/cli/threads.py:68-81` for `_message_command`; it is `:71-82`.
- Plan 276: `src/lodge/core/settings.py:31-37` for the words of `parse_core_settings`; they are `:30-35`.
- `docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md:33` still names d-pmaw3a, which d-j28rp0 replaced.
Fix: replace the handles; none changes a decision of the plan.

## Notes for the briefs (matches that need a sentence)

- N-1 (pair 4). Task 7a's brief: `reply` and `close` send `thread: command.ref`; `ask` sends `ref`.
- N-2 (pair 9). Task 4's brief: `create` without settings writes `settings: {}`; adjust plan 2's assertion if it reads the `project` event's body.
- N-3 (pair 14). Task 5's brief: a `GET` outside `/api/v1/` is `not-found` (path first), and `post_only` tests a `GET` under `/api/v1/`; Task 9 relies on it.
- N-4 (Part 2, Task 5). `world.ts` needs an option for a server not set up (`project_create_before_setup_is_usage`), or that test builds its own handler.
- N-5 (Part 2, Task 7a). `orphaned_thread_outputs` edits `store.files[…]`, so the test keeps the `MemoryStore` (`const store = project()`, then `wired(store)`), not `wired(project())` as line 539 words it; `openDatabase` is `async`, so `world.ts`, `server.ts`, and `main.ts` await it.

## Preconditions (not mismatches)

- P-1. Plan 1's fix wave must land d-d0vca9 in `ts/tests/structure/calls.ts` before Task 8's gate: at `7d5ecbc` `calls.ts:147` reports `process.stdout.write` and `process.stderr.write`.
- P-2. Plan 1's files move to `docs/superpowers/plans/done/` before this plan builds (line 16), and plan 2 merges into `server-api` before Task 4 (79, 98-101); the coordinator's diff of "Names consumed from plan 2" (101) against the merged code is the check for lines 116-126, which this scan read from plan 2's text only.

## Files read

Plan 3 (whole), its ledger, `probes.md` (items 1 to 8), `docs/superpowers/specs/2026-11-02-lodge-server-design.md` (lines 49, 55, 66, 72, 75, 79, 80, 192, 213), `docs/research/2026-11-02-server-feasibility.md` line 43.
Plan 2: lines 1-30 by search, 84-296, 330-366, 368-440, 479-510, 551-660 (Tasks 1 to 3, 6, 7a, 7b, 9 in part, 11, 12a, 12b, 12c).
Plan 1 code: `ts/src/core/{index,search,drafts,settings,ids,stamps,model,snapshot,views,text,headers}.ts`, `ts/tests/structure/{calls,table}.ts`, `ts/.dependency-cruiser.cjs`, `ts/package.json`, `ts/knip.json`, `ts/tsconfig.json`, `ts/biome.json`, `ts/tests/parity.json`, `ts/tests/parity.test.ts`, `ts/tests/parity-names.ts`, `scripts/check-ts.sh`, plan 1's probe `passkey.test.ts` and its ledger line 90.
Python (this tree): `src/lodge/app/{lodge,results,reads}.py`, `src/lodge/cli/{commands,threads,parser,guide.md}`, `src/lodge/main.py`, `src/lodge/core/{apply,settings}.py`, `src/lodge/gitstore/{setup,settings,errors}.py`, `tests/e2e/*.py` (the 31 rows' files, read in part by grep), `tests/app/{support,test_thread_fix_paths}.py`, `tests/test_wheel.py`.
Installed copies: `@simplewebauthn/server` 14.0.3 typings and `verifyAuthenticationResponse.js`, `smol-toml` 1.9.1 typings, knip 6.42.0 (a scratch probe, since removed).

Not read: plan 2's Tasks 3 (beyond the interface lines), 4, 5, 8, 10, 13, 14 in full, plan 4, the plan 3 review and fix files under `docs/superpowers/plans/2026-11-02-lodge-server-api/` (`plan-review-*`, `plan-fix-*`, `plan-recheck-*`, `planner-*`), the Python viewer and hook code, and the bodies of `tests/e2e` files outside the rows quoted above.
Not run: no task of plan 3 exists, so no test, gate, or build of it was run; the `bun`/`tsc` checks that depend on plan 2's code were not run, since plan 2 is a text.
