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
This round's independent native s90000 synthetic copy, isolated from user git configuration and with every process counted at spawn, measures before: new-commit 5.740158 s / 2,267 processes; cold-index 5.730874 s / 2,267 processes, best of three.

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
After the code commit, the same isolated s90000 probe measures new-commit 0.555728 s / 15 processes and cold-index 0.532518 s / 15 processes, best of three.
The checked-in `task12-tools/relist.py` times store construction and `identities()`, with a commit changing `lodge/`, a refreshed git index, and a separate cold index file.
Both source revisions use the same compiled, frozen workspace Python 3.13.5 and isolated synthetic HOME; the two-second CPU sampler records no competing interval above half a core (peak 0.194).
Commands and source extraction are in `task12-tools/README.md`, and all twelve process timings are retained in `task12-tools/relist-results.jsonl`.

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

11. F-2: the timings and main report now state that other CPU-heavy jobs overlapped parts of the initial a1500 s90000 matrix, every cell is best of three, and no table value is known to depend on them, following the review's mapping.
The code-identical a1500/a1900 seen and third-sighting cells agree within 1.3 per cent.
This is a limitation statement, with no code or test change.

12. F-5: stale measurement-in-progress and next-stage sentences are removed in place, and contradictory production and runtime claims are rewritten to the current rulings and verified runtimes.
This is documentation cleanup, with no new test.

13. F-6: the renderer labels completed base argument-parser failures `exit 2 (argument parser)` instead of displaying their elapsed times beside read timings.
This affects the multi-ref show, multi-query search, and phrase-search base cells at every size and in both base modes.
There is no production behaviour change; the final table audit checks these cells.

14. M-E: the progress ledger names production R11-B throughout the affected Task 8c, Task 10b, and Task 11 entries, settles SCALE-1 and DISK-1 with d-j51qmy, and lists d-k194gk with d-dxqxsn.
The Task 10c facts and M-1 wording also follow their current rulings, and the R11-A comparison measurements remain explicitly labelled.
This is an in-place documentation correction, with no new test.

The Task 11 fix report also states the overturned per-folder-only, two-second, process-count, and clear-retention claims, so those paragraphs are rewritten in place with the same final rules.
This additional documentation file is required by the dispatch's in-place correction rule.

## Final production measurements

Production source `2a82ebe` is measured only after the code and tooling commits are pushed.
Command: `LODGE_TASK12_RESULTS=/var/tmp/lodge-bench/task12/results-fix.jsonl uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/task12-tools/measure.py fix`, after `setup.py --production-only`.
No tests, gate, compilation, or other CPU-heavy jobs run alongside the production rerun.
The two-second process sampler observes no sustained competing load, with one isolated background burst at 0.597 of one core; the adjacent intervals peak at 0.010 and 0.020 of one core.
All numbers below are seconds through exit, best of three; before is the original R11-B / 1,900 matrix, and after is the refreshed final-code rerun.

| Targeted row | Seen before | Seen after | First before | First after | Second before | Second after | Third before | Third after |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `show {code}` | 0.477424 | 0.318994 | 4.800864 | 4.763202 | 10.317305 | 10.246784 | 0.478916 | 0.329925 |
| `show {entry} --reasoning --provenance` | 0.476497 | 0.318172 | 4.771788 | 4.713574 | 10.288060 | 10.191667 | 0.477585 | 0.330271 |
| `show {decision}` | 0.475398 | 0.329614 | 4.793418 | 4.816772 | 10.270693 | 10.230127 | 0.474254 | 0.338072 |
| `search berth --brief` | 3.642551 | 3.413660 | 7.404895 | 7.275897 | 12.827831 | 12.770222 | 3.625916 | 3.466161 |
| `search "berth crane" --brief` | 4.641889 | 4.463174 | 7.377556 | 7.325683 | 12.832411 | 12.726447 | 4.664825 | 4.475804 |
| `search {code} --brief` | 1.044527 | 0.897457 | 7.335697 | 7.218180 | 12.753654 | 12.736158 | 1.032708 | 0.902660 |
| `search berth` | 3.633163 | 3.417063 | 7.305099 | 7.267444 | 12.755167 | 12.709092 | 3.640357 | 3.457474 |
| `waiting` | 0.476562 | 0.333287 | 4.744800 | 4.686042 | 10.258561 | 10.189438 | 0.477600 | 0.330963 |
| `threads` | 0.475154 | 0.331928 | 4.743270 | 4.691910 | 10.219870 | 10.143268 | 0.475081 | 0.324553 |
| `show {code} {code2} {entry}` | 0.484303 | 0.342795 | 4.944153 | 4.928847 | 10.510862 | 10.408809 | 0.482194 | 0.337126 |
| `show A` | 0.488491 | 0.344006 | 6.887569 | 6.834685 | 12.363042 | 12.354877 | 0.490858 | 0.348936 |
| `search berth tide --brief` | 6.873480 | 6.672988 | 10.099970 | 9.903198 | 15.469657 | 15.376479 | 6.877241 | 6.678739 |
| `search --phrase "berth crane" --brief` | 5.359782 | 5.146775 | 8.417321 | 8.341705 | 13.860674 | 13.836106 | 5.335343 | 5.181692 |

