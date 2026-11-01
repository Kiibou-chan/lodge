# Task 5 report

Status: Task 5 built and validated; Tasks 1 and 2 fix round committed and pushed as `8f980c9`.
The coordinator supplied Task 5's product decision and spec edit as d-y94v0n, read through `lodge show --reasoning`.
No record files have been opened or written.

## Tasks 1 and 2 fix round

The supplied review is copied verbatim to `task-1-2-review.md`.
I1, M1, M2, M4, M5, and M6 were addressed before Task 5.
M3 has two parts: grouping entries once per render fixes `written_order`'s repeated scans without new imports, and is deferred to the next round touching `order.py` or `render.py` (Task 5 review M5).
The `derived_order` part remains a plan gap: a standard priority queue for maintaining ready placements would require `heapq`, which the Global Constraints' fixed `CORE_MODULES` list excludes.
The review itself identifies M3 as a plan gap and allows recording it as out of scope.
Whole-spec rendering and large independent areas therefore remain an open performance concern for the coordinator; no rule is loosened and no additional rewrite is attempted in this fix round.
M6 is closed: Task 2's 0.424 s state check and 0.950 s derivation meet the plan's separate phase estimates.

### Built and test-first evidence

`change_facts` is the only constructor used by `app/state.py`, `app/reads.py`, and the shape probe, and calls `sort_key`.
It accepts precomputed derivations and problems, so callers reuse work without spelling keys.
`State` carries the checked published snapshot and the original current-state result for reuse by the gate when the published tree is the same object.
The former core-suite app test moved unchanged to `tests/app/test_change_facts.py`, with its import-path manipulation removed.
The independent oracle copies pre-Task-2 `check_change` from `0aa7759`, with only its name and the now-required status arguments to `check_entries` adapted.
The existing core facts test now compares both current-state variants against that oracle.

Commands used `uv run --frozen pytest <node-or-file> -q`.
The facts interface skeleton passed the structure suite (39 passed) and strict mypy before new tests.
Initial failing output, with environment-specific pytest paths omitted:

```text
FAILED tests/core/test_linear_checks.py::test_check_change_with_facts_equals_old_oracle
src/lodge/core/check_change.py:41: NotImplementedError
FAILED tests/app/test_change_facts.py::test_gate_reuses_published_facts
E       AssertionError: assert 3 == 2
E        +  where 3 = <MagicMock name='derive'>.call_count
```

The gate-note test changes `sort_key` to catch hand-built tuples, then asserts success and the printed note.
Its corrected initial failing run, before the fix:

```text
FAILED tests/app/test_change_facts.py::test_gate_prints_already_published_note
E       AssertionError: assert 1 == 0
Captured stdout:
fetched 2026-10-29T08:00:00+00:00
check 7: s-aaaaaa: is not listed in the order of area storage
1 failed
```

The moved call-budget test already passed, as expected for a pure relocation.
An initial CLI test invocation had the wrong adapter signature and was corrected before the meaningful failure above.
The copied oracle also needed the now-required `check_entries` status arguments before its passing comparison.

Benchmark regression tests failed before implementation:

```text
FAILED tests/test_bench_cleanup.py::test_benchmark_timeout_restores_edit
E       TypeError: measure() got an unexpected keyword argument 'timeout'
FAILED tests/test_bench_cleanup.py::test_benchmark_rejects_dirty_store[cold]
E       Failed: dirty store timed
FAILED tests/test_bench_cleanup.py::test_benchmark_rejects_dirty_store[seen]
E       Failed: dirty store timed
FAILED tests/test_bench_cleanup.py::test_sigterm_raises_for_cleanup
E       AttributeError: module 'bench_reads' has no attribute 'terminate'
FAILED tests/test_bench_cleanup.py::test_replay_passes_timeout
E       TypeError: run() got an unexpected keyword argument 'timeout'
5 failed, 1 passed
```

The changed-mode dirty-store case already passed because that safeguard existed.
After implementation the targeted app, core, and benchmark suites passed: 79 passed.

Fix-round full gate: `UV_FROZEN=true sh scripts/check.sh` passed format, Ruff, strict mypy (212 files), Vulture, pytest (1,564 passed, 1 skipped in 52.03 s), and `lodge check --gate` (`ok`).
The corrected shape probe ran with `uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/shapes.py --sizes 2000 4000 8000 --runs 3`, with cyclic collection disabled and synthetic in-memory harbour snapshots.
Best-of-three timings:

