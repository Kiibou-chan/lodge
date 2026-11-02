# Plan review, practice angle: plan 3, the API, sign-in, and the command

Plan `docs/superpowers/plans/2026-11-02-lodge-server-api.md` at `3e4c29c` on `server-api`, read from the builder's seat (Codex, one brief, no network, no sockets, read-only git index).
Written incrementally; findings first, then the files read.

## Findings

### B-1 (Blocking): the structure rule refuses every `.write(` outside `git`, so `main` cannot print the command's output

- Handle: plan line 539 has `main` pass `process.stdout` and `process.stderr` to `run`, and plan line 26 says `main` "neither writes files nor opens sockets itself"; `ts/tests/structure/calls.ts:43-46` on `origin/server-core` puts `write` in the set of file-writing calls, and `calls.ts:147-149` reports any call whose property name is in it, in any package but `git`, as `file writing outside git`.
- Verified: in the scratch worktree at `6cc1986`, a `src/main.ts` calling `process.stdout.write(text)` and an `src/api/index.ts` calling `process.stderr.write(...)` make `repository_has_no_violations` fail with `src/main.ts:2: file writing outside git` and `src/api/index.ts:2: file writing outside git`; `console.write` (Bun has it) and `Bun.write(Bun.stdout, …)` are caught by the same rule, and `console.log` adds a newline the command's texts already end with.
- Failure scenario: Task 8's builder writes `out: (text) => process.stdout.write(text)`, the structure test fails, and since the plan says raising a limit or adding an allowed edge "is the author's call" (plan line 27), Task 8 stops with BLOCKED after the whole main line has been built; or Codex evades the rule with `process.stdout.write.bind(process.stdout)` or a destructured alias the rule cannot see, which the review must then reject.
- Fix: settle it before the build, as an author ruling recorded in lodge (it changes a structure rule), that writing to the process's standard output and error is not file writing, allowed in `main` (and, if wanted, `api` for its log); add the change to `ts/tests/structure/calls.ts` with one allowed case and one refused case (`Bun.write` of a path in `main`) to Task 1 (the coordinator's) or to Task 8's Files, and say in Task 8 which call `main` uses.

### I-1 (Important): Task 8's `includeEntryExports` reaches every front door, and the plan exempts only `#core`'s names

- Handle: plan line 545 (and d-djh40k, plan line 50) removes "each export knip then reports", except a name of `__all__` of `src/lodge/core/__init__.py`, which gets `/** @public */`.
- Verified: in the scratch worktree at `6cc1986` with `"includeEntryExports": true`, knip reports unused exports of `src/cli/index.ts` as well as of `src/core/index.ts` (`Unused exports (11)`, `Unused exported types (12)`, among them `UNREAD src/cli/index.ts:5` and `Command src/cli/index.ts:3`), and also an export of a test file (`EXAMPLE tests/core/thread-files.test.ts:51`); so `#app` and `#store`, plan 2's front doors, are checked too.
- Failure scenario: at Task 8, `#app` exports names of `src/lodge/app/__init__.py`'s `__all__` that plan 2's `front_door_exports_every_python_name` requires (plan 2, line 333) and additions plan 4 relies on (`Role`, `minuteOf`; `#store`'s `rebuild` and `Tables`; plan 4's table at `origin/server-import:docs/superpowers/plans/2026-11-02-lodge-server-import.md:64-74`) that no file reads yet; the brief tells Codex to remove them, which breaks plan 2's front-door test (BLOCKED) or deletes names plan 4's tasks consume, found only when plan 4 builds.
- Fix: widen d-djh40k before the build: a name a front-door test requires (`#core`'s and `#app`'s `__all__`) or another plan's interface table names gets `/** @public */`, the rest is removed; list the files Task 8 may touch (`ts/src/app/*.ts`, `ts/src/store/*.ts`, plan 1's test files) under its Modify; or move `includeEntryExports` to plan 4's last task, after the last consumer exists.

### I-2 (Important): no "Exports read in a later task" table, so Task 7a's gate fails on `support.ts`

