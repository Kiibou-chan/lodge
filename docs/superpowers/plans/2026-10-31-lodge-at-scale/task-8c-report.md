# Task 8c build report

Status: built and verified in the dispatched worktree on `read-speed-build`.
The current plan, progress ledger, builder rules, CONV-1 (`d-egknpk`), both Codex reviews, and their identity, descriptor, gitlink, and removed-attribute probes were read.
No record was opened or written directly, and no `lodge add` is needed.

The brief supplies the interim R11-A rule, pending the author's STALE-1.
The implementation will keep that choice in one function, with active exact-byte tests and the alternative test skipped with `awaits the author's STALE-1`.
The benchmark will switch only that function in a scratch package to measure R11-B.

## Step 0

New disk, concurrent git, scan/config, and committed-listing signatures are skeletons before tests.
Structure: `39 passed in 0.37s`.
Strict mypy: `Success: no issues found in 251 source files`.

## Steps 1 and 2

New tests were run before implementation, against the moved-interface skeletons.
The first primitive run exposed a runtime-only annotation error in the parser test; postponed annotations fixed that test before the complete red run.

```text
=========================== short test summary info ============================
FAILED tests/gitstore/test_identity_lazy.py::test_identities_run_no_ls_tree_for_published
FAILED tests/gitstore/test_identity_lazy.py::test_lazy_listings_agree[clean]
FAILED tests/gitstore/test_identity_lazy.py::test_lazy_listings_agree[edit]
FAILED tests/gitstore/test_identity_lazy.py::test_lazy_listings_agree[untracked]
FAILED tests/gitstore/test_identity_lazy.py::test_lazy_listings_agree[deleted]
FAILED tests/gitstore/test_identity_lazy.py::test_lazy_listings_agree[behind]
FAILED tests/gitstore/test_identity_lazy.py::test_staged_between_diff_calls_is_seen
FAILED tests/gitstore/test_identity_lazy.py::test_index_changing_every_time_falls_back_to_exact
FAILED tests/gitstore/test_identity_lazy.py::test_conversion_key_takes_no_paths
FAILED tests/gitstore/test_identity_lazy.py::test_nested_attributes_found_without_a_path_scan[False]
FAILED tests/gitstore/test_identity_lazy.py::test_nested_attributes_found_without_a_path_scan[True]
FAILED tests/gitstore/test_identity_lazy.py::test_bare_autocrlf_key_converts
FAILED tests/gitstore/test_identity_lazy.py::test_removed_attributes_agree[ident]
FAILED tests/gitstore/test_identity_lazy.py::test_removed_attributes_agree[working-tree-encoding=UTF-16]
FAILED tests/gitstore/test_identity_lazy.py::test_removed_attributes_agree[filter=berth]
FAILED tests/gitstore/test_identity_lazy.py::test_removed_attributes_agree[text eol=crlf]
FAILED tests/gitstore/test_identity_lazy.py::test_every_file_read_without_a_conversion_source
FAILED tests/gitstore/test_identity_links.py::test_folder_replaced_by_symlink_to_copy
FAILED tests/gitstore/test_identity_links.py::test_folder_replaced_by_symlink_to_other_content
FAILED tests/gitstore/test_identity_links.py::test_attachments_folder_symlink
FAILED tests/gitstore/test_identity_links.py::test_folder_link_to_outside_is_never_read
FAILED tests/gitstore/test_identity_links.py::test_link_inside_an_attachment_path
FAILED tests/gitstore/test_identity_links.py::test_folder_swapped_for_link_during_the_walk
FAILED tests/gitstore/test_identity_links.py::test_unlistable_folder_agrees
FAILED tests/gitstore/test_identity_links.py::test_fifo_agrees - NotImplement...
FAILED tests/gitstore/test_identity_links.py::test_regular_file_swapped_for_fifo_before_open
FAILED tests/gitstore/test_identity_gitlinks.py::test_empty_submodule_folder[checkout]
FAILED tests/gitstore/test_identity_gitlinks.py::test_empty_submodule_folder[branch]
FAILED tests/gitstore/test_identity_gitlinks.py::test_populated_submodule[checkout]
FAILED tests/gitstore/test_identity_gitlinks.py::test_populated_submodule[branch]
FAILED tests/gitstore/test_identity_gitlinks.py::test_absent_submodule_folder[checkout]
FAILED tests/gitstore/test_identity_gitlinks.py::test_absent_submodule_folder[branch]
FAILED tests/gitstore/test_identity_gitlinks.py::test_branch_gitlink_key_is_empty_text
FAILED tests/gitstore/test_identity_gitlinks.py::test_submodule_commit_absent_from_the_object_database
FAILED tests/gitstore/test_git_many.py::test_results_in_call_order - NotImple...
FAILED tests/gitstore/test_git_many.py::test_all_started_before_any_awaited
FAILED tests/gitstore/test_git_many.py::test_request_exit_waits_for_every_call
FAILED tests/gitstore/test_git_many.py::test_missing_git_raises_git_missing
FAILED tests/gitstore/test_flag_scan.py::test_scan_equals_the_loop - NotImple...
FAILED tests/gitstore/test_flag_scan.py::test_config_values_spellings - NotIm...
FAILED tests/test_parser_named.py::test_help_texts_unchanged - NotImplemented...
FAILED tests/test_parser_named.py::test_errors_unchanged - NotImplementedError
FAILED tests/test_parser_named.py::test_named_parser_builds_one_subcommand - ...
43 failed, 1 passed, 4 skipped in 11.99s
```