| Shape | Size | Derive (s) | State checks (s) | Change checks (s) | Total (s) |
|---|---:|---:|---:|---:|---:|
| one entry, many decisions | 2000 | 0.0056 | 0.0032 | 0.0043 | 0.0132 |
| chain, no doubts | 2000 | 0.0019 | 0.0023 | 0.0025 | 0.0068 |
| new decisions, published state | 2000 | 0.0196 | 0.0129 | 0.0160 | 0.0493 |
| one entry, many decisions | 4000 | 0.0114 | 0.0066 | 0.0089 | 0.0269 |
| chain, no doubts | 4000 | 0.0039 | 0.0047 | 0.0050 | 0.0136 |
| new decisions, published state | 4000 | 0.0436 | 0.0287 | 0.0346 | 0.1076 |
| one entry, many decisions | 8000 | 0.0244 | 0.0149 | 0.0184 | 0.0591 |
| chain, no doubts | 8000 | 0.0086 | 0.0102 | 0.0108 | 0.0296 |
| new decisions, published state | 8000 | 0.0911 | 0.0593 | 0.0722 | 0.2255 |

The probe also passes an explicit Ruff import and upgrade check outside the normal gate's documentation exclusions.
No Task 5 implementation is included in the fix-round commit.

## Task 5

The interface skeleton added the five code helpers, the `Shown` fields, `ShownMany`, and `show_many` through both app front doors.
The shared one-record builder was skeletonised before tests so the unchanged single-ref contract is tested through the new path too.
Before any Task 5 test, the structure suite passed (39 passed) and strict mypy passed (213 files).
No prior tests have been edited for Task 5.
The new tests were run with `uv run --frozen pytest tests/core/test_codes.py tests/app/test_show_many.py -q`, then `uv run --frozen pytest tests/e2e/test_show_many.py -q`.
Failing output:

```text
FAILED tests/core/test_codes.py::test_family_takes_dotted_siblings_not_longer_numbers
FAILED tests/core/test_codes.py::test_family_orders_the_code_first - NotImple...
FAILED tests/core/test_codes.py::test_cites_whole_tokens_only - NotImplemente...
FAILED tests/core/test_codes.py::test_cites_equals_the_boundary_rule - NotImp...
FAILED tests/core/test_codes.py::test_citers_exclude_the_family_and_order_newest_first
FAILED tests/core/test_codes.py::test_is_code_token_uses_the_ascii_grammar - ...
FAILED tests/app/test_show_many.py::test_each_record_once_in_ref_order - NotI...
FAILED tests/app/test_show_many.py::test_failing_ref_in_place_and_others_shown
FAILED tests/app/test_show_many.py::test_one_read_for_many_refs - NotImplemen...
FAILED tests/app/test_show_many.py::test_siblings_and_citers_capped_at_ten - ...
FAILED tests/app/test_show_many.py::test_broken_files_reported_once_for_the_batch
11 failed in 0.22s
FAILED tests/e2e/test_show_many.py::test_show_three_refs_one_output - Asserti...
FAILED tests/e2e/test_show_many.py::test_unknown_ref_exits_2_after_the_others
FAILED tests/e2e/test_show_many.py::test_stdout_flushed_before_each_error - A...
FAILED tests/e2e/test_show_many.py::test_single_ref_output_unchanged - NotImp...
4 failed in 0.84s
```

Every core/app failure above raised `NotImplementedError` from a skeleton helper or `Lodge.show_many`.
The first three end-to-end failures exposed the old single-ref parser: exit 2 for extra arguments, with no record text.
The single-ref literal-output test raised `NotImplementedError` from the shared record-builder skeleton.
The caps test also checks the CLI's context headings, their position after provenance, twenty brief lines, and the exact omitted-count sentence.
An additional mixed-exit test was run before implementation and failed because the old parser rejected the extra refs before any output; it checks that a later exit-1 conflict cannot lower an earlier exit-2 failure.

### Implementation and targeted validation

`core/codes.py` implements the ASCII grammar, dotted code families, whole-token citation sets, and citers ordered by their level-1 date and ID, including undated entries last.
Case comparisons use `str.lower()` throughout.
The app reads once for a batch, retains errors at their ref positions, and reuses the first `Shown` result for aliases and repeats with `repeat=True`.
Both single and batched show use the same record builder, with ten siblings and ten citers at most and separate omitted counts.
The CLI prints freshness and unreadable-file problems once for a batch, marks repeated records, flushes stdout before reporting each failed ref on stderr, and keeps the highest failure exit code.
The context follows all requested levels and uses existing brief-line formatting.
Single-ref output, including the existing empty stdout for a failed single ref, remains compatible; the new separators apply to the multi-ref command.
The parser change touches four existing lines, within Task 5's six-line allowance.
Both requested benchmark lines were added to `scripts/bench_reads.txt`.

