# lodge at scale: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** an agent's reads through lodge are cheap and fast at 160,000 record files: the superlinear steps go, headers parse with libyaml where that is provably the same, identical states are not compared, reads batch several refs and queries and treat codes as codes, and a local SQLite index answers a read of a seen state in at most 0.3 s on native disk, and a search with more than 5,000 candidates in at most 1.0 s (d-hxmdkz).

**Architecture:** `core` gains linear checks and traversals, one `derive` per snapshot, a guarded C loader, a per-file parse and an assembly from parses, a plain-value codec, the new search ranking, and code families.
`app` gains the identical-state shortcut, multi-ref and multi-query reads, an `Index` port, and a read path that answers `show`, `search`, `waiting`, `threads`, and `thread` from stored rows.
`Store.trees()` stays and every `Tree` carries the blob ID of each file, hashed by lodge from the bytes it read; the five indexed reads alone use a new fast identity and listing that `gitstore` computes from git and a folder-signature cache (d-7e8zhd).
`gitstore` holds the SQLite index in new modules; the command line gains `show REF...`, `search Q...`, `search --phrase`, and `guide --read`; `scripts/` gains the read-replay benchmark.

**Tech stack:** Python 3.12 or later, uv, PyYAML (with libyaml where present), pytest, mypy (strict), Ruff, Vulture; the standard library's `sqlite3` (FTS5 where present), `json`, `hashlib`, `gc` (in `main.py` only), and `subprocess` (in `gitstore` only).

**Spec:** `lodge spec`, with the coordinator's rulings for this plan recorded as d-1bww1r (correctness first), d-1ftgg3 (speed order), d-232gxs (the index and its targets), d-3g6ard (leaner reads), d-542m5g (benchmarks), and for the first fix round d-q051s2, d-q0tb8r, d-rs76ks, d-rvf532, d-ty4dks, d-vmpspc, and d-ytf272, for the second fix round d-hxmdkz (broad searches), for the third d-t3afj1 (the index's consistency, replacing d-6hb3yd), and for the fourth d-e3stjn (one file per build, cleared in place).
The brief is `docs/superpowers/plans/2026-10-31-lodge-at-scale/brief.md`; the planner's probes and their output are in `docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-report.md` and `probes/`; the reviews and what this plan changed for each finding are in the same folder (`plan-review-*.md`, `plan-recheck-*.md`, `plan-fix-1.md`, `plan-fix-2.md`, `plan-fix-3.md`, `plan-fix-4.md`, `plan-fix-5.md`, and `plan-fix-6/`, which holds plan fixes 6, 6b, and 7b with Codex's reviews of them; plan fixes 6 and 7 were withdrawn, 6b and 7b replace them).
The plan argues from them, never over them; where `lodge spec` and a task disagree, the spec wins and the builder reports it.

## Global Constraints

