# lodge at scale: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** an agent's reads through lodge are cheap and fast at 160,000 record files: the superlinear steps go, headers parse with libyaml, identical states are not compared, reads batch several refs and queries and treat codes as codes, and a local SQLite index answers a read of a seen state in at most 0.3 s on native disk.

**Architecture:** `core` gains linear checks, one `derive` per snapshot, a C loader with a fallback, a per-file parse and an assembly from parses, a plain-tuple codec, the new search ranking, and code families.
`app` gains the identical-state shortcut, multi-ref and multi-query reads, an `Index` port, and a read path that answers `show`, `search`, `waiting`, `threads`, and `thread` from stored rows.
The `Store` port moves from whole trees to listings of blob IDs with texts on demand and a cheap state identity; `gitstore` computes the identity from git and a folder-signature cache, and holds the SQLite index in new modules.
The command line gains `show REF...`, `search Q...`, and `guide --read`; `scripts/` gains the read-replay benchmark.

**Tech stack:** Python 3.12 or later, uv, PyYAML (with libyaml where present), pytest, mypy (strict), Ruff, Vulture; the standard library's `sqlite3` (FTS5 where present), `marshal`, `hashlib`, `gc` (in `main.py` only), and `subprocess` (in `gitstore` only).

**Spec:** `lodge spec`, with the coordinator's rulings for this plan recorded as d-1bww1r (correctness first), d-1ftgg3 (speed order), d-232gxs (the index and its targets), d-3g6ard (leaner reads), and d-542m5g (benchmarks).
The brief is `docs/superpowers/plans/2026-10-31-lodge-at-scale/brief.md`; the planner's probes and their output are in `docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-report.md` and `probes/`.
The plan argues from them, never over them; where `lodge spec` and a task disagree, the spec wins and the builder reports it.

## Global Constraints

