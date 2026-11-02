# lodge server, build step 1, plan 4: the importer, the export, and the design's records

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** a lodge 0.2 store moves onto the server and back out to git with nothing changed but the people in its `decided_by` lines and its thread messages' `by` lines, the hook tells an agent that a moved project's records live on the server, and lodge's specification holds the server design, whose document is then frozen.

**Architecture:** the `git` package reads a 0.2 store's files at a revision and writes the export's commits through a temporary index; it is the only package that runs git (d-k5swcq, d-x6f9za).
`app` prepares and runs an import (it checks the store as a change from an empty state with the store's settings, maps the author to the project's one owner, checks the mapped state the same way with the project's settings and owners, and publishes it through the owner's store) and batches the export on plan 2's clock; `store` keeps each project's export target as an event; `api` serves `import` and `export-target` to the signed-in person only; `hook` ports lodge 0.2's hook with advice for a moved project; `cli` gains `lodge hook` and builds the hook's context; `main` joins `git` to the rest (d-bs5mm8, d-j5s0h0).
Records cross every boundary as path and file text, as lodge 0.2 writes them (d-smx3xf).

**Tech stack:** plans 1 to 3's, with no new dependency (Task 1): git through the `git` program, as lodge 0.2 runs it (`src/lodge/gitstore/git.py`); TOML through plan 3's smol-toml reading in `cli`; stored bytes through plan 2's `decodeUtf8` and `encodeUtf8` (d-0q54zn, d-ryss91).

**Spec:** `lodge spec` and lodge 0.2's tests for the behaviour carried over; `docs/superpowers/specs/2026-11-02-lodge-server-design.md` (the design, approved by the author 2026-11-02 13:52) for what changes.
The plan argues from them, never over them; where they disagree with this plan, they win and the builder reports it.
"Design line N" is a line of the design; "probe N" is an item of `docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md`, whose sources are in `probes/` beside it; "plan 1", "plan 2", and "plan 3" are `docs/superpowers/plans/2026-11-02-lodge-server-core.md`, `…-server-store.md`, and `…-server-api.md`.

**Aligned against:** plan 2 at `origin/server-store` 0244e79 and plan 3 at `origin/server-api` 9a25b93, one pin each, re-stated at each alignment; the names this plan takes from them are listed below, and the coordinator checks each against the merged code before the task that consumes it.

## Global Constraints

- Builders are Codex (`codex exec`), one task per brief; a brief holds these constraints and its task, and Codex sees only its brief, `CLAUDE.md`, and the repository.
- In Codex's sandbox git's index is read-only, sockets are refused, and there is no network (plan 1, Global Constraints): the builder never stages, commits, or pushes, and never runs `bun install` or `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name.
  Git in a temporary folder works there: lodge 0.2's 1,056 tests, its git store's among them, passed in the sandbox (`docs/superpowers/plans/2026-10-30-lodge-on-itself/task-5-report.md:102`).
- Every process is spawned with `Bun.spawnSync`, never `Bun.spawn`: an asynchronous spawn with piped output hands the child a socket pair, which the sandbox may refuse, while `Bun.spawnSync` gives it `memfd` files (probe 9), and plan 1's one spawning test, `ts/scripts/differential.test.ts`, passed in the sandbox with it (`docs/superpowers/plans/2026-11-02-lodge-server-core/task-12-report.md:30` on `server-core`); plan 1 has no git adapter whose way this could follow.
- The file-writing call rule reports `write` and `writev` only as functions of `fs` called by name, and `.write` only on a `Bun.file(…)` (d-d0vca9, replacing d-4zg8q3, on `server-core`), so `process.stdout.write` in `main.ts` and the port method `ExportPorts.write` pass it; that rule change lands in plan 1's fix wave before this plan builds, and no task here makes it.
  A function or parameter of `src/` outside `git` is still never named after a name of the rule's list (`writeFile`, `mkdir`, `rm`, and the rest), so `#hook`'s output function is `out`.
- The builder's gate: `sh scripts/check-ts.sh`; the coordinator's gate after every task: `sh scripts/check.sh` green outside the sandbox, then it stages with explicit paths, commits with `git -c user.name="Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, the message ending `Co-Authored-By: Claude <noreply@anthropic.com>`, and pushes `server-import` (or the task's lane branch) to `origin`; never `main`.
- lodge 0.2 keeps working: `src/`, `tests/`, `pyproject.toml`, and `uv.lock` are not edited.
- Test-first: each carried or new test is written and seen failing before its code (a missing module or export counts as failing); a carried test over code that already exists is seen failing against a mutation of that code, which the builder names in its report and then reverts (d-mfayy5); every existing test keeps passing, edited only where a task says so.
- Porting follows plan 1's Global Constraints, "Porting", "Types", "Exceptions", "Names", "Text", and "Times", which the brief repeats: carried tests keep their Python names without `test_`, an assertion asserts no less than its Python original, a parametrised test keeps every case, `X | None` is `X | null`, a `raise ValueError` is the `ValueError` of `#core`, a Python string operation whose JavaScript namesake differs goes through `text.ts`, and times cross into `core` and `app` as stamps.
- Errors: every refusal the command or the API reports is a `LodgeError` of `#app` or one of its subclasses (`NotFound`, `Conflict`, `Forbidden`), as in lodge 0.2 (`src/lodge/app/errors.py`, `src/lodge/gitstore/errors.py`), with its message given in the task; plan 3's handler maps them to kinds by class.
- Structure (plan 1, Task 3; d-k5swcq, d-x6f9za, d-mfskz3, d-s5s2c3): `cli`, `hook`, and `api` import only `app` and `core`, `store` and `git` only `app` and `core`, and only `main` imports every package (`ts/tests/structure/table.ts`); only `git` spawns processes and writes files, `git` and `cli` read them, and `hook` reads none; `core` and `app` take the time and the waiting through plan 2's `Clock`; no file over 300 lines.
- Exports (d-tha8st): every export a task adds has a reader in that task, its own tests counting, and each task names that reader; a type only its own module's signatures use is not exported (as Task 3's `exportStore` types are not), so knip passes after each task, with plan 3's `includeEntryExports` on (d-s2rdn2, d-amxk94); the names of "Names this plan consumes" carry `/** @public */` from plan 3's Task 8 where nothing read them before this plan, and a task that adds their first reader leaves the tag.
- Git in tests: only in folders made with `mkdtempSync` under the system's temporary folder, through `isolateGit()` of `ts/tests/git/isolated.ts` (Task 2), which gives every test an empty `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_TERMINAL_PROMPT=0`, and a fixed identity; every repository is made with `git init -b main` (or `--bare -b main`); a remote is a bare repository named by its path, so no test needs a socket or the network (`CLAUDE.md`, "Hard rules").
  A spawn without `env` does not see a change a test made to `process.env` (probe 9), so every test helper runs git only through `#git`'s `run` or `attempt`, which pass `{ ...process.env, … }` as `env` at each call.
- No task exports into this repository: every export target is a repository in a folder from `mkdtempSync`, since this repository's gate (`scripts/check.sh`, `uv run lodge check --gate`) and `scripts/differential.sh` read its own `lodge/` with lodge 0.2, whose check an export naming the person fails (probe 7, d-b61590).
- Fixtures are the made-up project of lodge 0.2's tests (the `storage` area, transcripts, logs) and made-up people (`ana`, `bo`), never her words or another project's records; the made-up 0.2 store of `probes/zero-two-store/` is lodge 0.2's own output for that project (probe 6).
- User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; code comments state the fact.
- Records (Tasks 11a to 11c): written only through `lodge add`, drafts under `.drafts/`, a dry run before every add; in the sandbox, once per task, `mkdir -p .drafts/objects && cp "$(git rev-parse --absolute-git-dir)/index" .drafts/index`, then every `lodge add` runs as `GIT_INDEX_FILE="$PWD/.drafts/index" GIT_OBJECT_DIRECTORY="$PWD/.drafts/objects" GIT_ALTERNATE_OBJECT_DIRECTORIES="$(git rev-parse --path-format=absolute --git-common-dir)/objects" uv run --frozen --quiet lodge add FILE...` (`docs/superpowers/plans/done/2026-10-31-lodge-viewer.md:25`); when that fails, the coordinator runs the adds from the builder's drafts.

## Calls made

Each is the planner's ruling, recorded in lodge with scope `process` and this plan as its work item; its reasoning there holds a handle per argument and the cost if wrong.
Every task repeats what it needs of them, so no brief needs this section.

1. d-1skjw1: the `import` operation names a repository on the server's machine and a revision, the server reads it through `git`, and only the signed-in person may call it; step 1 gives it no command and no form (Tasks 2 and 8).
2. d-sdpcyb (replacing d-ag8p8h and d-y42b7b): the importer checks the store as a change from an empty state, with the store's own `.lodge.toml` read at a settings revision defaulting to the store's, maps, checks the mapped state the same way with the project's settings and owners, refusing a path that is not UTF-8, and imports into an empty project only, with one `publish` through the owner's store, writing no settings (Tasks 2, 5, and 8).
3. d-83kt6y: the importer maps each `decided_by: author` and each thread message's `by: author` to the owner, through the record and thread writers, and refuses a file its writer would not give back byte for byte (Task 5).
4. d-ryss91: every file read from git, attachments included, is decoded with plan 2's `decodeUtf8`, and no file is refused for its bytes (Tasks 2 and 5).
5. d-b61590 (the author's): the export names the person who decided or wrote a message, and need not stay readable by lodge 0.2 (Tasks 6 and 10).
6. d-pv341r: the export writes only a branch holding nothing outside `lodge/` that no work tree has checked out, through a temporary index, without force, with no commit when nothing changed (Task 3).
7. d-sj6hmf: `app`'s exporter batches the writes into at most one commit a minute by sleeping on plan 2's clock, retries a minute after a failure, flushes on start, and writes every file of the project with the two `.gitkeep` files (Task 6).
8. d-j5s0h0: a project's export target is an `export-target` event read back by an `ExportTargets` port; the composition root wraps each project's store so that every published write tells the exporter; and it joins `git`'s reading of a 0.2 store with `cli`'s reading of its `.lodge.toml` (Tasks 6, 7, and 8); d-v0r9cb: the wrappers are `Proxy`s forwarding every method they do not change, and `exportingProjects` takes a function (Task 6).
9. d-va3j7x: a project has moved when its `.lodge.toml` names its server; then every file under `lodge/` but the attachments gets the moved advice, whatever the store's mode (Tasks 4 and 9).
10. d-bs5mm8: `parseHookSettings` lives in `app`; `cli` builds the hook's context with `git`'s functions given as parameters; the grammar runs `lodge hook EVENT` through a function of `Io` that `main` builds; the carried hook tests run in a real repository without `[server]` (Tasks 4 and 9).
11. d-yng7m8: the server design goes into lodge whole, a decision per section, in three tasks, an unbuilt claim naming its build step; new areas `work` and `sessions` (Tasks 11a to 11c).
12. d-s83a6e: Task 8 extends plan 3's code by names only (`tomlTable`, the two person operations dispatched as `approve` is, an optional `ApiOptions.moving`, and `world.ts`'s `exporters`, `targets`, `createProject`, and `asPerson`), the exports start in `main.ts`'s `listen`, and Task 10 runs over `world.ts` (Tasks 8 and 10).

The author answered IMP-1 (`docs/superpowers/plans/2026-11-02-lodge-server-import/questions.md`): the export writes the person (design line 78), and lodge 0.2 need not read it (d-b61590).
So design line 284's "the export reads like a lodge 0.2 store" means lodge 0.2's file layout only, not that lodge 0.2's `check`, `spec`, or `waiting` read it cleanly (probe 7), and the export writes no `.lodge.toml`, which no task of the server needs.

## Names this plan consumes from plans 1, 2, and 3