Supplemental `thread q-000000`, an intact stored not-found answer (exit 2), is 0.331919 s before and 0.321106 s after.
The production start-up floor is 0.089991 s for guide read, leaving 0.210009 s of the 0.3 s seen budget; Python pass is 0.010071 s and import is 0.090095 s.
The best seen-show diagnostic is 0.323667 s, with identity 0.098370 s and state metadata 0.112492 s.
Every targeted seen diagnostic has three samples, and the phase table in `timings.md` is replaced in place.
CONV-1 is also remeasured, outside the targets, for all three commands and all four sightings.

| CONV-1 row | Seen before | Seen after | First before | First after | Second before | Second after | Third before | Third after |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `show {code}` | 2.300646 | 2.185481 | 6.445687 | 6.328846 | 11.965020 | 11.802129 | 2.298526 | 2.199060 |
| `waiting` | 2.306276 | 2.173459 | 6.366917 | 6.257886 | 11.873642 | 11.766341 | 2.316908 | 2.172053 |
| `search berth --brief` | 5.442970 | 5.283014 | 8.969317 | 8.828960 | 14.456538 | 14.443522 | 5.443402 | 5.306203 |

Each of the ten edit/read/read/read cycles is repeated in three independent sequences; the following after values are the best per sighting across those three sequences.

| Cycle | First before | First after | Second before | Second after | Third before | Third after |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 4.811746 | 4.766836 | 10.355870 | 10.276971 | 0.481155 | 0.326203 |
| 2 | 4.786936 | 4.762863 | 10.421792 | 10.285816 | 0.476907 | 0.324796 |
| 3 | 4.807344 | 4.757626 | 10.560354 | 10.259215 | 0.488215 | 0.325779 |
| 4 | 4.784026 | 4.727121 | 10.448955 | 10.316525 | 0.483020 | 0.324511 |
| 5 | 4.810145 | 4.734484 | 10.414587 | 10.288514 | 0.477197 | 0.324634 |
| 6 | 4.835643 | 4.746970 | 10.381966 | 10.273092 | 0.485695 | 0.327114 |
| 7 | 4.790396 | 4.749836 | 10.377060 | 10.272791 | 0.479523 | 0.320938 |
| 8 | 4.801044 | 4.751830 | 10.347026 | 10.308052 | 0.478507 | 0.325993 |
| 9 | 4.831874 | 4.744635 | 10.361969 | 10.271444 | 0.483304 | 0.321117 |
| 10 | 4.886653 | 4.743494 | 10.381199 | 10.307854 | 0.479419 | 0.325532 |

All three sequences clear zero times and end with four kept states, just as the original ten-cycle R11-B / 1,900 run does.
Sequence 1: 266,977,280 used bytes, 267,530,240 physical bytes, and 1 published facts row / 3,329,566 value bytes.
Sequence 2: 266,973,184 used bytes, 267,534,336 physical bytes, and 1 published facts row / 3,329,566 value bytes.
Sequence 3: 266,964,992 used bytes, 267,526,144 physical bytes, and 1 published facts row / 3,329,566 value bytes.
The capacity and clear verdicts agree in every sequence; timings.md shows the first sequence's byte counts.
The production stop remains: seen point reads exceed 0.3 s, broad searches exceed 1.0 s, and first and second changed reads exceed 3 s; no later work starts, and the server question remains with the coordinator.

## Coverage and final table checks

`audit.py --fix` exits 0: `replay_samples=195`, `cycle_samples=90`, `phase_samples=51`, `cycle_samples_per_sequence=3`, and `cycle_clears=0`.
All 195 replay samples match the exact reader in stdout, stderr, and exit status; all ninety cycle streams match their reference, and all 51 diagnostics match after removing their trailer.
Seen and third-sighting replay metadata is unchanged.
The initial four-way audit also exits 0: 1,602 replay samples, 360 cycle samples, 288 base samples with 78 timeouts, 216 phase samples, three clears, and 100 chained samples with one clear.
The retained R11-A and R11-B / 1,500 command tables are byte-for-byte unchanged; nine base parser-failure rows are labelled in both clean and changed columns.
The production raw samples are retained verbatim, and all twelve repeated relist samples are checked in beside the scripts.
Both dispatched reviews still match their input files verbatim.
The measured production sources remain identical to `2a82ebe`.

## Final validation and delivery

`UV_FROZEN=1 sh scripts/check.sh` exits 0, with formatting, Ruff, strict mypy over 301 source files, and Vulture green.
Its final result lines are:

```text
2236 passed, 2 skipped in 211.06s (0:03:31)
ok
note: area storage: order changed
```

`git diff --check` and the scan of added lines and retained samples for personal paths, names, and machine identifiers are clean.
The two skips are existing capability cases; no STALE-1 skip remains.
Delivery before the final results commit: `98cc34e` (reviews), `2a82ebe` (code and test evidence), `adf8980` (measurement tools and refresh regression), and `7021d3a` (relist reproduction and repeated-cycle rendering), each pushed to `read-speed-build` immediately after committing.
Every requested item is addressed or explicitly ruled not fixed, with no context question outstanding and no later work started.
