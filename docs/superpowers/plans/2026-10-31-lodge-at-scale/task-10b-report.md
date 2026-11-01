# Task 10b report

Status: Task 8c fix round complete; Task 10b is NEEDS_CONTEXT before its skeleton.
Read the current plan, progress ledger, standing builder rules, Task 8c review and scratch probes, and decisions through `lodge show --reasoning`.
No record writes are required or authorised by this task.
Production retains interim R11-A; SECOND-1 is d-n65rhr, and CONV-1 is d-egknpk.

## Task 8c fix round

The review is copied to `task-8c-review.md`.
A1 preserves the full 1,100-deep exact tree, without the review's proposed depth cap, which conflicts with the dispatched requirement to preserve reads.
B1 concerns the test's removed conversion source and staged CRLF bytes, plus a FIFO swap that R11-B never opens unless the file changes first.
M1 to M6 are addressed, with the required `unlistable` interface retained as explained below.

### Red evidence

The initial regression run was `uv run --frozen pytest tests/gitstore/test_disk_depth.py tests/gitstore/test_identity_fix_round.py -q`:

```text
FAILED tests/gitstore/test_disk_depth.py::test_1100_deep_tree_is_read_with_bounded_descriptors
FAILED tests/gitstore/test_disk_depth.py::test_repository_root_may_be_a_link
FAILED tests/gitstore/test_identity_fix_round.py::test_r11a_does_not_compute_git_candidates
3 failed, 1 passed in 0.72s
```

The unchanged R11-B scratch baseline reproduced B1:

```text
test_random_edits_agree: record-29.md index blob 1256ee5b89faf459873751d6677b61268f189966 != disk blob 8342dc7293138208401bb2ec1672592098201473
1 failed in 9.90s
```

The first baseline run passed in 14.27s, confirming the timing dependence.
The unchanged FIFO test also failed in the scratch R11-B package:

```text
test_regular_file_swapped_for_fifo_before_open: listing blob 67969c3e0daaba8ef035b8cfe1c92e74cd02dbc2 != empty-file blob e69de29bb2d1d6434b8b29ae775ad8c2e48c5391
1 failed in 0.34s
```

The failed `ls-files` test failed against the pre-fix R11-B package before the conservative fallback was added:

```text
FAILED tests/gitstore/test_identity_fix_round.py::test_failed_ls_files_reads_every_base_path
1 failed in 0.35s
```

The first deep-tree test lost its file under the 128-descriptor soft limit, the root-link test raised `NotADirectoryError`, and the R11-A test raised `AssertionError: unneeded candidate group`.
The parser list equality test passes on the existing complete lists; removing `guide` from the shortcut list in memory makes its new assertion fail.
No parser behaviour change was needed for M6.

```text
  assert set(action.choices) == grammar._COMMANDS == set(COMMANDS)
AssertionError
```

### Implementation and focused verification

A1 uses an explicit folder stack and reopens validated ancestors with a constant descriptor bound, preserving every file at depth 1,100 even under a soft limit of 128 descriptors.
The root may be a link; every folder below it still uses `O_NOFOLLOW`.
M1 removes `Flags.read`, the unused conversion defaults, the unread root field, and the checkout alias assignment; flag tests now execute `CheckoutIdentity.current` under R11-B.
The `unlistable` field stays because Task 8c's documented walk interface produces it for Task 11; the new depth test reads it.
M2 reads every base path if `ls-files` fails.
M3 moves the candidate group into the R11-B branch: `candidates` returns `None` for production R11-A and switches to `identity.stat_current(rev, trunk)` for R11-B.
M4 opens only the repository root without `O_NOFOLLOW`.
M5 recognises the first descriptor listing by call order, removing the test's `/proc` dependency.
M6 compares both command lists with the complete parser's subparser choices.
B1 normalises any remaining CRLF working files before removing the conversion source between sequences, and edits the FIFO target before the swap, so the same tests cover either branch.
The source is still removed each sequence, preserving the property test's ability to detect missing diff and flag handling; dedicated removed-source history tests retain each R11 rule's byte-versus-index coverage.
Existing tests edited: `test_identity_property.py`, `test_identity_links.py`, `test_flags.py`, `test_attributes.py`, `test_identity_lazy.py`, `test_parser_named.py`; `identity_rules.py` supplies an explicit alternative-rule context manager.
The flag and conversion tests now supply the production group's explicit inputs; the staged-race and fallback tests explicitly select R11-B, where those mechanisms execute.
Focused verification: 63 passed, four skipped; strict mypy and the 39 structure checks pass.
The twenty-run scratch R11-B property/FIFO proof passes; all four property mutants fail.

