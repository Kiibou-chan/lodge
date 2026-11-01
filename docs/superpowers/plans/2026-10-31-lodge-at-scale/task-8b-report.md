# Task 8b and the Tasks 6 and 7 fix round

## Status

The Tasks 6 and 7 fix round is committed and pushed as `9747155`.
Task 8b is built and validated, with the final gate green and native-disk timings recorded.
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
The Task 5 versus Task 4 total-cost comparison requested conditionally in Task 7 M7 is recorded below.
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


### Task 5 versus Task 4 show cost

Task 7 M7's reference row uses source archives of Task 4 `0a29988` and Task 5 `ea92261`, installed separately under `/var/tmp/lodge-bench/venv-task-8b-task4` and `venv-task-8b-task5`.
Both use CPython 3.13.5, PyYAML 6.0.3 with libyaml, and compiled bytecode, on the same native-disk `s9000` store.
The selected root code and its `.why` sibling were found through lodge's CLI.
Command for each installed executable: `show CODE-10`, with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_ATTR_NOSYSTEM=1`, three sequential subprocesses after the final gate completed.
The benchmark script and samples are retained as `task-8b-task5-cost.py` and `task-8b-task5-cost.jsonl` under `/var/tmp/lodge-bench`.

| Build | Best of three (s) | Output bytes |
|---|---:|---:|
| Task 4, 0a29988 | 1.354353 | 241 |
| Task 5, ea92261 | 1.562437 | 458 |

The observed increase is 0.208084 s; Task 5 adds the family and citation context to the output.
This end-to-end comparison includes the fix rounds between those commits.
The earlier Task 5 fix-round measurement in `task-7-report.md` records the later citation-prefilter improvement separately.

## Task 8b

### Skeleton and test-first evidence

The Store protocol gains `identities`, `listings`, and `texts`.
New modules separate checkout overlays, selected texts and branch resolution, conversion sources, and index flags.
The two adapters bind these three methods to their listing delegate in their constructors, keeping each adapter within its ten-line allowance.
The existing concurrency-test `Interleaved` wrapper also needs three forwarding assignments for strict structural typing; its test behaviour is unchanged.
The initial skeleton mypy run exposed that wrapper, and the corrected skeleton passed 39 structure tests in 0.35 s and strict mypy on 231 source files before the new tests were written.
The shared isolated-git fixture now sets HOME and XDG_CONFIG_HOME inside the test folder for both gitstore and e2e tests, and disables real system attributes.
Tests modelling system attributes use a synthetic path through the patched git runner.

All required test functions were written and run against the skeleton, including 200 seeded sequences over 40 records, source and flag races, attachments, folder replacements, branch tips, and rewrites.
Command: `uv run --frozen pytest tests/gitstore/test_identity.py tests/gitstore/test_flags.py tests/gitstore/test_attributes.py tests/gitstore/test_identity_property.py tests/gitstore/test_listing_modes.py -q`.
The failing output, with repeated traces omitted:

```text
E       NotImplementedError
src/lodge/gitstore/listing.py:23: NotImplementedError
src/lodge/gitstore/listing.py:50: NotImplementedError
src/lodge/gitstore/flags.py:23: NotImplementedError
FAILED tests/gitstore/test_identity.py::test_clean_checkout_ident_is_the_head_tree
FAILED tests/gitstore/test_identity.py::test_touched_file_keeps_the_clean_ident
FAILED tests/gitstore/test_identity.py::test_staged_edit_reverted_on_disk_keeps_the_clean_ident
FAILED tests/gitstore/test_identity.py::test_unstaged_edit_agrees - NotImplem...
FAILED tests/gitstore/test_identity.py::test_untracked_file_agrees - NotImple...
FAILED tests/gitstore/test_identity.py::test_ignored_file_agrees - NotImpleme...
FAILED tests/gitstore/test_identity.py::test_deleted_file_agrees - NotImpleme...
FAILED tests/gitstore/test_identity.py::test_staged_deletion_left_on_disk_agrees
FAILED tests/gitstore/test_identity.py::test_rename_agrees - NotImplementedError
FAILED tests/gitstore/test_identity.py::test_symbolic_link_agrees - NotImplem...
FAILED tests/gitstore/test_identity.py::test_fifo_agrees - NotImplementedError
FAILED tests/gitstore/test_identity.py::test_attachment_bytes_changed_keeps_the_ident
FAILED tests/gitstore/test_identity.py::test_unborn_head - NotImplementedError
FAILED tests/gitstore/test_identity.py::test_head_without_lodge - NotImplemen...
FAILED tests/gitstore/test_identity.py::test_commit_after_edit_agrees - NotIm...
FAILED tests/gitstore/test_identity.py::test_attachment_only_commit_agrees - ...
FAILED tests/gitstore/test_identity.py::test_reverted_to_published_with_head_ahead_agrees
FAILED tests/gitstore/test_identity.py::test_file_replaced_by_folder_agrees[empty-lodge/decisions/old.md]
FAILED tests/gitstore/test_identity.py::test_file_replaced_by_folder_agrees[empty-lodge/attachments/d-aaaaaa/log.txt]
FAILED tests/gitstore/test_identity.py::test_file_replaced_by_folder_agrees[populated-lodge/decisions/old.md]
FAILED tests/gitstore/test_identity.py::test_file_replaced_by_folder_agrees[populated-lodge/attachments/d-aaaaaa/log.txt]
FAILED tests/gitstore/test_identity.py::test_folder_replaced_by_file_agrees[lodge/decisions]
FAILED tests/gitstore/test_identity.py::test_folder_replaced_by_file_agrees[lodge/attachments/d-aaaaaa]
FAILED tests/gitstore/test_flags.py::test_assume_unchanged_edit_agrees - NotI...
FAILED tests/gitstore/test_flags.py::test_skip_worktree_missing_file_agrees
FAILED tests/gitstore/test_flags.py::test_ignore_stat_entries_agree - NotImpl...
FAILED tests/gitstore/test_flags.py::test_cached_flags_and_conversions_keyed
FAILED tests/gitstore/test_attributes.py::test_no_sources_no_check_attr_call[False]
FAILED tests/gitstore/test_attributes.py::test_no_sources_no_check_attr_call[True]
FAILED tests/gitstore/test_attributes.py::test_autocrlf_spellings[true] - Not...
FAILED tests/gitstore/test_attributes.py::test_autocrlf_spellings[yes] - NotI...
FAILED tests/gitstore/test_attributes.py::test_autocrlf_spellings[on] - NotIm...
FAILED tests/gitstore/test_attributes.py::test_autocrlf_spellings[1] - NotImp...
FAILED tests/gitstore/test_attributes.py::test_autocrlf_spellings[input] - No...
FAILED tests/gitstore/test_attributes.py::test_autocrlf_spellings[false] - No...
FAILED tests/gitstore/test_attributes.py::test_autocrlf_spellings[no] - NotIm...
FAILED tests/gitstore/test_attributes.py::test_autocrlf_spellings[off] - NotI...
FAILED tests/gitstore/test_attributes.py::test_autocrlf_spellings[0] - NotImp...
FAILED tests/gitstore/test_attributes.py::test_autocrlf_spellings[] - NotImpl...
FAILED tests/gitstore/test_attributes.py::test_global_attributes_file_reads_from_disk
FAILED tests/gitstore/test_attributes.py::test_info_attributes_and_attributes_file[info]
FAILED tests/gitstore/test_attributes.py::test_info_attributes_and_attributes_file[configured]
FAILED tests/gitstore/test_attributes.py::test_info_attributes_and_attributes_file[system]
FAILED tests/gitstore/test_attributes.py::test_text_attribute_on_one_pattern[text-eol]
FAILED tests/gitstore/test_attributes.py::test_text_attribute_on_one_pattern[legacy-crlf]
FAILED tests/gitstore/test_attributes.py::test_root_attributes_only_in_the_index
FAILED tests/gitstore/test_attributes.py::test_git_var_failure_converts_every_path
FAILED tests/gitstore/test_attributes.py::test_warm_change_of_a_source_agrees
FAILED tests/gitstore/test_identity_property.py::test_random_edits_agree - No...
FAILED tests/gitstore/test_listing_modes.py::test_branch_mode_ident_is_the_tip_tree
FAILED tests/gitstore/test_listing_modes.py::test_rewritten_branch_publishes_the_accepted_tree
51 failed in 4.40s
```

Strict mypy also passes with the new tests, on 236 source files.


### Implementation and verification in progress

The checkout identity resolves HEAD and the published merge base, lists committed blob IDs, and applies only disk-hashed overlay paths.
The overlay combines staged and unstaged differences with git stat shortcuts disabled, flagged index entries, converting paths, and a names-only scan that includes ignored and untracked files.
Real folders are traversed; symbolic links and non-regular files have the exact disk-tree representation, and any lstat error, including ENOTDIR, is a deletion.
Attachments are presence-only and are never opened or hashed.
Matching base blobs and unchanged attachment presence leave the clean tree identity intact.
Listings retain those resolved revisions, and selected texts use one cat-file batch plus retained overlay bytes.
The branch delegate mirrors the existing fetch, locking, acceptance, and rewrite handling, without making listings or texts resolve a new tip.
Both adapter constructors bind the three listing methods directly to the delegate, with no git calls until one is used.
Checkout adds seven lines and removes one; branch adds five lines, both within the ten-line allowance.

The flag cache is keyed on the index inode, size, mtime_ns, and ctime_ns before and after ls-files.
Conversion keys include configuration values, separately queried global and system paths, indexed attributes-source membership, all source bytes and stat signatures, the requested paths, and the index stat, before and after check-attr.
Including source stat signatures detects a changed-and-restored source even when its bytes match again.
The no-source path skips check-attr; unsupported git var conservatively converts every path; all git boolean spellings and the legacy crlf attribute are covered.
Caches stay in the store object, with no index or other persistent writes.

The first focused implementation run exposed fixture mistakes: mock argument indexing, the non-recursive `lodge/*.md` attributes pattern, and an attempted system-attributes environment override.
The corrected legacy case uses a top-level record, and the system-source seam runs real check-attr against a synthetic configured file.
The property fixture now checks current index membership and HEAD existence before reverting, and clears assume-unchanged and skip-worktree separately because a combined update-index invocation left a skip-worktree entry set.
After correction, all 200 sequences pass: 1 property test in 19.77 s.
The 50 focused cases pass in 8.50 s.

Two additional regression tests were seen failing before their fixes:

```text
FAILED tests/gitstore/test_listing_modes.py::test_missing_published_message_matches_exact
E       AssertionError: assert None == 'the published state cannot be found: origin/main and main were tried, and neither exists here or shares history with HEAD; set base in .lodge.toml to your trunk branch, or fetch it'
1 failed in 0.42s
FAILED tests/gitstore/test_flags.py::test_index_attributes_appearing_between_cache_keys
E       AssertionError: assert frozenset() == {'lodge/decisions/old.md'}
1 failed in 0.35s
```

The first keeps freshness correct when exact and fast reads share a store object; exact trees and fast identities now both set the same warning field.
The second prevents caching a no-source answer when an index-only attributes file appears between collecting flags and taking the conversion key.
The current source membership is part of that key, so the next flags read invalidates the raced answer.
The initial freshness-test draft had a missing clock import; the retained failure above is its corrected behavioural regression before implementation.


A third additional regression covers the updated MemoryStore adapter's attachment presence:

```text
FAILED tests/gitstore/test_listing_modes.py::test_memory_listing_keeps_attachment_presence
E       AssertionError: assert frozenset() == {'lodge/attachments/d-aaaaaa/log.txt'}
1 failed in 0.61s
```

MemoryStore now puts attachment paths in Tree.attachments as well as omitting their bytes from blob keys, so its fast identity tracks presence and ignores attachment edits.
The existing fake's files mapping remains available to the app tests.
Broader validation before this final helper correction: 526 adapter, e2e, and app tests passed in 64.19 s; the subsequent focused cache, attributes, and mode run passed 29 tests in 5.15 s.


The final root-kind review added one more regression, also seen failing first:

```text
FAILED tests/gitstore/test_identity.py::test_head_with_a_file_instead_of_lodge_folder
E       lodge.app.errors.LodgeError: fatal: not a tree object
1 failed in 0.62s
```

When HEAD has a file named lodge but the working tree has a real lodge folder, there is no committed lodge/ tree.
Committed listings now run ls-tree on the resolved commit, as exact read_tree does, and use the empty-tree base for that root-kind mismatch.
The final gate and timing tables are refreshed after this correction.

The property seed reuses the helper's original record as one of its 40 records, rather than leaving it as a forty-first record.
The final 40-record property run passed in 17.62 s.
The complete Task 8b suite passed 55 cases in 26.12 s before that seed-only adjustment.

### Native-disk timings

Store: `/var/tmp/lodge-bench/s90000`, generated by `scripts/bench_store.py`, with 160,800 listed files.
Installed build: `/var/tmp/lodge-bench/venv-task-8b`, CPython 3.13.5, PyYAML 6.0.3 with libyaml, bytecode compiled with `python -m compileall -q`.
The benchmark imports before timing and disables cyclic collection, matching the CLI read process.
Each condition has three sequential samples after the gate and other checks finished, without overlapping test work.
A new object has empty process-local caches; a same-object measurement first calls identities and listings once to populate those caches.
The one-edit condition appends one synthetic line to a tracked entry, and a finally block restores its original bytes; git status is clean afterwards.

Command: `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_ATTR_NOSYSTEM=1 /var/tmp/lodge-bench/venv-task-8b/bin/python /var/tmp/lodge-bench/task-8b-timing.py`.
These environment settings isolate the intended unconverted store without changing repository or user configuration.
Raw samples and per-call measurements are retained in `/var/tmp/lodge-bench/task-8b-timing-isolated.jsonl`.

| State | Object caches | identities, best of three (s) | listings, best of three (microseconds) | Git in the fastest identity (s) |
|---|---|---:|---:|---:|
| clean | new-object | 0.755814 | 1.433 | 0.217830 |
| clean | same-object | 0.470453 | 1.793 | 0.126084 |
| one-edit | new-object | 0.751629 | 1.483 | 0.227106 |
| one-edit | same-object | 0.462162 | 1.984 | 0.124998 |

Listing retrieval follows identities as the port contract specifies: identities has already prepared and retained both mappings, so listings itself performs no git call or file read.
The numbers exclude importing Python modules and constructing the store object.
The following tables give every git invocation, in order, in the fastest identity sample of each condition; shares are percentages of the whole identity duration.
Repeated config and var calls take the full cache key before and after computing a conversion result; stable same-object cache hits take the key once.
The three commit verifications resolve HEAD, the remote base, and the local base fallback, respectively; this synthetic store has no remote-tracking base.
Both diff commands use `core.fsmonitor=false`, `core.checkStat=default`, and `core.trustctime=true`, with `--no-renames -z --name-only`, and diff-index uses `--cached`.


clean, new-object:

| Call | Operation | Time (ms) | Identity share |
|---:|---|---:|---:|
| 1 | `verify commit reference` | 1.666 | 0.22% |
| 2 | `resolve lodge tree` | 2.047 | 0.27% |
| 3 | `ls-tree -r -z --full-tree` | 53.953 | 7.14% |
| 4 | `rev-parse --git-path index` | 2.811 | 0.37% |
| 5 | `ls-files -t -v -z` | 25.551 | 3.38% |
| 6 | `rev-parse --git-path info/attributes` | 2.757 | 0.36% |
| 7 | `config --get core.autocrlf` | 2.067 | 0.27% |
| 8 | `config --path --get core.attributesFile` | 1.929 | 0.26% |
| 9 | `var GIT_ATTR_GLOBAL` | 1.843 | 0.24% |
| 10 | `config --get core.autocrlf` | 2.612 | 0.35% |
| 11 | `config --path --get core.attributesFile` | 1.900 | 0.25% |
| 12 | `var GIT_ATTR_GLOBAL` | 1.969 | 0.26% |
| 13 | `diff-index --cached` | 12.788 | 1.69% |
| 14 | `diff-files` | 41.840 | 5.54% |
| 15 | `verify commit reference` | 2.514 | 0.33% |
| 16 | `verify commit reference` | 1.979 | 0.26% |
| 17 | `merge-base` | 2.084 | 0.28% |
| 18 | `resolve lodge tree` | 2.178 | 0.29% |
| 19 | `ls-tree -r -z --full-tree` | 53.342 | 7.06% |
| | All git | 217.830 | 28.82% |

clean, same-object:

| Call | Operation | Time (ms) | Identity share |
|---:|---|---:|---:|
| 1 | `verify commit reference` | 2.523 | 0.54% |
| 2 | `config --get core.autocrlf` | 2.571 | 0.55% |
| 3 | `config --path --get core.attributesFile` | 2.136 | 0.45% |
| 4 | `var GIT_ATTR_GLOBAL` | 1.428 | 0.30% |
| 5 | `diff-index --cached` | 12.408 | 2.64% |
| 6 | `diff-files` | 42.430 | 9.02% |
| 7 | `verify commit reference` | 2.980 | 0.63% |
| 8 | `verify commit reference` | 2.727 | 0.58% |
| 9 | `merge-base` | 1.781 | 0.38% |
| 10 | `resolve lodge tree` | 2.143 | 0.46% |
| 11 | `ls-tree -r -z --full-tree` | 52.956 | 11.26% |
| | All git | 126.084 | 26.80% |

one-edit, new-object:

| Call | Operation | Time (ms) | Identity share |
|---:|---|---:|---:|
| 1 | `verify commit reference` | 2.438 | 0.32% |
| 2 | `resolve lodge tree` | 1.869 | 0.25% |
| 3 | `ls-tree -r -z --full-tree` | 62.491 | 8.31% |
| 4 | `rev-parse --git-path index` | 2.938 | 0.39% |
| 5 | `ls-files -t -v -z` | 22.794 | 3.03% |
| 6 | `rev-parse --git-path info/attributes` | 2.626 | 0.35% |
| 7 | `config --get core.autocrlf` | 1.986 | 0.26% |
| 8 | `config --path --get core.attributesFile` | 2.224 | 0.30% |
| 9 | `var GIT_ATTR_GLOBAL` | 2.247 | 0.30% |
| 10 | `config --get core.autocrlf` | 2.781 | 0.37% |
| 11 | `config --path --get core.attributesFile` | 2.273 | 0.30% |
| 12 | `var GIT_ATTR_GLOBAL` | 1.653 | 0.22% |
| 13 | `diff-index --cached` | 13.987 | 1.86% |
| 14 | `diff-files` | 41.776 | 5.56% |
| 15 | `verify commit reference` | 2.724 | 0.36% |
| 16 | `verify commit reference` | 2.058 | 0.27% |
| 17 | `merge-base` | 2.073 | 0.28% |
| 18 | `resolve lodge tree` | 2.181 | 0.29% |
| 19 | `ls-tree -r -z --full-tree` | 53.985 | 7.18% |
| | All git | 227.106 | 30.22% |

one-edit, same-object:

| Call | Operation | Time (ms) | Identity share |
|---:|---|---:|---:|
| 1 | `verify commit reference` | 3.088 | 0.67% |
| 2 | `config --get core.autocrlf` | 2.628 | 0.57% |
| 3 | `config --path --get core.attributesFile` | 1.444 | 0.31% |
| 4 | `var GIT_ATTR_GLOBAL` | 1.914 | 0.41% |
| 5 | `diff-index --cached` | 12.384 | 2.68% |
| 6 | `diff-files` | 40.180 | 8.69% |
| 7 | `verify commit reference` | 2.878 | 0.62% |
| 8 | `verify commit reference` | 2.132 | 0.46% |
| 9 | `merge-base` | 1.988 | 0.43% |
| 10 | `resolve lodge tree` | 2.296 | 0.50% |
| 11 | `ls-tree -r -z --full-tree` | 54.066 | 11.70% |
| | All git | 124.998 | 27.05% |

The initial run used the inherited Git configuration, which has `core.autocrlf=input`.
That setting requires every path to be read and hashed on every identity, even when Git reports a clean tree, exactly as d-dqpf59 requires.
Command: `/var/tmp/lodge-bench/venv-task-8b/bin/python /var/tmp/lodge-bench/task-8b-timing.py`.
Its separate observations are retained in `/var/tmp/lodge-bench/task-8b-timing.jsonl`:

| State | Object caches | identities, best of three (s) | listings, best of three (microseconds) | Git in the fastest identity (s) |
|---|---|---:|---:|---:|
| clean | new-object | 2.987764 | 1.512 | 0.225344 |
| clean | same-object | 2.688120 | 1.994 | 0.130126 |
| one-edit | new-object | 2.959963 | 1.412 | 0.222765 |
| one-edit | same-object | 2.687345 | 1.512 | 0.134562 |

### Concerns and remaining scope

The unconverted identity still takes 0.756 s on a new object and 0.470 s with process-local caches on the clean 160,800-file store.
Those observations are above the eventual 0.3 s indexed-read target; Task 8b has no stop on that target, and the index and folder-signature work is still to come.
Git accounts for about 0.218 s and 0.126 s of those samples; the remainder includes listing construction, walking names, collecting source keys, mapping copies, and overlay work.
An autocrlf conversion setting intentionally forces reads of every file and costs about 3.0 s here.
No timing assertion was added to pytest.
No product read uses these new methods yet; the existing exact-tree gate and write paths retain their behaviour.
No project record creation or edit, reviewer-file edit, plan-step edit, or new decision was needed.
The concurrency-test wrapper change is the only required file outside Task 8b's listed files; it solely forwards the expanded Store protocol.
There is no unresolved NEEDS_CONTEXT.


### Final validation and delivery

`UV_FROZEN=true sh scripts/check.sh` passed on the final implementation and 40-record fixture: 616 files formatted, Ruff clean, strict mypy on 236 source files, Vulture clean, 1,690 passed and 1 skipped in 77.86 s, and `lodge check --gate` printed `ok`.
The log is retained at `/var/tmp/lodge-bench/task-8b-check-final.txt`.
`git diff --check` passed, and the benchmark store is clean after restoration.
The earlier green full gates were repeated after the final regression fixes and fixture adjustment; the result above is the final run.
The implementation, test-first evidence, timings, and this report are delivered together in the Task 8b commit.