- One brief per task; the builder sees its brief, `CLAUDE.md`, and the repository.
- Test-first: each named test is written and seen failing before its code; every existing test keeps passing, edited only where a task says so.
- The gate after every task: `sh scripts/check.sh` green (ruff format, ruff, mypy strict, vulture, pytest, `lodge check --gate`); then stage with explicit paths, commit with `git -c user.name="Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, the message ending `Co-Authored-By: Claude <noreply@anthropic.com>`, and push `read-speed` to `origin`; never `main`.
- Correctness first (d-1bww1r): no task changes a check's result, a problem's wording, or what the gate compares, except where it records a product decision with a spec edit.
  The gate and `add` derive and check in full on every store; they may use the parse cache, which is content-addressed.
- Structure (`tests/structure_rules.py`, `tests/structure_tables.py`): allowed imports as `ALLOWED`, no new package and no new edge (d-5zqvxb); front doors only; no cycles; no module over 300 lines, tests included; `core` imports only `CORE_MODULES` (`marshal`, `zlib`, and `sqlite3` are not among them and stay out of `core`); `subprocess` only in `gitstore`; file I/O only in `gitstore` and `cli`.
- `core` and `app` read no clock and no randomness; the time comes from `Clock`.
- Modules near the limit take no new code beyond the lines a task states: `gitstore/checkout.py` (267 lines), `core/views.py` (245), `core/derive.py` (243), `cli/parser.py` (236), `core/apply.py` (277), `app/writes.py` (214), `core/feedback.py` (209); new code goes in the new modules each task names.
- Tests near the limit take no new tests: `tests/gitstore/test_branch.py` (298), `tests/app/test_reads.py` (282), `tests/core/test_derive.py` (273), `tests/gitstore/test_checkout_safety.py` (240); new tests go in the new files each task names, marked "(new)", with basenames unique across `tests/`, `tests/core/`, `tests/app/`, and `tests/gitstore/`.
- Vulture scans `src` and `tests`; every produced name is read in the task that adds it.
- Tests never touch a real repository: git only in `tmp_path` through the existing helpers (`tests/gitstore/repos.py`, `tests/e2e/conftest.py`), no network; fixtures are a made-up project, never another project's records.
- Benchmarks run on native disk under `/var/tmp/lodge-bench/` with stores from `scripts/bench_store.py` (`s900` 1,593 files, `s9000` 16,008, `s90000` 159,716); timings in a task report give the command, the store, and best of three; never a timing assertion in pytest.
- Timing claims compare like with like: the same Python, a native-disk virtual environment with its bytecode compiled (`python -m compileall`), and the store on native disk; a FUSE-mounted disk is reported apart when used.
- Records only through `lodge add`; drafts under `.drafts/`; `lodge add --dry-run` before every `lodge add`; product decisions have `scope: product`, `decided_by: coordinator` unless the coordinator says otherwise, and `work_item` this plan; a number in a statement or reasoning gets a `numbers` handle unless it is a label.
- User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line.

## Calls made

Each is recorded in lodge as a process decision with its reasoning, handles, and cost if wrong; a task repeats what it needs.

1. d-5xhxh1: leaner reads (Tasks 5 to 7) come before the index (Tasks 8 to 11), after the four speed tasks, because the index's search only feeds core's ranking.
2. d-5zqvxb: the index lives in `gitstore` as new modules behind an `Index` port in `app`.
3. d-8kq2nk: checkout-mode identity is the `HEAD` tree of `lodge/`, the paths `git diff-index --cached HEAD` and `git diff-files` name (read and hashed), and the files `HEAD` lacks, found through a folder-signature cache under git's racy rule; never `git status`.
4. d-atsx8n: a path git may convert (`core.autocrlf`, or a `text`, `eol`, `filter`, `ident`, or `working-tree-encoding` attribute) is always read from disk.
5. d-c400w8: the parse cache is keyed by path and git blob ID and stores `marshal` of plain tuples, never `pickle`.
6. d-c4w7xy: a state's rows hold the derived facts only, in 1,024 buckets by the last two characters of the ID.
7. d-eby5pb: FTS5 over core's own words with the `ascii` tokenizer gives candidates; core ranks; without FTS5, search runs in memory.
8. d-f3r5aq: results are keyed by a schema number, a digest of lodge's package files, and a digest of the core settings; a state's result expires at the date of a new decision dated after its build.
9. d-hf2fms: four states kept, first in first out; a read of a seen state writes nothing.
10. d-kj554d: an unwritable or locked index is opened read-only or skipped, a database error drops to memory, a corrupt or mismatched file is rebuilt when writable; output never changes and a read never fails.
11. d-m0g9tx: stored rows serve `show`, `search`, `waiting`, `threads`, and `thread`; `spec`, `timeline`, `draft`, `check`, `id`, `add`, the gate, and the viewer build the snapshot in memory from the parse cache.
12. d-n9w4by: a query is a code when it is one token of the code grammar with a non-empty family in the state; citers are matched in titles and statements; `show` lists ten siblings and ten citers at most.
13. d-p60ka9: brief lines drop ` · current` under the default status filter, with a first line saying so.
14. d-s2ypth: every command but `view` runs with the cyclic collector off, when `main` runs as the program.
15. d-zyqzkg: identical states skip `check_change`, by the proof in Task 4.

## Expected cost at 160,000 files (estimates from the probes, native disk)

| Read | Today | After Tasks 2 to 4 | After Task 11 |
|---|---|---|---|
| any read, seen state | not finished in 900 s on a FUSE disk; natively the phases of `probes/phases.py` sum to 53 s with `_missing` made linear, and today's `_missing` is quadratic (6.7 s at 16,008 files, so about 100 times that at 160,000) | about 14 s: trees 5.5, one libyaml load 7.1, `derive` 0.9, `check_state` about 0.5 | about 0.2 s: import 0.10, git 0.08 (`rev-parse`, `merge-base`, `diff-index` 0.012, `diff-files` 0.045), folder signatures 0.01, SQLite 0.01 |
| after one changed record (checkout, uncommitted) | as above | about 25 s (two loads, the change check) | about 3 s: listing 0.06, parse cache 0.45, assembly 0.2, `derive` 0.9, `check_state` 0.3, the change check with stored published facts 0.6, rows 0.6, writing 0.2 |
| first read in a clone | as above | as above | about 12 s: libyaml parse 7, FTS 1.1, parse cache 1.4, state 2.5 |

The second column of the last row is the risk: Task 10 measures it, and over 3 s the task reports its phase table and stops for the coordinator.

## Review Focus

1. A read whose output differs between the index path, the in-memory path, and today's code on the same store: the differential tests of Tasks 4, 9, and 10, and the replay of Task 12 comparing output byte for byte.
2. A checkout state identity that misses a change on disk: staged, unstaged, untracked, ignored, deleted, renamed, a symbolic link, a non-regular file, a file git converts, a file created in the same second as the folder was listed (Tasks 8 and 11).
3. A cached result used where its inputs differ: another lodge build, other settings, a later time for a future-dated decision (Task 10's expiry), a published state that moved.
4. A read that fails, hangs, or writes in a read-only sandbox or with the database locked (Task 9).
5. A search result list that differs from the ranking's definition because the index's candidates missed a record (Task 10's property test).
6. A check whose wording or result changed in the linear rewrites of Task 2.

---

### Task 1: Benchmarks

**Files:**
- Modify: `scripts/bench_store.py` (its four ruff findings only, with `uv run ruff check scripts/bench_store.py` naming them)
- Create: `scripts/bench_reads.py`, `scripts/bench_reads.txt`
- Report: `docs/superpowers/plans/2026-10-31-lodge-at-scale/task-1-report.md`

**Interfaces:**
- Consumes: nothing.
- Produces:
  ```
  uv run --frozen python scripts/bench_reads.py STORE --lodge CMD [--against CMD2] [--runs N] [--commands FILE]
  ```
  - `CMD` and `CMD2` are commands that run a lodge build, such as `/var/tmp/lodge-bench/venv-a/bin/lodge`; each line of `FILE` (default `scripts/bench_reads.txt`) is one lodge argument list in shell syntax, run with `shlex.split`, never through a shell.
  - Placeholders in a line: `{entry}` the first entry ID and `{decision}` the first decision ID in the store's file order under `lodge/spec/` and `lodge/decisions/`, `{code}` the first code found, `{code2}` the second; read from file names and headers of the store, never from lodge's output.
  - For each line: best and median wall time of `N` runs (default 3) per build, exit code, output size in characters, and with `--against` whether the two builds' standard output is byte-identical; a Markdown table on standard output, one row per line.
  - `--changed` copies the store to a temporary folder beside it, edits one entry's statement on disk (not staged), and times every line once after the change, to measure the read after one changed record; the copy is removed at the end.
- `scripts/bench_reads.txt`: `show {code}`, `show {entry} --reasoning --provenance`, `show {decision}`, `search berth --brief`, `search "berth crane" --brief`, `search {code} --brief`, `search berth`, `waiting`, `threads`, `spec --area area-001`, `check`, and `check --gate` (the last measured, not targeted); Task 5 adds `show {code} {code2} {entry}` and Task 6 adds `search berth tide --brief`.

- [ ] **Step 1:** fix the four ruff findings of `scripts/bench_store.py` without changing the stores it writes; check by rebuilding `s900` to a temporary folder and comparing `git rev-parse HEAD^{tree}` with `/var/tmp/lodge-bench/s900`.
  Then give the stores code families and citations, which today's stores lack: for one coded decision in fifty, a second decision coded `CODE-n.why`, and one new entry whose statement cites `CODE-n`; rebuild `s900`, `s9000`, and `s90000` and record their file counts.
- [ ] **Step 2:** write `scripts/bench_reads.py` (no tests: `scripts/` is outside pytest and mypy; `ruff check scripts` clean).
- [ ] **Step 3:** build a native-disk venv of this branch (`uv venv /var/tmp/lodge-bench/venv-base`, `uv pip install .`, `python -m compileall`), and record in the report the table for `s900` and `s9000`, and for `s90000` one `show {code}` under `timeout 900`, reported as not finished if it is not.
- [ ] **Step 4:** gate, commit, push.

### Task 2: The superlinear steps, one `derive` per snapshot, and the collector

**Files:**
- Modify: `src/lodge/core/check_change.py` (`_missing`; the keyword `facts`), `src/lodge/core/check_areas.py`, `src/lodge/core/check_cycles.py`, `src/lodge/core/check_state.py` (the keyword `derived`), `src/lodge/core/check_entries.py` and `_links_to_dead` (take the statuses from `facts`), `src/lodge/core/derive.py` (at most 10 lines: the `.index` scans in `_behind_entry_edits` and `_follows_author_change` become position maps), `src/lodge/core/__init__.py`, `src/lodge/app/state.py` (derive once, pass it), `src/lodge/app/reads.py` (the gate passes what it has), `src/lodge/main.py` (`gc.disable()` when `argv is None` and the command is not `view`)
- Test: `tests/core/test_linear_checks.py` (new), `tests/test_entry_point.py` (one test for the collector, if it fits under 300 lines; else `tests/test_collector.py` (new))

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
  `check_change` with `facts=None` computes `change_facts(published, after)` first, so every caller that passes nothing gets today's result; `derive` runs once per snapshot in one checked read and once more per state the gate compares.
- `check_areas`: entries grouped by area in one pass; an order's duplicates counted once with `collections.Counter` semantics written with a dict (no new module); the same problems in the same order, wording unchanged.
- `check_cycles`: Tarjan's strongly connected components, iterative (no recursion limit), over `rests_on` targets that exist; for each entry `i` in a component of two or more, the problem lists the other members sorted, exactly as today; a self-link stays check 2's alone, as today (today's `others` is empty for it).
- `_missing`: the union of the `after` IDs built once.

- [ ] **Step 1: Write the failing tests** in `test_linear_checks.py`: `test_missing_uses_one_union` (a snapshot of 2,000 entries with one published entry missing gives exactly today's one problem); `test_check_areas_same_problems_as_before` (each sample of `tests/core/samples.py` and a 50-area made-up snapshot with an entry unlisted, an order naming a retired entry, a duplicate, and a folder without `_area.md`: the problems equal those of a copy of today's function kept in the test file as the oracle); `test_cycles_same_as_reachability` (random `rests_on` graphs of 1 to 40 entries, seeded, against a copy of today's reachability function as oracle, 200 graphs); `test_deep_chain_has_no_recursion_error` (a chain of 5,000 entries); `test_check_change_with_facts_equals_without` (every sample pair in `tests/core/test_check_change.py`'s fixtures, and the 50-area snapshot with an edited entry and a new decision: same `CheckResult`); `test_derive_once_per_checked_read` (count calls of `derive` through `read_checked` on a `MemoryStore` with `staged=True`: 2, one per snapshot; with identical trees after Task 4 it becomes 1, so this test asserts `<= 2` now and Task 4 tightens it).
  Collector: `test_main_disables_the_collector_for_one_shot_commands` (run `lodge.main.main` with `argv=None` patched through `sys.argv` for `guide`, then `gc.isenabled()` is False, re-enabled in a `finally`; for `view` it stays enabled, with `serve` patched out).
- [ ] **Step 2:** run them; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; then `probes/phases.py` at `s9000` and `s90000` without its `_missing` patch (delete the patch lines in a scratch copy, not in the repository), recording `check_state`, `derive`, and `check_change` in the report; expected `check_state` under 1 s at 160,000 files.
- [ ] **Step 5:** commit, push.

### Task 3: libyaml with a fallback to the Python loader

**Files:**
- Modify: `src/lodge/core/yamlio.py` (if it would pass 120 lines, the C loader goes in `src/lodge/core/yamlfast.py` (new))
- Test: `tests/core/test_yaml_loaders.py` (new)

**Interfaces:**
- Consumes: nothing.
- Produces: `load_yaml(text)` tries a loader built on `yaml.CSafeLoader` with today's empty implicit resolvers, kept constructors, surrogate-pair joining, and duplicate-key refusal (written without the two-argument `super()`, which fails on another base class), and on any exception from it calls today's pure-Python path, so every value, error message, and line number comes from today's loader whenever the C loader does not succeed; where `yaml.__with_libyaml__` is False, today's path alone.

- [ ] **Step 1: Write the failing tests:** `test_c_loader_is_used_when_present` (a patched counter on the C path sees a call for a plain header); `test_same_value_as_the_python_loader` (every header in today's yamlio tests and fileformat tests, plus a seeded generator of 500 headers mixing quoted and plain scalars, flow and block lists, `yes`, `14:14`, `~`, `1234`, escaped surrogate pairs, U+2028, tabs, and unicode: the C path's value equals the Python path's, or the C path raised and the result equals the Python path's); `test_errors_come_from_the_python_loader` (a duplicate key, bad indentation, an unreadable character: `YamlError` message and line equal today's); `test_falls_back_without_libyaml` (patched `__with_libyaml__ = False`).
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; `probes/phases.py --pure-yaml` against without at `s9000`, recorded.
- [ ] **Step 5:** commit, push.

### Task 4: Identical states reuse the snapshot and skip the change check

**Files:**
- Modify: `src/lodge/app/state.py`
- Test: `tests/core/test_identical_change.py` (new), `tests/app/test_identical_reads.py` (new); tighten Task 2's `test_derive_once_per_checked_read`

**Interfaces:**
- Consumes: Task 2's `facts`.
- Produces: `read_checked` loads the published tree only when `(current.files, current.attachments) != (published.files, published.attachments)`; when equal it adds no change problems (d-zyqzkg).
  The proof, which the report repeats against the code as built: for identical states every problem of `check_state(after)` is in `known`; `_missing` finds every ID; `_dates`, `_imports_over_live`, `_unlisted_sources`, and the decision half of `_links_to_dead` iterate over new decisions or new records, of which there are none; check 4 compares each entry with itself and finds no listed change wanted; check 5 compares each decision and thread with itself; the entry half of check 6 looks only at `rests_on` targets the published entry lacks.
  Task 8 replaces the comparison of file mappings by a comparison of state identities.

- [ ] **Step 1: Write the failing tests:** `test_check_change_of_a_state_with_itself_is_empty` (every sample snapshot of `tests/core/samples.py`, the builders' snapshots used in `tests/core/test_check_change.py`, and snapshots holding a hand-edited published decision, a duplicate ID, a cycle, and an out-of-order entry: `check_change(s, s, settings, now).problems == ()`); `test_identical_trees_load_once` (count `load` calls through `read_checked` on a `MemoryStore` without `staged`: 1); `test_identical_read_output_unchanged` (show, search, waiting, and check on four sample stores give the same results with the shortcut patched off and on).
- [ ] **Step 2:** run; expected FAIL on the counts.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; `scripts/bench_reads.py --against` today's build at `s900`, `s9000`, and `s90000` (the last now finishes), output byte-identical on every line, the table in the report.
- [ ] **Step 5:** commit, push.

### Task 5: `show REF...`, siblings, and citers

**Files:**
- Create: `src/lodge/core/codes.py` (`family`, `citers`, `is_code_token`, `cites`)
- Modify: `src/lodge/core/__init__.py`, `src/lodge/app/reads.py` (a `show_many`), `src/lodge/app/lodge.py`, `src/lodge/app/results.py` (`Shown` gains `siblings` and `citers`), `src/lodge/cli/parser.py` (at most 6 lines: `ref` becomes `refs`, `nargs="+"`), `src/lodge/cli/commands.py`, `src/lodge/cli/output.py` (the two lines, the separators), `scripts/bench_reads.txt`
- Records: a product decision with an edit of s-3n0ndk, through `lodge add`
- Test: `tests/core/test_codes.py` (new), `tests/app/test_show_many.py` (new), `tests/e2e/test_show_many.py` (new)

**Interfaces:**
- Consumes: Task 4's `read_checked`.
- Produces:
  ```python
  def is_code_token(query: str) -> bool        # one token of [A-Za-z0-9][A-Za-z0-9._-]*
  def family(s: Snapshot, code: str) -> tuple[str, ...]
      # records whose code, casefolded, equals code or starts with code + "."; the code itself first, then by casefolded code
  def cites(text: str, code: str) -> bool
      # code, casefolded, as a whole token: the character before is not in [A-Za-z0-9._-] (or the start),
      # the character after is not in [A-Za-z0-9_-] and is not a "." followed by [A-Za-z0-9] (or the end)
  def citers(s: Snapshot, d: Derived, code: str) -> tuple[str, ...]
      # records outside the family whose title or statement cites code, newest first by (date, ID) as search orders
  def show_many(w: Wiring, refs: Sequence[str], reasoning: bool, provenance: bool) -> ShownMany
  @dataclass(frozen=True) class ShownMany:
      items: tuple[Shown | LodgeError, ...]   # one per distinct record, in the order of the refs; an error in place of a ref that fails
      read: Read
  Shown.siblings: tuple[Level1, ...] = ()     # family(s, code) without the record itself, up to 10
  Shown.citers: tuple[Level1, ...] = ()       # citers(s, d, code), up to 10
  Shown.more: tuple[int, int] = (0, 0)        # siblings and citers left out
  ```
- Output of `lodge show A B C`: the freshness and problem lines once; each record's text as today; between records a line `----- B` naming the ref, so no shell separator is needed; a ref naming a record already shown prints `----- B is d-xxxxxx, shown above`; a ref that fails prints `----- B` then `lodge: <the error>` on standard error in place, and the others still print.
  The exit status is the highest exit code among the failed refs, 0 when none failed.
  One ref prints exactly as today, without a separator line, plus the new lines.
- The new lines, after the level 3 section, only for a record with a code that has siblings or citers: `siblings:` then one brief line each; `cited by:` then one brief line each; then `and N more siblings and M more citing records; lodge search CODE` when any were left out.
- The product decision: `show` takes several refs, printed in one read with each record once, and names a coded record's sibling codes and citing records; it edits s-3n0ndk's third sentence to say so, the rest of the entry unchanged.

- [ ] **Step 1: Write the failing tests:** `test_codes.py`: `test_family_takes_dotted_siblings_not_longer_numbers` (`X-1`, `X-1.why`, `x-1.b`, not `X-10`, `X-1a`); `test_family_orders_the_code_first`; `test_cites_whole_tokens_only` (`see X-1.` yes, `X-1,` yes, `(X-1)` yes, `X-10` no, `X-1.why` no, `AX-1` no, `x-1` yes); `test_citers_exclude_the_family_and_order_newest_first`.
  `test_show_many.py`: `test_each_record_once_in_ref_order` (an ID and its code given both); `test_failing_ref_in_place_and_others_shown`; `test_one_read_for_many_refs` (count `trees()` calls: 1); `test_siblings_and_citers_capped_at_ten` (12 siblings, 11 citers: 10 each and the counts 2 and 1).
  `tests/e2e/test_show_many.py`: `test_show_three_refs_one_output` (separators, exit 0); `test_unknown_ref_exits_2_after_the_others`; `test_single_ref_output_unchanged` (`show ITEM-1` equals the output before this task, kept as a literal in the test).
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement; the product decision through `lodge add --dry-run` then `lodge add`.
- [ ] **Step 4:** gate; bench line `show {code} {code2} {entry}` recorded.
- [ ] **Step 5:** commit, push.

### Task 6: Search: several queries, codes first, phrases, all words first, leaner brief lines

**Files:**
- Create: `src/lodge/core/ranking.py` (the ranking over candidate views; `search.py` keeps `resolve`, `related`, and `Filters`, and calls it)
- Modify: `src/lodge/core/search.py`, `src/lodge/core/__init__.py`, `src/lodge/app/reads.py` (`search_many`), `src/lodge/app/lodge.py`, `src/lodge/app/results.py` (`Listed` gains `query`, `skipped`), `src/lodge/cli/parser.py` (at most 6 lines: `query` becomes `queries`, `nargs="*"`), `src/lodge/cli/commands.py`, `src/lodge/cli/output.py`, `tests/e2e/test_search_brief.py` and `tests/core/test_search.py` (the expectations that print ` · current` or rank by one word, each edit listed in the report), `scripts/bench_reads.txt`
- Records: a product decision with an edit of s-3n0ndk (search semantics, the brief line) through `lodge add`
- Test: `tests/core/test_ranking.py` (new), `tests/app/test_search_many.py` (new), `tests/e2e/test_search_many.py` (new)

**Interfaces:**
- Consumes: Task 5's `is_code_token`, `family`, `cites`.
- Produces:
  ```python
  @dataclass(frozen=True)
  class Query:
      text: str
      words: frozenset[str]          # core.words of the text without its quoted phrases' quotes
      phrases: tuple[str, ...]       # each "..." in the text, lower-cased, whitespace collapsed
  def parse_query(text: str) -> Query
  @dataclass(frozen=True)
  class Candidate:
      view: Level1
      areas: frozenset[str]          # an entry's area; a decision's, the areas of the entries it changes
  def rank(candidates: Iterable[Candidate], query: Query, filters: Filters, family: Sequence[str],
           citing: Sequence[str], limit: int) -> tuple[list[str], int]
  def search_counted(s, d, query, filters, limit) -> tuple[list[str], int]   # builds every candidate and calls rank
  ```
- The ranking (`rank`), for a non-empty query, among candidates passing the filters:
  1. the exact ID;
  2. when `is_code_token` and the family is not empty, the family in `family`'s order, then `citing`'s order (d-n9w4by); otherwise the record whose code equals the query, as today;
  3. records whose title and statement hold every phrase (substring of the lower-cased, whitespace-collapsed text) and every word, by score;
  4. records holding at least one word or phrase but not all, by score;
  score as today (3 per query word in the title, 1 per word in the statement, 3 or 1 per phrase likewise), ties newest first by `(date, ID)`.
  An empty query lists by `(date, ID)` newest first, as today.
- `lodge search Q1 Q2 ...`: one read; each query's results under a line `query: Q1 · N matches` (only when more than one query), a record already printed under an earlier query left out and counted in `(k already listed)` on that line; `--limit` applies per query; no query lists newest first, as today.
  A quoted multi-word argument is one query; unquoted words are separate queries, which the guide says.
- Brief lines (d-p60ka9): under the default status filter, a line omits ` · current`, and the output's first line, after the freshness lines, is `records are current unless marked`; under any other `--status` the status prints as today.
- The product decision: search takes several queries, ranks a code's family and citers first, matches quoted phrases, ranks records with every word first, and brief lines omit the default status; it edits s-3n0ndk's first two sentences, its third unchanged from Task 5.

- [ ] **Step 1: Write the failing tests:** `test_ranking.py`: `test_exact_id_first`; `test_code_family_then_citers_then_words`; `test_code_without_family_ranks_as_words` (the plain-word ranking of today for a code no record carries); `test_phrase_must_be_contiguous` (`"settled point"` against `point settled`); `test_all_words_before_some_words`; `test_ties_newest_first`; `test_filters_apply_to_family_and_citers`; `test_rank_over_candidates_equals_rank_over_all` (for 300 seeded queries over a made-up 400-record snapshot: `rank` over the records matching any word, phrase word, the family, or the citers equals `rank` over every record; the property Task 10 relies on).
  `test_search_many.py`: `test_each_record_once_across_queries`; `test_limit_per_query`; `test_one_read_for_many_queries`.
  `tests/e2e/test_search_many.py`: `test_two_queries_with_headers`; `test_quoted_phrase_is_one_query`; `test_brief_omits_current_and_says_so`; `test_brief_with_status_any_prints_status`.
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
- Consumes: Tasks 5 and 6 (the commands it shows).
- Produces: `lodge guide --read` prints at most 25 lines: what lodge holds (one line each for decisions, entries, areas); `lodge waiting` first in a session; quoted examples, each on its own line in backticks: `lodge search "phrase of words" --brief`, `lodge search CODE --brief` (the family and citers first), `lodge search word1 word2 --brief` (two queries), `lodge show REF REF REF`, `lodge show CODE.why --reasoning`, `lodge show REF --provenance`; that multi-word queries need quotes; what "awaiting the author", "in doubt", "fails check", `problem:`, and an unmarked status mean; that `show` lists siblings and citers; never the writing rules.
- The product decision: lodge prints a short reading guide with `lodge guide --read` beside the full guide; it edits s-7f10zc's first sentence.

- [ ] **Step 1: Write the failing tests:** `test_guide_read_is_short_and_has_no_writing_rules` (at most 25 lines; no `lodge add`, `lodge draft`, `decided_by`); `test_guide_read_examples_run` (each backticked example with `REF`, `CODE`, and words replaced from the seeded project runs with exit 0); `test_full_guide_points_at_read`.
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement; the product decision.
- [ ] **Step 4:** gate, commit, push.

### Task 8: Listings, blob IDs, and the state identity in the Store port

**Files:**
- Create: `src/lodge/core/listing.py` (`Listing`, `blob_id`, `parse_file`, `assemble`), `src/lodge/gitstore/identity.py` (checkout identity and overlay), `src/lodge/gitstore/listing.py` (listings and texts for both modes), `src/lodge/gitstore/attributes.py` (the conversion check of d-atsx8n)
- Modify: `src/lodge/core/snapshot.py` (`load` becomes `assemble` of `parse_file`s), `src/lodge/core/__init__.py`, `src/lodge/app/ports.py` (the new Store methods), `src/lodge/app/state.py`, `src/lodge/app/reads.py`, `src/lodge/app/writes.py` (at most 12 lines: reads by listing; `publish` compares blob IDs), `src/lodge/app/threads.py`, `src/lodge/app/confirm.py`, `src/lodge/gitstore/checkout.py` (at most 25 lines, moving `disk_tree` and `_read` into `identity.py` is allowed and frees lines), `src/lodge/gitstore/branch.py`, `src/lodge/gitstore/published.py`, `tests/app/fakes.py` (`MemoryStore` gives listings with `blob_id` of each text)
- Test: `tests/core/test_listing.py` (new), `tests/gitstore/test_identity.py` (new), `tests/gitstore/test_listing_modes.py` (new), `tests/gitstore/test_attributes.py` (new)

**Interfaces:**
- Consumes: Task 4's shortcut (its comparison becomes `current.ident == published.ident`).
- Produces:
  ```python
  # core/listing.py
  def blob_id(raw: bytes) -> str          # git's: sha1 of b"blob %d\0" % len(raw) + raw, hex
  Parsed = Decision | SpecEntry | Area | Thread | Problem
  def parse_file(path: str, text: str) -> Parsed | None   # None for attachments and .gitkeep; Problem for strays
  @dataclass(frozen=True)
  class Listing:
      rev: str | None
      ident: str                          # equal idents mean equal files and attachments
      blobs: Mapping[str, str]            # path -> blob_id, every file but attachments
      attachments: frozenset[str]
  def assemble(parsed: Mapping[str, Parsed | None], attachments: frozenset[str]) -> Snapshot
      # load(tree) == assemble({p: parse_file(p, t) for p, t in tree.files.items()}, attachments of tree)
  # app/ports.py, Store gains:
  def identities(self) -> tuple[str, str]           # current and published ident; branch mode fetches and accepts here
  def listings(self) -> tuple[Listing, Listing]      # the same states identities() named
  def texts(self, listing: Listing, paths: Collection[str]) -> dict[str, str]
  def gate(self, current: Listing) -> Gate           # Gate holds Listings
  # trees() is removed; read_state, add, the thread writes, and the confirmation move to listings and texts
  def publish(self, base: Listing, writes: Mapping[str, str], message: str) -> PublishOutcome
  ```
- Identity, branch mode: `ident` is `rev-parse <tip>:lodge` (the empty tree's ID when absent); published is the accepted tip's when the branch was rewritten, else the same.
- Identity, checkout mode (d-8kq2nk): `base` = `rev-parse HEAD:lodge` (empty tree when `HEAD` is unborn or lacks `lodge/`); `overlay` = for each path named by `git diff-index --cached --no-renames -z --name-only HEAD -- lodge` or `git diff-files --no-renames -z --name-only -- lodge`, or present on disk but absent from `base`, or a path d-atsx8n says git may convert: the file read as today's `_read` reads it, `blob_id` of its bytes, or deleted when it is not on disk; `ident` = sha1 over `base` and the sorted overlay.
  In this task the files `base` lacks are found with a names-only `os.scandir` walk of `lodge/`, compared folder by folder with `base`'s names (from `ls-tree` on a miss, cached in the store object for the process); Task 11 replaces the walk with the signature cache.
  Published: the merge base's `lodge/` tree, as `published_state` finds it today, its missing-state message unchanged.
- Listing: `ls-tree -r` of `base` with the overlay applied; `texts` reads git blobs with one `cat-file --batch` and overlay files from the bytes already read.
- d-atsx8n's check: when `git config --get-regexp '^core\.(autocrlf|attributesfile)$'` gives nothing set to true or input, no `$GIT_COMMON_DIR/info/attributes` exists, and no `.gitattributes` is in the working tree root or under `lodge/` (from the listing), no path converts; otherwise `git check-attr --stdin -z text eol filter ident working-tree-encoding` over the listing's paths, and every path with any of them set (not `unspecified` or `unset`) joins the overlay; the result is cached in the store object for the process (Task 10 stores it in the index with the attributes files' bytes as its key).
- Reads compare `ident`s for Task 4's shortcut; the gate's "committed against working tree" note stays, decided by comparing the `HEAD` tree's ident with the current ident.

- [ ] **Step 1: Write the failing tests:** `test_listing.py`: `test_blob_id_matches_git` (three texts against `git hash-object --stdin` run in `tmp_path`); `test_assemble_equals_load` (every sample tree, a tree with a duplicate ID, a stray, an attachment, and an unreadable header); `test_parse_file_ignores_attachments_and_gitkeep`.
  `test_identity.py` (each in a `tmp_path` repository, the listing's files read through `texts` equal today's `disk_tree`, and `ident` changes exactly when the files or attachments change): `test_clean_checkout`; `test_unstaged_edit`; `test_staged_edit_then_reverted_on_disk`; `test_untracked_file`; `test_ignored_file_under_lodge` (a `.gitignore` entry for it); `test_deleted_file`; `test_staged_deletion_left_on_disk` (`git rm --cached`); `test_rename`; `test_symbolic_link_reads_as_its_target`; `test_fifo_reads_as_empty` (skipped where `os.mkfifo` is missing); `test_touched_but_unchanged_keeps_the_ident`; `test_unborn_head`; `test_head_without_lodge`.
  `test_attributes.py`: `test_no_attributes_no_check_attr_call` (a patched `run` sees no `check-attr`); `test_autocrlf_true_reads_every_file_from_disk` (a CRLF file committed with `core.autocrlf=true` in the repository's own config: the listing's text equals the disk bytes); `test_text_attribute_on_one_pattern` (`lodge/decisions/*.md text eol=crlf` in `.gitattributes`: those paths read from disk, others from git).
  `test_listing_modes.py`: `test_branch_mode_ident_is_the_tip_tree`; `test_rewritten_branch_publishes_the_accepted_tree`; `test_publish_rejects_a_changed_blob` (checkout: the file changed on disk after the listing).
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement; existing gitstore and app tests keep passing, edited only for the port's new names, each edit listed in the report.
- [ ] **Step 4:** gate; `bench_reads.py --against` Task 7's build at all three sizes, output byte-identical, timings recorded.
- [ ] **Step 5:** commit, push.

### Task 9: The parse cache, and the index's open, versioning, and failure modes

**Files:**
- Create: `src/lodge/core/codec.py` (plain tuples), `src/lodge/gitstore/index_db.py` (opening, schema, meta, the failure modes), `src/lodge/gitstore/index_parses.py` (the parse cache), `src/lodge/gitstore/package_digest.py` (the digest of lodge's own files)
- Modify: `src/lodge/app/ports.py` (`Index`), `src/lodge/app/state.py` (snapshots through the cache), `src/lodge/app/lodge.py` (`Lodge` takes `index: Index | None = None`), `src/lodge/gitstore/__init__.py`, `src/lodge/main.py` (opens the index; `LODGE_INDEX=off` in the environment gives `None`), `src/lodge/core/__init__.py`
- Records: a product decision creating an entry in the `storage` area, "A disposable index speeds reads", and listing it in the area's order; the entry rests on s-j8tp0n
- Test: `tests/core/test_codec.py` (new), `tests/gitstore/test_index_db.py` (new), `tests/gitstore/test_index_parses.py` (new), `tests/app/test_parse_cache.py` (new), `tests/e2e/test_index_off_same_output.py` (new)

**Interfaces:**
- Consumes: Task 8's `Listing`, `parse_file`, `assemble`.
- Produces:
  ```python
  # core/codec.py
  def to_plain(value: object) -> object      # dataclass -> (class name, *fields); enum -> ("=" + class name, value); tuple -> list; str, int, None, bool, frozenset as they are
  def from_plain(plain: object, classes: Mapping[str, type]) -> object   # ValueError on any shape it did not write
  CORE_CLASSES: Mapping[str, type]             # every dataclass and enum that a parse or a Level1 or Level3 holds
  # app/ports.py
  FileKey = tuple[str, str]                    # (path, blob_id)
  class Index(Protocol):
      def parses(self, keys: Collection[FileKey]) -> dict[FileKey, Parsed | None]
      def keep_parses(self, parsed: Mapping[FileKey, Parsed | None]) -> None
  # gitstore
  def open_index(common_dir: Path, settings_digest: str) -> Index | None
  ```
- Location: `<git common dir>/lodge/index.sqlite`, created with its folder when missing; journal mode `DELETE` (the common dir may be on a file system without shared memory), `busy_timeout` 200 ms, `synchronous=OFF` (the file is disposable).
- Meta table: schema number (an integer constant in `index_db.py`), the package digest (sha1 over each `.py` file of the installed `lodge` package: relative name, size, `st_mtime_ns`), and the parse format; any mismatch empties every table (d-f3r5aq).
- Parses table: `(path, blob, value)` with `value` = `marshal.dumps(to_plain(parsed))`; `from_plain` with `CORE_CLASSES` on read; a row that fails to decode is a miss.
- Failure modes (d-kj554d), each a test:
  - the folder or file cannot be written (read-only file system, permissions): opened with `mode=ro` through a `file:` URI; reads use what it holds, `keep_parses` does nothing;
  - the database is locked past `busy_timeout`: the write is skipped, the read answers from what it has and from memory;
  - the file is not a SQLite database (`sqlite3.DatabaseError` on reading the meta table): deleted and recreated when writable, otherwise `open_index` returns `None`;
  - the schema or digest differs: emptied when writable, otherwise `None`;
  - any `sqlite3.Error` during a read operation: that operation returns a miss, never raises.
- `app` builds every snapshot (reads, the gate, `add`, `id`, `draft`) as `assemble` of cached parses plus `parse_file` of the misses (texts fetched in one `texts` call), and keeps the misses; `derive` and every check run in full on that snapshot.
- The product decision: lodge keeps a disposable index in the git common dir, never committed, rebuilt when lodge or its settings change, that never changes what a read prints or what the gate decides; its entry rests on s-j8tp0n.

- [ ] **Step 1: Write the failing tests:** `test_codec.py`: `test_round_trip_of_every_parse_kind` (a decision with every field, an entry with `rests_on`, an area with a rank, a thread with an author message, a problem with a line); `test_refuses_unknown_class_and_bad_shapes`; `test_no_pickle_imported` (`codec` and the index modules do not import `pickle`, by `ast`).
  `test_index_db.py` (in `tmp_path`): `test_creates_folder_and_schema`; `test_read_only_folder_opens_read_only` (`chmod 0o500` on the folder, skipped when running as root); `test_read_only_and_missing_returns_none`; `test_locked_database_skips_the_write` (a second connection holds `BEGIN EXCLUSIVE`; `keep_parses` returns within 1 s and writes nothing); `test_corrupt_file_is_rebuilt` (garbage bytes); `test_corrupt_file_read_only_returns_none`; `test_schema_mismatch_empties`; `test_digest_mismatch_empties`.
  `test_index_parses.py`: `test_hit_after_keep`; `test_key_is_path_and_blob` (the same blob at two paths in two areas parses to two areas); `test_undecodable_row_is_a_miss`.
  `test_parse_cache.py` (app, a fake index): `test_second_read_parses_nothing` (count `parse_file` calls: 0); `test_gate_uses_cache_and_checks_in_full` (a cached snapshot with a hand-edited published decision still fails check 5); `test_read_output_same_with_and_without_index` (show, search, waiting, check on four sample stores).
  `tests/e2e/test_index_off_same_output.py`: `test_index_off_same_output` (`show`, `search`, `waiting`, `spec`, `check --gate` print the same with `LODGE_INDEX=off` and without, twice each); `test_read_only_common_dir_reads` (the common dir made read-only after one read: exit 0, same output; skipped as root).
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement; the product decision through `lodge add`.
- [ ] **Step 4:** gate; the replay at all three sizes, cold (index deleted) and warm, recorded; output byte-identical to Task 8's build.
- [ ] **Step 5:** commit, push.

### Task 10: Stored states: rows, answers, and search candidates

**Files:**
- Create: `src/lodge/app/read_model.py` (building a state's rows and answers from a checked `State`), `src/lodge/app/indexed.py` (the five reads from the index), `src/lodge/gitstore/index_states.py` (states, buckets, answers, eviction), `src/lodge/gitstore/index_words.py` (FTS5 candidates)
- Modify: `src/lodge/app/ports.py` (`Index` gains the methods below), `src/lodge/app/lodge.py` (`read_model: bool = True`; the viewer's `Lodge` passes False), `src/lodge/app/state.py`, `src/lodge/main.py` (the viewer's factory without the read model), `src/lodge/core/codec.py` (app's result classes registered by `app`, not imported by `core`)
- Test: `tests/app/test_read_model.py` (new), `tests/app/test_indexed_reads.py` (new), `tests/gitstore/test_index_states.py` (new), `tests/gitstore/test_index_words.py` (new), `tests/e2e/test_indexed_reads.py` (new)

**Interfaces:**
- Consumes: Task 6's `rank`, `Candidate`, `parse_query`; Task 5's `family`, `citers`; Task 9's `Index`, codec, and failure modes; Task 2's `ChangeFacts`.
- Produces:
  ```python
  @dataclass(frozen=True)
  class Row:                                   # the derived part of one record in one state
      key: FileKey                             # its parse
      status: str; decided_by: str | None; date: str | None; scope: str | None; area: str | None
      flags: tuple[str, ...]; quote: Quote | None
      links: tuple[tuple[str, str, str], ...]  # Level3.links
      changed_by: tuple[str, ...]              # for level 2 of an entry
      areas: frozenset[str]                    # for the area filter
  def level1_of(row: Row, record: Decision | SpecEntry) -> Level1     # equals core.level1 for that state
  @dataclass(frozen=True)
  class StoredState:
      key: str                                 # sha1 of current ident, published ident, settings digest
      expires: str | None                      # the earliest new decision's date after the build time, if any
      codes: Mapping[str, tuple[str, ...]]     # casefolded code -> IDs
      unrecorded: tuple[Problem, ...]
      answers: Mapping[str, bytes]             # "waiting", "threads", "thread:<id>": marshal of to_plain
  class Index(Protocol):                       # in addition to Task 9's
      def state(self, key: str) -> StoredState | None
      def rows(self, key: str, ids: Collection[str]) -> dict[str, Row]
      def all_rows(self, key: str) -> dict[str, Row]
      def keep_state(self, state: StoredState, rows: Mapping[str, Row], words: Mapping[FileKey, tuple[str, str]]) -> None
      def candidates(self, words: Collection[str], every: bool) -> set[FileKey] | None   # None without FTS5
  ```
- A read (`show`, `search`, `waiting`, `threads`, `thread`) with an index and the read model on: `identities()`; the key; a stored state not expired at `clock.now()` answers through lookups (one bucket per ID, the parse rows of the records printed); otherwise the state is built in memory through Task 9's path, its rows, answers, and words kept, and the read answers from memory.
- Building a state where the published state's rows are stored: `check_change` gets `ChangeFacts` with the published statuses from those rows and its `check_state` problems from its stored state, so `derive` and `check_state` run on the current snapshot only.
- Buckets: 1,024 per state, by the ID's last two characters, `marshal` of `{id: to_plain(row)}`; four states kept, the oldest dropped when a fifth is kept, with its buckets and answers (d-hf2fms); words rows of parses no state uses are dropped then too.
- Words (d-eby5pb): FTS5 table `(key, title, statement)` with `tokenize='ascii'`, the text being `" ".join(sorted(core.words(...)))`; `candidates(words, every=False)` matches any word, `every=True` all; with no FTS5 (`sqlite3.OperationalError` on creating the table) `candidates` returns None and the search builds the state in memory.
- Search through the index: candidates are the keys matching any query word or phrase word, the ID if it exists, the family from `codes`, and for a code the keys matching every word of the code; then rows of those keys in this state whose `key` matches (a record's older parse matching an old word is not a candidate); `cites` checks citers on the parse's text; `rank` orders, the same function as in memory.
  An empty query or a filter-only search reads `all_rows`.
- Expiry (d-f3r5aq): `expires` is the smallest date of a decision new against the published state that is later than the build's `now`; at or after it the state is rebuilt from the parse cache.
- An answer's `Read` is rebuilt at read time with the store's live `freshness()`; only the unrecorded problems are stored.
- The viewer, `spec`, `timeline`, `draft`, `check`, `id`, `add`, and the gate never read rows (d-m0g9tx).

- [ ] **Step 1: Write the failing tests:** `test_read_model.py`: `test_level1_of_row_equals_core_level1` (every record of four sample stores and of a made-up 500-record store with replaced, narrowed, retired, flagged, confirmed, doubted, and failing records); `test_level3_links_equal`; `test_answers_equal_the_in_memory_reads`.
  `test_indexed_reads.py` (a fake index in `tests/app/fakes.py`): `test_seen_state_reads_no_snapshot` (patched `assemble` never called on the second `show`); `test_outputs_equal_in_memory` (for 200 seeded commands over the 500-record store: `show` of IDs, codes, unknown refs, several refs; `search` of words, phrases, codes, empty queries, every filter; `waiting`; `threads`; `thread`: equal results); `test_candidates_never_miss` (the property: for 300 seeded queries the indexed search equals `search_counted` over the snapshot); `test_older_parse_of_a_record_is_not_a_candidate`; `test_expired_state_is_rebuilt` (a decision dated 10 minutes after the clock: it fails check 1 before, the clock moved 11 minutes, it does not); `test_settings_change_is_another_state`; `test_published_facts_from_rows_equal_full` (the `CheckResult` of a new state built with stored published facts equals one built without); `test_without_fts5_reads_in_memory` (`candidates` returns None).
  `test_index_states.py`: `test_four_states_kept`; `test_seen_read_writes_nothing` (the file's mtime and size unchanged after a warm read); `test_bucket_by_last_two_characters`.
  `test_index_words.py`: `test_ascii_tokenizer_returns_core_words` (words with digits, non-ASCII letters, and combining marks round-trip as the same set); `test_any_and_every`.
  `tests/e2e/test_indexed_reads.py`: `test_edit_on_disk_then_show_sees_it`; `test_commit_then_show_sees_it`; `test_branch_mode_after_fetch_sees_the_new_tip`; `test_viewer_factory_has_no_read_model`.
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; the replay at all three sizes: cold, warm, and `--changed`, with the phase times of one changed-record read at 160,000 files; if the warm read is above 0.3 s or the changed read above 3 s, the report gives the phase table and the task stops for the coordinator (d-232gxs).
- [ ] **Step 5:** commit, push.

### Task 11: Untracked files through folder signatures

**Files:**
- Create: `src/lodge/gitstore/folders.py`
- Modify: `src/lodge/gitstore/identity.py` (the walk replaced), `src/lodge/gitstore/index_db.py` (a `folders` table), `src/lodge/app/ports.py` only if the identity needs the index passed (prefer handing the store the index at construction in `main.py`)
- Test: `tests/gitstore/test_folders.py` (new)

**Interfaces:**
- Consumes: Task 8's identity, Task 9's index and failure modes.
- Produces: the files on disk that `base` lacks come from a table `folders(path, ino, mtime_ns, ctime_ns, names, base)`, `names` being `marshal` of the folder's entries with their kind; a folder whose `stat` matches its row, whose row's `ctime_ns` is at least 2 s before the time the row was listed, and whose `base` equals the current base tree keeps its recorded extra names; any other folder is listed again with `os.scandir`, its subfolders followed, and its row rewritten when the index is writable (d-8kq2nk).
  Without a writable index the names-only walk of Task 8 runs, so the output is the same.
- `stat` of every known folder, plus listing any folder that changed; never `git status`, never `git ls-files -o`.

- [ ] **Step 1: Write the failing tests** (`tmp_path`, each comparing the found files with Task 8's walk): `test_unchanged_folders_are_not_listed` (patched `os.scandir` not called on a second identity); `test_new_file_in_a_listed_folder`; `test_new_subfolder_with_a_file`; `test_deleted_untracked_file`; `test_rename_within_a_folder`; `test_change_in_the_same_second_as_the_listing` (the row written at a patched time within 2 s of the folder's ctime is not trusted); `test_mtime_set_back_still_detected` (`os.utime` to the old mtime after adding a file: ctime differs); `test_base_change_relists`; `test_read_only_index_falls_back_to_the_walk`.
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; the replay at 160,000 files, warm, recorded with the identity's share.
- [ ] **Step 5:** commit, push.

### Task 12: The recorded table and the final measurements

**Files:**
- Create: `docs/superpowers/plans/2026-10-31-lodge-at-scale/timings.md`
- Modify: `README.md` (one paragraph: the index, where it lives, that it is safe to delete, `LODGE_INDEX=off`)

**Interfaces:**
- Consumes: every task.
- Produces: `timings.md`, for `s900`, `s9000`, and `s90000` on native disk, per line of `scripts/bench_reads.txt`: the base build of Task 1, this branch cold, warm, and after one changed record, `check --gate` included, with the output comparison against the base build (identical, or the lines Tasks 5 to 7 changed on purpose, named); the index file's size per store; the machine's Python, SQLite, and disk kind; where a FUSE-mounted copy of `s90000` is at hand, the same `show {code}` warm on it for contrast, one line, without its path.
- [ ] **Step 1:** run the replay; write `timings.md`.
- [ ] **Step 2:** if the warm read at 160,000 files is above 0.3 s, `timings.md` says so with the phase table, and the ledger records that the server question (d-232gxs) goes to the coordinator.
- [ ] **Step 3:** gate, commit, push.
