# Review of Task 4: identical states reuse the checked snapshot and skip the change check

Reviewed: commits 0a29988 and d1ebe63 on `read-speed-build`, in a detached worktree at d1ebe63.
Old build for equivalence: bd7e03b.
Status: done. Blocking 0, Important 1, Minor 3.
The code change is correct and its output equals the old build's in every scenario run; the one Important is the plan's Step 4, which the builder correctly stopped on.

## Findings

### Correctness pass

The code change is the early return at `src/lodge/app/state.py:66-70`.
It is sound unconditionally, not only on the samples: `load` (`src/lodge/core/snapshot.py:49-72`) is a function of `tree.files` and `tree.attachments` alone (it never reads `rev`), so equal listings give equal snapshots; and `read_checked` already discarded `check_change`'s notes and kept only problems not in `state.result.problems`, so the old path's result equals the shortcut's when `check_change(s, s).problems` is empty.
Each sub-check checked against the code: `_missing` (`check_change.py:81`) finds every ID; `_dates`, `_imports_over_live`, `_unlisted_sources` (`check_entries.py:75`), the decision half of `_links_to_dead` (`check_change.py:157`), and the link and create halves of `check_entries` iterate over `new_decisions` or new entries, empty here; `check_entries` wants nothing since `before == entry` and `was == now` (one `derive` of equal snapshots); `check_immutable` (`check_immutable.py:16`) sees equal fields, equal messages, and for a closed thread takes the first branch, never the `elif`; the entry half of `_links_to_dead` skips every target in `previous == e.rests_on`.
The old path's `sorted(...)` on an already sorted tuple (`check_state.py:38`, same key) is the identity, so order, `failing`, and `unrecorded` are equal too.
The comparison is of listings only: `(current.files, current.attachments) == (published.files, published.attachments)`; no `rev`, ident, or revision name enters it.
The gate (`src/lodge/app/reads.py:79-104`) still loads the published tree and runs `check_change` itself, so `check --gate` is untouched; `committed_gate` (`gitstore/published.py:38`) already used the same listing comparison.

Tests: `uv run --frozen --quiet pytest tests/core/test_identical_change.py tests/app/test_identical_reads.py tests/core/test_linear_derive.py tests/app/test_reads.py tests/core/test_check_change.py -q`: 136 passed.
Mutations in my scratch worktree, each reverted: comparing `rev` instead of listings, 23 failed; comparing file keys only, 19 failed; comparing `files` without attachments, 2 failed (`attachment-added`, `attachment-removed`).
So the tests pin listing comparison, the attachment half, and revision independence.
The output test forces the old path through a `dict` subclass whose `__eq__` is false (`tests/app/test_identical_reads.py:75-83`); Python tries the subclass's reflected `__eq__` first, so the old path really runs, and the test asserts `check_change` ran (`:142`).

### Findings

