# Task 7 report

Status: Task 5 fix round in progress, before Task 7.
The coordinator's d-32cvvz and s-7f10zc were read through `lodge show --reasoning`.
There is nothing waiting for an agent.
No record files were opened or written, and no product decision is needed from the builder.

## Task 5 fix round

The supplied review is copied verbatim to `task-5-review.md`.
This round takes M1 to M4 and corrects the account of M5 in the earlier report and ledger.
The grouping for `written_order` remains deferred until a round touches `order.py` or `render.py`, as the review requests.
Before-code timing is running on the synthetic `s9000` store, with an installed and compiled copy of the starting build.

### Changes and failing tests

`citers` now checks the lower-cased title and statement for the lower-cased code before tokenising.
The viewer's single-record `show` skips siblings and citers, while command-line `show_many` retains them.
`fields.py` owns the grammar pattern shared by code validation and query classification, without a new package edge.
The `code_tokens` docstring now states the exact dot-prefix rule.
A timeout becomes a bounded sample with no exit status or output, and replay continues in cold, seen, and changed modes, including warm-up timeouts.
Timeout comparisons are always false, and partial subprocess output is discarded.
Mixed successful and timed-out samples retain the successful best time and label the median as including a bound.

Existing tests edited: the context equality in `test_siblings_and_citers_capped_at_ten` now compares the viewer result with empty context, and `test_benchmark_timeout_restores_edit` expects a returned timeout sample instead of an exception while retaining cleanup checks.
All new behaviour tests were run before implementation with `uv run --frozen pytest <nodes> -q`.
The first run failed as follows (irrelevant trace detail omitted):

```text
FAILED tests/core/test_codes.py::test_citers_tokenise_only_records_containing_the_lower_cased_code
E       AssertionError: assert 3 == 2
FAILED tests/app/test_show_many.py::test_viewer_show_does_not_compute_unused_code_context
E               AssertionError: unused siblings
FAILED tests/app/test_show_many.py::test_siblings_and_citers_capped_at_ten
E         Differing attributes:
E         ['siblings', 'citers', 'left_out']
FAILED tests/test_bench_cleanup.py::test_benchmark_timeout_restores_edit
E           subprocess.TimeoutExpired: Command 'lodge' timed out after 0.01 seconds
FAILED tests/test_bench_cleanup.py::test_timeout_keeps_measured_rows_and_continues[cold]
FAILED tests/test_bench_cleanup.py::test_timeout_keeps_measured_rows_and_continues[seen]
FAILED tests/test_bench_cleanup.py::test_timeout_keeps_measured_rows_and_continues[changed]
E           subprocess.TimeoutExpired: Command '['lodge', 'show', 'slow']' timed out after 0.01 seconds
7 failed in 0.30s
```

A further test caught a mixed-sample reporting error before its fix:

```text
FAILED tests/test_bench_cleanup.py::test_timeout_keeps_successful_samples_in_the_same_row
E       AssertionError: assert '| 0.001 | includes >0.010 | 0, timeout | 2, n/a |' in ...
| `show A` | lodge | >0.010 | >0.010 | 0, timeout | 2, n/a | n/a |
1 failed in 0.42s
```

The affected core, app, benchmark, viewer, and structure tests passed together: 196 passed in 8.71 s, before the mixed-sample test was added.

### Timing

Command: `uv run --frozen python scripts/bench_reads.py /var/tmp/lodge-bench/s9000 --lodge /var/tmp/lodge-bench/venv-t5-fix/bin/lodge --against /var/tmp/lodge-bench/venv-t5-fix-before/bin/lodge --commands /var/tmp/lodge-bench/show-code.txt --runs 3 --mode seen`.
The commands file contains only `show {code}`.
Both builds were installed on native disk, using Python 3.13.5 and PyYAML 6.0.3, and bytecode compiled before measurement.
The before build is `b4cd90e`, immediately before this round, including Task 6.

| Build | Best of three (s) | Median (s) | Exit | Output characters | Identical |
|---|---:|---:|---:|---:|---|
| Before, standalone | 1.744 | 1.757 | 0 | 458 | n/a |
| After | 1.510 | 1.546 | 0 | 458 | true |
| Before, replay comparison | 1.734 | 1.750 | 0 | 458 | true |

The substring filter retains a scan of record titles and statements, and does not avoid tokenisation for codes such as `A` that appear throughout the store.
The deferred `written_order` grouping needs no new import; only the standard priority queue proposed for `derived_order` raises the `heapq` constraint.

### Fix-round gate

`UV_FROZEN=true sh scripts/check.sh` passed: formatting, Ruff, strict mypy (222 source files), Vulture, 1,606 tests passed and 1 skipped in 50.43 s, and `lodge check --gate` printed `ok`.
The first gate attempts found an import-order issue and four typing errors in test doubles, all corrected before the successful gate.
Status: Task 5 fix round complete, ready for its separate commit and push.
