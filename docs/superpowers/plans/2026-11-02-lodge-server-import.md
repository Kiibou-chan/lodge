# lodge server, build step 1, plan 4: the importer, the export, and the design's records

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** a lodge 0.2 store moves onto the server and back out to git with nothing changed but the people in `decided_by`, the hook tells an agent that a moved project's records live on the server, and lodge's specification holds the server design, whose document is then frozen.

**Architecture:** the `git` package reads a 0.2 store's files at a revision and writes the export's commits through a temporary index; it is the only package that runs git or touches files (d-k5swcq, d-x6f9za).
`app` prepares an import (it checks the store as lodge 0.2 checks it, then maps the author to the project's first owner) and batches the export behind clock and timer ports; `api` serves `import` and `export-target` to the signed-in person only; `hook` ports lodge 0.2's hook with advice for a moved project; `cli` gains `lodge hook`; `main` wires them.
Records cross every boundary as path and file text, as lodge 0.2 writes them (d-smx3xf).

**Tech stack:** plan 1's, with no new dependency (Task 1): git through the `git` program, as lodge 0.2 runs it (`src/lodge/gitstore/git.py`); TOML through plan 3's reader of `.lodge.toml`; stored bytes decoded by `text.ts` (probe 1).

**Spec:** `lodge spec` and lodge 0.2's tests for the behaviour carried over; `docs/superpowers/specs/2026-11-02-lodge-server-design.md` (the design, approved by the author 2026-11-02 13:52) for what changes.
The plan argues from them, never over them; where they disagree with this plan, they win and the builder reports it.
"Design line N" is a line of the design; "probe N" is an item of `docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md`, whose sources are in `probes/` beside it; "plan 1", "plan 2", and "plan 3" are `docs/superpowers/plans/2026-11-02-lodge-server-core.md`, `…-server-store.md`, and `…-server-api.md`.

**Aligned against:** ALIGNMENT-PENDING.

## Global Constraints

- Builders are Codex (`codex exec`), one task per brief; a brief holds these constraints and its task, and Codex sees only its brief, `CLAUDE.md`, and the repository.
- In Codex's sandbox git's index is read-only, sockets are refused, and there is no network (plan 1, Global Constraints): the builder never stages, commits, or pushes, and never runs `bun install` or `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name.
  Git in a temporary folder works there: lodge 0.2's 1,056 tests, its git store's among them, passed in the sandbox (`docs/superpowers/plans/2026-10-30-lodge-on-itself/task-5-report.md:102`).
- The builder's gate: `sh scripts/check-ts.sh`; the coordinator's gate after every task: `sh scripts/check.sh` green outside the sandbox, then it stages with explicit paths, commits with `git -c user.name="Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, the message ending `Co-Authored-By: Claude <noreply@anthropic.com>`, and pushes `server-import` to `origin`; never `main`.
- lodge 0.2 keeps working: `src/`, `tests/`, `pyproject.toml`, and `uv.lock` are not edited.
- Test-first: each carried or new test is written and seen failing before its code (a missing module or export counts as failing); a carried test over code that already exists is seen failing against a mutation of that code, which the builder names in its report and then reverts (d-mfayy5); every existing test keeps passing, edited only where a task says so.
- Porting follows plan 1's Global Constraints, "Porting", "Types", "Exceptions", "Names", "Text", and "Times", which the brief repeats: carried tests keep their Python names without `test_`, an assertion asserts no less than its Python original, a parametrised test keeps every case, `X | None` is `X | null`, a `raise ValueError` is the `ValueError` of `#core`, a Python string operation whose JavaScript namesake differs goes through `text.ts`, and times cross into `core` and `app` as stamps.
- Errors: every refusal the command or the API reports is a `LodgeError` of `#app` or one of its subclasses (`NotFound`, `Conflict`), as in lodge 0.2 (`src/lodge/app/errors.py`, `src/lodge/gitstore/errors.py`), with its message given in the task.
- Structure (plan 1, Task 3; d-k5swcq, d-x6f9za, d-mfskz3, d-s5s2c3): only `git` spawns processes and writes files, and `git` and `cli` read them; `hook` neither reads files nor resolves links, so it gets path resolution from `git` through `main`; `core` and `app` take the time and timers through ports; another package only through `#name`; no file over 300 lines.
- Exports (d-tha8st): every export a task adds has a reader in that task, its own tests counting, so knip passes after each task, including once plan 3 turns on `includeEntryExports` (d-s2rdn2).
- Git in tests: only in folders made with `mkdtempSync` under the system's temporary folder, through `isolateGit()` of `ts/tests/git/isolated.ts` (Task 3), which gives every test an empty `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_TERMINAL_PROMPT=0`, and a fixed identity; every repository is made with `git init -b main` (or `--bare -b main`); a remote is a bare repository named by its path, so no test needs a socket or the network (`CLAUDE.md`, "Hard rules").
- Fixtures are the made-up project of lodge 0.2's tests (the `storage` area, transcripts, logs), never her words or another project's records; the made-up 0.2 store of `probes/zero-two-store/` is lodge 0.2's own output for that project (probe 6).
- User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; code comments state the fact.
- Records (Tasks 11a to 11c): written only through `lodge add`, drafts under `.drafts/`, a dry run before every add; in the sandbox, once per task, `mkdir -p .drafts/objects && cp "$(git rev-parse --absolute-git-dir)/index" .drafts/index`, then every `lodge add` runs as `GIT_INDEX_FILE="$PWD/.drafts/index" GIT_OBJECT_DIRECTORY="$PWD/.drafts/objects" GIT_ALTERNATE_OBJECT_DIRECTORIES="$(git rev-parse --path-format=absolute --git-common-dir)/objects" uv run --frozen --quiet lodge add FILE...` (`docs/superpowers/plans/done/2026-10-31-lodge-viewer.md:25`); when that fails, the coordinator runs the adds from the builder's drafts.

## Calls made

Each is the planner's ruling, recorded in lodge with scope `process` and this plan as its work item; its reasoning there holds a handle per argument and the cost if wrong.
Every task repeats what it needs of them, so no brief needs this section.

1. d-1skjw1: the `import` operation names a repository on the server's machine and a revision, the server reads it through `git`, and only the signed-in person may call it; step 1 gives it no command and no form (Tasks 3 and 8).
2. d-ag8p8h: the importer runs lodge 0.2's state check on the store as read, with the store's own `.lodge.toml`, before it maps, and imports into an empty project only (Tasks 6 and 8).
3. d-bh93bn: the importer maps only `decided_by: author`, through the writer, refusing a decision the writer would not give back byte for byte; thread messages keep `by: author` (Task 6).
4. d-m31e0d: `decodeStored` and `encodeStored` live in `text.ts` (d-0q54zn), and the importer refuses an attachment that is not UTF-8 (Tasks 2 and 3).
5. d-pv341r: the export writes only a branch holding nothing outside `lodge/` that no work tree has checked out, through a temporary index, without force, with no commit when nothing changed (Task 4).
6. d-srfxj8: `app`'s `Exporter` batches the writes into at most one commit a minute behind clock and timer ports, retries a minute after a failure, flushes on start, and writes the two `.gitkeep` files back (Tasks 7 and 8).
7. d-va3j7x: a project has moved when its `.lodge.toml` names its server; then every file under `lodge/` but the attachments gets the moved advice, and the hook gets its context and path resolution from `git` through the composition root (Tasks 3, 5, and 9).
8. d-yng7m8: the server design goes into lodge whole, a decision per section, in three tasks, an unbuilt claim naming its build step; new areas `work` and `sessions` (Tasks 11a to 11c).

One question is the author's, since two lines of her approved design pull apart (IMP-1 in `docs/superpowers/plans/2026-11-02-lodge-server-import/questions.md`): writing the person in `decided_by` (design line 78) makes lodge 0.2's check fail on the export, which is to read like a 0.2 store (design line 284; probe 3).
The plan follows design line 78 until she answers; her answer changes one function of Task 7 and the expectations of Task 10.

## Names this plan consumes from plans 2 and 3

CONSUMED-PENDING

## Lanes

The tasks run on `server-import` in its worktree; a lane is a task built in its own worktree and merged into `server-import`, as plan 1's lanes are (d-xdqsmf).
What each task imports decides when it can start:

| Task | Packages it touches | Starts after | Beside |
|---|---|---|---|
| 1 | none (setup) | plan 1 merged into `server-import` | |
| 2 | `core` | Task 1 | |
| 3 | `git` | Task 2, and plan 2's `app` front door with `LodgeError` merged | 5, 6, 7 |
| 4 | `git` | Task 3 | 5, 6, 7 |
| 5 | `hook` | Task 2, and plan 2's `LodgeError` merged | 3, 4, 6, 7 |
| 6 | `app` | Task 2, and plan 2's `app` front door merged | 3, 4, 5, 7 |
| 7 | `app` | Task 2, and plan 2's `app` front door merged | 3, 4, 5, 6 |
| 8 | `app`, `api`, `main` | Tasks 3, 4, 6, and 7, and plans 2 and 3 merged | 9 |
| 9 | `hook`, `cli`, `main` | Tasks 3 and 5, and plan 3 merged | 8 |
| 10 | tests and scripts | Tasks 8 and 9 | |
| 11a, 11b, 11c | records | Task 10; in order | |

Tasks 6 and 7 both add to `ts/src/app/index.ts`, and Tasks 8 and 9 both to `ts/src/main.ts`; the merge of the second lane keeps both sides' lines.

## Review Focus

1. Bytes: a record file with an undecodable byte is problem 1 and refuses the import, an attachment that is not UTF-8 is refused by name, and no lone surrogate reaches the events store (probes 1 and 2).
2. The author mapping: only `decided_by: author` of a decision changes, through the writer, and a decision whose file the writer would not give back byte for byte is refused rather than rewritten; thread messages keep `by: author`.
3. The import refuses a store lodge 0.2's check refuses, with the same problems, and a project that already holds records; nothing is written when it refuses.
4. The export: never a branch holding anything outside `lodge/`, never a branch a work tree has checked out, never a force push, no commit when nothing changed, and at most one commit a minute however many writes come.
5. Who may: `import` and `export-target` answer an agent's token with `forbidden`, since an import writes decisions in a person's name (design line 75).
6. The hook: every carried test keeps its assertions, a moved project's advice names the server and never `git checkout`, and the hook stays silent on every failure.
7. The round trip: the made-up store comes back byte for byte apart from the `decided_by` lines of its author decisions.

## Parity rows this plan settles

| Python file | Status now | After | Task | TypeScript counterpart |
|---|---|---|---|---|
| `tests/gitstore/conftest.py` | planned | ported | 3 | `ts/tests/git/isolated.ts` |
| `tests/gitstore/repos.py` | planned | changed: "design line 72: records live in the server's events, not in files in git; the helpers of lodge 0.2's git store (`initialised`, `publish_one`, `checkout_project`, `Ticker`) have no counterpart, and the repository helpers are carried" | 3 | `ts/tests/git/repos.ts` |
| `tests/hook/test_post_tool_use.py` | changed | changed | 5 | `ts/tests/hook/post-tool-use.test.ts` |
| `tests/e2e/test_hook_feedback_after_hand_edits.py` | changed | changed | 9 | `ts/tests/hook/hand-edits.test.ts` |
| `tests/e2e/test_hook_outside_repository_exit_0_silent.py` | planned | ported | 9 | `ts/tests/hook/outside-repository.test.ts` |

The three hook rows keep every Python test name, since the design's change adds the moved project's advice and leaves the rest; Task 10 makes the parity test check that, and that their files exist.

---

### Task 1: Setup

The coordinator does this task itself, outside the sandbox.

**Files:** the ledger only.

**Interfaces:**
- Consumes: plan 1, merged into `server-import`.
- Produces: the ledger line naming the dependencies this plan adds: none.

- No dependency is added: git runs as the `git` program, `.lodge.toml` is parsed by plan 3's reader, and stored bytes are decoded by `text.ts` (probe 1); so `ts/package.json` and `ts/bun.lock` stay as plans 1 to 3 leave them, and only the `imports` map gains `#git` and `#hook` where Tasks 3 and 5 create those packages (or keeps plan 3's entries, if it created them).
- Merge points: plan 2's commit that creates `ts/src/app/index.ts` with `LodgeError` is merged into `server-import` before Tasks 3, 5, 6, and 7; all of plans 2 and 3 before Tasks 8 and 9; the ledger names each merged commit.

