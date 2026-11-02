# lodge server, build step 1, plan 3: the API, sign-in, and the command

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** the `lodge` command works at parity with lodge 0.2 against the lodge server, proved by lodge 0.2's command tests carried and run against an in-process server and through the compiled binary, and one person can register a passkey, sign in, issue agent tokens, and approve decisions drafted in their name on a minimal page.

**Architecture:** two adapters over plan 2's `app` and `store` (d-k5swcq): `api`, a `fetch` handler serving `POST /api/v1/<operation>` with JSON (d-sry12f), bearer tokens for agents, and passkeys and a session cookie for the person (d-yayhct); and `cli`, the command, which reads `.lodge.toml`, sends each operation to the server named there, and prints what lodge 0.2 prints.
`src/main.ts` wires both into one program built with `bun build --compile`: the command, and `lodge server setup` and `lodge server serve` (RULE-PROGRAM).
The page of d-jtxwg3 is `api`'s last task.

**Tech stack:** plan 1's (Bun 1.3.14, TypeScript 6.0.3 strict, Biome 2.5.15, dependency-cruiser 18.6.0, knip 6.42.0), plan 2's Kysely over `bun:sqlite`, and two dependencies added by Task 1: @simplewebauthn/server 14.0.3 in `api` (d-yayhct) and smol-toml 1.9.1 in `cli` (RULE-TOML).

**Spec:** `lodge spec` and lodge 0.2's tests for what the command does; `docs/superpowers/specs/2026-11-02-lodge-server-design.md` (the design, approved by the author 2026-11-02 13:52) for where it lives and what changes.
The plan argues from them, never over them; where they disagree with this plan, they win and the builder reports it.
"Design line N" is a line of the design; "probe N" is an item of `docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md`, whose sources are in `probes/` beside it; "plan 1, probe N" is an item of plan 1's.

## Global Constraints

Plan 1's Global Constraints hold unchanged (`docs/superpowers/plans/2026-11-02-lodge-server-core.md`, "Global Constraints"); each brief repeats them, with these for this plan:

