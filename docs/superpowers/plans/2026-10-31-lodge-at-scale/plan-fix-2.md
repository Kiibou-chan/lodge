# Plan fix round 2

Rechecks: `plan-recheck-opus.md` (correctness and design: N1 to N4 Important, N5 to N9 Minor) and `plan-recheck-codex.md` (feasibility and performance: F1, F3, F5, and F6 partly fixed; R1 to R4 Important, R5 Minor).
Every finding was taken; none is parked.
The coordinator's ruling for this round is d-6hb3yd: the index's consistency findings are one class, answered by five invariants in the plan's Global Constraints and tested by fault injection.
The planner's calls are d-c0q20c (narrows d-ana6c0), d-aej8rs (narrows d-n9w4by and d-dxqxsn), d-9r24jc (narrows d-dqpf59), d-4n5tr6 (narrows d-her016), and d-gd00c6 (narrows d-me8vm3).

## The index's consistency (d-6hb3yd)

The Global Constraints now list five invariants: a parse unit is a parse row with its words row; a state is published in one transaction with everything it promises, its row last as the completeness marker; eviction drops only what the evicted state owns; every cached value carries the key of its inputs; a reader takes a state only whole, inside one read transaction, and otherwise reads in memory.
The sweep applied them wherever the plan writes to the index:

| Place | Change |
|---|---|
| Task 9, parse cache | `keep_parses` in one transaction; `test_keep_parses_interrupted_at_each_statement`, `test_concurrent_keep_parses` |
| Task 9, flag and conversion cache | keyed by the index file's stat, the configuration values, and the source bytes; `test_cached_flags_and_conversions_keyed` |
| Task 9, pruning | journals deleted with their files, a locked one skipped |
| Task 10a, `keep_state` | takes the missing parse units, citer rows, and facts, and writes the state's row last; `StoredState.promised` counts what it holds; `test_keep_state_interrupted_at_each_statement`, `test_reader_during_a_concurrent_keep_state` |
| Task 10a, eviction | drops buckets, answers, citer rows, facts no kept state names, and parse units no kept state references; `test_eviction_drops_only_what_the_state_owns` |
| Task 10b, words | written and dropped with their parse unit; `keep_words` removed; `test_index_words_faults.py` |
| Task 11, folder signatures | one transaction per identity; a missing or undecodable row lists the folder; `test_interrupted_folder_write_lists_again` |

## Correctness and design recheck

| Finding | Change in the plan | Decision |
|---|---|---|
| N1, the fuzz test's two-way clause cannot hold | Task 3's fuzz asserts one direction (C succeeds implies the same value from today's loader) plus `load_yaml` equal to today's loader on every header; the guard no longer admits surrogate escapes or a plain value ending in `:`; written headers must parse under C | d-q051s2 |
| N2, idents agree exactly when trees agree is false | Task 8b states the one-way property, and the property test asserts it; canonical cases stay separate tests | d-c0q20c |
| N3, evicted words never come back | Invariant 1: words belong to the parse unit; `test_revert_after_eviction_is_found`; reverts in the property test | d-6hb3yd, d-aej8rs |
| N4, no citer lookup in Task 10a | Task 10a stores every code's citers per state and `Index.citing` reads them; `test_show_code_reads_citers_without_texts` | d-aej8rs |
| N5, the `crlf` attribute | `check-attr` asks for `crlf`; a test case with `lodge/*.md crlf` and `core.eol=crlf` | d-9r24jc |
| N6, published facts evicted | Eviction keeps the facts of every kept state's current and published idents; Task 10c's test checks they survive | d-aej8rs |
| N7, `synchronous=NORMAL` in rollback-journal mode | `synchronous=FULL` | d-4n5tr6 |
| N8, words queries of function words only | Task 6's ranking steps 3 and 4 apply only when `words` is not empty; `test_function_words_only_finds_id_and_code_only`; `of the` among the property test's queries | none needed |
| N9, pruning leaves journals | Pruning deletes the journal and skips a locked one; `test_pruning_takes_the_journal_and_skips_a_locked_one` | d-4n5tr6 |

## Feasibility and performance recheck

| Finding | Change in the plan | Decision |
|---|---|---|
| F1, identity depends on representation | One-way contract; the build's identical-state shortcut compares listings, so edit-then-commit, attachment-only commits, and a revert to the published contents still skip the change check; tests for each | d-c0q20c |
| F3, an attributes file only in git's index | `.gitattributes` entries in git's index count as sources (from the flags call); `test_root_attributes_only_in_the_index` with a content-changing filter | d-9r24jc |
| F5, the viewer still recurses | Task 2 makes the viewer's `_branches` iterative, and the deep-chain test renders the viewer's record page | none needed |
| F6, broad searches still open | Broad searches are reported apart with their own stop at 1.0 s warm; the 0.3 s stop covers the point reads and searches with at most 5,000 candidates | d-gd00c6, d-hxmdkz |
| R1, states searchable before their words | Invariants 1 and 2: words are part of the parse units a state's transaction writes; fault-injection, concurrent, and locked-write tests | d-6hb3yd, d-aej8rs |
| R2, no bounded path for citers | As N4; Task 1 adds a record coded `A`, and `show A` is benchmarked | d-aej8rs |
| R3, `git var` with two variables exits 129 | One call per variable; a failure converts every path; the cache key and a warm-change test are in Task 8b | d-9r24jc |
| R4, a file replaced by a folder | An overlay path that `lstat` finds as a real folder, or cannot find, is deleted; the walk compares kinds; tests in both directions, empty folders and attachments included | none needed |
| R5, empty skeleton bodies fail strict mypy | Concrete skeleton functions raise `NotImplementedError`; protocols keep `...` | none needed |
