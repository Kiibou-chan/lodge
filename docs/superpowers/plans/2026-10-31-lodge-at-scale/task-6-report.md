# Task 6 build report

Status: built and validated, with the coordinator's product decision d-e8pdqe read through lodge.
No repository record files were opened or changed, and no `lodge add` was run.

## Scope and skeleton

Task 6 adds query parsing, candidate ranking, several searches in one checked read, explicit phrases, and leaner default brief output.
The coordinator's M3 ruling also groups entries once per specification view, retaining the current derived traversal within each area.
The new `Filters`, `Query`, `Candidate`, `rank`, and `search_many` interfaces were installed as skeletons before new tests.
`uv run --frozen pytest tests/test_structure.py -q`: 39 passed.
`uv run --frozen mypy`: success, no issues in 218 source files.
The additional order keyword signatures were checked again before their implementation, with no issues in 222 source files.

## Test-first evidence

Commands: `uv run --frozen pytest tests/core/test_ranking.py tests/app/test_search_many.py tests/e2e/test_search_many.py -q`, followed by the two strengthened end-to-end cases, then `uv run --frozen pytest tests/core/test_render_grouping.py -q`.
The first run had 17 failures and two passes; the two passes covered existing behaviour, so they were strengthened to assert the new phrase and multi-query paths, then both failed before implementation.
The grouping test also failed before implementation.

```text
tests/e2e/test_search_many.py:48: AssertionError
=========================== short test summary info ============================
FAILED tests/core/test_ranking.py::test_exact_id_first - NotImplementedError
FAILED tests/core/test_ranking.py::test_code_family_then_citers_then_words - ...
FAILED tests/core/test_ranking.py::test_code_without_family_ranks_as_words - ...
FAILED tests/core/test_ranking.py::test_phrase_is_a_run_of_whole_words - NotI...
FAILED tests/core/test_ranking.py::test_phrase_keeps_function_words - NotImpl...
FAILED tests/core/test_ranking.py::test_needs_memory_cases - NotImplementedError
FAILED tests/core/test_ranking.py::test_function_words_only_finds_id_and_code_only
FAILED tests/core/test_ranking.py::test_all_words_before_some_words - NotImpl...
FAILED tests/core/test_ranking.py::test_ties_newest_first - NotImplementedError
FAILED tests/core/test_ranking.py::test_filters_apply_to_family_and_citers - ...
FAILED tests/core/test_ranking.py::test_rank_over_candidates_equals_rank_over_all
FAILED tests/app/test_search_many.py::test_each_record_once_across_queries - ...
FAILED tests/app/test_search_many.py::test_limit_per_query_excludes_earlier_records
FAILED tests/app/test_search_many.py::test_one_read_for_many_queries - NotImp...
FAILED tests/e2e/test_search_many.py::test_two_queries_with_headers - Asserti...
FAILED tests/e2e/test_search_many.py::test_phrase_option_is_one_query - Asser...
FAILED tests/e2e/test_search_many.py::test_brief_omits_current_and_says_so - ...
17 failed, 2 passed in 1.19s

=========================== short test summary info ============================
FAILED tests/e2e/test_search_many.py::test_quoted_words_are_all_words - Asser...
FAILED tests/e2e/test_search_many.py::test_brief_with_status_any_prints_status
2 failed in 0.43s

>       assert counted.scans <= 1
E       AssertionError: assert 40 <= 1
E        +  where 40 = {'s-000000': SpecEntry(id='s-000000', area='area-0', title='An entry', statement='What holds now.', code=None, importe...'s-000019', area='area-19', title='An entry', statement='What holds now.', code=None, imported_from=None, rests_on=())}.scans

tests/core/test_render_grouping.py:27: AssertionError
=========================== short test summary info ============================
FAILED tests/core/test_render_grouping.py::test_whole_spec_groups_entries_once
1 failed in 0.13s
```

Representative original failures were `NotImplementedError` in `parse_query`, exit 2 with `unrecognized arguments: --phrase`, exit 2 with `unrecognized arguments: ITEM-1`, and the brief output lacking `records are current unless marked`.
The full raw logs are retained under `/var/tmp/lodge-bench/task6-red.txt`, `task6-extra-red.txt`, and `task6-grouping-red.txt`.