Each name as the plan named in "Aligned against" gives it; when the merged code differs, the coordinator writes the merged name into the brief and the ledger, and a difference in meaning stops the task with BLOCKED.

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

Plan 3's `project-create` makes the person the server is set up for the project's owner (`projects.create(project, owner, settings)`), which is the one owner Task 5's `importStore` asks `Projects.members` for, and its `lodgeFor` builds every `Lodge` over `ApiOptions.projects.storeFor`, which Task 8 wraps.
Plan 2's `ask`, `reply`, and `close` hold an agent's message whose `by` names a person until that person approves it, and refuse one person writing under another's name (d-2v8vtk, the author's, replacing d-x6vaw8; plan 2's Task 12c); the import writes thread messages through `Store.publish`, which neither holds nor refuses a message (plan 2's Task 12c changes only `threads.ts`, `held.ts`, and `results.ts`), through the store the owner acts through, and only that owner may import (Task 5), so every message it writes under a person's name is written by that person, signed in, and nothing it writes is held.

## Lanes

The tasks run on `server-import` in its worktree; a lane is a task built in its own worktree and merged into `server-import`, as plan 1's lanes are (d-xdqsmf).
What each task imports decides when it can start; "plan 2's Task N" means that task merged into `server-import`:

| Task | Packages it touches | Starts after | Beside |
|---|---|---|---|
| 1 | tests (setup, coordinator) | plan 1 merged | |
| 2 | `git` | Task 1, plan 2's Tasks 2 and 7a | 4, 5, 6, 7 |
| 3 | `git` | Task 2 | 4, 5, 6, 7 |
| 4 | `hook`, `app` | Task 1, plan 2's Task 6 | 2, 3, 5, 6, 7 |
| 5 | `app` | Task 1, plan 2's Task 11 | 2, 3, 4, 6, 7 |
| 6 | `app` | Task 1, plan 2's Task 12a | 2, 3, 4, 5 |
| 7 | `store` | Task 6, plan 2's Task 7b | 2, 3, 4, 5 |
| 8 | `api`, `cli`, `main` | Tasks 2, 3, 5, 6, and 7, and plans 2 and 3 merged | 9 |
| 9 | `cli`, `main` | Tasks 2 and 4, and plan 3 merged | 8 |
| 10 | tests and scripts | Tasks 8 and 9 | |
| 11a, 11b, 11c | records | Task 10; in order | |

So four lanes run at once after Task 1 (2 then 3; 4; 5; 6 then 7), then 8 beside 9.
Tasks 4, 5, and 6 each add to `ts/src/app/index.ts` and to `ts/tests/app/front-door.test.ts`'s allowed additions, Tasks 2 and 4 each to `ts/package.json`'s `imports`, Tasks 2, 4, and 9 each to `ts/tests/parity.json`, Task 7 and plan 3's Task 4 each add cases to `ts/src/store/events.ts`, and Tasks 8 and 9 each to `ts/src/main.ts`, `ts/src/cli/index.ts`, and `ts/src/cli/settings.ts`; the merge of a later lane keeps both sides' lines.
Task 4 waits for plan 2's Task 6, which creates the front-door test, so that its addition lands on a list that exists.

## Review Focus

1. Bytes: a record file with an undecodable byte is problem 1 and refuses the import, an attachment that is not UTF-8 comes back byte for byte, and no text reaches git or the events but through `encodeUtf8`.
2. The author mapping: only `decided_by: author` of a decision and `by: author` of a thread message change, through the writers, and a file its writer would not give back byte for byte is refused rather than rewritten.
3. The import refuses a store whose change from an empty state the check refuses with the store's settings, a mapped state the check refuses with the project's settings and owners, a path that is not UTF-8, a project that already holds records, and a requester who is not the project's one owner; nothing is written when it refuses.
4. The export: never a branch holding anything outside `lodge/`, never a branch a work tree has checked out, never a force push, no commit when nothing changed, at most one commit a minute however many writes come within one run of the server (after a restart, `start` exports at once), and every published write reaching it.
5. Who may: `import` and `export-target` answer an agent's token with `forbidden`, since an import writes decisions in a person's name (design line 75).
6. The hook: every carried test keeps its assertions, a moved project's advice names the server and never `git checkout`, and the hook stays silent on every failure.
7. The round trip: the made-up store comes back byte for byte apart from the `decided_by: author` lines of its decisions and the `by: author` lines of its thread.

## Parity rows this plan settles

| Python file | Status now | After | Task | TypeScript counterpart |
|---|---|---|---|---|
| `tests/gitstore/conftest.py` | planned | ported | 2 | `ts/tests/git/isolated.ts` |
| `tests/gitstore/repos.py` | planned | changed: "design line 72: records live in the server's events, not in files in git; the helpers of lodge 0.2's git store (`initialised`, `publish_one`, `checkout_project`, `Ticker`) have no counterpart, and the repository helpers are carried" | 2 | `ts/tests/git/repos.ts` |
| `tests/hook/test_post_tool_use.py` | changed | changed: "d-va3j7x adds the moved project's advice, in `moved-advice.test.ts`; d-bs5mm8 moves `parse_hook_settings` to `#app`" | 4 | `ts/tests/hook/post-tool-use.test.ts` |
| `tests/e2e/test_hook_feedback_after_hand_edits.py` | changed | changed: "d-bs5mm8: the store's folders are made by hand where lodge 0.2 ran `lodge init`, which on the server names the server instead" | 9 | `ts/tests/hook/hand-edits.test.ts` |
| `tests/e2e/test_hook_outside_repository_exit_0_silent.py` | planned | ported | 9 | `ts/tests/hook/outside-repository.test.ts` |
| `tests/e2e/test_help_lists_every_command.py` | changed (plan 3) | changed: plan 3's `why` without "and `hook` for plan 4" | 9 | `ts/tests/e2e/help-lists-every-command.test.ts` |

The three hook rows keep every Python test name, since the design's change adds the moved project's advice and leaves the rest; Task 10 makes the parity test check that, and that their files exist.

---

### Task 1: Setup and the made-up store

The coordinator does this task itself, outside the sandbox.

**Files:**
- Create: `ts/tests/core/zero-two-store.ts` (generated), `ts/tests/core/zero-two-store.test.ts`
- Modify: the ledger

**Interfaces:**
- Consumes: plan 1, merged into `server-import`.
- Produces: `ZERO_TWO_STORE: ReadonlyMap<string, string>` in `ts/tests/core/zero-two-store.ts`, the eleven files of `probes/zero-two-store/` (ten under `lodge/` and `.lodge.toml`) by path, read by Tasks 2, 5, 6, 8, and 10.

- No dependency is added: git runs as the `git` program, `.lodge.toml` is read by plan 3's smol-toml reading in `cli`, and stored bytes by plan 2's codec; so `ts/package.json`, `ts/bun.lock`, and plan 3's `ts/bunfig.toml` (d-svv7gv) stay as plans 1 to 3 leave them, and only the `imports` map gains `#git` and `#hook` where Tasks 2 and 4 create those packages.
- Merge points, each named in the ledger with its commit: plan 2's Tasks 2, 6, 7a, 7b, 10, 11, and 12a as the lanes table says; all of plans 2 and 3 before Tasks 8 and 9.

- [ ] **Step 1:** Merge `server-core` into `server-import` once plan 1's last task is merged there; `sh scripts/check.sh` green.
- [ ] **Step 2:** Write the test `ts/tests/core/zero-two-store.test.ts` with `zero_two_store_checks_clean`: for `after` = `load` of `tree({ rev: null, files, attachments })` of the store's files under `lodge/` (the attachment's path in `attachments`, every other file in `files`), `checkState(after)` finds no problem, as lodge 0.2's `lodge check` printed `ok` (probe 6), and `checkChange(load(tree({ rev: null, files: new Map() })), after, parseCoreSettings(Bun.TOML.parse(<its .lodge.toml>)), "2026-11-03T00:00:00+00:00")` finds none either, as lodge 0.2's `check_change` found none (probe 9); run `cd ts && bun test tests/core/zero-two-store.test.ts`; expected: FAIL (no module).
- [ ] **Step 3:** `python3 docs/superpowers/plans/2026-11-02-lodge-server-import/probes/fixture.py docs/superpowers/plans/2026-11-02-lodge-server-import/probes/zero-two-store > ts/tests/core/zero-two-store.ts`, then Biome's formatter on it; run the test again; expected: PASS.
  The generator writes each text as a JSON string literal, and the 11 texts read back equal to the files (`files 11; equal 11`, run on 2026-11-02 against the store of probe 6).
- [ ] **Step 4:** `git diff server-core -- ts/package.json ts/bun.lock ts/bunfig.toml` shows only plan 2's and plan 3's changes; the ledger line says no dependency is added and why; `sh scripts/check.sh`, commit, push.

### Task 2: Running git and reading a lodge 0.2 store

**Files:**
- Create: `ts/src/git/index.ts`, `ts/src/git/run.ts`, `ts/src/git/read-store.ts`, `ts/src/git/paths.ts`, `ts/tests/git/isolated.ts`, `ts/tests/git/repos.ts`, `ts/tests/git/zero-two.ts`
- Modify: `ts/package.json` (`"#git": "./src/git/index.ts"` in `imports`), `ts/tests/parity.json` (two rows)
- Test: `ts/tests/git/run.test.ts`, `ts/tests/git/read-store.test.ts`, `ts/tests/git/paths.test.ts` (new)

**Interfaces:**
- Consumes: plan 2's `decodeUtf8` and `encodeUtf8` of `#core` (Task 7a); `#app`'s `LodgeError`; Task 1's `ZERO_TWO_STORE`.
- Produces, through `#git`:
  ```ts
  // run.ts, a port of src/lodge/gitstore/git.py without request_exit; synchronous, as Bun.spawnSync is
  export class GitMissing extends LodgeError {}                       // "git is not installed or is not on the PATH"
  interface GitDone { readonly code: number; readonly stdout: Uint8Array; readonly stderr: Uint8Array }
  export function attempt(args: readonly string[], cwd: string, env?: Readonly<Record<string, string>>, input?: Uint8Array | string): GitDone
  export function runBytes(args: readonly string[], cwd: string, env?: Readonly<Record<string, string>>, input?: Uint8Array | string): Uint8Array
  export function run(args: readonly string[], cwd: string, env?: Readonly<Record<string, string>>, input?: Uint8Array | string): string
  export function resolveRev(cwd: string, ref: string): string | null
  // read-store.ts
  interface StoreRead {
    readonly rev: string                                // the commit read
    readonly files: ReadonlyMap<string, string>         // every file under lodge/, attachments and .gitkeep included, by path
    readonly settings: string | null                    // .lodge.toml at the settings commit, as text
  }
  export function readStore(repository: string, rev: string, settingsRev?: string): Promise<StoreRead>   // settingsRev defaults to rev
  // paths.ts
  export function resolvePath(path: string): string     // Python's Path(path).resolve(): links followed where they exist
  export function repoRootOf(edited: string): Promise<string>
  export function isFolder(path: string): boolean
  ```
- `attempt` spawns `git -C <cwd> <args>` with `Bun.spawnSync` (Global Constraints), its `env` built at each call as `{ ...process.env, LC_ALL: "C", GIT_TERMINAL_PROMPT: "0", ...env }` and passed explicitly, since a spawn without `env` does not see a test's change to `process.env` (probe 9); standard input is ignored when there is no `input`, and a string `input` is encoded with `encodeUtf8`.
  A missing `git` program is the `ENOENT` error `Bun.spawnSync` throws (`code` `ENOENT`, `Executable not found in $PATH: "git"`, probe 9), which `attempt` throws again as a `GitMissing`; `runBytes` throws a `LodgeError` with git's first non-empty line of standard error, else of standard output, else `git <args[0]> failed`, as `run_bytes` does; `run` decodes with `decodeUtf8` and drops the final newlines; `resolveRev` is `resolve` of `git.py`, `rev-parse --verify --quiet --end-of-options <ref>^{commit}`, null on exit 1, `--end-of-options` kept as a defence that no test can show, since `^{commit}` after an option already makes git refuse it (practice review P4-M1).