- Builders are Codex (`codex exec`), one task per brief, with no network, a read-only git index, and no sockets; a package the task needs that `ts/package.json` lacks stops the task with BLOCKED and its name.
- The builder's gate is `sh scripts/check-ts.sh`; the coordinator's is `sh scripts/check.sh` outside the sandbox after every task, then it stages with explicit paths, commits with `git -c user.name="Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, the message ending `Co-Authored-By: Claude <noreply@anthropic.com>`, and pushes `server-api` (or the task's lane branch) to `origin`; never `main`.
- No test opens a socket: the server is reached through its handler, `handler(request)` (plan 1, probe 1), and the command through `run(argv, io)` with `io.fetch` bound to that handler.
  A test that needs a socket is a coordinator check, named in its task under **Coordinator** and run outside the sandbox (S1 to S3 below).
- A test that starts a child process uses `Bun.spawn` and awaits it, never `Bun.spawnSync` against a server in the same process, which never returns (probe 5).
- Structure (plan 1, Task 3; d-x6f9za, d-mfskz3, d-s5s2c3): `api` may use `fetch`, sockets (`Bun.serve`), `crypto`, and `process`, and reads no file (`Bun.file` and `node:fs` are `git`'s and `cli`'s), so its page and script come in as text imports (RULE-ASSETS); `cli` may read files and use `fetch` and writes none; `main` (`src/main.ts`) may import every package, and neither writes files nor opens sockets itself.
  Raising a limit or adding an allowed edge is the author's call; a task that finds it needs one stops with BLOCKED.
- Porting (d-88p8h9, plan 1's "Porting"): a carried command test keeps its Python name as its title, in the file the parity table names, and asserts what the Python asserts, no weaker, with the substitutions of RULE-E2E only: what lodge 0.2 reads from git (`git status`, the staged files, a file under `lodge/`) is read from the server's store, and the outcome `staged` is `published`, since a record is current from the moment it is written (design line 80).
  A test RULE-E2E drops is named in its row's `dropped` list in `ts/tests/parity.json` with the reason in `why`; every other name of a `changed` row is kept as for a `ported` row (Task 7a's parity change).
- The command prints what lodge 0.2 prints, byte for byte, wherever the parity table does not mark a change: its outputs are ports of `src/lodge/cli/output.py` and `thread_output.py`, fed by the server's answers decoded back into `app`'s results (RULE-WIRE).
- No secret in a URL, a log line, or the repository (must-not 6): the agent token travels only in `Authorization`, the session only in its cookie, and the server stores tokens, sessions, and setup codes only as SHA-256 hashes (RULE-TOKENS).
- User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; code comments state the fact.

## Calls made

Each is the planner's ruling, recorded in lodge with scope `process` and this plan as its work item; its reasoning there holds a handle per argument and the cost if wrong.
Every task repeats what it needs of them, so no brief needs this section.

1. RULE-CUT: the plan is ten tasks (1 to 6, 7a, 7b, 8, and the page as 9), run in lanes by the import graph (see "Order and lanes").
2. RULE-SERVER: the command finds the repository's root by walking up from its folder to the first that holds `.git`, reads the server's URL and the project's name from `[server]` in `.lodge.toml` there, and the agent token from the environment variable `LODGE_TOKEN`; it sends a token over `http` only to this machine (`localhost`, `127.0.0.1`, `[::1]`), and `https` otherwise.
3. RULE-TOML: the command parses `.lodge.toml` with smol-toml 1.9.1 and `integersAsBigInt`, which gives integers as `bigint` and floats as `number` (probe 1), so `title_chars = 80.0` is refused with lodge 0.2's sentence (probe 2), where `Bun.TOML.parse` gives the whole number 80 and also accepts a table header with no closing bracket (probe 1).
4. RULE-SETTINGS: a project's `[length]` and `[import]` settings live on the server, given once by `lodge init` from `.lodge.toml`, so that every client's check of the project uses the same settings; changing them later is outside build step 1, and the guide says so.
5. RULE-TOKENS: an agent token is issued by the signed-in person for one project's name, shown once, stored as its SHA-256, and revocable; it may create that project and call every operation on it but the person's; `approve`, `confirm`, and the token and project lists answer only the person's session cookie, sent with the server's own `Origin`.
6. RULE-WIRE: on the wire a field keeps its TypeScript name (`dryRun`, narrowing d-sry12f's `dry_run`), a `Map` or `Set` is tagged, `api` encodes and `cli` decodes, a write whose check fails answers 422 with its whole result, an unknown project answers kind `no-project`, an unexpected error kind `internal` (500), and every answer carries `Lodge-Version`, which the command requires to equal its own.
7. RULE-PROGRAM: there is one program, `lodge`; `src/main.ts` sends `lodge server setup` and `lodge server serve` to `api`'s `serverCommand` and everything else to `cli`'s `run`, since the layout allows one file at the root of `src` (`ts/tests/structure/calls.ts`, `layoutViolations`); it narrows d-yayhct's `lodge-server setup`; `ts/package.json` gains `"version": "0.3.0"`, which `--version` prints.
8. RULE-SIGNIN: the server's origin (`https://name` or `http://localhost:port`) and the person's name are fixed by the first `lodge server setup`; passkeys are created and used with user verification required; a session lasts 30 days; a ceremony's challenge lives in the server's memory for 5 minutes and is spent on use.
9. RULE-GRAMMAR: the command's grammar is a small parser of its own in `cli`, written to argparse's usage lines and messages (probe 6), with no library.
10. RULE-E2E: the carried command tests run the command in process against an in-process server built from plan 2's store on `:memory:`, the person signed in with the software authenticator of plan 1, probe 2; a hand edit of a record file is a write through the store that bypasses `app`; and with `LODGE_E2E_BINARY` set, the same tests run the compiled binary against that server on a loopback socket (S1).
11. RULE-ASSETS: the page and its script are text imports into `api` (`page.html` cast to `string`, `page.js` typed by `src/api/text.d.ts`), and the guide is a text import into `cli` (`src/cli/text.d.ts`), all embedded in the binary (probe 3).
12. RULE-KNIP: Task 8 turns on knip's `includeEntryExports` (d-s2rdn2), and a name of `#core` that `__all__` holds and no file reads is tagged `/** @public */` in its module (probe 4), so knip and the front-door test of d-hshapm agree.