- Handle: plan 1's Global Constraints require a file whose export is first read in a later task to sit in `ts/knip.json`'s `entry` from the task that creates it to the task that reads it (d-tha8st; plan 2 carries the same table at its line 36); plan 3 has no such table, and Task 7a (plan line 498) ports `support.py` whole.
- Verified: `document` of `tests/e2e/support.py` is read only by `test_add_non_string_scalar_exits_2.py`, and `entry_text` and `area_text` only by the add tests (`grep -l` over `tests/e2e/test_*.py`), all Task 7b's; knip at `6cc1986` reports a test helper's export that no other file reads (`areaText function tests/e2e/support.ts:2:17` in the scratch probe), use inside its own file not counting.
  The same happens to `ThreadCommand`: plan line 188 exports it from `grammar.ts`, plan line 206 has `index.ts` export only `parse`, `Command`, and `Exit`, and knip then reports `ThreadCommand type src/cli/grammar.ts:2:13` (probed), at Task 2's gate.
- Failure scenario: Task 7a's builder sees knip fail on `document`, `entryText`, and `areaText`, and either drops the exports (Task 7b then edits `support.ts` outside its Files) or puts the file into `entry` without the plan saying when it leaves; Task 2's builder meets the `ThreadCommand` report and guesses.
- Fix: add the table: `tests/e2e/support.ts` into `entry` in Task 7a and out in Task 7b, both listing `ts/knip.json` under Modify; and have Task 2's `index.ts` export `ThreadCommand` too.

### I-3 (Important): S1 cannot run every carried test through the binary as written