- `GitDone` and `StoreRead` are not exported, since no other module names them (Global Constraints, "Exports"); the exports' readers in this task: `run.test.ts` reads `GitMissing`, `attempt`, `runBytes`, `run`, and `resolveRev`; `read-store.test.ts` reads `readStore`; `paths.test.ts` reads `resolvePath`, `repoRootOf`, and `isFolder`.
- `readStore` and `exportStore` (Task 3) return a `Promise`, the shape of the ports they serve (`Moving.read`, `ExportPorts.write`), though their git calls are synchronous.
- `readStore` resolves `rev` and `settingsRev` with `resolveRev` and refuses one that names no commit with `LodgeError("<rev> is not a commit in <repository>")`; lists `ls-tree -r -z --full-tree <commit> -- lodge` and refuses an empty listing with `LodgeError("<rev> holds no lodge/ folder, so it is not a lodge 0.2 store")`; decodes each path with `decodeUtf8`, so a file name that is not UTF-8 holds U+DC80 to U+DCFF, as lodge 0.2 decodes it with `surrogateescape` (`src/lodge/gitstore/trees.py:32`), and Task 5 refuses it; reads every blob in one `cat-file --batch`, as `_contents` of `src/lodge/gitstore/trees.py` does, and gives each its text through `decodeUtf8`, an entry that is not a blob the empty text, as `read_tree` does; and reads `.lodge.toml` at the settings commit in the same batch, null when there is none.
  Unlike `read_tree`, it gives the attachments' texts too, since the import carries them, and refuses no file for its bytes: an attachment that is not UTF-8 holds U+DC80 to U+DCFF and goes back to the same bytes through `encodeUtf8` (d-ryss91).
  In lodge 0.2's branch mode the store's branch holds only `lodge/` and `.lodge.toml` is on the base branch (`src/lodge/gitstore/branch.py:169`), so the caller names the base branch as `settingsRev` (d-sdpcyb).
- `resolvePath` follows Python's non-strict `resolve`: an absolute path is normalised segment by segment, each existing prefix with `realpathSync` and the rest appended, `..` taken after the links before it are followed; it lives in `git` because `hook` may not read the file system (d-x6f9za).
- `repoRootOf(edited)` is `rev-parse --show-toplevel` in the nearest existing folder at or above `resolvePath(edited)`'s parent (`_existing_folder` and `_hook_context` of `src/lodge/main.py:65-78`), and a folder outside any repository is a `LodgeError("<folder> is not inside a git repository")`, as `repo_root` says it.
- `isolated.ts` exports `isolateGit()`, which registers `beforeEach` and `afterEach` hooks setting and restoring the variables of `tests/gitstore/conftest.py`'s `isolated_git`, the identity `Test Author <test@example.com>` included, and deleting `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, and `GIT_COMMON_DIR` for the test; `attempt`'s explicit `env` is what carries them to git.
- `repos.ts` carries `git`, `commit`, and `write` of `tests/gitstore/repos.py`, the helpers this task's tests and `zero-two.ts` call, each over a folder from `mkdtempSync`, `git` running through `#git`'s `run`; Task 3 adds the rest it needs, and the helpers that build lodge 0.2's git store have no counterpart.
- `zero-two.ts` exports `zeroTwoRepository(layout: "checkout" | "branch", extra: ReadonlyMap<string, string> = new Map()): Promise<{ repository: string; rev: string; settingsRev: string }>`, which commits Task 1's `ZERO_TWO_STORE` and the files of `extra` (paths under `lodge/`, each text written as the bytes `encodeUtf8` gives, so U+DCFF U+DCFE is the two bytes `ff fe`) into a new repository, on `main` for `checkout` and on an orphan branch `lodge` holding only `lodge/` for `branch`, with `.lodge.toml` on `main` in both, `rev` the commit holding `lodge/`, and `settingsRev` the commit of `main` holding `.lodge.toml` (equal to `rev` in the checkout layout).