- [ ] **Step 1:** Merge `server-core` into `server-import` once plan 1's last task is merged there; `sh scripts/check.sh` green.
- [ ] **Step 2:** `git diff server-core -- ts/package.json ts/bun.lock` prints nothing; the ledger line says no dependency is added and why.

### Task 2: Stored bytes as lodge 0.2 reads them (d-0q54zn, d-m31e0d)

**Files:**
- Modify: `ts/src/core/text.ts` (two functions), `ts/src/core/fileformat.ts` (`contentHash`)
- Create: `ts/tests/core/zero-two-store.ts` (the made-up 0.2 store, read by Tasks 3, 6, 7, 8, and 10)
- Test: `ts/tests/core/stored-bytes.test.ts` (new)

**Interfaces:**
- Consumes: plan 1's core.
- Produces, through `#core` (as names of `text.ts`, which the front-door test allows, d-hshapm):
  ```ts
  export function decodeStored(bytes: Uint8Array): string   // bytes.decode("utf-8", "surrogateescape")
  export function encodeStored(text: string): Uint8Array    // text.encode("utf-8", "surrogateescape")
  ```
- `decodeStored` reads well-formed UTF-8 as Unicode's table defines it (a second byte of `A0` to `BF` after `E0`, `80` to `9F` after `ED`, `90` to `BF` after `F0`, and `80` to `8F` after `F4`; no lead byte `C0`, `C1`, or `F5` to `FF`), and maps each byte b of anything else to U+DC00 + b, one byte at a time; this is the decoder of `probes/decode.ts`, which agrees with Python on 20,020 byte strings (probe 1).
- `encodeStored` encodes U+DC80 to U+DCFF as the byte U+DC00 less, and every other character as UTF-8; any other lone surrogate throws the `ValueError` of `errors.ts` with Python's message, `'utf-8' codec can't encode character '\ud83d' in position 0: surrogates not allowed`, the character as `\u` and four hex digits and the position in code points.
- `contentHash` hashes `encodeStored(normaliseNewlines(text))`, as `content_hash` hashes `normalise_newlines(text).encode("utf-8", errors="surrogateescape")` (`src/lodge/core/fileformat.py:93-96`).
- `zero-two-store.ts` exports `ZERO_TWO_STORE: ReadonlyMap<string, string>`, the eleven files of `probes/zero-two-store/` (ten under `lodge/` and `.lodge.toml`) by path, as literal texts copied byte for byte.
- If plan 2 has already built d-0q54zn, this task keeps only `zero-two-store.ts` and its test, and the ledger names plan 2's commit; Task 3 then calls plan 2's names.

- [ ] **Step 1: Write the failing tests** in `stored-bytes.test.ts`: `decode_matches_surrogateescape` (`test.each` over the 20 edge strings of `probes/decode-cases.py`, each with the code points Python gives, written into the test as literal arrays); `decode_keeps_valid_text` (`"a«é»😀\n"`'s UTF-8 bytes give the text back); `encode_gives_the_bytes_back` (each edge string through `decodeStored` and `encodeStored` gives its bytes); `encode_refuses_other_lone_surrogates` (`"\ud83d"` throws the `ValueError` with Python's message, and `"a\udc7f"` with position 1); `content_hash_of_escaped_bytes_is_the_hash_of_the_bytes` (`contentHash(decodeStored(Uint8Array.of(0xff, 0x0a)))` is `e4688624e5f1`, and of the bytes `a\r\nb\xc3\n` is `32094bb12f0c`, Python's `hashlib.sha256(...).hexdigest()[:12]` of `b"\xff\n"` and `b"a\nb\xc3\n"`); `undecodable_record_is_problem_1` (a record file whose bytes hold `\xff`, decoded with `decodeStored` and loaded with `load`, gives problem 1 at its path, as `tests/core/test_fileformat_text.py`'s `bad_utf8_is_problem_1` does for the synthetic surrogate); `zero_two_store_checks_clean` (`checkState` of `load` of the store's `lodge/` files, with the settings of its `.lodge.toml` parsed by `Bun.TOML.parse` and `parseCoreSettings`, finds no problem, as lodge 0.2's `lodge check` printed `ok`, probe 6).
- [ ] **Step 2: Run** `cd ts && bun test tests/core/stored-bytes.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 3: Running git and reading a lodge 0.2 store