The branch case already agreed on the old interface in that run.
It and the amended property test were then run against the committed-listing skeleton before implementation:

```text
=========================== short test summary info ============================
FAILED tests/gitstore/test_identity_lazy.py::test_lazy_listings_agree[branch]
FAILED tests/gitstore/test_identity_property.py::test_random_edits_agree - No...
2 failed in 0.41s
```

The four skipped cases are the requested R11-B histories, with reason `awaits the author's STALE-1`.

## Step 3

Built concurrent git calls under a before/after index key, with three attempts and one retained exact-tree fallback.
HEAD and trunk commits are pinned before the group; its merge-base result determines publication, and tree identities come from `rev-parse`.
Committed mappings are lazy and cached for at most two commits per store.
Flag scanning has the clean-index shortcut, and conversion keys contain sources rather than the path set; path construction and `check-attr` happen only on a miss.
Configuration uses one `config --list -z` and one `var -l` in the group, with individual fallbacks for omitted variables.
The shared disk reader opens folders relative to real parent descriptors, opens files without following links and without blocking on special files, and reads bytes only from regular descriptors.
Both the overlay and exact gate/add reader use it.
Gitlinks retain their kinds, use disk contents in checkout mode, and have empty-text keys and texts in branch mode without requesting missing commits.
The parser constructs arguments only for the named command; help and error differential tests preserve the full parser's text.
No Store port or branch tip-resolution contract changes.

The corrected unavailable-gitlink and removed-attribute fixtures were also run against an unchanged copy of the pre-task package.
This isolates real old-behaviour failures from the skeleton failures and corrects the original branch fixture, which initially lacked a remote-tracking lodge tip.
The filter history commits its clean `INDEXTXT` form before smudging `WORKTREE`; both diff calls are asserted empty after the untracked attributes source is removed.

```text
=========================== short test summary info ============================
FAILED tests/gitstore/test_identity_gitlinks.py::test_empty_submodule_folder[checkout]
FAILED tests/gitstore/test_identity_gitlinks.py::test_empty_submodule_folder[branch]
FAILED tests/gitstore/test_identity_gitlinks.py::test_populated_submodule[checkout]
FAILED tests/gitstore/test_identity_gitlinks.py::test_populated_submodule[branch]
FAILED tests/gitstore/test_identity_gitlinks.py::test_absent_submodule_folder[branch]
FAILED tests/gitstore/test_identity_gitlinks.py::test_branch_gitlink_key_is_empty_text
FAILED tests/gitstore/test_identity_gitlinks.py::test_submodule_commit_absent_from_the_object_database
FAILED tests/gitstore/test_identity_lazy.py::test_removed_attributes_agree[ident]
FAILED tests/gitstore/test_identity_lazy.py::test_removed_attributes_agree[working-tree-encoding=UTF-16]
FAILED tests/gitstore/test_identity_lazy.py::test_removed_attributes_agree[filter=berth]
FAILED tests/gitstore/test_identity_lazy.py::test_removed_attributes_agree[text eol=crlf]
11 failed, 1 passed in 10.37s
```

Extending the flag decoder oracle to unterminated buffers exposed and fixed a missing final attributes entry:

```text
FAILED tests/gitstore/test_flag_scan.py::test_scan_equals_the_loop
1 failed in 0.49s
```