## Review Focus

1. A carried command test that asserts less than its Python original beyond RULE-E2E's two substitutions, or a `changed` row whose kept tests lose a name.
2. Output: a line the command prints that differs from lodge 0.2's for the same records, an exit code that differs, or something printed on standard output that lodge 0.2 prints on standard error.
3. Authorisation: an operation an agent token reaches that RULE-TOKENS gives the person only, a token reaching another project, a cookie request without the server's `Origin` accepted, a setup code accepted twice or after 15 minutes, a passkey's counter going backwards accepted.
4. Secrets: a token, session, or setup code stored, logged, or put in a URL in clear, or a response that echoes one beyond the single answer that issues it.
5. Settings: `.lodge.toml` read as lodge 0.2 reads it wherever RULE-SERVER and RULE-TOML do not change it, every malformed file one sentence and exit 2 before any request.
6. The page: text from records reaching the page as HTML rather than text, or a script loaded from anywhere but the server.

## Order and lanes

The build starts after plan 1 merges into `server-api`; Tasks 4 to 9 also need plan 2 (`store` and `app`) merged into `server-api` first, since they import `#app` and `#store`.
Lanes follow the import graph, each in its own worktree merged into `server-api`, as plan 1's lanes are (d-xdqsmf):

| Task | Imports | Needs | Lane |
|---|---|---|---|
| 1 | none | plan 1 | coordinator, first |
| 2 | `#core` | 1 | A, beside 3 and 4 |
| 3 | `#core`, smol-toml | 1 | B, beside 2 and 4 |
| 4 | `#core`, `#app`, `bun:sqlite` | 1, plan 2 | C, beside 2 and 3 |
| 5 | `#core`, `#app` | 4 | C |
| 6 | `#core`, `#app`, @simplewebauthn/server | 5 | C |
| 7a | `#core`, `#app` (types); tests `#api`, `#store` | 2, 3, 6 | main line |
| 7b | as 7a | 7a | main line |
| 8 | every package | 7b | main line |
| 9 | `#core`, `#app` | 6 | D, beside 7a to 8; its browser check (S3) after 8 |

Tasks 2 and 3 both create files in `src/cli` and touch `src/cli/index.ts` and `package.json`'s `imports`; the second to merge keeps both entries.
Task 9 is the plan's last task by d-jtxwg3; by the import graph it can be built beside 7a to 8, and it merges last.

## Coordinator checks

These need a socket, a built binary, or a browser, so the coordinator runs them outside the sandbox and records each result in the ledger line of its task.

- **S1** (Task 8): `cd ts && bun run build && LODGE_E2E_BINARY="$PWD/dist/lodge" bun test tests/e2e`: every carried command test passes with the compiled binary as the command, talking over a loopback socket to the in-process server (RULE-E2E).
- **S2** (Task 9, during S3): the server runs as `LOG_TOKENS=1 LOG_STREAM=1 dist/lodge server serve …`, an `add` goes through it, and its output holds none of the `yaml` package's token or stream lines (d-v9mw2d).
- **S3** (Task 9, after Task 8): in a real browser, the coordinator registers a passkey with the setup code, signs out and in, issues an agent token, runs `lodge init` and an `add` of a decision drafted in the person's name from a scratch repository with that token, approves the decision on the page, and sees `lodge show` give it as current (d-jtxwg3); a browser's virtual authenticator from its developer tools counts.

