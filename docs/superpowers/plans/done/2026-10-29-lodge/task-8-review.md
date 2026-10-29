# Task 8 review: the application layer

Reviewed: `build-0.1` at f3e4ea1 against BASE 7bd7106 (b1ef630 adds only ledger lines).
Verdicts: spec compliance yes, with the gap in I1; task quality not approved until I1 is fixed.
Counts: 0 Blocking, 1 Important, 7 Minor.

## What I ran

- A scratch copy from `git archive f3e4ea1`; `uv run pytest -q tests/app`: 40 passed; `sh scripts/check.sh` on the clean copy: green, 674 passed.
- Probes against the builder's fakes, in `scratchpad/probes-t8/src/tests/app/test_probes_t8.py`, `test_probes_t8b.py`, and `test_probes_t8c.py`; output in `scratchpad/probes-t8/probes-run1.txt` to `probes-run3.txt`.
- Run with `uv run pytest -q -s tests/app/test_probes_t8*.py -p no:cacheprovider` from the scratch copy.

Probe results for the cases the dispatch named:

| Probe | Scenario | Result |
|---|---|---|
| p1 | another entry in the same area lands between `trees()` and `publish` | retried, published; order `s-aaaaaa, s-cccccc, s-bbbbbb`; `check_state` clean; gate against the old published state clean |
| p2 | an edit of the same entry lands between the reads | `Conflict` (exit 1), both bases named, nothing published |
| p3 | the area file's intro is edited between the reads | retried; their intro kept, our entry appended to the order; clean |
| p4 | another decision replacing `d-aaaaaa` lands while ours replaces it | retried and published; `replaced_by[d-aaaaaa] = (d-222222, d-cccccc)`; no feedback about the race (Minor M5) |
| p4b | the same, sequentially | identical outcome, so the retry adds nothing the sequential case lacks |
| p5 | rejection on every attempt | `Conflict` after three attempts, no publish |
| p6 | staged mode, two successive edits, then reuse of the first print | both `STAGED`; the reuse is a `Conflict`; the gate against published is clean |
| p7 | dry run whose check fails | `CHECK_FAILED`, `attempts == 0` |
| p8 | draft set failing to parse midway (two bad of four), and failing to apply midway | one `LodgeError` naming both bad files with lines; apply failure is a `LodgeError`; `attempts == 0` both times |
| p9 | a rejection lands a decision with our code, then the retry's check fails | `CHECK_FAILED` with both check 2 problems, no publish |
| p10 | `id:` and `id: null` in a decision or entry draft | `LodgeError` naming the ID; no `ValueError` from `apply_drafts` (the header loader keeps them as strings) |
| p11 | `show` and `draft` of a record whose file no longer parses | `LodgeError: no record named d-aaaaaa` (I1) |
| p12, p17, p18 | malformed, naive, and date-only dates in a stored decision | the loader refuses or normalises them, so `_newest_first`'s `fromisoformat` never sees a naive date; no escape |
| p13 | odd refs (`""`, `area:`, `d-`), `spec` of an area with entries but no file, `timeline(-1)` | `LodgeError` each; spec renders; `timeline(-1)` drops the last item (M3) |
| p14 | two adds both create area `storage` | the retry refuses with `LodgeError` exit 2, not `Conflict` (M4) |
| p15 | CRLF record file drafted and edited | published |
| p16 | staged mode, store moves after the read | retried, `STAGED` |
| p19 | self-replacement, cycles, dangling links, an entry without an area file, through every read and the gate | no exception escapes |

The invariant holds by construction and in every probe: `_attempt` publishes only when `check_change(load(state.published), after, ...)` passed, with `after` built from `state.current` of the same `read_state` call and `state.current` passed as the publish base (`src/lodge/app/writes.py:48-70`).
No exception other than `LodgeError` or `Conflict` escaped any probe; the one traceback in run 3 is my probe calling `.id` on an `Area`.

## Pass 1: correctness

### I1 (Important): an unreadable record is reported as one that does not exist

`src/lodge/app/state.py:64-65` raises `LodgeError(f"no record named {ref}")` without the snapshot's unrecorded problems, and the error path carries no `Read`, so Task 10 has nothing to print above it.
Scenario (p11): an agent breaks the YAML of `d-aaaaaa`'s header by hand; `lodge show d-aaaaaa` and `lodge draft d-aaaaaa` both say "no record named d-aaaaaa", while `search` on the same state lists the file in `Read.unrecorded`.
The agent concludes the decision does not exist and may draft a new one; that is must-not 1 (wrong information), and the brief's "files that fail to parse are never silent" is broken on exactly the read that names the file.
The same holds for `spec(area)` (`src/lodge/app/reads.py:58-59`) and `draft("area:x")` (`reads.py:81-82`) when the area's `_area.md` is the unreadable file.
Fix: when a reference or area is not found and `state.read.unrecorded` is not empty, add to the message the paths lodge could not read, for example "no record named d-aaaaaa; lodge could not read lodge/decisions/d-aaaaaa-keep-whole-transcripts.md, which may hold it" (filter to paths containing the lower-cased ref when one does, else list them all); one test per site, parametrised like `test_unparsable_file_reported_by_every_read`.

## Pass 2: practice

### M1 (Minor): one test name differs from the brief

The brief names `test_draft_prints_file_with_base`; the test is `test_draft_prints_the_file_with_its_base` (`tests/app/test_reads.py:146`), and the report says every brief name exists.
Scenario: a ledger or final-review grep for the brief's names misses it.
Fix: rename to the brief's name.

### M2 (Minor): the area path is spelt out a second time