- [ ] **Step 1: Write the failing tests.**
  - `run.test.ts`: `missing_git_is_one_sentence` (`attempt(["--version"], dir, { PATH: <an empty folder from mkdtempSync> })` throws a `GitMissing` with its message, as `tests/gitstore/test_setup.py:97-98` empties `PATH` to a folder; an empty `PATH` text would find git, probe 9); `failure_names_gits_first_line` (`runBytes(["rev-parse", "--verify", "nope"])` throws a `LodgeError` whose message is git's first line); `resolve_rev_gives_null_for_a_missing_ref`; `input_reaches_git` (`hash-object --stdin` of `"a\n"` gives `78981922613b2afb6025042ff6bd878ac1994e85`); `isolation_reaches_git` (inside `isolateGit()`, `run(["var", "GIT_AUTHOR_IDENT"], repo)` starts `Test Author <test@example.com>` and `attempt(["config", "--global", "--list"], repo)` lists nothing, and the same through `repos.ts`'s `git`; the builder names in its report the mutation that drops `env` from the spawn and the test that then fails).
  - `read-store.test.ts`: `reads_the_checkout_layout` (`readStore(repository, rev)` of `zeroTwoRepository("checkout")` gives the ten files of `ZERO_TWO_STORE` under `lodge/` with their texts, `.lodge.toml`'s text in `settings`, and the commit in `rev`); `reads_the_branch_layout` (`readStore(repository, rev, settingsRev)` of `zeroTwoRepository("branch")`: the same files and `settings`); `branch_layout_without_a_settings_revision_has_no_settings` (`readStore(repository, rev)` of the branch layout: `settings` null); `revision_that_is_no_commit_is_refused` (for `rev` and for `settingsRev`); `revision_without_lodge_is_refused` (the `main` of the branch layout); `undecodable_record_reads_as_escapes` (a decision with a `\xff` byte reads with U+DCFF); `undecodable_attachment_keeps_its_bytes` (`zeroTwoRepository("checkout", new Map([["lodge/attachments/d-q59cdf/raw.bin", "\uDCFF\uDCFE"]]))`: the attachment, the bytes `ff fe` on disk, reads as U+DCFF U+DCFE, which `encodeUtf8` gives back as the two bytes); `undecodable_name_reads_as_escapes` (a file under `lodge/spec/storage/` whose name holds the byte `\xff`, committed through `update-index -z --index-info`, is listed with U+DCFF in its path); `symbolic_link_reads_as_the_path_it_names` (a link committed under `lodge/` reads as the blob's text, the path the link names, as `read_tree` reads a blob of mode 120000); `settings_absent_is_null`.
  - `paths.test.ts`: `resolve_follows_links` (`tests/hook/test_post_tool_use.py`'s `test_symlinked_checkout_still_matches` layout); `resolve_takes_dot_dot_through_missing_folders` (`<tmp>/docs/../lodge/decisions/d.md` with no `docs` resolves to `<tmp>/lodge/decisions/d.md`); `repo_root_of_a_file_that_does_not_exist_yet` (as `test_hook_finds_the_repository_for_a_file_that_does_not_exist_yet`); `repo_root_outside_a_repository_is_one_sentence`; `is_folder_says_whether_a_folder_exists`.
- [ ] **Step 2: Run** `cd ts && bun test tests/git`; expected: the new tests FAIL.
- [ ] **Step 3: Implement**; add `#git` to `ts/package.json`'s `imports`; flip `tests/gitstore/conftest.py` to `ported` and `tests/gitstore/repos.py` to `changed` with the `why` of "Parity rows this plan settles".
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 3: The export writer

**Files:**
- Create: `ts/src/git/export.ts`
- Modify: `ts/src/git/index.ts`, `ts/tests/git/repos.ts` (`bareRemote`, `clone`, `seeded`, `worktree`, and `riggedRemote`)
- Test: `ts/tests/git/export.test.ts` (new)

**Interfaces:**
- Consumes: Task 2's `run.ts`, `readStore`, and test helpers; `encodeUtf8` of `#core`.
- Produces, through `#git`:
  ```ts
  export function exportStore(
    target: { readonly repository: string; readonly branch: string; readonly remote: string | null },
    files: ReadonlyMap<string, string>,
    message: string,
  ): Promise<{ readonly kind: "committed"; readonly commit: string } | { readonly kind: "unchanged" } | { readonly kind: "moved" }>
  ```
  The parameter and result types are written in `export.ts` and not exported, so this lane needs nothing of Task 6; they are `#app`'s `ExportTarget` and `ExportOutcome` (Task 6) in shape, which Task 8's wiring checks when it passes `exportStore` as the exporter's `write`.
- `exportStore` (d-pv341r):
  1. Refuses a path of `files` outside `lodge/` as `check_writes` of `src/lodge/gitstore/plumbing.py:14-26` refuses it, with its message, and a branch name that is not a name of letters, digits, and `. _ / -` not starting with a symbol or holding `..`, by `_name`'s rule (`src/lodge/gitstore/settings.py:76-83`) with its own sentence, `LodgeError("export-target: branch must be a name of letters, digits, and . _ / -, not starting with a symbol")`, since no `.lodge.toml` names it, and a remote starting with `-` with `LodgeError("export-target: remote must not start with -")`, so neither reaches git as an option.
  2. Finds the tip: with a remote, `ls-remote <remote> refs/heads/<branch>` (`remote_tip`), and when there is one, `fetch --quiet --no-tags <remote> refs/heads/<branch>` so that its commit is local; without one, `resolveRev(repository, "refs/heads/<branch>")`, and a branch that a work tree of the repository has checked out (`worktree list --porcelain` names `branch refs/heads/<branch>`) is refused with `LodgeError("<branch> is checked out in a work tree of <repository>; the export writes only a branch no work tree has checked out")`.
  3. Refuses a tip whose tree holds a path outside `lodge/` (`ls-tree -r --name-only <tip>`), with `LodgeError("<branch> holds files outside lodge/, so it is not a branch lodge exports to; name a branch of its own")`, so the export never writes a project's main branch (design must-not 7).
  4. Builds the tree in a temporary index in a folder from `mkdtempSync`: each text through `encodeUtf8` into a file there, one `hash-object -w --no-filters --stdin-paths`, one `update-index -z --index-info`, then `write-tree` (probe 4); the folder is removed in a `finally`.
  5. Answers `unchanged` when the tree equals the tip's tree, making no commit.
  6. Commits with `commit-tree <tree> [-p <tip>] -F -`, the author and committer `lodge <lodge@export.invalid>` through `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, `GIT_COMMITTER_NAME`, and `GIT_COMMITTER_EMAIL`, the message ending in one newline.
  7. Moves the branch without force: with a remote, `push --porcelain <remote> <commit>:refs/heads/<branch>`, `moved` when it is refused and `ls-remote` shows another tip, git's first line as a `LodgeError` otherwise (`push` of `plumbing.py:57-79`); without one, `update-ref refs/heads/<branch> <commit> <tip or forty zeros>`, and when git refuses it, `moved` if `resolveRev` now gives another commit than the tip read, git's first line as a `LodgeError` otherwise (probe 4).
- No work tree is read or written, so a bare repository is a target.
- The files' paths are written as they are given, so a symbolic link read by `readStore` as the path it names comes back as a regular file holding that path (mode 100644); lodge 0.2 never writes a link.
- `repos.ts` gains `bareRemote`, `clone`, `seeded`, and `worktree` of `tests/gitstore/repos.py`, and `riggedRemote(branch)`, carrying `rigged_remote` of `tests/gitstore/test_push_race.py:35-57`: a bare remote whose `pre-receive` hook, the first time it runs, moves the branch to a second clone's commit with `env -u GIT_QUARANTINE_PATH -u GIT_OBJECT_DIRECTORY -u GIT_ALTERNATE_OBJECT_DIRECTORIES git update-ref`, so the export's push, made after its fetch, finds the branch moved.

- [ ] **Step 1: Write the failing tests** in `export.test.ts`, each with `isolateGit()`: `first_export_makes_the_branch` (a bare repository; the branch's tree holds exactly the files, each byte for byte, and the author is `lodge <lodge@export.invalid>`); `same_files_make_no_commit` (`unchanged`, tip unmoved); `changed_file_makes_one_commit_on_the_last` (parent is the previous commit); `removed_file_leaves_the_tree`; `escaped_bytes_are_written_as_bytes` (a text holding U+DCFF is the byte `\xff` in the blob); `path_outside_lodge_is_refused` (`README.md`, `lodge/../x`, `lodge/.git/x`, each with its message); `branch_with_other_files_is_refused` (`main` of `seeded`); `checked_out_branch_is_refused`; `lodge_zero_two_branch_is_a_target` (the branch layout of `zeroTwoRepository`); `bad_branch_name_is_refused` (`-x`, `a..b`, and `a b`, each with its sentence, and a remote `-r`); `push_without_force` (a work repository with a bare remote: the remote's branch has the commit, the work repository's own branches are unmoved); `moved_remote_branch_answers_moved` (over `riggedRemote`: the export answers `moved`, the remote's branch is the second clone's commit, and a second export builds on it); `exported_store_reads_back` (`readStore` of the exported branch gives the files exported).
  The local race (a ref moved between the export's read and its `update-ref`) has no test: no hook runs between the two inside one `exportStore` call, and git's refusal of a stale old value is probe 4's.
- [ ] **Step 2: Run** `cd ts && bun test tests/git/export.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 4: The hook's advice

**Files:**
- Create: `ts/src/hook/index.ts`, `ts/src/hook/post-tool-use.ts`, `ts/src/hook/texts.ts`, `ts/src/app/hook-settings.ts`
- Modify: `ts/package.json` (`"#hook": "./src/hook/index.ts"` in `imports`), `ts/src/app/index.ts`, `ts/tests/app/front-door.test.ts` (`parseHookSettings` among the allowed additions), `ts/tests/parity.json` (the row's `why`)
- Test: `ts/tests/hook/post-tool-use.test.ts` (carried), `ts/tests/hook/moved-advice.test.ts` (new), split so that neither passes 300 lines: `tests/hook/test_post_tool_use.py` is 253 lines with 24 tests, and plan 1's ports ran at about 1.1 times their Python lines (practice review P4-I10)

**Interfaces:**
- Consumes: `#app`'s `LodgeError`.
- Produces, through `#app` (d-bs5mm8): `parseHookSettings(table: unknown): readonly string[]`, `parse_hook_settings` of `src/lodge/hook/post_tool_use.py:44-54` with its three messages, each beginning `.lodge.toml: `.
- Produces, through `#hook`, a port of the rest of `src/lodge/hook/post_tool_use.py`:
  ```ts
  export interface HookContext {
    readonly repoRoot: string
    readonly dataRoot: string | null      // the folder of the record files; null in branch mode
    readonly frozen: readonly string[]
    readonly server: string | null        // the server's address when the project has moved, else null
  }
  export type Resolve = (path: string) => string
  interface HookOutput { readonly hookSpecificOutput: { readonly hookEventName: "PostToolUse"; readonly additionalContext: string } }
  export function respond(payload: unknown, context: HookContext, resolve: Resolve, cwd?: string | null): HookOutput | null
  export function run(read: () => Promise<string>, out: (text: string) => void, context: (edited: string) => Promise<HookContext | null>, resolve: Resolve, cwd: string | null): Promise<0>
  ```
- `HookOutput` is not exported; `post-tool-use.test.ts` reads `HookContext` (each context it builds is typed with it), `Resolve` (its test-local `resolve`), `respond`, and `run`, and `parseHookSettings` of `#app`.
- `respond` and `run` keep the Python logic, with `context` and `resolve` given by the caller (Python's `respond` takes the three parts of the context as arguments; the TypeScript one takes them as one object, so a test's `respond(payload(record), tmp_path, data, ())` becomes `respond(payload(record), { repoRoot, dataRoot: data, frozen: [], server: null }, resolve)`).
  `run` reads the event with `read`, prints one JSON line with `out`, and gives 0 whatever fails, as Python's `run` does.
- `texts.ts` holds `RECORD_TEXT`, `THREAD_TEXT`, and `FROZEN_TEXT` as Python's, character for character, and three texts for a moved project, used when `context.server` is not null, `{server}` the address:
  - `MOVED_RECORD_TEXT`: `{path} is a lodge record file from before this project moved to the lodge server at {server}: its records live on the server now, and an edit here changes nothing there. Run \`lodge draft REF\` (or \`lodge draft area:NAME\`) to get the record as a draft, edit the draft, check it with \`lodge add --dry-run FILE\`, then publish it with \`lodge add FILE\`; the command sends both to the server. ` and then `REVERSE`;
  - `MOVED_THREAD_TEXT`: `{path} is a lodge thread file from before this project moved to the lodge server at {server}: its threads live on the server now, and an edit here changes nothing there. Add a message with \`lodge reply Q --by ROLE FILE\`, or close it with \`lodge close Q --by ROLE\`; the command sends both to the server. ` and then `REVERSE`;
  - `MOVED_FROZEN_TEXT`: `{path} is frozen: lodge holds its content now, on the lodge server at {server}, so do not edit it. Record the change as a new decision instead: write a draft (\`lodge guide\` shows the draft format), check it with \`lodge add --dry-run FILE\`, then publish it with \`lodge add FILE\`, which sends it to the server. ` and then `ASKED`, ` Otherwise reverse your own edit now: `, and `RESTORE`.
- For a moved project every file under `<repoRoot>/lodge/` but `lodge/attachments/` gets the moved record or thread text, whatever `dataRoot` says, since the files there are copies from before the move in either store mode (d-va3j7x); a frozen file gets the moved frozen text.
- Python's `_glob` becomes a pattern built with `new RegExp` and the `u` flag, its escape of each literal character the escape of every character that has a meaning in a JavaScript pattern, and `re.fullmatch` the test of `^(?:p)$`.
- The tests take `resolve` as a test-local function, since this lane runs beside Task 2 and `hook` may not import `git`: it resolves the longest existing prefix of the absolute path with `realpathSync` and appends the rest, `..` taken after the links before it, as Task 2's `resolvePath` does, since `realpathSync` alone throws on the files the carried tests name, which do not exist (`test_symlinked_checkout_still_matches`); Task 9's carried end-to-end tests run the hook with `#git`'s `resolvePath`.

- [ ] **Step 1: Write the failing tests:** in `post-tool-use.test.ts`, every test of `tests/hook/test_post_tool_use.py` by name, each parametrised case kept, `tmp_path` a folder from `mkdtempSync`, the settings tests calling `parseHookSettings` of `#app`; then, in `moved-advice.test.ts`, the new tests:
  `moved_record_edit_names_the_server` (the record text names the server and `lodge draft`, `lodge add --dry-run`, and `lodge add FILE` in that order, and holds neither `do not edit it by hand` nor `as a draft outside`, the two phrases of lodge 0.2's `RECORD_TEXT` that send the reader to edit beside the store, `src/lodge/hook/post_tool_use.py:26-27`; the edited path itself is under `lodge/decisions/`, so the folder's name is no test); `moved_thread_edit_names_reply_and_close`; `moved_frozen_edit_names_the_server`; `moved_project_protects_lodge_in_branch_mode` (`dataRoot` null and `server` set: a file under `lodge/decisions/` gets the moved text); `moved_attachment_edit_gets_nothing`; `moved_advice_reverses_the_edit_without_git` (as `test_record_advice_reverses_the_edit_without_git`, for the three moved texts).
- [ ] **Step 2: Run** `cd ts && bun test tests/hook`; expected: FAIL.
- [ ] **Step 3: Implement**; add `#hook` to `ts/package.json`'s `imports`; set the row's `why` in `parity.json`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 5: Preparing and making an import

**Files:**
- Create: `ts/src/app/importing.ts`
- Modify: `ts/src/app/index.ts`, `ts/tests/app/front-door.test.ts` (the names below among the allowed additions)
- Test: `ts/tests/app/importing.test.ts`, `ts/tests/app/import-store.test.ts` (new)

**Interfaces:**
- Consumes: `#core`'s `tree`, `load`, `checkChange`, `parseRecord`, `writeRecord`, `parseThread`, `writeThread`, `CoreSettings`, `Problem`, `problem`, `ATTACHMENTS` (with plan 2's `people`, Task 10); `#app`'s `Store`, `Projects`, `Role`, `person`, `PublishOutcome`, `Clock`, `stampOf`, `coreSettings(table)` (the one throwing `LodgeError`, not `#core`'s default-filling namesake), `LodgeError`, `Conflict`, `Forbidden` (plan 2, Tasks 2 and 11); plan 2's `MemoryStore`, `FixedClock`, and `START` in the tests.
- Produces, through `#app`:
  ```ts
  export interface ZeroTwoCopy {
    readonly rev: string
    readonly files: ReadonlyMap<string, string>                  // every file under lodge/, as git's readStore gives them
    readonly settings: Readonly<Record<string, unknown>>         // the [length] and [import] tables of the store's .lodge.toml
  }
  interface PreparedImport {
    readonly problems: readonly Problem[]                        // nothing is imported unless empty
    readonly stage: "lodge 0.2" | "server" | null                // which check found them
    readonly files: ReadonlyMap<string, string>                  // every record, area, thread, and attachment to write, mapped
    readonly mapped: readonly string[]                           // the decisions and threads whose author became the owner, by ID
  }
  type Imported =
    | { readonly kind: "imported"; readonly rev: string; readonly decisions: number; readonly entries: number; readonly areas: number; readonly threads: number; readonly attachments: number; readonly mapped: readonly string[] }
    | { readonly kind: "check-failed"; readonly stage: "lodge 0.2" | "server"; readonly problems: readonly Problem[] }
  export function prepareImport(copy: ZeroTwoCopy, owner: string, people: ReadonlySet<string>, settings: CoreSettings, now: string): PreparedImport
  export function importStore(copy: ZeroTwoCopy, project: string, requester: string, projects: Pick<Projects, "members" | "storeFor">, settings: CoreSettings, clock: Clock): Promise<Imported>
  ```
  `PreparedImport` and `Imported` are not exported, since callers read the results' fields; `importing.test.ts` reads `ZeroTwoCopy` (the copy it builds is typed with it) and `prepareImport`, and `import-store.test.ts` reads `importStore`.
  `importStore` takes only the two methods it calls, so a method plan 3 adds to `Projects` changes neither it nor its test's stand-in (correctness review I-4).