## Names consumed from plan 2

Plan 2's brief keeps `app`'s public names those of `src/lodge/app` in camelCase and names its additions in its Interfaces; this plan consumes the following, aligned against plan 2's plan as the ledger records.

- `#app`: `Lodge` (`new Lodge(store, clock, ids, settings)`, with `search`, `show`, `waitingAll`, `timeline`, `spec`, `problems`, `check`, `draft`, `mint`, `add`, `ask`, `reply`, `close`, `threads`, `thread`, `confirm`, and `behindArea`), the errors `LodgeError`, `NotFound`, `Conflict`, and `StaleList`, the results `Added`, `AddOutcome`, `Behind`, `Listed`, `Read`, `Shown`, `ThreadList`, `ThreadShown`, `ThreadsWaiting`, and `Written`, and the ports `Clock` and `IdSource`.
  `api` awaits every call, so a `Lodge` whose methods return promises and one whose methods return values both serve.
- Plan 2's model changes: the operation that approves a decision drafted in a person's name, the read that lists the decisions waiting for a person's approval, and the form a person's name takes in `decided_by`.
- `#store`: the function that opens the store on a path (`:memory:` in tests), the `Store` port it gives `Lodge` for one project, and a write of a record file's event that bypasses `app`, which RULE-E2E's hand edits use.

## Parity table, this plan's rows

Plan 1's table gives these rows plan 3; this plan settles each one's final status, which the task named writes into `ts/tests/parity.json` in its last step.
A `changed` row keeps its file, gives its `why`, and lists in `dropped` the Python tests with no counterpart; every other name of the row is checked as a `ported` row's is (Task 7a).
"Store for git" means RULE-E2E's substitution: what the Python test reads from git or from a file under `lodge/` is read from the server's store, and `staged` is `published`.