## Implementation and expectation edits

The new leaf modules hold filters and ranking over candidates, with an exact ID first, code families and citers next, phrase or all-word matches, then partial-word matches.
The existing `search_counted` string input remains supported alongside `Query`, for existing callers.
`search_many` uses one checked state, records earlier printed IDs in `above`, and applies each limit after removing them.
The CLI prints query totals, earlier matches, and one default-status brief notice after read lines.
Whole-spec views group current entries once and give the unchanged ordering functions a snapshot containing just that area's entries.
The temporary order keywords were removed after the gate caught an incompatibility with Task 2's differential traversal oracle.
Its tests and oracle remain unchanged, and no new import is needed.

Existing test edits: `tests/e2e/test_search_brief.py::test_search_brief_gives_one_line_per_record` consumes the notice and omits the current status; `test_search_brief_still_says_what_it_left_out` counts the notice; `test_search_brief_without_hits` includes it.
`tests/core/test_search.py` required no expectation changes.
Two new fixture expectations were corrected during implementation: a phrase's reversed all-word match belongs to neither the exact-phrase group nor the partial-word group, and a function-word code fixture must avoid unintentionally citing that code in its title.

## Validation and timings

`sh scripts/check.sh`: green, with Ruff formatting, Ruff lint, strict mypy, Vulture, 1,600 tests passed, one skipped, and `lodge check --gate` reporting `ok`.
The log is retained at `/var/tmp/lodge-bench/task6-check-final.txt`.
The earlier gate's dead `listed_text` function was removed after the CLI switched to batch output.

Both builds use Python 3.13.5 and PyYAML 6.0.3 in separately installed, bytecode-compiled virtual environments on native disk.
The Task 5 comparison build contains the code at this task's starting commit, with the coordinator's decision already recorded.
Benchmarks run on the synthetic s900, s9000, and s90000 stores under `/var/tmp/lodge-bench`.
The baseline `spec` command at s90000 took 47.609 s best of three (47.609, 48.060, and 49.317 s).
The lower-size baseline runs capture bytes only; they are not timing comparisons.
The rendered specification is byte-identical at s900 (156,730 bytes), s9000 (1,584,257 bytes), and s90000 (15,759,821 bytes).
The captures compare the complete standard output from `lodge spec` byte for byte, with exit 0 in both builds.
The s90000 after-change samples are 17.113, 18.070, and 17.867 s, so best of three is 17.113 s against 47.609 s before.
The command is `/var/tmp/lodge-bench/venv-task5/bin/lodge spec` before and `/var/tmp/lodge-bench/venv-task6/bin/lodge spec` after, each run with s90000 as its working directory.

Search replay command, substituting each store name:

```sh
uv run --frozen python scripts/bench_reads.py /var/tmp/lodge-bench/s900 \
  --lodge /var/tmp/lodge-bench/venv-task6/bin/lodge \
  --against /var/tmp/lodge-bench/venv-task5/bin/lodge \
  --commands /var/tmp/lodge-bench/task6-commands.txt --mode seen --runs 3
```

The commands file selects the six search lines in `scripts/bench_reads.txt`.
The raw replay tables are retained as `/var/tmp/lodge-bench/task6-s900.md`, `task6-s9000.md`, and `task6-s90000.md`.
The new commands intentionally exit 2 with empty standard output in Task 5, because it accepts neither several queries nor `--phrase`.
The brief-output differences implement d-e8pdqe; the full single-word search is byte-identical with the same exit status at all three sizes.
The search replay completed successfully at all three sizes.
All reported timing comparisons use best of three, without timing assertions in pytest.

## Search replay results

`lodge` is Task 6; `against` is Task 5.

### s900

Mode: `seen`; store: `s900`; runs: 3.

