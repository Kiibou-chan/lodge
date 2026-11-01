# Review of Tasks 1 and 2 (lodge at scale)

Reviewer: Claude (Opus), task review, correctness then practice then design.
Under review: branch `read-speed-build`, commits `d8cb076` (Task 1) and `b122942` (Task 2); their base is `2dffc85`, whose `src/`, `tests/`, and `scripts/` equal those of `0aa7759` (`git diff --stat 2dffc85 0aa7759 -- src tests scripts` is empty), so the old build is installed from `0aa7759`.
Report under review: `docs/superpowers/plans/2026-10-31-lodge-at-scale/task-1-2-report.md`.
Scratch: `/var/tmp/lodge-review-t1-2/` (detached worktrees `base` at `0aa7759` and `wt` at `b122942`, removed at the end; a compiled native-disk venv of each, `venv-base` and `venv-wt`; the probes `fuzz.py`, `inject.py`, `prun.sh`, `runner.py`; outputs under `out/`; the scratch store copies and the 69 MB fuzz outputs deleted).

## Counts

Blocking 0, Important 1, Minor 6.

## Verdict on the dispatch's three questions

1. Task 2 leaves every check result and problem wording unchanged, on every input this review could build: a 3,000-seed differential fuzz of the core, and byte-identical CLI output of old and new builds on the repository's own store (361 commands), the bench stores `s900` and `s9000` (15 commands each), and four fault-injected copies of the bench stores; at `s90000` equivalence was not run (the old build cannot finish there), and the new build ran without a crash.
2. The benchmark scripts measure what the plan says, with one gap in interruption handling (M2) and one shape the probe does not exercise (M4).
3. The committed diff `2dffc85..b122942` holds no personal path, machine name, or other project's data: a case-insensitive grep of `git diff 2dffc85 b122942` for home paths, user, machine, and other project names, and mail addresses matches nothing; the only absolute paths are `/var/tmp/lodge-bench/...` in the report, the benchmark location the plan itself names (Global Constraints, "Benchmarks run on native disk under `/var/tmp/lodge-bench/`"); the fixtures and the shape probe are the made-up harbour project.

## Evidence

### Differential fuzz of the core rewrites

`/var/tmp/lodge-review-t1-2/fuzz.py` builds 3,000 seeded random snapshots (1 to 30 entries over four areas, some areas without `_area.md`, orders with omissions, duplicates, and unknown IDs; 0 to 40 decisions by author, coordinator, and agent, some imported, with random create, edit, retire, and link changes, `replaces`, `narrows`, and `confirms` including unknown IDs; `rests_on` with self-links, unknown targets, and cycles; open and closed doubt and question threads), a published state with records dropped, entries edited, and decisions redated, and in 30 per cent of seeds a `current` state.
For each it prints `repr(derive(after))`, `check_state(after)`, `check_change(published, after, settings, now, current)`, `derived_order` of every area, `rests_on_tree` and the viewer's `_branches` HTML of every entry, and `render_spec`.
Command, once per build, from `/var/tmp`: `PYTHONHASHSEED=0 venv-{base,wt}/bin/python -s fuzz.py 3000`.
Result: the two 68.9 MB outputs are byte-identical (`cmp`).
They hold problems of all eight checks (31,260 of check 1, 74,619 of 2, 7,780 of 3, 25,851 of 4, 3,894 of 5, 7,525 of 6, 17,706 of 7, 9,736 of 8), 7,384 doubt marks, and 8,370 `(see above)` leaves, so each rewritten path ran.
(A first run under `-I` differed only in frozenset print order, since `-I` ignores `PYTHONHASHSEED`; with the seed fixed the outputs agree.)

### The test oracles

`linear_derive_oracle.old_derive` and its helpers equal the base `derive.py` from `def derive` on, apart from the name (`diff` of the two ranges).
`linear_check_oracles.py` and `linear_order_oracle.py` were compared by reading against `base/src/lodge/core/{check_areas,check_cycles,check_change,doubts,order}.py` and `base/src/lodge/viewer/pages.py`: the same code.

### CLI, old build against new build, byte for byte (stdout and exit status)

Runner: `/var/tmp/lodge-review-t1-2/prun.sh BUILD STORE CMDFILE OUTDIR`, then `diff -r` of the two output folders.

