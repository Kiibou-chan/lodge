# lodge server, build step 1, plan 3: the API, sign-in, and the command

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** the `lodge` command works at parity with lodge 0.2 against the lodge server, proved by lodge 0.2's command tests carried and run against an in-process server and through the compiled binary, and one person can register a passkey, sign in, issue agent tokens, and approve decisions drafted in their name on a minimal page.

**Architecture:** two adapters over plan 2's `app` and `store` (d-k5swcq): `api`, a `fetch` handler serving `POST /api/v1/<operation>` with JSON (d-sry12f), bearer tokens for agents, and passkeys and a session cookie for the person (d-yayhct); and `cli`, the command, which reads `.lodge.toml`, sends each operation to the server named there, and prints what lodge 0.2 prints.
`src/main.ts` wires both into one program built with `bun build --compile`: the command, and `lodge server setup` and `lodge server serve` (d-vfyex3).
The page of d-jtxwg3 is `api`'s last task.

**Tech stack:** plan 1's (Bun 1.3.14, TypeScript 6.0.3 strict, Biome 2.5.15, dependency-cruiser 18.6.0, knip 6.42.0), plan 2's Kysely over `bun:sqlite`, and two dependencies added by Task 1: @simplewebauthn/server 14.0.3 in `api` (d-yayhct) and smol-toml 1.9.1 in `cli` (d-dfkqec).

**Spec:** `lodge spec` and lodge 0.2's tests for what the command does; `docs/superpowers/specs/2026-11-02-lodge-server-design.md` (the design, approved by the author 2026-11-02 13:52) for where it lives and what changes.
The plan argues from them, never over them; where they disagree with this plan, they win and the builder reports it.
"Design line N" is a line of the design; "probe N" is an item of `docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md`, whose sources are in `probes/` beside it; "plan 1, probe N" is an item of plan 1's.
Plan 1's files are named at their paths under `docs/superpowers/plans/done/`, where plan 1's last task moves them before this plan builds.

## Global Constraints

Plan 1's Global Constraints hold unchanged (`docs/superpowers/plans/done/2026-11-02-lodge-server-core.md`, "Global Constraints"); each brief repeats them, with these for this plan:

- This plan starts from `server-core` after plan 1's fix wave, which lands d-d0vca9 in `ts/tests/structure/calls.ts`: outside `git`, `write` and its kin are file writes only when imported from `fs`, and `.write` only on a `Bun.file(…)`.
  So `main` prints the command's output through `process.stdout.write` and `process.stderr.write`, byte for byte, and `api` writes its log only through `ApiOptions.log`, which `main` binds to `process.stderr.write` and the tests to an array.
- Builders are Codex (`codex exec`), one task per brief, with no network, a read-only git index, and no sockets; a package the task needs that `ts/package.json` lacks stops the task with BLOCKED and its name.
- The builder's gate is `sh scripts/check-ts.sh`; the coordinator's is `sh scripts/check.sh` outside the sandbox after every task, then it stages with explicit paths, commits with `git -c user.name="Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, the message ending `Co-Authored-By: Claude <noreply@anthropic.com>`, and pushes `server-api` (or the task's lane branch) to `origin`; never `main`.
- No test opens a socket: the server is reached through its handler, `handler(request)` (plan 1, probe 1), and the command through `run(argv, io)` with `io.fetch` bound to that handler.
  A test that needs a socket is a coordinator check, named in its task under **Coordinator** and run outside the sandbox (S1 to S3 below).
- A test that starts a child process uses `Bun.spawn` and awaits it, never `Bun.spawnSync` against a server in the same process, which never returns (probe 5).
- Structure (plan 1, Task 3; d-x6f9za, d-mfskz3, d-s5s2c3): `api` may use `fetch`, sockets (`Bun.serve`), `crypto`, and `process`, and reads no file (`Bun.file` and `node:fs` are `git`'s and `cli`'s), so its page and script come in as text imports (d-5kskm3); `cli` may read files and use `fetch` and writes none; `main` (`src/main.ts`) may import every package, and neither writes files nor opens sockets itself, printing to standard output and error not being a file write (d-d0vca9).
  Raising a limit or adding an allowed edge is the author's call; a task that finds it needs one stops with BLOCKED.
- Porting (d-88p8h9, plan 1's "Porting"): a carried command test keeps its Python name as its title, in the file the parity table names, and asserts what the Python asserts, no weaker, with the three substitutions of d-bwb1tt only: what lodge 0.2 reads from git (`git status`, the staged files, a file under `lodge/`) is read from the server's store; the outcome `staged` is `published`, since a record is current from the moment it is written (design line 80); and an add or a thread message held for a person (d-znagqe, d-2v8vtk) is approved through the person's session, the test asserting the held line and then the approval's outcome, and reading the IDs from the approval (Task 7a's `seed`, d-4qv0xb).
  Where the server refuses what a Python test does, a hand edit rewriting a published decision (d-j28rp0), the test writes a new file as d-4qv0xb says, and its parity row is `changed` with that reason.
  A test d-bwb1tt drops is named in its row's `dropped` list in `ts/tests/parity.json` with the reason in `why`; every other name of a `changed` row is kept as for a `ported` row (Task 7a's parity change).
- The command prints what lodge 0.2 prints, byte for byte, wherever the parity table does not mark a change: its outputs are ports of `src/lodge/cli/output.py` and `thread_output.py`, fed by the server's answers decoded back into `app`'s results (d-3ywdhq).
- No secret in a URL, a log line, or the repository (must-not 6): the agent token travels only in `Authorization`, the session only in its cookie, and the server stores tokens, sessions, and setup codes only as SHA-256 hashes (d-kt4jkq).
- Exports read in a later task (d-tha8st): a file with an export whose first reader comes in a later task goes into `ts/knip.json`'s `entry` in the task that creates it and leaves in the task that gives it that reader, each task listing `ts/knip.json` under Modify; the files are in the table below.
- User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; code comments state the fact.

### Exports read in a later task

From the import lines of `tests/e2e/test_*.py` (`grep -l 'document\|entry_text\|area_text' tests/e2e/test_*.py`):

| File | Into `entry` | Names and the task that first reads them | Out of `entry` |
|---|---|---|---|
| `ts/tests/e2e/support.ts` | Task 7a | `document` (7b, `add-non-string-scalar-exits-2`), `entryText` and `areaText` (7b, the add tests) | Task 7b |

## Calls made

Each is the planner's ruling, recorded in lodge with scope `process` and this plan as its work item; its reasoning there holds a handle per argument and the cost if wrong.
Every task repeats what it needs of them, so no brief needs this section.

1. d-p8jdqj: the plan is ten tasks (1 to 6, 7a, 7b, 8, and the page as 9), run in lanes by the import graph (see "Order and lanes").
2. d-1zmfdr (replacing d-z1pncx): the command finds the repository's root by walking up from its folder to the first that holds `.git`, and reads the server's URL and the project's name from `[server]` in `.lodge.toml` there; it sends the agent token of the environment variable `LODGE_TOKEN` as `Authorization: Bearer` when it is set and not empty, and no `Authorization` otherwise, since a cloud session's token is a network secret the proxy adds and the session never sees (research note, line 43; design lines 49, 192, and 213); it talks `http` only to this machine (`localhost`, `127.0.0.1`, `[::1]`), and `https` otherwise.
3. d-dfkqec: the command parses `.lodge.toml` with smol-toml 1.9.1 and `integersAsBigInt`, which gives integers as `bigint` and floats as `number` (probe 1), so `title_chars = 80.0` is refused with lodge 0.2's sentence (probe 2), where `Bun.TOML.parse` gives the whole number 80 and also accepts a table header with no closing bracket (probe 1).
4. d-y0ppty: a project's `[length]` and `[import]` settings live on the server, given once by `lodge init` from `.lodge.toml` and kept in the body of plan 2's `project` event, so that every client's check of the project uses the same settings; changing them later is outside build step 1, and the guide says so.
5. d-kt4jkq: an agent token is issued by the signed-in person for one project's name, with an optional agent role its requests act as, shown once, stored as its SHA-256, and revocable; it may create that project and call every operation on it but the person's; `held`, `approve`, `decline`, `confirm`, and the token and project lists answer only the person's session cookie, sent with the server's own `Origin`.
6. d-3ywdhq: on the wire a field keeps its TypeScript name (`dryRun`, narrowing d-sry12f's `dry_run`), a `Map` or `Set` is tagged, `api` encodes and `cli` decodes, a write whose check fails answers 422 with its whole result, an unknown project answers kind `no-project`, an unexpected error kind `internal` (500), and every answer carries `Lodge-Version`, which the command requires to equal its own.
7. d-vfyex3: there is one program, `lodge`; `src/main.ts` sends `lodge server setup` and `lodge server serve` to `api`'s `serverCommand` and everything else to `cli`'s `run`, since the layout allows one file at the root of `src` (`ts/tests/structure/calls.ts`, `layoutViolations`); it narrows d-yayhct's `lodge-server setup`; `ts/package.json` gains `"version": "0.3.0"`, which `--version` prints.
8. d-rn4qzq: the server's origin (`https://name` or `http://localhost:port`) and the person's name are fixed by the first `lodge server setup`; passkeys are created and used with user verification required; a session lasts 30 days; a ceremony's challenge lives in the server's memory for 5 minutes and is spent on use.
9. d-kky8qc: the command's grammar is a small parser of its own in `cli`, written to argparse's usage lines and messages (probe 6), with no library.
10. d-bwb1tt: the carried command tests run the command in process against an in-process server built from plan 2's store on `:memory:`, the person signed in with the software authenticator of plan 1, probe 2; a hand edit of a record file is a write through the store that bypasses `app`; and with `LODGE_E2E_BINARY` set, the same tests run the compiled binary against that server on a loopback socket (S1).
11. d-5kskm3: the page and its script are text imports into `api` (`page.html` cast to `string`, `page.js` typed by `src/api/text.d.ts`), and the guide is a text import into `cli` (`src/cli/text.d.ts`), all embedded in the binary (probe 3).
12. d-amxk94 (replacing d-djh40k): Task 8 turns on knip's `includeEntryExports` (d-s2rdn2); an export nothing reads is removed, unless a front-door test requires it (`__all__` of lodge 0.2's `core` and `app`, and `#app`'s allowed additions) or plan 4's table of consumed names lists it, which is tagged `/** @public */` where it is defined (probe 4); a test file's unread export loses its `export`.
13. d-zthdm7 (narrowing d-p8jdqj): Task 7a stays one task; its report maps every ported function of `output.py`, `thread_output.py`, `commands.py`, and `threads.py` to the carried tests that assert its lines, and a function no carried test pins is seen failing against a named mutation.
14. d-svv7gv (narrowing d-4psbdv): `ts/bunfig.toml` sets `minimumReleaseAge = 1209600` under `[install]`, so every package `bun install` resolves, transitive ones included, is at least two weeks old; Task 1 checks the versions new in `ts/bun.lock`.
15. d-4qv0xb (replacing d-81ps01, narrowing d-bwb1tt): a carried test whose Python rewrites a published decision by hand writes a new file instead, since the store refuses a changed decision file (d-j28rp0); a carried test whose agent writes `--by author` with where and when gets the message held for the author (d-2v8vtk), asserts the held line, and approves it through the person's session, reading the thread's ID from the approval; probe 8 gives `check_and_gate`'s lines.

## Review Focus

1. A carried command test that asserts less than its Python original beyond d-bwb1tt's three substitutions and d-4qv0xb's changes, or a `changed` row whose kept tests lose a name.
2. Output: a line the command prints that differs from lodge 0.2's for the same records, an exit code that differs, or something printed on standard output that lodge 0.2 prints on standard error.
3. Authorisation: an operation an agent token reaches that d-kt4jkq gives the person only, a token reaching another project, a cookie request without the server's `Origin` accepted, a setup code accepted twice or after 15 minutes, a passkey's counter going backwards accepted.
4. Secrets: a token, session, or setup code stored, logged, or put in a URL in clear, or a response that echoes one beyond the single answer that issues it.
5. Settings: `.lodge.toml` read as lodge 0.2 reads it wherever d-1zmfdr and d-dfkqec do not change it, every malformed file one sentence and exit 2 before any request.
6. The page: text from records reaching the page as HTML rather than text, or a script loaded from anywhere but the server.

## Order and lanes

The build starts after plan 1 merges into `server-api`; Tasks 4 to 9 also need plan 2 (`store` and `app`) merged into `server-api` first, its Task 12c included (held messages, d-2v8vtk), since they import `#app` and `#store`.
Lanes follow the import graph, each in its own worktree merged into `server-api`, as plan 1's lanes are (d-xdqsmf):

| Task | Imports | Needs | Lane |
|---|---|---|---|
| 1 | none | plan 1 | coordinator, first |
| 2 | `#core` | 1 | A, beside 3 and 4 |
| 3 | `#core`, smol-toml | 1 | B, beside 2 and 4 |
| 4 | `#core`, `#app`; edits `store` (Kysely over `bun:sqlite`) | 1, plan 2 | C, beside 2 and 3 |
| 5 | `#core`, `#app`; tests `#store` | 4 | C |
| 6 | `#core`, `#app`, @simplewebauthn/server | 5 | C |
| 7a | `#core`, `#app` (types); tests `#api`, `#store` | 2, 3, 6 | main line |
| 7b | as 7a | 7a | main line |
| 8 | every package | 7b | main line |
| 9 | `#core`, `#app` | 6 | D, beside 7a to 8; its browser check (S3) after 8 |