- `prepareImport` (d-sdpcyb, d-83kt6y, d-ryss91), `settings` being the project's on the server, `now` a stamp, `empty` = `load(tree({ rev: null, files: new Map() }))`:
  1. Checks the store as `lodge add` checks a change, every decision being new: `checkChange(empty, load(tree({ rev: null, files, attachments })), coreSettings(copy.settings), now)`, the attachments' paths in `attachments` and every other file in `files`, `people` left to `tree()`'s default `{author}`, so a decision imported from a source the store's `.lodge.toml` does not list fails check 4 and a decision dated after `now` fails check 1, as lodge 0.2's `check_change` gives them (probe 9); any problem ends here, with `stage` `"lodge 0.2"` and `files` empty.
     A store's history raises no check 6 here, since the replaced statuses are derived from the empty state: `check_change` from an empty state finds no problem on this repository's 374 files of records (probe 9).
  2. Maps each decision whose `decidedBy` is `author` to `owner`: its new text is `writeRecord` of the decision with `decidedBy: owner`; each thread holding a message `by: author` likewise, `writeThread(thread with those messages by owner, people)`.
     A file whose writer does not give its unchanged text back byte for byte (`writeRecord` of the parsed decision, or `writeThread` of the parsed thread with its default people) is refused as a problem of check 1 at its path with the message `lodge 0.2 did not write this file as lodge writes it, so the importer cannot change who wrote it alone`, `stage` `"lodge 0.2"`.
  3. Gives every other file unchanged, but the paths ending `/.gitkeep`, which `load` skips (`src/lodge/core/snapshot.py:68`) and the export writes back (Task 6).
  4. Checks the mapped state as the server checks a write: a path holding U+DC80 to U+DCFF, a file name that is not UTF-8, is a problem of check 1 at its path, `this file's name is not UTF-8, which the server cannot store; rename it in the lodge 0.2 store and import again`, since plan 2's `publish` refuses a path holding a surrogate (d-j28rp0) and would otherwise throw after both checks passed; then `checkChange(empty, load(tree({ rev: null, files, attachments, people })), settings, now)`; any problem ends here, with `stage` `"server"` and `files` empty.
     So a project whose settings do not list the store's `[import]` sources fails check 4 here, as an add would, and an agent decision whose role is the owner's name reads as the owner's decision without a quote and fails check 3.
  Nothing else changes: IDs, dates, codes, `imported_from`, quotes, and every other line keep their bytes, as design line 289 asks.
- `importStore` (d-sdpcyb), in this order, writing nothing on any refusal:
  - the project's owners are the members of `projects.members(project)` with `Role.OWNER`; none or more than one is `LodgeError("project <name> has <n> owners; lodge imports into a project with one owner")`;
  - a `requester` who is not that owner is `Forbidden("only <owner>, the owner of project <name>, may import into it")`;
  - `store = projects.storeFor(project, person(owner))`; `[current] = await store.trees()`; a current state holding any file or attachment is `Conflict("project <name> already holds records; lodge imports a store into an empty project only")`;
  - `prepareImport(copy, owner, current.people, settings, stampOf(clock.now()))`; problems give `{ kind: "check-failed", stage, problems }`;
  - `store.publish(current, files, "Import the lodge 0.2 store at <rev>")`; `REJECTED` is `Conflict("project <name> changed during the import; nothing was imported")`;
  - otherwise `{ kind: "imported", … }`, the counts by path (`lodge/decisions/`, `lodge/spec/` but `_area.md`, `_area.md`, `lodge/threads/`, `lodge/attachments/`).
  Each imported file is written once, in that one publish into an empty project, so the store's refusal of a decision file's new text (d-j28rp0) cannot fire; a decision imported unchanged and later drafted and added back is refused by the store when lodge renders it differently from its lodge 0.2 bytes, which d-j28rp0 accepts, and no task's test re-adds an imported decision.
  The thread messages it writes under the owner's name go through `Store.publish` of the owner's own store, never through `ask` or `reply`, whose hold of an agent's relay and refusal of another person's name (d-2v8vtk) are not on this path; the requester is that owner, signed in, so each such message is written by the person it names and is published with the import, not held.

- [ ] **Step 1: Write the failing tests**, each with a clock at `2026-11-03T00:00:00+00:00`, after the made-up store's newest date (probe 9).
  - `importing.test.ts`, over Task 1's `ZERO_TWO_STORE` as a `ZeroTwoCopy` (`settings` from its `.lodge.toml`) with the owner `ana`, `people` `{ana}`, and the project settings `coreSettings(copy.settings)`: `clean_store_prepares_every_file` (the eight files of `ZERO_TWO_STORE` under `lodge/` that do not end `/.gitkeep`, named by path: four decisions, one entry, one area, one thread, and one attachment; `problems` empty); `author_decisions_name_the_owner` (the three author decisions, the imported one included, now read `decided_by: ana`, and each mapped text differs from the original in that line only); `agent_decision_is_unchanged`; `author_message_names_the_owner` (the thread's reply reads `by: ana` and differs in that line only; its `when` and `where` keep their bytes); `ids_dates_codes_and_imported_from_are_kept`; `failing_store_prepares_nothing` (the store's `[import]` sources emptied: check 4, `d-40q44p: imported from docs/choices.md, which is not listed in [import] sources`, `stage` `"lodge 0.2"`, and `files` empty, probe 9); `store_dated_after_now_is_refused` (`now` plan 2's `START`, 2026-10-29T09:30:00+01:00: check 1 for `d-q59cdf`, `d-qqrf9k`, and `d-t46j05`, `stage` `"lodge 0.2"`, probe 9); `stray_file_fails_the_check` (a `lodge/notes.txt`); `undecodable_record_refuses_the_import` (a decision holding U+DCFF: problem 1, `stage` `"lodge 0.2"`); `file_the_writer_would_not_give_back_is_refused` (an author decision with its keys in another order); `mapped_state_is_checked_with_the_project_settings` (project settings `coreSettings({})`, which list no source: check 4 for `d-40q44p`, `stage` `"server"`); `owner_name_used_as_a_role_fails_the_server_check` (an agent decision `decided_by: ana` without a quote added to the store, which passes the first stage: check 3, `stage` `"server"`); `undecodable_name_is_refused` (a path under `lodge/spec/storage/` holding U+DCFF: its sentence, `stage` `"server"`); `owner_named_author_changes_nothing` (owner `author` and `people` `{author}`: every file as read).
  - `import-store.test.ts`, over plan 2's `MemoryStore` built with `people` `{ana}`, the owner (its default `{author}` would check the mapped state as if `ana`'s decisions were a role's), and a stand-in with `members` and `storeFor` giving one store per project: `owner_imports_into_an_empty_project` (the answer's counts, and the store's `publishes` holds one publish of the eight files); `requester_must_be_the_owner` (`Forbidden`, nothing published); `project_with_two_owners_is_refused`; `project_with_records_is_a_conflict`; `failed_check_publishes_nothing`; `rejected_publish_is_a_conflict`; `now_is_the_clocks` (with `FixedClock` at `START`: `check-failed` with check 1, nothing published).
- [ ] **Step 2: Run** `cd ts && bun test tests/app/importing.test.ts tests/app/import-store.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement**; add the names to `front-door.test.ts`'s allowed additions.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 6: The export's files and its batching

**Files:**
- Create: `ts/src/app/exporting.ts`, `ts/src/app/exporters.ts`
- Modify: `ts/src/app/index.ts`, `ts/tests/app/front-door.test.ts` (the names below among the allowed additions)
- Test: `ts/tests/app/exporting.test.ts`, `ts/tests/app/exporters.test.ts` (new)

**Interfaces:**
- Consumes: `#core`'s `Tree`; `#app`'s `Clock`, `Store`, `Projects`, `Actor`, `PublishOutcome`, `LodgeError`; plan 2's `FixedClock` and `MemoryStore` and Task 1's `ZERO_TWO_STORE` in the tests.
- Produces, through `#app`:
  ```ts
  export interface ExportTarget { readonly repository: string; readonly branch: string; readonly remote: string | null }
  export type ExportOutcome = { readonly kind: "committed"; readonly commit: string } | { readonly kind: "unchanged" } | { readonly kind: "moved" }
  export interface ExportTargets {                                               // store's port, Task 7
    target(project: string): Promise<ExportTarget | null>;
    setTarget(project: string, target: ExportTarget | null, by: Actor): Promise<void>;
  }
  export interface ExportPorts {
    readonly clock: Clock
    readonly targets: ExportTargets
    readonly storeFor: (project: string) => Store                                 // the project's store, unwrapped
    readonly write: (target: ExportTarget, files: ReadonlyMap<string, string>, message: string) => Promise<ExportOutcome>
    readonly failed: (project: string, error: unknown) => void                    // the server logs it
  }
  export const EXPORT_INTERVAL_SECONDS = 60
  export const KEPT: readonly string[]                                          // lodge/decisions/.gitkeep, lodge/spec/.gitkeep
  export function exportTargetProblem(target: ExportTarget): string | null      // the export-target operation's refusal, Task 8
  export function exportFiles(current: Tree, attachmentTexts: ReadonlyMap<string, string>): ReadonlyMap<string, string>
  export function exportMessage(files: ReadonlyMap<string, string>): string
  export function exportFailedLine(project: string, error: unknown): string     // "lodge: the export of <project> failed: <message>\n"
  export class Exporters {
    constructor(ports: ExportPorts);
    written(project: string): Promise<void>;                                    // resolves when the run covering this write ends
    start(projects: readonly string[]): Promise<void>;                          // written() for each project with a target
    settled(): Promise<void>;                                                   // every run ended
  }
  export function exportingProjects(projects: Projects, written: (project: string) => void): Projects
  ```
