# lodge server, build step 1, plan 4: the importer, the export, and the design's records

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** a lodge 0.2 store moves onto the server and back out to git with nothing changed but the people in its `decided_by` lines and its thread messages' `by` lines, the hook tells an agent that a moved project's records live on the server, and lodge's specification holds the server design, whose document is then frozen.

**Architecture:** the `git` package reads a 0.2 store's files at a revision and writes the export's commits through a temporary index; it is the only package that runs git (d-k5swcq, d-x6f9za).
`app` prepares and runs an import (it checks the store as lodge 0.2 checks it, maps the author to the project's one owner, checks the mapped state as the server checks it, and publishes it through the project's store) and batches the export on plan 2's clock; `store` keeps each project's export target as an event; `api` serves `import` and `export-target` to the signed-in person only; `hook` ports lodge 0.2's hook with advice for a moved project; `cli` gains `lodge hook` and builds the hook's context; `main` joins `git` to the rest (d-bs5mm8, d-j5s0h0).
Records cross every boundary as path and file text, as lodge 0.2 writes them (d-smx3xf).

**Tech stack:** plans 1 to 3's, with no new dependency (Task 1): git through the `git` program, as lodge 0.2 runs it (`src/lodge/gitstore/git.py`); TOML through plan 3's smol-toml reading in `cli`; stored bytes through plan 2's `decodeUtf8` and `encodeUtf8` (d-0q54zn, d-ryss91).

**Spec:** `lodge spec` and lodge 0.2's tests for the behaviour carried over; `docs/superpowers/specs/2026-11-02-lodge-server-design.md` (the design, approved by the author 2026-11-02 13:52) for what changes.
The plan argues from them, never over them; where they disagree with this plan, they win and the builder reports it.
"Design line N" is a line of the design; "probe N" is an item of `docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md`, whose sources are in `probes/` beside it; "plan 1", "plan 2", and "plan 3" are `docs/superpowers/plans/2026-11-02-lodge-server-core.md`, `…-server-store.md`, and `…-server-api.md`.

**Aligned against:** plan 2 at `origin/server-store` 7204ad3 and plan 3 at `origin/server-api` f2dcc72, both still being planned; the names this plan takes from them are listed below, and the coordinator checks each against the merged code before the task that consumes it.

## Global Constraints

- Builders are Codex (`codex exec`), one task per brief; a brief holds these constraints and its task, and Codex sees only its brief, `CLAUDE.md`, and the repository.
- In Codex's sandbox git's index is read-only, sockets are refused, and there is no network (plan 1, Global Constraints): the builder never stages, commits, or pushes, and never runs `bun install` or `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name.
  Git in a temporary folder works there: lodge 0.2's 1,056 tests, its git store's among them, passed in the sandbox (`docs/superpowers/plans/2026-10-30-lodge-on-itself/task-5-report.md:102`).
- The builder's gate: `sh scripts/check-ts.sh`; the coordinator's gate after every task: `sh scripts/check.sh` green outside the sandbox, then it stages with explicit paths, commits with `git -c user.name="Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, the message ending `Co-Authored-By: Claude <noreply@anthropic.com>`, and pushes `server-import` (or the task's lane branch) to `origin`; never `main`.
- lodge 0.2 keeps working: `src/`, `tests/`, `pyproject.toml`, and `uv.lock` are not edited.
- Test-first: each carried or new test is written and seen failing before its code (a missing module or export counts as failing); a carried test over code that already exists is seen failing against a mutation of that code, which the builder names in its report and then reverts (d-mfayy5); every existing test keeps passing, edited only where a task says so.
- Porting follows plan 1's Global Constraints, "Porting", "Types", "Exceptions", "Names", "Text", and "Times", which the brief repeats: carried tests keep their Python names without `test_`, an assertion asserts no less than its Python original, a parametrised test keeps every case, `X | None` is `X | null`, a `raise ValueError` is the `ValueError` of `#core`, a Python string operation whose JavaScript namesake differs goes through `text.ts`, and times cross into `core` and `app` as stamps.
- Errors: every refusal the command or the API reports is a `LodgeError` of `#app` or one of its subclasses (`NotFound`, `Conflict`, `Forbidden`), as in lodge 0.2 (`src/lodge/app/errors.py`, `src/lodge/gitstore/errors.py`), with its message given in the task; plan 3's handler maps them to kinds by class.
- Structure (plan 1, Task 3; d-k5swcq, d-x6f9za, d-mfskz3, d-s5s2c3): `cli`, `hook`, and `api` import only `app` and `core`, `store` and `git` only `app` and `core`, and only `main` imports every package (`ts/tests/structure/table.ts`); only `git` spawns processes and writes files, `git` and `cli` read them, and `hook` reads none; `core` and `app` take the time and the waiting through plan 2's `Clock`; no file over 300 lines.
- Exports (d-tha8st): every export a task adds has a reader in that task, its own tests counting, so knip passes after each task, with plan 3's `includeEntryExports` on (d-s2rdn2).
- Git in tests: only in folders made with `mkdtempSync` under the system's temporary folder, through `isolateGit()` of `ts/tests/git/isolated.ts` (Task 2), which gives every test an empty `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_TERMINAL_PROMPT=0`, and a fixed identity; every repository is made with `git init -b main` (or `--bare -b main`); a remote is a bare repository named by its path, so no test needs a socket or the network (`CLAUDE.md`, "Hard rules").
- Fixtures are the made-up project of lodge 0.2's tests (the `storage` area, transcripts, logs) and made-up people (`ana`, `bo`), never her words or another project's records; the made-up 0.2 store of `probes/zero-two-store/` is lodge 0.2's own output for that project (probe 6).
- User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; code comments state the fact.
- Records (Tasks 11a to 11c): written only through `lodge add`, drafts under `.drafts/`, a dry run before every add; in the sandbox, once per task, `mkdir -p .drafts/objects && cp "$(git rev-parse --absolute-git-dir)/index" .drafts/index`, then every `lodge add` runs as `GIT_INDEX_FILE="$PWD/.drafts/index" GIT_OBJECT_DIRECTORY="$PWD/.drafts/objects" GIT_ALTERNATE_OBJECT_DIRECTORIES="$(git rev-parse --path-format=absolute --git-common-dir)/objects" uv run --frozen --quiet lodge add FILE...` (`docs/superpowers/plans/done/2026-10-31-lodge-viewer.md:25`); when that fails, the coordinator runs the adds from the builder's drafts.

## Calls made

Each is the planner's ruling, recorded in lodge with scope `process` and this plan as its work item; its reasoning there holds a handle per argument and the cost if wrong.
Every task repeats what it needs of them, so no brief needs this section.

1. d-1skjw1: the `import` operation names a repository on the server's machine and a revision, the server reads it through `git`, and only the signed-in person may call it; step 1 gives it no command and no form (Tasks 2 and 8).
2. d-ag8p8h: the importer runs lodge 0.2's state check on the store as read, with the store's own `.lodge.toml`, before it maps, and imports into an empty project only (Task 5).
3. d-83kt6y: the importer maps each `decided_by: author` and each thread message's `by: author` to the owner, through the record and thread writers, and refuses a file its writer would not give back byte for byte (Task 5).
4. d-ryss91: every file read from git, attachments included, is decoded with plan 2's `decodeUtf8`, and no file is refused for its bytes (Tasks 2 and 5).
5. d-y42b7b: the import publishes the mapped files with one `publish` of the project's `Store`, after lodge 0.2's check and the server's check of the mapped state, by the project's one owner, writing no settings; plan 2 records the same from its side (d-pprhpz) (Tasks 5 and 8).
6. d-pv341r: the export writes only a branch holding nothing outside `lodge/` that no work tree has checked out, through a temporary index, without force, with no commit when nothing changed (Task 3).
7. d-sj6hmf: `app`'s exporter batches the writes into at most one commit a minute by sleeping on plan 2's clock, retries a minute after a failure, flushes on start, and writes every file of the project with the two `.gitkeep` files (Task 6).
8. d-j5s0h0: a project's export target is an `export-target` event read back by an `ExportTargets` port; the composition root wraps each project's store so that every published write tells the exporter; and it joins `git`'s reading of a 0.2 store with `cli`'s reading of its `.lodge.toml` (Tasks 6, 7, and 8).
9. d-va3j7x: a project has moved when its `.lodge.toml` names its server; then every file under `lodge/` but the attachments gets the moved advice, whatever the store's mode (Tasks 4 and 9).
10. d-bs5mm8: `parseHookSettings` lives in `app`; `cli` builds the hook's context with `git`'s functions given as parameters; the grammar runs `lodge hook EVENT` through a function of `Io` that `main` builds; the carried hook tests run in a real repository without `[server]` (Tasks 4 and 9).
11. d-yng7m8: the server design goes into lodge whole, a decision per section, in three tasks, an unbuilt claim naming its build step; new areas `work` and `sessions` (Tasks 11a to 11c).