Tasks 2 and 3 both create files in `src/cli` and touch `src/cli/index.ts` and `package.json`'s `imports`; the second to merge keeps both entries.
Task 9 is the plan's last task by d-jtxwg3; by the import graph it can be built beside 7a to 8, and it merges last: once Task 8 has merged, lane D is rebased onto `server-api` and its gate run again, under Task 8's `includeEntryExports`, before its review.

Before the brief of Task 4, the coordinator, outside the sandbox:

1. merges plan 2 into `server-api`, keeping both sides of `ts/package.json` (plan 2's `kysely` and `#app` and `#store`, this plan's packages, `version`, and `#cli`), regenerates `ts/bun.lock` with `bun install` under Task 1's `ts/bunfig.toml`, checks `bun install --frozen-lockfile`, and runs `sh scripts/check.sh`;
2. diffs "Names consumed from plan 2" below against the merged `ts/src/app/index.ts`, `ts/src/store/index.ts`, `ts/tests/app/fakes.ts`, and `ts/tests/app/support.ts`, and against plan 2's ledger rulings; a mismatch is a plan fix round of this plan, with plan 4's planner told, before any brief of Tasks 4 to 9 is written.

## Coordinator checks

These need a socket, a built binary, or a browser, so the coordinator runs them outside the sandbox and records each result in the ledger line of its task.

- **S1** (Task 8): `cd ts && bun run build && LODGE_E2E_BINARY="$PWD/dist/lodge" bun test tests/e2e`: every carried command test passes with the compiled binary as the command, talking over a loopback socket to the in-process server (d-bwb1tt); `binary.test.ts` builds its own binary in either mode, and no carried test skips in binary mode, so the ledger line gives the pass, skip, and fail counts and a skip is a finding.
  Then the server's own socket: `dist/lodge server setup --data <scratch>/lodge.db --origin http://localhost:8787 --person ada`, `dist/lodge server serve --data <scratch>/lodge.db` in the background with its PID kept, and `curl -s -i -X POST -H 'Content-Type: application/json' -d '{}' http://127.0.0.1:8787/api/v1/me` answers 200 with `Lodge-Version: 0.3.0` and a body holding `"setUp":false` and `"signedIn":false`; then `kill` of that PID.
- **S2** (Task 9, during S3): the server runs as `LOG_TOKENS=1 LOG_STREAM=1 dist/lodge server serve …`, an `add` goes through it, and its output holds none of the `yaml` package's token or stream lines (d-v9mw2d).
- **S3** (Task 9, after Task 8): in a real browser, the coordinator registers a passkey with the setup code, signs out and in, issues an agent token, runs `lodge init` and an `add` of a decision drafted in the person's name from a scratch repository with that token, which the server holds (d-znagqe), approves it on the page, and sees `lodge show` give it as current (d-jtxwg3); a browser's virtual authenticator from its developer tools counts.

## Names consumed from plan 2

Aligned against plan 2 at `0244e79` of `origin/server-store`, after its fix rounds (Task 12c of a035344, and the coordinator's ruling on its recheck R3-1) (`docs/superpowers/plans/2026-11-02-lodge-server-store.md`, "Interfaces for plans 3 and 4", and its ledger's alignment notes for plan 3), whose names are those of `src/lodge/app` in camelCase with its additions marked; every operation of `Lodge` is `async` and takes its defaulted parameters as one trailing options object (d-59q4jc, d-vd3175).

- `#app`: `Lodge` (`new Lodge(store, clock, ids, settings, actor)`, with `search`, `show`, `waitingAll`, `timeline`, `spec`, `problems`, `check`, `draft`, `mint`, `add`, `ask`, `reply`, `close`, `threads`, `thread`, `threadsWaiting`, `confirm`, `behindArea`, `held`, `approve(seq)`, and `decline(seq, reason)`); the errors `LodgeError`, `NotFound`, `Conflict`, `StaleList`, and `Forbidden`, and `coreSettings(table)`, which words a bad table as `.lodge.toml: …`; the results `Added` (with `awaits` and `held`), `AddOutcome` (with `HELD`, `"held for approval"`), `Behind`, `Listed`, `Read`, `Shown`, `ThreadList`, `ThreadShown`, `ThreadsWaiting`, and `Written` (with `awaits` and `held`, Task 12c), `Held`, and `Approved`; the ports `Clock` (`now(): Now`, `{ epochMs, offsetMinutes }`, and `sleep(seconds): Promise<void>`), `IdSource`, `Store`, and `Projects` (`create`, `members`, `addMember`, `storeFor(project, actor)`); `Actor`, `person(name)`, `agent(role)`, and `actorText`; `stampOf(now)`; `Store.trees()` (one tree twice) and `Store.attachmentTexts()` (every attachment's text by path, which `stored` reads for a path under `lodge/attachments/`, since the tree lists attachments without their text).
- Test helpers of plan 2: `FixedClock(start: Now = START, stepMs = 0)` of `ts/tests/app/fakes.ts`, with `calls`, `slept`, `now()`, and `async sleep(seconds)`, which moves it on by `seconds` (and records them in `slept`), the one way this plan's expiry tests move time; `CountingIds`; `project()` and `wired(store, clock, ids, actor = person("author"))` of `ts/tests/app/support.ts`.
- `#store`: `openDatabase(path)` (`":memory:"` or a file), `SqliteProjects(database, clock)`, `SqliteStore`, `rebuild`, and the events table with its `applyEvent` cases, to which a later plan adds kinds, derived tables, and a migration (plan 2, "Interfaces for plans 3 and 4"); `applyEvent` inserts a `heads` row only for a `project` event and otherwise updates `heads` where the project matches, never upserting, so this plan's account events, whose `project` is the empty text, add no `heads` row; a store transaction that reads before it writes opens with a write (d-thvvzx), so a racing `create` throws `Conflict`.
- `Store.publish` refuses a changed text for a decision file its base holds (d-j28rp0), so no hand edit rewrites a published decision (d-4qv0xb); it runs no other check.
- Plan 2's Task 12c (d-2v8vtk, the author's answer C to STORE-1): an agent's `ask`, `reply`, or `close` whose `by` names a person is held for that person, answering `Written` with `outcome` `HELD`, `awaits` the person, `held` the hold's number, and `ids` the thread's ID for a reply or close or a provisional ID for an ask, whose real ID is minted at the approval; a person writing under their own name is published at once, and under another's name `Forbidden`; a held message changes no thread's waiting state, which follows the last published message only, and the person sees it through `held()` on the approval page (the coordinator's ruling on plan 2's recheck R3-1), so no test of this plan asserts waiting on a held message; lodge 0.2's refusals come first.
- `HeldDraft` is `HeldAdd | HeldMessage` by `kind` (`"add"`: `person`, `by`, `drafts`, `attachments`, `importing`, `message`; `"message"`: `person`, `by`, `operation` `ask`, `reply`, or `close`, `ref`, `raises`, `text`, `where`, `when`), `Held` is `HeldDraft & { seq, at }`, and `Lodge.approve(seq)` answers `Approved`, `{ kind: "add", added }` or `{ kind: "message", written }`; an unknown or settled hold is `NotFound("nothing is held under number <seq>")`, and another actor's approval or decline `Forbidden("only <person> approves this; nothing was written")`.
- `Tree.people` is the project's owners, and `confirm` refuses an actor not among them (d-vwsnz5, replacing d-kj59bz).
- A person's name is `^[a-z][a-z0-9-]{0,31}$` and a project's `^[a-z0-9][a-z0-9-]{0,62}$` (d-wx7d0f); lodge 0.2's words stay for a person named `author` (d-vwsnz5), so the carried command tests run with the server's person named `author`.
- An agent's add of a decision `decided_by` a person is held whole until that person approves it (d-znagqe): `add` answers `HELD`, its IDs provisional, and `approve(seq)` adds it again as that person, minting the decision's ID then; a carried test whose add or relayed message is held approves it through the person's session and reads the IDs from the approval's answer (the parity section's last paragraph).
- `test_thread_fix_paths.py` is this plan's row (d-rp74dr): plan 2 leaves `orphaned_thread_outputs` and `run_thread_outcomes` as `test.todo`s in `ts/tests/app/thread-fix-paths.test.ts`, and Task 7a turns them into tests.
- What this plan adds to plan 2's packages is Task 4's: the accounts' events, and the project's settings in `Projects` (d-y0ppty).

## Parity table, this plan's rows

Plan 1's table gives these rows plan 3; this plan settles each one's final status, which the task named writes into `ts/tests/parity.json` in its last step.
A `changed` row keeps its file, gives its `why`, and lists in `dropped` the Python tests with no counterpart; every other name of the row is checked as a `ported` row's is (Task 7a).
"Store for git" means d-bwb1tt's substitution: what the Python test reads from git or from a file under `lodge/` is read from the server's store, and `staged` is `published`.

| Python file | Task | TypeScript counterpart | Status, `dropped`, and why |
|---|---|---|---|
| `tests/e2e/conftest.py` | 7a | `ts/tests/e2e/project.ts` | ported; the server it talks to is `ts/tests/e2e/server.ts` |
| `tests/e2e/support.py` | 7a | `ts/tests/e2e/support.ts` | ported |
| `tests/e2e/test_add_attach.py` | 7b | `ts/tests/e2e/add-attach.test.ts` | changed; dropped `attachment_lands_on_the_branch_in_branch_mode`; design line 72: no branch mode on the server; store for git in the others |
| `tests/e2e/test_add_bad_yaml_exits_2_naming_file_and_line.py` | 7b | `ts/tests/e2e/add-bad-yaml-exits-2-naming-file-and-line.test.ts` | ported |
| `tests/e2e/test_add_dry_run.py` | 7b | `ts/tests/e2e/add-dry-run.test.ts` | ported; store for git |
| `tests/e2e/test_add_failing_check_exits_1.py` | 7b | `ts/tests/e2e/add-failing-check-exits-1.test.ts` | ported; store for git |
| `tests/e2e/test_add_import.py` | 7b | `ts/tests/e2e/add-import.test.ts` | ported; store for git; the import of a decision by `author` is held and approved (d-bwb1tt's third substitution) |
| `tests/e2e/test_add_new_decision_entry_area.py` | 7b | `ts/tests/e2e/add-new-decision-entry-area.test.ts` | ported; store for git, the five staged files being the three records, since `init` creates no `.gitkeep` |
| `tests/e2e/test_add_non_string_scalar_exits_2.py` | 7b | `ts/tests/e2e/add-non-string-scalar-exits-2.test.ts` | ported |
| `tests/e2e/test_before_init_one_sentence_exit_2.py` | 7a | `ts/tests/e2e/before-init-one-sentence-exit-2.test.ts` | ported; the sentence is kept through kind `no-project` (d-3ywdhq) |
| `tests/e2e/test_broken_agent_decision_warns_above_show.py` | 7a | `ts/tests/e2e/broken-agent-decision-warns-above-show.test.ts` | changed; dropped none; d-4qv0xb: the store refuses a rewritten decision (d-j28rp0), so one hand edit writes the broken agent decision, as a new file, and the entry's edited text, the state the Python test reaches |
| `tests/e2e/test_check_and_gate.py` | 7a | `ts/tests/e2e/check-and-gate.test.ts` | changed; dropped `gate_passes_with_notes_for_new_records`; design line 79: the published state is the current state, so check 5 (`src/lodge/core/check_immutable.py`) cannot fire and the gate notes a state problem as `already published` and passes, and the store refuses a rewritten decision (d-j28rp0), so `check_and_gate` writes a new decision that fails check 3 by hand (d-4qv0xb, probe 8); a gate after `seed` has no new records to note |
| `tests/e2e/test_draft_then_add_edit.py` | 7b | `ts/tests/e2e/draft-then-add-edit.test.ts` | ported; store for git |
| `tests/e2e/test_guide.py` | 7a | `ts/tests/e2e/guide.test.ts` | changed; dropped none; design line 72: the guide's lines on git (checkout and branch modes, the rewritten branch, the machine's clock) describe the server instead, so `guide_is_short_and_covers_the_write_path` looks for the new line |
| `tests/e2e/test_help_lists_every_command.py` | 7a | `ts/tests/e2e/help-lists-every-command.test.ts` | changed; dropped none; d-sry12f: `view` waits for step 3's interface and `hook` for plan 4, so the list of commands holds neither, and `version_works_anywhere` prints `ts/package.json`'s version (d-vfyex3) |
| `tests/e2e/test_id.py` | 7a | `ts/tests/e2e/id.test.ts` | ported |
| `tests/e2e/test_init.py` | 7a | `ts/tests/e2e/init.test.ts` | changed; dropped `init_in_an_unwritable_checkout`; design line 72: `init` creates the project on the server and writes no file, and its output names the project and the server |
| `tests/e2e/test_malformed_settings_one_sentence_exit_2.py` | 7a | `ts/tests/e2e/malformed-settings-one-sentence-exit-2.test.ts` | changed; dropped none; d-1zmfdr: `[store]` is an unknown section on the server, so the third case expects that sentence, and a fourth case refuses `title_chars = 80.0` (d-dfkqec) |
| `tests/e2e/test_outside_repository_one_sentence_exit_2.py` | 7a | `ts/tests/e2e/outside-repository-one-sentence-exit-2.test.ts` | ported |
| `tests/e2e/test_same_second.py` | 7b | `ts/tests/e2e/same-second.test.ts` | changed; dropped `agent_edit_in_the_same_second_publishes_in_branch_mode`; design line 72: no branch mode on the server; the clock that stands still is the server's |
| `tests/e2e/test_search.py` | 7a | `ts/tests/e2e/search.test.ts` | ported |
| `tests/e2e/test_search_limit.py` | 7a | `ts/tests/e2e/search-limit.test.ts` | ported |
| `tests/e2e/test_search_shows_unparsable_file.py` | 7a | `ts/tests/e2e/search-shows-unparsable-file.test.ts` | ported; the hand edit through the store |
| `tests/e2e/test_show_ambiguous_code_one_line.py` | 7a | `ts/tests/e2e/show-ambiguous-code-one-line.test.ts` | ported; the hand edit through the store |
| `tests/e2e/test_show_levels.py` | 7a | `ts/tests/e2e/show-levels.test.ts` | ported |
| `tests/e2e/test_spec.py` | 7a | `ts/tests/e2e/spec.test.ts` | ported |
| `tests/e2e/test_threads.py` | 7b | `ts/tests/e2e/threads.test.ts` | changed; dropped `thread_files_are_staged_not_committed`; design line 72: a thread is written to the server's store, with nothing staged or committed; store for git in the others; `author_words_are_recorded_exactly`'s relayed question is held and approved (d-bwb1tt's third substitution, d-2v8vtk) |
| `tests/e2e/test_waiting.py` | 7a | `ts/tests/e2e/waiting.test.ts` | ported; `waiting_groups_threads`'s relayed question is held and approved (d-bwb1tt's third substitution, d-2v8vtk) |
| `tests/app/test_thread_fix_paths.py` | 7a | `ts/tests/app/thread-fix-paths.test.ts` | ported; plan 2 writes the file with `waiting_reads_one_snapshot` and leaves `orphaned_thread_outputs` and `run_thread_outcomes` as `test.todo`s for this plan (d-rp74dr) |
| `tests/test_entry_point.py` | 8 | `ts/tests/e2e/binary.test.ts` | ported; the compiled binary's `--version` |
| `tests/test_wheel.py` | 8 | `ts/tests/e2e/binary.test.ts` | changed; dropped `installed_wheel_runs`; design line 55: the command ships as a binary built with `bun build --compile`, which `compiled_binary_runs` builds and runs |

Where plan 2's model change holds an agent's add of a decision `decided_by` a person, or an agent's thread message by a person, until that person approves it (SRV-2, d-znagqe, d-2v8vtk), a carried test whose add or message is held (`seed` with `decided_by="author"`, `test_add_import.py`'s import, and the `--by author` messages of `test_threads.py` and `test_waiting.py`) asserts the held line, `held for approval by author as hold <n>; nothing is current until they approve it`, approves hold `<n>` through the person's session, asserts the approval's outcome `published`, and reads the record's or thread's ID from the approval's answer; `support.ts`'s `seed` does so for adds, and the task's report lists each such test; that is d-bwb1tt's third substitution, not a weakening.

