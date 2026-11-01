# Task 11 build report

Status: Task 10b fix round complete; Task 11 NEEDS_CONTEXT before its skeleton.
The dispatch authorises every Task 10b review Minor except conflicts with the plan or a decision.
FOLD-1 is already recorded as d-eg5nra, and SECOND-1 and CONV-1 are read as d-n65rhr and d-egknpk.
No record operation is required or will be run.

## Task 10b fix round

I1 distinguishes query-level fallback from damaged cached data, and I2 filters historical parse candidates against current state rows.
M1 restores removed-source CRLF histories and compares parsed values in the property test.
M2 ranks empty searches from row metadata and fetches only displayed parses.
M3 treats a proven absent exact ID as absent.
M4's cap and M6's interim R11 rule and unused `every` argument are dictated by the plan, so they remain unchanged.
M5 runs the 300-query differential against SQLite, including non-ASCII and digit words.

## Task 11 context question

NEEDS_CONTEXT: does Task 11's requirement that a seen identity takes no base names and builds no mapping apply only to R11-B, while interim R11-A retains its full-file comparison and uses the folder cache for traversal?
Task 8c's production `candidates()` returns `None` under the dispatched interim R11-A rule.
`CheckoutIdentity.current()` therefore reads all disk files and compares their hashes with `Committed.listing(rev)` to construct the base-relative identity.
Folder rows contain names and kinds that differ from the base, rather than base file hashes, so they cannot provide that comparison on a new store object without the base mapping.
Changing the identity scheme, storing per-file hashes, switching the R11 rule, or dropping the full-file comparison would change behaviour the task does not name.
Task 11 is stopped before its skeleton pending clarification; the authorised Task 10b fix round is complete.

## Implementation and review coverage

QueryFallback leaves a valid stored state untouched when a query requires memory or FTS is unavailable; damaged stored data still raises Miss and can be healed by a complete keep.
Proven absent exact IDs and historical parses absent from current rows no longer invalidate the state.
Empty and filter-only queries rank metadata through core.rank, and only displayed records load their parses.
The real-file regression deletes a committed synthetic record, keeps the new state, and proves all six following searches equal the exact reader without calling memory search, keeping a state, or changing the epoch.
The query-fallback tests repeat six reads with a one-byte cap, count keeps, and verify an unchanged epoch, including unavailable FTS.
The differential now runs 300 queries each against MemoryIndex and IndexDB, with café, 港口, Straße, and numeric words in the vocabulary, and counts unnecessary keeps.
The CRLF property test keeps its source-removal histories, compares line-normalised text and parsed values, and retains one-way identity consistency over normalised texts.
Its existing test was run under both interim R11-A and the R11-B test switch.

Existing tests edited: test_search_prints_as_in_memory gains the real-index parameter, richer vocabulary, and zero-keeps assertion; the search_store fixture gains that vocabulary; the two damaged-row tests use the port's None sentinel for corruption rather than a proven empty result; test_random_edits_agree retains CRLF history and checks parsed equivalence.
The Task 10b Files list is amended for the extracted lookup helper, property regression, and two new regression files, as the dispatch's hand-off rule requires.
No Index port or schema changes are made.

M4 remains report-only: the production cap still cannot fit the larger stores' complete state with FTS, pending DISK-1 and Task 12.
M6's production R11-B alternative remains dormant pending STALE-1, and the every argument remains in the plan's candidate interface.
The six R11-A-only cases to revisit with an R11 ruling are test_removed_attributes_agree[ident], test_removed_attributes_agree[working-tree-encoding=UTF-16], test_removed_attributes_agree[filter=berth], test_removed_attributes_agree[text eol=crlf], test_every_file_read_without_a_conversion_source, and test_r11a_does_not_compute_git_candidates.
No R11 decision is inferred.

## Failing-test evidence

Output below is excerpted verbatim, omitting traceback paths and object addresses.
The first regression run, before the implementation, failed all six initial cases in 0.44 s; the complete final regression set was also run against the original indexed.py, with the cap forced low to exercise epoch clearing.

Command: `uv run --frozen pytest tests/app/test_indexed_search_review.py -q`.

```text
E           AssertionError: assert 3 == 0
E           AssertionError: assert 3 == 0
E           AssertionError: assert 3 == 0
E               AssertionError: must use stored rows
E           assert 100 <= 3
E               AssertionError: must use stored rows
E           AssertionError: assert 3 == 0
FAILED tests/app/test_indexed_search_review.py::test_query_fallback_does_not_keep_or_change_epoch[args0]
FAILED tests/app/test_indexed_search_review.py::test_query_fallback_does_not_keep_or_change_epoch[args1]
FAILED tests/app/test_indexed_search_review.py::test_query_fallback_does_not_keep_or_change_epoch[args2]
FAILED tests/app/test_indexed_search_review.py::test_deleted_record_does_not_send_search_to_memory
FAILED tests/app/test_indexed_search_review.py::test_empty_search_fetches_only_displayed_parses
FAILED tests/app/test_indexed_search_review.py::test_unknown_exact_id_uses_stored_absence
FAILED tests/app/test_indexed_search_review.py::test_unavailable_fts_does_not_keep_complete_state
7 failed in 0.48s
```

The strengthened existing 300-query differential also failed on the original implementation for both adapters.
Command: `uv run --frozen pytest tests/app/test_indexed_search.py -q -k search_prints`.

```text
E           AssertionError: assert 32 == 0
E           AssertionError: assert 32 == 0
FAILED tests/app/test_indexed_search.py::test_search_prints_as_in_memory[False]
FAILED tests/app/test_indexed_search.py::test_search_prints_as_in_memory[True]
2 failed, 13 deselected in 20.01s
```

The real deleted-file test was run against the original implementation before using the fix.
Command: `uv run --frozen pytest tests/e2e/test_search_deleted_file.py -q`.

```text
E               AssertionError: must use stored rows
FAILED tests/e2e/test_search_deleted_file.py::test_six_searches_after_deleted_record_use_stored_rows
1 failed in 0.56s
```

Restoring the CRLF history before changing its assertions failed under the R11-B test switch.
Command: `uv run --frozen python` invoking `pytest.main(['tests/gitstore/test_identity_property.py', '-q', '-x'])` within identity_rules.r11b().

```text
E           AssertionError: assert {'lodge/decis...6530749', ...} == {'lodge/decis...1fbc493', ...}
E             Differing items:
E             {'lodge/decisions/record-29.md': '1256ee5b89faf459873751d6677b61268f189966'} != {'lodge/decisions/record-29.md': '8342dc7293138208401bb2ec1672592098201473'}
FAILED tests/gitstore/test_identity_property.py::test_random_edits_agree - As...
1 failed in 10.34s
```

After the assertion fix, R11-B's property run passes in 13.84 s.
The targeted search, structure, and regression suite passes 61 tests in 23.09 s, and the real deleted-file regression passes in 0.57 s.
The R11-A property run passes with the targeted suite, 22 tests in 32.29 s.

## Gate and timings

`UV_FROZEN=1 sh scripts/check.sh` exits 0.
Ruff format checks 674 files, Ruff passes, strict mypy checks 288 source files, Vulture passes, and pytest reports 2,158 passed and six skipped in 196.13 s.
`lodge check --gate` prints `ok` and the existing `note: area storage: order changed`.
The environment variable keeps the script's uv invocations frozen.
The fix round is committed as `Task 10b fix round: avoid rebuilding complete search states` and pushed to `origin/read-speed-build`.
Task 11 has no implementation, replay, identity timing, or FUSE claim while its context question is unresolved.