- `exportTargetProblem` gives `export-target: repository must be an absolute path` for a `repository` that does not start with `/`, `export-target: branch must be a name of letters, digits, and . _ / -, not starting with a symbol` for a branch `_name`'s rule refuses (`src/lodge/gitstore/settings.py:76-83`: letters, digits, and `. _ / -`, not starting with a symbol, no `..`), `export-target: remote must not start with -` for a `remote` that does (a remote is a name or a path, so `_name`'s rule would refuse a path), and null otherwise, the branch and remote sentences being Task 3's, so a mistyped target is refused when it is set rather than failing every minute (correctness review M-12).
- `exportFiles` gives every file of `current.files` but the `/.gitkeep` paths, each attachment's text, and `KEPT` with the empty text, as `lodge init` lays a store out (`src/lodge/gitstore/trees.py:10`, `src/lodge/gitstore/setup.py:47-56`), so the export has lodge 0.2's file layout in either store mode (d-sj6hmf; d-b61590: the layout, not lodge 0.2's check).
- `exportMessage` is `Export lodge records: <d> decisions, <e> entries, <a> areas, <t> threads`, counted from the paths.
- `exportFailedLine` is `lodge: the export of <project> failed: <message>` and a newline, `<message>` the error's `message` for an `Error` and `String(error)` otherwise; `main.ts` and the test worlds pass `(project, error) => log(exportFailedLine(project, error))` as `failed`, so the line is under test here rather than only in `main.ts` (preflight M17).
- Readers in this task: `exporting.test.ts` reads `KEPT`, `exportFiles`, `exportMessage`, `exportFailedLine`, `exportTargetProblem` (its targets typed `ExportTarget`), and `exportingProjects`; `exporters.test.ts` reads `Exporters`, `EXPORT_INTERVAL_SECONDS`, and the types `ExportPorts`, `ExportTargets`, and `ExportOutcome`, with which it types its ports, its fake targets, and its recording `write`.
- `Exporters` (design line 285; d-sj6hmf), one run at most per project at a time:
  - `written(project)` notes a pending write; when no run is going for the project, it starts one, and otherwise the running one takes the write.
  - A run loops while a write is pending: it waits `EXPORT_INTERVAL_SECONDS` after the project's last commit by `clock.now()` with `clock.sleep(seconds)` (no wait before the first commit, or when the last is a minute old or more), clears the pending mark, and flushes: with no target from `targets.target(project)`, nothing; otherwise `write(target, exportFiles(current, await store.attachmentTexts()), exportMessage(…))`, `current` the first tree of `storeFor(project).trees()`.
    `committed` notes the commit's time; `unchanged` notes nothing; `moved`, or `write` throwing (given to `failed`), marks a write pending again after `clock.sleep(EXPORT_INTERVAL_SECONDS)`.
  - So two commits of one project within one run of the server are at least a minute apart, writes within that minute share the next commit, and a write is exported within a minute of the last commit; the last commit's time lives in memory, so after a restart `start` exports at once, which may follow the last commit before the stop by less than a minute (correctness review M-6).
  - `app` reads the time only from `clock.now()` and waits only through `clock.sleep` (`CLAUDE.md`, "Structure checks").
- `exportingProjects` (d-j5s0h0, d-v0r9cb) gives a `Proxy` over `projects` whose `storeFor(project, actor)` gives the inner store wrapped in a `Proxy` whose `publish` calls `written(project)` after an answer of `PUBLISHED` and before it returns, an approving `publish` (with `approves`, plan 2's Tasks 12a to 12c, an approved add or relayed message) included; every other member of either, `hold`, `held`, and `decline` among them whatever the hold's kind, reaches the inner object with its arguments as given, bound to it, so `create`'s settings and any method plan 3 or a later plan adds pass through without an edit here (correctness review I-4, practice review P4-I5).

- [ ] **Step 1: Write the failing tests.**
  - `exporting.test.ts`: `export_files_hold_the_store_and_kept` (a `MemoryStore()` into which the test publishes the eight files of `ZERO_TWO_STORE` under `lodge/` that do not end `/.gitkeep`, the attachment among them, through `publish`, since its constructor takes records and not threads or attachments: `exportFiles` of its current tree and `attachmentTexts()` gives those eight texts and both `.gitkeep`, nothing else); `failed_line_names_the_project` (an `Error("boom")` and a string each give their line); `message_counts_the_records`; `target_problems_are_named` (a relative repository, a branch `-x`, `a..b`, and `a b`, and a remote `-r`, each with its sentence; a target with a remote that is an absolute path null); `wrapped_store_tells_the_exporter_after_a_publish` (a recording `written`: one call after `PUBLISHED`, none after `REJECTED`); `wrapped_store_passes_every_other_method` (`trees`, `attachmentTexts`, `held`, and the rest reach the inner store); `wrapped_projects_pass_every_method_with_its_arguments` (over a recording stand-in for the inner `Projects`, built as a `Proxy` so that it needs no edit when `Projects` grows: `members`, `addMember`, and `create`, each called with the arguments plan 2's `Projects` declares, reach it with the same arguments and give its answer back; `create`'s third argument, plan 3's settings, is Task 8's `project_settings_survive_the_wrapper`, since a call with it fails `tsc` before plan 3 merges).
  - `exporters.test.ts`, with `FixedClock` (whose `sleep` moves its time and records `slept`) and a `write` that records its calls: `first_write_exports_at_once` (nothing slept, one `write`); `writes_within_a_minute_share_one_commit`, with a test-local clock whose `sleep` records its seconds and resolves only when the test calls `release()`, moving the time then (plan 2's `FixedClock` resolves at once, so no write could land during the wait; correctness review M-4, practice review P4-M4): a commit, then a write 10 seconds later starts a run held in `sleep(50)`, two more writes arrive while it is held, `release()`: one more `write` in all and `slept` `[50]`; `write_a_minute_after_exports_at_once`; `no_target_writes_nothing`; `unchanged_counts_no_commit` (after `unchanged`, the next write exports at once); `moved_retries_a_minute_later`; `failure_is_reported_and_retried` (`failed` gets the project and the error, `slept` holds 60, and the second `write` succeeds); `projects_batch_apart` (writes to two projects each export at once); `start_exports_projects_with_a_target`.
  - Every target a test sets is one whose `write` succeeds or fails a counted number of times, so no run retries without end under `FixedClock` (practice review P4-M5).
- [ ] **Step 2: Run** `cd ts && bun test tests/app/exporting.test.ts tests/app/exporters.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement**; add the names to `front-door.test.ts`'s allowed additions.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 7: Export targets in the store

**Files:**
- Create: `ts/src/store/export-targets.ts`
- Modify: `ts/src/store/events.ts` (the kind's case in `applyEvent`), `ts/src/store/index.ts`
- Test: `ts/tests/store/export-targets.test.ts` (new)

**Interfaces:**
- Consumes: Task 6's `ExportTargets`, `ExportTarget`; plan 2's `LodgeDatabase`, `openDatabase`, `appendEvents`, `actorText`, `stampOf`, `Clock`, `encodeUtf8`, and `decodeUtf8` (Tasks 2, 7a, and 7b).
- Produces, through `#store`: `SqliteExportTargets implements ExportTargets` (`constructor(database: LodgeDatabase, clock: Clock)`).
- `setTarget` appends one event of the kind `export-target` for the project, the actor `actorText(by)`, `at` `stampOf(clock.now())`, and the body `encodeUtf8` of the JSON `{"target": …}`; `target(project)` reads the project's newest such event, decodes its body with `decodeUtf8` (d-0q54zn: a `TextDecoder` would turn an escaped byte of a repository path into U+FFFD, correctness review M-3), and gives its target, null when there is none or the newest holds null (d-j5s0h0).
- The task adds no migration and no derived table; plan 2's `MIGRATIONS[1]` creates the `held` table (with `at`, plan 2's Task 12a) and plan 3's `MIGRATIONS[2]` its accounts' tables (`user_version` 2 to 3, plan 3's Task 4), so a migration a later change of this plan needed would be `MIGRATIONS[3]` or later.
- `applyEvent` gains the case `export-target`, which changes no derived table beyond what it does for every kind, as plan 2's rule for a new kind says ("Interfaces for plans 3 and 4"), so `rebuild` accepts the event.
- `setTarget` runs in one transaction whose first statement is a write, `update heads set rev = rev where project = :project` (d-thvvzx, plan 2's rule for a store transaction that reads before it writes); no row matched is `NotFound` as plan 2's `Projects` words an unknown project, and nothing is written; then `appendEvents` appends the event, which moves the project's `rev` as every event does, so a publish racing it is `REJECTED` and retried as any racing write is.
- Task 8's `export-target` answers an unknown project `no-project` before it reaches the store, as `import` does, so this `NotFound` is the store's guard, not an answer the API gives (preflight M8).
- Readers in this task: `export-targets.test.ts` reads `SqliteExportTargets`.

- [ ] **Step 1: Write the failing tests** in `export-targets.test.ts`, over plan 2's store on `:memory:` with a project `work`: `no_target_is_null`; `target_set_is_read_back`; `escaped_path_is_read_back` (a repository path holding U+DCFF comes back equal); `newest_target_wins`; `null_stops_the_target`; `target_is_an_event` (kind, actor, `at`, and body); `rebuild_keeps_the_target`; `unknown_project_is_not_found`.
- [ ] **Step 2: Run** `cd ts && bun test tests/store/export-targets.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 8: Import and export in the server

This task builds after plan 3 is merged and extends plan 3's code by names only (d-s83a6e): each addition below names its file and signature, and none changes the shape of a name plan 3 produces.
Where plan 3's merged code already has a function this task describes, the coordinator names it in the brief and the task uses it (the rule under "Names this plan consumes").

**Files:**
- Create: `ts/src/api/moving.ts`, `ts/src/cli/zero-two.ts`
- Modify: the file of plan 3's Task 5 that declares `ApiOptions` (`moving`), `ts/src/api/person.ts` (two operations), `ts/src/api/index.ts`, `ts/src/cli/settings.ts` (`tomlTable`), `ts/src/cli/index.ts`, `ts/src/main.ts`, `ts/tests/api/world.ts`
- Test: `ts/tests/api/import.test.ts`, `ts/tests/api/export-target.test.ts`, `ts/tests/cli/zero-two.test.ts` (new)

**Interfaces:**
- Consumes: Tasks 2, 3, 5, 6, and 7; plan 2's store and `Projects` with plan 3's additions; plan 3's handler, `ApiOptions` (`clock` and `log` among them), `lodgesOver`, `issueSetupCode`, the person's operations of `person.ts`, `Accounts`, `world.ts`, `SoftAuthenticator`, and `readSettings`' parsing steps.
- Produces, through `#cli` (preflight M1):
  ```ts
  // settings.ts, factored out of readSettings, which then calls it; readSettings answers as before
  export function tomlTable(text: string): Readonly<Record<string, unknown>>
  // zero-two.ts
  export function zeroTwoCoreTable(text: string): Readonly<Record<string, unknown>>
  ```
  `tomlTable` is `readSettings`' parsing and conversion of plan 3's Task 3, on text: smol-toml with `integersAsBigInt: true`, a `bigint` made a number, a float (`inf` and `nan` included) or a date or time made `null`, every top-level name kept; a text that is not TOML is `CliError(".lodge.toml: <smol-toml's first line>")`; plan 3's `settings.test.ts` keeps passing unchanged, which shows `readSettings` answers as before.
  `zeroTwoCoreTable` refuses a text holding U+DC80 to U+DCFF, a file that is not UTF-8, with `CliError(".lodge.toml: cannot be read: not UTF-8")`, as lodge 0.2 refuses to read it (`src/lodge/gitstore/settings.py:41-45`; correctness review M-3), and otherwise gives the `length` and `import` tables of `tomlTable(text)` only, every other top-level name ignored, since a lodge 0.2 file may hold `[store]` and `[hook]`.
- Produces, through `#api`:
  ```ts
  export interface Moving {
    readonly read: (repository: string, rev: string, settingsRev: string) => Promise<ZeroTwoCopy>   // main joins #git's readStore and #cli's zeroTwoCoreTable
    readonly targets: ExportTargets
    readonly exporters: Exporters
  }
  // moving.ts; each answers its result, with checkFailed true for an import whose check failed
  export function importOperation(options: ApiOptions, signedIn: string, body: Readonly<Record<string, unknown>>): Promise<{ readonly checkFailed: boolean; readonly result: unknown }>
  export function exportTargetOperation(options: ApiOptions, signedIn: string, body: Readonly<Record<string, unknown>>): Promise<{ readonly checkFailed: false; readonly result: { readonly target: ExportTarget | null } }>
  ```
  and `ApiOptions` gains `readonly moving?: Moving`, optional, so every other literal of `ApiOptions` (plan 3's e2e `server.ts`, the `open` of its `setup.test.ts`, and any other) compiles unchanged (preflight M15); without it both operations throw `LodgeError("this server was started without import and export")`.
  `ApiOptions.projects` is `exportingProjects(sqliteProjects, (project) => void exporters.written(project))`, given to `lodgesOver` too, so every publish, through `Lodge` or the import, tells the exporter; `exporting.ts` needs no change for plan 3's `Projects` methods, which its `Proxy` forwards (d-v0r9cb).
- The operations (preflight M16): `person.ts`'s person operations gain `import` and `export-target`, dispatched as `approve` is, so an agent's token is `forbidden` with `only the signed-in person may <operation>`, the session and its `Origin` are checked as for the others, each body's fields are checked with plan 3's sentences (`<operation>: <field> must be <what>`, `<operation>: unknown field <name>`, both `usage`), a `checkFailed` answer is answered 422 as `person.ts` answers `approve`'s `CHECK_FAILED` (`{"error": {"kind": "check-failed", "message": "the check failed"}, "result": …}`), any other answer 200 with its `result`, and a thrown error maps by class (`Forbidden` 403, `Conflict` 409, `LodgeError` 400); each body holds `project`:
  - `import` (`repository`, `rev`, and `settingsRev`, a string defaulting to `rev`, which names the base branch of a branch-mode store; d-1skjw1, d-sdpcyb): `projects.settings(project)` null is `no-project`; `moving.read(repository, rev, settingsRev)`; `importStore(copy, project, signedIn, options.projects, coreSettings(settings), options.clock)`; `checkFailed` when its kind is `check-failed`.
  - `export-target` (`target`, an object of `repository`, `branch`, and `remote` (a string or null), or null): `projects.settings(project)` null is `no-project`, as for `import` (preflight M8); `exportTargetProblem(target)` not null is `usage` with it; then `targets.setTarget(project, target, person(signedIn))`, then `void exporters.written(project)` when the target is not null, and the result `{"target": …}`.
- `main.ts`, in plan 3's `open(data)`: `SqliteExportTargets` over the opened store; `Exporters` with the real clock, `storeFor` = the inner `SqliteProjects`' `storeFor(project, agent("exporter"))`, `write` = `#git`'s `exportStore`, and `failed` = `(project, error) => log(exportFailedLine(project, error))`, `log` the one `open` gives `ApiOptions`; `ApiOptions.projects` = `exportingProjects(sqliteProjects, …)` and `lodgesOver` over it; `moving.read` = `readStore(repository, rev, settingsRev)` then `zeroTwoCoreTable` of its `settings` (`{}` when null), a `CliError` thrown again as a `LodgeError` with its message.
  The exports a stopped server left pending start with serving, not with `open` (preflight M10): `main.ts` keeps the `Exporters` and `Projects` of its last `open` in variables of the `ServerIo` it builds, and its `listen` runs `void exporters.start(await projects.names())` before it awaits `#api`'s listen; `setup` opens the store but never listens, so it starts no export.
  That call and the `ServerIo` closure are read in review, since no test imports `main.ts`; the failure line is `exportFailedLine`'s, tested in Task 6 (preflight M17).
- `world.ts` (preflight M2, M3) builds `moving` as `main.ts` does over its in-memory store, its `FixedClock`, and its `log`, with a `read` over `#git`'s `readStore` and `zeroTwoCoreTable`, and the object it gives the tests gains:
  ```ts
  readonly exporters: Exporters
  readonly targets: ExportTargets
  createProject(project: string, settings: Readonly<Record<string, unknown>>): Promise<void>       // options.projects.create(project, "ada", settings), through the wrapper
  asPerson(operation: string, body: Readonly<Record<string, unknown>>): Promise<Response>        // the signed-in person's request
  ```
  `asPerson`, on its first call, takes a code from `issueSetupCode(options)`, registers a passkey of plan 3's `SoftAuthenticator` through `register-options` and `register` with that code, and keeps the `lodge_session` cookie of the answer; each call then sends `POST /api/v1/<operation>` with that cookie, `Origin: https://lodge.test`, and the JSON body, as plan 3's `person.test.ts` signs in (plan 3, Task 6).
  `createProject` creates the project directly, as the world creates `work`, so no test depends on whether a session may call `project-create`.
  The world's person is `ada`, so an import maps `decided_by: author` to `ada`, which the tests can see; the e2e `testServer()`, whose person is `author` (plan 3, Task 7a), is not used by this plan, and `server.ts` is unchanged.
  The made-up store's decisions are dated 2026-11-02T18:56:28+01:00 to 18:56:30+01:00 and the world's `FixedClock` starts at 2026-10-29T09:30:00+01:00, so a test importing it first moves the clock on with `await clock.sleep(432000)`, five days; otherwise the import fails check 1 (probe 9).
- Readers in this task: `world.ts` reads `Moving`, `importOperation` and `exportTargetOperation` are read by `person.ts`, and the tests below read the world's additions; `zero-two.test.ts` reads `zeroTwoCoreTable`, and `zeroTwoCoreTable` reads `tomlTable`.

- [ ] **Step 1: Write the failing tests**, each calling the handler with a `Request` and no socket, over a fresh `world.ts` per test (so each layout imports into an empty `moved`), each repository from `zeroTwoRepository` with `isolateGit()`, the import into a project `moved` made with `createProject("moved", {"import": {"sources": ["docs/choices.md"]}})`, the store's own sources, and an agent token for `moved` from `asPerson("token-issue", { project: "moved", label: "t", role: null })`:
  - `import.test.ts`: `person_imports_the_made_up_store` (both layouts, the branch layout passing `settingsRev`: the answer's counts, and `show` of each author decision through the agent token names `ada`); `agent_token_is_forbidden`; `second_import_is_a_conflict`; `failing_store_answers_check_failed` (the store's `[import]` sources emptied: 422 with check 4 at `stage` `"lodge 0.2"`, and `search` finds nothing); `project_without_the_sources_answers_check_failed` (a project made with `{}`: 422 with check 4 at `stage` `"server"`); `branch_layout_without_its_settings_fails_check_4` (the branch layout without `settingsRev`: 422 with check 4 at `stage` `"lodge 0.2"`); `missing_revision_is_usage`; `unknown_field_is_usage`; `unknown_project_is_no_project`; `imported_records_read_as_imported` (`show` of the imported decision says imported and unquoted, as `test_import_needs_the_flag_and_a_listed_source` asserts in lodge 0.2); `project_settings_survive_the_wrapper` (`projects.settings("moved")` through `ApiOptions.projects` gives the table `createProject` gave, practice review P4-I5).
  - `export-target.test.ts`: `person_sets_the_target`; `agent_token_is_forbidden`; `bad_target_is_usage` (a branch `-x`: `usage` with Task 6's sentence, nothing stored); `unknown_project_is_no_project`; `write_after_target_exports` (the person sets a bare repository from `mkdtempSync` as the target, an agent's `add` follows, and after `world.exporters.settled()` the branch holds the new decision); `null_target_stops_the_export`.
    No test sets a target whose export fails, since under `FixedClock` each retry's sleep resolves at once and the run would not end (practice review P4-M5); Task 6's `failure_is_reported_and_retried` covers the retry with a `write` that fails once.
  - `zero-two.test.ts`: `core_tables_are_kept` (`[length]` and `[import]`); `store_and_hook_are_ignored`; `whole_number_float_is_refused_as_the_command_refuses_it` (`title_chars = 80.0`, then `parseCoreSettings` gives lodge 0.2's sentence); `not_utf8_is_one_sentence` (a text holding U+DCFF); `not_toml_is_one_sentence`.
- [ ] **Step 2: Run** `cd ts && bun test tests/api/import.test.ts tests/api/export-target.test.ts tests/cli/zero-two.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green, `tsc` accepting `exportStore` as the exporters' `write`, and plan 3's `ts/tests/cli/settings.test.ts` and `ts/tests/api` passing unchanged.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 9: The hook in the command

**Files:**
- Create: `ts/src/cli/hook-context.ts`, `ts/tests/hook/repository.ts` (helper)
- Modify: `ts/src/cli/grammar.ts`, `ts/src/cli/commands.ts` (or where plan 3's `run` dispatches), `ts/src/cli/settings.ts` (`[hook]` checked), `ts/src/cli/index.ts`, `ts/src/main.ts`, `ts/tests/cli/settings.test.ts` (plan 3's `hook_is_left_alone` becomes `hook_is_checked`), `ts/tests/cli/grammar.test.ts`, `ts/tests/e2e/help-lists-every-command.test.ts`, `ts/tests/parity.json`
- Test: `ts/tests/hook/hand-edits.test.ts`, `ts/tests/hook/outside-repository.test.ts` (carried)

**Interfaces:**
- Consumes: Task 4's `#hook` and `parseHookSettings`; Task 2's `repoRootOf`, `isFolder`, `resolvePath`, and `isolateGit`; plan 3's grammar, `run`, `Io`, and `readSettings`.
- Produces, through `#cli` (d-bs5mm8):
  ```ts
  export function hookContextFor(
    edited: string,
    git: { readonly repoRootOf: (edited: string) => Promise<string>; readonly isFolder: (path: string) => boolean },
  ): Promise<{ readonly repoRoot: string; readonly dataRoot: string | null; readonly frozen: readonly string[]; readonly server: string | null } | null>
  ```
  and `Io` gains `readonly hook?: () => Promise<number>`, optional, so that no `Io` of plan 3's tests changes and Tasks 8 and 9 do not meet in the e2e helpers (practice review P4-M8).
- `hookContextFor` is `_hook_context` (`src/lodge/main.py:73-78`): `repoRootOf(edited)`; `.lodge.toml` at that root read as plan 3's `readSettings` reads its bytes, strictly, so a file that is not UTF-8 gives null as lodge 0.2's `cannot be read` does (`src/lodge/gitstore/settings.py:41-45`, which `run` swallows; correctness review M-3), and parsed with smol-toml, every top-level name allowed; `server` the `[server]` table's `url`, null without one; `[store] mode`, `"checkout"` when absent; `frozen` from `parseHookSettings` of `[hook]`; for a project that has not moved and is in checkout mode, null unless `<root>/lodge/decisions` and `<root>/lodge/spec` are folders (`holds_records`); `dataRoot` `<root>/lodge` in checkout mode and null in branch mode; any error, a malformed file or a `[server]` without a string `url` included, gives null, so the hook stays silent.
- The grammar takes `hook EVENT` as `src/lodge/cli/parser.py:90-91` does: `argv[0]` `hook` with no `-h` or `--help` in `argv` gives `{ kind: "hook", event: argv[1] ?? "" }` before any other parsing; the help lists `hook` with lodge 0.2's summary `answer a Claude Code hook event: post-tool-use`, and `lodge hook -h` prints argparse's help for it.
- `run` answers the `hook` command before reading any setting: `io.hook()` for `post-tool-use`, 0 for any other event or when `io.hook` is absent (`src/lodge/cli/commands.py:91-92`).
- `readSettings` checks `[hook]` with `parseHookSettings`, a `LodgeError` becoming a `CliError` with its message, as `_settings` does (`src/lodge/main.py:41-45`), so a malformed `[hook]` exits 2 with one sentence before any request; plan 3's `hook_is_left_alone` becomes `hook_is_checked` (a `[hook] frozen = "x"` refused with `parseHookSettings`' sentence, and a well-formed `[hook]` read as before; correctness review M-11).
- `main.ts` gives `io.hook` as `run` of `#hook` with `() => Bun.stdin.text()`, `(text) => process.stdout.write(text)` as `out` (d-d0vca9), `(edited) => hookContextFor(edited, { repoRootOf, isFolder })`, `resolvePath`, and `process.cwd()` (null when it throws).
- `repository.ts` (helper): `hookProject()` makes a real repository in a folder from `mkdtempSync` with `git init -b main` under `isolateGit()`, with `configure(text)` writing `.lodge.toml` as given (no `[server]` unless the test writes one), `initialise()` writing `lodge/decisions/.gitkeep` and `lodge/spec/.gitkeep` and staging them with `git add --`, as `init_store` does (`src/lodge/gitstore/setup.py:47-56`), where the Python test ran `lodge init`, so its next `git commit` has something to commit (correctness review M-1, practice review P4-M6), `git(...args)` through `#git`'s `run`, and `run(argv, input?, cwd?)` calling `#cli`'s `run` with an `Io` whose `hook` is built as `main.ts` builds it but reads `input`, and whose `fetch` throws, since no carried hook test reaches a server.

- [ ] **Step 1: Write the failing tests:** every test of `tests/e2e/test_hook_feedback_after_hand_edits.py` and `tests/e2e/test_hook_outside_repository_exit_0_silent.py` by name, each parametrised case kept, through `hookProject()`; and, in `hand-edits.test.ts`, `hook_gives_the_moved_advice_for_a_project_on_the_server` (a `.lodge.toml` with `[server]` naming `https://lodge.test`: an edit under `lodge/decisions/` names it, in branch mode too); add `hook` to the names of plan 3's `help_lists_every_command`, `every_command_has_help`, and `help-lists-every-command.test.ts`.
- [ ] **Step 2: Run** `cd ts && bun test tests/hook tests/cli tests/e2e/help-lists-every-command.test.ts`; expected: the new and changed tests FAIL.
- [ ] **Step 3: Implement**; flip `tests/e2e/test_hook_outside_repository_exit_0_silent.py` to `ported`, and set the `why` of the two `changed` rows of "Parity rows this plan settles".
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`; build the binary as plan 3's Task 8 does, then `printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"},"cwd":"%s"}' "$PWD/lodge/decisions/x.md" "$PWD" | ts/dist/lodge hook post-tool-use` prints lodge 0.2's record advice for this repository, which has not moved; commit, push.

### Task 10: The round trip

**Files:**
- Create: `ts/tests/api/round-trip.test.ts`, `ts/scripts/round-trip.ts`, `scripts/round-trip.sh`
- Modify: `ts/tests/parity.test.ts` (the plan 4 rows)
- Report: `docs/superpowers/plans/2026-11-02-lodge-server-import/task-10-report.md`

**Interfaces:**
- Consumes: Tasks 2 to 9: Task 1's `ZERO_TWO_STORE` through Task 2's `zeroTwoRepository` (with its `extra`), `readStore`, and `isolateGit`; Task 5's `importStore` and `ZeroTwoCopy`; Task 6's `exportFiles` and `exportMessage`; Task 3's `exportStore`; Task 8's `zeroTwoCoreTable` and its additions to `world.ts` (`exporters`, `targets`, `createProject`, `asPerson`).
- Produces: the proof of this plan's end, and the coordinator's run on a scratch copy of lodge's own records (d-2jk0mw).
- Nothing here writes into this repository: every repository the test and the scripts make or export to is in a folder from `mkdtempSync` or `mktemp -d`, since this repository's gate (`scripts/check.sh`, `uv run lodge check --gate`) and `scripts/differential.sh` read its own `lodge/` with lodge 0.2, which an export naming the person would fail (d-b61590, probe 7).
- Each store is imported once and exported; no step drafts or re-adds an imported decision, which the store would refuse when lodge renders it differently from its lodge 0.2 bytes (d-j28rp0).
- `round-trip.test.ts`, through the handler of Task 8's `world.ts` in process with `isolateGit()` (its person `ada`, so the mapping is visible, and its `FixedClock`, moved on with `await clock.sleep(432000)` past the made-up store's dates; preflight M4): `made_up_store_survives_import_and_export` (for each layout of `zeroTwoRepository`, the branch layout passing `settingsRev` and given `extra` `new Map([["lodge/attachments/d-q59cdf/raw.bin", "\uDCFF\uDCFE"]])`, an attachment of the bytes `ff fe` (preflight M5): the person imports it with `asPerson("import", …)` into a project made with `createProject("moved", <the store's [import] table>)`, sets an export target on a new bare repository with `asPerson("export-target", …)`, awaits `world.exporters.settled()`, and `readStore` of the exported branch gives the original's paths, every text equal byte for byte but the `decided_by: author` line of each author decision and the `by: author` line of the thread's reply, which read `ada`, the attachments equal (the added one's `encodeUtf8` the two bytes), and both `.gitkeep` files; correctness review M-8); `export_of_an_export_is_unchanged` (a second `world.exporters.written("moved")` and `settled()` leave the exported branch's tip where it was, practice review P4-M7).
- `parity.test.ts`: `ported_files_exist` also covers plan 4's `changed` rows, and `plan_4_changed_rows_keep_every_python_test_name` runs `rowMissing` on them, the row for `tests/hook/test_post_tool_use.py` against `post-tool-use.test.ts` alone.
- `ts/scripts/round-trip.ts REPOSITORY REV [SETTINGS_REV]` runs in process without the handler, since a script may import `src/` only through the `#…` names and so not `src/main.ts` (plan 1's dependency-cruiser `front-door` rule): it opens `openDatabase(":memory:")` with `SqliteProjects` over a `Clock` of its own (`now()` from `Date.now()` and the offset of the machine's time zone, `sleep(seconds)` as `Bun.sleep(seconds * 1000)`), reads the store with `readStore` and `zeroTwoCoreTable`, creates the project `round-trip` owned by the made-up person `ana` with the store's `[length]` and `[import]` tables, imports with `importStore(copy, "round-trip", "ana", projects, coreSettings(table), clock)`, exports with `exportStore(<a new bare repository in a temporary folder>, exportFiles(current, attachmentTexts), exportMessage(…))` (no `Exporters`, since one export is made), and compares the two stores file by file; it prints the counts of files compared, files equal, files differing only in `decided_by` or a message's `by`, and other differences (each path and the first line that differs), and exits 1 on any other difference.
- `scripts/round-trip.sh` clones this repository with `git clone --no-local --quiet` into a folder from `mktemp -d` (d-2jk0mw: a scratch copy, never the live store) and runs `bun ts/scripts/round-trip.ts <clone> HEAD`; it runs no lodge 0.2 command on the export, which need not read like a lodge 0.2 store beyond its file layout (d-b61590).
- The expected differences are the person's name in `decided_by` and in a message's `by`; a symbolic link under `lodge/` would come back as a regular file holding the path it names (Task 3), and neither store holds one.

- [ ] **Step 1: Write the failing test and the scripts.**
- [ ] **Step 2: Run** `cd ts && bun test tests/api/round-trip.test.ts tests/parity.test.ts`; expected: the round trip passes once Tasks 2 to 9 are merged, and any failure is fixed in the module at fault with a test that fails first.
- [ ] **Step 3: Coordinator:** `sh scripts/round-trip.sh` outside the sandbox; the report gives its counts as printed: at 0522047 the store held 221 decisions and 137 files under `lodge/spec/`, 46 of the decisions `decided_by: author`, no thread, and no attachment (probe 5), and the plans' rulings add more; `git status --short lodge/` is empty afterwards.
- [ ] **Step 4: Coordinator:** `sh scripts/check.sh`, commit, push.

### Tasks 11a, 11b, and 11c: The design into lodge

The server is built (plans 1 to 4), so what it makes false in lodge's specification is edited now (d-j3z85y), and the design goes in whole, so that its document can be frozen.
Each part is its own brief, build, and review, in this order, each holding the rules below as well as its part.

**Files:** records via `lodge add`; report `docs/superpowers/plans/2026-11-02-lodge-server-import/task-11-report.md`, which each part extends; in 11c also `docs/superpowers/specs/2026-11-02-lodge-server-design.md` (one line at the end), `.lodge.toml` (`[hook] frozen`), and `CLAUDE.md` (two lines).

**Interfaces:**
- Consumes: plans 1 to 4 built; the design; her eight decisions (d-8kasej, d-b1yjpp, d-d3js00, d-khew4n, d-ffk7wy, d-wc9wt2, d-zzfmj2, d-5ps72w); the records named below.
- Produces: one coordinator decision per design section, its entries, and the edits and narrowings below; about 50 to 80 new entries in all.

Rules for every part (as the viewer plan's Tasks 9a to 9c, `docs/superpowers/plans/done/2026-10-31-lodge-viewer.md:523-564`):
- `lodge add` as in the Global Constraints; `uv run lodge id s` per new entry.
- A coordinator decision per design section, `decided_by: coordinator`, `scope: product`, creating the entries for its section's claims, one per claim a reader would look up on its own, within 150 words, each with `rests_on` where it would not hold without another entry (the viewer plan's Task 8 rule).
- An entry states the design's claim as the specification, in the present tense; a claim that build step 1 did not build says from which step it holds, as in "From build step 4, the runner…", and rests on the entry for the build order (d-yng7m8).
- Areas: Intent, Goals, Non-goals, and Must nots in `purpose`; Constraints in `constraints`, but the structure rules in `structure`; the model and the new objects in `model`; Workflow as data, Tasks, the waiting list, Claimed and checked, Usage and stuck work, and Code and git in a new area `work` ("Tasks and workflows"); Sessions and Artefacts in a new area `sessions` ("Sessions and artefacts"); People and sign-in, Export to git, and Moving from lodge 0.2 in `storage`; the Interface in `reading`; the Build order and Open in `rollout`; a new area's draft and rank in the same add as its first entry.
- Its reasoning carries the section's reasons, names her decision for each claim one settles, and says which claims are the design's **[my call]**.
- It narrows the coordinator decisions whose statements it makes false, never an author decision, and answers any other "looks related" feedback no.
- After each section's add, `uv run lodge spec | grep 'changed since'`: each entry that still holds is listed in the next decision of the same part with `edit`, its text unchanged, and one reasoning line saying why it holds; an entry that no longer holds is edited.
- Each part's report section: each new entry with its decision and the design lines it holds; each edited entry with the sentence that changed; each narrowed decision with why.

**Task 11a: what the built server makes false, and what step 1 built.**
- The decision for Constraints (design lines 52 to 62) edits s-a4jfp1 (lodge 0.2 is written in Python; the server, the runner, the interface, and the command in TypeScript, d-b1yjpp), s-v1sb0j (adds Bun 1.3.14 and `ts/package.json` with `ts/bun.lock`, the TypeScript environment beside uv's), s-165qfh (adds the TypeScript structure test over the import graph with dependency-cruiser and TypeScript's parser), and s-3xka4c (adds Biome, `tsc` strict, and knip, warnings failing the gate, d-f18pz7), and narrows d-zq5sfb and d-jxwj8m.
- The decision for The model (design lines 64 to 94) edits s-07ar34 (lodge 0.2 has no server; the server of the design exists from build step 1, d-8kasej), s-z1zvb4 (lodge 0.2's records are Markdown files in git; on the server they are events in one SQLite table, each holding the file's path and bytes, d-d3js00, d-smx3xf), and s-j8tp0n (for a project on lodge 0.2 the files in git are the source of truth; for a project on the server its events are, and the export is a one-way copy), and narrows d-cg3nn3 and d-a3e8kb.
- The decisions for Export to git (lines 280 to 285) and Moving from lodge 0.2 (lines 287 to 290) create their entries from what Tasks 2 to 10 built: the branch holding only `lodge/` in lodge 0.2's file layout, which lodge 0.2 need not read cleanly (d-b61590, the author's); the one commit a minute within one run of the server, `start` exporting at once after a restart; the person mapping; the import into an empty project by its owner, checked as a change from an empty state (d-sdpcyb); and the hook's moved advice.

**Task 11b: Intent, Goals, Non-goals, Must nots, Workflow as data, and Tasks** (design lines 8 to 50 and 96 to 176).
- The four must-nots added for the server (lines 47 to 50) go into `purpose` beside the first design's three, each its own entry.

**Task 11c: Sessions, Artefacts, the waiting list, Claimed and checked, Usage, Code and git, People and sign-in, Interface, Build order, Open, and Left to the builder** (design lines 178 to 317); then the document is frozen.
- Left to the builder (lines 311 to 317) becomes one entry in `rollout` naming what the design leaves open, each item with the decision that settled it where one has (d-sry12f, d-yayhct, d-4k9wcr, and the workflow's syntax still open).
- The report closes with every design line from 8 to 317 mapped to an entry or named as left out, with the reason.
- Then the design document gets its last line first, "Its content now lives in lodge (`lodge spec`, `lodge show`); this document is frozen."; only then does `.lodge.toml`'s `frozen` gain `"docs/superpowers/specs/2026-11-02-lodge-server-design.md"`, so the hook does not fire on that edit; and `CLAUDE.md`'s two lines naming the frozen design documents name the three: line 8 ("Both design documents (…) are frozen history.") and line 33, the hook rule's "(both design documents and the done ledger of the first build)" (preflight M14).

- [ ] **Step 1 (each part):** drafts of the new and edited entries, new areas, and the decisions; dry-run; add; the "changed since" pass.
- [ ] **Step 2: Verify (each part)** `uv run lodge check` prints `ok`; `uv run lodge spec | grep -c 'changed since'` prints 0, or the report names each remaining mark and why; in 11a, `uv run lodge show s-a4jfp1` names TypeScript and `uv run lodge show s-07ar34` no longer says there is no server; in 11c, `printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"},"cwd":"%s"}' "$PWD/docs/superpowers/specs/2026-11-02-lodge-server-design.md" "$PWD" | uv run --frozen --quiet lodge hook post-tool-use` prints the frozen-file advice.
- [ ] **Step 3: Coordinator (each part):** `git add lodge/` and the part's other files, `sh scripts/check.sh`, commit, push.