- Handle: plan line 86 (S1: "every carried command test passes with the compiled binary"), plan line 497 (binary mode writes the loopback `http` URL into `.lodge.toml`), plan line 500 (`init` expects `created project … on <url>` and `init_when_the_server_cannot_be_reached` uses "a `fetch` that throws").
- Failure scenario: under `LODGE_E2E_BINARY`, `init_when_the_server_cannot_be_reached` cannot inject a throwing `fetch` into a separate process, so it either fails or silently passes against the live server; every expected line that names `https://lodge.test` (`init`'s output, `LODGE_TOKEN is not set; the person issues an agent token on <url>`) now reads `http://127.0.0.1:<port>`; and `client.test.ts` and `thread-fix-paths.test.ts`, which build their own `Call` or `fetch`, never touch the binary; S1's counts in the ledger then hide which tests ran the binary.
- Fix: in Task 7a, have `project.ts` expose `url` and make every expected line read it rather than the literal; name the tests that run in process only and skip them under `LODGE_E2E_BINARY` with `test.skipIf`, so S1 reports them as skipped; say in S1 that only `tests/e2e/*.test.ts` other than `binary.test.ts` run in binary mode, and that its ledger line gives pass and skip counts.
  For `init_when_the_server_cannot_be_reached` in binary mode, a URL on a port nothing listens on (`http://127.0.0.1:9`) gives the same sentence.

### I-4 (Important): the plan already disagrees with plan 2 at `7204ad3`, and nothing re-aligns it after plan 2's build

- Handle: plan line 365 builds `world.ts` with "plan 2's `FixedClock` … that `advance(seconds)` moves", and Task 6's time tests (plan line 423-424: 15 minutes, 5 minutes, 30 days) depend on it; plan 2 at `7204ad3` gives `FixedClock(start, stepMs)` with `calls`, `slept`, `now()`, and `sleep(seconds)` only (plan 2, line 242).
  Plan line 494 has `stored` and `paths` "read the current tree", but plan 2's tree lists attachments by path without their text (plan 2, line 392), which only `attachmentTexts()` gives (plan 2, line 394), and Task 7b's `attachment_lands_beside_the_decision_in_checkout_mode` reads `run.log`'s text (plan line 518).
  The planner report's answer to drift is "Task 4's brief follows the merged code" (`planner-report.md`, Concerns), which is not in the plan, and Tasks 5, 6, 7a, and 9 consume plan 2's names too; plan 4 is aligned to this plan at `3e4c29c` (`origin/server-import`, `6c6322c`), so drift cascades.
- Failure scenario: Task 5's builder finds no `advance`, adds one to `ts/tests/app/fakes.ts` (plan 2's file, not under Task 5's Modify) or uses `sleep`, which also grows `slept`; a rename during plan 2's fourteen tasks and their fix rounds (plan 1's own build renamed and re-exported names, ledger lines on d-qe513h and `checkResult`) reaches a Codex brief that names something that no longer exists.
- Fix: name `sleep(seconds)` as what moves `FixedClock`, and `attachmentTexts()` as what `stored` reads under `lodge/attachments/`; add an explicit coordinator step before Task 4's brief: after plan 2 merges into `server-api`, diff "Names consumed from plan 2" (plan lines 90 to 99) against the merged `ts/src/app/index.ts`, `ts/src/store/index.ts`, `ts/tests/app/fakes.ts`, `ts/tests/app/support.ts`, and plan 2's ledger rulings, and run a plan fix round on any mismatch (with plan 4 told), before any brief of Tasks 4 to 9 is written.

### I-5 (Important): `mintId("t", …)` does not type-check, and the fix is outside Task 5's files

- Handle: plan line 364 has `issueToken` make the ID `mintId("t", random(8))`; `ts/src/core/ids.ts:8` on `origin/server-core` is `mintId(prefix: "d" | "s" | "q", entropy: Uint8Array)`.
- Verified: `mintId("t", new Uint8Array(8))` in a scratch `src/api/index.ts` gives `TS2345: Argument of type '"t"' is not assignable to parameter of type '"d" | "s" | "q"'`.
- Failure scenario: Task 5's builder widens `core`'s type (a `core` change outside Task 5's Files, and outside lodge 0.2's `mint_id`, `src/lodge/core/ids.py:11`) or casts the prefix, either of which the review must then rule on.
- Fix: have `api` mint the token ID itself (`t-` and six characters of the same alphabet from `random(6)`, a small function in `tokens.ts`), or list the widening of `mintId` under Task 5's Modify with the reason.

### I-6 (Important): Task 7a is two review's worth, and its 41 carried tests are seen failing only by a missing module

- Handle: plan lines 432 to 506; Task 7a ports `commands.py` (122 lines), `output.py` (96), `thread_output.py` (48), and the running half of `threads.py` (108 in all), writes `client.ts` and `wire.ts`, builds the test server with passkey sign-in (`server.ts`), `project.ts`, and `support.ts`, changes the parity check (`parity.test.ts`, `parity-names.ts`, a new parity test), turns plan 2's two `test.todo`s into tests, and carries 16 files holding 41 Python tests (505 lines, counted with `grep -c 'def test_'` and `wc -l`); Step 2 expects them to fail because the modules do not exist.
- Failure scenario: the review must check byte parity of every output function, the client protocol, the harness, and 41 parity claims in one pass, and a carried test that asserts nothing specific still "failed first"; this is the pattern the brief names from plan 1 (carried tests proved only by whole-function throws), and Task 7b already answers it with named mutations while Task 7a does not.
- Fix: cut Task 7a in two: 7a (the client, `wire.ts`, `commands.ts` with `init`, `id`, `add`, and `guide`, `added_lines` only, the harness, the parity `dropped` mechanics, and the tests `before-init`, `outside-repository`, `malformed-settings`, `id`, `init`, `help-lists-every-command`, and `guide`, which need no other output) and 7c (the rest of `output.ts`, `thread-output.ts`, `threads.ts`, `search`, `show`, `spec`, `waiting`, `check`, their carried tests, and `thread-fix-paths`), with 7c's carried tests each seen failing against a named mutation as Task 7b's are; or move the parity `dropped` mechanics into Task 2, which touches nothing else of the parity table.

### I-7 (Important): the two pins are old enough, but `bun install` today resolves their dependencies to releases days old

- Handle: d-4psbdv ("Every dependency is pinned to an exact version published at least two weeks before it is added"; its reasoning: "time for a bad release to be noticed and pulled"); plan line 153 and probe 7 check only the two direct packages, and Task 1's Step 2 (plan line 157) only that `ts/package.json` holds no range.
- Verified: `npm view <package> time` gives smol-toml 1.9.1 2026-10-09 and @simplewebauthn/server 14.0.3 2026-09-25, both more than two weeks before 2026-11-02, as probe 7 says.
  But @simplewebauthn/server 14.0.3 asks for its fourteen dependencies with caret ranges (`bun.lock` of the probe install), and a plain `bun install` resolves `tslib` 2.9.1 (published 2026-10-30, three days old) and the `@peculiar/asn1-*` packages at 2.11.1 (2026-10-25, eight days old).
  Bun 1.3.14 honours `[install] minimumReleaseAge = 1209600` in `bunfig.toml`: the same install then resolves `tslib` 2.8.1 (2024-10-31) and `@peculiar/asn1-schema` 2.11.0 (2026-10-12), both offline-runnable afterwards (`bun test` of plan 1's passkey probe and `bun toml.ts` pass under `unshare -rn` with `bun install --offline`).
- Failure scenario: Task 1 commits a lock holding releases younger than the rule allows, which the rule exists to keep out, while the ledger line says the versions comply.
- Fix: Task 1 adds `ts/bunfig.toml` with `[install]` `minimumReleaseAge = 1209600` (two weeks in seconds) before `bun install`, lists it under Files, and its Step 2 checks the resolved versions in `bun.lock` against their publication dates; or pins the transitive versions with `overrides`; a ruling records whether d-4psbdv covers transitive packages, since plan 1's own install (Biome, knip, dependency-cruiser) was not checked that way either.

### M-1 (Minor): merging plan 2 into `server-api` conflicts in `ts/package.json` and `ts/bun.lock`, and the plan does not say who settles it

- Handle: plan line 63 (Tasks 4 to 9 need plan 2 merged into `server-api`); plan 2's Task 1 adds `kysely` on `server-store` (plan 2, line 203), this plan's Task 1 adds two packages and `"version"` on `server-api`, and both plans' lanes add `#app`, `#store`, `#cli`, and `#api` to the same `imports` object.
- Failure scenario: the merge stops on `bun.lock`, whose package lists both sides edit next to each other, and a hand-merged lock passes `bun install --frozen-lockfile` only by luck.
- Fix: in "Order and lanes", name the merge of plan 2 as a coordinator step outside the sandbox: keep both sides of `package.json`, regenerate `bun.lock` with `bun install` (under the age gate of I-7), check `--frozen-lockfile`, and run `sh scripts/check.sh` before Task 4's brief.

### M-2 (Minor): `binary.test.ts` leaves a 95 MB binary behind on every gate run

- Handle: plan line 543 builds into "a temporary folder" in `beforeAll`; probe 5 and my probe give 94,587,008 bytes per binary.
- Verified, for the sandbox question: `bun build --compile` needs neither network nor a writable home: under `unshare -rn` with `HOME`, `XDG_CACHE_HOME`, and `BUN_INSTALL_CACHE_DIR` on a read-only folder it compiled a `#cli`-importing `main.ts` in 345 ms, and the binary ran under `env -i PATH=/usr/bin:/bin`.
- Failure scenario: every `sh scripts/check-ts.sh` from Task 8 on, by every builder and by the coordinator, adds a binary to the temporary folder; a few dozen runs fill a small `/tmp`.
- Fix: `afterAll` removes the folder (`rmSync(dir, { recursive: true })`, allowed in tests).

### M-3 (Minor): `#api`'s `listen` is first run in the browser check

- Handle: plan line 534 (`listen`, `Bun.serve`), plan line 426 (`serve_listens_where_told` records a fake `listen`), plan line 497 (S1 serves through `project.ts`'s own `Bun.serve`, not `#api`'s), plan line 572 (S3, the plan's last step).
- Failure scenario: a fault in `serve.ts` or in `main.ts`'s `open` (a data file path, the real clock) is first seen after Task 9, in the browser, and costs a fix round on the main line after the lanes have merged.
- Fix: add to S1 a short coordinator check after Task 8: `dist/lodge server setup` with a scratch data file, `dist/lodge server serve` in the background, then `curl -s -X POST -H 'Content-Type: application/json' -d '{}' http://127.0.0.1:8787/api/v1/me` answers `{"result":{"setUp":false,…}}` with `Lodge-Version`.

### M-4 (Minor): plan 1's paths will have moved to `done/` before this plan builds

- Handle: CLAUDE.md ("Plan's last task merged → same branch `git mv`s plan, progress, folder to `docs/superpowers/plans/done/`"); plan line 19 (plan 1's Global Constraints by path), plan line 420 (`docs/superpowers/plans/2026-11-02-lodge-server-core/probes/tests/passkey.test.ts`), and every "plan 1, probe N".
- Failure scenario: Task 6's brief sends Codex to a path that no longer exists, and it searches or reconstructs the software authenticator.
- Fix: write the paths as they will be after plan 1's move (`docs/superpowers/plans/done/2026-11-02-lodge-server-core/…`), or have the coordinator's brief template rewrite them.

### M-5 (Minor): the API's log has no sink, so its test must spy on a global

- Handle: plan line 354 ("the error written to the server's standard error"), plan line 368 (`unexpected_error_is_internal_without_detail` checks "the error on standard error"), plan line 405 (the library's message "to the server's standard error only"); `ApiOptions` (plan lines 337 to 344) has no writer, and `process.stderr.write` is refused in `api` by the rule of B-1 (verified).
- Failure scenario: the builder uses `console.error` and the test spies on it, which works but couples tests to a global and prints during the gate; or it uses `process.stderr.write` and the structure test fails.
- Fix: add `readonly log: (text: string) => void` to `ApiOptions`, `main` binding it to standard error under B-1's ruling and the tests to an array.

### M-6 (Minor): Task 9 merges after Task 8's knip change, which its builder never ran

- Handle: plan line 77 (Task 9 beside 7a to 8), plan line 557 (Task 9 modifies `ts/src/api/index.ts` without saying what it exports), plan line 545 (Task 8 turns on `includeEntryExports`).
- Failure scenario: Task 9's lane is built against a `knip.json` without `includeEntryExports`; an export it adds to `#api` (`PAGE`, `SCRIPT`, a route helper) that only `http.ts` reads passes in the lane and fails knip at the merge, in the coordinator's gate rather than the builder's.
- Fix: say what Task 9 adds to `index.ts` (nothing, if the routes live in `http.ts`), or rebase the lane onto `server-api` after Task 8 merges and rerun the gate before review.

### M-7 (Minor): the help text beyond the usage line has no stated bar

- Handle: plan line 30 (the command prints lodge 0.2's output "byte for byte, wherever the parity table does not mark a change"), plan line 195 (only the first line and the command list of each help are specified); argparse wraps help and long usage lines to the terminal's width (`COLUMNS`), so lodge 0.2's own help is not one fixed text.
- Failure scenario: the builder spends effort reproducing argparse's formatter, or the review flags help bodies as parity breaks that no carried test asserts (the carried help tests check names and the first line only, `tests/e2e/test_help_lists_every_command.py:11-27`).
- Fix: state that help bodies and wrapped usage lines follow argparse's layout at 80 columns as far as the carried tests and probe 6 check, and list the difference in the report; or give `lodge -h` and `lodge search -h` at `COLUMNS=80` as fixtures.

## Checked without a finding

- Lane test imports: Tasks 2 and 3 import only `#cli` and `#core`; Task 4's tests only `#app`, `#store`, and plan 2's `tests/app/fakes.ts`; Task 9's `page.test.ts` only `tests/api/world.ts` of Task 5, merged before lane D starts; Task 7a's `server.ts` reads Task 6's `tests/api/authenticator.ts` on the main line, after lane C; the structure rules bind `ts/src` only (`.dependency-cruiser.cjs` and `calls.ts` on `origin/server-core`), so a test reaching another test folder breaks no rule.
- Every `#core` name the tasks consume (`load`, `tree`, `Raises`, `Scope`, `pyRepr`, `parseCoreSettings`, `SettingsError`, `CoreSettings`, `coreSettings`, `compareStamps`, `WORD_CLASS`, `filters`, `formatLevel1`, `formatLevel3`) is exported through `ts/src/core/index.ts` on `origin/server-core`, mostly by `export *`.
- Sockets, network, and browser: S1 to S3 name the steps that need them; no gate test opens a socket or uses the global `fetch` (but see I-3 and M-3).
- The two new packages work with no network once installed: plan 1's passkey probe passes (1 pass, 4 `expect()` calls) and probe 1's `toml.ts` prints its table under `unshare -rn` after `bun install --offline`.
- `bun build --compile` works in a sandbox-like setting (M-2).
- `guide.md` as a text import through `src/cli/text.d.ts`, which probe 3 did not cover (it covered `.html` and `.js`): Biome, `tsc`, dependency-cruiser, knip, and `bun test` all pass in the scratch worktree (851 pass), and `bun-types` declares no `*.md` module to collide with.
- `import pkg from "../package.json" with { type: "json" }` in `src/main.ts` with `"version": "0.3.0"` and `src/main.ts` in knip's `entry`: the whole gate passes, and `bun src/main.ts` prints `0.3.0`.
- d-v9mw2d: the `yaml` package reads `LOG_TOKENS` and `LOG_STREAM` inside its functions (`node_modules/yaml/dist/parse/parser.js:178`, `compose/composer.js:139`), so deleting them in `main.ts`'s body, after the imports run, is in time.

## Counts

1 Blocking, 7 Important, 7 Minor.

## Files read

- Read: `CLAUDE.md`; the plan, its ledger, `planner-brief.md`, `planner-report.md`, `probes.md`, and every file under `probes/`; plan 1 (`docs/superpowers/plans/2026-11-02-lodge-server-core.md`, Global Constraints to "Settled for the later plans") and its ledger on `origin/server-core`; plan 1's probes 1 to 3, 10, 11, 13, and 25, and `probes/tests/passkey.test.ts`; plan 2 on `origin/server-store` at `7204ad3` (Global Constraints to "Tasks and lanes", and the Files and interface lines of Tasks 2, 7a, 7b, 11, and 12 by `grep`); plan 4 on `origin/server-import` at `6c6322c` by `grep` for its consumption of plan 3; on `origin/server-core`: `ts/knip.json`, `ts/package.json`, `ts/tsconfig.json`, `ts/biome.json`, `ts/.dependency-cruiser.cjs`, `ts/tests/structure/table.ts`, `ts/tests/structure/calls.ts`, the first 80 lines of `ts/tests/structure/imports.test.ts`, `ts/src/core/index.ts`, `ts/tests/parity.json`'s rows for this plan, `scripts/check-ts.sh`; `src/lodge/cli/files.py`, `tests/e2e/support.py`, the test names of the carried e2e files, `tests/test_entry_point.py`, and `tests/test_wheel.py` by `grep`; `lodge show` of d-4psbdv and d-v9mw2d.
- Not read: the server design document; `lodge spec`; the other rulings of this plan in lodge (d-p8jdqj, d-z1pncx, d-dfkqec, d-y0ppty, d-kt4jkq, d-3ywdhq, d-vfyex3, d-rn4qzq, d-kky8qc, d-bwb1tt, d-5kskm3, d-djh40k) beyond their summaries in the plan; `src/lodge/cli/commands.py`, `output.py`, `thread_output.py`, `threads.py`, and `parser.py` in full (sized with `wc -l` only); plan 2's task bodies beyond the lines named; plan 1's task bodies and reviews.