Existing tests edited: `test_identity_property.py` removes root attributes at the start of each sequence, as A6 requires.
`test_attributes.py::test_no_sources_no_check_attr_call` now expects `var -l` plus the individual system-variable fallback where the test omits it from `var -l`.
Its original no-`check-attr` and isolated-configuration assertions stay intact.
No other earlier-task tests or reviewer files were edited.

The corrected property test passes with R11-B selected in a scratch package.
The four requested mutants were run separately against that package, since R11-A's mandatory all-file reads deliberately make those candidate-discovery optimisations redundant:

```text
r11b-property 0 1 passed in 13.96s
no-diffs 1 1 failed in 0.50s
no-flags 1 1 failed in 0.62s
no-untracked 1 1 failed in 0.51s
no-conversions 1 1 failed in 1.95s
documented R11-B cases remain skipped in the source 0
```

Focused verification: 88 passed, 4 skipped (identity, attributes, flag scan, and structure); 55 passed (links, concurrent git, parser, and structure).
Strict mypy and Ruff pass.
The full gate and native timing table follow below.

Final edge review added an unreadable gitlink-folder case to `test_unlistable_folder_agrees`.
It first failed because the fast listing kept an empty-text file where the exact reader omitted the real directory:

```text
FAILED tests/gitstore/test_identity_links.py::test_unlistable_folder_agrees[lodge/decisions/submodule]
1 failed, 1 passed in 0.44s
```

The file-open error path now distinguishes an inaccessible real directory from an unreadable file.
The ten link/special-file cases pass.
The pre-entry link swap now happens after `scandir`'s entries have all been classified, before the child descriptor opens.

A fallback identity regression also exposed ambiguous newline-separated attachment names.
The fallback now separates attachment names with NUL, which a filesystem path cannot contain:

```text
FAILED tests/gitstore/test_identity_lazy.py::test_exact_fallback_identity_separates_attachment_names
1 failed in 0.35s
```

That test now passes.

## Step 4: native timings

Commands: `uv run --frozen python -m compileall -q src .venv/lib`, then `uv run --frozen python /var/tmp/lodge-bench/task-8c-bench.py`.
The measurement script and raw JSON remain under `/var/tmp/lodge-bench/` for review.
The store is a dedicated copy of `scripts/bench_store.py`'s synthetic `s90000`, with 160,800 files, under `/var/tmp/lodge-bench/task8c/s90000`.
The reference store is unchanged.
All measurements ran sequentially, without concurrent tests or other timing jobs.
Environment: CPython 3.13.5, SQLite 3.47.1, PyYAML 6.0.3, libyaml 0.2.5, Git 2.56.0, ext4, and a native virtual environment with compiled bytecode.
Configuration is isolated with `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_ATTR_NOSYSTEM=1`, and dedicated synthetic HOME/XDG folders.
The conversion rows set only local `core.autocrlf=input`.

Each sample constructs a new store before timing its actual `identities()` call.
Each row is the best of three fresh processes, excluding process start and imports from the identity timer.
The edit appends one synthetic statement to one specification file, restored afterwards.
The R11-B package is a scratch copy with only `read_paths` switched from `base | present | changed` to `changed`.
It uses all the same git calls, descriptor reader, mappings, and conversion logic.
The final fallback-name separator correction does not run in these stable-index samples.
These are identity timings, not completed indexed CLI read timings.

| Configuration | Checkout | Rule | Best identity (s) | Three samples (s) |
|---|---|---|---:|---|
| isolated | clean | R11-A | 1.988806 | 1.996052, 1.988806, 1.989275 |
| isolated | clean | R11-B | 0.442069 | 0.442069, 0.443880, 0.444893 |
| isolated | edited | R11-A | 1.998111 | 1.998111, 2.019867, 2.025078 |
| isolated | edited | R11-B | 0.448099 | 0.457982, 0.455884, 0.448099 |
| input | clean | R11-A | 2.080052 | 2.107371, 2.080052, 2.092822 |
| input | clean | R11-B | 2.003570 | 2.012890, 2.003570, 2.009300 |
| input | edited | R11-A | 2.070314 | 2.081193, 2.112537, 2.070314 |
| input | edited | R11-B | 2.008149 | 2.019240, 2.032857, 2.008149 |

Disjoint stage times from the fastest sample of each row follow.
Nested git time is subtracted from the caller stage, so the columns sum to the measured call.
“Other” includes set construction, path selection, and identity/adaptor work outside the named stages.
The read/hash overlay stage includes sorting, disk reads, hashes, and overlay construction.

