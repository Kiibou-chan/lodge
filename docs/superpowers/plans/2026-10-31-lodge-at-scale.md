# lodge at scale: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** an agent's reads through lodge are cheap and fast at 160,000 record files: the superlinear steps go, headers parse with libyaml where that is provably the same, identical states are not compared, reads batch several refs and queries and treat codes as codes, and a local SQLite index answers a read of a seen state in at most 0.3 s on native disk.

**Architecture:** `core` gains linear checks and traversals, one `derive` per snapshot, a guarded C loader, a per-file parse and an assembly from parses, a plain-value codec, the new search ranking, and code families.
`app` gains the identical-state shortcut, multi-ref and multi-query reads, an `Index` port, and a read path that answers `show`, `search`, `waiting`, `threads`, and `thread` from stored rows.
`Store.trees()` stays and every `Tree` carries the blob ID of each file, hashed by lodge from the bytes it read; the five indexed reads alone use a new fast identity and listing that `gitstore` computes from git and a folder-signature cache (d-7e8zhd).
`gitstore` holds the SQLite index in new modules; the command line gains `show REF...`, `search Q...`, `search --phrase`, and `guide --read`; `scripts/` gains the read-replay benchmark.

**Tech stack:** Python 3.12 or later, uv, PyYAML (with libyaml where present), pytest, mypy (strict), Ruff, Vulture; the standard library's `sqlite3` (FTS5 where present), `marshal` (in `gitstore` only), `hashlib`, `gc` (in `main.py` only), and `subprocess` (in `gitstore` only).

**Spec:** `lodge spec`, with the coordinator's rulings for this plan recorded as d-1bww1r (correctness first), d-1ftgg3 (speed order), d-232gxs (the index and its targets), d-3g6ard (leaner reads), d-542m5g (benchmarks), and for the first fix round d-q051s2, d-q0tb8r, d-rs76ks, d-rvf532, d-ty4dks, d-vmpspc, and d-ytf272.
The brief is `docs/superpowers/plans/2026-10-31-lodge-at-scale/brief.md`; the planner's probes and their output are in `docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-report.md` and `probes/`; the reviews and what this plan changed for each finding are in the same folder (`plan-review-*.md`, `plan-fix-1.md`).
The plan argues from them, never over them; where `lodge spec` and a task disagree, the spec wins and the builder reports it.

## Global Constraints