**Important I1 · Step 4 is not done, and as written it cannot finish.**
Handle: `docs/superpowers/plans/2026-10-31-lodge-at-scale.md:215` asks for `--against` Task 1's build at `s90000` "(the last now finishes)"; `task-4-report.md:336-342` stops on NEEDS_CONTEXT after Task 1's build was still in its first warm-up at 24 minutes.
Failure scenario: Task 4 is ledgered as done with no large-store parity, or a builder retries without a bound and spends hours on a baseline the plan's own Task 1 recorded as unfinished in 900 s.
The parenthesis is true of the new build (17.0 s best of three, `task-4-report.md`), not of the build it is compared with.
Fix: the coordinator rules the comparison point and records it with `lodge add` (scope `process`, `work_item` the plan), since it amends Step 4.
Two options: replay `s90000 --against` a build of 07dacb5 (Task 3's tip; it differs from d1ebe63 in `src/lodge/app/state.py:66-70` alone, so it isolates exactly this task), after one call under `timeout 900` shows it finishes; my estimate is about two loads plus the change check, tens of seconds, not measured, since I ran nothing old on `s90000`; or accept parity from `s900`, `s9000`, and the edited-store scenarios below, and record `s90000` as the new build's timings only.

**Minor M1 · The rule the shortcut rests on is stated in neither function.**
Handle: `src/lodge/app/state.py:59-64` (the docstring does not mention the early return) and `src/lodge/core/check_change.py:51-58` (the docstring does not say a check must find nothing when `published` equals `after`).
Failure scenario: a later check in `check_change` that fires on a state compared with itself (one over every decision rather than new ones) is silently skipped by every read but the gate; `tests/core/test_identical_change.py` catches it only if one of its 48 fixed snapshots triggers the new check.
Fix: one line in each docstring: in `read_checked`, "Equal listings load to equal snapshots, and a snapshot compared with itself adds no problem, so the comparison is skipped (d-zyqzkg)"; in `check_change`, "With `published` equal to `after` every check finds nothing; reads rely on it (d-zyqzkg)".

**Minor M2 · Unnamed self-comparison cases.**
Handle: `tests/core/test_identical_change.py:98` parametrizes 48 snapshots without `ids`, so a failure reads `snapshot31` and the reader counts list entries to find which.
Fix: build `snapshots()` as `pytest.param(..., id="duplicate-id")` pairs, or pass `ids` naming each case.

**Minor M3 · The listing comparison now exists twice, and Task 10a adds a third.**
Handle: `src/lodge/app/state.py:66-70` and `src/lodge/gitstore/published.py:41` spell the same test, `(a.files, a.attachments) == (b.files, b.attachments)`; the plan's Task 10a (`2026-10-31-lodge-at-scale.md:470`, `:517`) "consumes Task 4's shortcut" on blob listings, but Task 4 produced an inline condition, not something to consume.
Failure scenario: Task 8a adds blob IDs to every `Tree`; one copy is moved to compare blobs and another is not, and "identical" means two things in one read.
Fix: one function in `core/snapshot.py`, such as `same_listing(a: Tree, b: Tree) -> bool`, used by `read_checked` and `committed_gate` now and by Task 10a later.

### Equivalence: old (bd7e03b) against new (d1ebe63) on edited scratch copies

Harness: `/var/tmp/lodge-review-t4/harness/` (`scenarios.sh` checkout mode, `branch.sh` branch mode, `compare.py` runs both builds per command and compares exit status, standard output, and standard error, with branch mode's `fetched N s ago` normalised; `probe.py` counts `load` and `check_change` in the new build's `check`).
Builds: native-disk venvs `/var/tmp/lodge-review-t4/venv-old` (bd7e03b) and `venv-new` (d1ebe63), CPython 3.13.5, bytecode compiled.
Commands on `s900` and the own store: `show {code}`, `show {entry} --reasoning --provenance`, `show {decision}`, `search berth --brief`, `search berth`, `waiting`, `threads`, `spec --area {area}`, `check`, `check --gate`.
Checkout scenarios, each from a reset copy: clean; unstaged entry edit; staged entry edit; staged edit with the working tree reverted; untracked copied decision; untracked future-dated decision; untracked stray file; untracked attachment; touched only; mode change only; edited then reverted; unstaged and staged decision deletion; hand edit of a published decision; renamed decision; a feature-branch commit outside `lodge/`; a feature-branch commit editing an entry; that commit reverted in the working tree; that commit reverted by a second commit.
Branch-mode scenarios against a local bare remote: clean; rewritten with the same tree; rewritten with only a non-`lodge/` file changed; rewritten with an entry edited; rewritten with a decision deleted; back at the accepted tip; a fast-forward entry edit; a rewrite acknowledged with `git update-ref -d refs/lodge/accepted`.

Results (outputs in `/var/tmp/lodge-review-t4/*.txt`):
- `s900` checkout: 19 scenarios × 10 commands, 190 of 190 identical.
  The shortcut fired (one `load`, no `check_change`) on clean, staged-with-reverted-worktree, touched only, mode change only, edited then reverted, the commit outside `lodge/`, and both reverts; every other scenario took two loads and one change check and printed the expected check 1, 2, 4, or 5 problem.
- `s900` branch: 8 scenarios × 10 commands, 80 of 80 identical; the shortcut fired on both rewrites that keep `lodge/` equal (the freshness line still names the rewrite), and the change check ran on the rewrites that edit or delete a record.
- Own store on `main` (shortcut path at clean): 19 × 10, 190 of 190 identical.
- Own store on d1ebe63 (published is its merge base with `main`, 55 record files apart, so every scenario takes the comparison path on real records): 19 × 10, 190 of 190 identical.
- `s9000` checkout: the same 19 scenarios × 5 commands (`show {entry} --reasoning --provenance`, `search berth --brief`, `waiting`, `check`, `check --gate`, cut for time: the old build takes 7.5 s per call), 95 of 95 identical, the shortcut firing in the same scenarios as on `s900`.
- `s9000` branch: the same 8 scenarios × 5 commands, 40 of 40 identical.
- Not run: anything on `s90000`, per the dispatch.

Gate: `UV_FROZEN=true sh scripts/check.sh` in my worktree at d1ebe63: ruff clean, mypy strict clean on 209 files, 1,550 passed, `lodge check --gate` ok, exit 0; this confirms the report's gate line.

### Practice and design passes

Practice: the change is five lines, no duplication beyond M3, no comment explaining an edit; the tests are within 300 lines and use new basenames; the one edited existing test (`tests/core/test_linear_derive.py:143-144`) is the one the plan names.
The report's proof matches the code as built (checked line by line above); its "Requirements and approach" section is written in the future tense, harmless history.
Design: no new import edge or module; the shortcut sits in `app`, where the plan puts it; the gate keeps its own comparison (Global Constraints, exact trees); the open plan-versus-code gap is Step 4 (I1) and the inline condition Task 10a expects to consume (M3).

## Files read

`CLAUDE.md`; the plan's header, Global Constraints, Calls made, Expected cost, Review Focus, Tasks 1 and 4, and its lines on Task 10a's use of the shortcut; `task-4-report.md`; `brief-t4.md`; d-zyqzkg and d-c0q20c through `lodge show`; `src/lodge/app/state.py`; `src/lodge/app/reads.py:75-110`; `src/lodge/core/check_change.py`; `src/lodge/core/check_entries.py`; `src/lodge/core/check_immutable.py`; `src/lodge/core/check_state.py:1-70`; `src/lodge/core/snapshot.py:1-120`; `src/lodge/gitstore/trees.py`; `src/lodge/gitstore/checkout.py:1-120`; `src/lodge/gitstore/branch.py:1-90`; `src/lodge/gitstore/published.py`; `src/lodge/gitstore/accepted.py`; `src/lodge/gitstore/settings.py:1-80`; `tests/app/test_identical_reads.py`; `tests/core/test_identical_change.py`; the diff of `tests/core/test_linear_derive.py`; `tests/app/support.py:22-29`; `tests/app/fakes.py` (the `staged` lines); `tests/core/test_check_change.py` (its test names).

## Files not read

`lodge spec` as a whole; the plan's Tasks 2, 3, and 5 to 12 in full; `src/lodge/app/threads.py` and `writes.py` beyond the lines that call `check_change` (they load the published tree themselves and do not go through the shortcut); `src/lodge/core/derive.py`; `tests/core/checks.py`, `builders.py`, `samples.py` beyond their names; `scripts/bench_reads.py`.