| Store | Commands | Result |
|---|---|---|
| repository's own store (`wt`, 346 records) | `show REF --reasoning --provenance` for every record, `check`, `check --gate`, `waiting`, `threads`, `spec`, four searches | 361 identical |
| `s900` | the twelve lines of `scripts/bench_reads.txt`, `show A`, `search A --brief`, `search a --brief` | 15 identical |
| `s9000` | the same fifteen | 15 identical |
| `f900`: copy of `s900` with an unrecorded staged edit, a deleted published decision, three new decisions (dated before the decision it replaces and sharing entries, one narrowing a replaced decision and confirming as an agent, one dated 2099 retiring an entry), a three-cycle and a self-link, broken `rests_on` and area order lines, a removed `_area.md`, and open doubt and question threads | `check`, `check --gate`, `waiting`, `threads`, `spec`, three `spec`/search lines, `show` of 18 affected records, `thread`, `timeline` | 32 identical; `check --gate` prints 37 lines over checks 1, 2, 3, 4, 7, and 8 |
| `f900b`: copy of `s900` with an area order missing an entry and listing two entries twice | `check`, `check --gate`, `spec --area area-002`, `waiting` | 4 identical |
| `p900`: `f900b` with the area problems committed, then one unrecorded edit | `check`, `check --gate`, `waiting` | 3 identical; the gate prints the three `note: already published, check 7` lines, so the app-built `ChangeFacts` path for published problems is covered |
| `f9000`: `s9000` with the `f900` faults | `check`, `check --gate`, `waiting`, `threads`, `spec --area area-000`, `show` of 16 records | 21 identical |

### s90000

Equivalence at `s90000` was not run: the old build takes over 900 s per call at 160,000 files (the report's Task 1 run; this review's old-build `check --gate` had not finished after 33 minutes), so it cannot serve as an oracle at that size, and the coordinator stopped the old-build runs.
Equivalence rests on `s900`, `s9000`, the fault-injected copies, the repository's own store, and the fuzz above.
New build, crashes: `check --gate`, `show {code}`, `spec --area area-001`, `check`, `waiting`, `search {code} --brief`, and `show {entry} --reasoning --provenance` all exit 0; `check --gate` prints `ok`.
New build, timing, one run each at 01:05 with a load average of 4.9 from the other builder: `show CODE-53010` 72.2 s, `check --gate` 115.8 s.
These are well above the report's phase sums because the report's phase probe uses an experimental C loader for headers, which Task 3 has not yet brought to this commit, so each of the two loads runs the Python YAML loader here; not a finding against Task 2.
Note for the coordinator: between 00:14 and 01:03 this review ran one to four `s90000` processes while the Task 3 or 4 builder was benchmarking `s9000` and `s90000` (`ps` at 00:29); timings that builder took in that window ran under extra load.

### Gate

`UV_FROZEN=true sh scripts/check.sh` in the detached `b122942` worktree: format, Ruff, strict mypy (204 files), Vulture, 1,413 passed, `lodge check --gate` ok.
`ruff check scripts` clean.
Store sizes: `git ls-files | wc -l` gives 1,608, 16,121, and 160,801, the report's 1,607, 16,120, and 160,800 records plus `.lodge.toml`.

### Bench script behaviour

`bench_reads.py` on a scratch copy of `s900` (`c900`), `--runs 2`, both builds, `--mode changed` and `--mode cold`: tables printed, `Identical` true, the changed edit visible (`show {entry}` 306 characters against 275 cold), the store clean afterwards (`git status --porcelain` empty), no temporary folder left.
Placeholders resolved: `s900` `{code}` CODE-9 (whose sibling CODE-9.why exists), `{code2}` CODE-896; `s90000` `{code}` CODE-53010.
The entry coded `A` has citers: 543 record files of `s90000` hold the token `a` or `A`, so `show A` exercises the ten-citer cap.

## Findings

### I1 · Important · The facts the app builds for `check_change` are checked by no test

Handle: `src/lodge/app/state.py:66-76` and `src/lodge/app/reads.py:86-97` build `ChangeFacts` by hand, spelling the published sort key as `(p.path, p.check, p.message)`; `src/lodge/core/check_change.py:32-39` (`change_facts`) builds it with `sort_key`; `docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/shapes.py:91-96` is a fourth copy.
`tests/core/test_linear_checks.py:125-156` (`test_check_change_with_facts_equals_without`) compares `check_change(facts=change_facts(...))` with `check_change(facts=None)`, which calls the same `change_facts`, so the test cannot fail.
`grep -rn "already published" tests` finds nothing: no test asserts the note that the published-problem set produces.
Failure scenario: `sort_key` gains the line (which `Problem` carries), or Task 10c's stored facts (which the plan says build `published_problems` "from those facts' sort keys") key them by a different tuple; `sort_key(found) in known` (`check_change.py:63`) then never holds, every problem already published is printed as new, and `check --gate` fails a clean change, while all 1,413 tests stay green.
The code is right today: `sort_key` is exactly that tuple (`check_state.py:41-42`), and the `p900` run above shows identical notes from both builds.
Fix: one constructor in `core` used by `state.py`, `reads.py`, the probe, and later Task 10c (for example `change_facts(published, after, *, before=None, after_derived=None, after_problems=None)`, or a `published_facts(published, derived) -> (status, keys)` helper applying `sort_key`); a test in `tests/app/` (new file) that a problem in the published tree still present prints `note: already published` under `check --gate` and is not a problem; and the core test compared with an oracle copy of the pre-Task-2 `check_change` in `linear_check_oracles.py` rather than with `change_facts` itself.