| Python file | Task | TypeScript counterpart | Status, `dropped`, and why |
|---|---|---|---|
| `tests/e2e/conftest.py` | 7a | `ts/tests/e2e/project.ts` | ported; the server it talks to is `ts/tests/e2e/server.ts` |
| `tests/e2e/support.py` | 7a | `ts/tests/e2e/support.ts` | ported |
| `tests/e2e/test_add_attach.py` | 7b | `ts/tests/e2e/add-attach.test.ts` | changed; dropped `attachment_lands_on_the_branch_in_branch_mode`; design line 72: no branch mode on the server; store for git in the others |
| `tests/e2e/test_add_bad_yaml_exits_2_naming_file_and_line.py` | 7b | `ts/tests/e2e/add-bad-yaml-exits-2-naming-file-and-line.test.ts` | ported |
| `tests/e2e/test_add_dry_run.py` | 7b | `ts/tests/e2e/add-dry-run.test.ts` | ported; store for git |
| `tests/e2e/test_add_failing_check_exits_1.py` | 7b | `ts/tests/e2e/add-failing-check-exits-1.test.ts` | ported; store for git |
| `tests/e2e/test_add_import.py` | 7b | `ts/tests/e2e/add-import.test.ts` | ported; store for git |
| `tests/e2e/test_add_new_decision_entry_area.py` | 7b | `ts/tests/e2e/add-new-decision-entry-area.test.ts` | ported; store for git, the five staged files being the three records, since `init` creates no `.gitkeep` |
| `tests/e2e/test_add_non_string_scalar_exits_2.py` | 7b | `ts/tests/e2e/add-non-string-scalar-exits-2.test.ts` | ported |
| `tests/e2e/test_before_init_one_sentence_exit_2.py` | 7a | `ts/tests/e2e/before-init-one-sentence-exit-2.test.ts` | ported; the sentence is kept through kind `no-project` (RULE-WIRE) |
| `tests/e2e/test_broken_agent_decision_warns_above_show.py` | 7a | `ts/tests/e2e/broken-agent-decision-warns-above-show.test.ts` | ported; the hand edit through the store (RULE-E2E) |
| `tests/e2e/test_check_and_gate.py` | 7a | `ts/tests/e2e/check-and-gate.test.ts` | changed; dropped `gate_passes_with_notes_for_new_records`; design line 79: the published state is the current state, so `check --gate` prints what `check` prints and has no new records to note |
| `tests/e2e/test_draft_then_add_edit.py` | 7b | `ts/tests/e2e/draft-then-add-edit.test.ts` | ported; store for git |
| `tests/e2e/test_guide.py` | 7a | `ts/tests/e2e/guide.test.ts` | changed; dropped none; design line 72: the guide's lines on git (checkout and branch modes, the rewritten branch, the machine's clock) describe the server instead, so `guide_is_short_and_covers_the_write_path` looks for the new line |
| `tests/e2e/test_help_lists_every_command.py` | 7a | `ts/tests/e2e/help-lists-every-command.test.ts` | changed; dropped none; d-sry12f: `view` waits for step 3's interface and `hook` for plan 4, so the list of commands holds neither, and `version_works_anywhere` prints `ts/package.json`'s version (RULE-PROGRAM) |
| `tests/e2e/test_id.py` | 7a | `ts/tests/e2e/id.test.ts` | ported |
| `tests/e2e/test_init.py` | 7a | `ts/tests/e2e/init.test.ts` | changed; dropped `init_in_an_unwritable_checkout`; design line 72: `init` creates the project on the server and writes no file, and its output names the project and the server |
| `tests/e2e/test_malformed_settings_one_sentence_exit_2.py` | 7a | `ts/tests/e2e/malformed-settings-one-sentence-exit-2.test.ts` | changed; dropped none; RULE-SERVER: `[store]` is an unknown section on the server, so the third case is a malformed `[server]` |
| `tests/e2e/test_outside_repository_one_sentence_exit_2.py` | 7a | `ts/tests/e2e/outside-repository-one-sentence-exit-2.test.ts` | ported |
| `tests/e2e/test_same_second.py` | 7b | `ts/tests/e2e/same-second.test.ts` | changed; dropped `agent_edit_in_the_same_second_publishes_in_branch_mode`; design line 72: no branch mode on the server; the clock that stands still is the server's |
| `tests/e2e/test_search.py` | 7a | `ts/tests/e2e/search.test.ts` | ported |
| `tests/e2e/test_search_limit.py` | 7a | `ts/tests/e2e/search-limit.test.ts` | ported |
| `tests/e2e/test_search_shows_unparsable_file.py` | 7a | `ts/tests/e2e/search-shows-unparsable-file.test.ts` | ported; the hand edit through the store |
| `tests/e2e/test_show_ambiguous_code_one_line.py` | 7a | `ts/tests/e2e/show-ambiguous-code-one-line.test.ts` | ported; the hand edit through the store |
| `tests/e2e/test_show_levels.py` | 7a | `ts/tests/e2e/show-levels.test.ts` | ported |
| `tests/e2e/test_spec.py` | 7a | `ts/tests/e2e/spec.test.ts` | ported |
| `tests/e2e/test_threads.py` | 7b | `ts/tests/e2e/threads.test.ts` | changed; dropped `thread_files_are_staged_not_committed`; design line 72: a thread is written to the server's store, with nothing staged or committed; store for git in the others |
| `tests/e2e/test_waiting.py` | 7a | `ts/tests/e2e/waiting.test.ts` | ported |
| `tests/test_entry_point.py` | 8 | `ts/tests/e2e/binary.test.ts` | ported; the compiled binary's `--version` |
| `tests/test_wheel.py` | 8 | `ts/tests/e2e/binary.test.ts` | changed; dropped `installed_wheel_runs`; design line 55: the command ships as a binary built with `bun build --compile`, which `compiled_binary_runs` builds and runs |