**Files:**
- Create: `ts/src/git/index.ts`, `ts/src/git/run.ts`, `ts/src/git/read-store.ts`, `ts/src/git/paths.ts`, `ts/tests/git/isolated.ts`, `ts/tests/git/repos.ts`, `ts/tests/git/zero-two.ts`
- Modify: `ts/package.json` (`"#git": "./src/git/index.ts"` in `imports`), `ts/tests/parity.json` (two rows)
- Test: `ts/tests/git/run.test.ts`, `ts/tests/git/read-store.test.ts`, `ts/tests/git/paths.test.ts` (new)

**Interfaces:**
- Consumes: Task 2's `decodeStored`; `#app`'s `LodgeError`; `#core`'s `Tree`, `tree`, `ATTACHMENTS`.
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
  export interface StoreCopy {
    readonly rev: string                                   // the commit read
    readonly tree: Tree                                    // every file under lodge/ but the attachments, and the attachments' paths
    readonly attachmentTexts: ReadonlyMap<string, string>  // each attachment's text, by path
    readonly settings: string | null                       // .lodge.toml at that commit, as text
  }
  export function readStore(repository: string, rev: string): Promise<StoreCopy>
  // paths.ts
  export function resolvePath(path: string): string        // Python's Path(path).resolve(): links followed where they exist
  export function repoRootOf(edited: string): Promise<string>
  export function isFolder(path: string): boolean
  ```
- `attempt` spawns `git -C <cwd> <args>` with `Bun.spawn`, `LC_ALL=C` and `GIT_TERMINAL_PROMPT=0` over the process's environment and `env`, standard input closed when there is no `input` and a string `input` encoded with `encodeStored`; a missing `git` program is a `GitMissing`; `runBytes` throws a `LodgeError` with git's first non-empty line of standard error, else of standard output, else `git <args[0]> failed`, as `run_bytes` does; `run` decodes with `decodeStored` and drops the final newlines; `resolveRev` is `resolve` of `git.py`, `rev-parse --verify --quiet --end-of-options <ref>^{commit}`, null on exit 1.
- `readStore` resolves `rev` with `resolveRev` and refuses one that names no commit with `LodgeError("<rev> is not a commit in <repository>")`; lists `ls-tree -r -z --full-tree <commit> -- lodge` and refuses an empty listing with `LodgeError("<rev> holds no lodge/ folder, so it is not a lodge 0.2 store")`; reads every blob in one `cat-file --batch`, as `_contents` of `src/lodge/gitstore/trees.py` does; gives each file outside `lodge/attachments/` its text through `decodeStored` and each entry that is not a blob the empty text, as `read_tree` does; and reads `.lodge.toml` at the commit with `cat-file --batch` too, null when there is none.
  Unlike `read_tree`, it reads the attachments, since the import carries them; an attachment whose `decodeStored` text holds U+DC80 to U+DCFF is not UTF-8, and `readStore` refuses it with `LodgeError("<path>: not UTF-8 text; attachments are text in this version")`, lodge 0.2's message for `--attach` (`src/lodge/cli/commands.py:121`), since a lone surrogate does not survive the events store (probe 2).
- `resolvePath` follows Python's non-strict `resolve`: an absolute path is normalised segment by segment, each existing prefix with `realpathSync` and the rest appended, `..` taken after the links before it are followed; it lives in `git` because `hook` may not read the file system (d-x6f9za).
- `repoRootOf(edited)` is `rev-parse --show-toplevel` in the nearest existing folder at or above `edited` (`_existing_folder` and `_hook_context` of `src/lodge/main.py:62-78`), and a folder outside any repository is a `LodgeError("<folder> is not inside a git repository")`, as `repo_root` says it.
- `isolated.ts` exports `isolateGit()`, which registers `beforeEach` and `afterEach` hooks setting and restoring the variables of `tests/gitstore/conftest.py`'s `isolated_git`, the identity `Test Author <test@example.com>` included, and deleting `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, and `GIT_COMMON_DIR` for the test.
- `repos.ts` carries `git`, `bareRemote`, `clone`, `seeded`, `worktree`, `commit`, and `write` of `tests/gitstore/repos.py`, each over a folder from `mkdtempSync`; the rest of that file builds lodge 0.2's git store and has no counterpart.
- `zero-two.ts` exports `zeroTwoRepository(layout: "checkout" | "branch"): Promise<{ repository: string; rev: string }>`, which commits Task 2's `ZERO_TWO_STORE` into a new repository, on `main` for `checkout` and on an orphan branch `lodge` holding only `lodge/` for `branch`, with `.lodge.toml` on `main` in both.