### M1 · Minor · `check --gate` loads, derives, and checks the published snapshot twice

Handle: `src/lodge/app/reads.py:81-98`: `read_checked` (`state.py:66-72`) loads `state.published`, derives it, and runs `check_state` on it; `check` then loads `base.published`, derives it, and checks it again; in checkout mode `base.published` is the same `Tree` object (`gitstore/checkout.py:45-46` and `53-56`, `published.py:37-44`).
Failure scenario: at 160,000 files the gate spends about 6 s on a second `load` and 1.4 s on a second `derive` and `check_state` (the report's phase table: `load(published)` 6.0 s, `derive` 0.95 s, `check_state(derived=)` 0.42 s); not a regression (the base did the same), but against "one derive per snapshot" and the plan's 14 s gate estimate.
Fix: when `base.published is state.published`, reuse the snapshot and its derived facts; carry them out of `read_checked` on `State`.

### M2 · Minor · `bench_reads.py` leaves its traces when killed

Handle: `scripts/bench_reads.py:48-75` relies on `finally` and `TemporaryDirectory` for cleanup, and Python's default SIGTERM ends the process without either.
Evidence: the report's own `timeout 900 ... --mode cold` run left `/var/tmp/lodge-bench/read-cache-uidl5f6k` (created 23:43:57, beside `task1-s90000.md` at 23:43:52).
Failure scenario: the same interruption in `changed` mode leaves the entry's edit on disk; `changed` refuses a dirty store (`bench_reads.py:100-103`), but `seen` and `cold` do not check, so the next replay silently times and compares a changed store.
Fix: a SIGTERM handler that raises `SystemExit` so `finally` runs, the clean-store check in every mode, and a `--timeout` per run through `subprocess.run(timeout=...)` instead of wrapping the script in `timeout`.

### M3 · Minor · Whole-spec rendering stays quadratic in the number of areas and in an area's size

Handle: `src/lodge/core/order.py:31-36` (`written_order` scans every entry of the snapshot for each area, and `render.py:63-66` calls it per area) and `order.py:53-73` (`derived_order` scans the whole area for each placement).
Measured with `venv-wt`, collector off: `render_spec` over all areas at 12,000, 24,000, and 48,000 entries in 226, 452, and 905 areas takes 0.22, 0.72, and 2.56 s, so about 16 s at the bench's 120,000 entries; `derived_order` of one area of 2,000, 4,000, and 8,000 independent entries takes 0.18, 0.79, and 3.78 s.
Failure scenario: `lodge spec` and the viewer's whole-spec page at 160,000 files spend about 16 s in these scans, beyond the plan's "about 14 s" for the spec after Tasks 2 to 4; one large area grows it quadratically.
The plan's Task 2 list does not name these steps, so this is a plan gap rather than the builder's; `spec --area` and the five targeted reads are not affected.
Fix: group entries by area once per render, and in `derived_order` keep, per entry, its unplaced dependants in written order with a count of unplaced targets; or record it as out of scope for this plan.

### M4 · Minor · The shape probe never runs the second prefix scan Task 2 replaced

Handle: `docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/shapes.py:41-52` makes every decision a coordinator's, so no decision is flagged and `_behind_entry_edits` (`src/lodge/core/derive.py:152-164`, called only for flagged decisions at `derive.py:72-75`) never runs; the "one entry, many decisions" row's doubling says nothing about it.
`ruff check` also reports UP017 at `shapes.py:47` (outside the gate's scope).
Failure scenario: a regression to a prefix scan in `_behind_entry_edits` keeps the probe linear; only `test_derive_same_as_before`'s comparison budget would catch it.
Fix: make every third decision of that shape an author's (as `test_derive_same_as_before` does) and use `datetime.UTC`.

### M5 · Minor · An app test in the core suite, with its path inserted at import

Handle: `tests/core/test_linear_derive.py:30-34` inserts `tests/app` into `sys.path` in the module body to import `fakes`, for `test_derive_once_per_checked_read` (`:122-144`), which drives `lodge.app.state.read_checked`; the other suites do this in `conftest.py` (`tests/app/conftest.py:5-6`, `tests/gitstore/conftest.py:9-10`).
Failure scenario: collecting `tests/core` alone now depends on `tests/app/fakes.py` through a side effect at import, and Task 4 tightens this test, so it grows in the wrong suite.
Fix: move that test to a new file under `tests/app/` (Task 4 already adds `tests/app/test_identical_reads.py`), or move the path insertion into `tests/core/conftest.py`.
The plan names the file, so this is practice, not a deviation.

### M6 · Minor · The report's open concern about `check_state` is answered by the plan

Handle: report, "Concerns and delivery"; plan, "Expected cost", row "a point read", column "After Tasks 2 to 4": "`derive` 0.9, `check_state` about 0.5" are separate phases.
Failure scenario: the ledger carries an open concern that the 1 s expectation for `check_state` is missed, when the comparable figure (`check_state(current, derived=d)`, 0.424 s, beside `derive` 0.950 s) meets the plan's split.
Fix: close the concern in the ledger line with this handle; no code change.

## Correctness pass, per rewrite (reasoning checked against the fuzz)

- `check_areas`: `counts` keeps first-occurrence order as `dict.fromkeys(order)` did, `in counts` equals `in order`; folders and entries sorted as before.
- `check_cycles`: iterative Tarjan over existing targets; a component of two or more is exactly the set `reach[i]` with `i in reach[t]` the old code built; self-links form singleton components and stay check 2's.
- `_missing`: the union built once.
- `_dates`: the smallest shared entry is the first sorted entry of `d` that a target changes, as `sorted(...)[0]` gave; `((replaces | narrows | confirms) & earlier) | shared` is the old target set, iterated sorted, with the same reason precedence.
- `derive`: `touches[d.id]` is deduplicated (`_entries_changed`, `dict.fromkeys`), so a decision appears once per entry list and `_previous` returns the old `list.index` prefix's last non-skipped element.
- `doubt_marks`: `changed_by` values are decision IDs, so the dropped `& s.decisions.keys()` filter changes nothing; reverse propagation reaches the same sources, excluding the entry itself, and marks are added in sorted entry order.
- `derived_order`, `rests_on_tree`, `_branches`: the stack versions visit children in the old order, with the same `ancestors` path and the same point at which `seen` and `expanded` grow.
- `main`: `lodge` has no option before the command but `--version`, so `args[:1] != ["view"]` identifies the viewer.

## Files read

`CLAUDE.md`; `.claude/agents/reviewer.md`; the plan `docs/superpowers/plans/2026-10-31-lodge-at-scale.md` (Global Constraints, Calls made, Expected cost, Review Focus, Tasks 1, 2, 3, 6, 7, 10b, 10c, 11, and 12 in part); `task-1-2-report.md`; `plan-recheck-codex.md` (R2), `plan-fix-2.md` (R2 and N4 lines); the full diff `2dffc85..b122942` of `src/`, `scripts/`, and `tests/`; `src/lodge/core/derive.py`, `doubts.py`, `order.py` (first 80 lines and the diff), `check_state.py` (`sort_key`), `model.py`, `settings.py` (`CoreSettings`); `src/lodge/app/state.py` (55-90), `reads.py` (60-120); `src/lodge/main.py` (95-125); `src/lodge/cli/parser.py` (argument lines); `src/lodge/gitstore/checkout.py` (gate), `branch.py` (gate), `published.py` (`committed_gate`); `scripts/bench_reads.py`, `bench_reads.txt`, the `bench_store.py` diff; `probes/shapes.py`; `tests/core/builders.py`, `linear_fixtures.py`, `linear_check_oracles.py`, `linear_order_oracle.py`, `linear_derive_oracle.py` (by diff), `test_linear_checks.py`, `test_linear_derive.py` (parts), `test_deep_chains.py`, `tests/test_collector.py`.

## Files not read

`lodge spec` and the recorded decisions (the dispatch's questions are about equivalence and the scripts, which the runs settle; no spec text was needed); the brief and the plan's other review and fix files; `probes/phases.py` and the builder's scratch copies under `/var/tmp/lodge-bench/` (`phases-task2*.py`); `src/lodge/core/render.py` beyond its imports and the `written_order` call; `src/lodge/viewer/pages.py` beyond `_branches`; `tests/core/test_linear_derive.py` lines 60-115 in full; `tests/app/fakes.py`; `tests/structure_rules.py`.