| Command | Build | Best (s) | Median (s) | Exit | Characters | Identical |
|---|---|---:|---:|---|---|---|
| `search berth --brief` | lodge | 0.357 | 0.359 | 0 | 1927 | false |
| `search berth --brief` | against | 0.341 | 0.347 | 0 | 2093 | false |
| `search "berth crane" --brief` | lodge | 0.353 | 0.368 | 0 | 1937 | false |
| `search "berth crane" --brief` | against | 0.342 | 0.349 | 0 | 2103 | false |
| `search {code} --brief` | lodge | 0.369 | 0.395 | 0 | 679 | false |
| `search {code} --brief` | against | 0.338 | 0.347 | 0 | 627 | false |
| `search berth` | lodge | 0.349 | 0.359 | 0 | 5006 | true |
| `search berth` | against | 0.350 | 0.350 | 0 | 5006 | true |
| `search berth tide --brief` | lodge | 0.379 | 0.381 | 0 | 3964 | false |
| `search berth tide --brief` | against | 0.162 | 0.163 | 2 | 0 | false |
| `search --phrase "berth crane" --brief` | lodge | 0.358 | 0.370 | 0 | 1987 | false |
| `search --phrase "berth crane" --brief` | against | 0.163 | 0.164 | 2 | 0 | false |

### s9000

Mode: `seen`; store: `s9000`; runs: 3.

| Command | Build | Best (s) | Median (s) | Exit | Characters | Identical |
|---|---|---:|---:|---|---|---|
| `search berth --brief` | lodge | 1.764 | 1.781 | 0 | 1946 | false |
| `search berth --brief` | against | 1.661 | 1.670 | 0 | 2112 | false |
| `search "berth crane" --brief` | lodge | 1.766 | 1.772 | 0 | 2009 | false |
| `search "berth crane" --brief` | against | 1.665 | 1.692 | 0 | 2175 | false |
| `search {code} --brief` | lodge | 1.956 | 2.016 | 0 | 1653 | false |
| `search {code} --brief` | against | 1.666 | 1.678 | 0 | 1804 | false |
| `search berth` | lodge | 1.756 | 1.764 | 0 | 5038 | true |
| `search berth` | against | 1.673 | 1.698 | 0 | 5038 | true |
| `search berth tide --brief` | lodge | 2.007 | 2.027 | 0 | 3991 | false |
| `search berth tide --brief` | against | 0.157 | 0.159 | 2 | 0 | false |
| `search --phrase "berth crane" --brief` | lodge | 1.871 | 1.876 | 0 | 1952 | false |
| `search --phrase "berth crane" --brief` | against | 0.156 | 0.157 | 2 | 0 | false |

### s90000

Mode: `seen`; store: `s90000`; runs: 3.

| Command | Build | Best (s) | Median (s) | Exit | Characters | Identical |
|---|---|---:|---:|---|---|---|
| `search berth --brief` | lodge | 17.413 | 17.566 | 0 | 1963 | false |
| `search berth --brief` | against | 16.408 | 16.533 | 0 | 2129 | false |
| `search "berth crane" --brief` | lodge | 17.528 | 18.063 | 0 | 1917 | false |
| `search "berth crane" --brief` | against | 16.462 | 16.499 | 0 | 2083 | false |
| `search {code} --brief` | lodge | 19.398 | 19.452 | 0 | 1659 | false |
| `search {code} --brief` | against | 16.434 | 16.456 | 0 | 1809 | false |
| `search berth` | lodge | 17.370 | 17.378 | 0 | 4769 | true |
| `search berth` | against | 16.493 | 16.582 | 0 | 4769 | true |
| `search berth tide --brief` | lodge | 20.211 | 20.233 | 0 | 4021 | false |
| `search berth tide --brief` | against | 0.158 | 0.162 | 2 | 0 | false |
| `search --phrase "berth crane" --brief` | lodge | 18.477 | 18.477 | 0 | 1946 | false |
| `search --phrase "berth crane" --brief` | against | 0.161 | 0.162 | 2 | 0 | false |

## Concerns

Timings are provisional before the index tasks, with the target stop applying after Task 11.
At s90000 the new code search takes 19.398 s against 16.434 s in Task 5, and brief word search takes 17.413 s against 16.408 s.
The two-query search takes 20.211 s from one checked read.

Known limit from the coordinator: `derived_order` within one very large area retains its existing traversal cost.
No `heapq` import or change to `CORE_MODULES` was made.