---

### Task 1: The dependencies

The coordinator does this task outside the sandbox, since it installs packages (d-4psbdv).

**Files:**
- `ts/bunfig.toml` exists already (d-svv7gv; added by plan 1's final fix wave, `server-core` 4f5d5fb); check it holds `minimumReleaseAge = 1209600`
- Modify: `ts/package.json`, `ts/bun.lock` (by `bun install`), `ts/knip.json`

**Interfaces:**
- Produces: `@simplewebauthn/server` 14.0.3 and `smol-toml` 1.9.1 in `ts/package.json`'s `dependencies`, each at least two weeks old on 2026-11-02 (probe 7); `"version": "0.3.0"` in `ts/package.json` (d-vfyex3).
- `ts/knip.json`'s `ignoreDependencies` gains both names, since no code imports them yet; Task 3 takes `smol-toml` out and Task 6 `@simplewebauthn/server`, as plan 1's Tasks 4 and 5a did for `yaml` and `@noble/hashes`.

- `ts/bunfig.toml` holds `[install]` with `minimumReleaseAge = 1209600` (two weeks in seconds), so `bun install` resolves every package, a dependency's own included, to a version published at least two weeks before (d-svv7gv; with it Bun 1.3.14 resolves `tslib` 2.8.1 where a plain install takes 2.9.1 of 2026-10-30, practice review I-7).

- [ ] **Step 1:** Check `ts/bunfig.toml`; add the two dependencies and the version; in `ts/`, `bun install`, then `bun install --frozen-lockfile`, then `bun x biome format --write package.json`.
- [ ] **Step 2: Verify** `grep -c '"[~^]' ts/package.json` prints 0; for each package version that `git diff ts/bun.lock` adds, `npm view <package>@<version> time --json` gives a publication date at least 14 days before the day of the install, one request at a time; `sh scripts/check.sh` exits 0.
- [ ] **Step 3:** Commit `ts/package.json`, `ts/bun.lock`, and `ts/knip.json`; push; the ledger line names the versions, the transitive ones with their dates.

### Task 2: The command's grammar

**Files:**
- Create: `ts/src/cli/args.ts`, `ts/src/cli/grammar.ts`, `ts/src/cli/index.ts`
- Modify: `ts/package.json` (`"#cli": "./src/cli/index.ts"` in `imports`; no dependency)
- Test: `ts/tests/cli/args.test.ts`, `ts/tests/cli/grammar.test.ts` (new)

**Interfaces:**
- Consumes: plan 1's `#core` (`filters`, `Filters`, `Scope`, `Raises`, `pyRepr`).
- Produces, through `#cli`:
  ```ts
  // grammar.ts, from src/lodge/cli/parser.py and the grammar half of threads.py
  export type Command =
    | { readonly kind: "init" }
    | { readonly kind: "id"; readonly prefix: "d" | "s" }
    | { readonly kind: "search"; readonly query: string; readonly filters: Filters; readonly limit: number }
    | { readonly kind: "show"; readonly ref: string; readonly reasoning: boolean; readonly provenance: boolean }
    | { readonly kind: "draft"; readonly ref: string }
    | { readonly kind: "add"; readonly files: readonly string[]; readonly importing: boolean; readonly dryRun: boolean; readonly attachments: readonly string[] }
    | { readonly kind: "check"; readonly gate: boolean }
    | { readonly kind: "spec"; readonly area: string | null }
    | { readonly kind: "waiting" }
    | { readonly kind: "guide" }
    | { readonly kind: "threads" }
    | { readonly kind: "thread"; readonly ref: string }
    | { readonly kind: "ask"; readonly ref: string; readonly raises: Raises; readonly by: string; readonly where: string | null; readonly when: string | null; readonly file: string }
    | { readonly kind: "reply"; readonly ref: string; readonly by: string; readonly where: string | null; readonly when: string | null; readonly file: string }
    | { readonly kind: "close"; readonly ref: string; readonly by: string; readonly where: string | null; readonly when: string | null; readonly file: string | null };
  export type ThreadCommand = Extract<Command, { readonly kind: "threads" | "thread" | "ask" | "reply" | "close" }>;
  export interface Exit { readonly kind: "exit"; readonly code: number; readonly out: string; readonly err: string }
  export function parse(argv: readonly string[], version: string): Command | Exit
  ```
- `args.ts` is a small parser of declared commands (d-kky8qc): each command has a name, a summary, positionals (required, optional as `?`, one or more as `+`, with choices or a converter), and options (a flag, a value, a repeatable value, with choices, a converter, a default, or required); it reads options before, between, and after positionals, `--name=value`, `--` as the end of options, and a unique prefix of a long option as that option, as argparse's `allow_abbrev` does.
- What `parse` gives, as lodge 0.2 gives it (probe 6, `src/lodge/cli/parser.py`, `src/lodge/cli/threads.py`):
  - `--version` anywhere before the command: `Exit` 0 with `lodge <version>\n` on `out`.
  - `-h` or `--help`: `Exit` 0 with the help on `out`; the top-level help has parser.py's description and epilog, a line `usage: lodge [-h] [--version] COMMAND ...`, and one line per command beginning with its name, then its summary; a command's help begins `usage: lodge <name> `, then its options and positionals in argparse's form, then its summary.
  - A usage error: `Exit` 2 with the command's usage line, then `lodge <name>: error: <message>` (or `lodge: error: …` before a command), each ending in `\n`, on `err`; but leftover words, which argparse reports from the top-level parser, give the top-level usage line `usage: lodge [-h] [--version] COMMAND ...` and `lodge: error: unrecognized arguments: <words>` whatever the command (lodge 0.2, `lodge thread q-aaaaaa extra`, correctness review M-1); the messages are argparse's: `the following arguments are required: <names joined by ", ">`, `argument <name>: invalid choice: <pyRepr of the value> (choose from <choices joined by ", ">)`, `argument --limit: <pyRepr of the value> is not a positive whole number`, `argument <name>: expected one argument`, `unrecognized arguments: <words joined by " ">`, and `ambiguous option: <word> could match <options joined by ", ">`.
  - The commands, summaries, and options of parser.py and threads.py, but `view` and `hook` (d-sry12f; `hook` comes with plan 4): `init`, `id`, `search`, `show`, `draft` (its summary holding "a decision is immutable"), `add`, `check`, `spec`, `waiting`, `guide`, `threads`, `thread`, `ask`, `reply`, and `close`.
  - Help bodies and wrapped usage lines follow argparse's layout at 80 columns (`COLUMNS=80`) as far as the carried tests and probe 6 check them; the report lists any other difference from `uv run --frozen --quiet lodge <name> -h` at `COLUMNS=80`.
  - `--limit` takes ASCII digits naming a number of 1 or more; Python's `isdecimal` also takes other decimal digits (`src/lodge/cli/parser.py:153`), so the report lists the narrowing.
  - The rule of `_message_command` (`src/lodge/cli/threads.py:71-82`): `--by author` without `--where` or `--when`, or `--where` or `--when` without `--by author`, is `Exit` 2 with `lodge: <its sentence>\n` on `err`, as lodge 0.2 raises a `LodgeError` there.
  - `search`'s `filters` come from `#core`'s `filters` with `kind`, `scope`, `status` (default `current`), `area`, and `decidedBy` from `--by`.

- [ ] **Step 1: Write the failing tests.**
  - `args.test.ts`: `options_before_between_and_after_positionals`; `equals_form`; `double_dash_ends_options` (`show -- -x` gives the ref `-x`); `unique_prefix_is_the_option` (`show d-aaaaaa --prov`); `ambiguous_prefix_is_an_error` (`search x --s y`: `ambiguous option: --s could match --scope, --status`); `repeatable_option_collects` (`--attach a --attach b`); `missing_value_is_an_error` (`search --kind`: `argument --kind: expected one argument`); `extra_words_are_an_error` (`thread q-aaaaaa extra`: `err` is exactly `usage: lodge [-h] [--version] COMMAND ...\nlodge: error: unrecognized arguments: extra\n`).
  - `grammar.test.ts`: `every_command_parses` (`test.each` over one argv per command and its `Command`, `search` with every filter included); `help_lists_every_command` (the fifteen names, each the first word of a line of the top-level help); `every_command_has_help` (`test.each` over the fifteen: code 0, `out` beginning `usage: lodge <name>`); `no_command_is_a_usage_error` (code 2, `err` holding `usage:` and ending `lodge: error: the following arguments are required: COMMAND\n`); `invalid_choice_is_argparse_s_line` (`search x --status gone` and `id x`, each `err`'s last line as probe 6 prints it); `missing_positional_is_argparse_s_line` (`add`: `lodge add: error: the following arguments are required: FILE`); `limit_must_be_a_positive_whole_number` (`0`, `-1`, `many`, and `٣`); `author_message_needs_where_and_when`; `where_with_an_agent_role`; `version_prints_the_version_given`; `draft_help_says_decisions_are_immutable`.
- [ ] **Step 2: Run** `cd ts && bun test tests/cli`; expected: FAIL (no module).
- [ ] **Step 3: Implement** `args.ts` and `grammar.ts`; `index.ts` exports `parse`, `Command`, `ThreadCommand`, and `Exit` (knip reports `ThreadCommand` of `grammar.ts` otherwise, practice review I-2); add `#cli` to `package.json`'s `imports`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 3: The command's settings and files

**Files:**
- Create: `ts/src/cli/errors.ts`, `ts/src/cli/settings.ts`, `ts/src/cli/files.ts`
- Create or modify: `ts/src/cli/index.ts` and `ts/package.json`'s `imports` (`#cli`): this lane runs beside Task 2, so the builder creates both when Task 2 has not merged, and the second lane to merge keeps both sides
- Modify: `ts/knip.json` (`smol-toml` leaves `ignoreDependencies`)
- Test: `ts/tests/cli/settings.test.ts`, `ts/tests/cli/files.test.ts` (new)

**Interfaces:**
- Consumes: plan 1's `#core` (`parseCoreSettings`, `SettingsError`, `CoreSettings`); smol-toml 1.9.1.
- Produces, through `#cli`:
  ```ts
  // errors.ts
  export class CliError extends Error { constructor(message: string, readonly exitCode: 1 | 2 = 2) }
  // settings.ts
  export interface ServerPlace { readonly url: string; readonly project: string }   // url without a trailing slash
  export interface ProjectSettings {
    readonly server: ServerPlace | null;
    readonly core: Readonly<Record<string, unknown>>;   // the [length] and [import] tables as read, sent by init
    readonly coreSettings: CoreSettings;
  }
  export const NO_SERVER: string   // "this repository's .lodge.toml names no lodge server; add [server] with url and project"
  export function repositoryRoot(cwd: string): string
  export function readSettings(root: string): ProjectSettings
  export function serverOf(settings: ProjectSettings): ServerPlace
  export function tokenOf(env: Readonly<Record<string, string | undefined>>): string | null
  // files.ts
  export function readDraft(path: string): string
  export function readExact(path: string, notUtf8: string): string
  ```
- `repositoryRoot` (d-1zmfdr): the nearest folder at or above `cwd` holding an entry named `.git`, a folder or a file (a worktree's); none is `CliError("<cwd> is not inside a git repository")`, lodge 0.2's sentence (`src/lodge/gitstore/setup.py:24`).
- `readSettings` (d-dfkqec, d-1zmfdr), every refusal a `CliError` whose message begins `.lodge.toml: ` and is one line:
  - no `.lodge.toml`: no server, no core table, and `coreSettings()`, as lodge 0.2 reads defaults (`src/lodge/gitstore/settings.py:42`);
  - unreadable, or not UTF-8: `.lodge.toml: cannot be read: <reason>`;
  - not TOML: `.lodge.toml: ` and the first line of smol-toml's message (probe 1);
  - parsed with `integersAsBigInt: true`, then converted: a `bigint` becomes a number, a `number` (a TOML float, `inf` and `nan` included) becomes `null`, and a date or time becomes `null`, so that `parseCoreSettings` refuses each where lodge 0.2 refuses a float or a date, with lodge 0.2's sentence and in its order (probes 1 and 2);
  - the top-level names are read in the file's order: `server` and `hook` are this package's, `length` and `import` core's, and any other name is `unknown section [<name>]` for a table and `unknown key <name>` otherwise, as `parse_core_settings` words them (`src/lodge/core/settings.py:30-35`), `store` included (lodge 0.2's `[store]` has no meaning on the server);
  - `[server]`: a table holding `url` and `project` and nothing else (`server must be a table`, `unknown key server.<key>`, `[server] needs url and project`); `url` an `https` URL, or an `http` URL whose host is `localhost`, `127.0.0.1`, or `[::1]`, with no user, path other than `/`, query, or fragment (`server.url must be an https URL, or an http URL on this machine`); `project` lower-case letters, digits, and hyphens, starting with a letter or digit, at most 63 characters (`server.project must be lower-case letters, digits, and hyphens`);
  - `[hook]` is left as it is: lodge 0.2 checks it on every command (`src/lodge/main.py:42-46`), and plan 4's hook brings that check back;
  - `core` holds the `length` and `import` tables as converted, and `coreSettings` is `parseCoreSettings` of them.
- `serverOf` throws `CliError(NO_SERVER)` when `server` is `null`; `tokenOf` gives `LODGE_TOKEN`, and `null` when it is unset or empty, so the command sends no `Authorization` and a cloud environment's network secret can add it (d-1zmfdr).
- `readDraft` reads as Python's `read_text(encoding="utf-8")` does (`src/lodge/cli/files.py`): strict UTF-8 with a byte order mark kept, then `\r\n` and a lone `\r` made `\n`; `readExact` reads as `read_bytes().decode("utf-8")`, with no change to line ends.
  Not UTF-8 is `CliError("<path>: <notUtf8>")` (`readDraft` passes `not UTF-8 text`); an unreadable file is `CliError("<path>: cannot be read: <reason>")`, the reason being the system's description of the error, which the report compares with Python's `strerror`.

- [ ] **Step 1: Write the failing tests.**
  - `settings.test.ts`, each on files written into a temporary folder: `root_is_the_nearest_folder_with_git` (a nested folder; `.git` as a folder and as a file); `outside_a_repository_is_one_sentence`; `no_settings_file_has_no_server`; `whole_number_float_is_refused` (`test.each` over `title_chars = 80.0` under `[length]`, `8e1`, `length = {title_chars = 80.0}`, and `length.title_chars = 80.0`, each `.lodge.toml: length.title_chars must be a positive whole number`); `integer_forms_are_read` (`80`, `0x50`, `+80`, `1_000`, and `99999999999999999999`); `inf_and_a_date_are_refused`; `float_in_sources_is_refused` (`.lodge.toml: import.sources must be a list of file names`); `unclosed_table_header_is_one_sentence` (`[store` with no bracket: one line beginning `.lodge.toml: `); `store_is_an_unknown_section`; `first_unknown_name_in_file_order_is_named`; `server_is_read`; `server_is_needed` (a `ProjectSettings` with `server: null`: `serverOf` throws a `CliError` whose message is `NO_SERVER` and whose exit code is 2); `server_url_must_be_https_or_this_machine` (`test.each` over refused and accepted URLs, `http://example.org`, a path, a query, and `https://user@host` among the refused, and `http://localhost:8787`, `http://127.0.0.1:9`, `http://[::1]:9`, and `https://lodge.example.org` the accepted); `server_project_is_a_name`; `server_needs_url_and_project`; `hook_is_left_alone`; `core_table_holds_length_and_import_only`; `token_comes_from_the_environment` (set gives it; unset and empty give `null`).
  - `files.test.ts`: `draft_line_ends_are_translated` (`a\r\nb\rc\n` to `a\nb\nc\n`); `draft_keeps_a_byte_order_mark`; `exact_text_keeps_its_line_ends`; `not_utf8_is_one_sentence`; `missing_file_is_one_sentence`.
- [ ] **Step 2: Run** `cd ts && bun test tests/cli`; expected: the new tests FAIL.
- [ ] **Step 3: Implement**; take `smol-toml` out of `ts/knip.json`'s `ignoreDependencies`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green, knip reporting no unused dependency.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 4: Accounts and project settings in the store

**Files:**
- Create: `ts/src/app/accounts.ts`, `ts/src/store/accounts.ts`
- Modify: `ts/src/app/ports.ts` (`Projects`), `ts/src/app/index.ts`, `ts/src/store/projects.ts`, `ts/src/store/events.ts` (the new kinds' `applyEvent` cases), `ts/src/store/schema.ts` (a migration and the derived tables), `ts/src/store/index.ts`, `ts/tests/app/front-door.test.ts` (the additions it allows), `ts/tests/store/database.test.ts` (plan 2's two schema tests, below)
- Test: `ts/tests/store/accounts.test.ts`, `ts/tests/store/project-settings.test.ts` (new)

**Interfaces:**
- Consumes: plan 2's `store` (`openDatabase`, `appendEvents`, `applyEvent`, `rebuild`, `SqliteProjects`) and `app` (`Projects`, `Clock`, `stampOf`); plan 1's `#core` (`compareStamps`).
- Produces, through `#app` (types and a port only, so `app` stays pure):
  ```ts
  export interface ServerSetup { readonly origin: string; readonly person: string; readonly at: string }
  export interface Passkey {
    readonly id: string;               // the credential ID, base64url
    readonly publicKey: string;        // the COSE public key, base64url
    readonly counter: number;
    readonly transports: readonly string[];
    readonly created: string;
  }
  export interface AgentToken {
    readonly id: string;               // t-xxxxxx, from tokenId (Task 5)
    readonly project: string;
    readonly role: string | null;      // the agent role its requests act as, agent(role)
    readonly label: string;
    readonly issued: string;
    readonly revoked: string | null;
  }
  export interface Accounts {
    setup(): Promise<ServerSetup | null>;
    setUp(setup: ServerSetup): Promise<void>;
    issueSetupCode(hash: string, expires: string): Promise<void>;
    setupCodeValid(hash: string): Promise<boolean>;
    spendSetupCode(hash: string): Promise<boolean>;
    passkeys(): Promise<readonly Passkey[]>;
    addPasskey(passkey: Passkey): Promise<void>;
    usePasskey(id: string, counter: number): Promise<void>;
    startSession(hash: string, expires: string): Promise<void>;
    sessionExpiry(hash: string): Promise<string | null>;
    endSession(hash: string): Promise<void>;
    issueToken(token: AgentToken, hash: string): Promise<void>;
    tokenFor(hash: string): Promise<AgentToken | null>;
    revokeToken(id: string): Promise<boolean>;
    tokens(): Promise<readonly AgentToken[]>;
  }
  ```
  and `Projects` gains, beside plan 2's four methods (d-y0ppty):
  ```ts
  create(project: string, owner: string, settings?: Readonly<Record<string, unknown>>): Promise<void>;   // settings default {}
  settings(project: string): Promise<Readonly<Record<string, unknown>> | null>;                            // null for an unknown project
  names(): Promise<readonly string[]>;                                                                     // in code-point order
  ```
- Produces, through `#store`: `SqliteAccounts(database, clock)`, implementing `Accounts`, and `SqliteProjects` with the three additions.
- Every change is an event in plan 2's one append-only table (design line 66), through `appendEvents`, with `at` = `stampOf(clock.now())`: the accounts' kinds `server-set-up`, `setup-code-issued`, `setup-code-spent`, `passkey-added`, `passkey-used`, `session-started`, `session-ended`, `token-issued`, and `token-revoked` belong to the server, not a project, so their `project` is the empty text, which no project's name matches (d-wx7d0f), and their actor is `server`; `applyEvent` touches `heads` for them only by its update where the project matches, which matches no row (plan 2, "Interfaces for plans 3 and 4"); the project's settings go into the body of plan 2's `project` event (`{ owner, settings }`), so a project and its settings land in one transaction.
- The derived tables (`MIGRATIONS[2]`, after plan 2's `MIGRATIONS[0]` and `[1]`, raising `user_version` from 2 to 3; plan 2, "Interfaces for plans 3 and 4"): `setup`, `setup_codes`, `passkeys`, `sessions`, `tokens`, and `project_settings`, each filled by its kinds' `applyEvent` cases and refilled by `rebuild`; nothing updates or deletes an event.
- Only hashes reach the store: the API hashes a setup code, a session, and a token before it calls (d-kt4jkq), and no event holds the clear text.
- `setUp` throws a `Conflict` when the server is already set up; `setupCodeValid` is true exactly when `hash` is the newest code issued, it is unspent, and the clock's stamp is before its `expires` (by `compareStamps`), and `spendSetupCode` is true in the same case and then spends it, reading and appending in one transaction that opens with a write (d-thvvzx), so two spends of one code cannot both be true; `sessionExpiry` is `null` for an unknown or ended session; `revokeToken` is false for an unknown or revoked token; lists keep the order of issue.

- [ ] **Step 1: Write the failing tests.**
  - `accounts.test.ts`, each over `openDatabase(":memory:")` with plan 2's `FixedClock` unless named: `server_is_set_up_once`; `setup_code_is_spent_once` (then two spends of a new code at once, through `Promise.all`, of which exactly one is true); `checking_a_setup_code_spends_nothing`; `setup_code_expires` (one second before `expires` valid, at `expires` not, the clock moved by `FixedClock.sleep`); `newer_setup_code_replaces_older`; `passkeys_keep_their_counter`; `sessions_start_and_end`; `tokens_issue_list_and_revoke`; `revoked_token_keeps_its_revocation`; `no_event_holds_a_clear_secret` (each event's body holds none of the clear values the test hashed); `server_events_belong_to_no_project` (`project` is empty, and `heads` gains no row); `accounts_survive_reopening_and_rebuild` (a database on a file in a temporary folder, closed and opened again, then `rebuild`, gives the same answers).
  - plan 2's `database.test.ts`, changed: `schema_is_created_once` expects `user_version` 3; `schema_1_is_migrated_to_2` keeps its name and its file at version 1 and now expects 3, with `held` and the six account tables present and its event kept; a new sibling `schema_2_is_migrated_to_3` builds a file at version 2 through a raw `bun:sqlite` connection (plan 2's statements for migrations 0 and 1 written out in the test, since `MIGRATIONS` is not exported) with one event, and opens it with `openDatabase` at 3, the account tables present and the event kept.
  - `project-settings.test.ts`: `create_keeps_the_settings` (then `settings` gives them); `create_without_settings_keeps_none` (`{}`, so plan 2's calls are unchanged); `unknown_project_has_no_settings` (`null`); `names_lists_the_projects`; `settings_survive_rebuild`.
- [ ] **Step 2: Run** `cd ts && bun test tests/store`; expected: the new tests FAIL, plan 2's passing.
- [ ] **Step 3: Implement**; add the new names to `front-door.test.ts`'s allowed additions.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 5: The API's handler, the record operations, and agent tokens

**Files:**
- Create: `ts/src/api/index.ts`, `ts/src/api/http.ts`, `ts/src/api/errors.ts`, `ts/src/api/wire.ts`, `ts/src/api/args.ts`, `ts/src/api/operations.ts`, `ts/src/api/auth.ts`, `ts/src/api/tokens.ts`
- Modify: `ts/package.json` (`"#api": "./src/api/index.ts"` in `imports`)
- Test: `ts/tests/api/world.ts` (helper), `ts/tests/api/handler.test.ts`, `ts/tests/api/wire.test.ts`, `ts/tests/api/operations.test.ts`, `ts/tests/api/bearer.test.ts` (new)

**Interfaces:**
- Consumes: Task 4's `Accounts` and `Projects` additions; plan 2's `Lodge` (its methods taking options objects, d-vd3175), `Projects`, `Actor`, `person`, `agent`, `coreSettings` of `#app`, `stampOf`, its errors (with `Forbidden`) and results; plan 1's `#core` (`parseCoreSettings`, `filters`, `compareStamps`).
- Produces, through `#api`:
  ```ts
  export interface ApiOptions {
    readonly accounts: Accounts;
    readonly projects: Projects;
    readonly lodgeFor: (project: string, settings: CoreSettings, actor: Actor) => Lodge;   // new Lodge(projects.storeFor(project, actor), clock, ids, settings, actor)
    readonly clock: Clock;                                 // app's port
    readonly random: (bytes: number) => Uint8Array;
    readonly version: string;
    readonly log: (text: string) => void;                  // the server's log; main binds it to process.stderr.write (d-d0vca9)
  }
  export function lodgesOver(projects: Projects, clock: Clock, ids: IdSource): ApiOptions["lodgeFor"]   // the lodgeFor of main and the tests
  export function handler(options: ApiOptions): (request: Request) => Promise<Response>
  export function toWire(value: unknown): unknown
  export function hashSecret(secret: string): string                       // SHA-256 of the UTF-8 bytes, in hex
  export function issueToken(options: ApiOptions, project: string, label: string, role: string | null): Promise<{ readonly token: AgentToken; readonly secret: string }>
  export function tokenId(entropy: Uint8Array): string                     // tokens.ts: "t-" and six characters, as #core's mintId spells an ID
  ```
- Routing (d-sry12f, d-3ywdhq): `POST /api/v1/<operation>` with `Content-Type: application/json` (a `charset` parameter allowed) and a JSON object as the body.
  Another method is `usage` (`use POST`); another type is `usage` (`send JSON`); a body that is not JSON is `usage` (`the body is not JSON`), and one that is not an object `usage` (`the body is not a JSON object`); an unknown operation is `not-found` (`no operation named <name>`); any other path is `not-found` (`nothing here`) until Task 9 serves the page.
- Every answer is JSON with `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, and `Lodge-Version: <version>`; success is 200 with `{"result": <toWire(result)>}`; an error is `{"error": {"kind": K, "message": M}}` with the status of its kind: `usage` 400, `unauthorised` 401, `forbidden` 403, `not-found` 404, `no-project` 404, `conflict` 409, `check-failed` 422, and `internal` 500.
  `app`'s errors map by class, most specific first: `Conflict` (and so `StaleList`) to `conflict`, `NotFound` to `not-found`, `Forbidden` to `forbidden`, `LodgeError` to `usage`, each with its message; anything else is `internal` with the message `the server failed; see its log` and the error's stack written through `options.log`, with no part of the request.
- `toWire`: `null`, booleans, strings, and finite numbers as they are; an array element by element; a `Map` as `{"$map": [[key, value], …]}` and a `Set` as `{"$set": […]}` in iteration order; any other object by its own enumerable properties in order, `undefined` ones left out; a bigint, a function, a symbol, a non-finite number, or an object with a key `$map` or `$set` throws, which the handler answers as `internal`.
- The record operations (`operations.ts`), each body holding `project` and the fields below in camelCase (d-3ywdhq), with defaults where lodge 0.2's `Lodge` has them (`src/lodge/app/lodge.py`), checked field by field (`<operation>: <field> must be <what>` and `<operation>: unknown field <name>`, both `usage`), then given to the project's `Lodge`, built by `lodgeFor(project, coreSettings(settings), actor)` with `settings` = `projects.settings(project)` and the caller's actor (below), each optional argument in its options object:
  `search` (`query` `""`, `filters` with `kind`, `scope`, `status` `"current"`, `area`, and `decidedBy`, `limit` 20, a whole number from 1); `show` (`ref`, `reasoning` false, `provenance` false); `waiting` (`waitingAll`); `timeline` (`limit` 50); `spec` (`area` null); `problems`; `check` (`gate` false, passed positionally, as plan 2's `check(gate)` takes it); `draft` (`ref`); `mint` (`prefix` `"d"` or `"s"`); `add` (`drafts` and `attachments` as lists of `[name, text]`, `importing` false, `dryRun` false); `ask` (`ref`, `raises` `"doubt"` or `"question"`, `by`, `text`, `where` null, `when` null); `reply` and `close` (`thread`, `by`, `text`, `where`, `when`; `close`'s `text` null); `threads`; `thread` (`ref`); and `behind-area` (`name`).
  A tuple result (`waitingAll`, `spec`, `check`, `problems`) is a JSON array.
  `add`, `ask`, `reply`, and `close` whose outcome is `AddOutcome.CHECK_FAILED` answer 422 with `{"error": {"kind": "check-failed", "message": "the check failed"}, "result": <the whole result>}`, so the command prints what lodge 0.2 prints (`src/lodge/cli/output.py`, `added_lines`).
- `project-create` (`settings`, the table the command read): on a server not set up (`accounts.setup()` is `null`) it is `usage` with `the server is not set up; run lodge server setup`; a key of `settings` other than `length` and `import` is `usage` with `settings: unknown section [<name>]` for a table and `settings: unknown key <name>` otherwise, the words of `src/lodge/core/settings.py:30-35`, since the server keeps only the core's tables; `parseCoreSettings(settings)` refusing is `usage` with `settings: <its message>`; a name `projects.names()` already holds is `usage` with `lodge is already initialised: project <name> exists`; then `projects.create(project, owner, settings)`, the owner the person the server is set up for (`accounts.setup()`), whose name check (d-wx7d0f) refusing is `usage` with its message, and whose `Conflict` from a create racing this one is `conflict`; it answers `{"project": <name>}` (d-y0ppty).
- A record operation on a project whose `projects.settings` is `null` is `no-project` with `no project named <name>` (d-3ywdhq); the command prints lodge 0.2's sentence for it.
- A request's actor is `agent(token.role)` for an agent token and, from Task 6, `person(<the person the server is set up for>)` for a session (d-vwsnz5); `app` decides from it what is held and who may approve (d-znagqe).
- Agent requests (`auth.ts`, d-kt4jkq): `Authorization: Bearer <secret>`; `hashSecret(secret)` through `accounts.tokenFor`; an unknown or revoked token is `unauthorised` (`the agent token is not known or was revoked`); a request with neither a token nor (from Task 6) a session is `unauthorised` (`sign in, or send an agent token`); a token used for another project is `forbidden` (`this agent token is for project <name>`); a token may call `project-create` for its own project's name only.
- `issueToken` makes the secret `lodge_` and the base64url of 32 bytes from `random`, the ID `tokenId(random(6))`, `t-` and six characters of `#core`'s ID alphabet (`0123456789abcdefghjkmnpqrstvwxyz`, each byte modulo 32, as `mintId` of `ts/src/core/ids.ts` spells one, whose prefix stays `d`, `s`, or `q`), stores the token (with its `role`, `issued` = `stampOf(clock.now())`) with `hashSecret(secret)`, and returns both; only the answer that issues a token holds its secret (Task 6's `token-issue`).
- `world.ts` builds a handler over `openDatabase(":memory:")`, `SqliteProjects`, and `SqliteAccounts`, with plan 2's `FixedClock` at `2026-10-29T09:30:00+01:00`, which `await clock.sleep(seconds)` moves on, `CountingIds`, entropy from a counter, the server set up for `https://lodge.test` and the person `ada`, the project `work` created with `ada` as owner, and an agent token for `work` made with `issueToken`, and `log` collecting into an array the tests read; `lodgeFor` is `lodgesOver(projects, clock, ids)`, which `main` uses too (Task 8), so the tests and the program build `Lodge` alike.

- [ ] **Step 1: Write the failing tests.**
  - `handler.test.ts`: `post_only`; `json_only`; `body_must_be_json`; `body_must_be_an_object`; `unknown_operation_is_not_found`; `other_paths_are_not_found`; `every_answer_carries_the_version_and_no_store` (a success, a usage error, and a 404 alike); `unexpected_error_is_internal_without_detail` (a `lodgeFor` that throws a `TypeError`: 500, the fixed message, and the error's message in the world's log, never in the answer).
  - `wire.test.ts`: `plain_values_pass`; `maps_and_sets_are_tagged_in_order`; `nested_values_are_encoded`; `undefined_properties_are_left_out`; `unsupported_values_throw` (`test.each` over a bigint, a function, `NaN`, and an object with a key `$map`).
  - `operations.test.ts`, through `handler`: `each_operation_reaches_lodge` (`test.each` over every record operation with a fake `Lodge` that records its call: the arguments arrive as lodge 0.2's command passes them, defaults filled); `arguments_are_checked` (`test.each` over a wrong type per field kind and an unknown field: `usage` with the sentence); `app_errors_map_to_kinds` (a fake `Lodge` throwing `NotFound`, `Conflict`, `StaleList`, `Forbidden`, and `LodgeError`: 404, 409, 409, 403, and 400 with the message); `token_role_is_the_actor` (a token issued with the role `builder` reaches `lodgeFor` as `agent("builder")`, one without as `agent()`); `failed_check_answers_422_with_the_result` (a real `add` of an entry without its decision, as `tests/e2e/test_add_failing_check_exits_1.py` drafts it); `unknown_project_is_no_project`; `project_create_records_the_settings` (then `search` on it answers 200); `project_create_checks_the_settings` (`{"length": {"title_chars": 0}}`: `usage`, `settings: length.title_chars must be a positive whole number`; `{"store": {"mode": "tree"}}`: `usage`, `settings: unknown section [store]`, and no project created); `project_create_twice_is_already_initialised`; `project_name_is_checked`; `project_create_makes_the_person_owner` (`projects.members` gives `ada` as owner); `project_create_before_setup_is_usage`; `agents_relay_is_held` (first an `add` through the token of the three drafts of `tests/e2e/support.py`'s `seed`, `decided_by: coordinator`, which creates an entry in the area `storage`; then an `ask` about that entry with `by: "ada"`, `where: "chat"`, and `when: "2026-10-29 09:00"` through the token answers 200 with `outcome` `held for approval`, `awaits` `ada`, and a `held` number, and `threads` lists nothing; d-2v8vtk).
  - `bearer.test.ts`: `no_credentials_is_unauthorised`; `unknown_token_is_unauthorised`; `revoked_token_is_unauthorised`; `token_reaches_only_its_project`; `token_may_create_its_own_project_only`; `issued_token_is_stored_as_its_hash` (the `Accounts` calls, recorded by a wrapper, never hold the secret); `token_id_is_spelled_as_an_id` (`tokenId` of six bytes `0, 31, 32, 33, 255, 10` gives `t-0z01za`).
- [ ] **Step 2: Run** `cd ts && bun test tests/api`; expected: FAIL.
- [ ] **Step 3: Implement**; add `#api` to `package.json`'s `imports`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 6: Sign-in, the person's operations, and setting up the server

**Files:**
- Create: `ts/src/api/passkeys.ts`, `ts/src/api/session.ts`, `ts/src/api/person.ts`, `ts/src/api/setup.ts`
- Modify: `ts/src/api/auth.ts`, `ts/src/api/http.ts`, `ts/src/api/operations.ts`, `ts/src/api/index.ts`, `ts/knip.json` (`@simplewebauthn/server` leaves `ignoreDependencies`)
- Test: `ts/tests/api/authenticator.ts` (helper), `ts/tests/api/passkeys.test.ts`, `ts/tests/api/session.test.ts`, `ts/tests/api/person.test.ts`, `ts/tests/api/setup.test.ts` (new)

**Interfaces:**
- Consumes: Task 5; plan 1's `#core` (`parseDraft`, `recordFromDraft`); @simplewebauthn/server 14.0.3 (`generateRegistrationOptions`, `verifyRegistrationResponse`, `generateAuthenticationOptions`, `verifyAuthenticationResponse`); plan 2's `Lodge.held()`, `approve(seq)`, and `decline(seq, reason)` (d-znagqe), `Held`, and `AddOutcome.HELD`.
- Produces, through `#api`:
  ```ts
  export interface ServerParts { readonly options: ApiOptions }           // what main opens for a data file
  export interface ServerIo {
    readonly out: (text: string) => void;
    readonly err: (text: string) => void;
    readonly open: (data: string) => Promise<ServerParts>;
    readonly listen: (fetch: (request: Request) => Promise<Response>, host: string, port: number) => Promise<void>;   // resolves when serving stops
  }
  export function serverCommand(argv: readonly string[], io: ServerIo): Promise<number>
  export function issueSetupCode(options: ApiOptions): Promise<string>     // the code in clear, once
  ```
- The ceremonies (`passkeys.ts`, d-yayhct, d-rn4qzq), each a public operation (no token, no session needed) unless named:
  - `register-options` (`setupCode`, or none for a signed-in person): with a setup code, the code must pass `accounts.setupCodeValid`, which spends nothing; registration options with the relying party ID the origin's host, the name `lodge`, the person's name, the user ID the first 16 bytes of SHA-256 of the UTF-8 of `<origin> <person>`, so every passkey of the person carries one user handle (correctness review M-4), attestation `none`, `residentKey: "preferred"`, `userVerification: "required"`, and the person's passkeys as `excludeCredentials`.
  - `register` (`setupCode` or a session, `response`): verified with `expectedChallenge` a function that accepts only a challenge this server issued for registration less than 5 minutes ago and spends it, `expectedOrigin` and `expectedRPID` the server's, and `requireUserVerification: true`; then the setup code is spent (`accounts.spendSetupCode`, false being `unauthorised`); the passkey is added; a session starts as for `sign-in`.
  - `sign-in-options`: authentication options with the person's passkeys as `allowCredentials` and `userVerification: "required"`.
  - `sign-in` (`response`): the passkey found by `response.id` (none is `unauthorised`); verified as `register` is, with the stored counter, which @simplewebauthn/server refuses to see go back unless both are 0; `accounts.usePasskey` with the new counter; a session starts.
  - `sign-out` (a session): the session ends and the cookie is cleared.
  - `me`: `{"setUp": <a passkey exists>, "signedIn": <the request's session is live>, "person": <the name, when signed in>}`.
  - A refused ceremony is `unauthorised` with `the passkey was not accepted`, or `the setup code is wrong, spent, or expired`; the library's message goes to `options.log` only.
  - Challenges live in the handler's memory (d-rn4qzq), each spent on its first use and dead after 5 minutes by `options.clock`.
- The session (`session.ts`): 32 bytes from `random` in base64url, stored as `hashSecret` with its expiry 30 days on (d-rn4qzq), set as `lodge_session=<value>; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=2592000`; cleared with `Max-Age=0`.
  A request with `Authorization` is an agent's whatever cookie it carries; one with only the cookie is the person's when the session is live (otherwise `unauthorised`, `sign in again`) and its `Origin` header equals the server's origin (otherwise `forbidden`, `the request does not come from this server's page`).
- The person's operations (`person.ts`, d-kt4jkq), each `forbidden` (`only the signed-in person may <operation>`) for an agent token:
  `token-issue` (`project`, `label`, `role` null: the answer `{"token": <AgentToken>, "secret": <secret>}` from `issueToken`); `token-revoke` (`id`; unknown or revoked is `not-found`); `tokens` (the list, never a secret or a hash); `projects` (`projects.names()`); `confirm` (`project`, `ids`, `words`, `area` null), which is `Lodge.confirm(ids, words, { area })` and, like lodge 0.2's viewer, the person's own words; `held` (`project`), the open holds of `Lodge.held()` whose `person` is the signed-in person, oldest first, each with its `seq`, `at`, `by`, and `kind`: a held message (`kind` `"message"`) as `{seq, at, by, kind, operation, ref, raises, text, where, when}`, `ref` the record or thread it is about; a held add (`kind` `"add"`) as `{seq, at, by, kind, drafts}`, where a decision's draft is `{name, kind, title, statement, quote}` read through `#core`'s `parseDraft` and then `recordFromDraft(draft, id, held.at, area)`, which types the header, `id` being the draft's own `id` when its header holds a string and otherwise a placeholder of its kind (`d-000000` for a decision, `s-000000` for an entry; an area takes none), and `area`, for an entry, the draft's own `area` when its header holds a string and otherwise the placeholder `held`, since an edit draft from `lodge draft` has no `area` and lodge 0.2 takes an existing entry's area from the tree (`src/lodge/core/apply.py:137`; plan recheck 2, N-7), `null` for a decision or an area, since a decision needs an `id` and a `date` and an entry's own `id` must match (`ts/src/core/headers.ts:56,61`, `withId` of `ts/src/core/drafts.ts`; plan recheck 2, N-5, run at `origin/server-core` 7d5ecbc); the placeholder ID, area, and date never reach the answer, `statement` being the decision's statement without its reasoning and `quote` its `{text, where, when}` or `null`; an entry's draft is `{name, kind, title, statement}` and an area's `{name, kind, title, intro}` from the same two calls, `statement` the `SpecEntry`'s and `intro` the `Area`'s (`ts/src/core/model.ts`); and a draft for which either call gives a `Problem` is `{name, problem: <its message>, text: <the draft's text>}`, so the page shows what the approval records and never parses YAML itself (correctness review I-7); `approve` (`project`, `seq`), which is `Lodge.approve(seq)` and answers its `Approved` (`{kind: "add", added}` or `{kind: "message", written}`), a `CHECK_FAILED` outcome of either answering 422 with the `Approved` as `add` does; and `decline` (`project`, `seq`, `reason`), which is `Lodge.decline(seq, reason)` and answers `null`.
- `serverCommand` (`setup.ts`, d-vfyex3, d-rn4qzq):
  - `setup --data PATH --origin URL --person NAME`: the origin is `https://<host>` or `http://localhost:<port>`, with no path, since WebAuthn refuses an IP address as the relying party ID (correctness review I-6; the command's `server.url` of Task 3 keeps all three loopback forms, since it makes no passkey); the person's name matches `^[a-z][a-z0-9-]{0,31}$` (d-wx7d0f), otherwise `lodge: the person's name must be lower-case letters, digits, and hyphens, starting with a letter` and exit 2; on a server not set up it records origin and person (`accounts.setUp`); on one set up with another origin or person it prints `lodge: the server is set up for <origin> and <person>` and exits 2; with a passkey registered it prints `lodge: a passkey is registered; sign in on <origin> to add another` and exits 2; otherwise it issues a setup code and prints two lines:
    ```
    setup code: <code>
    it works once, for 15 minutes: open <origin>, enter it, and register a passkey
    ```
  - `issueSetupCode`: 20 characters of Crockford's base32 from 100 random bits, shown in four groups of five joined by `-`; stored as `hashSecret` of the code in lower case without hyphens, with `expires` 15 minutes on (d-yayhct); the page sends the code as typed, and the server lowers it and drops hyphens and spaces before hashing.
  - `serve --data PATH [--host HOST] [--port PORT]`: the host defaults to `127.0.0.1` and the port to 8787 (lodge 0.2's `DEFAULT_PORT`, `src/lodge/cli/parser.py:11`); a server not set up prints `lodge: the server is not set up; run lodge server setup` and exits 2; otherwise it prints `serving <origin> on http://<host>:<port>` and awaits `io.listen` with `handler(parts.options)`.
  - Usage errors print a usage line and exit 2, as the command's grammar does; `--help` prints the two subcommands.
- `authenticator.ts` carries `SoftAuthenticator` of plan 1's probe 2 (`docs/superpowers/plans/done/2026-11-02-lodge-server-core/probes/tests/passkey.test.ts`) with every buffer built as `new Uint8Array(new ArrayBuffer(n))`, so strict `tsc` accepts it (plan 1, probe 20), and with options to clear the user-verification flag, set the counter, and sign with another origin.

- [ ] **Step 1: Write the failing tests.**
  - `passkeys.test.ts`: `register_with_the_setup_code_then_sign_in` (the counter reads 1 after sign-in); `setup_code_is_spent_by_registration`; `setup_code_lasts_15_minutes` (14 minutes 59 seconds after it is issued it registers, 15 minutes after it does not); `wrong_setup_code_is_refused`; `wrong_challenge_is_refused`; `challenge_is_spent_on_use` (the same response sent twice); `challenge_lasts_5_minutes` (each expiry test moving the clock with `FixedClock.sleep`); `register_options_keep_one_user_id` (two `register-options` answers give the same `user.id`); `counter_going_back_is_refused`; `user_verification_is_required` (flags without UV, at registration and at sign-in); `other_origin_is_refused`; `signed_in_person_adds_a_passkey` (no setup code; the first passkey excluded); `refusal_does_not_echo_the_library` (the answer holds only the fixed sentence).
  - `session.test.ts`: `cookie_is_http_only_secure_and_strict`; `session_lasts_30_days` (live one second before, refused at 30 days); `sign_out_ends_the_session`; `cookie_request_needs_this_servers_origin` (none and another: `forbidden`); `authorization_makes_an_agent_request` (a token and a cookie together: treated as the token's); `session_is_stored_as_its_hash`; `me_says_who_is_signed_in`.
  - `person.test.ts`: `token_issue_shows_the_secret_once` (the `tokens` answer holds neither the secret nor its hash); `issued_token_works_for_its_project`; `revoked_token_stops_working`; `person_operations_refuse_an_agent_token` (`test.each` over `token-issue`, `token-revoke`, `tokens`, `projects`, `confirm`, `held`, `approve`, and `decline`); `person_may_call_record_operations`; `confirm_writes_the_persons_confirmation`; `approve_makes_the_held_decision_current` (an agent's `add` of a decision `decided_by: ada` answers `held for approval` with `held` its number, then `approve` with that number answers `kind` `add` with `published` and the minted ID, then `show` gives it current); `held_lists_a_relayed_message` (an agent's `reply` by `ada` with `where` and `when` to a thread by `reviewer`: `held` lists it with `kind` `message`, `operation` `reply`, its `ref`, `text`, `where`, and `when`, beside a held add, oldest first); `approve_publishes_the_relayed_message` (`approve` answers `kind` `message` with `published`, `thread` shows `ada`'s message last with its `where` and `when`, and `held` is empty); `decline_drops_the_relayed_message` (`decline` answers `null`, the thread's last message stays `reviewer`'s, `held` is empty, and `approve` of it is `not-found` with `nothing is held under number <seq>`); `held_lists_what_waits_for_the_person`; `decline_closes_the_hold` (then `held` is empty and `approve` of it is `not-found`); `approval_failing_the_check_answers_422` (a hand edit of the entry through `projects.storeFor("work", agent("hand"))` between the hold and the approval makes the approval fail check 6, as in plan 2's `approval_runs_the_check_again` of its Task 12b, and the hold stays open); `held_shows_the_drafts_as_core_reads_them` (a hold of `seed`'s three drafts with `decided_by: ada` and her quote, the decision's draft without an `id` and the entry's with its own: no draft answers a `problem`, the decision answers its `title`, the `statement` `Transcripts are kept.` without its reasoning, and the `quote` `{text: "Keep them.", where: "chat", when: "2026-10-29 10:00"}`, and the entry answers its `title` `Transcripts are kept` and its `statement` `Held.`, and the area its `title` `Storage` and its `intro` `How data is kept.`; a second hold whose entry draft is `lodge draft` of that entry once current (with `base`, no `area`) answers it with its `title` `Transcripts are kept` and its `statement` `Held.` and no `problem`; then a hold holding an unparsable draft answers its `problem` and raw `text`).
  - `setup.test.ts`, `serverCommand` with an `open` over the store on `:memory:` and a `listen` that records its arguments: `setup_prints_a_code`; `setup_again_before_a_passkey_gives_a_new_code` (the old one refused); `setup_after_a_passkey_is_refused`; `setup_fixes_origin_and_person`; `setup_refuses_a_bad_origin` (`test.each` over `http://lodge.example.org`, `https://lodge.example.org/path`, `ftp://x`, `http://127.0.0.1:8787`, and `http://[::1]:8787`); `setup_refuses_a_bad_person` (`Ada` and `1ada`); `serve_needs_setup`; `serve_listens_where_told` (defaults, then `--host 0.0.0.0 --port 9000`); `server_usage_errors_exit_2`.
- [ ] **Step 2: Run** `cd ts && bun test tests/api`; expected: the new tests FAIL.
- [ ] **Step 3: Implement**; take `@simplewebauthn/server` out of `ts/knip.json`'s `ignoreDependencies`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 7a: The command against the server, with the reading tests

**Files:**
- Create: `ts/src/cli/client.ts`, `ts/src/cli/wire.ts`, `ts/src/cli/output.ts`, `ts/src/cli/thread-output.ts`, `ts/src/cli/commands.ts`, `ts/src/cli/threads.ts`, `ts/src/cli/guide.md`, `ts/src/cli/text.d.ts`
- Modify: `ts/src/cli/index.ts`, `ts/tests/parity.json`, `ts/tests/parity.test.ts` and `ts/tests/parity-names.ts` (a `changed` row's `dropped` list), `ts/tests/app/thread-fix-paths.test.ts` (plan 2's two `test.todo`s become tests, d-rp74dr), `ts/knip.json` (`tests/e2e/support.ts` into `entry`, d-tha8st)
- Port: `src/lodge/cli/commands.py`, `output.py`, `thread_output.py`, the running half of `threads.py`, and `guide.md`
- Test: `ts/tests/e2e/server.ts` (helper, new), `ts/tests/e2e/project.ts`, `ts/tests/e2e/support.ts`; carried: `before-init-one-sentence-exit-2`, `outside-repository-one-sentence-exit-2`, `malformed-settings-one-sentence-exit-2`, `id`, `init`, `help-lists-every-command`, `guide`, `search`, `search-limit`, `search-shows-unparsable-file`, `show-ambiguous-code-one-line`, `show-levels`, `spec`, `waiting`, `check-and-gate`, and `broken-agent-decision-warns-above-show`, each `ts/tests/e2e/<name>.test.ts`; new: `ts/tests/cli/client.test.ts`, `ts/tests/cli/wire.test.ts`

**Interfaces:**
- Consumes: Tasks 2, 3, 5, and 6; plan 1's `#core` (`formatLevel1`, `formatLevel3`, `WORD_CLASS`); `app`'s result types (with `AddOutcome.HELD`, `Added.awaits` and `held`, `Written.awaits` and `held`, and `Approved`), decoded from the wire; plan 2's `#store` (`openDatabase`, `SqliteProjects`) and `#app` (`agent`) for the test server.
- Produces, through `#cli`:
  ```ts
  export interface Io {
    readonly cwd: string;
    readonly env: Readonly<Record<string, string | undefined>>;
    readonly fetch: (request: Request) => Promise<Response>;
    readonly out: (text: string) => void;
    readonly err: (text: string) => void;
    readonly version: string;
  }
  export function run(argv: readonly string[], io: Io): Promise<number>
  export function fromWire(value: unknown): unknown
  export type Call = (operation: string, body: Readonly<Record<string, unknown>>) => Promise<unknown>;   // the decoded result, or a CliError
  export function runThread(command: ThreadCommand, call: Call, out: (text: string) => void): Promise<number>   // threads.py's run_thread
  ```
  `run` builds the `Call` of `client.ts` for the server and the token and hands it to `runThread` for `ask`, `reply`, `close`, `threads`, and `thread`, so `thread-fix-paths.test.ts` can run `runThread` over a `Call` the test answers in process.
- `run` is `src/lodge/cli/commands.py`'s `run` and `src/lodge/main.py`'s error handling: it parses (Task 2), prints an `Exit` as it is, prints the guide for `guide` without reading any setting, and otherwise finds the root and reads the settings (Task 3), takes the server and the token, and calls the operation; a `CliError` prints `lodge: <message>` on `err` and returns its exit code.
  `add` reads its drafts and attachments before the settings, as lodge 0.2 reads them before it builds `Lodge` (`src/lodge/cli/commands.py:71-73`); `ask`, `reply`, and `close` read their message file after, as `run_thread` does (`src/lodge/cli/threads.py:95-102`).
- What each command sends and prints, every printed line as lodge 0.2 prints it:
  `init` sends `project-create` with the settings' `core` table and prints `created project <project> on <url>` and `next: lodge guide`; `id` sends `mint`; `search`, `show`, `draft`, `check`, `spec`, `waiting`, `threads`, `thread`, `ask`, `reply`, and `close` as `commands.py` and `threads.py` run them; `add` sends the drafts as `[name as given, text]` and the attachments as `[base name, exact text]` (`src/lodge/cli/commands.py:115-122`).
- `client.ts` (d-3ywdhq, d-1zmfdr): a `Request` to `<url>/api/v1/<operation>` with `Authorization: Bearer <token>` when `tokenOf` gives one and no `Authorization` when it gives `null`, `Content-Type: application/json`, and the body `{"project": …, …}`; `io.fetch` throwing is `CliError("cannot reach <url>: <message>")`; an answer without `Lodge-Version` is `CliError("<url> does not answer as a lodge server")`, and one whose version differs is `CliError("the server at <url> runs lodge <theirs> and this command is lodge <ours>; use the same version")`; an answer that is not JSON is `CliError("<url> answered something other than JSON")`.
  Then by kind: 200 gives `fromWire(result)`; `check-failed` gives the decoded result to the command, which prints its lines and exits 1 (`src/lodge/cli/commands.py:104-105`, `threads.py:104-106`); `conflict` is `CliError(message, 1)`; `no-project` is `CliError("lodge has no data in this repository yet; run \`lodge init\`")`, lodge 0.2's sentence; `unauthorised` is `CliError("<message>; an agent token goes in LODGE_TOKEN, or in a cloud environment's network secret for this server")`; every other kind is `CliError(message)`.
- A thread message held for a person (`Written` with `outcome` `HELD`, d-2v8vtk): `runThread` prints `held for approval by <awaits> as hold <held>; nothing is current until they approve it` and returns 0.
- An add held for a person (`AddOutcome.HELD`, d-znagqe), which lodge 0.2 has no line for: `added_lines` marks the IDs `(provisional)` as for a dry run and ends with `held for approval by <awaits> as hold <held>; nothing is current until they approve it`, exit 0; a dry run whose `awaits` is set prints `note: <awaits> approves this add before it is current` before `dry run: nothing published`.
- `fromWire` undoes `toWire` of Task 5: `{"$map": …}` becomes a `Map`, `{"$set": …}` a `Set`, recursively; the command treats its value as the `app` result the operation returns.
- `output.ts` and `thread-output.ts` port `output.py` and `thread_output.py` function by function, with the constants `NO_MATCHES`, `NOTHING_RECORDED`, and `DECISION_DRAFT_NOTE`; `check_lines`'s `p not in already_shown` compares every field of the two problems; `_marked`'s `\b` follows plan 1's Global Constraints (`WORD_CLASS` lookarounds), and its ID is escaped for the pattern.
- `guide.md` is `src/lodge/cli/guide.md` with these lines changed, so that it describes the server (the parity row of `tests/e2e/test_guide.py`), still at most 60 lines:
  - after line 7, a new line: ``The command talks to the lodge server named in `[server]` of `.lodge.toml`, with the agent token the author issues on the server's page in `LODGE_TOKEN`, or added by a cloud environment's network secret; `[length]` and `[import]` reach the server once, with `lodge init`.``
  - line 19 becomes ``A `problem:` line names a record file lodge cannot read, and a record flagged `fails check` fails a check, such as one imported broken from lodge 0.2; tell the author.``
  - line 20, on the rewritten lodge branch, goes.
  - line 29 becomes ``2. Write drafts as files, Markdown with a YAML header; the body is the statement, and `## Reasoning` starts the why.``
  - line 33 becomes ``Then `add` sends them to the server, which checks them and makes them current at once; nothing is staged or committed.``
  - line 34 becomes ``The check runs on the server at every write; a dry run marks new IDs `(provisional)`: the real add mints new ones, so never write them into another draft.``
  - line 24 gains a clause after `write threads`: ``; a message `--by author` you send waits for the author's approval on the server's page`` (d-2v8vtk); line 26 stays as lodge 0.2 has it, which the carried `guide_says_waiting_first` asserts verbatim (`tests/e2e/test_guide.py:58`).
  - line 50 says `at the server's clock` where it says `at this machine's clock`.
  - line 55 becomes `` `decided_by: author` is for the author's decisions only, with `quote: {text, where, when}`; such an add waits for the author's approval on the server's page and prints `held for approval`. `` (d-znagqe; correctness review M-7), and `guide_is_short_and_covers_the_write_path` looks for `held for approval` as well as the new line of line 33.
- `guide.md` is a text import (d-5kskm3): `import guide from "./guide.md" with { type: "text" }`, typed by `declare module "*/guide.md" { const text: string; export default text; }` in `text.d.ts`.
- The parity check (`parity.test.ts`, `parity-names.ts`): a row may hold `dropped`, a list of Python test names, allowed only on a `changed` row, each of its names a test of the Python file (`dropped_names_are_python_tests_of_a_changed_row`).
  Before widening, this task sets `ts/tests/parity.json`'s `tests/test_wheel.py` row, which plan 1 wrote as `changed` with `plan` 3 and the file `ts/tests/e2e/binary.test.ts` that only Task 8 creates, back to `planned` with `plan` 3 and the same `ts` and `why`, so that the widened tests do not read a file two tasks away (plan recheck 1, N-1); Task 8's last step writes it `changed` again with its `dropped`.
  Plan 2's Task 9 has `ported_files_exist`, `ported_files_keep_every_python_test_name`, and `ported_files_hold_no_todo` take a `changed` row with `plan` 2; this task widens the same three to a `changed` row with `plan` 2 or 3, the name check leaving out the row's `dropped`, so that the `changed` rows of plans 1 and 4 (`tests/test_structure.py`, `tests/test_structure_io.py`, and plan 4's hook rows, some of whose files do not exist yet) are not checked by name (correctness review I-3).
- The test server (`server.ts`, d-bwb1tt):
  ```ts
  export interface TestClock extends Clock { minutes(): void; standStill(): void; readonly slept: number[] }
  export interface TestServer {
    readonly fetch: (request: Request) => Promise<Response>;
    readonly origin: string;                                   // "https://lodge.test"
    readonly token: string;                                    // an agent token for project "work"
    readonly clock: TestClock;
    approve(project: string, seq: number): Promise<readonly string[]>;   // as the signed-in person; throws unless the add's or message's outcome is published; its IDs
    handEdit(project: string, files: Readonly<Record<string, string>>): Promise<void>;       // one publish of every file
    stored(project: string, path: string): Promise<string | null>;
    paths(project: string): Promise<readonly string[]>;
  }
  export function testServer(): Promise<TestServer>
  ```
  It opens `openDatabase(":memory:")` with `SqliteProjects` and `SqliteAccounts`, wires `handler` with `lodgeFor` as Task 5's `world.ts` does, sets the server up for `https://lodge.test` and the person `author`, so lodge 0.2's words for the author stay (d-vwsnz5), registers a passkey with `issueSetupCode` and the `SoftAuthenticator` of Task 6 to hold a session, and issues the token for `work` through `token-issue`.
  `clock` reads as `tests/e2e/conftest.py`'s `MinuteClock` (each reading a minute after the last, from `2026-10-29T09:30:00+01:00`) until `standStill()`, then as `StuckClock` (the same `Now`, `epochMs` that of `2026-10-29T09:30:00.250+01:00` and `offsetMinutes` 60, until `sleep` moves it and records the seconds in `slept`).
  `handEdit` takes `projects.storeFor(project, agent("hand"))`, reads `trees()`, and calls `publish(current, new Map(Object.entries(files)), "hand edit")`, which runs no check, as a hand edit of a file under `lodge/` did in lodge 0.2, and throws unless it answers `published`; the store refuses a rewritten decision file (d-j28rp0), so no test rewrites one (d-4qv0xb).
  `stored` and `paths` read the current tree of the same store, `stored` reading a path under `lodge/attachments/` from `attachmentTexts()`, since the tree lists attachments without their text.
- `project.ts` (from `conftest.py`): `Result` (`code`, `out`, `err`); `Project` with `root` (a temporary folder `work` holding a folder `.git` and a `.lodge.toml` of `[server]` with `url` and `project = "work"`), `url` (the URL written there, `https://lodge.test` in process), `run(...argv)` and `runIn(cwd, ...argv)` (both async), `configure(text)` (the `[server]` table, then `text`), `draft(name, text)` (a file in `drafts` beside `root`; its path), `stored(path)`, `paths()`, `handEdit(files)`, `approve(seq)` (the published IDs), and `standStill()` (the server's clock stands still and is returned, as the `stuck_clock` fixture); `project({ unreachable = false } = {})` makes one with its own `testServer()`, and with `unreachable` the command cannot reach it.
  Every expected line that names the server's URL reads `project.url`, never a literal.
  `run` calls `run` of `#cli` with `io.fetch` the server's `fetch` (with `unreachable`, a `fetch` that throws `TypeError("Unable to connect")`), `io.env` holding only `LODGE_TOKEN`, and `io.version` read from `ts/package.json`.
  With `LODGE_E2E_BINARY` set to a binary's path, `project()` instead serves the server's `fetch` with `Bun.serve` on `127.0.0.1` port 0 (with `unreachable`, it serves on port 0, notes the port, and stops, so nothing listens there), writes that `http` URL into `.lodge.toml` and `url`, and `run` runs the binary with `Bun.spawn` in the folder with `PATH` and `LODGE_TOKEN` only, awaiting it (probe 5); this mode is S1's, no test of the gate sets it, and every carried test runs in both modes.
- `support.ts` ports `support.py`; `seed` with `decided_by="author"` asserts the add's exit 0, nothing on `err`, and its last line matching `^held for approval by author as hold (\d+); nothing is current until they approve it$`, approves that hold (`approve` throwing unless `published`), and takes the decision's ID from the approval's answer (the parity section's last paragraph); with an agent role (`coordinator`, the default) nothing is held.
- `thread-fix-paths.test.ts`: `orphaned_thread_outputs` and `run_thread_outcomes` assert what the Python tests assert, with `runThread` over a `Call` the test builds: over plan 2's `wired(project())` for the first, answering `threads` and `thread` from its `Lodge` through `toWire` and `fromWire`, and for the second answering `ask` with the fixed `Written` (`test.each` over `PUBLISHED` 0 and `CHECK_FAILED` 1).
- Each carried test asserts what its Python test asserts, with d-bwb1tt's three substitutions and the changes its parity row names (d-4qv0xb):
  - `check-and-gate.test.ts`'s `check_and_gate`: `check` prints `ok\n` and exits 0 on the seeded store, nothing on `err`; then `handEdit` writes `lodge/decisions/<id>-unquoted.md`, `<id>` from `lodge id d`, holding `id: <id>`, `kind: decision`, `title: Unquoted`, `scope: product`, `decided_by: author`, `date: 2026-10-29T12:00:00+01:00`, and the body `Unquoted statement.`; `check` exits 1 with nothing on `err` and its output starts `check 3: ` and holds `<id>`; `show <id>` holds `fails check`; `check --gate` exits 0, nothing on `err`, its first line `ok` and its second starting `note: already published, check 3: lodge/decisions/<id>-unquoted.md: <id>: ` (probe 8);
  - `broken-agent-decision-warns-above-show.test.ts`: after `seed` with the quote and `decided_by="author"`, one `handEdit` writes `lodge/decisions/<id>-keep-them-whole.md`, `<id>` from `lodge id d`, as `---\ntitle: [unclosed\n---\n`, and the entry's file (its path from `paths()`) with `Held.` made `Held, whole.`; then `show` of the entry is asserted line for line as the Python test asserts it, the `problem:` line naming that file;
  - `waiting.test.ts`'s `waiting_groups_threads`: the command's `ask … --by author --where chat --when "2026-10-31 12:00"` exits 0 with nothing on `err` and its last line matching `^held for approval by author as hold (\d+); nothing is current until they approve it$`; `approve` of that hold gives the thread's ID, which stands for `author.out.split()[-1]`, and the rest is asserted as the Python test asserts it (d-2v8vtk); `init.test.ts`'s three tests are `init` (the two lines above, nothing on `err`, and `paths("work")` empty), `init_twice_is_refused` (`lodge: lodge is already initialised: project work exists`, exit 2), and `init_when_the_server_cannot_be_reached` (`project({ unreachable: true })`: `err` starting `lodge: cannot reach <project.url>: `, one line, nothing on `out`, exit 2); `init`'s first line is `created project work on <project.url>`; `malformed-settings-one-sentence-exit-2.test.ts` keeps the three Python texts, the third (`[store]` with `mode = "tree"`) expecting the start `lodge: .lodge.toml: unknown section [store]`, and adds a fourth, `[length]` with `title_chars = 80.0`, expecting `lodge: .lodge.toml: length.title_chars must be a positive whole number` (d-dfkqec).

- [ ] **Step 1: Write the failing tests:** the carried files above by name with `server.ts`, `project.ts`, and `support.ts`; `client.test.ts` (`version_must_match`, `missing_version_is_not_lodge`, `not_json_is_one_sentence`, `unreachable_server_is_one_sentence`, `kinds_map_to_exit_codes` (`test.each` over `usage` 2, `unauthorised` 2, `forbidden` 2, `not-found` 2, `conflict` 1, `internal` 2, and `check-failed` 1 with the result printed), `no_project_is_lodge_0_2_s_sentence`, `token_travels_only_in_authorization`, `no_token_sends_no_authorization` (with `LODGE_TOKEN` unset the request has no `Authorization`, and an `unauthorised` answer prints the sentence naming both places a token comes from)); `wire.test.ts` (`round_trip` through `toWire` of `#api` and `fromWire` of `#cli` for a value with nested maps and sets, arrays, nulls, and text with an astral character); the parity tests of `dropped`.
- [ ] **Step 2: Run** `cd ts && bun test tests/e2e tests/cli tests/parity.test.ts`; expected: the new tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green; write this task's rows into `parity.json` as the parity section says; green again; the report lists each test that approves a held add, every substitution of d-bwb1tt and change of d-4qv0xb by test, and any output that differs from lodge 0.2's with its reason; it maps every function ported from `output.py`, `thread_output.py`, `commands.py`, and `threads.py` to the carried tests that assert its lines, and any function no carried test pins is seen failing against a mutation the report names, then reverted (d-zthdm7).
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 7b: The writing tests

**Files:**
- Modify: `ts/tests/parity.json`, `ts/knip.json` (`tests/e2e/support.ts` leaves `entry`, d-tha8st); Task 7a's modules only where a carried test finds them wrong
- Test: carried: `add-attach`, `add-bad-yaml-exits-2-naming-file-and-line`, `add-dry-run`, `add-failing-check-exits-1`, `add-import`, `add-new-decision-entry-area`, `add-non-string-scalar-exits-2`, `draft-then-add-edit`, `same-second`, and `threads`, each `ts/tests/e2e/<name>.test.ts`; new: `ts/tests/e2e/held.test.ts`, not carried

**Interfaces:**
- Consumes: Task 7a.
- Produces: no new name; the carried tests of the commands that write.
- These tests carry over code Task 7a wrote, so each is seen failing against a mutation of that code the report names (such as `readDraft` keeping `\r\n`, `added_lines` leaving out `(provisional)`, attachments sent under their full path, or the 422 answer printed as an error), and the mutation is reverted (d-mfayy5).
- `add-import.test.ts`'s `import_needs_the_flag_and_a_listed_source`: the `--import` add exits 0 with nothing on `err` and its last line matches `^held for approval by author as hold (\d+); nothing is current until they approve it$`; approving that hold gives the outcome `published`, and `show` of its first `d-` ID holds `imported` and `unquoted`, as the Python asserts of `staged d-…` (correctness review I-2).
- `held.test.ts` (new, d-znagqe's lines, which lodge 0.2 has none of): `held_add_marks_its_ids_provisional` (an add of `seed`'s three drafts with `decided_by: author` and the quote, its statement made 81 words of `word`, which draws the length feedback naming the decision (`feedback: <id> (provisional): the statement is 81 words; …`): every line above the last that names a minted ID gives it ` (provisional)`, at least one such line exists, and the last line is the held line); `dry_run_of_a_persons_decision_names_who_approves` (`add --dry-run` of the same drafts: exit 0, nothing on `err`, its last two lines `note: author approves this add before it is current` and `dry run: nothing published`); each is seen failing against a named mutation of `added_lines` (the note left out, the marks left out), then reverted.
- Each carried test asserts what its Python test asserts, with d-bwb1tt's three substitutions and its parity row's changes: `add-attach.test.ts`'s `attachment_lands_beside_the_decision_in_checkout_mode` reads `lodge/attachments/<decision>/run.log` from the store and finds `LOG` exactly, `\r\n` kept; `same-second.test.ts`'s carried test stands the server's clock still and finds `slept` equal to `[0.75]`; `threads.test.ts`'s `author_words_are_recorded_exactly`: the command's `ask … --by author --where chat --when "2026-10-31 12:00"` exits 0 with the held line, `approve` of that hold gives `<q>`, and then `thread <q>` through the command and `lodge/threads/<q>.md` from the store, loaded with `#core`'s `load` and `tree`, are asserted as the Python test asserts them with `Tree` (d-2v8vtk, d-4qv0xb); `author_message_needs_where_and_when_exit_2` keeps lodge 0.2's message, since the command's grammar refuses first.

- [ ] **Step 1: Write the tests:** the carried files above by name.
- [ ] **Step 2: Run** each test against its named mutation and see it fail; revert each mutation.
- [ ] **Step 3: Fix** in Task 7a's modules what a carried test finds, each fix named in the report with the test that failed before it.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green; write this task's rows into `parity.json`; green again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 8: The program and the binary

**Files:**
- Create: `ts/src/main.ts`, `ts/src/api/serve.ts`, `ts/tests/e2e/binary.test.ts`, `ts/tests/api/environment.test.ts`
- Modify: `ts/src/api/index.ts`, `ts/package.json` (a `build` script), `ts/knip.json` (`includeEntryExports`, and `src/main.ts` in `entry`), `.gitignore` (`ts/dist/`), `ts/tests/parity.json`; for the names knip then reports (d-amxk94), `ts/src/core/*.ts`, `ts/src/app/*.ts`, `ts/src/store/*.ts`, `ts/src/cli/*.ts`, `ts/src/api/*.ts`, and the test files knip names

**Interfaces:**
- Consumes: every package.
- Produces, through `#api`: `listen(fetch, host, port): Promise<void>` (`serve.ts`, `Bun.serve` with `hostname` and `port`, resolving when the server stops) and `withoutYamlLogging(env: Record<string, string | undefined>): void`, which deletes `LOG_TOKENS` and `LOG_STREAM` (d-v9mw2d).
- `src/main.ts` (d-vfyex3), the composition root:
  - first `withoutYamlLogging(process.env)`, for every run (d-v9mw2d);
  - the version from `ts/package.json` (`import pkg from "../package.json" with { type: "json" }`);
  - with `server` as the first argument, `serverCommand(rest, io)`, whose `open(data)` runs `openDatabase(data)` and builds `ApiOptions` from it (`new SqliteAccounts(database, clock)`, `new SqliteProjects(database, clock)`, `lodgesOver(projects, clock, ids)`, the real clock and entropy, `crypto.getRandomValues`, the version, and `log` writing through `process.stderr.write`), and whose `listen` is `#api`'s;
  - otherwise `run(argv, io)` of `#cli` with `process.cwd()`, `process.env`, the global `fetch`, `out` and `err` writing through `process.stdout.write` and `process.stderr.write` (d-d0vca9), and the version;
  - the exit code returned is the process's;
  - the real clock's `now()` is `{ epochMs: Date.now(), offsetMinutes: -new Date().getTimezoneOffset() }`, this machine's offset, as lodge 0.2's `datetime.now().astimezone()` (`src/lodge/main.py:29-30`), and its `sleep(seconds)` a timer of `seconds * 1000` milliseconds; both live in `main.ts`, outside `core` and `app` (d-mfskz3); entropy is 8 bytes of `crypto.getRandomValues` (`src/lodge/main.py:38`).
- `ts/package.json` gains `"build": "bun build --compile src/main.ts --outfile dist/lodge"`.
- `binary.test.ts` builds the binary once (`beforeAll`, `Bun.spawn` of `process.execPath` with `build --compile src/main.ts --outfile <temporary folder>/lodge`, awaited; `afterAll` removes that folder with `rmSync(dir, { recursive: true })`, since each binary is about 95 MB) and runs it from another temporary folder with `PATH` alone in its environment: `version` (`--version` prints `lodge <ts/package.json's version>` and a newline, exit 0; `tests/test_entry_point.py`) and `compiled_binary_runs` (`guide` exits 0, its output starting `# ` and holding `lodge add`, as `tests/test_wheel.py` asserts of the installed wheel).
- `environment.test.ts`: `yaml_logging_variables_are_cleared` (`withoutYamlLogging` on an object holding both and another variable leaves only the other); `main_clears_yaml_logging_first` (TypeScript's parser over `src/main.ts` finds `withoutYamlLogging(process.env)` as the first statement after the imports; correctness review M-8).
- d-amxk94: `ts/knip.json` gains `"includeEntryExports": true` and `src/main.ts` in `entry` (d-s2rdn2); each export knip then reports is removed, except a name a front-door test requires (`front_door_exports_every_python_name` of `#core` and of `#app`, and the additions `#app`'s `front_door_exports_nothing_else` allows) or one that plan 4's "Names consumed" table lists (`docs/superpowers/plans/2026-11-02-lodge-server-import.md` on `origin/server-import`, not in this worktree; the coordinator pastes that table, as it stands the day the brief is written, into Task 8's brief), which gets `/** @public */` in the module that defines it (probe 4); an unread export of a test file loses its `export`; the report lists the three kinds.

- [ ] **Step 1: Write the failing tests:** `binary.test.ts` and `environment.test.ts`.
- [ ] **Step 2: Run** `cd ts && bun test tests/e2e/binary.test.ts tests/api/environment.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement** `serve.ts`, `withoutYamlLogging`, and `main.ts`; add the `build` script and `ts/dist/` to `.gitignore`; turn on `includeEntryExports` and act on what knip reports.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green, knip reporting nothing; flip `tests/test_entry_point.py` to `ported` and `tests/test_wheel.py` to `changed` with its `dropped`; green again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`; then S1; commit, push; the ledger line gives S1's counts.

### Task 9: The page

**Files:**
- Create: `ts/src/api/page.html`, `ts/src/api/page.js`, `ts/src/api/page.ts`, `ts/src/api/text.d.ts`
- Modify: `ts/src/api/http.ts` (two `GET` routes, reading `PAGE` and `SCRIPT` of `page.ts`); `ts/src/api/index.ts` gains no export
- Test: `ts/tests/api/page.test.ts` (new)

**Interfaces:**
- Consumes: Task 6's operations.
- Produces: `GET /` (the page) and `GET /page.js` (its script) from `handler`; any other `GET` stays `not-found`.
- The assets are text imports (d-5kskm3, probe 3): `import bundle from "./page.html" with { type: "text" }` with `const PAGE = bundle as unknown as string`, since `bun-types` types an HTML import as `HTMLBundle`; `import SCRIPT from "./page.js" with { type: "text" }` typed by `declare module "*/page.js" { const text: string; export default text; }` in `text.d.ts`; Biome lints both files.
- Headers: the page with `Content-Type: text/html; charset=utf-8`, the script with `text/javascript; charset=utf-8`, both with `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, and `Content-Security-Policy: default-src 'none'; script-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'`.
- `page.html` (d-jtxwg3): `<html lang="en-GB">`, a title `lodge`, one `<script src="/page.js" defer>`, no inline script or style, and the sections the script fills: signing in (a setup code field and "Register a passkey", and "Sign in"), and, once signed in, "Sign out", "Add a passkey", the agent tokens (a list with "Revoke", and a form of project and label that issues one and shows its secret once), and what is held for the person's approval, per project (`held`), each by its `kind`: an add with its drafts' `title`, `statement`, `quote`, and an area's `intro`, as Task 6's `held` answers them (a draft with a `problem` as that message and its raw text), a relayed message with its operation, the record or thread it is about, its text, `where`, and `when`; each with an "Approve" button, after which it shows the IDs the approval published, and a "Decline" button that asks for a reason.
- `page.js`, plain JavaScript with no import: it calls only `/api/v1/<operation>` with `POST` and JSON (`me`, `register-options`, `register`, `sign-in-options`, `sign-in`, `sign-out`, `tokens`, `token-issue`, `token-revoke`, `projects`, `held`, `approve`, and `decline`); it turns the options' base64url fields into buffers for `navigator.credentials.create` and `get`, and the credential's buffers back into base64url for the server; it writes every text from the server with `textContent` and builds elements with `document.createElement`, never as HTML.

- [ ] **Step 1: Write the failing tests:** `page.test.ts`: `page_is_served_with_its_policy`; `script_is_served_as_javascript`; `other_paths_are_not_found`; `page_loads_only_its_script` (one `<script`, its `src` `/page.js`, no `http:` or `https:` in the page); `script_writes_no_html` (the script holds none of `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval`, or `Function(`); `script_calls_only_the_api` (every `fetch(` in the script is followed by a path beginning `/api/v1/`); `every_operation_the_script_names_exists` (each `/api/v1/<name>` in the script answers anything but `no operation named <name>`).
- [ ] **Step 2: Run** `cd ts && bun test tests/api/page.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push; after Task 8 has merged, lane D rebased onto `server-api` and its gate run again before review; then S3 with S2 inside it: build the binary, `lodge server setup` with a scratch data file, `--origin http://localhost:8787`, and a person's name, then `LOG_TOKENS=1 LOG_STREAM=1 dist/lodge server serve --data …`; in the browser register a passkey with the printed code, sign out, sign in, and issue a token for a project `trial`; in a scratch repository whose `.lodge.toml` names `http://localhost:8787` and `trial`, with `LODGE_TOKEN` set, `lodge init`, then `lodge add` of a decision drafted in the person's name with a quote and its entry and area, which prints `held for approval by <person> as hold <n>`; approve it on the page, which shows the IDs the approval published; `lodge show` of the decision's ID gives it as current; the server's output holds no `yaml` token or stream line; the ledger line records each step.
