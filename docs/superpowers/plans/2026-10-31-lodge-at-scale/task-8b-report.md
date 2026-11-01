# Task 8b and the Tasks 6 and 7 fix round

## Status

Reading and test preparation are in progress.
The fix round precedes Task 8b and will be committed separately.
Authority read through lodge: the specification, d-t2dsd3, and Task 8b's identity, conversion, and cache decisions.
Nothing waits for an agent; d-gvz66f still awaits the author.

## Tasks 6 and 7 fix round

The per-query candidate rebuild is measured only, as requested; Task 10b replaces it.

### Built

Task 6 I1 and Task 7 M2 follow d-t2dsd3: exact phrase runs, every searchable word without the run, then some words, each scored separately with newest-first ties.
Task 6 M2 to M4 add interspersed search options, explanatory query and phrase help, a per-query limit description, and singular `1 match`.
Task 6 M5 and M6 centralise filter, date, and score rules for search and related records, and share one word-run tokeniser across words and phrases.
Task 6 M7 formats brief status through a parameter rather than editing rendered strings; M8 uses `dataclasses.replace` for the area-local snapshot.
Task 6 M9 expands the candidate property with specification entries in three areas, replaced decisions, absent family roots, mixed-case IDs, reversed phrases, and non-empty filters.
The area grouping deferred in the older ledger was already built in Task 6, as Task 8a's report established; this round preserves it.
Task 7 M1 and M3 to M5 clarify phrase near matches, the optional CODE.why convention, noting waiting work for the author, `lodge thread ID`, and the author's responsibility for a rewritten branch.
The reading guide is still 25 lines.
Task 7 M6 checks the two query headers and code-family ordering, and includes the reading guide in the wheel contents assertion.
Task 7 M7 makes `Lodge.show` include code context by default; the viewer and the call-budget test explicitly decline it with `context=False`.
The earlier Task 5 fix round remains documented in `task-7-report.md`; the ledger now points there.
The optional Task 5 versus Task 4 total-cost comparison was not requested, so it was not added.
No finding conflicts with the plan or a decision after applying d-t2dsd3 and the dispatch's measurement-only instruction for Task 6 M1.

### Test-first evidence

Skeleton checks for the new shared tokeniser passed before test edits: 39 structure tests and strict mypy on 227 files.
Command: `uv run --frozen pytest tests/core/test_ranking.py tests/e2e/test_search_many.py tests/e2e/test_guide_read.py tests/app/test_show_many.py -q`.
The first run's retained output, with repeated traces omitted:

```text
FAILED tests/core/test_ranking.py::test_phrase_is_a_run_of_whole_words - Asse...
FAILED tests/core/test_ranking.py::test_phrase_keeps_function_words - Asserti...
FAILED tests/core/test_ranking.py::test_rank_over_candidates_equals_rank_over_all
FAILED tests/core/test_ranking.py::test_phrase_and_words_share_tokens - NotIm...
FAILED tests/e2e/test_search_many.py::test_two_queries_with_headers - Asserti...
FAILED tests/e2e/test_search_many.py::test_quoted_words_are_all_words - Value...
FAILED tests/e2e/test_search_many.py::test_options_between_queries - Assertio...
FAILED tests/e2e/test_search_many.py::test_phrase_lists_exact_then_all_then_some
FAILED tests/e2e/test_search_many.py::test_search_help_explains_queries_and_phrases
FAILED tests/e2e/test_guide_read.py::test_guide_read_is_short_and_has_no_writing_rules
FAILED tests/app/test_show_many.py::test_siblings_and_citers_capped_at_ten - ...
FAILED tests/app/test_show_many.py::test_viewer_show_does_not_compute_unused_code_context
12 failed, 18 passed in 2.59s
E       AssertionError: assert ['d-cccccc'] == ['d-cccccc', 'd-aaaaaa', 'd-dddddd']
E       assert 0 == 4
E       NotImplementedError
E       TypeError: Lodge.show() got an unexpected keyword argument 'context'
```

The first three-group CLI fixture accidentally contained the exact phrase in its reversed-word title.
It was corrected before implementation from `Brief lines brief` to `Brief brief lines`, then rerun alone:

```text
FAILED tests/e2e/test_search_many.py::test_phrase_lists_exact_then_all_then_some
E       assert all(ident in result.out for ident in ids)
E       assert False
1 failed in 0.28s
```

Existing expectations edited: the phrase run test now includes reversed and separated words after the run; the function-word test includes a near match; the quoted-query CLI test retains its reversed-word record under `--phrase`; the batch header expects `1 match`; the show tests assert the explicit context contract.
The candidate property's final score-only assertion uses a current candidate after the fixture gained a replaced first record.
Guide and wheel assertions were strengthened; their unchanged working examples and existing packaged file already passed, while the new guide wording assertions failed before the prose edit.
No existing test in `tests/core/test_search.py` was changed.

### Validation

Affected suites: 47 passed in 2.59 s, then strict mypy passed.
`UV_FROZEN=true sh scripts/check.sh`: exit 0; Ruff format and lint, mypy, Vulture, 1,635 passed and 1 skipped in 52.73 s, and `lodge check --gate` printed `ok`.
`git diff --check` passed.

### Candidate rebuild measurement

Native-disk synthetic store `s9000`, installed fix build in `venv-task-6-7-fix`, CPython 3.13.5, PyYAML 6.0.3 with libyaml, compiled bytecode, three sequential processes per command after the gate finished.
Commands: `/var/tmp/lodge-bench/venv-task-6-7-fix/bin/lodge search berth --brief` and the same executable with `search berth tide crane cargo --brief`, each run in `/var/tmp/lodge-bench/s9000`.
Best of three: 1.767 s for one query and 2.505 s for four queries, a 0.738 s increase, about 0.246 s per additional query.
An in-process probe wraps `_candidates` to time materialising its iterator, over the same loaded snapshot with cyclic collection disabled, three four-query runs.
Every query rebuilds 15,895 candidates; best of three per query: berth 0.155 s, tide 0.151 s, crane 0.152 s, and cargo 0.151 s.
The raw observations are retained under `/var/tmp/lodge-bench/task-6-7-cost.txt` and `task-6-7-rebuild.txt`; the first probe's post-timing phase had a Tree-versus-files argument error, corrected for the separate successful phase run.
Task 6 M1 is measured and remains for Task 10b, as requested.