- One brief per task; the builder sees its brief, `CLAUDE.md`, and the repository.
- Step 0 of every task that adds or moves an interface is a skeleton: the new modules with their signatures, `...` bodies in protocols and `raise NotImplementedError` in concrete functions (strict mypy refuses an empty body that returns a value), the front doors updated, then `uv run pytest tests/test_structure.py -q` and `uv run mypy` green before any test is written (the feasibility review's F7: a cycle or a past-the-front-door import is found before the code).
- Test-first: each named test is written and seen failing before its code; every existing test keeps passing, edited only where a task says so, each edit listed in the task report.
- The gate after every task: `sh scripts/check.sh` green (ruff format, ruff, mypy strict, vulture, pytest, `lodge check --gate`); then stage with explicit paths, commit with `git -c user.name="Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, the message ending `Co-Authored-By: Claude <noreply@anthropic.com>`, and push `read-speed` to `origin`; never `main`.
- Correctness first (d-1bww1r): no task changes a check's result, a problem's wording, or what the gate compares, except where it records a product decision with a spec edit.
- The gate and `add` (and every command but the five indexed reads) read exact trees: every working-tree file read and hashed by lodge, committed trees by git's object IDs; they never take derived state, flags, or tree claims from the index, and use only its parse cache, keyed by those hashes (d-q0tb8r, d-7e8zhd).
- An indexed read prints exactly what the in-memory read prints; where the index cannot prove it, the read takes the in-memory path (d-rs76ks).
- The index's invariants (d-t3afj1, d-4j98ph, d-gvz66f, d-e3stjn, d-c6cegr, d-a8gkrh), which every task from Task 9 on keeps and tests by fault injection:
  1. A parse unit (a parse row and, from Task 10b, the FTS words row with the same rowid) and a state's facts are content-addressed by their key and immutable: inserted once with `INSERT OR IGNORE`, never updated, and never deleted except by a clear of the whole index (invariant 4); so no reference counting, and no unit or fact can vanish under a kept state.
     Bucket blobs are content-addressed and immutable while referenced; states share identical blobs through per-state pointers.
     Eviction deletes only the evicted state's pointers, then unreferenced bucket blobs, in the same transaction (the Task 10a fix-round coordinator ruling).
  2. A state owns only its own rows: its state row and its rows in the per-state tables (buckets, answers, citers), all keyed by the state's key; one write transaction writes the parse units and facts it needs that are absent, then its own rows, and last its state row, the completeness marker; re-keeping a key replaces its own rows whole in one write transaction, and the state becomes the newest.
  3. Evicting a state deletes its own rows by its key, and bucket blobs with no remaining kept-state pointer, in the transaction that keeps the new state; FTS rows are never deleted, so no deletion by anything but rowid exists.
  4. Growth is bounded by `INDEX_FILE_CAP` (Task 9); past it the writer that notices clears the index in place, the rows of every table but `meta` in one `BEGIN IMMEDIATE` transaction that also raises `meta.epoch` (1 when the file is created, so it never repeats within a file); WAL readers finish on their snapshot; the file is never swapped, renamed, or vacuumed on a read; states then rebuild lazily as cold reads (d-e3stjn); a build reads `Index.epoch()` once before its first lookup, and a `keep_state` that finds, inside its write transaction, another epoch than that one writes every parse unit and fact the build used (d-c6cegr; the fourth recheck's W1).
  5. Connections run with `isolation_level=None` in WAL mode; every read runs inside one explicit `BEGIN` ... `COMMIT` (or `ROLLBACK`, in a `finally`), so one read sees one snapshot, and every write inside `BEGIN IMMEDIATE` ... `COMMIT`.
  6. Every cached value carries the key of its inputs (a parse its path and blob; a folder signature its stat and base), and a different key is a miss; a reader treats anything missing, undecodable, or short of what the state row promised as a miss, ends its transaction, and runs the whole read in memory.
- Structure (`tests/structure_rules.py`, `tests/structure_tables.py`): allowed imports as `ALLOWED`, no new package and no new edge (d-5zqvxb); front doors only; no cycles, `TYPE_CHECKING` imports included; no module over 300 lines, tests included; `core` imports only `CORE_MODULES`; `sqlite3` only in `gitstore`, and `marshal`, `pickle`, and `shelve` nowhere (`tests/structure_imports.py`, the Task 9 review's I2); `subprocess` only in `gitstore`; file I/O only in `gitstore` and `cli`.
- Shared value types live in leaf modules, so no two modules import each other: `core/filters.py` (`Filters`), `core/listing.py` (`Listing`, `blob_id`), `app/index_types.py` (`FileKey`, `Row`, `StoredState`, `StateFacts`); `app/__init__.py` exports every type `gitstore` consumes (`Index`, `FileKey`, `Row`, `StoredState`, `StateFacts`).
- `core` and `app` read no clock and no randomness; the time comes from `Clock`.
- Modules near the limit take no new code beyond the lines a task states: `core/apply.py` (277 lines), `gitstore/checkout.py` (267), `core/views.py` (245), `core/derive.py` (243), `cli/parser.py` (236), `app/writes.py` (214), `core/feedback.py` (209); new code goes in the new modules each task names.
- Tests near the limit take no new tests: `tests/gitstore/test_branch.py` (298), `tests/app/test_reads.py` (282), `tests/core/test_derive.py` (273), `tests/gitstore/test_checkout_safety.py` (240); new tests go in the new files each task names, marked "(new)", with basenames unique across `tests/`, `tests/core/`, `tests/app/`, and `tests/gitstore/`.
- Vulture scans `src` and `tests`; every produced name is read in the task that adds it.
- Tests never touch a real repository: git only in `tmp_path` through the existing helpers (`tests/gitstore/repos.py`, `tests/e2e/conftest.py`), no network; from Task 8b on those helpers also set `HOME` and `XDG_CONFIG_HOME` to the test's folder, so no developer's attributes or configuration reach a test (d-dqpf59); fixtures are a made-up project, never another project's records.
- Benchmarks run on native disk under `/var/tmp/lodge-bench/` with stores from `scripts/bench_store.py`; timings in a task report give the command, the store, and best of three; never a timing assertion in pytest.
- Timing claims compare like with like: the same Python, a native-disk virtual environment with its bytecode compiled (`python -m compileall`), and the store on native disk; a FUSE-mounted disk is reported apart when used.
- Records only through `lodge add`; drafts under `.drafts/`; `lodge add --dry-run` before every `lodge add`; product decisions have `scope: product`, `decided_by: coordinator` unless the coordinator says otherwise, and `work_item` this plan; a number in a statement or reasoning gets a `numbers` handle unless it is a label.
- User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line.

## Calls made

Each is recorded in lodge as a process decision with its reasoning, handles, and cost if wrong; a task repeats what it needs.

1. d-5xhxh1: leaner reads (Tasks 5 to 7) come before the index (Tasks 8a to 11), after the four speed tasks, because the index's search only feeds core's ranking.
2. d-5zqvxb: the index lives in `gitstore` as new modules behind an `Index` port in `app`.
3. d-8kq2nk, with d-ana6c0, d-c0q20c, d-c5a1y4, d-dqpf59, and d-n6tqzq: the fast identity of a checkout is the `HEAD` tree of `lodge/` when nothing differs on disk, else a hash of it and the overlay; the overlay holds what `git diff-index --cached` and `git diff-files` name (run with git's stat shortcuts off), the entries flagged assume-unchanged or skip-worktree, the paths git may convert, and the files `HEAD` lacks; each is read and hashed, and dropped when its bytes equal the base's; equal identities imply equal exact trees, not the reverse, and the identical-state shortcut compares listings (d-c0q20c); flag and conversion results are cached in the process only, keyed before and after the git call (d-n6tqzq).
4. d-atsx8n with d-dqpf59 and d-9r24jc: a path git may convert is read from disk; the conversion sources come from git (`git var GIT_ATTR_GLOBAL` and `git var GIT_ATTR_SYSTEM`, one call each, `core.attributesFile`, `info/attributes`, every `.gitattributes` on disk or in git's index), the `crlf` attribute counts, and `core.autocrlf` in any of git's spellings of true, or `input`, makes every path convert.
5. d-c400w8 with d-4j98ph: the parse cache is keyed by path and blob ID, stores `marshal` of plain values, never `pickle`, and its units are immutable, the words row sharing the parse row's rowid; as built, Task 9 stores compact JSON instead, since `marshal` is banned (the Task 9 review's I2).
6. d-c4w7xy: a state's rows hold the derived facts only, in 1,024 buckets by the last two characters of the ID.
7. d-eby5pb, narrowed by d-emtwbs: FTS5 over core's own words with the `ascii` tokenizer gives candidates; core ranks; without FTS5, and for a phrase or code with no word outside the function words, search runs in memory.
8. d-faakge (replacing d-f3r5aq) and d-rvf532: one index file per digest of lodge's source bytes, the Python, PyYAML, libyaml, and SQLite versions, and the schema number; a state's result is keyed by the core settings too, and is valid over the interval between the latest new decision dated before its build and the earliest dated after it.
9. d-hf2fms, d-ytf272, and d-gvz66f: `KEPT_STATES = 4`, one constant, first in first out by the order of keeping, a re-kept state counting as the newest; a read of a seen state writes nothing.
10. d-kj554d with d-her016, d-4n5tr6, d-gvz66f, d-e3stjn, and d-c6cegr: an unwritable index is opened read-only or skipped; only `SQLITE_CORRUPT` and `SQLITE_NOTADB` delete and rebuild; WAL mode with `synchronous=NORMAL`; a state is written in one `BEGIN IMMEDIATE` transaction with its eviction and read in one explicit read transaction; one file per build, cleared in place past the cap, and other builds' files deleted only after 7 days unwritten and under an exclusive lock (d-e3stjn, d-c6cegr); output never changes and a read never fails.
11. d-m0g9tx with d-7e8zhd: stored rows and the fast identity serve `show`, `search`, `waiting`, `threads`, and `thread`; every other command reads exact trees and builds the snapshot in memory from the parse cache.
12. d-n9w4by, narrowed by d-4j98ph: a query is a code when it is one token of the code grammar with a non-empty family in the state; citers are records whose title or statement holds the code among `core.code_tokens`, stored per state for every code and every family root; `show` lists ten siblings and ten citers at most.
13. d-emtwbs and d-ty4dks: `--phrase "words"` gives a phrase, matched as a contiguous run of word tokens with function words kept; a multi-word argument is all its words.
14. d-p60ka9: brief lines drop ` · current` under the default status filter, with a first line saying so.
15. d-s2ypth: every command but `view` runs with the cyclic collector off, when `main` runs as the program.
16. d-zyqzkg: identical states skip `check_change`, by the proof in Task 4.
17. d-q051s2: the C loader parses only headers a guard admits as the writer's shapes.
18. d-dxqxsn with d-4j98ph: each state's own statuses and `check_state` problems are stored by its identity alone, immutable, for a later change check.
19. d-me8vm3, narrowed by d-gd00c6 and d-hxmdkz: searches with more than 5,000 candidates are measured apart, with their own stop at 1.0 s warm at 160,000 files; the 0.3 s stop covers `show`, `waiting`, `threads`, `thread`, and searches with at most 5,000 candidates.
20. d-26e6zj: the stop on missed targets applies after Task 11.
21. d-t3afj1 (replacing d-6hb3yd), d-4j98ph (replacing d-aej8rs), d-gvz66f (its generations replaced by d-e3stjn), and d-c6cegr: the index's invariants of the Global Constraints.
22. R11-A or R11-B (proposed, for the coordinator; one of them): whether the fast identity reads every file on every read (exact; R11-A), or, with no conversion source present, takes stat-clean files at git's index blob as `git status` does (R11-B); Task 8c carries the one ruled.
23. CONV-1 (proposed, records the coordinator's ruling 4, narrows d-232gxs): where a conversion source is present the identity reads every file it may convert (d-dqpf59); that configuration is reported beside the targets, not under them; the stop (d-26e6zj) applies to the configuration without conversions.
24. FOLD-1 (proposed, narrows d-8kq2nk): a folder row holds the folder's difference from the base tree, keyed by the base tree's ID and taken with `lstat`, so a hit takes none of the base's names and never follows a link (Task 11).
25. SECOND-1 (proposed, for the coordinator; amends d-c4w7xy's keeping of a state with every build): a read keeps a state only the second time it finds it not kept, and then only after its output is written and flushed; the first read writes a marker and the units it computed (Task 10a, plan fix 7b).

## Expected cost at 160,000 files (estimates from the probes, native disk)

| Read | Today | After Tasks 2 to 4 | After Task 11 |
|---|---|---|---|
| a point read (`show`, `waiting`), seen state, no conversion source | not finished in 900 s on a FUSE disk; natively the phases of `probes/phases.py` sum to 53 s with `_missing` made linear, and today's `_missing` is quadratic (6.7 s at 16,008 files, so about 100 times that at 160,000) | about 14 s: trees 5.5, one load 7.1 (libyaml where the guard admits, which the writer's records all are), `derive` 0.9, `check_state` about 0.5 | about 0.26 s plus the app path and printing, with R11-B: one process measured at 0.273 s best and 0.278 s median doing everything but the app path and printing (Python 0.019, imports 0.123, parser 0.017, the git group 0.066 to 0.072, published tree and flag scan 0.018, folder rows 0.0075, digest and index hit 0.0067), less 0.012 for the parser of the named command; with R11-A about 3.4 s (every file read, 3.148 s) |
| a point read, seen state, `core.autocrlf=input` | as above | as above | about 3.4 s: every file read (identity 3.148 s at 83ef70b) plus the rest; reported beside the targets (CONV-1) |
| a broad search (100,000 candidates) | as above | as above | about 0.7 s, measured apart, against its own 1.0 s stop (d-hxmdkz) |
| after one changed record (checkout, uncommitted), no conversion source | as above | about 25 s (two loads, the change check) | about 4.7 s exact (plan fix 7b: stages 4.713 s with the published facts kept, 6.249 s without, floor 3.214 s), so above the 3 s target; the second read of that state ends later by the complete keep, which Task 10a measures (SECOND-1); Task 12 measures them |
| first read in a clone | as above | as above | about 12 s: parse 7, FTS 1.1, parse cache 1.4, state 2.5 |
| the read that passes `INDEX_FILE_CAP` | not applicable | not applicable | a cold read (as the first read in a clone, less the parses still in memory), since the clearing writer rewrites every unit it used; the reads after it pay only their own misses; reported as cold and not under the changed-read stop (d-e3stjn); the clear itself, a `DELETE` of every table but `meta` and a new FTS table, measured in Task 9 |
| the gate, `add`, `spec`, the viewer | as above | about 14 s | about 4 s: exact trees 2.0 (every working-tree file read), parse cache 0.45, assembly, `derive`, and checks 1.5 |

The changed-record row misses its 3 s target by plan fix 7b's measurement: its stages sum to 4.713 s with the published facts kept, and the stages that run in full whatever is kept (the fixed stages, the parse lookup, `assemble`, `derive`, and `check_state`) to 3.214 s; Task 12 measures it and applies the stop after every optimisation has landed (d-26e6zj).

## Review Focus

1. A read whose printed output differs between the index path, the in-memory path, and today's code on the same store: the differential and property tests of Tasks 4, 8b, 9, 10a, and 10b, and Task 12's replay comparing output byte for byte.
2. A fast identity that misses a change on disk: staged, unstaged, untracked, ignored, deleted, renamed, touched only, reverted, a symbolic link, a non-regular file, a file git converts (global or system attributes, autocrlf in any spelling), an assume-unchanged or skip-worktree entry, a file created in the same second as its folder was listed (Tasks 8b and 11).
3. The gate or `add` taking anything from the index but a parse keyed by bytes lodge hashed (Tasks 8a and 9).
4. A cached result used where its inputs differ: another lodge build or dependency version, other settings, a time outside the state's validity interval (forward or back), a published state that moved.
5. A read that fails, hangs, deletes a healthy index, or writes in a read-only sandbox, with the database locked, or with another process writing (Tasks 9 and 10a).
6. A search result list that differs from the ranking's definition because the index's candidates missed a record (Task 10b's property test, with reverts).
7. A check whose wording or result changed in the linear rewrites of Task 2, or a C-parsed header whose value or problem differs from the Python loader's (Task 3).
8. A state the reader takes whose rows, words, citers, or parses are incomplete or from two builds, after an interrupted write, a concurrent writer, a re-keep, an eviction, or a clear (the fault-injection and snapshot tests of Tasks 9, 10a, and 10b).

---

Build order: Tasks 1 to 7, 8a, 8b, and 9 as built; then Task 8c, Task 9c, Task 10a, Task 10b, Task 10c, Task 11, and Task 12 (plan fixes 6b and 7b); the sections below follow that order.

### Task 1: Benchmarks

**Files:**
- Modify: `scripts/bench_store.py`
- Create: `scripts/bench_reads.py`, `scripts/bench_reads.txt`
- Report: `docs/superpowers/plans/2026-10-31-lodge-at-scale/task-1-report.md`

**Interfaces:**
- Consumes: nothing.
- Produces:
  ```
  uv run --frozen python scripts/bench_reads.py STORE --lodge CMD [--against CMD2] [--runs N] [--commands FILE] [--mode cold|seen|changed]
  ```
  - `CMD` and `CMD2` run a lodge build, such as `/var/tmp/lodge-bench/venv-a/bin/lodge`; each line of `FILE` (default `scripts/bench_reads.txt`) is one lodge argument list in shell syntax, run with `shlex.split`, never through a shell.
  - Placeholders: `{entry}` and `{decision}` the first entry and decision ID in the store's file order, `{code}` the first code with a sibling, `{code2}` the second code found; read from file names and headers, never from lodge's output.
  - Per line and build: best and median wall time of `N` runs (default 3), exit code, output characters, and with `--against` whether standard output and exit status are identical; a Markdown table, one row per line.
  - Modes (the feasibility review's F15): `seen` runs each line once untimed, then times `N` runs; `cold` deletes lodge's index files in the store's git folder (`.git/lodge/`) before each timed run; `changed` prepares a seen index once, saves a copy of `.git/lodge/` aside, and for each timed run of each line restores that copy, writes a distinct edit (the run's number into one entry's statement, on disk, not staged), and times the line; the edits are undone with `git checkout -- lodge` and the copy removed at the end.
  - Builds without an index ignore the cache steps; the table names the mode.
- `scripts/bench_store.py`: its four ruff findings fixed without changing the stores it writes; then, for one coded decision in fifty, a second decision coded `CODE-n.why` and one new entry whose statement cites `CODE-n`, so stores have families and citers; and one entry coded `A`, whose citers are every record holding the token `a` (the feasibility recheck's R2).
- `scripts/bench_reads.txt`: `show {code}`, `show {entry} --reasoning --provenance`, `show {decision}`, `search berth --brief`, `search "berth crane" --brief`, `search {code} --brief`, `search berth`, `waiting`, `threads`, `spec --area area-001`, `check`, and `check --gate` (measured, not targeted); Task 5 adds `show {code} {code2} {entry}` and `show A`, Task 6 adds `search berth tide --brief` and `search --phrase "berth crane" --brief`.

- [ ] **Step 1:** fix the ruff findings; check by rebuilding `s900` to a temporary folder and comparing `git rev-parse HEAD^{tree}` with `/var/tmp/lodge-bench/s900`.
- [ ] **Step 2:** add the families and citers; rebuild `s900`, `s9000`, and `s90000` (about 1,600, 16,000, and 160,000 files) and record their file counts.
- [ ] **Step 3:** write `scripts/bench_reads.py` (no tests: `scripts/` is outside pytest and mypy; `ruff check scripts` clean).
- [ ] **Step 4:** build a native-disk venv of this branch (`uv venv /var/tmp/lodge-bench/venv-base`, `uv pip install .`, `python -m compileall`), and record the `seen` table for `s900` and `s9000`, and for `s90000` one `show {code}` under `timeout 900`, reported as not finished if it is not.
- [ ] **Step 5:** gate, commit, push.

### Task 2: The superlinear steps, iterative traversals, one `derive` per snapshot, and the collector

**Files:**
- Modify: `src/lodge/core/check_change.py` (`_missing`; `_dates` through an index of earlier decisions; the keyword `facts`), `src/lodge/core/check_areas.py`, `src/lodge/core/check_cycles.py`, `src/lodge/core/check_state.py` (the keyword `derived`), `src/lodge/core/check_entries.py` and `_links_to_dead` (statuses from `facts`), `src/lodge/core/derive.py` (at most 20 lines: running pointers replace the prefix scans of `_behind_entry_edits` and `_follows_author_change`), `src/lodge/core/doubts.py` (propagation from the doubted records through reverse dependencies), `src/lodge/core/order.py` (`derived_order` and `rests_on_tree` iterative), `src/lodge/viewer/pages.py` (`_branches` with an explicit stack), `src/lodge/core/__init__.py`, `src/lodge/app/state.py`, `src/lodge/app/reads.py`, `src/lodge/main.py` (`gc.disable()` when `argv is None` and the command is not `view`)
- Create: `docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/shapes.py` (the shape probe of the feasibility review's F4: one entry with many decisions, a long `rests_on` chain without doubts, many new decisions against a large published state)
- Test: `tests/core/test_linear_checks.py` (new), `tests/core/test_linear_derive.py` (new), `tests/core/test_deep_chains.py` (new), `tests/test_collector.py` (new)

**Interfaces:**
- Consumes: nothing.
- Produces:
  ```python
  @dataclass(frozen=True)
  class ChangeFacts:
      """What check_change would otherwise compute from the two snapshots."""
      published_status: Mapping[str, Status]
      published_problems: frozenset[tuple[str, int, str]]   # sort keys of check_state(published)
      after_derived: Derived
      after_problems: tuple[Problem, ...]                     # check_state(after).problems
  def change_facts(published: Snapshot, after: Snapshot) -> ChangeFacts
  def check_change(published, after, settings, now, current=None, *, facts: ChangeFacts | None = None) -> CheckResult
  def check_state(s: Snapshot, *, derived: Derived | None = None) -> CheckResult
  def check_areas(s: Snapshot, status: Mapping[str, Status]) -> Iterator[Problem]
  ```
  `check_change` with `facts=None` computes `change_facts(published, after)` first, so every caller that passes nothing gets today's result; `derive` runs once per snapshot in one checked read.
- `check_areas`: entries grouped by area in one pass; duplicates in an order counted with a dict; the same problems in the same order, wording unchanged.
- `check_cycles`: Tarjan's strongly connected components, iterative, over `rests_on` targets that exist; for each entry in a component of two or more, the other members sorted, exactly as today; a self-link stays check 2's alone.
- `_missing`: the union of the `after` IDs built once.
- `_dates`: earlier decisions indexed by ID and by the entries they change, so each new decision looks only at its `replaces`, `narrows`, `confirms`, and the decisions sharing an entry; the targets visited in sorted order as today, so the problems and their order are unchanged.
- `derive`: for each entry, one pass over its changes oldest first keeps the last change not in `undone` and the last not replaced, so each decision reads its predecessor in constant time.
- `doubt_marks`: the affected set propagated from doubted records through the reverse of `rests_on`; marks and their order as today.
- `derived_order`, `rests_on_tree`, and the viewer's `_branches`: explicit stacks, no recursion; the same output for every graph, `(see above)` marks included.

- [ ] **Step 1: Write the failing tests:**
  `test_linear_checks.py`: `test_missing_builds_the_union_once` (the `after` snapshot's mappings wrapped in a counting `Mapping` whose `keys()` counts calls: at most one per mapping for 2,000 published records, and the one problem as today); `test_check_areas_same_problems_as_before` (each sample of `tests/core/samples.py` and a made-up 50-area snapshot with an entry unlisted, an order naming a retired entry, a duplicate, and a folder without `_area.md`, against a copy of today's function kept in the test file as the oracle); `test_cycles_same_as_reachability` (200 seeded random `rests_on` graphs of 1 to 40 entries against a copy of today's function); `test_dates_same_as_before` (seeded snapshots with 1 to 30 new decisions linking and sharing entries with earlier ones, against a copy of today's `_dates`); `test_check_change_with_facts_equals_without` (the fixtures of `tests/core/test_check_change.py`, and the 50-area snapshot with an edited entry and a new decision).
  `test_linear_derive.py`: `test_derive_same_as_before` (seeded snapshots with author, agent, imported, replaced, confirmed, and retiring decisions, up to 60 changes of one entry, against a copy of today's `derive`); `test_doubt_marks_same_as_before` (seeded graphs with doubts, questions, and none, against a copy of today's `doubt_marks`); `test_derive_once_per_checked_read` (count `derive` calls through `read_checked` on a `MemoryStore` with `staged=True`: 2, one per snapshot).
  `test_deep_chains.py`: `test_chain_of_5000_checks_shows_and_orders` (a 5,000-entry chain in one area: `check_state`, `rests_on_tree` of its last entry, `derived_order`, `render_spec`, and the viewer's record page of its last entry, rendered through the viewer's page function as a request would, return without `RecursionError`, and on a 30-entry chain and a diamond with a repeated branch equal a copy of today's functions).
  `test_collector.py`: `test_main_disables_the_collector_for_one_shot_commands` (`main` with `argv=None` and `sys.argv` patched for `guide`: `gc.isenabled()` False afterwards, re-enabled in a `finally`); `test_view_keeps_the_collector` (`serve` patched out).
- [ ] **Step 2:** run them; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; `probes/phases.py` at `s9000` and `s90000` without its `_missing` patch (in a scratch copy), and `probes/shapes.py` at 2,000, 4,000, and 8,000 for each shape, recorded; expected `check_state` under 1 s at 160,000 files and each shape roughly doubling with its size.
- [ ] **Step 5:** commit, push.

### Task 3: libyaml behind a guard

**Files:**
- Create: `src/lodge/core/yamlfast.py` (the guard and the C loader)
- Modify: `src/lodge/core/yamlio.py` (`load_yaml` asks the guard first)
- Test: `tests/core/test_yaml_guard.py` (new), `tests/core/test_yaml_fuzz.py` (new)

**Interfaces:**
- Consumes: nothing.
- Produces:
  ```python
  def admitted(header: str) -> bool     # every line has a shape lodge's writer produces
  def load_yaml(text: str) -> object    # the C loader when libyaml is present and admitted(text); otherwise today's loader
  ```
- The guard (d-q051s2): `admitted` holds when the text has no character outside printable ASCII, the space, the newline, and non-ASCII characters other than U+0085, U+2028, U+2029, U+FEFF, and the surrogates; and every line matches one of:
  - `KEY: PLAIN` or `KEY: STRING`
  - `KEY:` alone, followed by block list lines
  - `  - {KEY: VALUE(, KEY: VALUE)*}` (a block list of flow mappings, as `changes` and `numbers` are written)
  - `KEY: {KEY: VALUE(, KEY: VALUE)*}` (as `quote` and `imported_from` are written)
  - `KEY: [VALUE(, VALUE)*]` or `KEY: []` (as `order`, `rests_on`, `replaces` are written)
  where `KEY` is `[a-z_]+`, `PLAIN` is `[A-Za-z0-9][A-Za-z0-9._:+-]*` not ending in `:`, with nothing after it, `STRING` is a JSON string (`"`, then characters other than `"`, `\`, and controls, or the escapes `\"`, `\\`, `\/`, `\b`, `\f`, `\n`, `\r`, `\t`, `\uXXXX` outside `\uD800` to `\uDFFF`, then `"`), and `VALUE` is `PLAIN` or `STRING`; no tab, no trailing space, no `#`, `|`, `>`, `&`, `*`, `!`, `%`, or `?` outside a `STRING`.
- The C loader: `yaml.CSafeLoader` with today's empty implicit resolvers, kept constructors, surrogate-pair joining, and duplicate-key refusal (written without the two-argument `super()`); any exception from it still falls back to today's loader.
- So a header lodge did not write, a hand edit with a trailing tab, a deep nesting, or a block scalar always takes today's loader, and its value, error message, and line come from it (the correctness review's B1, the feasibility review's F14).

- [ ] **Step 0:** skeleton.
- [ ] **Step 1: Write the failing tests:**
  `test_yaml_guard.py`: `test_every_written_header_is_admitted` (`write_record` of every decision and entry built in `tests/core/builders.py` and samples, `write_area`, and `write_thread` with author and agent messages: every header and message block admitted, and parsed by the C loader to today's value); `test_trailing_tab_is_not_admitted_and_fails_as_today` (`title: x` then a tab, `title:` then a tab and a value, `- a` then a tab, `title: x` then a tab and `# c`: not admitted, and `parse_record` gives today's problem); `test_block_scalar_bom_and_nesting_not_admitted` (`key: |#`, a BOM after a line break, a 600-level nested sequence); `test_c_loader_used_for_admitted_headers` (a patched counter on the C path); `test_falls_back_without_libyaml` (patched `__with_libyaml__ = False`).
  `test_yaml_fuzz.py`: `test_admitted_headers_parse_the_same` (seeded generator of headers built from the writer's shapes with random keys, plain and JSON-string values including escapes, unicode, surrogate pairs, and with random single-character mutations (tab, `#`, `|`, `&`, BOM, U+2028, deleted quote, extra indentation); for every admitted header on which the C loader succeeds, today's loader succeeds with an equal value (the C loader may fail where today's succeeds, and then `load_yaml` falls back), and for every header `load_yaml` equals today's loader in value or in `YamlError` message and line; the share of admitted headers the C loader parses is printed; 20,000 headers, bounded to about 10 s, the seed printed on failure).
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; `probes/phases.py --pure-yaml` against without at `s9000`, recorded, with the share of headers admitted (expected all, since the bench stores are written by lodge's writer).
- [ ] **Step 5:** commit, push.

### Task 4: Identical states reuse the snapshot and skip the change check

**Files:**
- Modify: `src/lodge/app/state.py`
- Test: `tests/core/test_identical_change.py` (new), `tests/app/test_identical_reads.py` (new); tighten Task 2's `test_derive_once_per_checked_read`

**Interfaces:**
- Consumes: Task 2's `facts`.
- Produces: `read_checked` loads the published tree only when `(current.files, current.attachments) != (published.files, published.attachments)`; when equal it adds no change problems (d-zyqzkg).
  The proof, which the report repeats against the code as built: for identical states every problem of `check_state(after)` is in `known`; `_missing` finds every ID; `_dates`, `_imports_over_live`, `_unlisted_sources`, and the decision half of `_links_to_dead` iterate over new decisions or new records, of which there are none; check 4 compares each entry with itself and finds no listed change wanted; check 5 compares each decision and thread with itself; the entry half of check 6 looks only at `rests_on` targets the published entry lacks.
  Task 10a uses the same shortcut when the two listings' blobs and attachments are equal (d-c0q20c).

- [ ] **Step 1: Write the failing tests:** `test_check_change_of_a_state_with_itself_is_empty` (every sample snapshot, the builders' snapshots of `tests/core/test_check_change.py`, and snapshots holding a hand-edited published decision, a duplicate ID, a cycle, an out-of-order entry, a new decision dated after `now`, an imported record from a source not in `[import] sources`, and an entry whose decision lists `link`: `check_change(s, s, settings, now).problems == ()`); `test_identical_trees_load_once` (count `load` calls through `read_checked` on a `MemoryStore` without `staged`: 1; `derive` calls: 1); `test_identical_read_output_unchanged` (show, search, waiting, and check on four sample stores print the same with the shortcut patched off and on).
- [ ] **Step 2:** run; expected FAIL on the counts.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; `scripts/bench_reads.py --against` Task 1's build at `s900`, `s9000`, and `s90000` (the last now finishes), output and exit status identical on every line, the table in the report.
- [ ] **Step 5:** commit, push.

### Task 5: `show REF...`, siblings, and citers

**Files:**
- Create: `src/lodge/core/codes.py` (`family`, `citers`, `is_code_token`, `cites`)
- Modify: `src/lodge/core/__init__.py`, `src/lodge/app/reads.py` (`show_many`), `src/lodge/app/lodge.py`, `src/lodge/app/results.py` (`Shown` gains `siblings`, `citers`, `left_out`; `ShownMany`), `src/lodge/app/__init__.py`, `src/lodge/cli/parser.py` (at most 6 lines: `ref` becomes `refs`, `nargs="+"`), `src/lodge/cli/commands.py`, `src/lodge/cli/output.py`, `scripts/bench_reads.txt`
- Records: a product decision with an edit of s-3n0ndk, through `lodge add`
- Test: `tests/core/test_codes.py` (new), `tests/app/test_show_many.py` (new), `tests/e2e/test_show_many.py` (new)

**Interfaces:**
- Consumes: Task 4's `read_checked`.
- Produces:
  ```python
  def is_code_token(query: str) -> bool        # one token of [A-Za-z0-9][A-Za-z0-9._-]*
  def family(s: Snapshot, code: str) -> tuple[str, ...]
      # records whose code, lower-cased, equals code.lower() or starts with code.lower() + "."; the code itself first, then by lower-cased code
  def code_tokens(text: str) -> frozenset[str]
      # for each maximal run r of [A-Za-z0-9._-] in text.lower(): r itself, and r[:i] for every i with r[i] == "."
      # and r[i+1] not in [a-z0-9] (or i the last position)
  def cites(text: str, code: str) -> bool     # code.lower() in code_tokens(text)
  def citers(s: Snapshot, d: Derived, code: str) -> tuple[str, ...]
      # records outside the family whose title or statement cites code, newest first by (date, ID)
  @dataclass(frozen=True) class ShownMany:
      items: tuple[tuple[str, Shown | LodgeError], ...]   # (ref, result) per ref, a repeat of a shown record as LodgeError-free marker below
      read: Read
  def show_many(w: Wiring, refs: Sequence[str], reasoning: bool, provenance: bool) -> ShownMany
  Shown.siblings: tuple[Level1, ...] = ()     # family without the record itself, up to 10
  Shown.citers: tuple[Level1, ...] = ()       # citers, up to 10
  Shown.left_out: tuple[int, int] = (0, 0)    # siblings and citers left out
  ```
  A ref naming a record already shown is carried as `(ref, Shown)` of that record with a flag `repeat: bool = False` on `Shown`, printed as one line.
- Case comparison is `str.lower()`, as `core.words` uses, never `casefold` (the correctness review's M3).
- Output of `lodge show A B C`: the freshness and problem lines once; each record's text as today; before each record after the first a line `----- B` naming the ref, so no shell separator is needed; a repeat prints `----- B is d-xxxxxx, shown above`; a ref that fails prints `----- B` on standard output, then standard output is flushed and `lodge: <the error>` goes to standard error, and the others still print (the correctness review's M2).
  The exit status is the highest exit code among the failed refs, 0 when none failed.
  One ref prints exactly as today, plus the new lines.
- The new lines, after the level 3 section, only for a record with a code that has siblings or citers: `siblings:` then one brief line each; `cited by:` then one brief line each; then `and N more siblings and M more citing records; lodge search CODE` when any were left out.
- The product decision: `show` takes several refs, printed in one read with each record once, and names a coded record's sibling codes and citing records; it edits s-3n0ndk's third sentence to say so, the rest of the entry unchanged.

- [ ] **Step 0:** skeleton.
- [ ] **Step 1: Write the failing tests:** `test_codes.py`: `test_family_takes_dotted_siblings_not_longer_numbers` (`X-1`, `X-1.why`, `x-1.b`, not `X-10`, `X-1a`); `test_family_orders_the_code_first`; `test_cites_whole_tokens_only` (`see X-1.` yes, `X-1,` yes, `(X-1)` yes, `X-1.-` yes, `X-10` no, `X-1.why` no, `AX-1` no, `x-1` yes, `ſ-1` no); `test_cites_equals_the_boundary_rule` (2,000 seeded strings over a small alphabet of letters, digits, `.`, `-`, `_`, and spaces, and codes drawn from their substrings: `cites` equals the rule "the code, lower-cased, occurs where the character before is not in `[a-z0-9._-]` or is the start, and the character after is not in `[a-z0-9_-]`, is not a `.` followed by `[a-z0-9]`, or is the end"); `test_citers_exclude_the_family_and_order_newest_first`.
  `test_show_many.py`: `test_each_record_once_in_ref_order` (an ID and its code given both); `test_failing_ref_in_place_and_others_shown`; `test_one_read_for_many_refs` (count `trees()` calls: 1); `test_siblings_and_citers_capped_at_ten` (12 siblings, 11 citers: 10 each and the counts 2 and 1).
  `tests/e2e/test_show_many.py`: `test_show_three_refs_one_output` (separators, exit 0); `test_unknown_ref_exits_2_after_the_others`; `test_stdout_flushed_before_each_error` (a patched `sys.stdout.flush` records a call before the error is written); `test_single_ref_output_unchanged` (`show ITEM-1` equals today's output, kept as a literal).
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement; the product decision through `lodge add --dry-run` then `lodge add`.
- [ ] **Step 4:** gate; bench line `show {code} {code2} {entry}` recorded.
- [ ] **Step 5:** commit, push.

### Task 6: Search: several queries, codes first, phrases, all words first, leaner brief lines

**Files:**
- Create: `src/lodge/core/filters.py` (`Filters`, moved from `search.py` and re-exported by `core/__init__.py`), `src/lodge/core/ranking.py` (the query, the ranking over candidates)
- Modify: `src/lodge/core/search.py` (calls `ranking`; keeps `resolve` and `related`), `src/lodge/core/__init__.py`, `src/lodge/app/reads.py` (`search_many`), `src/lodge/app/lodge.py`, `src/lodge/app/results.py` (`Listed` gains `query` and `above`), `src/lodge/cli/parser.py` (at most 8 lines: `query` becomes `queries`, `nargs="*"`; `--phrase`, repeatable), `src/lodge/cli/commands.py`, `src/lodge/cli/output.py`, `tests/e2e/test_search_brief.py` and `tests/core/test_search.py` (the expectations that print ` · current` or rank by one word, each edit listed in the report), `scripts/bench_reads.txt`
- Records: a product decision with an edit of s-3n0ndk (search semantics, the brief line) through `lodge add`
- Test: `tests/core/test_ranking.py` (new), `tests/app/test_search_many.py` (new), `tests/e2e/test_search_many.py` (new)

**Interfaces:**
- Consumes: Task 5's `is_code_token`, `family`, `cites`, `citers`.
- Produces:
  ```python
  @dataclass(frozen=True)
  class Query:
      text: str
      phrase: bool                     # given with --phrase
      words: frozenset[str]            # core.words(text)
      tokens: tuple[str, ...]          # every [^\W_]+ run of text.lower(), function words kept; used for a phrase
  def parse_query(text: str, phrase: bool = False) -> Query
  def needs_memory(q: Query) -> bool   # a phrase, or a code token, with empty words: the index cannot prove its candidates (d-rs76ks)
  @dataclass(frozen=True)
  class Candidate:
      view: Level1
      areas: frozenset[str]            # an entry's area; a decision's, the areas of the entries it changes
      title_words: frozenset[str]      # core.words(view.title); the index supplies these from its word table
      statement_words: frozenset[str]
  def rank(candidates: Iterable[Candidate], query: Query, filters: Filters, family: Sequence[str],
           citing: Sequence[str], limit: int) -> tuple[list[str], int]
  def search_counted(s, d, query: Query, filters, limit) -> tuple[list[str], int]   # builds every candidate and calls rank
  ```
- The ranking (`rank`), for a non-empty query, among candidates passing the filters:
  1. the exact ID;
  2. when `is_code_token` and the family is not empty, the family in `family`'s order, then `citing`'s order (d-n9w4by); otherwise the record whose code equals the query, as today;
  3. only when `words` is not empty: for a phrase, records whose title or statement token sequence holds `tokens` contiguously (d-emtwbs), by score; for words, records holding every word, by score;
  4. only when `words` is not empty: records holding at least one word but not all, by score (for a phrase too, so its words still find near matches below the exact ones);
  score as today (3 per query word in the title, 1 per word in the statement), from `title_words` and `statement_words`, ties newest first by `(date, ID)`.
  An empty query lists by `(date, ID)` newest first, as today.
- `lodge search Q1 Q2 --phrase "P1" ...`: one read; queries in argument order, positional ones first, then each `--phrase`; each query's results under a line `query: Q1 · N matches` when there is more than one query, followed by `· also d-xxxxxx, s-yyyyyy above` naming the records of this query already printed under an earlier one, which are not printed again and do not count toward `--limit` (the correctness review's M8); `--limit` applies per query; no query lists newest first, as today.
  A multi-word argument is all its words; only `--phrase` makes a phrase (d-ty4dks).
- Brief lines (d-p60ka9): under the default status filter a line omits ` · current`, and the output's first line, after the freshness lines, is `records are current unless marked`; under any other `--status` the status prints as today.
- The product decision: search takes several queries and `--phrase`, ranks a code's family and citers first, matches a phrase as a contiguous run of whole words, ranks records with every word first, and brief lines omit the default status; it edits s-3n0ndk's first two sentences, its third unchanged from Task 5.

- [ ] **Step 0:** skeleton, with `Filters` moved and `tests/test_structure.py` green.
- [ ] **Step 1: Write the failing tests:** `test_ranking.py`: `test_exact_id_first`; `test_code_family_then_citers_then_words`; `test_code_without_family_ranks_as_words`; `test_phrase_is_a_run_of_whole_words` (`--phrase "settled point"` against `point settled`, `unsettled points`, and `settled, point.`: only the last two words in order with punctuation between match); `test_phrase_keeps_function_words` (`--phrase "of the berth"`); `test_needs_memory_cases` (`--phrase "of the"`, the code `NO-ONE`, the code `A`: True; `--phrase "the berth"`: False); `test_function_words_only_finds_id_and_code_only` (`search of the` and `search "of the"`: only an exact ID or code, as today); `test_all_words_before_some_words`; `test_ties_newest_first`; `test_filters_apply_to_family_and_citers`; `test_rank_over_candidates_equals_rank_over_all` (for 300 seeded queries over a made-up 400-record snapshot, words, phrases, codes, their mixes, and the unquoted `of the`, skipping those `needs_memory` holds for: `rank` over the records holding any query word, the family, and the citers equals `rank` over every record; the property Task 10b relies on).
  `test_search_many.py`: `test_each_record_once_across_queries` (the header names the earlier records); `test_limit_per_query_excludes_earlier_records`; `test_one_read_for_many_queries`.
  `tests/e2e/test_search_many.py`: `test_two_queries_with_headers`; `test_phrase_option_is_one_query`; `test_quoted_words_are_all_words` (`search "berth crane"` ranks records with both words first, not a phrase); `test_brief_omits_current_and_says_so`; `test_brief_with_status_any_prints_status`.
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement; edit the existing expectations the report lists; the product decision through `lodge add`.
- [ ] **Step 4:** gate; bench lines recorded, with output sizes against Task 5's build for the brief lines.
- [ ] **Step 5:** commit, push.

### Task 7: `lodge guide --read`

**Files:**
- Create: `src/lodge/cli/guide-read.md`
- Modify: `src/lodge/cli/parser.py` (at most 3 lines), `src/lodge/cli/commands.py`, `src/lodge/cli/guide.md` (one line pointing readers at `--read`), `README.md` if it lists the guide
- Records: a product decision with an edit of s-7f10zc through `lodge add`
- Test: `tests/e2e/test_guide_read.py` (new)

**Interfaces:**
- Consumes: Tasks 5 and 6.
- Produces: `lodge guide --read` prints at most 25 lines: what lodge holds (one line each for decisions, entries, areas); `lodge waiting` first in a session; examples, each on its own line in backticks: `lodge search "several words" --brief` (records with all the words first), `lodge search --phrase "exact words in order" --brief`, `lodge search CODE --brief` (the family and citers first), `lodge search word1 word2 --brief` (two queries), `lodge show REF REF REF`, `lodge show CODE.why --reasoning`, `lodge show REF --provenance`; that quotes only group words into one query and `--phrase` matches them in order; what "awaiting the author", "in doubt", "fails check", `problem:`, and an unmarked status mean; that `show` lists siblings and citers; never the writing rules.
- The product decision: lodge prints a short reading guide with `lodge guide --read` beside the full guide; it edits s-7f10zc's first sentence.

- [ ] **Step 1: Write the failing tests:** `test_guide_read_is_short_and_has_no_writing_rules` (at most 25 lines; no `lodge add`, `lodge draft`, `decided_by`); `test_guide_read_examples_run` (each backticked example, with `REF`, `CODE`, and words replaced from the seeded project, runs with exit 0; the `--phrase` example's first result holds the phrase's words in order, and the quoted-words example's first result holds all its words); `test_full_guide_points_at_read`.
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement; the product decision.
- [ ] **Step 4:** gate, commit, push.

### Task 8a: Blob IDs on exact trees, and the snapshot from per-file parses

**Files:**
- Create: `src/lodge/core/listing.py` (`blob_id`, `Listing`; a leaf)
- Modify: `src/lodge/core/snapshot.py` (`Tree.blobs`; `parse_file` and `assemble`, with `load` their composition), `src/lodge/core/__init__.py`, `src/lodge/gitstore/trees.py` (`read_tree` fills `blobs` from `ls-tree`), `src/lodge/gitstore/checkout.py` (at most 6 lines: `disk_tree` fills `blobs` with `blob_id` of the bytes it read), `tests/app/fakes.py` (`MemoryStore` fills `blobs`)
- Test: `tests/core/test_listing.py` (new), `tests/gitstore/test_tree_blobs.py` (new)

**Interfaces:**
- Consumes: nothing beyond Task 4.
- Produces:
  ```python
  # core/listing.py, a leaf
  def blob_id(raw: bytes) -> str          # git's: sha1 of b"blob %d\0" % len(raw) + raw, hex
  @dataclass(frozen=True)
  class Listing:                          # used from Task 8b on
      rev: str | None
      ident: str                          # equal idents mean equal file mappings and attachment sets
      blobs: Mapping[str, str]            # path -> blob_id, every file but attachments
      attachments: frozenset[str]
  # core/snapshot.py
  Tree.blobs: Mapping[str, str] = field(default_factory=dict)   # path -> blob_id of the bytes read, every file but attachments
  Parsed = Decision | SpecEntry | Area | Thread | Problem
  def parse_file(path: str, text: str) -> Parsed | None   # None for attachments and .gitkeep; a Problem for strays
  def assemble(parsed: Mapping[str, Parsed | None], attachments: frozenset[str]) -> Snapshot
      # load(tree) == assemble({p: parse_file(p, t) for p, t in tree.files.items()}, attachments of tree)
  ```
- `disk_tree` hashes the bytes it read (a link's target bytes, an empty file for anything not regular), so a working-tree file's key is never git's claim (d-q0tb8r); `read_tree` takes the object IDs `ls-tree` gives for committed trees.
- No port changes; the gate, `add`, and every read keep `trees()`.

- [ ] **Step 0:** skeleton.
- [ ] **Step 1: Write the failing tests:** `test_listing.py`: `test_blob_id_matches_git` (three byte strings, one not UTF-8, against `git hash-object --stdin` in `tmp_path`); `test_assemble_equals_load` (every sample tree, a tree with a duplicate ID, a stray, an attachment, and an unreadable header); `test_parse_file_ignores_attachments_and_gitkeep`.
  `test_tree_blobs.py`: `test_disk_tree_blobs_hash_the_bytes_read` (a clean checkout: equal to `git ls-files -s`; after an edit, an untracked file, and a symbolic link: each `blob_id` of the bytes on disk); `test_disk_tree_ignores_assume_unchanged` (an assume-unchanged file edited on disk: the blob is the edited bytes'); `test_read_tree_blobs_are_git_object_ids`.
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; bench `seen` at `s9000` against Task 7's build, output identical, the cost of hashing in `disk_tree` recorded.
- [ ] **Step 5:** commit, push.

### Task 8b: The fast identity and listing for the indexed reads

**Files:**
- Create: `src/lodge/gitstore/identity.py` (the checkout overlay and identity), `src/lodge/gitstore/listing.py` (listings and texts, both modes), `src/lodge/gitstore/attributes.py` (the conversion check), `src/lodge/gitstore/flags.py` (assume-unchanged and skip-worktree)
- Modify: `src/lodge/app/ports.py` (`Store` gains three methods), `src/lodge/gitstore/checkout.py` and `src/lodge/gitstore/branch.py` (at most 10 lines each: the methods delegate to the new modules), `tests/app/fakes.py`, `tests/gitstore/conftest.py` and `tests/e2e/conftest.py` (`HOME` and `XDG_CONFIG_HOME` set to the test's folder)
- Test: `tests/gitstore/test_identity.py` (new), `tests/gitstore/test_identity_property.py` (new), `tests/gitstore/test_attributes.py` (new), `tests/gitstore/test_flags.py` (new), `tests/gitstore/test_listing_modes.py` (new)

**Interfaces:**
- Consumes: Task 8a's `Listing`, `blob_id`, exact trees as the oracle.
- Produces:
  ```python
  # app/ports.py, Store gains (trees(), gate(), publish() unchanged):
  def identities(self) -> tuple[str, str]           # current and published ident; branch mode fetches and accepts here
  def listings(self) -> tuple[Listing, Listing]      # the states identities() named, from the same resolved revisions
  def texts(self, listing: Listing, paths: Collection[str]) -> dict[str, str]
  ```
- The overlay, checkout mode (d-8kq2nk, d-ana6c0, d-c5a1y4, d-dqpf59): `base` is `rev-parse HEAD:lodge` (the empty tree's ID when `HEAD` is unborn or lacks `lodge/`); a path joins the overlay when `git -c core.fsmonitor=false -c core.checkStat=default -c core.trustctime=true diff-index --cached --no-renames -z --name-only HEAD -- lodge` or the same `diff-files` names it, when `flags.py` lists it, when `attributes.py` says git may convert it, or when it is on disk and `base` lacks it (found in this task by a names-only `os.scandir` walk compared folder by folder with `base`'s names and kinds, so a file where `base` has a folder, or a folder where `base` has a file, counts as lacking; Task 11 replaces the walk); each overlay path is read as `disk_tree` reads it and hashed when `os.lstat` finds anything but a real folder (a link to a folder is a file, as in `disk_tree`), and is marked deleted when `os.lstat` finds a real folder or raises any `OSError`, `ENOTDIR` included, the folder's files coming in through the walk (the feasibility recheck's R4); an entry whose hash equals `base`'s blob at that path, a deletion of a path `base` lacks, and an attachment present in both are dropped.
- The identity (d-ana6c0, d-c0q20c): `base` itself when the overlay is empty, else `sha1(base + "\0" + sorted "path\0blob" lines)`; equal idents imply equal exact trees, while equal trees may have unequal idents (an edit later committed, an attachment's bytes committed, a working tree reverted to the published contents while `HEAD` differs), which costs a rebuild, never a wrong read; published is the merge base's `lodge/` tree ID as `published_state` finds it, its missing-state message unchanged; branch mode: the tip's `lodge/` tree ID, and the accepted tip's for published while a rewrite stands.
- Flags: `git ls-files -t -v -z -- lodge .gitattributes`, entries under `lodge/` tagged `S` or with a lower-case tag; the same call names every `.gitattributes` in git's index for the conversion check; cached in the store object only, never in the index (d-n6tqzq), keyed by the stat of git's index file (`git rev-parse --git-path index`) as inode, size, `mtime_ns`, and `ctime_ns`.
- Conversions (d-dqpf59, d-9r24jc): none when `git config --get core.autocrlf` is unset or false in git's spellings (`false`, `no`, `off`, `0`, empty), no `core.attributesFile`, no file named by `git var GIT_ATTR_GLOBAL` or by `git var GIT_ATTR_SYSTEM` (one call each; the system one skipped when `GIT_ATTR_NOSYSTEM` is set) exists, no `$GIT_COMMON_DIR/info/attributes`, and no `.gitattributes` at the root or under `lodge/`, on disk or in git's index (git reads an index entry when the file is gone from disk); `core.autocrlf` true in any spelling (`true`, `yes`, `on`, `1`) or `input`, or a `git var` call that fails: every path converts; otherwise `git check-attr --stdin -z text eol crlf filter ident working-tree-encoding` over the listing's paths, and each path with any of them set converts.
  The result is cached in the store object only, keyed by the configuration values, the bytes of every source file, and the stat of git's index file, so a change to any of them is a miss.
- Both caches take their whole key (the index file's stat, and for conversions also the configuration values and every source file's bytes) before the git call and again after it, and keep the result only when the two keys are equal (d-n6tqzq, d-e3stjn; the second recheck's V4, the third's R3).
- The listing: `ls-tree -r` of `base` with the overlay applied; `texts` reads git blobs with one `cat-file --batch` and overlay files from the bytes already read.
- Nothing calls these methods yet but the tests; Task 10a's reads do.

- [ ] **Step 0:** skeleton.
- [ ] **Step 1: Write the failing tests** (each in a `tmp_path` repository; "agrees" means the listing's paths, attachments, and `texts` equal Task 8a's exact `disk_tree`, and the ident equals the ident of an earlier state only when their exact trees are equal):
  `test_identity.py`: `test_clean_checkout_ident_is_the_head_tree` (and equals the published ident and `git rev-parse HEAD:lodge`); `test_touched_file_keeps_the_clean_ident`; `test_staged_edit_reverted_on_disk_keeps_the_clean_ident`; `test_unstaged_edit_agrees`; `test_untracked_file_agrees`; `test_ignored_file_agrees`; `test_deleted_file_agrees`; `test_staged_deletion_left_on_disk_agrees`; `test_rename_agrees`; `test_symbolic_link_agrees`; `test_fifo_agrees` (skipped without `os.mkfifo`); `test_attachment_bytes_changed_keeps_the_ident`; `test_unborn_head`; `test_head_without_lodge`; `test_commit_after_edit_agrees` (the ident before and after the commit may differ, the listings' blobs are equal); `test_attachment_only_commit_agrees`; `test_reverted_to_published_with_head_ahead_agrees` (the current listing's blobs and attachments equal the published listing's); `test_file_replaced_by_folder_agrees` (tracked `lodge/decisions/old.md` becomes a folder holding `new.md`, and an empty folder, and the same under `lodge/attachments/`); `test_folder_replaced_by_file_agrees`.
  `test_flags.py`: `test_assume_unchanged_edit_agrees`; `test_skip_worktree_missing_file_agrees` (a sparse checkout without one record: missing, as `disk_tree` sees it); `test_ignore_stat_entries_agree` (`core.ignoreStat=true` in the repository's config, then an edit); `test_cached_flags_and_conversions_keyed` (a key with another index-file stat, configuration value, or source byte is a miss; `git update-index --assume-unchanged` run between the key and the `ls-files` call, through a patched runner: the result is not kept, and a later edit of that file agrees; an attributes file given a filter between the key and `check-attr` and restored afterwards, with git's index file untouched: the result is not kept, and the record filtered on disk agrees).
  `test_attributes.py`: `test_no_sources_no_check_attr_call`; `test_autocrlf_spellings` (`true`, `yes`, `on`, `1`, `input`: every path read from disk; `false`, `no`, `off`, `0`: none); `test_global_attributes_file_reads_from_disk` (`*.md text eol=crlf` in `$XDG_CONFIG_HOME/git/attributes`: agrees); `test_info_attributes_and_attributes_file` (each source alone: agrees); `test_text_attribute_on_one_pattern` (`lodge/decisions/*.md text eol=crlf`, and the old `lodge/*.md crlf` with `core.eol=crlf`: those paths read from disk, others from git; agrees); `test_root_attributes_only_in_the_index` (a committed root `.gitattributes` with a clean and smudge filter that change a record's statement, then the file removed from disk without staging: the record is read from disk; agrees); `test_git_var_failure_converts_every_path` (the git runner patched to exit 129 for `var`: every path read from disk); `test_warm_change_of_a_source_agrees` (one store object; after a first listing, in turn `core.autocrlf`, `core.attributesFile`, and a source file's bytes change: the next listing agrees).
  `test_identity_property.py`: `test_random_edits_agree` (200 seeded sequences of 1 to 8 operations on a 40-record made-up store: create, edit, delete, untracked file, touch only, stage, unstage, revert, commit, assume-unchanged edit, skip-worktree removal, a CRLF rewrite under an attributes file, a file replaced by a folder; after each sequence the fast listing agrees with `disk_tree`, and any two states seen in the run with equal idents have equal exact trees).
  `test_listing_modes.py`: `test_branch_mode_ident_is_the_tip_tree`; `test_rewritten_branch_publishes_the_accepted_tree`.
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; `identities()` and `listings()` timed at `s90000` clean and with one edit, recorded with each git call's share.
- [ ] **Step 5:** commit, push.

### Task 9: The parse cache, and the index's files, keys, and failure modes

**Files:**
- Create: `src/lodge/core/codec.py` (plain values), `src/lodge/gitstore/index_db.py` (files, schema, the build digest, the settings, the failure modes), `src/lodge/gitstore/index_parses.py` (the parse cache), `src/lodge/gitstore/index_space.py` (the cap, the clear, and deletion of old builds' files under the lock), `src/lodge/app/index_types.py` (`FileKey`)
- Modify: `src/lodge/app/ports.py` (`Index`), `src/lodge/app/__init__.py`, `src/lodge/app/state.py` (snapshots through the cache), `src/lodge/app/lodge.py` (`Lodge` takes `index: Index | None = None`), `src/lodge/gitstore/__init__.py`, `src/lodge/main.py` (opens the index; `LODGE_INDEX=off` in the environment gives `None`), `src/lodge/core/__init__.py`
- Records: a product decision creating an entry in the `storage` area, "A disposable index speeds reads", listed in the area's order and resting on s-j8tp0n
- Test: `tests/core/test_codec.py` (new), `tests/gitstore/test_index_db.py` (new), `tests/gitstore/test_index_failures.py` (new), `tests/gitstore/test_index_parses.py` (new), `tests/app/test_parse_cache.py` (new), `tests/e2e/test_index_off_same_output.py` (new)

**Interfaces:**
- Consumes: Task 8a's `parse_file`, `assemble`, `Parsed`, and `Tree.blobs`.
- Produces:
  ```python
  # core/codec.py: pure, no marshal
  def to_plain(value: object) -> object
      # dataclass -> (class name, *fields); enum -> ("=" + class name, value); tuple -> list;
      # Mapping with str keys -> dict of plain values; frozenset -> frozenset of plain values; str, int, bool, None as they are
  def from_plain(plain: object, classes: Mapping[str, type]) -> object   # ValueError on any shape it did not write
  CORE_CLASSES: Mapping[str, type]   # every dataclass and enum a parse, a Level1, or a Level3 holds; app passes {**CORE_CLASSES, **APP_CLASSES}
  # app/index_types.py
  FileKey = tuple[str, str]          # (path, blob_id)
  # app/ports.py
  class Index(Protocol):
      def parses(self, keys: Collection[FileKey]) -> dict[FileKey, Parsed | None]
      def keep_parses(self, parsed: Mapping[FileKey, Parsed | None], *, files: int,
                      used: Mapping[FileKey, Parsed | None] | None = None,
                      epoch: int | None = None) -> None
      def epoch(self) -> int   # meta.epoch; a build calls it once, before its first lookup (the fourth recheck's W1)
  # gitstore
  def open_index(common_dir: Path) -> Index | None
  ```
- Files (d-faakge, d-rvf532, d-e3stjn): `<git common dir>/lodge/index-<digest>.sqlite` with its `-wal` and `-shm`, one per build key, never swapped or renamed, and beside it `index-<digest>.lock`, which is never deleted; `<digest>` the first 16 hex characters of sha1 over the schema number, lodge's source bytes (every `.py` and `.md` file of the installed `lodge` package, by relative name, 2.3 ms for 273,039 bytes in the planner's probe), `sys.version`, `yaml.__version__`, `yaml.__with_libyaml__`, and `sqlite3.sqlite_version`.
- The lock (d-e3stjn, d-bzp30x): `open_index` takes `fcntl.flock(LOCK_SH)`, blocking, on its lock file before it connects, and releases it after the connection is closed; it creates the lock file, or opens an existing one read-only when it cannot create it, and touches it (`os.utime`, a failure ignored), so a build's age is its lock file's modification time; on opening, another build's file whose lock file is older than 7 days, or that is beyond the four most recently touched builds, is deleted, with its `-wal` and `-shm`, only while `flock(LOCK_EX | LOCK_NB)` on its lock file succeeds; any failure skips it; without `fcntl`, or when no lock file can be opened, nothing is deleted; the protocol is at most about 40 lines, else deletion is dropped and the README's `rm` of the folder is the way to reclaim space.
- Settings (d-t3afj1, d-gvz66f): `isolation_level=None`, journal mode `WAL`, `synchronous=NORMAL` (safe from corruption in WAL mode), `secure_delete=OFF` and `journal_size_limit=16777216` (so a clear frees pages without zeroing them through the WAL, and the `-wal` shrinks back after checkpoints even while another connection is open; d-a8gkrh, the fourth recheck's W4), `busy_timeout` 200 ms; every read inside `BEGIN` ... `COMMIT`, every write inside `BEGIN IMMEDIATE` ... `COMMIT`, with `ROLLBACK` in a `finally` (invariant 5).
- Parses (invariant 1): `parses(rowid INTEGER PRIMARY KEY, path, blob, value, UNIQUE (path, blob))` with `value` the compact JSON (`json.dumps(..., ensure_ascii=True, separators=(",", ":"))`) of `to_plain(parsed)`, as built, inserted with `INSERT OR IGNORE`, never updated or deleted; a row that fails to decode is a miss; `keep_parses` writes all its rows in one transaction.
- The index holds no flag or conversion result (d-n6tqzq), so a read of a seen state writes nothing, whatever `git status` did to git's index file.
- The cap (invariant 4, d-e3stjn, d-c6cegr, d-a8gkrh): `INDEX_BYTES_PER_FILE = 1_500` and `INDEX_FILE_CAP = max(16 MiB, INDEX_BYTES_PER_FILE × files in the tree)`, about 240 MB at 160,000 files as the author chose (d-4pbeax), compared with the used pages, `(page_count - freelist_count) × page_size`, so a cleared file whose pages are free is under it; the file never grows much past the cap, since a clear frees pages for reuse and the file keeps its size; a writer that finds the index over the cap, and at least one state kept since the last clear, first clears it: in one `BEGIN IMMEDIATE` transaction, `DELETE` of every table but `meta`, a drop and re-creation of the FTS table (no FTS row is deleted by key), and `meta.epoch` raised; when one state's own working set exceeds the cap (records far larger than the bench store's), the file holds that state and at most one more, every second changed read clears, the reads stay correct, and Task 12 reports the clears per hundred changed reads; then it writes as usual, the epoch telling it to write every unit it used; freed pages are reused, and nothing on a read's path vacuums.
- Failure modes (d-kj554d, d-her016), each a test:
  - the folder or file cannot be written: opened with `mode=ro` through a `file:` URI; reads use what it holds, writes do nothing;
  - an error whose `sqlite_errorcode` is `SQLITE_CORRUPT` or `SQLITE_NOTADB` in `open_index`: the file deleted, with its `-wal` and `-shm`, and recreated only while this process's lock can be made exclusive without waiting; a refused upgrade (which on Linux drops the shared lock) closes the lock file and returns `None`, as does a corrupt file without `fcntl` or when not writable; after opening, such an error is a miss like any other (d-bzp30x, the fourth recheck's W5 and W7);
  - any other `sqlite3.Error` (busy, locked, read-only, I/O), at opening or later: no delete; that operation returns a miss or does nothing, never raises;
  - a read and a write of one operation each run in one explicit transaction, rolled back on any error;
  - in WAL mode a read-only file opens only when its `-shm` and `-wal` can be used; otherwise `open_index` returns `None`.
- `app` builds every snapshot as `assemble` of cached parses for the tree's `(path, blobs[path])` keys plus `parse_file` of the misses, and keeps the misses; `derive` and every check run in full on that snapshot; the gate and `add` read exact trees as today (d-q0tb8r).
- The product decision: lodge keeps a disposable index in the git common dir, never committed, one file per lodge build, that never changes what a read prints or what the gate decides; its entry rests on s-j8tp0n.

- [ ] **Step 0:** skeleton.
- [ ] **Step 1: Write the failing tests:** `test_codec.py`: `test_round_trip_of_every_parse_kind` (a decision with every field, an entry with `rests_on`, an area with a rank, a thread with an author message, a problem with a line); `test_round_trip_of_mappings_and_read` (a `Read` with statuses, a titles mapping); `test_refuses_unknown_class_and_bad_shapes`; `test_no_pickle_or_marshal_in_core` (by `ast` over `core`).
  `test_index_db.py`: `test_creates_folder_and_file_named_by_digest`; `test_digest_changes_with_source_bytes` (a same-size, same-mtime source change: a new digest); `test_digest_names_python_yaml_libyaml_sqlite` (each patched in turn: a new digest); `test_two_builds_keep_their_files` (two digests alternating: the second open of each finds its parses); `test_old_build_deleted_after_seven_days_under_the_lock` (`os.utime` sets the ages: a file unwritten for 6 days stays; one unwritten for 8 days goes with its `-wal` and `-shm` and keeps its lock file; one whose lock another process holds shared stays); `test_no_fcntl_deletes_nothing`; `test_lock_taken_before_connect_and_touched` (a patched `sqlite3.connect` finds the lock held shared, and the lock file's mtime is now); `test_read_only_lock_file_is_opened`; `test_fifth_most_recent_build_is_deleted`; `test_refused_upgrade_returns_none_and_holds_no_lock` (another process holds the lock shared on a corrupt file: `open_index` returns `None` and a third process can take `LOCK_EX | LOCK_NB` only after the other releases); `test_corrupt_without_fcntl_returns_none`; `test_secure_delete_off_and_wal_bounded` (on every index connection `pragma secure_delete` reads 0 and `journal_size_limit` 16777216; where `sqlite3.connect(':memory:')` reads `secure_delete` 1, as on a build compiled with it, a clear of a populated 20 MB index leaves the `-wal` at most 16 MiB after a checkpoint, else that half is skipped and the reason printed); `test_two_clears_in_a_row_raise_the_epoch` (a fresh file reads epoch 1; two clears read 3; a build that took its hits between the clears, then keeps: every key of its rows has its parse row); `test_connection_is_explicit_and_wal` (`journal_mode` is `wal`, `isolation_level` is None, and `in_transaction` holds inside every read); `test_cap_counts_used_pages` (after a clear the file's size is unchanged and it is under the cap); `test_clear_keeps_a_readers_snapshot` (a connection inside a read transaction finishes its lookups with the rows it began with while another clears and commits; the next read transaction finds nothing and the epoch raised); `test_two_writers_over_the_cap_clear_once` (the second finds the index under the cap after the first's clear, and both reads print the same).
  `test_index_failures.py`: `test_read_only_folder_reads_or_skips` (`chmod 0o500`, skipped as root: `open_index` returns a read-only index or `None`, nothing is written, and the output is the same); `test_read_only_and_missing_returns_none`; `test_locked_at_open_does_not_delete` (a second connection holds `BEGIN EXCLUSIVE` on a populated index: `open_index` returns within 1 s, the file is unchanged, and after release the parses are found); `test_locked_write_is_skipped`; `test_corrupt_file_is_rebuilt` (garbage bytes); `test_corrupt_file_held_by_another_reader_is_not_deleted`; `test_corrupt_file_read_only_returns_none`; `test_keep_parses_interrupted_at_each_statement` (for each k, a failure injected after the k-th SQL statement of `keep_parses`, through a connection wrapper: no row of that call is kept, and the next read prints as with `LODGE_INDEX=off`); `test_concurrent_keep_parses` (two connections keep overlapping parses, interleaved deterministically: each call keeps all its rows or none, and every row found decodes to the parse of its key); `test_parse_units_are_immutable` (a second keep of a key with another value leaves the first value and rowid).
  `test_index_parses.py`: `test_hit_after_keep`; `test_key_is_path_and_blob` (the same blob at two paths in two areas parses to two areas); `test_undecodable_row_is_a_miss`.
  `test_parse_cache.py` (app, a fake index in `tests/app/fakes.py`): `test_second_read_parses_nothing`; `test_gate_uses_only_parses_keyed_by_read_bytes` (a fake index holding a wrong parse under a git blob ID the disk bytes do not hash to: the gate's result as without the index); `test_read_output_same_with_and_without_index` (show, search, waiting, check on four sample stores, printed text).
  `tests/e2e/test_index_off_same_output.py`: `test_index_off_same_output` (`show`, `search`, `waiting`, `spec`, `check --gate` print the same with `LODGE_INDEX=off` and without, twice each); `test_read_only_common_dir_reads` (made read-only after one read: exit 0, same output; skipped as root).
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement; the product decision through `lodge add`.
- [ ] **Step 4:** gate; the replay at all three sizes, `cold` and `seen`, recorded; output identical to Task 8b's build; one clear of a full index of `s90000` timed on a copy, with `pragma secure_delete` of the Python used named.
- [ ] **Step 5:** commit, push.

### Task 8c: The fast identity without needless work, and the Task 8b review's identity findings

Built after Task 9 and before Task 10a; it changes no port, and no output except where the Task 8b review found the fast listing disagreeing with the exact tree.

**Files:**
- Create: `src/lodge/gitstore/disk.py` (the one disk reader: folders and files opened relative to their parent's descriptor, never through a link)
- Modify: `src/lodge/gitstore/git.py` (`run_many`), `src/lodge/gitstore/identity.py` (the git group under one key of git's index file; `Committed` memoised per store object by commit ID, keeping entry kinds; the overlay through `disk.py`), `src/lodge/gitstore/listing.py` (`identities()` takes both tree IDs from `rev-parse`; `listings()` builds mappings on first use; `texts()` reads blobs only), `src/lodge/gitstore/flags.py` (`scan`, `config_values`), `src/lodge/gitstore/attributes.py` (the key on the sources alone; one `config --list -z` and one `var -l`), `src/lodge/gitstore/checkout.py` (`disk_tree` calls `disk.py`; lines removed, none added), `src/lodge/cli/parser.py` (the parser for the named command), `tests/gitstore/test_identity_property.py` (the review's A6: one line)
- Test: `tests/gitstore/test_identity_lazy.py` (new), `tests/gitstore/test_identity_links.py` (new), `tests/gitstore/test_identity_gitlinks.py` (new), `tests/gitstore/test_git_many.py` (new), `tests/gitstore/test_flag_scan.py` (new), `tests/test_parser_named.py` (new)

**Interfaces:**
- Consumes: Task 8b's `CheckoutIdentity`, `CheckoutListing`, `BranchListing`, `Flags`, `Conversions`, and its tests as the oracle where they agree with the exact readers; `disk_tree` and `read_tree` as the exact readers.
- Produces:
  ```python
  # gitstore/git.py
  def run_many(calls: Sequence[Sequence[str]], cwd: Path) -> list[subprocess.CompletedProcess[bytes]]
      # starts every call before waiting for any; results in the order of `calls`;
      # request_exit waits until all have returned; a missing git raises GitMissing as attempt does
  # gitstore/disk.py
  def walk(root: Path) -> DiskWalk          # names with kinds, the real folders reached, the folders that could not be listed
  def read_at(walked: DiskWalk, path: str, *, attachment: bool = False) -> bytes | None
      # None (deleted) unless every folder on the path is a real folder the walk reached; never follows a link;
      # a link's target bytes, an empty file for anything not regular, as disk_tree reads them;
      # never blocks: the open is nonblocking and the descriptor's own type decides (Links, below)
  # gitstore/flags.py
  def scan(raw: bytes) -> Flagged         # equals Task 8b's decode loop on every input
  def config_values(raw: bytes) -> Mapping[str, str | None]   # `config --list -z`; a key with no value is None, git's true
  # gitstore/identity.py
  class Committed:                        # per store object; at most the two most recent commits
      def tree_id(self, rev: str | None) -> str            # `rev-parse rev:lodge`, EMPTY_TREE when absent or not a tree
      def listing(self, rev: str | None) -> CommittedListing   # `ls-tree` once per commit ID, each entry with its kind
  ```
- Lazy listings (the review's P1 item 1): `identities()` resolves `HEAD` and the published commit as today and takes both idents without an `ls-tree` of the published commit; `listings()` builds a mapping only when called, from `Committed.listing`, so a published commit equal to `HEAD` costs no second `ls-tree`; until Task 11 the walk still needs the base's names, so `HEAD`'s mapping is still built in `identities()`.
- One snapshot of git's index (plan fix 6, `measure/race.py`; the review confirmed it): `diff-index --cached`, `diff-files`, `ls-files -t -v`, `config --list -z`, `var -l`, and the `rev-parse` and `merge-base` calls start together through `run_many`, with commit IDs pinned; the stat of git's index file (inode, size, `mtime_ns`, `ctime_ns`) is taken before the first starts and after the last ends; when they differ, the whole group and every result that depends on it (flags, conversions) are discarded and run again, at most twice, and then the identity, `listings()`, and `texts()` all take one exact tree from `disk_tree`, so a `git add` between two calls never hides an edit.
- Conversions keyed on their sources (P1 item 3): the key is the configuration values, the `git var` values, every source file's stat and bytes, the index-only attributes files, and the index stat, without the path set; the path set is built, and `check-attr` run, only on a miss; nested `.gitattributes` come from the walk's names and from `scan`'s attributes entries, never from an `rsplit` of every path; where a source converts, the paths it may convert are read from disk (d-dqpf59, CONV-1).
- Flags (P1 item 4): `scan` counts the entries and the `H` entries and finds `.gitattributes\0`; only when the counts differ does it run Task 8b's loop.
- Merged configuration calls (P1 item 5): one `config --list -z` gives `core.autocrlf` and `core.attributesFile` in git's spellings, a key with no value counting as true (review A2); one `var -l` gives `GIT_ATTR_GLOBAL` and `GIT_ATTR_SYSTEM`, a variable it omits being asked with `git var NAME` as today; a failing call converts every path.
- Links (review A1 and R3): `disk_tree` and the overlay read through `disk.py` only; a folder is entered with `O_NOFOLLOW | O_DIRECTORY` relative to its parent's descriptor and a file opened with `O_RDONLY | O_NOFOLLOW | O_NONBLOCK | O_CLOEXEC` relative to its folder's descriptor, then `fstat` of the opened descriptor decides: bytes are read only from a regular file, and anything else (a FIFO, socket, or device, whatever the walk saw before) gives the empty text `disk_tree` gives; an open that fails with `ELOOP` is a link, read with `readlink` relative to the folder's descriptor (the review of 6b and 7, F10: `O_NOFOLLOW` alone blocks on a regular file swapped for a FIFO before the open); an overlay path, attachment or not, whose folders are not all real folders the walk reached is deleted, never read; a folder swapped for a link after its parent was listed is read as the link it now is; a folder that cannot be listed hides its base files as `disk_tree` does (review A3); `disk_tree`'s result changes only in that swap.
- Gitlinks (review A4 and R13): `Committed.listing` keeps each entry's kind; in checkout mode a base entry that is not a blob always joins the overlay, so the disk decides, as `disk_tree` does; in branch mode such an entry keeps `read_tree`'s representation, its key the empty text's blob ID `blob_id(b"")` (`e69de29b...`), never the gitlink's commit ID, and `texts()` gives it empty text without asking `cat-file`; a checkout gitlink whose folder is absent, empty, or populated is whatever the disk holds there.
- The parser: `parse` builds a parser holding only the subcommand that `argv[0]` names, with all its arguments; `--help`, `-h`, `--version`, no command, and a name that is not a command take the full parser; every help and error text is unchanged (14.4 ms against 1.9 ms, `measure-6b/parser_partial.txt`).
- R11, as ruled (STALE-1 is with the author; the build brief carries the ruled sentence whole, never a bare letter; STALE-1's answer A is R11-B, its answer B is R11-A):
  - R11-A: "The fast identity reads and hashes every working-tree file under `lodge/` on every read, whether or not a conversion source is present now, since a conversion source removed after git wrote its index leaves no trace and can make git's index text differ from the disk's."
    `identities()` then reads every file through `disk.py` in every configuration, stat-clean files included.
  - R11-B: "With no conversion source present, the five indexed reads take a file that git's index records as stat-clean at git's index blob, as `git status` does; after a conversion source is removed without the file being touched or staged again, such a read prints git's index text, which differs from the disk's only for `ident`, `filter`, and `working-tree-encoding` histories and never for line ends, which lodge's parser normalises; the gate and `add` read every file exactly."
    It is recorded as the stated exception to d-dqpf59 and d-rs76ks before the build uses it.
  - Under both, the gate, `add`, and every other exact reader read bytes.
- Untouched: the gate, `add`, `trees()` but for `disk.py`, and branch mode's tip resolution.

- [ ] **Step 0:** skeleton.
- [ ] **Step 1: Write the failing tests** ("agrees" means equal to the exact reader's tree, `disk_tree` in checkout mode, `read_tree` in branch mode):
  `test_identity_lazy.py`: `test_identities_run_no_ls_tree_for_published` (a patched runner counts `ls-tree` calls: clean store with published equal to `HEAD`, one; then `listings()`, still one; published behind `HEAD`, `identities()` one and `listings()` two); `test_lazy_listings_agree` (clean, an unstaged edit, an untracked file, a staged deletion, published behind `HEAD`, branch mode); `test_staged_between_diff_calls_is_seen` (the runner runs `git add` of an edited record after the first call of the group returns: agrees; fails on Task 8b's code); `test_index_changing_every_time_falls_back_to_exact` (the runner touches git's index file after every group: the identity, `listings()`, and `texts()` all agree with one `disk_tree`, and three groups ran); `test_conversion_key_takes_no_paths` (a second identity on one store object makes no `check-attr` call and never builds the path set, checked by a path source that raises); `test_nested_attributes_found_without_a_path_scan` (`lodge/decisions/.gitattributes` with `*.md text eol=crlf`, once on disk only and once in git's index only: agrees); `test_bare_autocrlf_key_converts` (review A2: a `[core]` section with a bare `autocrlf` line, a CRLF checkout of one record, `git status` clean: agrees); the R11 regression tests, each history made as the review of 6b and 7 made it (`scratch/67/probe_gitlinks_history.py`: the converted file written, aged, staged, its untracked attribute source then removed, a fresh store object), for four attributes: `ident`, `working-tree-encoding=UTF-16`, a length-preserving `filter`, and `text eol=crlf`; with R11-B, `test_removed_attributes_follow_the_index` (the first three: the five indexed reads print git's index text, the ruled exception; CRLF: they agree; the gate and `add` agree with `disk_tree` in all four), or with R11-A, `test_removed_attributes_agree` (all four: every read, the gate, and `add` agree) and `test_every_file_read_without_a_conversion_source` (a reader that counts calls sees every file under `lodge/` on a clean store with no conversion source).
  `test_identity_links.py`: the three review A1 probes, `test_folder_replaced_by_symlink_to_copy`, `test_folder_replaced_by_symlink_to_other_content`, and `test_attachments_folder_symlink`; `test_folder_link_to_outside_is_never_read` (a link to a folder outside the repository holding `old.md`: no outside bytes in the listing or `texts()`); `test_link_inside_an_attachment_path`; `test_folder_swapped_for_link_during_the_walk` (a patched `os.scandir` swaps a listed folder for a link before it is entered: both readers give the link, never the files behind it); `test_unlistable_folder_agrees` (review A3, skipped as root); `test_fifo_agrees` (kept from Task 8b); `test_regular_file_swapped_for_fifo_before_open` (F10: a patched hook replaces a file the walk classified as regular with a FIFO between the classification and the open; the identity, `texts()`, the gate's reader, and `add`'s run in a child process killed after 10 s: each returns the empty text `disk_tree` gives, and none blocks; fails with `O_NOFOLLOW` alone).
  `test_identity_gitlinks.py` (review A4 and R13, each in checkout and branch mode against the exact readers, with a gitlink commit absent from the object database and `diff.ignoreSubmodules=all`): `test_empty_submodule_folder`; `test_populated_submodule`; `test_absent_submodule_folder` (checkout: the folder removed from disk agrees with `disk_tree`); `test_branch_gitlink_key_is_empty_text` (branch mode: the key is `blob_id(b"")`, not the commit ID); `test_submodule_commit_absent_from_the_object_database` (branch mode: `texts()` gives the empty text `read_tree` gives, and no `cat-file` request for it).
  `test_git_many.py`: `test_results_in_call_order`; `test_all_started_before_any_awaited` (a patched `Popen` records starts and waits); `test_request_exit_waits_for_every_call`; `test_missing_git_raises_git_missing`.
  `test_flag_scan.py`: `test_scan_equals_the_loop` (500 seeded buffers in `ls-files -t -v -z` form with every tag git prints, lower-case tags, root and nested `.gitattributes`, and paths that are not UTF-8); `test_config_values_spellings` (a bare key is None, `autocrlf=` the empty string, `input`, `true`, `yes`, `on`, `1`, `false`, `no`, `off`, `0`, values holding newlines).
  `test_parser_named.py`: `test_help_texts_unchanged` (`lodge --help` and `lodge <command> --help` for every command, byte for byte against the full parser); `test_errors_unchanged` (an unknown command, a missing argument, and a bad option for each command, standard error and exit status against the full parser); `test_named_parser_builds_one_subcommand`.
  `test_identity_property.py`: the review's A6, `(repo / ".gitattributes").unlink(missing_ok=True)` at the top of each sequence; the review's four mutants (no diff calls, no flagged paths, no untracked paths, no conversions) each fail it, run once and recorded in the report.
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement; the Task 8b tests pass unchanged except where they encoded a disagreement with the exact readers, each such edit listed in the report.
- [ ] **Step 4:** gate; at `s90000`, isolated configuration, `identities()` on a new store object, clean and with one edit, best of three, with each stage's share: expected about 0.34 s against 0.785 s with R11-B, about 3.1 s with R11-A; the same under `core.autocrlf=input`, expected about 3.1 s (CONV-1); `lodge guide --read` and `python -c "import lodge.main"`, best of nine: about 0.16 s and 0.145 s, the first about 0.012 s below today; above 0.45 s for the R11-B identity, the report gives the stage table and the ledger names it.
- [ ] **Step 5:** commit, push.

### Task 9c: The parse lookup in one scan

Built after Task 8c and before Task 10a; it changes no port and no output.

**Files:**
- Modify: `src/lodge/gitstore/index_parses.py` (`find_parses`)
- Test: `tests/gitstore/test_index_parses.py`

**Interfaces:**
- `find_parses(db, keys)` keeps its signature, its result, and `IndexDB.parses`'s explicit read transaction around it (`BEGIN ... COMMIT`, so a clear committed meanwhile is not seen).
  When `len(keys)` is at least `SCAN_FROM = 1_000` and `len(keys) * 4` is at least `SELECT max(rowid) FROM parses` (an empty table counts as 0), it reads `SELECT path, blob, value FROM parses ORDER BY rowid` once, keeps each row whose whole `(path, blob)` is in the set of requested keys, and decodes that row's value on its own, `from_plain(json.loads(value), CORE_CLASSES)` with the validators, the row's key and its decoded value carried together; the decoded value is then admitted by today's check, `value is None or isinstance(value, (Area, Decision, Problem, SpecEntry, Thread))`, in both the scan and the per-key path (the review of 7b, B1: `123`, `"text"`, `{}`, `[""]`, and a valid non-parse dataclass decode without raising); a row whose decode or validation raises, or whose value the check refuses, is a miss for its own key alone; a decoded `None` is a hit, as today; duplicate requested keys and rows of other blobs change nothing.
  Below `SCAN_FROM` keys, or below that fraction of the table, it keeps the per-key `SELECT`.
  The rowid bound is one b-tree probe; a cursor SQL error preserves the scan hits already decoded (Task 9c review M2 and M3).
  No values are joined into one document (the review's F1).
- Measured at 160,800 keys on 094e9ce, with the admission check: 1.089 s against 1.435 s for the per-key lookup, its result equal to the per-key lookup's (plan fix 7b, `scan7c.txt`).
  The scan reads every row, so its cost grows with the table; the cap (Task 9, d-4pbeax) bounds the table, and Step 4 reports the scan with the table at the cap.

- [ ] **Step 1: Write the failing tests:** `test_scan_equals_per_key` (a table of 2,000 units with older blobs of the same paths, a `None` parse, and a Problem; 1,500 requested keys, 20 of them absent and 5 requested twice: the result equals the per-key result); `test_one_bad_value_is_one_miss`, one case each, every other key found and equal to the per-key result: a truncated value; the review's `null,null` (valid only when joined); the pair `null,"foo` and `bar"` in adjacent rows (valid only when joined, with the right count of elements); a value of valid JSON that fails a validator; each of `123`, `"text"`, `{}`, `[""]`, and a valid `Level1` (decodes, refused by the admission check); `test_scan_reads_once` (a connection wrapper counts one scan plus the size probe when both thresholds hold, and one per key otherwise (with the size probe for requests at least `SCAN_FROM`)); `test_scan_inside_one_read_transaction` (the read transaction's snapshot is established by a first `SELECT` inside it, then another connection clears and commits, then the scan runs: the result is the one from before the clear; and a clear committed between the `BEGIN` and the first `SELECT` gives misses only, which the read answers from memory; the review of 7b, B3).
  Mutants run once and recorded in the report, each failing a test: values joined into one `json.loads`; rows matched on the path alone; an exception ending the whole scan; the admission check removed from the scan.
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; at `s90000`, the whole state's lookup, best of three, beside 1.435 s, and once more with older units filling the table to the cap.
- [ ] **Step 5:** commit, push.

### Task 10a: Stored states for `show`, `waiting`, `threads`, and `thread`

**Files:**
- Create: `src/lodge/app/read_model.py` (rows, facts, and answers from a checked `State`), `src/lodge/app/indexed.py` (the indexed reads), `src/lodge/gitstore/index_states.py` (states, buckets, answers, citers, facts, eviction)
- Modify: `src/lodge/app/index_types.py` (`Row`, `StoredState`, `StateFacts`), `src/lodge/app/ports.py` (`Index` gains the methods below), `src/lodge/app/__init__.py`, `src/lodge/app/lodge.py` (`read_model: bool = True`; the viewer's `Lodge` passes False), `src/lodge/app/state.py`, `src/lodge/main.py` (the viewer's factory without the read model), `src/lodge/cli/commands.py` (the four reads run the deferred keep after their explicit flush), `src/lodge/gitstore/index_space.py` (the cap's condition)
- Test: `tests/app/test_read_model.py` (new), `tests/app/test_indexed_reads.py` (new), `tests/gitstore/test_index_states.py` (new), `tests/gitstore/test_index_concurrency.py` (new), `tests/e2e/test_indexed_reads.py` (new)

The fix round additionally modifies `app/reads.py`, `app/writes.py`, and `app/threads.py` to forward the build's starting epoch to subsequent `snapshot_of` calls, `app/index_lookups.py`, `gitstore/index_db.py`, `gitstore/index_schema.py`, and `tests/app/fake_index.py` for the existing lookup and writer hand-offs.
Its regression tests are `tests/gitstore/test_index_shared_buckets.py` and `tests/gitstore/test_index_closed_streams.py`; existing writer interception and bucket-corruption tests in `tests/gitstore/test_indexed_cli_contract.py` follow the new storage layout.
`index_file_cap(files: int) -> int` in `gitstore/index_space.py` names the unchanged cap formula and is used by the cap tests.
An empty parse-only write returns before taking the writer lock.
Marker and non-empty parse-only writers receive the caller's used parses and starting epoch; after a clear they insert that complete working set, otherwise only misses.

**Interfaces:**
- Consumes: Task 8b's `identities`, `listings`, `texts` as Task 8c leaves them (`listings()` builds mappings on first use, so a stored-state hit calls `identities()` only); Task 9's `Index`, codec, and failure modes, with Task 9c's lookup; Task 4's shortcut; Task 5's `family`, `code_tokens`, `show_many`, and the `Shown` fields it adds.
- Produces:
  ```python
  # app/index_types.py
  @dataclass(frozen=True)
  class Row:                                   # the derived part of one record in one state
      key: FileKey
      status: str; decided_by: str | None; date: str | None; scope: str | None; area: str | None
      flags: tuple[str, ...]; quote: Quote | None
      links: tuple[tuple[str, str, str], ...]  # Level3.links
      changed_by: tuple[str, ...]              # for level 2 of an entry
      areas: frozenset[str]                    # for the area filter
  @dataclass(frozen=True)
  class StateFacts:                            # one state's own facts, keyed by its ident alone, immutable (d-dxqxsn, d-4j98ph)
      status: Mapping[str, str]
  @dataclass(frozen=True)
  class StoredState:                         # its row is the completeness marker, written last in keep_state's transaction
      key: str                                 # sha1 of current ident, published ident, settings digest
      current: str; published: str             # the two idents, for the facts lookup
      promised: tuple[int, int, int]           # buckets, answers, and citer rows kept with it
      valid_from: str | None                   # ISO datetimes with offsets (d-faakge)
      valid_until: str | None
      codes: Mapping[str, tuple[str, ...]]     # lower-cased code -> IDs
      citers: Mapping[str, int]                # lower-cased code or family root -> its number of citers; the IDs are in citer rows
      unrecorded: tuple[Problem, ...]
      threads: tuple[str, ...]                 # complete thread IDs, including closed threads
  def level1_of(row: Row, record: Decision | SpecEntry) -> Level1     # equals core.level1 for that state
  class Index(Protocol):                       # in addition to Task 9's
      def keep_parses(self, parsed: Mapping[FileKey, Parsed | None], *, files: int,
                      used: Mapping[FileKey, Parsed | None] | None = None,
                      epoch: int | None = None) -> None
      def reading(self) -> ContextManager[None]   # BEGIN ... COMMIT around a read's lookups, ROLLBACK in a finally
      def seen(self, key: str) -> bool
      def mark_seen(self, key: str, parses: Mapping[FileKey, Parsed | None],
                    facts: Mapping[str, StateFacts], *, files: int,
                    used: Mapping[FileKey, Parsed | None] | None = None,
                    epoch: int | None = None) -> None
          # `files` is the caller's tree file count, required for every writer
      def state(self, key: str) -> StoredState | None
      def rows(self, key: str, ids: Collection[str]) -> dict[str, Row] | None
          # None for missing or undecodable buckets; {} proves the IDs absent in intact buckets
      def all_rows(self, key: str) -> dict[str, Row]
      def answer(self, key: str, name: str) -> object | None   # "waiting", "threads", "thread:<id>", decoded with the classes app passes
      def citing(self, key: str, code: str, limit: int | None) -> tuple[str, ...] | None   # newest first; None when the row is missing
      def facts(self, ident: str) -> StateFacts | None
      def keep_state(self, state: StoredState, rows: Mapping[str, Row], answers: Mapping[str, object],
                     citing: Mapping[str, tuple[str, ...]], facts: Mapping[str, StateFacts],
                     parses: Mapping[FileKey, Parsed | None], misses: Collection[FileKey], epoch: int, *, files: int) -> None
          # one BEGIN IMMEDIATE transaction: INSERT OR IGNORE of the parse units in misses and of the facts,
          # then the eviction (DELETE of the oldest state's own rows, by its key), then this state's own rows
          # (replacing them whole if the key exists), and last its state row (invariants 1 to 3);
          # `parses` and `facts` hold every unit and fact the build used, hits included; when `meta.epoch`, read inside
          # this transaction, differs from `epoch`, the value of `Index.epoch()` the build read before its first lookup,
          # all of them are written (d-c6cegr; the third recheck's R5, the fourth's W1);
          # a keep that finds the index over the cap clears it first (Task 9)
  ```
- A read (`show`, `waiting`, `threads`, `thread`) with an index and the read model on: `identities()`; the key; inside `reading()`, a stored state whose validity interval holds `clock.now()` answers through lookups (one bucket per ID, the parse rows of the records printed, and for a coded record the family from `codes` and the first ten citers from `citing` with the count from `citers`); any lookup that finds less than the state promised (a bucket, answer, citer row, or parse unit missing or undecodable) ends the transaction and the whole read runs in memory (invariant 6); otherwise the read answers from memory, built from `listings()` and the parse cache, and keeps by SECOND-1: when the index holds no marker for the state's key (the full stored-state key, in the build's own index file), the read writes one (`seen(key, at)`, the 64 newest kept, the oldest deleted in the transaction that adds one), in one short `BEGIN IMMEDIATE` transaction with the parse units it missed and any facts it computed (Task 10c), and builds no rows, buckets, answers, or citers; when it holds a marker, the read returns its answer together with a deferred keep (below), and the command runs that keep only after its whole output was written and flushed without error.
  The deferred keep (the review of 7b, B5): a closure over the read's checked `State`, its listings, its parses, its `now`, its epoch, and its stored-state key, all pinned when the read answered; it never reads the files, the listings, or git again, so an edit during the output or the keep only leads the next identity to another key; inside it, the whole construction of rows, buckets, answers, citers, and facts, their encoding, and `keep_state` run, in that order, all within one boundary that catches every ordinary exception (not `KeyboardInterrupt` or `SystemExit`), prints nothing, and leaves the command's own exit status, nonzero ones included; it is called from the command's success path after the explicit flush, never from a `finally`, an `atexit` hook, or a release hook, and never after a write or flush that failed.
  `keep_state` requires the caller's tree file count as keyword-only `files: int`; the read model's constructors are called only from inside the deferred keep, never while answering.
  A clear deletes the `seen` table with the others; eviction leaves markers alone; a marker never answers a read, it only lets the next read keep.
  The cap (the review of 7b, B2), replacing Task 9's condition "and at least one state kept since the last clear": every write transaction (a marker's, a parse-only writer's, and a keep) first compares the used pages with `INDEX_FILE_CAP`, and when over it clears, provided the units inserted since the last clear (parse units and facts, counted in `meta.written`, which the clear resets to 0 and each insert raises by the rows it inserted) number at least the tree's file count, or a state was kept since the last clear; so a read that writes a whole working set after a clear is not cleared away by the next writer, and growth stays within the cap plus one working set whether or not any state is ever kept.
  `meta.kept` keeps its meaning, a complete state kept (Task 9 fix report, I4).
  `keep_state` is called only from the deferred keep, so no changed read builds or writes any row or citer before it prints.
  Building a state uses Task 4's shortcut when the two listings' blobs and attachments are equal, whatever their idents (d-c0q20c).
- Citers (d-4j98ph, the rechecks' N4, R2, and V5): built with the state, one pass over each record's `code_tokens(title) | code_tokens(statement)` against the state's codes and family roots (every prefix of a code that ends before a `.`), each one's citers outside its family newest first by `(date, ID)`, one row per code and per family root, empty ones included; so `show CODE` and Task 10b's code queries never scan texts.
- Validity (d-faakge): `valid_from` is the latest date among decisions new against the published state that is not after the build's `now`, `valid_until` the earliest that is after it; compared as timezone-aware datetimes; a missing end is open.
- What equals what (the correctness review's I4): indexed results print the same text through `cli/output.py` and `cli/thread_output.py` as in-memory results; their `Read.statuses` is empty and the viewer-only `Shown` fields keep their defaults; the differential tests compare printed text.
- An answer's `Read` is rebuilt at read time with the store's live `freshness()` and the state's `unrecorded`.
- Buckets (d-c4w7xy, amended by the Task 10a fix-round coordinator ruling): 1,024 pointers per state to content-addressed shared immutable blobs, by the ID's last two characters, compact JSON (`json.dumps(..., ensure_ascii=True, separators=(",", ":"))`, as Task 9 stores parses) of `{id: to_plain(row)}`; `KEPT_STATES = 4` (d-hf2fms, d-ytf272), first in first out by a sequence number set at each keep, so a re-kept state is the newest (d-gvz66f); the oldest is evicted in the transaction that keeps a fifth, as invariant 3 says: its state row, bucket pointers, answers, and citer rows, each table keyed by the state's key, then bucket blobs with no remaining pointer; parse units and facts stay (invariant 1).
- Why the hits need no check (the second recheck's V1 and V2): a parse unit or fact found in the file stays there until a clear, and a clear raises the epoch, so `keep_state` inserts only the misses its build found unless the epoch moved, and then writes everything it used.
- The viewer, `spec`, `timeline`, `draft`, `check`, `id`, `add`, and the gate never read rows (d-m0g9tx).

- [ ] **Step 0:** skeleton.
- [ ] **Step 1: Write the failing tests:** `test_read_model.py`: `test_level1_of_row_equals_core_level1` (every record of four sample stores and of a made-up 500-record store with replaced, narrowed, retired, flagged, confirmed, doubted, and failing records); `test_level3_links_equal`; `test_answers_print_as_in_memory`.
  `test_indexed_reads.py` (a fake index): `test_seen_state_reads_no_snapshot` (patched `assemble` never called on the third `show`, after the second's keep was seen to commit); `test_outputs_print_as_in_memory` (200 seeded commands over the 500-record store: `show` of IDs, codes, unknown refs, several refs; `waiting`; `threads`; `thread`); `test_validity_interval` (a new decision dated 10 minutes after the build: it fails check 1; the clock 11 minutes later: rebuilt, it does not; the clock 1 minute before the build: rebuilt); `test_settings_change_is_another_state`; `test_missing_bucket_falls_back_to_memory`; `test_missing_citer_row_or_parse_falls_back_to_memory`; `test_show_code_reads_citers_without_texts` (12 citers, among them one that cites the code only in its statement: patched `assemble` and `code_tokens` not called on the third `show`, after the second's keep was seen to commit, ten citers and the count 2 printed as in memory; the same for the code `A`); `test_equal_listings_with_different_idents_take_the_shortcut` (an edit read, then committed: `load` of the published tree not called); `test_first_read_keeps_only_a_marker` (the first `show` of a new state: a connection wrapper sees one write transaction holding the marker and parse units and no bucket, citer, answer, or state row); `test_second_read_keeps_after_its_output` (the second `show`: the whole output is written and flushed, recorded by a stream wrapper, before the first call of any read-model constructor and before the first SQL statement of `keep_state`, both instrumented; the third `show` is a seen read that writes nothing); `test_first_read_builds_no_rows` (the first `show`: the read-model constructors are never called); `test_failed_keep_keeps_output_and_status` (a failure injected in turn into row building, bucket encoding, citer building, answer building, facts encoding, and each SQL statement of `keep_state`, with and without an eviction: the printed output and exit status equal `LODGE_INDEX=off`'s, for a `show` that exits 0 and for a `show` of several refs, one unknown, that exits nonzero, and `state()` finds nothing new); `test_keep_uses_pinned_inputs` (a file edited after the second read answered and before its deferred keep runs: the kept state is the one under the second read's key, equal to a full build of the files before the edit, and the next read builds the edited state); `test_output_failure_keeps_nothing`, one case each, no constructor called and no keep begun: a stream that accepts the writes and raises on the flush; Python's standard output closed; a broken pipe with Python's default handling (the exception); a broken pipe with `SIGPIPE` at its default disposition (the process ends by signal 13, and the next read finds no new state); `test_killed_during_keep_leaves_no_state` (a child process killed with `SIGKILL` inside the keep's transaction, after its buckets: the next read finds no state row and prints as `LODGE_INDEX=off`); `test_marker_bounded_and_cleared` (65 states seen once: 64 markers; a clear removes them); tests whose subject is not the keep's timing preseed a complete state through `keep_state` directly.
  `test_index_states.py`: `test_kept_states_constant`; `test_seen_read_writes_nothing` (no write transaction begun, recorded by a connection wrapper, and the main file and its `-wal` unchanged, after a `git status` that rewrote git's index file too; a read that finds a marker but no state is not a seen read); `test_first_sightings_alone_stay_under_the_cap` (from an empty index and again just after a clear, 50 states each seen once with a cap of 16 MiB and parse units filling it: used pages never pass the cap plus one working set, the epoch rises, `meta.kept` stays 0, and a second and third read of the last state keep it and then answer from it); `test_bucket_by_last_two_characters`; `test_eviction_deletes_only_the_states_own_rows` (after an eviction every parse unit and every facts row is still there, and no row of any table carries the evicted key); `test_revert_to_the_evicted_states_contents` (S0 holds `r` at `b1`, S1 to S4 hold `b2`, evicting S0, then the edit reverted: the new state's `keep_state` inserts nothing for `r`, the parse unit of `(r, b1)` and the facts of its published ident are found; Task 10b's `test_revert_after_eviction_is_found` checks the search); `test_rekeep_replaces_the_state_whole` (a key kept again with other rows: only the new rows remain, and it is the newest for first in, first out); `test_keep_after_another_process_cleared` (process A takes hits, process B clears, A keeps: every key of A's rows has its parse row, and the facts of its published ident, a hit for A, are present); `test_clear_between_the_parses_and_facts_lookups` (A reads the epoch, takes parse hits, B clears, A takes its facts lookup and keeps: every key of A's rows has its parse row; the interleaving of the fourth recheck's `epoch_model.py`).
  `test_index_concurrency.py` (two connections, deterministic interleaving): `test_reader_keeps_its_snapshot_across_a_commit` (inside `reading()`, after the state row and one bucket, another connection re-keeps the same key with other rows and commits; the reader's next bucket comes from the build it began with, `in_transaction` holds throughout, and the printed output equals the in-memory read at the reader's own `now`; the same steps on a connection in Python's default mode read the new bucket, so the test fails without the explicit transaction (the second recheck's V3)); `test_eviction_between_lookups_cannot_split_a_read` (reader inside `reading()`, another connection keeps a fifth state that evicts the reader's: the reader finishes on its snapshot, and the printed output equals `LODGE_INDEX=off`); `test_unit_found_by_one_process_survives_another_keep` (process A finds `(r, b1)` as a hit, process B keeps a state whose eviction removes the last state holding `r` at `b1`, then A keeps its state: every key of A's rows has its parse row); `test_keep_state_interrupted_at_each_statement` (for each k, a failure injected after the k-th SQL statement of `keep_state`, with and without an eviction in it: `state()` finds nothing new, the evicted state is still whole, and the next read prints as with `LODGE_INDEX=off`); `test_two_builders_of_one_state` (both keep; the second replaces the first whole).
  `tests/e2e/test_indexed_reads.py`: `test_edit_on_disk_then_show_sees_it`; `test_commit_then_show_sees_it`; `test_branch_mode_after_fetch_sees_the_new_tip`; `test_viewer_factory_has_no_read_model`.
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 3a: Complete Task 9's hand-offs before the gate.**
  I4/M10, quoted from `task-9-fix-report.md`: "Task 10a must wire the cap, clear, and keep callers, including parse-only writers, use the tree's file count, name `INDEX_FILE_CAP`, and make `meta.kept` mean a state kept."
  Wire `prepare_keep` into both `keep_state` and parse-only keeps (`add`, the gate, and every non-indexed read), within their write transaction, with the file count supplied by the tree's caller rather than the number of misses.
  Set `meta.kept` only when a complete state is kept, and clear by the condition in Interfaces (a working set inserted since the last clear, or a state kept), so invariant 1's unit growth is bounded by the end of this task even when no state is ever kept; test parse-only writers and first sightings crossing the cap, with and without a state keep.
  M9, quoted from `task-9-recheck.md`: "batching gains about 0.05 s".
  That measured gain supports deferring batched SELECTs; the previous report's claim that per-key error isolation requires per-key SQL is superseded, and Task 9c (plan fix 7b) is the lookup redesign: one ordered scan, each row decoded on its own.
  The parse-only opening path no longer computes or threads a settings digest; add a settings digest, `sha1(repr(settings).encode()).hexdigest()` (never `to_plain`, Task 9 review M5), when constructing the stored state's key and exercise `test_settings_change_is_another_state`.
- [ ] **Step 4:** gate; the replay at all three sizes for the four reads, `show A` included, `cold`, `seen`, and `changed`, recorded as provisional (d-26e6zj), with the phase times of one `changed` read, `keep_state`'s inserts and its eviction apart (the second recheck's V2); the read that clears is a cold read and is reported with the cold ones (d-e3stjn); at `s90000`, the first read of a changed state (prints and ends), the second (prints, then ends after its keep), and the third (seen), each timed to its exit, with the complete keep's parts (rows as `Row`, buckets, answers, citers with family exclusion and roots, facts, and `keep_state`'s transaction with its eviction and any clear apart); the kept state's bytes, how many states fit under the cap, and the clears after ten such cycles; plan fix 7b's 8.764 s is a partial proxy, not this.
- [ ] **Step 5:** commit, push.

### Task 10b: Indexed search

**Files:**
- Create: `src/lodge/gitstore/index_words.py` (FTS5 candidates and word sets)
- Modify: `src/lodge/app/indexed.py` (search), `src/lodge/app/index_lookups.py` (query fallback and metadata-only empty-search candidates, Task 10b review fix round), `tests/gitstore/test_identity_property.py` (Task 10b review M1), `src/lodge/core/words.py` (`parse_words(parsed) -> tuple[str, str]`, the title's and statement's words space-joined, a pure function in `core`, which `gitstore` may import, so no `app` module computes words and `app/state.py` and `app/read_model.py` need not import each other; the second recheck's V8), `src/lodge/core/__init__.py`, `tests/app/fake_index.py` (the extracted fake index's `candidates`), `src/lodge/app/ports.py` (`Index` gains the method below; `keep_parses` and `keep_state` preserve Task 10a's required keyword-only `files: int`, so no caller or earlier test changes), `src/lodge/gitstore/index_parses.py` and `src/lodge/gitstore/index_states.py` (words written with their parse unit), `src/lodge/gitstore/index_db.py` (the schema number rises, so Task 9's files are another build's), `src/lodge/app/lodge.py` (both search entry points route to indexed), `src/lodge/gitstore/index_schema.py` (FTS creation), `src/lodge/gitstore/index_space.py` (coordinated FTS drop and re-creation on whole-index clear), `src/lodge/cli/commands.py` (search flushes output before its deferred keep)
- Test: `tests/gitstore/test_index_words.py` (new), `tests/gitstore/test_index_words_faults.py` (new), `tests/app/test_indexed_search.py` (new), `tests/e2e/test_index_property.py` (new), `tests/e2e/index_property_support.py` (new helper), `tests/app/test_indexed_search_review.py` (new, review regressions), `tests/e2e/test_search_deleted_file.py` (new, real deleted-record regression)

**Interfaces:**
- Consumes: Task 6's `rank`, `Candidate`, `parse_query`, `needs_memory`, `Filters`, and `search_many`; Task 5's `family`; Task 9's `keep_parses`; Task 10a's states, `rows`, `all_rows`, `codes`, `citing`, and `keep_state`.
- Produces:
  ```python
  class Index(Protocol):                       # in addition to Task 10a's
      # keep_parses(parsed, *, files: int) and
      # keep_state(state, rows, answers, citing, facts, parses, misses, epoch, *, files: int), unchanged:
      # gitstore computes words[key] = core.parse_words(parsed[key]) for each parse unit it inserts,
      # inserted with the same rowid as the parse row of that key, in its transaction, only when that row was inserted (invariant 1)
      def candidates(self, words: Collection[str], every: bool) -> dict[FileKey, tuple[frozenset[str], frozenset[str]]] | None
          # the keys with any (or every) word, with their title and statement word sets; None without FTS5
  ```
- Words (d-eby5pb, d-4j98ph): FTS5 table `(title, statement)` with `tokenize='ascii'` and no key column, its rowid the parse row's, matched with `{title statement}:` column filters (the second recheck's V7), text `" ".join(sorted(core.words(...)))`, one row per parse unit, immutable like it, so a parse unit present means its words are present, and no FTS row is ever deleted (d-t3afj1); with no FTS5 (`sqlite3.OperationalError` creating the table) `candidates` returns None and the search runs in memory.
- An indexed search: when `needs_memory` holds for any query, or `candidates` is None, the whole search runs in memory (d-rs76ks); otherwise candidates are the keys (through the shared rowid) holding any query word, the exact ID if it exists, the family from `codes`, and for a code the citers from `citing`; their rows in this state whose `key` equals the candidate key (an older parse of a record is not a candidate); a phrase checks `tokens` on the parse's text; `rank` orders, with the word sets from `candidates`, the same function as in memory.
  An empty query or a filter-only search reads `all_rows`.
- The property test of d-rs76ks lives here, over every read, because only now does every read go through the index.

- [ ] **Step 0:** skeleton.
- [ ] **Step 1: Write the failing tests:** `test_index_words.py`: `test_ascii_tokenizer_returns_core_words` (words with digits, non-ASCII letters, and combining marks come back as the same set); `test_any_and_every`; `test_path_words_are_not_candidates` (`lodge`, `decisions`, and `md` match no record that lacks them in its title and statement); `test_words_row_shares_the_parse_rowid`.
  `test_indexed_search.py` (a fake index): `test_search_prints_as_in_memory` (300 seeded searches over the 500-record store: words, `--phrase`, codes with and without families, a family root no record holds as its own code, function-word phrases and codes, empty queries, every filter, several queries); `test_older_parse_of_a_record_is_not_a_candidate`; `test_needs_memory_queries_run_in_memory` (a patched `candidates` must not be called); `test_without_fts5_runs_in_memory`; `test_revert_after_eviction_is_found` (an edit, `KEPT_STATES + 1` further states, the edit reverted on disk: a search for a word of the reverted record lists it as in memory); `test_words_rows_after_a_clear_and_another_keep` (Task 10a's two cross-process keeps, `test_keep_after_another_process_cleared` and `test_unit_found_by_one_process_survives_another_keep`, run again: every key of A's rows also has its words row, and a search for a word only it holds lists it).
  `test_index_words_faults.py` (new, in `tests/gitstore/`): `test_keep_state_interrupted_leaves_no_searchable_state` (a failure injected after each SQL statement of `keep_state`, the words rows included: the next search prints as with `LODGE_INDEX=off`); `test_locked_word_write_keeps_no_state` (the database locked during `keep_state`: no state kept, the search runs in memory and prints the same).
  `tests/e2e/test_index_property.py` (d-rs76ks): `test_index_reads_equal_memory_under_random_edits` (a 300-record store built with `scripts/bench_store.py`'s builder logic copied into the test's helper, then 60 seeded steps, each one edit from create, edit, delete, untracked file, touch only, stage, commit, revert to an earlier step's contents, CRLF rewrite under an attributes file, assume-unchanged edit, skip-worktree removal, with at least one revert after `KEPT_STATES + 1` states; after each step a seeded read from `show`, `search`, `waiting`, `threads`, and `thread` prints the same text and exit status with the index as with `LODGE_INDEX=off`; bounded to about 60 s, the seed printed on failure).
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; search lines of the replay at all three sizes, `seen` and `changed`, with each search's candidate count, provisional (d-26e6zj, d-me8vm3).
- [ ] **Step 5:** commit, push.

### Task 10c: The published state's facts from the index

**Files:**
- Modify: `src/lodge/app/read_model.py` (`ChangeFacts` from stored facts), `src/lodge/app/indexed.py`, `src/lodge/app/state.py` (`Checked` carries cached published facts without a derived object; `finish_checked` accepts the already-built change facts), `src/lodge/core/__init__.py` (exports the existing `Status` type for the validated facts-to-change-facts hand-off), `src/lodge/gitstore/index_states.py` (skip an unencodable facts key without discarding other marker units)
- Test: `tests/app/test_published_facts.py` (new), `tests/app/test_index_review_facts.py`, `tests/e2e/test_index_review_regressions.py`
- Fix-round hand-offs: `app/index_types.py`, `app/index_lookups.py`, `gitstore/index_db.py` (empty parse write and schema 7), `tests/gitstore/state_helpers.py`, and `tests/gitstore/test_index_states.py` follow the status-only facts and required-thread shapes.

**Interfaces:**
- Consumes: Task 2's `ChangeFacts` and `check_change(..., facts=)`; Task 10a's `StateFacts`, `facts`, and `keep_state`.
- Produces: building a state whose published ident has stored `StateFacts` passes its validated status map to `ChangeFacts`, with an empty published-problems set and the current derived state and problems.
  The Task 10c fix-round dispatch explicitly narrows the original facts policy: store only published identities and their statuses, never dirty current identities or problem lists.
  The indexed path derives missing published statuses without running published `check_state`; `finish_checked` already restores all current standing problems and discards the published-problem notes.
  The exact readers and gate retain their complete computations and use only the parse cache (d-q0tb8r).
  The published snapshot is still assembled in full, and the full change check still runs.
  Facts remain immutable, keyed by published ident, retained through markers and keeps, and rewritten with the build's used units after an epoch change.

- [ ] **Step 1: Write the failing tests:** `test_published_facts_equal_full` (the `CheckResult` of a state built with stored facts equals one built without, for published states holding a duplicate code, a hand-edited published decision, an out-of-order entry, and a cycle, each with a new problem on the same path in the current state); `test_facts_keyed_by_ident_alone` (two stored states sharing a published ident read the same facts); `test_absent_facts_are_computed_and_kept` (and the published facts survive the `keep_state` that wrote them and every later eviction, since facts are immutable); `test_facts_written_on_the_first_read` (the first read of a changed state with no published facts writes them in its marker transaction; the next read of another changed state with the same published ident runs no published `derive`, by a patched counter); `test_other_published_ident_reads_other_facts` (a commit moves the published ident: the old ident's facts are not selected, and the new ones are computed).
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; the replay's `changed` mode at `s90000` with the phase times of one changed-record read as in plan fix 7b's table, the facts hit and miss apart, and the bytes of facts each changed read adds, provisional (d-26e6zj).
- [ ] **Step 5:** commit, push.

### Task 11: Untracked files through folder signatures

**Files:**
- Create: `src/lodge/gitstore/folders.py`, `src/lodge/gitstore/committed.py` (committed-tree helper extracted from identity)
- Modify: `src/lodge/gitstore/identity.py` (the walk replaced when an index is writable or holds rows; the base's names taken only when a folder is listed), `src/lodge/gitstore/index_db.py` (a `folders` table), `src/lodge/main.py` (the store is handed the index at construction), `src/lodge/gitstore/setup.py`, `src/lodge/gitstore/checkout.py`, `src/lodge/gitstore/listing.py` (construction and lazy-listing hand-offs), `src/lodge/gitstore/index_schema.py` (schema and folder snapshot completeness), `src/lodge/gitstore/disk.py` (descriptor-relative folder stat and listing)
- Records: FOLD-1, through `lodge add` (scope `process`, `work_item` the plan, narrowing d-8kq2nk)
- Test: `tests/gitstore/test_folders.py` (new), `tests/gitstore/test_folder_property.py` (new, persistent-cache property oracle), `tests/gitstore/test_folder_recovery.py` (new, partial-walk recovery), `tests/e2e/test_indexed_reads.py` (establish stable folder rows before the existing no-write assertion)

**Interfaces:**
- Consumes: Task 8c's `disk.py`, `Committed`, and `run_many`; Task 9's `open_index`, settings, and failure modes.
- Produces: a table `folders(path, ino, mtime_ns, ctime_ns, listed_at_ns, base, added, removed)`, `added` being compact JSON (`json.dumps(..., ensure_ascii=True, separators=(",", ":"))`, as Task 9 stores parses) of the folder's entries the base lacks, each with its kind (a file where the base has a folder, or a folder where it has a file, counts as lacking), and `removed` the same of the base's names in that folder absent from disk; for each folder lodge takes `lstat`, then lists it through `disk.py`, then takes the listing time, in that order (the correctness review's M7); a folder whose `lstat` shows a real folder matching its row, whose row's `ctime_ns` is at least 2 s before its `listed_at_ns`, and whose `base` equals the current base tree ID keeps its recorded `added` and `removed`, and its subfolders are taken from the rows below it; a folder that is now a link or a file is listed again from its parent, and every row below it is dropped; any other folder is listed again, compared with the base's names in it, its subfolders followed, and its row rewritten when the index is writable (d-8kq2nk); all rows of one identity are written in one `BEGIN IMMEDIATE` transaction, replacing earlier rows in place, since each row carries its own key and no state depends on it; a folder whose row is missing or undecodable is listed (invariants 5 and 6).
- No base names on a hit (the Task 8b review's P1 item 2): the files on disk the base lacks are the union of the rows' `added`, and the attachments the disk lacks are the union of `removed` under `lodge/attachments/`; the reachable real folders are the rows' folders; the base's names, from `Committed.listing` of the current commit, are taken only when at least one folder is listed again, so a seen read of an unchanged checkout runs no `ls-tree` and builds no 160,800-path set; `identities()` then builds no mapping, and `listings()` builds the current one on first use.
- Without a usable index the walk of Task 8c runs, with the base's names, so the output is the same.

- [x] **Step 1: Write the failing tests** (`tmp_path`, each agreeing with `disk_tree`): `test_unchanged_folders_are_not_listed` (patched listing not called on a second identity); `test_seen_identity_takes_no_base_names` (on a second identity a patched runner sees no `ls-tree`, and `Committed.listing` is not called); `test_new_file_in_a_listed_folder`; `test_new_subfolder_with_a_file`; `test_deleted_untracked_file`; `test_rename_within_a_folder`; `test_deleted_attachment_is_absent` (a committed attachment removed from disk: absent on the second identity, with no `ls-tree`); `test_folder_replaced_by_link_drops_its_rows` (the three Task 8c link probes, each on a second identity after rows were written); `test_change_in_the_same_second_as_the_listing` (a row listed within 2 s of the folder's ctime is not trusted); `test_mtime_set_back_still_detected` (`os.utime` to the old mtime after adding a file: ctime differs); `test_base_change_relists` (a commit that adds a file: every folder listed again against the new base); `test_read_only_index_falls_back_to_the_walk`; `test_interrupted_folder_write_lists_again` (a failure injected after each SQL statement of the folder write: the next identity agrees).
- [x] **Step 2:** run; expected FAIL.
- [x] **Step 3:** implement; FOLD-1 through `lodge add`.
- [x] **Step 4:** gate; the replay at 160,000 files, `seen`, recorded with the identity's share, and `identities()` on a new store object timed as in Task 8c (with R11-B expected about 0.1 s isolated: the git group 0.07, published tree and flag scan 0.018, folder rows 0.0075); the tests run once with `--basetemp` on a FUSE-mounted disk where one is at hand, the result recorded, and if any fails there the signature cache is disabled on that file system kind (detected by `os.statvfs` and `/proc/mounts`) with the walk used instead.
- [x] **Step 5:** commit, push.

### Task 12: The recorded table, and the stop on the targets

**Files:**
- Create: `docs/superpowers/plans/2026-10-31-lodge-at-scale/timings.md`
- Modify: `scripts/bench_reads.py` (a `--mode chained` that runs `changed`'s distinct edits without restoring the saved index between runs, and prints the index's epoch before and after, for the clears per hundred changed reads; Task 1's `changed` restores the copy each run; a `--git-config FILE` that runs every command with `GIT_CONFIG_GLOBAL=FILE`, `GIT_CONFIG_NOSYSTEM=1`, and `GIT_ATTR_NOSYSTEM=1`; and a `--startup` that times `python -c pass`, `python -c "import lodge.main"`, and `lodge guide --read` with the build's Python, best of nine), `README.md` (one paragraph: the index, where it lives, one file per build, cleared in place past its cap, that `rm -r` of the folder is safe at any time and reclaims all its space, `LODGE_INDEX=off`)
- Test: `tests/test_bench_replay_options.py` (new), `tests/test_bench_cleanup.py` (SECOND-1 warm-up expectation).

The replay primes two sightings before measuring seen reads or saving a changed baseline, so its timed seen samples start with a complete kept state.
The seven new regression tests cover chained edits without cache restoration, the two sightings, environment propagation to every child, start-up measurements with the build's Python, an incomplete epoch probe, resolving an installed lodge command to its sibling Python, and locating the shared common-directory cache.

**Interfaces:**
- Consumes: every task.
- Produces: `timings.md`, for `s900`, `s9000`, and `s90000` on native disk, per line of `scripts/bench_reads.txt`, under `--git-config /dev/null` (no conversion source): the base build of Task 1, this branch `cold`, `seen`, and `changed`, `check --gate` included, cold reads in their own column and under no stop (d-e3stjn), with Task 9's time of one clear beside them, with the output and exit-status comparison against the base build (identical, or the lines Tasks 5 to 7 and Task 8c's link and gitlink fixes changed on purpose, named); each search's candidate count, with searches over 5,000 candidates in a table of their own (d-me8vm3); the index file's size per store against d-4pbeax's figure; at `s90000`, the clears in a `--mode chained` run of 100 consecutive changed reads; the machine's Python, SQLite, git, and disk kind; where a FUSE-mounted copy of `s90000` is at hand, the same `show {code}` `seen` on it, one line, without its path.
  Two rows of their own at `s90000`:
  - The start-up floor (`--startup`): measured at 83ef70b as 18.0 to 19.8 ms, 142.3 to 149.7 ms, and 158.6 to 172.6 ms; expected about the same, the last about 0.012 s lower (Task 8c's parser); every `seen` read is at least this floor, and the row says how much of the 0.3 s it leaves.
  - The changed rows: the target is 3 s without a conversion source; plan fix 7b measures the exact path's stages at 4.713 s with the published facts kept and its floor at 3.214 s, so the row is expected to miss; three changed rows, each timed to the process's exit: the first read of a changed state, the second (its keep after the output, ending after the read plus the complete keep, which Task 10a measures; plan fix 7b's partial proxy alone took 8.764 s), and the third (a seen read), each under the stop, with the phase table and the floor named.
  - The conversion row (CONV-1; `--git-config` with a file holding `[core] autocrlf = input`), `seen` and `changed` for `show {code}`, `waiting`, and `search berth --brief`: the identity reads every file (3.148 s at 83ef70b), so these reads are expected at about 3.4 s `seen`; reported beside the targets, never under the stop.
- [x] **Step 1:** run the replay, the start-up row, and the conversion row; write `timings.md`.
- [x] **Step 2:** the stop (d-26e6zj, d-232gxs as narrowed by CONV-1, d-hxmdkz): if at 160,000 files without a conversion source `show`, `waiting`, `threads`, `thread`, or a search with at most 5,000 candidates is above 0.3 s `seen`, a search with more than 5,000 candidates is above 1.0 s `seen`, or a read is above 3 s `changed`, `timings.md` gives the phase table, with the start-up floor as its first phase, and the ledger records that the server question goes to the coordinator; broad searches and the conversion row are reported apart, whatever they are.
- [x] **Step 3:** gate, commit, push.
