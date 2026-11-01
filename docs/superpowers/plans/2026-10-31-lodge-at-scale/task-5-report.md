# Task 5 report

Status: Tasks 1 and 2 fix round in progress, then Task 5.
The coordinator supplied Task 5's product decision and spec edit as d-y94v0n, read through `lodge show --reasoning`.
No record files have been opened or written.

## Tasks 1 and 2 fix round

The supplied review is copied verbatim to `task-1-2-review.md`.
I1, M1, M2, M4, M5, and M6 are being addressed before Task 5.
M3 conflicts with the task's explicit rewrite list and the Global Constraints' fixed `CORE_MODULES` list: a standard priority queue for maintaining ready placements would require `heapq`, which that list excludes.
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