isolated, seconds:

| Stage | R11-A clean | R11-B clean | R11-A edited | R11-B edited |
|---|---:|---:|---:|---:|
| git group | 0.056753 | 0.059866 | 0.062582 | 0.061300 |
| serial git | 0.064276 | 0.067581 | 0.064405 | 0.065392 |
| committed mapping | 0.128734 | 0.121530 | 0.118864 | 0.125777 |
| flag scan | 0.014415 | 0.013905 | 0.013898 | 0.014491 |
| disk walk | 0.119057 | 0.117265 | 0.125587 | 0.118040 |
| conversions | 0.000245 | 0.000347 | 0.000314 | 0.000354 |
| read/hash overlay | 1.483644 | 0.002994 | 1.488108 | 0.003146 |
| other | 0.121681 | 0.058582 | 0.124353 | 0.059600 |

input, seconds:

| Stage | R11-A clean | R11-B clean | R11-A edited | R11-B edited |
|---|---:|---:|---:|---:|
| git group | 0.061695 | 0.058215 | 0.055947 | 0.056311 |
| serial git | 0.066353 | 0.065133 | 0.066198 | 0.065890 |
| committed mapping | 0.120404 | 0.126592 | 0.120869 | 0.126885 |
| flag scan | 0.014118 | 0.014054 | 0.014161 | 0.014550 |
| disk walk | 0.123200 | 0.119409 | 0.126253 | 0.119407 |
| conversions | 0.049208 | 0.049538 | 0.050869 | 0.049674 |
| read/hash overlay | 1.496047 | 1.493857 | 1.487138 | 1.498757 |
| other | 0.149027 | 0.076772 | 0.148879 | 0.076676 |

The initial diagnostic R11-B edited identity was 0.485094 s, above the task's 0.45 s reporting threshold; the final rerun is 0.448099 s, just below it.
The progress ledger names both, and the stage table above records the final run.
The stage table shows where it is spent; no target or stop is changed.
R11-A's full-file reads remain the interim production behaviour while STALE-1 is with the author.
The conversion configuration is reported beside the targets under CONV-1, never under the no-conversion stop.

Startup, best of nine fresh processes, with the same compiled native environment:

```text
guide best 0.14300359800108708 median 0.14808564601116814 samples [0.15676037900266238, 0.14300359800108708, 0.14446660300018266, 0.14902955299476162, 0.14808564601116814, 0.15051493898499757, 0.14567680098116398, 0.15284479601541534, 0.14642092201393098]
import best 0.13786510299541987 median 0.14643746300134808 samples [0.13786510299541987, 0.14643746300134808, 0.1394066649954766, 0.14055517801898532, 0.13913120698998682, 0.1499491939903237, 0.15057161598815583, 0.1490347329818178, 0.15396528501878493]
```

The commands are `.venv/bin/lodge guide --read` and `.venv/bin/python -c "import lodge.main"`.
The initial startup harness mistakenly used `python -m lodge`, which has no package entry point; that failed attempt is excluded, and the console entry point above was measured instead.
The earlier diagnostic startup run is also excluded from this final table.

The skipped R11-B histories were explicitly unskipped only in a scratch pytest plugin with the one-function R11-B package: `4 passed in 8.85s`.
The committed test retains the exact skip reason requested by the brief.

## Gate and delivery

The first full gate passed: `1976 passed, 6 skipped in 88.20s`, then `lodge check --gate` printed `ok` and the existing `area storage: order changed` note.
The final gate initially stopped at Vulture's unused `traceback` parameter in the strengthened scan-swap test.
That test parameter is now explicitly marked unused.
Final command: `UV_FROZEN=true sh scripts/check.sh`, exit 0.
Ruff format, Ruff, strict mypy, Vulture, all tests, and the lodge gate passed:

```text
641 files already formatted
All checks passed!
Success: no issues found in 257 source files
1978 passed, 6 skipped in 88.38s (0:01:28)
ok
note: area storage: order changed
```

Concerns: STALE-1 remains with the author; the dispatched full-file rule is interim, and the alternative is measured only in scratch.
R11-B is close to the 0.45 s reporting threshold and crossed it in the initial diagnostic, so the report keeps both measurements.
No end-to-end indexed command target is claimed here, and Task 12's stop is unchanged.
No NEEDS_CONTEXT remains, and no record or other task's reviewer file was changed.
