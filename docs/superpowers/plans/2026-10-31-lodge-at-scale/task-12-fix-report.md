# Task 12 fix round

Scope: Task 12 review F-1 to F-6 and P-1 to P-3, and Task 11 fix recheck I-A and M-A to M-F.
The two dispatched reviews are copied verbatim to `task-12-review.md` and `task-11-fix-recheck.md`, committed and pushed first as `98cc34e`.
No record is opened directly, added, or edited, and no later task is started.

## Code and policy items

1. I-A: one walk collects its relisted directories before choosing their bases; at most sixteen use `Committed.folder`, and above sixteen every base comes from the cached per-commit `Committed.listing`.
The full listing retains file, link, folder, and gitlink kinds for these bases, and cache eviction drops the corresponding folder map.
The existing internal folder-walk callback and identity hand-off change with this requirement; the added committed-helper skeleton passes structure (39 tests) and strict mypy before the regression is written.
The new 300-folder regression counts `subprocess.Popen`, including the grouped children and store construction, for both a changed `lodge/` commit and a cold folder index.
Red: `AssertionError: 319`, `assert 319 <= 12`, `2 failed in 3.15s`.
The final bound is fifteen, including construction; the old implementation exceeds both bounds.
The focused folder suite passes 41 tests after implementation.
The recheck measured s90000 new-commit 7.634 s / 2,264 git calls, and cold-index 7.566 s.
This round's independent native synthetic copy, with every process counted at spawn, measures before: new-commit 8.188227 s / 2,268 processes; cold-index 8.262224 s / 2,268 processes.

2. M-B: `rev-parse --absolute-git-dir` joins the existing `run_many` group, and its result is passed to the folder walk.
The existing 300-path test now counts every spawn, retains the batch-input assertions, and checks that the git-directory command belongs to the group.
Red: `AssertionError: assert ['rev-parse', '--absolute-git-dir'] in ...`, `2 failed, 8 deselected in 0.62s`.
Green: `2 passed, 8 deselected in 0.64s`.

3. M-C: `Committed.folder` uses `git ls-tree <rev> -- <folder>/`, whose successful empty output means an absent folder, and whose failure raises through `run_bytes`.
No failed call can publish an empty base or folder row.
Red with an injected failing git: `Failed: DID NOT RAISE LodgeError`, `1 failed, 1 deselected in 0.32s`.
Green: committed-helper and folder-fix tests, `12 passed in 2.33s`.
The existing per-folder command assertion follows the changed git spelling.

4. M-A: the trust margin is three seconds, exceeding two-second rounding plus a coarse kernel tick; both the module docstring and Task 11 wording match.
The existing timestamp-ordering regression gains the recheck's 12.000 s scan, 12.005 s mutation, and stat stuck at 10 s.
Red: the exact-tree comparison reports `Right contains 1 more item: {'lodge/decisions/late.md': ...}`, `1 failed, 2 passed, 8 deselected in 0.80s`.
Green: `3 passed, 8 deselected in 0.73s`.

5. M-D: a clear deletes folder rows and the completeness row for roots whose recorded git directory no longer exists, preserving every row for existing roots.
The plan states this rule in Task 11.
The regression seeds two worktrees, removes and prunes one, and compares the other's rows byte for byte after clearing.
Red: `AssertionError: assert [...] == []`, `Left contains 5 more items`, `1 failed, 2 deselected in 0.42s`.
Green: `1 passed, 2 deselected in 0.32s`.

6. M-F: no test or code change is needed: the index filename embeds a digest of every source file as well as the schema, so a schema bump cannot meet an old index file.

7. P-1: d-k194gk is read with reasoning through lodge, together with d-dxqxsn and d-j51qmy.
Call 18 and the `StateFacts` interface text are rewritten in place: only immutable published statuses, keyed by published identity, and no stored problems.
`read_model.build_facts` and its published-only regression already match the ruling, so no new test or production change is needed.

8. P-3: the required-threads test now attempts to construct a real stored state's values after omitting threads, and requires refusal.
It fails behaviourally for both a tuple default and `field(default_factory=tuple)`: `Failed: DID NOT RAISE TypeError`, respectively `1 failed, 10 deselected in 0.19s` and `0.18s`.
Both deliberate mutants are reverted; unchanged required-threads production passes (`1 passed, 10 deselected in 0.15s`).

9. Task 10c M-1 / P-2 is ruled not fixed: a damaged shared bucket blob arises only through an edit of the index file, reads stay exact through the memory fallback, and the index is safe to delete.
The same sentence is placed in Task 10c of the plan; no test or code change is requested.

The combined code regression run passes `98 passed in 25.20s`, including persistent-folder properties, recovery, committed helpers, app facts, and structure.
Formatting, Ruff, and strict mypy over 300 source files pass.
After the code commit, the same s90000 probe measures new-commit 2.097658 s / 15 processes and cold-index 2.076388 s / 15 processes, against 8.188227 s and 8.262224 s / 2,268 processes before.
The probe times `identities()` on a newly constructed store, with the source revision changed in `lodge/`, an explicit refreshed git index, and a separate cold index file.

## Measurement tooling

10. F-1 / F-3 / F-4: `task12-tools/` now retains setup, measurement, probe, rendering, and audit scripts from the synthetic benchmark area.
Benchmark paths take `LODGE_BENCH_ROOT`, default `/var/tmp/lodge-bench`, with the workspace derived from the script location or `LODGE_BENCH_WORKSPACE`; setup also accepts arguments.
Historical four-way sources can be recreated from `bb9fe48`; production setup takes the committed current R11-B / 1,900 sources directly.
The replay refreshes git's index once before any timed read; setup does so once for each new or reused store copy, and the matrix refreshes after restoration.
The regression runs red before implementation: replay `AssertionError: Expected 'mock' to have been called once. Called 0 times.`, and both new/reused setup cases `NotImplementedError`, `3 failed in 0.17s`.
Green: `20 passed in 0.18s` across refresh, replay options, and cleanup.
Two existing mocked-main tests stub the newly required refresh subprocess; their tested behaviour is unchanged.
The original R11-B inflation comes from git re-hashing racily clean files in freshly cloned checkouts while `GIT_OPTIONAL_LOCKS=0` prevents the reads from refreshing the index.
The changed-mode cleanup refreshed that index before the diagnostics; the review reproduces an approximately 0.14 s difference.
The rerun uses three samples for every targeted s90000 row and seen diagnostic, and three independent ten-edit/read/read/read sequences.