The targeted suite covering the structure checks, all new tests, existing app reads, and existing single-ref/ambiguous-code CLI behaviour passed: 93 passed.
The narrower new-test and identical-state suite then passed: 45 passed.
Ruff, strict mypy (216 files), and Vulture pass after implementation.
No existing Task 5 test was edited, and no file outside Task 5's file list was changed after the separate fix-round commit, apart from this report.

Representative exception lines from the saved Task 5 failures:

```text
src/lodge/core/codes.py:12: NotImplementedError
src/lodge/core/codes.py:20: NotImplementedError
src/lodge/core/codes.py:24: NotImplementedError
src/lodge/core/codes.py:8: NotImplementedError
src/lodge/app/lodge.py:37: NotImplementedError
E       ValueError: substring not found
E       AssertionError: assert (2 == 2 and 's-qbgbz8' in '')
src/lodge/app/reads.py:45: NotImplementedError
FAILED tests/app/test_show_many.py::test_batch_exit_uses_highest_failure - As...
E       AssertionError: assert False
1 failed in 0.22s
```

Full scratch outputs are retained under `/var/tmp/lodge-bench/` as `task5-core-app-red.txt`, `task5-e2e-red.txt`, and `task5-exit-red.txt`.

### Benchmarks

Native-disk worktree and virtual environment, Python 3.13.5, PyYAML with libyaml available.
Bytecode was compiled with `uv run --frozen python -m compileall -q src .venv/lib` before the replay.
Stores are the existing synthetic `bench_store.py` stores under `/var/tmp/lodge-bench/`, with 1,607, 16,120, and 160,800 record files respectively.
Each sample starts a fresh process, with an untimed warm-up per command and three timed runs; the runner reports the best and median.
The commands file `/var/tmp/lodge-bench/task5-commands.txt` contains exactly:

```text
show {code} {code2} {entry}
show A
```

For each of `s900`, `s9000`, and `s90000`, the command was:

```sh
uv run --frozen python scripts/bench_reads.py /var/tmp/lodge-bench/STORE --lodge /var/tmp/lodge-build/.venv/bin/lodge --commands /var/tmp/lodge-bench/task5-commands.txt --mode seen --runs 3 --timeout 180
```

Mode: `seen`; store: `s900`; runs: 3.

| Command | Build | Best (s) | Median (s) | Exit | Characters | Identical |
|---|---|---:|---:|---|---|---|
| `show {code} {code2} {entry}` | lodge | 0.383 | 0.387 | 0 | 998 | n/a |
| `show A` | lodge | 0.366 | 0.367 | 0 | 789 | n/a |

Mode: `seen`; store: `s9000`; runs: 3.

| Command | Build | Best (s) | Median (s) | Exit | Characters | Identical |
|---|---|---:|---:|---|---|---|
| `show {code} {code2} {entry}` | lodge | 2.017 | 2.029 | 0 | 1004 | n/a |
| `show A` | lodge | 1.784 | 1.801 | 0 | 1183 | n/a |

Mode: `seen`; store: `s90000`; runs: 3.

| Command | Build | Best (s) | Median (s) | Exit | Characters | Identical |
|---|---|---:|---:|---|---|---|
| `show {code} {code2} {entry}` | lodge | 19.771 | 19.908 | 0 | 839 | n/a |
| `show A` | lodge | 16.997 | 17.130 | 0 | 1194 | n/a |

All samples exited 0, with stable output sizes for each command and store.
`Identical` is not applicable because this replay measures the new product behaviour without an old-build comparison.
The added citation scans run in memory at this stage; the later index tasks own the warm-read target.
No new timing assertion was added to pytest.

### Concerns

The review's M3 whole-spec/large-area performance gap remains reported to the coordinator, as described above.
Task 5 has no unresolved context question or further implementation concern.
The final full gate, `UV_FROZEN=true sh scripts/check.sh`, passed before commit.
Results: 591 files already formatted, Ruff clean, strict mypy clean (216 files), Vulture clean, 1,580 tests passed and 1 skipped in 51.19 s, and `lodge check --gate` returned `ok`.
The working diff passes `git diff --check`.
Task 5 is delivered in its own commit after the fix round, with the required Codex co-author trailer and branch push.