The first attempted property repair retained the attributes file permanently, which let the no-diffs mutant survive because every Markdown path became a conversion candidate.
It was replaced before delivery by normalising the files before each source removal.
All four mutants now fail independently: no-diffs in 0.44 s, no-flags in 0.63 s, no-untracked in 0.47 s, and no-conversions in 2.05 s.

The final candidate branch checks a failing `ls-files` separately from the two diff outputs, avoiding any attempt to interpret flag-tagged names as diff paths.
The four mutants of that final source fail in 0.49 s, 0.69 s, 0.56 s, and 2.16 s respectively.
The first full gate passed: 2,081 tests, six skipped, plus formatting, Ruff, strict mypy, Vulture, and `lodge check --gate`.
The final uninterrupted `UV_FROZEN=1 sh scripts/check.sh` exited 0 before the fix-round commit:

```text
662 files already formatted
All checks passed!
Success: no issues found in 277 source files
2081 passed, 6 skipped in 148.69s (0:02:28)
ok
note: area storage: order changed
```

The storage-order note predates this fix round.
The complete gate log is `/var/tmp/lodge-bench/t8c-fix-gate-final.log`.
`git diff --check` passes.

### Fix-round identity timing

Command: `uv run --frozen python` with three fresh child processes calling `open_store(...).identities()` on synthetic `s90000` under `/var/tmp/lodge-bench`, with `LODGE_INDEX=off`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_ATTR_NOSYSTEM=1`, and `GIT_OPTIONAL_LOCKS=0`.
The native virtual environment and source were bytecode-compiled first; imports are outside the measured call, and a new store object is constructed in each process.
Interim R11-A, 160,800 files, samples 2.220533 s, 2.180887 s, and 2.213531 s; best of three 2.180887 s.
This verification ran beside the test suites and is diagnostic, with no speed-up claim against the previous isolated measurements.
No Task 10b search replay timing is claimed while its scope question is pending.

The final scratch R11-B package also passes the four unskipped removed-source history cases and the failed-`ls-files` regression: five passed in 9.00 s.
Production keeps the four R11-B history cases skipped until the author's ruling.

### Twenty-run R11-B proof and delivery

A scratch package under `/var/tmp/lodge-bench/t8c-fix-r11b` differs from the finished production source only in the `candidates` function body, which returns `identity.stat_current(rev, trunk)`.
In twenty fresh subprocesses, run with `PYTHONPATH` pointing at that scratch source, the command was `python -m pytest tests/gitstore/test_identity_property.py tests/gitstore/test_identity_links.py::test_regular_file_swapped_for_fifo_before_open -q`.
Every invocation exited 0 and printed `2 passed`, for twenty property-test passes and twenty FIFO-test passes, with no failures.
The full output is `/var/tmp/lodge-bench/t8c-fix-r11b-proof.log`.
Both the full gate and this proof use the final source, with no further production changes afterwards.
The fix-round commit includes the copied review, implementation, tests, ledger, and this report, with message `Task 8c fix round: preserve deep reads and prove both R11 branches`.
The dispatch's push command follows that commit.

## Task 10b: NEEDS_CONTEXT before the skeleton

The task's file list omits the search dispatch and the modules split out during Task 10a.
`app/lodge.py` routes both search entry points directly to `reads`, and must route them to `indexed` for the CLI to reach indexed search.
`gitstore/index_schema.py` owns schema creation, and `gitstore/index_space.py` owns whole-index clearing, including iteration over every SQLite table; FTS5 requires coordinated creation and drop/re-creation rather than deleting its shadow tables independently.
`tests/app/fakes.py` only re-exports `MemoryIndex` from `tests/app/fake_index.py`, so implementing the specified fake method belongs in that module.
Question: may Task 10b modify `app/lodge.py`, `gitstore/index_schema.py`, `gitstore/index_space.py`, and `tests/app/fake_index.py` to complete those hand-offs, in addition to its listed files?
The dispatch requires an unclear step to be reported and stopped, and prohibits changes to earlier tasks' files unless Task 10b calls for them.
No Task 10b skeleton, tests, implementation, or benchmark has started while this scope question is pending.