Where plan 2's model change makes a decision `decided_by` a person a draft that waits for that person (SRV-2), a carried test that seeds one approves it through the person's session before it reads (`seed` in `support.ts` does so), and the task's report lists each such test; that is the model change, not a weakening.

---

### Task 1: The dependencies

The coordinator does this task outside the sandbox, since it installs packages (d-4psbdv).

**Files:**
- Modify: `ts/package.json`, `ts/bun.lock` (by `bun install`), `ts/knip.json`

**Interfaces:**
- Produces: `@simplewebauthn/server` 14.0.3 and `smol-toml` 1.9.1 in `ts/package.json`'s `dependencies`, each at least two weeks old on 2026-11-02 (probe 7); `"version": "0.3.0"` in `ts/package.json` (RULE-PROGRAM).
- `ts/knip.json`'s `ignoreDependencies` gains both names, since no code imports them yet; Task 3 takes `smol-toml` out and Task 6 `@simplewebauthn/server`, as plan 1's Tasks 4 and 5a did for `yaml` and `@noble/hashes`.

- [ ] **Step 1:** Add the two dependencies and the version; in `ts/`, `bun install`, then `bun install --frozen-lockfile`, then `bun x biome format --write package.json`.
- [ ] **Step 2: Verify** `grep -c '"[~^]' ts/package.json` prints 0; `sh scripts/check.sh` exits 0.
- [ ] **Step 3:** Commit `ts/package.json`, `ts/bun.lock`, and `ts/knip.json`; push; the ledger line names the versions.

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
  export interface Exit { readonly kind: "exit"; readonly code: number; readonly out: string; readonly err: string }
  export function parse(argv: readonly string[], version: string): Command | Exit
  ```
- `args.ts` is a small parser of declared commands (RULE-GRAMMAR): each command has a name, a summary, positionals (required, optional as `?`, one or more as `+`, with choices or a converter), and options (a flag, a value, a repeatable value, with choices, a converter, a default, or required); it reads options before, between, and after positionals, `--name=value`, `--` as the end of options, and a unique prefix of a long option as that option, as argparse's `allow_abbrev` does.
- What `parse` gives, as lodge 0.2 gives it (probe 6, `src/lodge/cli/parser.py`, `src/lodge/cli/threads.py`):
  - `--version` anywhere before the command: `Exit` 0 with `lodge <version>\n` on `out`.
  - `-h` or `--help`: `Exit` 0 with the help on `out`; the top-level help has parser.py's description and epilog, a line `usage: lodge [-h] [--version] COMMAND ...`, and one line per command beginning with its name, then its summary; a command's help begins `usage: lodge <name> `, then its options and positionals in argparse's form, then its summary.
  - A usage error: `Exit` 2 with the command's usage line, then `lodge <name>: error: <message>` (or `lodge: error: …` before a command), each ending in `\n`, on `err`; the messages are argparse's: `the following arguments are required: <names joined by ", ">`, `argument <name>: invalid choice: <pyRepr of the value> (choose from <choices joined by ", ">)`, `argument --limit: <pyRepr of the value> is not a positive whole number`, `argument <name>: expected one argument`, `unrecognized arguments: <words joined by " ">`, and `ambiguous option: <word> could match <options joined by ", ">`.
  - The commands, summaries, and options of parser.py and threads.py, but `view` and `hook` (d-sry12f; `hook` comes with plan 4): `init`, `id`, `search`, `show`, `draft` (its summary holding "a decision is immutable"), `add`, `check`, `spec`, `waiting`, `guide`, `threads`, `thread`, `ask`, `reply`, and `close`.
  - `--limit` takes ASCII digits naming a number of 1 or more; Python's `isdecimal` also takes other decimal digits (`src/lodge/cli/parser.py:137`), so the report lists the narrowing.
  - The rule of `_message_command` (`src/lodge/cli/threads.py:68-81`): `--by author` without `--where` or `--when`, or `--where` or `--when` without `--by author`, is `Exit` 2 with `lodge: <its sentence>\n` on `err`, as lodge 0.2 raises a `LodgeError` there.
  - `search`'s `filters` come from `#core`'s `filters` with `kind`, `scope`, `status` (default `current`), `area`, and `decidedBy` from `--by`.