- [ ] **Step 1: Write the failing tests.**
  - `run.test.ts`: `missing_git_is_one_sentence` (with `PATH` emptied for the call, `attempt` throws a `GitMissing` with its message); `failure_names_gits_first_line` (`runBytes(["rev-parse", "--verify", "nope"])` throws a `LodgeError` whose message is git's first line); `resolve_rev_gives_null_for_a_missing_ref`; `resolve_rev_refuses_an_option` (`resolveRev(repo, "--output=x")` gives null and writes no file named `x`, since `--end-of-options` comes first); `input_reaches_git` (`hash-object --stdin` of `"a\n"` gives `78981922613b2afb6025042ff6bd878ac1994e85`).
  - `read-store.test.ts`: `reads_the_checkout_layout` and `reads_the_branch_layout` (`readStore` of `zeroTwoRepository(...)` gives every file of `ZERO_TWO_STORE` under `lodge/` but the attachment in `tree.files`, the attachment's path in `tree.attachments` and its text in `attachmentTexts`, `.lodge.toml`'s text in `settings`, and the commit in `rev`); `revision_that_is_no_commit_is_refused`; `revision_without_lodge_is_refused` (the `main` of the branch layout); `undecodable_record_reads_as_escapes` (a decision with a `\xff` byte reads with U+DCFF, and `load` of the tree gives problem 1); `undecodable_attachment_is_refused`; `symbolic_link_reads_as_its_target` (a link committed under `lodge/` reads as its target's text, as `read_tree` reads a blob of mode 120000); `settings_absent_is_null`.
  - `paths.test.ts`: `resolve_follows_links` (`tests/hook/test_post_tool_use.py`'s `test_symlinked_checkout_still_matches` layout); `resolve_takes_dot_dot_through_missing_folders` (`<tmp>/docs/../lodge/decisions/d.md` with no `docs` resolves to `<tmp>/lodge/decisions/d.md`); `repo_root_of_a_file_that_does_not_exist_yet` (as `test_hook_finds_the_repository_for_a_file_that_does_not_exist_yet`); `repo_root_outside_a_repository_is_one_sentence`; `is_folder_says_whether_a_folder_exists`.
- [ ] **Step 2: Run** `cd ts && bun test tests/git`; expected: the new tests FAIL.
- [ ] **Step 3: Implement**; add `#git` to `ts/package.json`'s `imports`; flip `tests/gitstore/conftest.py` to `ported` and `tests/gitstore/repos.py` to `changed` with the `why` of "Parity rows this plan settles".
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 4: The export writer

**Files:**
- Create: `ts/src/git/export.ts`
- Modify: `ts/src/git/index.ts`
- Test: `ts/tests/git/export.test.ts` (new)

**Interfaces:**
- Consumes: Task 3's `run.ts`, `readStore`, and test helpers; Task 7's `ExportTarget` and `ExportOutcome` types of `#app`, or, when Task 7 is not merged yet, the same two types declared in `export.ts` and replaced by `#app`'s in Task 8.
- Produces, through `#git`:
  ```ts
  export function exportStore(target: ExportTarget, files: ReadonlyMap<string, string>, message: string): Promise<ExportOutcome>
  // ExportTarget = { readonly repository: string; readonly branch: string; readonly remote: string | null }
  // ExportOutcome = { readonly kind: "committed"; readonly commit: string } | { readonly kind: "unchanged" } | { readonly kind: "moved" }
  ```
- `exportStore` (d-pv341r):
  1. Refuses a path of `files` outside `lodge/` as `check_writes` of `src/lodge/gitstore/plumbing.py:14-26` refuses it, with its message, and a branch name that is not a name of letters, digits, and `. _ / -` not starting with a symbol, as `_name` of `src/lodge/gitstore/settings.py:76-83` says it.
  2. Finds the tip: with a remote, `ls-remote <remote> refs/heads/<branch>` (`remote_tip`), and when there is one, `fetch --quiet --no-tags <remote> refs/heads/<branch>` so that its commit is local; without one, `resolveRev(repository, "refs/heads/<branch>")`, and a branch that a work tree of the repository has checked out (`worktree list --porcelain` names `branch refs/heads/<branch>`) is refused with `LodgeError("<branch> is checked out in a work tree of <repository>; the export writes only a branch no work tree has checked out")`.
  3. Refuses a tip whose tree holds a path outside `lodge/` (`ls-tree -r --name-only <tip>`), with `LodgeError("<branch> holds files outside lodge/, so it is not a branch lodge exports to; name a branch of its own")`, so the export never writes a project's main branch (design must-not 7).
  4. Builds the tree in a temporary index in a folder from `mkdtempSync`: each text through `encodeStored` into a file there, one `hash-object -w --no-filters --stdin-paths`, one `update-index -z --index-info`, then `write-tree` (probe 4); the folder is removed in a `finally`.
  5. Answers `unchanged` when the tree equals the tip's tree, making no commit.
  6. Commits with `commit-tree <tree> [-p <tip>] -F -`, the author and committer `lodge <lodge@export.invalid>` through `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, `GIT_COMMITTER_NAME`, and `GIT_COMMITTER_EMAIL`, the message ending in one newline.
  7. Moves the branch without force: with a remote, `push --porcelain <remote> <commit>:refs/heads/<branch>`, `moved` when it is refused and `ls-remote` shows another tip, git's first line as a `LodgeError` otherwise (`push` of `plumbing.py:57-79`); without one, `update-ref refs/heads/<branch> <commit> <tip or forty zeros>`, `moved` when the ref moved under it (probe 4).
- No work tree is read or written, so a bare repository is a target.

- [ ] **Step 1: Write the failing tests** in `export.test.ts`, each with `isolateGit()`: `first_export_makes_the_branch` (a bare repository; the branch's tree holds exactly the files, each byte for byte, and the author is `lodge <lodge@export.invalid>`); `same_files_make_no_commit` (`unchanged`, tip unmoved); `changed_file_makes_one_commit_on_the_last` (parent is the previous commit); `removed_file_leaves_the_tree`; `path_outside_lodge_is_refused` (`README.md`, `lodge/../x`, `lodge/.git/x`, each with its message); `branch_with_other_files_is_refused` (`main` of `seeded`); `checked_out_branch_is_refused`; `lodge_zero_two_branch_is_a_target` (the branch layout of `zeroTwoRepository`); `push_without_force` (a work repository with a bare remote: the remote's branch has the commit, the work repository's own branches are unmoved); `moved_remote_branch_answers_moved` (a commit pushed to the remote by another clone between the fetch and the push, staged by pushing from a second clone before the export's push, through a `files` map built after the fetch: the export answers `moved` and a second export builds on the new tip); `exported_store_reads_back` (`readStore` of the exported branch gives the files exported).
- [ ] **Step 2: Run** `cd ts && bun test tests/git/export.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 5: The hook's advice

**Files:**
- Create: `ts/src/hook/index.ts`, `ts/src/hook/post-tool-use.ts`, `ts/src/hook/texts.ts`
- Modify: `ts/package.json` (`"#hook": "./src/hook/index.ts"` in `imports`), `ts/tests/parity.json`
- Test: `ts/tests/hook/post-tool-use.test.ts` (carried, with new tests)

**Interfaces:**
- Consumes: `#app`'s `LodgeError`.
- Produces, through `#hook`, a port of `src/lodge/hook/post_tool_use.py`:
  ```ts
  export interface HookContext {
    readonly repoRoot: string
    readonly dataRoot: string | null      // the folder of the record files; null in branch mode
    readonly frozen: readonly string[]
    readonly server: string | null        // the server's address when the project has moved, else null
  }
  export type Resolve = (path: string) => string
  export interface HookOutput { readonly hookSpecificOutput: { readonly hookEventName: "PostToolUse"; readonly additionalContext: string } }
  export function parseHookSettings(table: unknown): readonly string[]
  export function respond(payload: unknown, context: HookContext, resolve: Resolve, cwd?: string | null): HookOutput | null
  export function run(read: () => Promise<string>, write: (text: string) => void, context: (edited: string) => Promise<HookContext | null>, resolve: Resolve, cwd: string | null): Promise<0>
  ```
- `respond` and `run` keep the Python logic, with `context` and `resolve` given by the caller (Python's `respond` takes the three parts of the context as arguments; the TypeScript one takes them as one object, so a test's `respond(payload(record), tmp_path, data, ())` becomes `respond(payload(record), { repoRoot, dataRoot: data, frozen: [], server: null }, resolvePath)` with `resolvePath` of `#git`).
  `run` reads the event with `read`, writes one JSON line with `write`, and gives 0 whatever fails, as Python's `run` does.
- `texts.ts` holds `RECORD_TEXT`, `THREAD_TEXT`, and `FROZEN_TEXT` as Python's, character for character, and three texts for a moved project, used when `context.server` is not null, `{server}` the address:
  - `MOVED_RECORD_TEXT`: `{path} is a lodge record file from before this project moved to the lodge server at {server}: its records live on the server now, and an edit here changes nothing there. Run \`lodge draft REF\` (or \`lodge draft area:NAME\`) to get the record as a draft, edit the draft, check it with \`lodge add --dry-run FILE\`, then publish it with \`lodge add FILE\`; the command sends both to the server. ` and then `REVERSE`;
  - `MOVED_THREAD_TEXT`: `{path} is a lodge thread file from before this project moved to the lodge server at {server}: its threads live on the server now, and an edit here changes nothing there. Add a message with \`lodge reply Q --by ROLE FILE\`, or close it with \`lodge close Q --by ROLE\`; the command sends both to the server. ` and then `REVERSE`;
  - `MOVED_FROZEN_TEXT`: `{path} is frozen: lodge holds its content now, on the lodge server at {server}, so do not edit it. Record the change as a new decision instead: write a draft (\`lodge guide\` shows the draft format), check it with \`lodge add --dry-run FILE\`, then publish it with \`lodge add FILE\`, which sends it to the server. ` and then `ASKED`, ` Otherwise reverse your own edit now: `, and `RESTORE`.
- For a moved project every file under `<repoRoot>/lodge/` but `lodge/attachments/` gets the moved record or thread text, whatever `dataRoot` says, since the files there are copies from before the move in either store mode (d-va3j7x); a frozen file gets the moved frozen text.
- `parseHookSettings` throws `LodgeError` with Python's three messages.
- Python's `_glob` becomes a pattern built with `new RegExp` and the `u` flag, its escape of each literal character the escape of every character that has a meaning in a JavaScript pattern, and `re.fullmatch` the test of `^(?:p)$`.

- [ ] **Step 1: Write the failing tests:** every test of `tests/hook/test_post_tool_use.py` by name, each parametrised case kept, with `tmp_path` a folder from `mkdtempSync`, and `resolvePath` of `#git` for `resolve` (or, while Task 3 is not merged into this lane, a test-local `resolve` with `realpathSync` and `path.resolve`, replaced by `#git`'s in Task 9); then the new tests:
  `moved_record_edit_names_the_server` (the record text names the server and `lodge draft`, `lodge add --dry-run`, and `lodge add FILE` in that order, and not `lodge/decisions` as a place to edit); `moved_thread_edit_names_reply_and_close`; `moved_frozen_edit_names_the_server`; `moved_project_protects_lodge_in_branch_mode` (`dataRoot` null and `server` set: a file under `lodge/decisions/` gets the moved text); `moved_attachment_edit_gets_nothing`; `moved_advice_reverses_the_edit_without_git` (as `test_record_advice_reverses_the_edit_without_git`, for the three moved texts).
- [ ] **Step 2: Run** `cd ts && bun test tests/hook`; expected: FAIL.
- [ ] **Step 3: Implement**; add `#hook` to `ts/package.json`'s `imports`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 6: Preparing an import

**Files:**
- Create: `ts/src/app/importing.ts`
- Modify: `ts/src/app/index.ts`
- Test: `ts/tests/app/importing.test.ts` (new)

**Interfaces:**
- Consumes: `#core`'s `Tree`, `load`, `checkState`, `parseRecord`, `writeRecord`, `CoreSettings`, `Problem`, `ATTACHMENTS`.
- Produces, through `#app`:
  ```ts
  export interface ImportSource { readonly tree: Tree; readonly attachmentTexts: ReadonlyMap<string, string> }
  export interface PreparedImport {
    readonly problems: readonly Problem[]          // what lodge 0.2's check finds in the store; nothing is imported unless empty
    readonly files: ReadonlyMap<string, string>    // every record, area, thread, and attachment to write, by path, mapped
    readonly mapped: readonly string[]             // the decisions whose decided_by became the owner, by ID
  }
  export function prepareImport(source: ImportSource, owner: string, settings: CoreSettings): PreparedImport
  ```
- `prepareImport` (d-ag8p8h, d-bh93bn):
  1. Checks the store as lodge 0.2 checks its published state: `checkState(load(source.tree), settings)`, with the settings of the store's own `.lodge.toml`, so a record imported from a source that file does not list fails as it does in 0.2 (`tests/e2e/test_add_import.py`); any problem ends here, with `files` empty.
  2. Maps each decision whose `decidedBy` is `author` to `owner`: its new text is `writeRecord` of the decision with `decidedBy: owner`, and the decision is refused, as a problem of check 1 at its path with the message `lodge 0.2 did not write this file as it writes records, so the importer cannot change its decided_by alone`, when `writeRecord` of the unchanged decision does not give its text byte for byte.
  3. Gives every other file of the tree unchanged, but the paths ending `/.gitkeep`, which `load` skips (`src/lodge/core/snapshot.py:68`) and the export writes back (Task 7), and each attachment's text from `attachmentTexts`.
  Thread messages keep `by: author`, and nothing but `decided_by` changes, as design line 78 and this plan's end both say.
- `owner` is the person as plan 2's model writes a person in `decided_by`; an `owner` that `writeRecord` refuses, or that holds `author` in any case, is a `LodgeError` naming it, since lodge 0.2's check 3 reads such a `decided_by` as a misspelt author (`src/lodge/core/check_state.py:124-128`).

- [ ] **Step 1: Write the failing tests** in `importing.test.ts`, over Task 2's `ZERO_TWO_STORE` with the made-up owner `ana`: `clean_store_prepares_every_file` (nine files: four decisions, one entry, one area, one thread, one attachment, and no `.gitkeep`; `problems` empty); `author_decisions_name_the_owner` (the three author decisions, the imported one included, now have `decided_by: <owner>`, and each mapped text differs from the original in that line only); `agent_decision_is_unchanged`; `thread_keeps_by_author`; `ids_dates_codes_and_imported_from_are_kept` (each mapped decision parses with the same `id`, `date`, `code`, and `importedFrom`); `failing_store_prepares_nothing` (the store with its `[import]` sources emptied gives lodge 0.2's check problem for the imported decision, and `files` empty); `stray_file_fails_the_check` (a `lodge/notes.txt` gives the stray-file problem); `file_the_writer_would_not_give_back_is_refused` (an author decision with its keys in another order); `owner_naming_author_is_refused`.
- [ ] **Step 2: Run** `cd ts && bun test tests/app/importing.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 7: The export's files and its batching

**Files:**
- Create: `ts/src/app/exporting.ts`
- Modify: `ts/src/app/index.ts`
- Test: `ts/tests/app/exporting.test.ts` (new)

**Interfaces:**
- Consumes: `#core`'s `Tree`, `instant`; plan 2's clock port.
- Produces, through `#app`:
  ```ts
  export interface ExportTarget { readonly repository: string; readonly branch: string; readonly remote: string | null }
  export type ExportOutcome = { readonly kind: "committed"; readonly commit: string } | { readonly kind: "unchanged" } | { readonly kind: "moved" }
  export interface Timer { after(seconds: number, run: () => void): void }
  export interface ExportPorts {
    readonly clock: Clock                                                         // plan 2's port
    readonly timer: Timer
    readonly target: () => Promise<ExportTarget | null>
    readonly current: () => Promise<ImportSource>                                 // the state's files and attachment texts
    readonly write: (target: ExportTarget, files: ReadonlyMap<string, string>, message: string) => Promise<ExportOutcome>
    readonly failed: (error: unknown) => void                                     // the server logs it
  }
  export const EXPORT_INTERVAL_SECONDS = 60
  export const KEPT: readonly string[]                                            // lodge/decisions/.gitkeep, lodge/spec/.gitkeep
  export function exportFiles(source: ImportSource): ReadonlyMap<string, string>
  export function exportMessage(files: ReadonlyMap<string, string>): string
  export class Exporter { constructor(ports: ExportPorts); written(): void; flush(): Promise<ExportOutcome | null> }
  ```
- `exportFiles` gives every file of the tree but the `/.gitkeep` paths, each attachment's text, and `KEPT` with the empty text, as `lodge init` lays a store out (`src/lodge/gitstore/trees.py:10`, `src/lodge/gitstore/setup.py:47-56`), so the export is a lodge 0.2 store in either layout (d-srfxj8).
- `exportMessage` is `Export lodge records: <d> decisions, <e> entries, <a> areas, <t> threads`, counted from the paths.
- `Exporter` (design line 285; d-srfxj8):
  - `written()` notes that a write happened; when no export is scheduled, it schedules one with `timer.after(wait)`, `wait` being 0 when no commit was made yet or the last one is `EXPORT_INTERVAL_SECONDS` or more ago by `clock.now()`, and otherwise the rest of that interval; further writes before it runs schedule nothing, so they go out together.
  - The scheduled run calls `flush()`: with no target, it does nothing; otherwise it writes `exportFiles(await current())` with `exportMessage`, and on `committed` notes the commit's time; on `moved`, or when `write` throws (handed to `failed`), it schedules another run `EXPORT_INTERVAL_SECONDS` later; on `unchanged` it notes nothing.
  - So two commits are at least a minute apart, and a write is exported within a minute of the last commit.
  - Times are read only from `clock.now()` and compared with `instant` of `#core`, and the waiting is the `Timer` port's, since `app` may use neither (`CLAUDE.md`, "Structure checks").

- [ ] **Step 1: Write the failing tests** in `exporting.test.ts`, with a fake clock that stands still until advanced and a fake timer that records each `after` and runs it on demand: `export_files_hold_the_store_and_kept` (the made-up store's files, its attachment, and both `.gitkeep`, nothing else); `message_counts_the_records`; `first_write_exports_at_once` (one `after(0, …)`); `writes_within_a_minute_batch_into_one_commit` (a commit, then three writes at 10, 20, and 30 seconds: one run scheduled at 60 seconds after the commit, one more `write` call); `write_a_minute_after_exports_at_once`; `no_target_writes_nothing`; `unchanged_counts_no_commit` (after `unchanged`, the next write exports at once); `moved_retries_a_minute_later`; `failure_is_reported_and_retried` (`failed` gets the error, and a run is scheduled 60 seconds later); `no_write_no_export` (nothing scheduled without `written`).
- [ ] **Step 2: Run** `cd ts && bun test tests/app/exporting.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 8: Import and export in the server

**Files:**
- Modify: OPS-PENDING (plan 3's operation table in `api`), `ts/src/main.ts` or plan 3's server entry, `ts/src/app/index.ts` (the import operation), `ts/src/git/export.ts` (the types from `#app`, if Task 4 declared its own)
- Test: `ts/tests/api/import.test.ts`, `ts/tests/api/export-target.test.ts` (new)

**Interfaces:**
- Consumes: Tasks 3, 4, 6, and 7; plan 2's store and model; plan 3's handler, sign-in, and test helpers.
- Produces: the operations `import` and `export-target` of `POST /api/v1/<operation>` (d-sry12f), and the server's exporter.
- `import`, the body `{"repository": string, "rev": string}` (d-1skjw1, d-ag8p8h):
  - only the signed-in person, by the session cookie: an agent's bearer token answers `forbidden` (403), since the import writes decisions in a person's name, which only that person may do (SRV-2, design line 75);
  - the server reads the repository on its own machine with `readStore`, parses `settings` with plan 3's reader of `.lodge.toml` into `CoreSettings`, and calls `prepareImport` with the project's first owner;
  - a project that holds any record answers `conflict` (409), `Conflict("the project already holds records; lodge imports a store into an empty project only")`;
  - problems answer `check-failed` (422) with the problems, as `add` does;
  - otherwise it writes the project's core settings from the store's `.lodge.toml` and every file of `files` as events in one write of plan 2's store, through plan 2's check on every write, and answers `{"rev": …, "decisions": n, "entries": n, "areas": n, "threads": n, "attachments": n, "mapped": [ids]}`.
- `export-target`, the body `{"target": {"repository": string, "branch": string, "remote": string | null} | null}`: only the signed-in person, likewise; it stores the target as plan 2's project setting event, `null` stopping the export, and answers the target stored.
- The server's composition root builds one `Exporter` per project with `exportStore` of `#git` as `write`, a `Timer` over `setTimeout`, plan 2's clock, and plan 2's reading of the current state, calls `written()` after every write that changes the project's records (WRITE-HOOK-PENDING), and `flush()`es once on start, so a server that stopped with writes pending exports them.

- [ ] **Step 1: Write the failing tests**, each calling the handler with a `Request` and no socket (plan 3's helpers):
  - `import.test.ts`: `person_imports_the_made_up_store` (both layouts of `zeroTwoRepository`: the answer's counts, and `show` of each author decision names the owner); `agent_token_is_forbidden`; `second_import_is_a_conflict`; `failing_store_answers_check_failed` (nothing written); `missing_revision_is_usage`; `imported_records_read_as_imported` (`show` of the imported decision says imported and unquoted, as `test_import_needs_the_flag_and_a_listed_source` asserts in lodge 0.2).
  - `export-target.test.ts`: `person_sets_the_target`; `agent_token_is_forbidden`; `write_after_target_exports` (a fake timer: after the person sets the target and an agent's `add`, the branch of a bare repository holds the new decision); `null_target_stops_the_export`.
- [ ] **Step 2: Run** `cd ts && bun test tests/api/import.test.ts tests/api/export-target.test.ts`; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 9: The hook in the command

**Files:**
- Modify: CLI-PENDING (plan 3's parser and command dispatch), `ts/src/main.ts` or plan 3's command entry, `ts/tests/parity.json`, plan 3's `help-lists-every-command.test.ts` (`hook` listed)
- Test: `ts/tests/hook/hand-edits.test.ts`, `ts/tests/hook/outside-repository.test.ts` (carried)

**Interfaces:**
- Consumes: Task 5's `#hook`; Task 3's `repoRootOf`, `isFolder`, and `resolvePath`; plan 3's command, its reader of `.lodge.toml`, and its test project.
- Produces: `lodge hook post-tool-use`, answering as lodge 0.2's does, with the moved advice.
- The command's composition root builds the hook's context for an edited file as `_hook_context` does (`src/lodge/main.py:73-78`): `repoRootOf(edited)`; `.lodge.toml` at that root through plan 3's reader; `[store] mode`, `"checkout"` when absent; for checkout mode `dataRoot` is `<root>/lodge` and the context is null unless `<root>/lodge/decisions` and `<root>/lodge/spec` are folders (`holds_records`); for branch mode `dataRoot` is null; `frozen` from `parseHookSettings` of `[hook]`; `server` from SERVER-KEY-PENDING; any error makes the context null, so the hook stays silent.
  A `[store]` value other than `mode` is not read, where lodge 0.2's hook falls silent on a malformed one, since the server's command has no git store to configure; the report lists this as a known difference.
- Every other command validates `[hook]` with `parseHookSettings`, as `_settings` does (`src/lodge/main.py:41-45`), so a malformed `[hook]` exits 2 with one sentence.
- The carried tests build lodge 0.2's store in the test project by hand (the folders `lodge/decisions` and `lodge/spec`, each with `.gitkeep`), where lodge 0.2's tests run `lodge init`, since the server's `init` names the server instead.

- [ ] **Step 1: Write the failing tests:** every test of `tests/e2e/test_hook_feedback_after_hand_edits.py` and `tests/e2e/test_hook_outside_repository_exit_0_silent.py` by name, each parametrised case kept, through plan 3's test project; and, in `hand-edits.test.ts`, `hook_gives_the_moved_advice_for_a_project_on_the_server` (a `.lodge.toml` naming a server: an edit under `lodge/decisions/` names it).
- [ ] **Step 2: Run** `cd ts && bun test tests/hook`; expected: FAIL.
- [ ] **Step 3: Implement**; flip `tests/e2e/test_hook_outside_repository_exit_0_silent.py` to `ported`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, then `printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"},"cwd":"%s"}' "$PWD/lodge/decisions/x.md" "$PWD" | bun ts/src/<command entry> hook post-tool-use` prints lodge 0.2's record advice for this repository; commit, push.

### Task 10: The round trip

**Files:**
- Create: `ts/tests/e2e/round-trip.test.ts`, `ts/scripts/round-trip.ts`, `scripts/round-trip.sh`
- Modify: `ts/tests/parity.test.ts` (the plan 4 rows)
- Report: `docs/superpowers/plans/2026-11-02-lodge-server-import/task-10-report.md`

**Interfaces:**
- Consumes: Tasks 3 to 9.
- Produces: the proof of this plan's end, and the coordinator's run on a scratch copy of lodge's own records (d-2jk0mw).
- `round-trip.test.ts`, through the server's handler in process: `made_up_store_survives_import_and_export` (for each layout of `zeroTwoRepository`: the person imports it, sets an export target on a new bare repository, the exporter is flushed, and `readStore` of the exported branch gives the same paths as the original, every text equal byte for byte but the `decided_by: author` line of each author decision, which reads `decided_by: <owner>`, and the same attachment text and settings-independent `.gitkeep` files); `export_of_an_export_is_unchanged` (a second flush answers `unchanged`).
- `parity.test.ts`: `ported_files_exist` also covers `changed` rows of plan 4, and a new `plan_4_changed_rows_keep_every_python_test_name` runs `rowMissing` on them.
- `ts/scripts/round-trip.ts REPOSITORY REV` imports the store at `REV` into an in-process server over an in-memory store, with a made-up owner `ana`, exports it into a new bare repository in a temporary folder, and compares the two stores file by file; it prints the counts of files compared, files equal, files differing only in `decided_by`, and other differences (each path and the first line that differs), and exits 1 on any other difference.
- `scripts/round-trip.sh` clones this repository with `git clone --no-local --quiet` into a temporary folder (d-2jk0mw: a scratch copy, never the live store), runs `bun ts/scripts/round-trip.ts <clone> HEAD`, and then lodge 0.2's `lodge spec` in a checkout of the clone and of the export, comparing the two outputs, and `lodge check` in the export's checkout, whose lines it prints.
- Under design line 78 (the export writes the person), lodge 0.2's check on the export fails check 3 for each confirmation the owner made, and `lodge show` loses its "confirmed by the author" (probe 3); the report lists those lines as the expected effect, and the author's answer to IMP-1 (`questions.md`) decides whether they stay.

- [ ] **Step 1: Write the failing test and the scripts.**
- [ ] **Step 2: Run** `cd ts && bun test tests/e2e/round-trip.test.ts tests/parity.test.ts`; expected: the round trip passes once Tasks 3 to 9 are merged, and any failure is fixed in the module at fault with a test that fails first.
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
- The decision for The model (design lines 64 to 94) edits s-07ar34 (lodge 0.2 has no server; the server of the design exists from build step 1, d-8kasej), s-z1zvb4 (lodge 0.2's records are Markdown files in git; on the server they are events in one SQLite table, each holding the file's path and text, d-d3js00, d-smx3xf), and s-j8tp0n (for a project on lodge 0.2 the files in git are the source of truth; for a project on the server its events are, and the export is a one-way copy), and narrows d-cg3nn3 and d-a3e8kb.
- The decisions for Export to git (lines 280 to 285) and Moving from lodge 0.2 (lines 287 to 290) create their entries from what Tasks 3 to 10 built: the branch holding only `lodge/`, the one commit a minute, the person mapping and IMP-1's answer, the import into an empty project by the person, and the hook's moved advice.

**Task 11b: Intent, Goals, Non-goals, Must nots, Workflow as data, and Tasks** (design lines 8 to 50 and 96 to 176).
- The four must-nots added for the server (lines 47 to 50) go into `purpose` beside the first design's three, each its own entry.

**Task 11c: Sessions, Artefacts, the waiting list, Claimed and checked, Usage, Code and git, People and sign-in, Interface, Build order, Open, and Left to the builder** (design lines 178 to 317); then the document is frozen.
- Left to the builder (lines 311 to 317) becomes one entry in `rollout` naming what the design leaves open, each item with the decision that settled it where one has (d-sry12f, d-yayhct, d-4k9wcr, and the workflow's syntax still open).
- The report closes with every design line from 8 to 317 mapped to an entry or named as left out, with the reason.
- Then the design document gets its last line first, "Its content now lives in lodge (`lodge spec`, `lodge show`); this document is frozen."; only then does `.lodge.toml`'s `frozen` gain `"docs/superpowers/specs/2026-11-02-lodge-server-design.md"`, so the hook does not fire on that edit; and `CLAUDE.md`'s line naming the two frozen design documents names the three.

- [ ] **Step 1 (each part):** drafts of the new and edited entries, new areas, and the decisions; dry-run; add; the "changed since" pass.
- [ ] **Step 2: Verify (each part)** `uv run lodge check` prints `ok`; `uv run lodge spec | grep -c 'changed since'` prints 0, or the report names each remaining mark and why; in 11a, `uv run lodge show s-a4jfp1` names TypeScript and `uv run lodge show s-07ar34` no longer says there is no server; in 11c, `printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"},"cwd":"%s"}' "$PWD/docs/superpowers/specs/2026-11-02-lodge-server-design.md" "$PWD" | uv run --frozen --quiet lodge hook post-tool-use` prints the frozen-file advice.
- [ ] **Step 3: Coordinator (each part):** `git add lodge/` and the part's other files, `sh scripts/check.sh`, commit, push.