- One brief per task; the builder sees its brief, `CLAUDE.md`, and the repository.
- Step 0 of every task that adds or moves an interface is a skeleton: the new modules with their signatures and `...` bodies, the front doors updated, then `uv run pytest tests/test_structure.py -q` and `uv run mypy` green before any test is written (the feasibility review's F7: a cycle or a past-the-front-door import is found before the code).
- Test-first: each named test is written and seen failing before its code; every existing test keeps passing, edited only where a task says so, each edit listed in the task report.
- The gate after every task: `sh scripts/check.sh` green (ruff format, ruff, mypy strict, vulture, pytest, `lodge check --gate`); then stage with explicit paths, commit with `git -c user.name="Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, the message ending `Co-Authored-By: Claude <noreply@anthropic.com>`, and push `read-speed` to `origin`; never `main`.
- Correctness first (d-1bww1r): no task changes a check's result, a problem's wording, or what the gate compares, except where it records a product decision with a spec edit.
- The gate and `add` (and every command but the five indexed reads) read exact trees: every working-tree file read and hashed by lodge, committed trees by git's object IDs; they never take derived state, flags, or tree claims from the index, and use only its parse cache, keyed by those hashes (d-q0tb8r, d-7e8zhd).
- An indexed read prints exactly what the in-memory read prints; where the index cannot prove it, the read takes the in-memory path (d-rs76ks).
- Structure (`tests/structure_rules.py`, `tests/structure_tables.py`): allowed imports as `ALLOWED`, no new package and no new edge (d-5zqvxb); front doors only; no cycles, `TYPE_CHECKING` imports included; no module over 300 lines, tests included; `core` imports only `CORE_MODULES`; `marshal` and `sqlite3` only in `gitstore`; `subprocess` only in `gitstore`; file I/O only in `gitstore` and `cli`.
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
3. d-8kq2nk, with d-ana6c0, d-c5a1y4, and d-dqpf59: the fast identity of a checkout is the `HEAD` tree of `lodge/` when nothing differs on disk, else a hash of it and the overlay; the overlay holds what `git diff-index --cached` and `git diff-files` name (run with git's stat shortcuts off), the entries flagged assume-unchanged or skip-worktree, the paths git may convert, and the files `HEAD` lacks; each is read and hashed, and dropped when its bytes equal the base's.
4. d-atsx8n with d-dqpf59: a path git may convert is read from disk; the conversion sources come from git (`git var GIT_ATTR_GLOBAL GIT_ATTR_SYSTEM`, `core.attributesFile`, `info/attributes`, every `.gitattributes`), and `core.autocrlf` in any of git's spellings of true, or `input`, makes every path convert.
5. d-c400w8: the parse cache is keyed by path and blob ID and stores `marshal` of plain values, never `pickle`.
6. d-c4w7xy: a state's rows hold the derived facts only, in 1,024 buckets by the last two characters of the ID.
7. d-eby5pb, narrowed by d-emtwbs: FTS5 over core's own words with the `ascii` tokenizer gives candidates; core ranks; without FTS5, and for a phrase or code with no word outside the function words, search runs in memory.
8. d-faakge (replacing d-f3r5aq) and d-rvf532: one index file per digest of lodge's source bytes, the Python, PyYAML, libyaml, and SQLite versions, and the schema number; a state's result is keyed by the core settings too, and is valid over the interval between the latest new decision dated before its build and the earliest dated after it.
9. d-hf2fms and d-ytf272: `KEPT_STATES = 4`, one constant, first in first out; a read of a seen state writes nothing.
10. d-kj554d with d-her016: an unwritable index is opened read-only or skipped; only `SQLITE_CORRUPT` and `SQLITE_NOTADB` delete and rebuild; a state is written in one transaction with its eviction and read in one read transaction; output never changes and a read never fails.
11. d-m0g9tx with d-7e8zhd: stored rows and the fast identity serve `show`, `search`, `waiting`, `threads`, and `thread`; every other command reads exact trees and builds the snapshot in memory from the parse cache.
12. d-n9w4by: a query is a code when it is one token of the code grammar with a non-empty family in the state; citers are matched in titles and statements; `show` lists ten siblings and ten citers at most.
13. d-emtwbs and d-ty4dks: `--phrase "words"` gives a phrase, matched as a contiguous run of word tokens with function words kept; a multi-word argument is all its words.
14. d-p60ka9: brief lines drop ` · current` under the default status filter, with a first line saying so.
15. d-s2ypth: every command but `view` runs with the cyclic collector off, when `main` runs as the program.
16. d-zyqzkg: identical states skip `check_change`, by the proof in Task 4.
17. d-q051s2: the C loader parses only headers a guard admits as the writer's shapes.
18. d-dxqxsn: each state's own statuses and `check_state` problems are stored by its identity alone, for a later change check.
19. d-me8vm3: searches with more than 5,000 candidates are measured apart; whether the 0.3 s target covers them is the coordinator's call, open.
20. d-26e6zj: the stop on missed targets applies after Task 11.

## Expected cost at 160,000 files (estimates from the probes, native disk)

| Read | Today | After Tasks 2 to 4 | After Task 11 |
|---|---|---|---|
| a point read (`show`, `waiting`), seen state | not finished in 900 s on a FUSE disk; natively the phases of `probes/phases.py` sum to 53 s with `_missing` made linear, and today's `_missing` is quadratic (6.7 s at 16,008 files, so about 100 times that at 160,000) | about 14 s: trees 5.5, one load 7.1 (libyaml where the guard admits, which the writer's records all are), `derive` 0.9, `check_state` about 0.5 | about 0.2 s: import 0.10, git 0.08 (`rev-parse`, `merge-base`, `diff-index` 0.012, `diff-files` 0.045), folder signatures 0.01, SQLite 0.01 |
| a broad search (100,000 candidates) | as above | as above | about 0.7 s, measured apart (d-me8vm3) |
| after one changed record (checkout, uncommitted) | as above | about 25 s (two loads, the change check) | about 3 s: listing 0.06, parse cache 0.45, assembly 0.2, `derive` 0.9, `check_state` 0.3, the change check with stored published facts 0.6, rows 0.6, writing 0.2 |
| first read in a clone | as above | as above | about 12 s: parse 7, FTS 1.1, parse cache 1.4, state 2.5 |
| the gate, `add`, `spec`, the viewer | as above | about 14 s | about 4 s: exact trees 2.0 (every working-tree file read), parse cache 0.45, assembly, `derive`, and checks 1.5 |

The changed-record row is at its target; Task 10c measures it, and Task 12 applies the stop after every optimisation has landed (d-26e6zj).

## Review Focus

1. A read whose printed output differs between the index path, the in-memory path, and today's code on the same store: the differential and property tests of Tasks 4, 8b, 9, 10a, and 10b, and Task 12's replay comparing output byte for byte.
2. A fast identity that misses a change on disk: staged, unstaged, untracked, ignored, deleted, renamed, touched only, reverted, a symbolic link, a non-regular file, a file git converts (global or system attributes, autocrlf in any spelling), an assume-unchanged or skip-worktree entry, a file created in the same second as its folder was listed (Tasks 8b and 11).
3. The gate or `add` taking anything from the index but a parse keyed by bytes lodge hashed (Tasks 8a and 9).
4. A cached result used where its inputs differ: another lodge build or dependency version, other settings, a time outside the state's validity interval (forward or back), a published state that moved.
5. A read that fails, hangs, deletes a healthy index, or writes in a read-only sandbox, with the database locked, or with another process writing (Tasks 9 and 10a).
6. A search result list that differs from the ranking's definition because the index's candidates missed a record (Task 10b's property test).
7. A check whose wording or result changed in the linear rewrites of Task 2, or a C-parsed header whose value or problem differs from the Python loader's (Task 3).

---

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
- `scripts/bench_store.py`: its four ruff findings fixed without changing the stores it writes; then, for one coded decision in fifty, a second decision coded `CODE-n.why` and one new entry whose statement cites `CODE-n`, so stores have families and citers.
- `scripts/bench_reads.txt`: `show {code}`, `show {entry} --reasoning --provenance`, `show {decision}`, `search berth --brief`, `search "berth crane" --brief`, `search {code} --brief`, `search berth`, `waiting`, `threads`, `spec --area area-001`, `check`, and `check --gate` (measured, not targeted); Task 5 adds `show {code} {code2} {entry}`, Task 6 adds `search berth tide --brief` and `search --phrase "berth crane" --brief`.

- [ ] **Step 1:** fix the ruff findings; check by rebuilding `s900` to a temporary folder and comparing `git rev-parse HEAD^{tree}` with `/var/tmp/lodge-bench/s900`.
- [ ] **Step 2:** add the families and citers; rebuild `s900`, `s9000`, and `s90000` (about 1,600, 16,000, and 160,000 files) and record their file counts.
- [ ] **Step 3:** write `scripts/bench_reads.py` (no tests: `scripts/` is outside pytest and mypy; `ruff check scripts` clean).
- [ ] **Step 4:** build a native-disk venv of this branch (`uv venv /var/tmp/lodge-bench/venv-base`, `uv pip install .`, `python -m compileall`), and record the `seen` table for `s900` and `s9000`, and for `s90000` one `show {code}` under `timeout 900`, reported as not finished if it is not.
- [ ] **Step 5:** gate, commit, push.

### Task 2: The superlinear steps, iterative traversals, one `derive` per snapshot, and the collector

**Files:**
- Modify: `src/lodge/core/check_change.py` (`_missing`; `_dates` through an index of earlier decisions; the keyword `facts`), `src/lodge/core/check_areas.py`, `src/lodge/core/check_cycles.py`, `src/lodge/core/check_state.py` (the keyword `derived`), `src/lodge/core/check_entries.py` and `_links_to_dead` (statuses from `facts`), `src/lodge/core/derive.py` (at most 20 lines: running pointers replace the prefix scans of `_behind_entry_edits` and `_follows_author_change`), `src/lodge/core/doubts.py` (propagation from the doubted records through reverse dependencies), `src/lodge/core/order.py` (`derived_order` and `rests_on_tree` iterative), `src/lodge/core/__init__.py`, `src/lodge/app/state.py`, `src/lodge/app/reads.py`, `src/lodge/main.py` (`gc.disable()` when `argv is None` and the command is not `view`)
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
- `derived_order` and `rests_on_tree`: explicit stacks, no recursion; the same output for every graph.

- [ ] **Step 1: Write the failing tests:**
  `test_linear_checks.py`: `test_missing_builds_the_union_once` (the `after` snapshot's mappings wrapped in a counting `Mapping` whose `keys()` counts calls: at most one per mapping for 2,000 published records, and the one problem as today); `test_check_areas_same_problems_as_before` (each sample of `tests/core/samples.py` and a made-up 50-area snapshot with an entry unlisted, an order naming a retired entry, a duplicate, and a folder without `_area.md`, against a copy of today's function kept in the test file as the oracle); `test_cycles_same_as_reachability` (200 seeded random `rests_on` graphs of 1 to 40 entries against a copy of today's function); `test_dates_same_as_before` (seeded snapshots with 1 to 30 new decisions linking and sharing entries with earlier ones, against a copy of today's `_dates`); `test_check_change_with_facts_equals_without` (the fixtures of `tests/core/test_check_change.py`, and the 50-area snapshot with an edited entry and a new decision).
  `test_linear_derive.py`: `test_derive_same_as_before` (seeded snapshots with author, agent, imported, replaced, confirmed, and retiring decisions, up to 60 changes of one entry, against a copy of today's `derive`); `test_doubt_marks_same_as_before` (seeded graphs with doubts, questions, and none, against a copy of today's `doubt_marks`); `test_derive_once_per_checked_read` (count `derive` calls through `read_checked` on a `MemoryStore` with `staged=True`: 2, one per snapshot).
  `test_deep_chains.py`: `test_chain_of_5000_checks_shows_and_orders` (a 5,000-entry chain in one area: `check_state`, `rests_on_tree` of its last entry, `derived_order`, and `render_spec` return without `RecursionError`, and on a 30-entry chain equal a copy of today's functions).
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
  where `KEY` is `[a-z_]+`, `PLAIN` is `[A-Za-z0-9][A-Za-z0-9._:+-]*` with nothing after it, `STRING` is a JSON string (`"`, then characters other than `"`, `\`, and controls, or the escapes `\"`, `\\`, `\/`, `\b`, `\f`, `\n`, `\r`, `\t`, `\uXXXX`, then `"`), and `VALUE` is `PLAIN` or `STRING`; no tab, no trailing space, no `#`, `|`, `>`, `&`, `*`, `!`, `%`, or `?` outside a `STRING`.
- The C loader: `yaml.CSafeLoader` with today's empty implicit resolvers, kept constructors, surrogate-pair joining, and duplicate-key refusal (written without the two-argument `super()`); any exception from it still falls back to today's loader.
- So a header lodge did not write, a hand edit with a trailing tab, a deep nesting, or a block scalar always takes today's loader, and its value, error message, and line come from it (the correctness review's B1, the feasibility review's F14).

- [ ] **Step 0:** skeleton.
- [ ] **Step 1: Write the failing tests:**
  `test_yaml_guard.py`: `test_every_written_header_is_admitted` (`write_record` of every decision and entry built in `tests/core/builders.py` and samples, `write_area`, and `write_thread` with author and agent messages: every header and message block admitted); `test_trailing_tab_is_not_admitted_and_fails_as_today` (`title: x` then a tab, `title:` then a tab and a value, `- a` then a tab, `title: x` then a tab and `# c`: not admitted, and `parse_record` gives today's problem); `test_block_scalar_bom_and_nesting_not_admitted` (`key: |#`, a BOM after a line break, a 600-level nested sequence); `test_c_loader_used_for_admitted_headers` (a patched counter on the C path); `test_falls_back_without_libyaml` (patched `__with_libyaml__ = False`).
  `test_yaml_fuzz.py`: `test_admitted_headers_parse_the_same` (seeded generator of headers built from the writer's shapes with random keys, plain and JSON-string values including escapes, unicode, surrogate pairs, and with random single-character mutations (tab, `#`, `|`, `&`, BOM, U+2028, deleted quote, extra indentation); for every admitted header both loaders succeed with equal values or both fail, and for every header `load_yaml` equals today's loader in value or in `YamlError` message and line; 20,000 headers, bounded to about 10 s, the seed printed on failure).
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
  Task 10a uses the same shortcut when the fast identities are equal.

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
  def cites(text: str, code: str) -> bool
      # code.lower() in text.lower() as a whole token: the character before is not in [A-Za-z0-9._-] (or the start),
      # the character after is not in [A-Za-z0-9_-] and is not a "." followed by [A-Za-z0-9] (or the end)
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
- [ ] **Step 1: Write the failing tests:** `test_codes.py`: `test_family_takes_dotted_siblings_not_longer_numbers` (`X-1`, `X-1.why`, `x-1.b`, not `X-10`, `X-1a`); `test_family_orders_the_code_first`; `test_cites_whole_tokens_only` (`see X-1.` yes, `X-1,` yes, `(X-1)` yes, `X-10` no, `X-1.why` no, `AX-1` no, `x-1` yes, `ſ-1` no); `test_citers_exclude_the_family_and_order_newest_first`.
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
- Consumes: Task 5's `is_code_token`, `family`, `cites`.
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
  3. for a phrase: records whose title or statement token sequence holds `tokens` contiguously (d-emtwbs), by score; for words: records holding every word, by score;
  4. records holding at least one word but not all, by score (for a phrase too, so its words still find near matches below the exact ones);
  score as today (3 per query word in the title, 1 per word in the statement), from `title_words` and `statement_words`, ties newest first by `(date, ID)`.
  An empty query lists by `(date, ID)` newest first, as today.
- `lodge search Q1 Q2 --phrase "P1" ...`: one read; queries in argument order, positional ones first, then each `--phrase`; each query's results under a line `query: Q1 · N matches` when there is more than one query, followed by `· also d-xxxxxx, s-yyyyyy above` naming the records of this query already printed under an earlier one, which are not printed again and do not count toward `--limit` (the correctness review's M8); `--limit` applies per query; no query lists newest first, as today.
  A multi-word argument is all its words; only `--phrase` makes a phrase (d-ty4dks).
- Brief lines (d-p60ka9): under the default status filter a line omits ` · current`, and the output's first line, after the freshness lines, is `records are current unless marked`; under any other `--status` the status prints as today.
- The product decision: search takes several queries and `--phrase`, ranks a code's family and citers first, matches a phrase as a contiguous run of whole words, ranks records with every word first, and brief lines omit the default status; it edits s-3n0ndk's first two sentences, its third unchanged from Task 5.

- [ ] **Step 0:** skeleton, with `Filters` moved and `tests/test_structure.py` green.
- [ ] **Step 1: Write the failing tests:** `test_ranking.py`: `test_exact_id_first`; `test_code_family_then_citers_then_words`; `test_code_without_family_ranks_as_words`; `test_phrase_is_a_run_of_whole_words` (`--phrase "settled point"` against `point settled`, `unsettled points`, and `settled, point.`: only the last two words in order with punctuation between match); `test_phrase_keeps_function_words` (`--phrase "of the berth"`); `test_needs_memory_cases` (`--phrase "of the"`, the code `NO-ONE`, the code `A`: True; `--phrase "the berth"`: False); `test_all_words_before_some_words`; `test_ties_newest_first`; `test_filters_apply_to_family_and_citers`; `test_rank_over_candidates_equals_rank_over_all` (for 300 seeded queries over a made-up 400-record snapshot, words, phrases, codes, and their mixes, skipping those `needs_memory` holds for: `rank` over the records holding any query word, the family, and the citers equals `rank` over every record; the property Task 10b relies on).
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
- The overlay, checkout mode (d-8kq2nk, d-ana6c0, d-c5a1y4, d-dqpf59): `base` is `rev-parse HEAD:lodge` (the empty tree's ID when `HEAD` is unborn or lacks `lodge/`); a path joins the overlay when `git -c core.fsmonitor=false -c core.checkStat=default -c core.trustctime=true diff-index --cached --no-renames -z --name-only HEAD -- lodge` or the same `diff-files` names it, when `flags.py` lists it, when `attributes.py` says git may convert it, or when it is on disk and `base` lacks it (found in this task by a names-only `os.scandir` walk compared folder by folder with `base`'s names; Task 11 replaces the walk); each overlay path is read as `disk_tree` reads it and hashed, or marked deleted when it is not on disk; an entry whose hash equals `base`'s blob at that path, a deletion of a path `base` lacks, and an attachment present in both are dropped.
- The identity (d-ana6c0): `base` itself when the overlay is empty, else `sha1(base + "\0" + sorted "path\0blob" lines)`; published is the merge base's `lodge/` tree ID as `published_state` finds it, its missing-state message unchanged; branch mode: the tip's `lodge/` tree ID, and the accepted tip's for published while a rewrite stands.
- Flags: `git ls-files -t -v -z -- lodge`, entries tagged `S` or with a lower-case tag, cached in the store object for the process; Task 9 caches them in the index by the stat of git's index file (`git rev-parse --git-path index`).
- Conversions: none when `git config --get core.autocrlf` is unset or false in git's spellings (`false`, `no`, `off`, `0`, empty), no `core.attributesFile`, no file named by `git var GIT_ATTR_GLOBAL GIT_ATTR_SYSTEM` exists (system one skipped when `GIT_ATTR_NOSYSTEM` is set), no `$GIT_COMMON_DIR/info/attributes`, and no `.gitattributes` in the working tree root or in the listing; `core.autocrlf` true in any spelling (`true`, `yes`, `on`, `1`) or `input`: every path converts; otherwise `git check-attr --stdin -z text eol filter ident working-tree-encoding` over the listing's paths, and each path with any of them set converts.
- The listing: `ls-tree -r` of `base` with the overlay applied; `texts` reads git blobs with one `cat-file --batch` and overlay files from the bytes already read.
- Nothing calls these methods yet but the tests; Task 10a's reads do.

- [ ] **Step 0:** skeleton.
- [ ] **Step 1: Write the failing tests** (each in a `tmp_path` repository; "agrees" means the listing's paths, attachments, and `texts` equal Task 8a's exact `disk_tree`, and the ident changes exactly when they change):
  `test_identity.py`: `test_clean_checkout_ident_is_the_head_tree` (and equals the published ident and `git rev-parse HEAD:lodge`); `test_touched_file_keeps_the_clean_ident`; `test_staged_edit_reverted_on_disk_keeps_the_clean_ident`; `test_unstaged_edit_agrees`; `test_untracked_file_agrees`; `test_ignored_file_agrees`; `test_deleted_file_agrees`; `test_staged_deletion_left_on_disk_agrees`; `test_rename_agrees`; `test_symbolic_link_agrees`; `test_fifo_agrees` (skipped without `os.mkfifo`); `test_attachment_bytes_changed_keeps_the_ident`; `test_unborn_head`; `test_head_without_lodge`.
  `test_flags.py`: `test_assume_unchanged_edit_agrees`; `test_skip_worktree_missing_file_agrees` (a sparse checkout without one record: missing, as `disk_tree` sees it); `test_ignore_stat_entries_agree` (`core.ignoreStat=true` in the repository's config, then an edit).
  `test_attributes.py`: `test_no_sources_no_check_attr_call`; `test_autocrlf_spellings` (`true`, `yes`, `on`, `1`, `input`: every path read from disk; `false`, `no`, `off`, `0`: none); `test_global_attributes_file_reads_from_disk` (`*.md text eol=crlf` in `$XDG_CONFIG_HOME/git/attributes`: agrees); `test_info_attributes_and_attributes_file` (each source alone: agrees); `test_text_attribute_on_one_pattern` (`lodge/decisions/*.md text eol=crlf`: those paths read from disk, others from git; agrees).
  `test_identity_property.py`: `test_random_edits_agree` (200 seeded sequences of 1 to 8 operations on a 40-record made-up store: create, edit, delete, untracked file, touch only, stage, unstage, revert, commit, assume-unchanged edit, skip-worktree removal, a CRLF rewrite under an attributes file; after each sequence the fast listing agrees with `disk_tree`, and two states agree in ident exactly when their exact trees are equal).
  `test_listing_modes.py`: `test_branch_mode_ident_is_the_tip_tree`; `test_rewritten_branch_publishes_the_accepted_tree`.
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; `identities()` and `listings()` timed at `s90000` clean and with one edit, recorded with each git call's share.
- [ ] **Step 5:** commit, push.

### Task 9: The parse cache, and the index's files, keys, and failure modes

**Files:**
- Create: `src/lodge/core/codec.py` (plain values), `src/lodge/gitstore/index_db.py` (files, schema, the build digest, pruning, the failure modes), `src/lodge/gitstore/index_parses.py` (the parse cache and the flag cache of Task 8b), `src/lodge/app/index_types.py` (`FileKey`)
- Modify: `src/lodge/app/ports.py` (`Index`), `src/lodge/app/__init__.py`, `src/lodge/app/state.py` (snapshots through the cache), `src/lodge/app/lodge.py` (`Lodge` takes `index: Index | None = None`), `src/lodge/gitstore/__init__.py`, `src/lodge/main.py` (opens the index; `LODGE_INDEX=off` in the environment gives `None`), `src/lodge/core/__init__.py`
- Records: a product decision creating an entry in the `storage` area, "A disposable index speeds reads", listed in the area's order and resting on s-j8tp0n
- Test: `tests/core/test_codec.py` (new), `tests/gitstore/test_index_db.py` (new), `tests/gitstore/test_index_failures.py` (new), `tests/gitstore/test_index_parses.py` (new), `tests/app/test_parse_cache.py` (new), `tests/e2e/test_index_off_same_output.py` (new)

**Interfaces:**
- Consumes: Task 8a's `parse_file`, `assemble`, and `Tree.blobs`.
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
      def keep_parses(self, parsed: Mapping[FileKey, Parsed | None]) -> None
  # gitstore
  def open_index(common_dir: Path, settings_digest: str) -> Index | None
  ```
- Files (d-faakge, d-rvf532): `<git common dir>/lodge/index-<digest>.sqlite`, `<digest>` the first 16 hex characters of sha1 over the schema number, lodge's source bytes (every `.py` and `.md` file of the installed `lodge` package, by relative name, 2.3 ms for 273,039 bytes in the planner's probe), `sys.version`, `yaml.__version__`, `yaml.__with_libyaml__`, and `sqlite3.sqlite_version`; on opening, other builds' files beyond the two most recently modified are deleted, and others' files are deleted oldest first while the folder holds more than `INDEX_FOLDER_LIMIT = 1 GiB`; a delete that fails is skipped.
- Settings: journal mode `DELETE`, `busy_timeout` 200 ms, `synchronous=NORMAL` (d-her016).
- Parses: `(path, blob, value)` with `value` = `marshal.dumps(to_plain(parsed))`; a row that fails to decode is a miss.
- Failure modes (d-kj554d, d-her016), each a test:
  - the folder or file cannot be written: opened with `mode=ro` through a `file:` URI; reads use what it holds, writes do nothing;
  - an error whose `sqlite_errorcode` is `SQLITE_CORRUPT` or `SQLITE_NOTADB`: the file deleted and recreated when writable, otherwise `open_index` returns `None`;
  - any other `sqlite3.Error` (busy, locked, read-only, I/O), at opening or later: no delete; that operation returns a miss or does nothing, never raises;
  - a read and a write of one operation each run in one transaction, rolled back on any error.
- `app` builds every snapshot as `assemble` of cached parses for the tree's `(path, blobs[path])` keys plus `parse_file` of the misses, and keeps the misses; `derive` and every check run in full on that snapshot; the gate and `add` read exact trees as today (d-q0tb8r).
- The product decision: lodge keeps a disposable index in the git common dir, never committed, one file per lodge build, that never changes what a read prints or what the gate decides; its entry rests on s-j8tp0n.

- [ ] **Step 0:** skeleton.
- [ ] **Step 1: Write the failing tests:** `test_codec.py`: `test_round_trip_of_every_parse_kind` (a decision with every field, an entry with `rests_on`, an area with a rank, a thread with an author message, a problem with a line); `test_round_trip_of_mappings_and_read` (a `Read` with statuses, a titles mapping); `test_refuses_unknown_class_and_bad_shapes`; `test_no_pickle_or_marshal_in_core` (by `ast` over `core`).
  `test_index_db.py`: `test_creates_folder_and_file_named_by_digest`; `test_digest_changes_with_source_bytes` (a same-size, same-mtime source change: a new digest); `test_digest_names_python_yaml_libyaml_sqlite` (each patched in turn: a new digest); `test_two_builds_keep_their_files` (two digests alternating: the second open of each finds its parses); `test_old_builds_pruned_by_count_and_size`.
  `test_index_failures.py`: `test_read_only_folder_opens_read_only` (`chmod 0o500`, skipped as root); `test_read_only_and_missing_returns_none`; `test_locked_at_open_does_not_delete` (a second connection holds `BEGIN EXCLUSIVE` on a populated index: `open_index` returns within 1 s, the file is unchanged, and after release the parses are found); `test_locked_write_is_skipped`; `test_corrupt_file_is_rebuilt` (garbage bytes); `test_corrupt_file_read_only_returns_none`; `test_error_mid_write_rolls_back` (a patched failure after the first row: no rows kept).
  `test_index_parses.py`: `test_hit_after_keep`; `test_key_is_path_and_blob` (the same blob at two paths in two areas parses to two areas); `test_undecodable_row_is_a_miss`.
  `test_parse_cache.py` (app, a fake index in `tests/app/fakes.py`): `test_second_read_parses_nothing`; `test_gate_uses_only_parses_keyed_by_read_bytes` (a fake index holding a wrong parse under a git blob ID the disk bytes do not hash to: the gate's result as without the index); `test_read_output_same_with_and_without_index` (show, search, waiting, check on four sample stores, printed text).
  `tests/e2e/test_index_off_same_output.py`: `test_index_off_same_output` (`show`, `search`, `waiting`, `spec`, `check --gate` print the same with `LODGE_INDEX=off` and without, twice each); `test_read_only_common_dir_reads` (made read-only after one read: exit 0, same output; skipped as root).
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement; the product decision through `lodge add`.
- [ ] **Step 4:** gate; the replay at all three sizes, `cold` and `seen`, recorded; output identical to Task 8b's build.
- [ ] **Step 5:** commit, push.

### Task 10a: Stored states for `show`, `waiting`, `threads`, and `thread`

**Files:**
- Create: `src/lodge/app/read_model.py` (rows, facts, and answers from a checked `State`), `src/lodge/app/indexed.py` (the indexed reads), `src/lodge/gitstore/index_states.py` (states, buckets, answers, facts, eviction)
- Modify: `src/lodge/app/index_types.py` (`Row`, `StoredState`, `StateFacts`), `src/lodge/app/ports.py` (`Index` gains the methods below), `src/lodge/app/__init__.py`, `src/lodge/app/lodge.py` (`read_model: bool = True`; the viewer's `Lodge` passes False), `src/lodge/app/state.py`, `src/lodge/main.py` (the viewer's factory without the read model)
- Test: `tests/app/test_read_model.py` (new), `tests/app/test_indexed_reads.py` (new), `tests/gitstore/test_index_states.py` (new), `tests/gitstore/test_index_concurrency.py` (new), `tests/e2e/test_indexed_reads.py` (new)

**Interfaces:**
- Consumes: Task 8b's `identities`, `listings`, `texts`; Task 9's `Index`, codec, and failure modes; Task 4's shortcut.
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
  class StateFacts:                            # one state's own facts, keyed by its ident alone (d-dxqxsn)
      status: Mapping[str, str]
      problems: tuple[Problem, ...]            # check_state's
  @dataclass(frozen=True)
  class StoredState:
      key: str                                 # sha1 of current ident, published ident, settings digest
      valid_from: str | None                   # ISO datetimes with offsets (d-faakge)
      valid_until: str | None
      codes: Mapping[str, tuple[str, ...]]     # lower-cased code -> IDs
      unrecorded: tuple[Problem, ...]
  def level1_of(row: Row, record: Decision | SpecEntry) -> Level1     # equals core.level1 for that state
  class Index(Protocol):                       # in addition to Task 9's
      def reading(self) -> ContextManager[None]   # one read transaction around a read's lookups
      def state(self, key: str) -> StoredState | None
      def rows(self, key: str, ids: Collection[str]) -> dict[str, Row]
      def all_rows(self, key: str) -> dict[str, Row]
      def answer(self, key: str, name: str) -> object | None   # "waiting", "threads", "thread:<id>", decoded with the classes app passes
      def facts(self, ident: str) -> StateFacts | None
      def keep_state(self, state: StoredState, rows: Mapping[str, Row], answers: Mapping[str, object],
                     facts: Mapping[str, StateFacts]) -> None   # one transaction, with the eviction
  ```
- A read (`show`, `waiting`, `threads`, `thread`) with an index and the read model on: `identities()`; the key; inside `reading()`, a stored state whose validity interval holds `clock.now()` answers through lookups (one bucket per ID, the parse rows of the records printed); any lookup that finds less than the state promised ends the transaction and the whole read runs in memory (d-her016); otherwise the state is built in memory from `listings()` and the parse cache, kept, and the read answers from memory.
  Equal current and published idents use Task 4's shortcut.
- Validity (d-faakge): `valid_from` is the latest date among decisions new against the published state that is not after the build's `now`, `valid_until` the earliest that is after it; compared as timezone-aware datetimes; a missing end is open.
- What equals what (the correctness review's I4): indexed results print the same text through `cli/output.py` and `cli/thread_output.py` as in-memory results; their `Read.statuses` is empty and the viewer-only `Shown` fields keep their defaults; the differential tests compare printed text.
- An answer's `Read` is rebuilt at read time with the store's live `freshness()` and the state's `unrecorded`.
- Buckets (d-c4w7xy): 1,024 per state, by the ID's last two characters, `marshal` of `{id: to_plain(row)}`; `KEPT_STATES = 4` (d-hf2fms, d-ytf272), the oldest dropped in the same transaction that keeps a fifth, with its buckets and answers; facts kept for the idents of kept states only.
- The viewer, `spec`, `timeline`, `draft`, `check`, `id`, `add`, and the gate never read rows (d-m0g9tx).

- [ ] **Step 0:** skeleton.
- [ ] **Step 1: Write the failing tests:** `test_read_model.py`: `test_level1_of_row_equals_core_level1` (every record of four sample stores and of a made-up 500-record store with replaced, narrowed, retired, flagged, confirmed, doubted, and failing records); `test_level3_links_equal`; `test_answers_print_as_in_memory`.
  `test_indexed_reads.py` (a fake index): `test_seen_state_reads_no_snapshot` (patched `assemble` never called on the second `show`); `test_outputs_print_as_in_memory` (200 seeded commands over the 500-record store: `show` of IDs, codes, unknown refs, several refs; `waiting`; `threads`; `thread`); `test_validity_interval` (a new decision dated 10 minutes after the build: it fails check 1; the clock 11 minutes later: rebuilt, it does not; the clock 1 minute before the build: rebuilt); `test_settings_change_is_another_state`; `test_missing_bucket_falls_back_to_memory`.
  `test_index_states.py`: `test_kept_states_constant`; `test_seen_read_writes_nothing` (the file's size and mtime unchanged); `test_bucket_by_last_two_characters`.
  `test_index_concurrency.py` (two connections, deterministic interleaving): `test_eviction_between_lookups_cannot_split_a_read` (reader inside `reading()`, writer keeps a fifth state: the writer waits or the reader falls back, and the printed output equals `LODGE_INDEX=off`); `test_interrupted_keep_state_leaves_no_state` (a failure after the buckets are written: `state()` finds nothing); `test_two_builders_of_one_state`.
  `tests/e2e/test_indexed_reads.py`: `test_edit_on_disk_then_show_sees_it`; `test_commit_then_show_sees_it`; `test_branch_mode_after_fetch_sees_the_new_tip`; `test_viewer_factory_has_no_read_model`.
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; the replay at all three sizes for the four reads, `cold`, `seen`, and `changed`, recorded as provisional (d-26e6zj).
- [ ] **Step 5:** commit, push.

### Task 10b: Indexed search

**Files:**
- Create: `src/lodge/gitstore/index_words.py` (FTS5 candidates and word sets)
- Modify: `src/lodge/app/indexed.py` (search), `src/lodge/app/read_model.py` (words per parse), `src/lodge/app/ports.py` (`Index` gains the methods below), `src/lodge/gitstore/index_states.py` (words rows dropped with the last state that uses them)
- Test: `tests/gitstore/test_index_words.py` (new), `tests/app/test_indexed_search.py` (new), `tests/e2e/test_index_property.py` (new)

**Interfaces:**
- Consumes: Task 6's `rank`, `Candidate`, `parse_query`, `needs_memory`; Task 5's `family`, `citers`, `cites`; Task 10a's states.
- Produces:
  ```python
  class Index(Protocol):                       # in addition to Task 10a's
      def keep_words(self, words: Mapping[FileKey, tuple[str, str]]) -> None   # title words, statement words, space-joined
      def candidates(self, words: Collection[str], every: bool) -> dict[FileKey, tuple[frozenset[str], frozenset[str]]] | None
          # the keys with any (or every) word, with their title and statement word sets; None without FTS5
  ```
- Words (d-eby5pb): FTS5 table `(key, title, statement)` with `tokenize='ascii'`, text `" ".join(sorted(core.words(...)))`; with no FTS5 (`sqlite3.OperationalError` creating the table) `candidates` returns None and the search runs in memory.
- An indexed search: when `needs_memory` holds for any query, or `candidates` is None, the whole search runs in memory (d-rs76ks); otherwise candidates are the keys holding any query word (for a code, also those holding every word of the code), the exact ID if it exists, and the family from `codes`; their rows in this state whose `key` equals the candidate key (an older parse of a record is not a candidate); `cites` checks citers on the parse's text; a phrase checks `tokens` on the parse's text; `rank` orders, with the word sets from `candidates`, the same function as in memory.
  An empty query or a filter-only search reads `all_rows`.
- The property test of d-rs76ks lives here, over every read, because only now does every read go through the index.

- [ ] **Step 0:** skeleton.
- [ ] **Step 1: Write the failing tests:** `test_index_words.py`: `test_ascii_tokenizer_returns_core_words` (words with digits, non-ASCII letters, and combining marks come back as the same set); `test_any_and_every`.
  `test_indexed_search.py` (a fake index): `test_search_prints_as_in_memory` (300 seeded searches over the 500-record store: words, `--phrase`, codes with and without families, function-word phrases and codes, empty queries, every filter, several queries); `test_older_parse_of_a_record_is_not_a_candidate`; `test_needs_memory_queries_run_in_memory` (a patched `candidates` must not be called); `test_without_fts5_runs_in_memory`.
  `tests/e2e/test_index_property.py` (d-rs76ks): `test_index_reads_equal_memory_under_random_edits` (a 300-record store built with `scripts/bench_store.py`'s builder logic copied into the test's helper, then 60 seeded steps, each one edit from create, edit, delete, untracked file, touch only, stage, commit, CRLF rewrite under an attributes file, assume-unchanged edit, skip-worktree removal; after each step a seeded read from `show`, `search`, `waiting`, `threads`, and `thread` prints the same text and exit status with the index as with `LODGE_INDEX=off`; bounded to about 60 s, the seed printed on failure).
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; search lines of the replay at all three sizes, `seen` and `changed`, with each search's candidate count, provisional (d-26e6zj, d-me8vm3).
- [ ] **Step 5:** commit, push.

### Task 10c: The published state's facts from the index

**Files:**
- Modify: `src/lodge/app/read_model.py` (`ChangeFacts` from stored facts), `src/lodge/app/indexed.py`
- Test: `tests/app/test_published_facts.py` (new)

**Interfaces:**
- Consumes: Task 2's `ChangeFacts`; Task 10a's `facts` and `keep_state`.
- Produces: building a state whose published ident has stored `StateFacts` passes `ChangeFacts(published_status, published_problems from those facts' sort keys, after_derived, after_problems)` to `check_change`, so `derive` and `check_state` run on the current snapshot only; every build stores the current snapshot's own facts under its ident, and the published snapshot's when it computed them.
  The published snapshot itself is still assembled from the parse cache, since checks 4, 5, and 6 compare records.
  This is an optimisation of the read after one changed record only; the gate never uses it (d-q0tb8r).

- [ ] **Step 1: Write the failing tests:** `test_published_facts_equal_full` (the `CheckResult` of a state built with stored facts equals one built without, for published states holding a duplicate code, a hand-edited published decision, an out-of-order entry, and a cycle, each with a new problem on the same path in the current state); `test_facts_keyed_by_ident_alone` (two stored states sharing a published ident read the same facts); `test_absent_facts_are_computed_and_kept`.
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; the replay's `changed` mode at `s90000` with the phase times of one changed-record read, provisional (d-26e6zj).
- [ ] **Step 5:** commit, push.

### Task 11: Untracked files through folder signatures

**Files:**
- Create: `src/lodge/gitstore/folders.py`
- Modify: `src/lodge/gitstore/identity.py` (the walk replaced when an index is writable or holds rows), `src/lodge/gitstore/index_db.py` (a `folders` table), `src/lodge/main.py` (the store is handed the index at construction)
- Test: `tests/gitstore/test_folders.py` (new)

**Interfaces:**
- Consumes: Task 8b's identity; Task 9's index and failure modes.
- Produces: the files on disk that `base` lacks come from a table `folders(path, ino, mtime_ns, ctime_ns, listed_at_ns, names, base)`, `names` being `marshal` of the folder's entries with their kind; for each folder lodge takes `stat`, then `os.scandir`, then the listing time, in that order (the correctness review's M7); a folder whose `stat` matches its row, whose row's `ctime_ns` is at least 2 s before its `listed_at_ns`, and whose `base` equals the current base tree keeps its recorded extra names; any other folder is listed again, its subfolders followed, and its row rewritten when the index is writable (d-8kq2nk).
  Without a usable index the walk of Task 8b runs, so the output is the same.

- [ ] **Step 1: Write the failing tests** (`tmp_path`, each comparing with Task 8b's walk): `test_unchanged_folders_are_not_listed` (patched `os.scandir` not called on a second identity); `test_new_file_in_a_listed_folder`; `test_new_subfolder_with_a_file`; `test_deleted_untracked_file`; `test_rename_within_a_folder`; `test_change_in_the_same_second_as_the_listing` (a row listed within 2 s of the folder's ctime is not trusted); `test_mtime_set_back_still_detected` (`os.utime` to the old mtime after adding a file: ctime differs); `test_base_change_relists`; `test_read_only_index_falls_back_to_the_walk`.
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; the replay at 160,000 files, `seen`, recorded with the identity's share; the tests run once with `--basetemp` on a FUSE-mounted disk where one is at hand, the result recorded, and if any fails there the signature cache is disabled on that file system kind (detected by `os.statvfs` and `/proc/mounts`) with the walk used instead.
- [ ] **Step 5:** commit, push.

### Task 12: The recorded table, and the stop on the targets

**Files:**
- Create: `docs/superpowers/plans/2026-10-31-lodge-at-scale/timings.md`
- Modify: `README.md` (one paragraph: the index, where it lives, one file per build, that it is safe to delete, `LODGE_INDEX=off`)

**Interfaces:**
- Consumes: every task.
- Produces: `timings.md`, for `s900`, `s9000`, and `s90000` on native disk, per line of `scripts/bench_reads.txt`: the base build of Task 1, this branch `cold`, `seen`, and `changed`, `check --gate` included, with the output and exit-status comparison against the base build (identical, or the lines Tasks 5 to 7 changed on purpose, named); each search's candidate count, with searches over 5,000 candidates in a table of their own (d-me8vm3); the index file's size per store; the machine's Python, SQLite, and disk kind; where a FUSE-mounted copy of `s90000` is at hand, the same `show {code}` `seen` on it, one line, without its path.
- [ ] **Step 1:** run the replay; write `timings.md`.
- [ ] **Step 2:** the stop (d-26e6zj, d-232gxs): if a point read or a search under 5,000 candidates at 160,000 files is above 0.3 s `seen`, or a read is above 3 s `changed`, `timings.md` gives the phase table, and the ledger records that the server question goes to the coordinator; broad searches go to the coordinator with their numbers, whatever they are.
- [ ] **Step 3:** gate, commit, push.