- [ ] **Step 1: Write the failing tests.**
  - `args.test.ts`: `options_before_between_and_after_positionals`; `equals_form`; `double_dash_ends_options` (`show -- -x` gives the ref `-x`); `unique_prefix_is_the_option` (`show d-aaaaaa --prov`); `ambiguous_prefix_is_an_error` (`search x --s y`: `ambiguous option: --s could match --scope, --status`); `repeatable_option_collects` (`--attach a --attach b`); `missing_value_is_an_error` (`search --kind`: `argument --kind: expected one argument`); `extra_words_are_an_error` (`thread q-aaaaaa extra`: `unrecognized arguments: extra`).
  - `grammar.test.ts`: `every_command_parses` (`test.each` over one argv per command and its `Command`, `search` with every filter included); `help_lists_every_command` (the fifteen names, each the first word of a line of the top-level help); `every_command_has_help` (`test.each` over the fifteen: code 0, `out` beginning `usage: lodge <name>`); `no_command_is_a_usage_error` (code 2, `err` holding `usage:` and ending `lodge: error: the following arguments are required: COMMAND\n`); `invalid_choice_is_argparse_s_line` (`search x --status gone` and `id x`, each `err`'s last line as probe 6 prints it); `missing_positional_is_argparse_s_line` (`add`: `lodge add: error: the following arguments are required: FILE`); `limit_must_be_a_positive_whole_number` (`0`, `-1`, `many`, and `٣`); `author_message_needs_where_and_when`; `where_with_an_agent_role`; `version_prints_the_version_given`; `draft_help_says_decisions_are_immutable`.
- [ ] **Step 2: Run** `cd ts && bun test tests/cli`; expected: FAIL (no module).
- [ ] **Step 3: Implement** `args.ts` and `grammar.ts`; `index.ts` exports `parse`, `Command`, and `Exit`; add `#cli` to `package.json`'s `imports`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 3: The command's settings and files

**Files:**
- Create: `ts/src/cli/errors.ts`, `ts/src/cli/settings.ts`, `ts/src/cli/files.ts`
- Modify: `ts/src/cli/index.ts`, `ts/knip.json` (`smol-toml` leaves `ignoreDependencies`); `ts/package.json`'s `imports` gains `#cli` if Task 2 has not merged
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
  export function tokenOf(env: Readonly<Record<string, string | undefined>>, server: ServerPlace): string
  // files.ts
  export function readDraft(path: string): string
  export function readExact(path: string, notUtf8: string): string
  ```
- `repositoryRoot` (RULE-SERVER): the nearest folder at or above `cwd` holding an entry named `.git`, a folder or a file (a worktree's); none is `CliError("<cwd> is not inside a git repository")`, lodge 0.2's sentence (`src/lodge/gitstore/setup.py:24`).
- `readSettings` (RULE-TOML, RULE-SERVER), every refusal a `CliError` whose message begins `.lodge.toml: ` and is one line:
  - no `.lodge.toml`: no server, no core table, and `coreSettings()`, as lodge 0.2 reads defaults (`src/lodge/gitstore/settings.py:42`);
  - unreadable, or not UTF-8: `.lodge.toml: cannot be read: <reason>`;
  - not TOML: `.lodge.toml: ` and the first line of smol-toml's message (probe 1);
  - parsed with `integersAsBigInt: true`, then converted: a `bigint` becomes a number, a `number` (a TOML float, `inf` and `nan` included) becomes `null`, and a date or time becomes `null`, so that `parseCoreSettings` refuses each where lodge 0.2 refuses a float or a date, with lodge 0.2's sentence and in its order (probes 1 and 2);
  - the top-level names are read in the file's order: `server` and `hook` are this package's, `length` and `import` core's, and any other name is `unknown section [<name>]` for a table and `unknown key <name>` otherwise, as `parse_core_settings` words them (`src/lodge/core/settings.py:31-37`), `store` included (lodge 0.2's `[store]` has no meaning on the server);
  - `[server]`: a table holding `url` and `project` and nothing else (`server must be a table`, `unknown key server.<key>`, `[server] needs url and project`); `url` an `https` URL, or an `http` URL whose host is `localhost`, `127.0.0.1`, or `[::1]`, with no user, path other than `/`, query, or fragment (`server.url must be an https URL, or an http URL on this machine`); `project` lower-case letters, digits, and hyphens, starting with a letter or digit, at most 63 characters (`server.project must be lower-case letters, digits, and hyphens`);
  - `[hook]` is left as it is: lodge 0.2 checks it on every command (`src/lodge/main.py:42-46`), and plan 4's hook brings that check back;
  - `core` holds the `length` and `import` tables as converted, and `coreSettings` is `parseCoreSettings` of them.
- `serverOf` throws `CliError(NO_SERVER)` when `server` is `null`; `tokenOf` gives `LODGE_TOKEN`, and when it is unset or empty throws `CliError("LODGE_TOKEN is not set; the person issues an agent token on <url>")`.
- `readDraft` reads as Python's `read_text(encoding="utf-8")` does (`src/lodge/cli/files.py`): strict UTF-8 with a byte order mark kept, then `\r\n` and a lone `\r` made `\n`; `readExact` reads as `read_bytes().decode("utf-8")`, with no change to line ends.
  Not UTF-8 is `CliError("<path>: <notUtf8>")` (`readDraft` passes `not UTF-8 text`); an unreadable file is `CliError("<path>: cannot be read: <reason>")`, the reason being the system's description of the error, which the report compares with Python's `strerror`.

- [ ] **Step 1: Write the failing tests.**
  - `settings.test.ts`, each on files written into a temporary folder: `root_is_the_nearest_folder_with_git` (a nested folder; `.git` as a folder and as a file); `outside_a_repository_is_one_sentence`; `no_settings_file_has_no_server`; `whole_number_float_is_refused` (`test.each` over `title_chars = 80.0` under `[length]`, `8e1`, `length = {title_chars = 80.0}`, and `length.title_chars = 80.0`, each `.lodge.toml: length.title_chars must be a positive whole number`); `integer_forms_are_read` (`80`, `0x50`, `+80`, `1_000`, and `99999999999999999999`); `inf_and_a_date_are_refused`; `float_in_sources_is_refused` (`.lodge.toml: import.sources must be a list of file names`); `unclosed_table_header_is_one_sentence` (`[store` with no bracket: one line beginning `.lodge.toml: `); `store_is_an_unknown_section`; `first_unknown_name_in_file_order_is_named`; `server_is_read`; `server_url_must_be_https_or_this_machine` (`test.each` over refused and accepted URLs, `http://example.org`, a path, a query, and `https://user@host` among the refused, and `http://localhost:8787`, `http://127.0.0.1:9`, `http://[::1]:9`, and `https://lodge.example.org` the accepted); `server_project_is_a_name`; `server_needs_url_and_project`; `hook_is_left_alone`; `core_table_holds_length_and_import_only`; `token_comes_from_the_environment` (set, unset, and empty).
  - `files.test.ts`: `draft_line_ends_are_translated` (`a\r\nb\rc\n` to `a\nb\nc\n`); `draft_keeps_a_byte_order_mark`; `exact_text_keeps_its_line_ends`; `not_utf8_is_one_sentence`; `missing_file_is_one_sentence`.
- [ ] **Step 2: Run** `cd ts && bun test tests/cli`; expected: the new tests FAIL.
- [ ] **Step 3: Implement**; take `smol-toml` out of `ts/knip.json`'s `ignoreDependencies`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green, knip reporting no unused dependency.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.