One question is the author's, since two lines of her approved design pull apart (IMP-1 in `docs/superpowers/plans/2026-11-02-lodge-server-import/questions.md`): writing the person in `decided_by` (design line 78) makes lodge 0.2's check fail on the export and its threads unreadable, where the export is to read like a 0.2 store (design line 284; probes 3 and 7).
The plan follows design line 78 until she answers; her answer changes one function of Task 6 and the expectations of Task 10.

## Names this plan consumes from plans 2 and 3

Each name as the plan named in "Aligned against" gives it; when the merged code differs, the coordinator writes the merged name into the brief and the ledger, and a difference in meaning stops the task with BLOCKED.

| Name | From | Used by |
|---|---|---|
| `Clock` (`now()` giving `Now { epochMs, offsetMinutes }`, `sleep(seconds)`) | plan 2, Task 2, `#app` | 6, 8 |
| `Store` (`trees()` as `[current, published]`, `attachmentTexts()`, `publish(base, writes, message, approves?)`, `hold`, `held`, `decline`, `commit`, `freshness`, `gate`), `PublishOutcome` | plan 2, Tasks 2 and 12, `#app` | 5, 6 |
| `Actor`, `person(name)`, `agent(role)`, `Role`, `Projects` (`members(project)` in code-point order, `storeFor(project, actor)`, `create`, `addMember`) | plan 2, Task 2, `#app` | 5, 6, 8 |
| `LodgeError`, `NotFound`, `Conflict`, `Forbidden`, `coreSettings(table)` | plan 2, Tasks 2 and 11, `#app` | 2 to 9 |
| `decodeUtf8`, `encodeUtf8` | plan 2, Task 7a, `#core` (`text.ts`) | 2, 3 |
| `Tree.people`, `tree()` defaulting `people` to `{author}`, `parseThread(path, text, people)`, `writeThread(thread, people)` | plan 2, Task 10, `#core` | 5 |
| `LodgeDatabase`, `openDatabase`, `SqliteProjects`, `applyEvent`'s cases in `ts/src/store/events.ts` | plan 2, Tasks 7a and 7b, `#store` | 7, 8 |
| `FixedClock` (`slept`), `MemoryStore` (`people` option), `CountingIds` | plan 2, Tasks 2 and 11, `ts/tests/app/fakes.ts` | 5, 6 |
| `ApiOptions`, `handler`, the person's operations of `ts/src/api/person.ts` and their `forbidden` sentence, the session cookie with the server's `Origin`, the 422 answer with the whole result | plan 3, Tasks 5 and 6, `#api` | 8 |
| `Accounts` (`setup()` with `person`, `project(name)` with `settings`, `projects()`), `ProjectEntry` | plan 3, Task 4, `#app` and `#store` | 8 |
| `world.ts` (the API's test world) and the e2e `server.ts` (both build `ApiOptions`) | plan 3, Tasks 5 and 7a, tests | 8 |
| `Io`, `run(argv, io)`, `parse`, `Command`, `readSettings`, `CliError`, the TOML conversion of `ts/src/cli/settings.ts` | plan 3, Tasks 2, 3, and 7a, `#cli` | 8, 9 |
| `ts/src/main.ts` (`serverCommand`'s `open(data)` and the command's `Io`) | plan 3, Task 8 | 8, 9 |
| `grammar.test.ts`'s `help_lists_every_command` and `every_command_has_help`, `ts/tests/e2e/help-lists-every-command.test.ts`, and `parity.json`'s `dropped` | plan 3, Tasks 2 and 7a | 9 |

Two joins neither plan writes down yet, which Task 8 needs: the project's one owner in plan 2's `Projects.members` (plan 3's `project-create` records a `ProjectEntry` in its `Accounts` and does not say that it calls `Projects.create(name, person)`), and the actor that plan 3's `lodgeFor` gives plan 2's `Lodge` and `storeFor` (plan 2, Task 11).
Task 8 takes the owner from `Projects.members`; if the merged plan 3 creates no owner there, Task 8 stops with BLOCKED, and the coordinator settles it with plan 3's ledger.

## Lanes

The tasks run on `server-import` in its worktree; a lane is a task built in its own worktree and merged into `server-import`, as plan 1's lanes are (d-xdqsmf).
What each task imports decides when it can start; "plan 2's Task N" means that task merged into `server-import`:

| Task | Packages it touches | Starts after | Beside |
|---|---|---|---|
| 1 | tests (setup, coordinator) | plan 1 merged | |
| 2 | `git` | Task 1, plan 2's Tasks 2 and 7a | 4, 5, 6, 7 |
| 3 | `git` | Task 2 | 4, 5, 6, 7 |
| 4 | `hook`, `app` | Task 1, plan 2's Task 2 | 2, 3, 5, 6, 7 |
| 5 | `app` | Task 1, plan 2's Task 11 | 2, 3, 4, 6, 7 |
| 6 | `app` | Task 1, plan 2's Task 12 | 2, 3, 4, 5 |
| 7 | `store` | Task 6, plan 2's Task 7b | 2, 3, 4, 5 |
| 8 | `api`, `cli`, `main` | Tasks 2, 3, 5, 6, and 7, and plans 2 and 3 merged | 9 |
| 9 | `cli`, `main` | Tasks 2 and 4, and plan 3 merged | 8 |
| 10 | tests and scripts | Tasks 8 and 9 | |
| 11a, 11b, 11c | records | Task 10; in order | |

So four lanes run at once after Task 1 (2 then 3; 4; 5; 6 then 7), then 8 beside 9.
Tasks 4, 5, and 6 each add to `ts/src/app/index.ts`, and Tasks 8 and 9 each to `ts/src/main.ts` and `ts/src/cli/index.ts`; the merge of a later lane keeps both sides' lines.

## Review Focus

1. Bytes: a record file with an undecodable byte is problem 1 and refuses the import, an attachment that is not UTF-8 comes back byte for byte, and no text reaches git or the events but through `encodeUtf8`.
2. The author mapping: only `decided_by: author` of a decision and `by: author` of a thread message change, through the writers, and a file its writer would not give back byte for byte is refused rather than rewritten.
3. The import refuses a store lodge 0.2's check refuses, with the same problems, a mapped state the server's check refuses, a project that already holds records, and a requester who is not the project's one owner; nothing is written when it refuses.
4. The export: never a branch holding anything outside `lodge/`, never a branch a work tree has checked out, never a force push, no commit when nothing changed, at most one commit a minute however many writes come, and every published write reaching it.
5. Who may: `import` and `export-target` answer an agent's token with `forbidden`, since an import writes decisions in a person's name (design line 75).
6. The hook: every carried test keeps its assertions, a moved project's advice names the server and never `git checkout`, and the hook stays silent on every failure.
7. The round trip: the made-up store comes back byte for byte apart from the `decided_by: author` lines of its decisions and the `by: author` lines of its thread.

## Parity rows this plan settles

| Python file | Status now | After | Task | TypeScript counterpart |
|---|---|---|---|---|
| `tests/gitstore/conftest.py` | planned | ported | 2 | `ts/tests/git/isolated.ts` |
| `tests/gitstore/repos.py` | planned | changed: "design line 72: records live in the server's events, not in files in git; the helpers of lodge 0.2's git store (`initialised`, `publish_one`, `checkout_project`, `Ticker`) have no counterpart, and the repository helpers are carried" | 2 | `ts/tests/git/repos.ts` |
| `tests/hook/test_post_tool_use.py` | changed | changed: "d-va3j7x adds the moved project's advice; d-bs5mm8 moves `parse_hook_settings` to `#app`" | 4 | `ts/tests/hook/post-tool-use.test.ts` |
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

- No dependency is added: git runs as the `git` program, `.lodge.toml` is read by plan 3's smol-toml reading in `cli`, and stored bytes by plan 2's codec; so `ts/package.json` and `ts/bun.lock` stay as plans 1 to 3 leave them, and only the `imports` map gains `#git` and `#hook` where Tasks 2 and 4 create those packages.
- Merge points, each named in the ledger with its commit: plan 2's Tasks 2, 7a, 7b, 10, 11, and 12 as the lanes table says; all of plans 2 and 3 before Tasks 8 and 9.

- [ ] **Step 1:** Merge `server-core` into `server-import` once plan 1's last task is merged there; `sh scripts/check.sh` green.
- [ ] **Step 2:** Write the test `ts/tests/core/zero-two-store.test.ts` with `zero_two_store_checks_clean`: `checkState` of `load` of `tree({ rev: null, files, attachments })` of the store's files under `lodge/` (the attachment's path in `attachments`, every other file in `files`), with `parseCoreSettings` of `Bun.TOML.parse` of its `.lodge.toml`, finds no problem, as lodge 0.2's `lodge check` printed `ok` (probe 6); run `cd ts && bun test tests/core/zero-two-store.test.ts`; expected: FAIL (no module).
- [ ] **Step 3:** `python3 docs/superpowers/plans/2026-11-02-lodge-server-import/probes/fixture.py docs/superpowers/plans/2026-11-02-lodge-server-import/probes/zero-two-store > ts/tests/core/zero-two-store.ts`, then Biome's formatter on it; run the test again; expected: PASS.
  The generator writes each text as a JSON string literal, and the 11 texts read back equal to the files (`files 11; equal 11`, run on 2026-11-02 against the store of probe 6).
- [ ] **Step 4:** `git diff server-core -- ts/package.json ts/bun.lock` shows only plan 2's and plan 3's changes; the ledger line says no dependency is added and why; `sh scripts/check.sh`, commit, push.

### Task 2: Running git and reading a lodge 0.2 store

**Files:**
- Create: `ts/src/git/index.ts`, `ts/src/git/run.ts`, `ts/src/git/read-store.ts`, `ts/src/git/paths.ts`, `ts/tests/git/isolated.ts`, `ts/tests/git/repos.ts`, `ts/tests/git/zero-two.ts`
- Modify: `ts/package.json` (`"#git": "./src/git/index.ts"` in `imports`), `ts/tests/parity.json` (two rows)
- Test: `ts/tests/git/run.test.ts`, `ts/tests/git/read-store.test.ts`, `ts/tests/git/paths.test.ts` (new)

**Interfaces:**
- Consumes: plan 2's `decodeUtf8` and `encodeUtf8` of `#core` (Task 7a); `#app`'s `LodgeError`; Task 1's `ZERO_TWO_STORE`.
- Produces, through `#git`:
  ```ts
  // run.ts, a port of src/lodge/gitstore/git.py without request_exit
  export class GitMissing extends LodgeError {}                       // "git is not installed or is not on the PATH"
  export interface GitDone { readonly code: number; readonly stdout: Uint8Array; readonly stderr: Uint8Array }
  export function attempt(args: readonly string[], cwd: string, env?: Readonly<Record<string, string>>, input?: Uint8Array | string): Promise<GitDone>
  export function runBytes(args: readonly string[], cwd: string, env?: Readonly<Record<string, string>>, input?: Uint8Array | string): Promise<Uint8Array>
  export function run(args: readonly string[], cwd: string, env?: Readonly<Record<string, string>>, input?: Uint8Array | string): Promise<string>
  export function resolveRev(cwd: string, ref: string): Promise<string | null>
  // read-store.ts
  export interface StoreRead {
    readonly rev: string                                // the commit read
    readonly files: ReadonlyMap<string, string>         // every file under lodge/, attachments and .gitkeep included, by path
    readonly settings: string | null                    // .lodge.toml at that commit, as text
  }
  export function readStore(repository: string, rev: string): Promise<StoreRead>
  // paths.ts
  export function resolvePath(path: string): string     // Python's Path(path).resolve(): links followed where they exist
  export function repoRootOf(edited: string): Promise<string>
  export function isFolder(path: string): boolean
  ```
- `attempt` spawns `git -C <cwd> <args>` with `Bun.spawn`, `LC_ALL=C` and `GIT_TERMINAL_PROMPT=0` over the process's environment and `env`, standard input closed when there is no `input` and a string `input` encoded with `encodeUtf8`; a missing `git` program is a `GitMissing`; `runBytes` throws a `LodgeError` with git's first non-empty line of standard error, else of standard output, else `git <args[0]> failed`, as `run_bytes` does; `run` decodes with `decodeUtf8` and drops the final newlines; `resolveRev` is `resolve` of `git.py`, `rev-parse --verify --quiet --end-of-options <ref>^{commit}`, null on exit 1.
- `readStore` resolves `rev` with `resolveRev` and refuses one that names no commit with `LodgeError("<rev> is not a commit in <repository>")`; lists `ls-tree -r -z --full-tree <commit> -- lodge` and refuses an empty listing with `LodgeError("<rev> holds no lodge/ folder, so it is not a lodge 0.2 store")`; reads every blob in one `cat-file --batch`, as `_contents` of `src/lodge/gitstore/trees.py` does, and gives each its text through `decodeUtf8`, an entry that is not a blob the empty text, as `read_tree` does; and reads `.lodge.toml` at the commit in the same batch, null when there is none.
  Unlike `read_tree`, it gives the attachments' texts too, since the import carries them, and refuses no file for its bytes: an attachment that is not UTF-8 holds U+DC80 to U+DCFF and goes back to the same bytes through `encodeUtf8` (d-ryss91).
- `resolvePath` follows Python's non-strict `resolve`: an absolute path is normalised segment by segment, each existing prefix with `realpathSync` and the rest appended, `..` taken after the links before it are followed; it lives in `git` because `hook` may not read the file system (d-x6f9za).
- `repoRootOf(edited)` is `rev-parse --show-toplevel` in the nearest existing folder at or above `resolvePath(edited)`'s parent (`_existing_folder` and `_hook_context` of `src/lodge/main.py:65-78`), and a folder outside any repository is a `LodgeError("<folder> is not inside a git repository")`, as `repo_root` says it.
- `isolated.ts` exports `isolateGit()`, which registers `beforeEach` and `afterEach` hooks setting and restoring the variables of `tests/gitstore/conftest.py`'s `isolated_git`, the identity `Test Author <test@example.com>` included, and deleting `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, and `GIT_COMMON_DIR` for the test.
- `repos.ts` carries `git`, `bareRemote`, `clone`, `seeded`, `worktree`, `commit`, and `write` of `tests/gitstore/repos.py`, each over a folder from `mkdtempSync`; the rest of that file builds lodge 0.2's git store and has no counterpart.
- `zero-two.ts` exports `zeroTwoRepository(layout: "checkout" | "branch"): Promise<{ repository: string; rev: string }>`, which commits Task 1's `ZERO_TWO_STORE` into a new repository, on `main` for `checkout` and on an orphan branch `lodge` holding only `lodge/` for `branch`, with `.lodge.toml` on `main` in both and `rev` the commit holding `lodge/`.

- [ ] **Step 1: Write the failing tests.**
  - `run.test.ts`: `missing_git_is_one_sentence` (with `PATH` emptied for the call, `attempt` throws a `GitMissing` with its message); `failure_names_gits_first_line` (`runBytes(["rev-parse", "--verify", "nope"])` throws a `LodgeError` whose message is git's first line); `resolve_rev_gives_null_for_a_missing_ref`; `resolve_rev_refuses_an_option` (`resolveRev(repo, "--output=x")` gives null and writes no file named `x`, since `--end-of-options` comes first); `input_reaches_git` (`hash-object --stdin` of `"a\n"` gives `78981922613b2afb6025042ff6bd878ac1994e85`).
  - `read-store.test.ts`: `reads_the_checkout_layout` and `reads_the_branch_layout` (`readStore` of `zeroTwoRepository(...)` gives the ten files of `ZERO_TWO_STORE` under `lodge/` with their texts, `.lodge.toml`'s text in `settings`, and the commit in `rev`); `revision_that_is_no_commit_is_refused`; `revision_without_lodge_is_refused` (the `main` of the branch layout); `undecodable_record_reads_as_escapes` (a decision with a `\xff` byte reads with U+DCFF); `undecodable_attachment_keeps_its_bytes` (an attachment holding `\xff\xfe` reads as U+DCFF U+DCFE, which `encodeUtf8` gives back as the two bytes); `symbolic_link_reads_as_its_target` (a link committed under `lodge/` reads as its target's text, as `read_tree` reads a blob of mode 120000); `settings_absent_is_null`.
  - `paths.test.ts`: `resolve_follows_links` (`tests/hook/test_post_tool_use.py`'s `test_symlinked_checkout_still_matches` layout); `resolve_takes_dot_dot_through_missing_folders` (`<tmp>/docs/../lodge/decisions/d.md` with no `docs` resolves to `<tmp>/lodge/decisions/d.md`); `repo_root_of_a_file_that_does_not_exist_yet` (as `test_hook_finds_the_repository_for_a_file_that_does_not_exist_yet`); `repo_root_outside_a_repository_is_one_sentence`; `is_folder_says_whether_a_folder_exists`.
- [ ] **Step 2: Run** `cd ts && bun test tests/git`; expected: the new tests FAIL.
- [ ] **Step 3: Implement**; add `#git` to `ts/package.json`'s `imports`; flip `tests/gitstore/conftest.py` to `ported` and `tests/gitstore/repos.py` to `changed` with the `why` of "Parity rows this plan settles".
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 3: The export writer

**Files:**
- Create: `ts/src/git/export.ts`
- Modify: `ts/src/git/index.ts`
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
  1. Refuses a path of `files` outside `lodge/` as `check_writes` of `src/lodge/gitstore/plumbing.py:14-26` refuses it, with its message, and a branch name that is not a name of letters, digits, and `. _ / -` not starting with a symbol, as `_name` of `src/lodge/gitstore/settings.py:76-83` says it.
  2. Finds the tip: with a remote, `ls-remote <remote> refs/heads/<branch>` (`remote_tip`), and when there is one, `fetch --quiet --no-tags <remote> refs/heads/<branch>` so that its commit is local; without one, `resolveRev(repository, "refs/heads/<branch>")`, and a branch that a work tree of the repository has checked out (`worktree list --porcelain` names `branch refs/heads/<branch>`) is refused with `LodgeError("<branch> is checked out in a work tree of <repository>; the export writes only a branch no work tree has checked out")`.
  3. Refuses a tip whose tree holds a path outside `lodge/` (`ls-tree -r --name-only <tip>`), with `LodgeError("<branch> holds files outside lodge/, so it is not a branch lodge exports to; name a branch of its own")`, so the export never writes a project's main branch (design must-not 7).
  4. Builds the tree in a temporary index in a folder from `mkdtempSync`: each text through `encodeUtf8` into a file there, one `hash-object -w --no-filters --stdin-paths`, one `update-index -z --index-info`, then `write-tree` (probe 4); the folder is removed in a `finally`.
  5. Answers `unchanged` when the tree equals the tip's tree, making no commit.
  6. Commits with `commit-tree <tree> [-p <tip>] -F -`, the author and committer `lodge <lodge@export.invalid>` through `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, `GIT_COMMITTER_NAME`, and `GIT_COMMITTER_EMAIL`, the message ending in one newline.
  7. Moves the branch without force: with a remote, `push --porcelain <remote> <commit>:refs/heads/<branch>`, `moved` when it is refused and `ls-remote` shows another tip, git's first line as a `LodgeError` otherwise (`push` of `plumbing.py:57-79`); without one, `update-ref refs/heads/<branch> <commit> <tip or forty zeros>`, `moved` when the ref moved under it (probe 4).
- No work tree is read or written, so a bare repository is a target.

- [ ] **Step 1: Write the failing tests** in `export.test.ts`, each with `isolateGit()`: `first_export_makes_the_branch` (a bare repository; the branch's tree holds exactly the files, each byte for byte, and the author is `lodge <lodge@export.invalid>`); `same_files_make_no_commit` (`unchanged`, tip unmoved); `changed_file_makes_one_commit_on_the_last` (parent is the previous commit); `removed_file_leaves_the_tree`; `escaped_bytes_are_written_as_bytes` (a text holding U+DCFF is the byte `\xff` in the blob); `path_outside_lodge_is_refused` (`README.md`, `lodge/../x`, `lodge/.git/x`, each with its message); `branch_with_other_files_is_refused` (`main` of `seeded`); `checked_out_branch_is_refused`; `lodge_zero_two_branch_is_a_target` (the branch layout of `zeroTwoRepository`); `push_without_force` (a work repository with a bare remote: the remote's branch has the commit, the work repository's own branches are unmoved); `moved_remote_branch_answers_moved` (a commit pushed to the remote by a second clone after the export's fetch and before its push: the export answers `moved`, and a second export builds on the new tip); `exported_store_reads_back` (`readStore` of the exported branch gives the files exported).
- [ ] **Step 2: Run** `cd ts && bun test tests/git/export.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 4: The hook's advice

**Files:**
- Create: `ts/src/hook/index.ts`, `ts/src/hook/post-tool-use.ts`, `ts/src/hook/texts.ts`, `ts/src/app/hook-settings.ts`
- Modify: `ts/package.json` (`"#hook": "./src/hook/index.ts"` in `imports`), `ts/src/app/index.ts`, `ts/tests/parity.json` (the row's `why`)
- Test: `ts/tests/hook/post-tool-use.test.ts` (carried, with new tests)

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
  export interface HookOutput { readonly hookSpecificOutput: { readonly hookEventName: "PostToolUse"; readonly additionalContext: string } }
  export function respond(payload: unknown, context: HookContext, resolve: Resolve, cwd?: string | null): HookOutput | null
  export function run(read: () => Promise<string>, write: (text: string) => void, context: (edited: string) => Promise<HookContext | null>, resolve: Resolve, cwd: string | null): Promise<0>
  ```
- `respond` and `run` keep the Python logic, with `context` and `resolve` given by the caller (Python's `respond` takes the three parts of the context as arguments; the TypeScript one takes them as one object, so a test's `respond(payload(record), tmp_path, data, ())` becomes `respond(payload(record), { repoRoot, dataRoot: data, frozen: [], server: null }, resolve)`).
  `run` reads the event with `read`, writes one JSON line with `write`, and gives 0 whatever fails, as Python's `run` does.
- `texts.ts` holds `RECORD_TEXT`, `THREAD_TEXT`, and `FROZEN_TEXT` as Python's, character for character, and three texts for a moved project, used when `context.server` is not null, `{server}` the address:
  - `MOVED_RECORD_TEXT`: `{path} is a lodge record file from before this project moved to the lodge server at {server}: its records live on the server now, and an edit here changes nothing there. Run \`lodge draft REF\` (or \`lodge draft area:NAME\`) to get the record as a draft, edit the draft, check it with \`lodge add --dry-run FILE\`, then publish it with \`lodge add FILE\`; the command sends both to the server. ` and then `REVERSE`;
  - `MOVED_THREAD_TEXT`: `{path} is a lodge thread file from before this project moved to the lodge server at {server}: its threads live on the server now, and an edit here changes nothing there. Add a message with \`lodge reply Q --by ROLE FILE\`, or close it with \`lodge close Q --by ROLE\`; the command sends both to the server. ` and then `REVERSE`;
  - `MOVED_FROZEN_TEXT`: `{path} is frozen: lodge holds its content now, on the lodge server at {server}, so do not edit it. Record the change as a new decision instead: write a draft (\`lodge guide\` shows the draft format), check it with \`lodge add --dry-run FILE\`, then publish it with \`lodge add FILE\`, which sends it to the server. ` and then `ASKED`, ` Otherwise reverse your own edit now: `, and `RESTORE`.
- For a moved project every file under `<repoRoot>/lodge/` but `lodge/attachments/` gets the moved record or thread text, whatever `dataRoot` says, since the files there are copies from before the move in either store mode (d-va3j7x); a frozen file gets the moved frozen text.
- Python's `_glob` becomes a pattern built with `new RegExp` and the `u` flag, its escape of each literal character the escape of every character that has a meaning in a JavaScript pattern, and `re.fullmatch` the test of `^(?:p)$`.
- The tests take `resolve` as a test-local function over `realpathSync` and `path.resolve`, since `hook` may not import `git`; Task 9's carried end-to-end tests run the hook with `#git`'s `resolvePath`.

- [ ] **Step 1: Write the failing tests:** every test of `tests/hook/test_post_tool_use.py` by name, each parametrised case kept, `tmp_path` a folder from `mkdtempSync`, the settings tests calling `parseHookSettings` of `#app`; then the new tests:
  `moved_record_edit_names_the_server` (the record text names the server and `lodge draft`, `lodge add --dry-run`, and `lodge add FILE` in that order, and not `lodge/decisions` as a place to edit); `moved_thread_edit_names_reply_and_close`; `moved_frozen_edit_names_the_server`; `moved_project_protects_lodge_in_branch_mode` (`dataRoot` null and `server` set: a file under `lodge/decisions/` gets the moved text); `moved_attachment_edit_gets_nothing`; `moved_advice_reverses_the_edit_without_git` (as `test_record_advice_reverses_the_edit_without_git`, for the three moved texts).
- [ ] **Step 2: Run** `cd ts && bun test tests/hook`; expected: FAIL.
- [ ] **Step 3: Implement**; add `#hook` to `ts/package.json`'s `imports`; set the row's `why` in `parity.json`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 5: Preparing and making an import

**Files:**
- Create: `ts/src/app/importing.ts`
- Modify: `ts/src/app/index.ts`
- Test: `ts/tests/app/importing.test.ts`, `ts/tests/app/import-store.test.ts` (new)

**Interfaces:**
- Consumes: `#core`'s `tree`, `load`, `checkState`, `parseRecord`, `writeRecord`, `parseThread`, `writeThread`, `CoreSettings`, `Problem`, `ATTACHMENTS` (with plan 2's `people`, Task 10); `#app`'s `Store`, `Projects`, `Role`, `person`, `PublishOutcome`, `coreSettings`, `LodgeError`, `Conflict`, `Forbidden` (plan 2, Tasks 2 and 11); plan 2's `MemoryStore` and `FixedClock` in the tests.
- Produces, through `#app`:
  ```ts
  export interface ZeroTwoCopy {
    readonly rev: string
    readonly files: ReadonlyMap<string, string>                  // every file under lodge/, as git's readStore gives them
    readonly settings: Readonly<Record<string, unknown>>         // the [length] and [import] tables of the store's .lodge.toml
  }
  export interface PreparedImport {
    readonly problems: readonly Problem[]                        // nothing is imported unless empty
    readonly stage: "lodge 0.2" | "server" | null                // which check found them
    readonly files: ReadonlyMap<string, string>                  // every record, area, thread, and attachment to write, mapped
    readonly mapped: readonly string[]                           // the decisions and threads whose author became the owner, by ID
  }
  export type Imported =
    | { readonly kind: "imported"; readonly rev: string; readonly decisions: number; readonly entries: number; readonly areas: number; readonly threads: number; readonly attachments: number; readonly mapped: readonly string[] }
    | { readonly kind: "check-failed"; readonly stage: "lodge 0.2" | "server"; readonly problems: readonly Problem[] }
  export function prepareImport(copy: ZeroTwoCopy, owner: string, people: ReadonlySet<string>, settings: CoreSettings): PreparedImport
  export function importStore(copy: ZeroTwoCopy, project: string, requester: string, projects: Projects, settings: CoreSettings): Promise<Imported>
  ```
- `prepareImport` (d-ag8p8h, d-83kt6y, d-ryss91), `settings` being the project's on the server:
  1. Checks the store as lodge 0.2 checks its published state: `checkState(load(tree({ rev: null, files, attachments })), coreSettings(copy.settings))`, the attachments' paths in `attachments` and every other file in `files`, `people` left to `tree()`'s default `{author}`, so a record imported from a source the store's `.lodge.toml` does not list fails as it does in 0.2 (`tests/e2e/test_add_import.py`); any problem ends here, with `stage` `"lodge 0.2"` and `files` empty.
  2. Maps each decision whose `decidedBy` is `author` to `owner`: its new text is `writeRecord` of the decision with `decidedBy: owner`; each thread holding a message `by: author` likewise, `writeThread` of the thread with those messages `by: owner`, written with `people`.
     A file whose writer does not give its unchanged text back byte for byte (`writeRecord` of the parsed decision, or `writeThread` of the parsed thread with `{author}`) is refused as a problem of check 1 at its path with the message `lodge 0.2 did not write this file as lodge writes it, so the importer cannot change who wrote it alone`, `stage` `"lodge 0.2"`.
  3. Gives every other file unchanged, but the paths ending `/.gitkeep`, which `load` skips (`src/lodge/core/snapshot.py:68`) and the export writes back (Task 6).
  4. Checks the mapped state as the server checks a write: `checkState(load(tree({ rev: null, files, attachments, people })), settings)`; any problem ends here, with `stage` `"server"` and `files` empty.
  Nothing else changes: IDs, dates, codes, `imported_from`, quotes, and every other line keep their bytes, as design line 289 asks.
- `importStore` (d-y42b7b), in this order, writing nothing on any refusal:
  - the project's owners are the members of `projects.members(project)` with `Role.OWNER`; none or more than one is `LodgeError("project <name> has <n> owners; lodge imports into a project with one owner")`;
  - a `requester` who is not that owner is `Forbidden("only <owner>, the owner of project <name>, may import into it")`;
  - `store = projects.storeFor(project, person(owner))`; `[current] = await store.trees()`; a current state holding any file or attachment is `Conflict("project <name> already holds records; lodge imports a store into an empty project only")`;
  - `prepareImport(copy, owner, current.people, settings)`; problems give `{ kind: "check-failed", stage, problems }`;
  - `store.publish(current, files, "Import the lodge 0.2 store at <rev>")`; `REJECTED` is `Conflict("project <name> changed during the import; nothing was imported")`;
  - otherwise `{ kind: "imported", … }`, the counts by path (`lodge/decisions/`, `lodge/spec/` but `_area.md`, `_area.md`, `lodge/threads/`, `lodge/attachments/`).

- [ ] **Step 1: Write the failing tests.**
  - `importing.test.ts`, over Task 1's `ZERO_TWO_STORE` as a `ZeroTwoCopy` (`settings` from its `.lodge.toml`) with the owner `ana` and `people` `{ana}`: `clean_store_prepares_every_file` (nine files: four decisions, one entry, one area, one thread, one attachment, and no `.gitkeep`; `problems` empty); `author_decisions_name_the_owner` (the three author decisions, the imported one included, now read `decided_by: ana`, and each mapped text differs from the original in that line only); `agent_decision_is_unchanged`; `author_message_names_the_owner` (the thread's reply reads `by: ana` and differs in that line only; its `when` and `where` keep their bytes); `ids_dates_codes_and_imported_from_are_kept`; `failing_store_prepares_nothing` (the store's `[import]` sources emptied gives lodge 0.2's check problem for the imported decision, `stage` `"lodge 0.2"`, and `files` empty); `stray_file_fails_the_check` (a `lodge/notes.txt`); `file_the_writer_would_not_give_back_is_refused` (an author decision with its keys in another order); `mapped_state_is_checked_with_the_project_settings` (project settings with `[length] title_chars = 10`: `stage` `"server"`); `owner_named_author_changes_nothing` (owner `author` and `people` `{author}`: every file as read).
  - `import-store.test.ts`, over plan 2's `MemoryStore` and a fake `Projects` giving one store per project: `owner_imports_into_an_empty_project` (the answer's counts, and the store's `publishes` holds one publish of the nine files); `requester_must_be_the_owner` (`Forbidden`, nothing published); `project_with_two_owners_is_refused`; `project_with_records_is_a_conflict`; `failed_check_publishes_nothing`; `rejected_publish_is_a_conflict`.
- [ ] **Step 2: Run** `cd ts && bun test tests/app/importing.test.ts tests/app/import-store.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 6: The export's files and its batching

**Files:**
- Create: `ts/src/app/exporting.ts`, `ts/src/app/exporters.ts`
- Modify: `ts/src/app/index.ts`
- Test: `ts/tests/app/exporting.test.ts`, `ts/tests/app/exporters.test.ts` (new)

**Interfaces:**
- Consumes: `#core`'s `Tree`; `#app`'s `Clock`, `Store`, `Projects`, `Actor`, `agent`, `PublishOutcome`; plan 2's `FixedClock` and `MemoryStore` in the tests.
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
  export function exportFiles(current: Tree, attachmentTexts: ReadonlyMap<string, string>): ReadonlyMap<string, string>
  export function exportMessage(files: ReadonlyMap<string, string>): string
  export class Exporters {
    constructor(ports: ExportPorts);
    written(project: string): Promise<void>;                                    // resolves when the run covering this write ends
    start(projects: readonly string[]): Promise<void>;                          // written() for each project with a target
    settled(): Promise<void>;                                                   // every run ended
  }
  export function exportingProjects(projects: Projects, exporters: Exporters): Projects
  ```
- `exportFiles` gives every file of `current.files` but the `/.gitkeep` paths, each attachment's text, and `KEPT` with the empty text, as `lodge init` lays a store out (`src/lodge/gitstore/trees.py:10`, `src/lodge/gitstore/setup.py:47-56`), so the export is a lodge 0.2 store in either layout (d-sj6hmf).
- `exportMessage` is `Export lodge records: <d> decisions, <e> entries, <a> areas, <t> threads`, counted from the paths.
- `Exporters` (design line 285; d-sj6hmf), one run at most per project at a time:
  - `written(project)` notes a pending write; when no run is going for the project, it starts one, and otherwise the running one takes the write.
  - A run loops while a write is pending: it waits `EXPORT_INTERVAL_SECONDS` after the project's last commit by `clock.now()` with `clock.sleep(seconds)` (no wait before the first commit, or when the last is a minute old or more), clears the pending mark, and flushes: with no target from `targets.target(project)`, nothing; otherwise `write(target, exportFiles(current, await store.attachmentTexts()), exportMessage(…))`, `current` the first tree of `storeFor(project).trees()`.
    `committed` notes the commit's time; `unchanged` notes nothing; `moved`, or `write` throwing (given to `failed`), marks a write pending again after `clock.sleep(EXPORT_INTERVAL_SECONDS)`.
  - So two commits of one project are at least a minute apart, writes within that minute share the next commit, and a write is exported within a minute of the last commit.
  - `app` reads the time only from `clock.now()` and waits only through `clock.sleep` (`CLAUDE.md`, "Structure checks").
- `exportingProjects` gives a `Projects` whose `storeFor(project, actor)` is the inner store wrapped so that a `publish` answering `PUBLISHED` calls `void exporters.written(project)` before it returns; every other method of `Projects` and of the store, plan 2's Task 12 methods included, passes to the inner one unchanged (d-j5s0h0).

- [ ] **Step 1: Write the failing tests.**
  - `exporting.test.ts`: `export_files_hold_the_store_and_kept` (a `MemoryStore` holding the made-up store's records: its files, its attachment's text, and both `.gitkeep`, nothing else); `message_counts_the_records`; `wrapped_store_tells_the_exporter_after_a_publish` (a recording `Exporters` stand-in: one call after `PUBLISHED`, none after `REJECTED`); `wrapped_store_passes_every_other_method` (`trees`, `attachmentTexts`, `held`, and the rest reach the inner store).
  - `exporters.test.ts`, with `FixedClock` (whose `sleep` moves its time and records `slept`) and a `write` that records its calls: `first_write_exports_at_once` (nothing slept, one `write`); `writes_within_a_minute_share_one_commit` (a commit, then three writes 10, 20, and 30 seconds later before the run ends: `slept` holds the rest of the minute once, and one more `write`); `write_a_minute_after_exports_at_once`; `no_target_writes_nothing`; `unchanged_counts_no_commit` (after `unchanged`, the next write exports at once); `moved_retries_a_minute_later`; `failure_is_reported_and_retried` (`failed` gets the project and the error, `slept` holds 60, and the second `write` succeeds); `projects_batch_apart` (writes to two projects each export at once); `start_exports_projects_with_a_target`.
- [ ] **Step 2: Run** `cd ts && bun test tests/app/exporting.test.ts tests/app/exporters.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 7: Export targets in the store

**Files:**
- Create: `ts/src/store/export-targets.ts`
- Modify: `ts/src/store/events.ts` (the kind's case in `applyEvent`), `ts/src/store/index.ts`
- Test: `ts/tests/store/export-targets.test.ts` (new)

**Interfaces:**
- Consumes: Task 6's `ExportTargets`, `ExportTarget`; plan 2's `LodgeDatabase`, `openDatabase`, `appendEvents`, `actorText`, `stampOf`, and `Clock` (Tasks 2, 7a, and 7b).
- Produces, through `#store`: `SqliteExportTargets implements ExportTargets` (`constructor(database: LodgeDatabase, clock: Clock)`).
- `setTarget` appends one event of the kind `export-target` for the project, the actor `actorText(by)`, `at` `stampOf(clock.now())`, and the body UTF-8 JSON `{"target": …}`; `target(project)` reads the project's newest such event and gives its target, null when there is none or the newest holds null (d-j5s0h0).
- `applyEvent` gains the case `export-target`, which changes no derived table beyond what it does for every kind, as plan 2's rule for a new kind says ("Interfaces for plans 3 and 4"), so `rebuild` accepts the event.
- A target for a project that does not exist is `NotFound` as plan 2's `Projects` words it.

- [ ] **Step 1: Write the failing tests** in `export-targets.test.ts`, over plan 2's store on `:memory:` with a project `work`: `no_target_is_null`; `target_set_is_read_back`; `newest_target_wins`; `null_stops_the_target`; `target_is_an_event` (kind, actor, `at`, and body); `rebuild_keeps_the_target`; `unknown_project_is_not_found`.
- [ ] **Step 2: Run** `cd ts && bun test tests/store/export-targets.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 8: Import and export in the server

**Files:**
- Create: `ts/src/api/moving.ts`, `ts/src/cli/zero-two.ts`
- Modify: plan 3's `ApiOptions` (where its Task 5 declares it) and its operation table (`ts/src/api/person.ts`), `ts/src/api/index.ts`, `ts/src/cli/index.ts`, `ts/src/main.ts`, `ts/tests/api/world.ts`, `ts/tests/e2e/server.ts`
- Test: `ts/tests/api/import.test.ts`, `ts/tests/api/export-target.test.ts`, `ts/tests/cli/zero-two.test.ts` (new)

**Interfaces:**
- Consumes: Tasks 2, 3, 5, 6, and 7; plan 2's store and `Projects`; plan 3's handler, person's operations, `Accounts`, test world, and `cli`'s TOML conversion.
- Produces, through `#cli`: `zeroTwoCoreTable(text: string): Readonly<Record<string, unknown>>`, which parses `.lodge.toml` text with the conversion `readSettings` uses (RULE-TOML) and gives its `length` and `import` tables only, every other top-level name ignored, since a lodge 0.2 file may hold `[store]` and `[hook]`; a file that is not TOML is `CliError(".lodge.toml: <smol-toml's first line>")`.
- Produces, through `#api`: `ApiOptions` gains `readonly moving: Moving`, with
  ```ts
  export interface Moving {
    readonly read: (repository: string, rev: string) => Promise<ZeroTwoCopy>   // main joins #git's readStore and #cli's zeroTwoCoreTable
    readonly projects: Projects                                                 // exportingProjects over plan 2's projects
    readonly targets: ExportTargets
    readonly exporters: Exporters
  }
  ```
  and `lodgeFor` builds its `Lodge` over `moving.projects.storeFor`, so every publish tells the exporter.
- The operations (`moving.ts`), registered with the person's operations, so an agent's token is `forbidden` with `only the signed-in person may <operation>` (plan 3, Task 6), each body holding `project`:
  - `import` (`repository`, `rev`; d-1skjw1): `accounts.project(project)` null is `no-project`; `moving.read(repository, rev)`; `importStore(copy, project, <the signed-in person>, moving.projects, coreSettings(entry.settings))`; `imported` answers 200 with it, and `check-failed` answers 422 as plan 3 answers a write whose check fails, with the result; the errors map by class (`Forbidden` 403, `Conflict` 409, `LodgeError` 400).
  - `export-target` (`target`, an object of `repository`, `branch`, and `remote` (a string or null), or null): `targets.setTarget(project, target, person(<the signed-in person>))`, then `void exporters.written(project)` when the target is not null, and answers `{"target": …}`.
- `main.ts`, in plan 3's `open(data)`: `SqliteExportTargets` over the opened store; `Exporters` with plan 2's real clock, `storeFor` = `projects.storeFor(project, agent("exporter"))`, `write` = `#git`'s `exportStore`, and `failed` writing `lodge: the export of <project> failed: <message>` on the server's standard error; `moving.projects` = `exportingProjects(projects, exporters)`; `moving.read` = `readStore` then `zeroTwoCoreTable` of its `settings` (`{}` when null), a `CliError` thrown again as a `LodgeError` with its message; and `exporters.start` of every project's name from `accounts.projects()`, not awaited, so `serve` exports what a stopped server left pending.
- `world.ts` and the e2e `server.ts` build `moving` the same way over the in-memory store, with `FixedClock`.

- [ ] **Step 1: Write the failing tests**, each calling the handler with a `Request` and no socket (plan 3's helpers), each repository from `zeroTwoRepository` with `isolateGit()`:
  - `import.test.ts`: `person_imports_the_made_up_store` (both layouts: the answer's counts, and `show` of each author decision through the agent's token names the person); `agent_token_is_forbidden`; `second_import_is_a_conflict`; `failing_store_answers_check_failed` (the store's `[import]` sources emptied: 422 with the problems, and `search` finds nothing); `missing_revision_is_usage`; `unknown_project_is_no_project`; `imported_records_read_as_imported` (`show` of the imported decision says imported and unquoted, as `test_import_needs_the_flag_and_a_listed_source` asserts in lodge 0.2).
  - `export-target.test.ts`: `person_sets_the_target`; `agent_token_is_forbidden`; `write_after_target_exports` (the person sets a bare repository as the target, an agent's `add` follows, and after `exporters.settled()` the branch holds the new decision); `null_target_stops_the_export`.
  - `zero-two.test.ts`: `core_tables_are_kept` (`[length]` and `[import]`); `store_and_hook_are_ignored`; `whole_number_float_is_refused_as_the_command_refuses_it` (`title_chars = 80.0`, then `parseCoreSettings` gives lodge 0.2's sentence); `not_toml_is_one_sentence`.
- [ ] **Step 2: Run** `cd ts && bun test tests/api/import.test.ts tests/api/export-target.test.ts tests/cli/zero-two.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green, `tsc` accepting `exportStore` as the exporters' `write`.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 9: The hook in the command

**Files:**
- Create: `ts/src/cli/hook-context.ts`, `ts/tests/hook/repository.ts` (helper)
- Modify: `ts/src/cli/grammar.ts`, `ts/src/cli/commands.ts` (or where plan 3's `run` dispatches), `ts/src/cli/settings.ts` (`[hook]` checked), `ts/src/cli/index.ts`, `ts/src/main.ts`, every `Io` the tests build, `ts/tests/cli/grammar.test.ts`, `ts/tests/e2e/help-lists-every-command.test.ts`, `ts/tests/parity.json`
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
  and `Io` gains `readonly hook: () => Promise<number>`.
- `hookContextFor` is `_hook_context` (`src/lodge/main.py:73-78`): `repoRootOf(edited)`; `.lodge.toml` at that root parsed with smol-toml, every top-level name allowed; `server` the `[server]` table's `url`, null without one; `[store] mode`, `"checkout"` when absent; `frozen` from `parseHookSettings` of `[hook]`; for a project that has not moved and is in checkout mode, null unless `<root>/lodge/decisions` and `<root>/lodge/spec` are folders (`holds_records`); `dataRoot` `<root>/lodge` in checkout mode and null in branch mode; any error, a malformed file or a `[server]` without a string `url` included, gives null, so the hook stays silent.
- The grammar takes `hook EVENT` as `src/lodge/cli/parser.py:90-91` does: `argv[0]` `hook` with no `-h` or `--help` in `argv` gives `{ kind: "hook", event: argv[1] ?? "" }` before any other parsing; the help lists `hook` with lodge 0.2's summary `answer a Claude Code hook event: post-tool-use`, and `lodge hook -h` prints argparse's help for it.
- `run` answers the `hook` command before reading any setting: `io.hook()` for `post-tool-use`, 0 for any other event (`src/lodge/cli/commands.py:91-92`).
- `readSettings` checks `[hook]` with `parseHookSettings`, a `LodgeError` becoming a `CliError` with its message, as `_settings` does (`src/lodge/main.py:41-45`), so a malformed `[hook]` exits 2 with one sentence before any request.
- `main.ts` gives `io.hook` as `run` of `#hook` with `() => Bun.stdin.text()`, `process.stdout`'s write, `(edited) => hookContextFor(edited, { repoRootOf, isFolder })`, `resolvePath`, and `process.cwd()` (null when it throws).
- `repository.ts` (helper): `hookProject()` makes a real repository in a folder from `mkdtempSync` with `git init -b main` under `isolateGit()`, with `configure(text)` writing `.lodge.toml` as given (no `[server]` unless the test writes one), `initialise()` making `lodge/decisions/.gitkeep` and `lodge/spec/.gitkeep` where the Python test ran `lodge init`, `git(...args)`, and `run(argv, input?, cwd?)` calling `#cli`'s `run` with an `Io` whose `hook` is built as `main.ts` builds it but reads `input`, and whose `fetch` throws, since no carried hook test reaches a server.
- Every other `Io` the tests build gains `hook: async () => 0`.

- [ ] **Step 1: Write the failing tests:** every test of `tests/e2e/test_hook_feedback_after_hand_edits.py` and `tests/e2e/test_hook_outside_repository_exit_0_silent.py` by name, each parametrised case kept, through `hookProject()`; and, in `hand-edits.test.ts`, `hook_gives_the_moved_advice_for_a_project_on_the_server` (a `.lodge.toml` with `[server]` naming `https://lodge.test`: an edit under `lodge/decisions/` names it, in branch mode too); add `hook` to the names of plan 3's `help_lists_every_command`, `every_command_has_help`, and `help-lists-every-command.test.ts`.
- [ ] **Step 2: Run** `cd ts && bun test tests/hook tests/cli tests/e2e/help-lists-every-command.test.ts`; expected: the new and changed tests FAIL.
- [ ] **Step 3: Implement**; flip `tests/e2e/test_hook_outside_repository_exit_0_silent.py` to `ported`, and set the `why` of the two `changed` rows of "Parity rows this plan settles".
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`; build the binary as plan 3's Task 8 does, then `printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"},"cwd":"%s"}' "$PWD/lodge/decisions/x.md" "$PWD" | ts/dist/lodge hook post-tool-use` prints lodge 0.2's record advice for this repository, which has not moved; commit, push.

### Task 10: The round trip

**Files:**
- Create: `ts/tests/e2e/round-trip.test.ts`, `ts/scripts/round-trip.ts`, `scripts/round-trip.sh`
- Modify: `ts/tests/parity.test.ts` (the plan 4 rows)
- Report: `docs/superpowers/plans/2026-11-02-lodge-server-import/task-10-report.md`

**Interfaces:**
- Consumes: Tasks 2 to 9.
- Produces: the proof of this plan's end, and the coordinator's run on a scratch copy of lodge's own records (d-2jk0mw).
- `round-trip.test.ts`, through the server's handler in process with `isolateGit()`: `made_up_store_survives_import_and_export` (for each layout of `zeroTwoRepository`: the person imports it into the project `work`, sets an export target on a new bare repository, `exporters.settled()`, and `readStore` of the exported branch gives the original's paths, every text equal byte for byte but the `decided_by: author` line of each author decision and the `by: author` line of the thread's reply, which read the person's name, the attachment's text equal, and both `.gitkeep` files); `export_of_an_export_is_unchanged` (a second flush answers `unchanged`).
- `parity.test.ts`: `ported_files_exist` also covers plan 4's `changed` rows, and `plan_4_changed_rows_keep_every_python_test_name` runs `rowMissing` on them.
- `ts/scripts/round-trip.ts REPOSITORY REV` imports the store at `REV` into an in-process server over a store on `:memory:`, with the made-up person `ana`, exports it into a new bare repository in a temporary folder, and compares the two stores file by file; it prints the counts of files compared, files equal, files differing only in `decided_by` or a message's `by`, and other differences (each path and the first line that differs), and exits 1 on any other difference.
- `scripts/round-trip.sh` clones this repository with `git clone --no-local --quiet` into a temporary folder (d-2jk0mw: a scratch copy, never the live store), runs `bun ts/scripts/round-trip.ts <clone> HEAD`, and then lodge 0.2's `lodge spec` in a checkout of the clone and of the export, comparing the two outputs, and `lodge check` in the export's checkout, whose lines it prints.
- Under design line 78 (the export writes the person), lodge 0.2's check on the export fails check 3 for each confirmation the owner made, `lodge show` loses its "confirmed by the author", and a thread with the person's message is unreadable to lodge 0.2 (probes 3 and 7); the report lists those lines as the expected effect, and the author's answer to IMP-1 (`questions.md`) decides whether they stay.

- [ ] **Step 1: Write the failing test and the scripts.**
- [ ] **Step 2: Run** `cd ts && bun test tests/e2e/round-trip.test.ts tests/parity.test.ts`; expected: the round trip passes once Tasks 2 to 9 are merged, and any failure is fixed in the module at fault with a test that fails first.
- [ ] **Step 3: Coordinator:** `sh scripts/round-trip.sh` outside the sandbox; the report gives its counts as printed: at 0522047 the store held 221 decisions and 137 files under `lodge/spec/`, 46 of the decisions `decided_by: author`, no thread, and no attachment (probe 5), and the plans' rulings add more.
- [ ] **Step 4: Coordinator:** `sh scripts/check.sh`, commit, push.

### Tasks 11a, 11b, and 11c: The design into lodge

The server is built (plans 1 to 4), so what it makes false in lodge's specification is edited now (d-j3z85y), and the design goes in whole, so that its document can be frozen.
Each part is its own brief, build, and review, in this order, each holding the rules below as well as its part.

**Files:** records via `lodge add`; report `docs/superpowers/plans/2026-11-02-lodge-server-import/task-11-report.md`, which each part extends; in 11c also `docs/superpowers/specs/2026-11-02-lodge-server-design.md` (one line at the end), `.lodge.toml` (`[hook] frozen`), and `CLAUDE.md` (one line).

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
- The decisions for Export to git (lines 280 to 285) and Moving from lodge 0.2 (lines 287 to 290) create their entries from what Tasks 2 to 10 built: the branch holding only `lodge/`, the one commit a minute, the person mapping and IMP-1's answer, the import into an empty project by its owner, and the hook's moved advice.

**Task 11b: Intent, Goals, Non-goals, Must nots, Workflow as data, and Tasks** (design lines 8 to 50 and 96 to 176).
- The four must-nots added for the server (lines 47 to 50) go into `purpose` beside the first design's three, each its own entry.

**Task 11c: Sessions, Artefacts, the waiting list, Claimed and checked, Usage, Code and git, People and sign-in, Interface, Build order, Open, and Left to the builder** (design lines 178 to 317); then the document is frozen.
- Left to the builder (lines 311 to 317) becomes one entry in `rollout` naming what the design leaves open, each item with the decision that settled it where one has (d-sry12f, d-yayhct, d-4k9wcr, and the workflow's syntax still open).
- The report closes with every design line from 8 to 317 mapped to an entry or named as left out, with the reason.
- Then the design document gets its last line first, "Its content now lives in lodge (`lodge spec`, `lodge show`); this document is frozen."; only then does `.lodge.toml`'s `frozen` gain `"docs/superpowers/specs/2026-11-02-lodge-server-design.md"`, so the hook does not fire on that edit; and `CLAUDE.md`'s line naming the two frozen design documents names the three.

- [ ] **Step 1 (each part):** drafts of the new and edited entries, new areas, and the decisions; dry-run; add; the "changed since" pass.
- [ ] **Step 2: Verify (each part)** `uv run lodge check` prints `ok`; `uv run lodge spec | grep -c 'changed since'` prints 0, or the report names each remaining mark and why; in 11a, `uv run lodge show s-a4jfp1` names TypeScript and `uv run lodge show s-07ar34` no longer says there is no server; in 11c, `printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"},"cwd":"%s"}' "$PWD/docs/superpowers/specs/2026-11-02-lodge-server-design.md" "$PWD" | uv run --frozen --quiet lodge hook post-tool-use` prints the frozen-file advice.
- [ ] **Step 3: Coordinator (each part):** `git add lodge/` and the part's other files, `sh scripts/check.sh`, commit, push.