`src/lodge/app/reads.py:83` builds `f"lodge/spec/{name}/_area.md"` by hand, while `lodge.core.area_path` (`src/lodge/core/fileformat.py:78`) is the one definition the store and `apply_drafts` use.
Scenario: a layout change in `area_path` leaves `draft area:x` raising `KeyError` on `state.current.files[path]` (an escape, not a `LodgeError`).
Fix: `path = area_path(name)`.

### M3 (Minor): a negative timeline limit silently drops the oldest decisions

`src/lodge/app/reads.py:52` slices `[:limit]`; `timeline(-1)` returns all but the oldest (p13, an empty list for a one-decision store).
Scenario: a viewer query string or a CLI flag passes `-1` meaning "all" and the oldest decision vanishes without a word.
Fix: `LodgeError` for `limit < 0` (or treat it as no limit), with a test; or have Task 10 and 11 reject it, recorded as a ruling.

## Pass 3: design

### M4 (Minor): a race on creating the same area ends as a usage error

When another add creates area `storage` between our reads, the retry's `apply_drafts` sees an existing area and refuses our area draft for lacking `base` (`src/lodge/core/apply.py:192-196`, reached from `writes.py:57-58`), which `_refusal` turns into `LodgeError` exit 2 (p14).
Scenario: a script treating exit 1 as "retry after re-reading" and exit 2 as "fix your input" files this concurrency outcome as bad input.
Fix: in `_attempt`, on a retry (not the first attempt), turn the refusal into `Conflict` when the area or entry it names did not exist in the first attempt's snapshot; or accept it as is with a ruling, since the message's remedy (print the area draft and add again) is right.

### M5 (Minor, spec level): replacing a decision another add has just replaced gives no feedback

p4 and p4b: our decision `replaces: [d-aaaaaa]` publishes beside a concurrent (or earlier) `d-cccccc` that also replaces it, leaving two current decisions both replacing `d-aaaaaa`, with no note.
Check 6 allows it ("other than through `replaces`", spec, Writing), so this is not a Task 8 defect and the retry adds nothing the sequential case lacks; I record it because the dispatch asked for this probe.
Fix, if wanted: a feedback line in `core.feedback` (Task 7's module), "d-aaaaaa is already replaced by d-cccccc", parked for the final wave or the author.

### M6 (Minor): the `publish` docstring promises more than the plan's checkout mode does

`src/lodge/app/ports.py:27` says REJECTED "when the store moved since `base` was read"; the plan's checkout mode rejects only when a path it writes changed (plan, "Calls made", Checkout mode; Task 9 interfaces).
Scenario: two sessions in one worktree each add a decision with code `ITEM-2` (different paths, no shared area file); both stage, the working tree fails check 2, and the app reported both checks clean.
The gate before push catches it, so nothing reaches the published state, but Task 9's builder reads the port docstring as the contract.
Fix: state the weaker contract in the docstring ("REJECTED when a path in `writes`, or the branch tip, no longer matches `base`"), so the port and the plan agree.

### M7 (Minor): a no-op edit publishes an empty change

`_attempt` publishes whenever the check passes, including when every written file equals its current text (an area draft or entry draft printed and added unchanged).
Scenario: in branch mode this creates a commit with an empty diff and the message "lodge: add s-aaaaaa ..."; in checkout mode a no-op stage.
Fix: drop writes equal to `state.current.files.get(path)` before publishing, and return `PUBLISHED` (or a note) without calling `publish` when none remain; low priority.

## Rulings in the ledger

Ruling 110 (core names reached as `core.<name>`) stands: `tests/structure_imports.py` reads `from lodge.core import derive` as the submodule, and the alternative is the author's call.
Ruling 111 stands: fresh IDs on each attempt are needed, since a concurrent writer may take an ID the first attempt minted, and `writes.py:52-53` mints against the fresh snapshot; `core_settings` in `errors.py` is a small placement oddity, not worth a change.

## Brief items checked

- Every brief and carried test exists (one renamed, M1); the carried items hold: one `clock.now()` per attempt used for date and `now` (`writes.py:50,55,62`), exactly as many IDs as `apply_drafts` counts (`writes.py:52`, same predicate as `apply.py:54`), `StaleBase` to `Conflict` (`writes.py:90-91`), feedback skipping edited decisions (`writes.py:102-110`), `dry_run` and `DRY_RUN` (`writes.py:68-69`, `results.py:13`).
- Review Focus 1 (app half) and 4 hold in p1 and p2; Focus 3 in `test_show_resolves_code_and_levels`.
- Structure: `lodge.py` only delegates; `reads.py` 99 lines, `writes.py` 116; no clock or randomness read outside the ports.

## Files read

Read: `src/lodge/app/{__init__,errors,lodge,ports,reads,results,state,writes}.py`; `tests/app/{fakes,support,conftest,test_reads,test_writes,test_writes_retry}.py`; `src/lodge/core/apply.py`, `core/__init__.py`, and the parts of `core/drafts.py`, `core/fileformat.py`, and `core/snapshot.py` that `app` calls; `tests/core/applying.py` and the builders in `tests/core/builders.py`; the brief, the report, `CLAUDE.md`, the plan's Global Constraints, Calls made, Review Focus, and Task 9 text, the spec's Must nots, Writing, Storage, and Structure sections, and every `Ruling:` line in the ledger.
Not read: the review package diff line by line (I read the same files at f3e4ea1 instead, and b1ef630 touches only the ledger), `core/check_change.py`, `core/feedback.py`, `core/views.py`, `core/search.py`, and `tests/structure_imports.py` beyond what the probes exercised.
