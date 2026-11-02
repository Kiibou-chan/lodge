# Review of Tasks 7b and 8a

Reviewer: `reviewer` agent (Opus), task review, three passes in order.
Task 7b: `git diff 0d1c6c5 48e4a51 -- ts/` on `server-core-t7b`.
Task 8a: `git diff 0d1c6c5 b5f9f0b -- ts/` on `server-core`.
Merge: 632c9eb on `server-core`.
Probes ran in a detached scratch worktree at 632c9eb, removed afterwards; probe scripts are outside the repository.
Already ruled and not raised again: d-p48gr1, d-fbhdvf, d-g1hrmn, d-4m6m35, d-0q54zn, d-f18pz7, d-442r2f.

## Counts

| Task | Blocking | Important | Minor |
|---|---|---|---|
| 7b | 0 | 0 | 2 |
| 8a | 0 | 1 | 3 |

## Pass 1: correctness

No correctness finding in either task.
The evidence follows, so that the recheck can rerun it.

### Carried tests against the Python ones (Review Focus 1)

Every test of `test_confirmation.py` (8 functions, 9 cases), `test_order.py` (13), and `test_check_state.py` (27 functions, 39 cases) is carried by name, with every parametrised case.
The one-parameter lists go through `.map((c) => [c])` (`confirmation.test.ts:116`, `check-state.test.ts:151`, `:163`, `:176`, `:198`), so `[]` reaches `confirmation_draft_without_area_requires_one_id` whole; the two-parameter `check_2_unresolved_link` is `test.each([[a, b], …])` with `%p %p` (`check-state.test.ts:69-78`).
Each `pytest.raises(ValueError, match="one decision")` is `toThrow(ValueError)` and `toThrow(/one decision/u)` (`confirmation.test.ts:120-121`).
`isinstance(draft, Draft)` and `isinstance(made, Decision)` became `kind` checks; every `==` became `toEqual` or `toBe` on the whole value; no `toContain` stands for a whole-value comparison.
Run: `bun test tests/core/confirmation.test.ts tests/core/order.test.ts tests/core/check-state.test.ts tests/parity.test.ts` at 632c9eb, `74 pass, 0 fail`.

### Targeted mutations (d-mfayy5, `task-5b-review.md` C-1)

Each mutation applied alone in the scratch worktree, run against the task's test files, reverted.
Earlier tasks' code that the carried tests observe:

| Mutation | Fails |
|---|---|
| `snapshot.ts:87-88` duplicate-ID problems as check 1 | `check_2_duplicate_id_from_load_is_reported` |
| `snapshot.ts:87` only one of the two duplicate-ID problems | `check_2_duplicate_id_from_load_is_reported` |
| `derive-review.ts:5` `isAuthor` ignores case | `check_3_author_lookalike` "Author" and "AUTHOR" |
| `derive.ts:109` retired entries read as current | `check_7_order_lists_a_retired_entry`, `retired_target_does_not_hold_an_entry_back` |
| `fileformat.ts:66` `_area.md` to `area.md` | `check_7_folder_with_entries_has_no_area_file` |

The 8a report's own mutations were in `check-state.ts` (the problem spread dropped, `checkCycles` dropped, `casefold` swapped), targeted rather than whole-function throws; the table above adds the earlier-code side.
New code, 7b: 15 targeted mutations of `confirmation.ts` and `order.ts` (creator test dropped, last-changer test widened, ID tie-break dropped, date order dropped, confirmed or replaced kept, Oxford comma dropped, `VIEWER` replaced, unranked first, retired kept in the written order, depth fixed at 1, dependant test dropped, ancestors ignored) each fail a carried test.
One survives: `order.ts:89` `seen ? [] :` removed, which the Python suite also lets through in `test_order.py` and catches only in `tests/viewer/test_pages_fix_round.py::test_rests_on_tree_expands_a_shared_dependency_once`; not a weakening by the port.
New code, 8a: the prefix test of check 1, the per-link set of check 2, the imported exemption of check 3, the twice-listed count and the missing entry's path of check 7, the self-cycle of check 8, and `ok` each fail a carried or added test.
Survivors are listed under 8a-D-2; each has the same survivor in `test_check_state.py`.
Two more survive `check-state.test.ts` and are caught by Python tests that later tasks carry: threads left out of check 1 (`check-state.ts:31`, caught by `tests/core/test_check_threads.py::test_file_name_must_start_with_the_id`) and the mutual reach of check 8 (8a-P-2).

### Python against TypeScript on this repository's records and edited variants

A Python script read the 361 files under `lodge/` at 632c9eb into `Tree`s: the store as it is, and ten variants edited through `write_record` and `write_area` (a misnamed decision file; an entry resting on itself, on a missing ID, twice on one target, a two-entry and a three-entry cycle across areas; a diamond with a cross-area target; a code shared without regard to case; an order with a duplicate, a missing ID, an entry of another area, and one dropped; an area file deleted; `decided_by` lookalikes, a non-author `confirms`, self and missing `replaces` and `narrows`, a quote `where` of a blank; attachments listed twice, one present and one elsewhere; a duplicate ID and an unclosed header; a retirement, an author confirmation of four decisions, and a replacement).
For each, both cores gave `area_names`, `written_order` and `derived_order` (ID, depth, under) of every area, `confirmable_ids`, `behind_area` of every area, `rests_on_tree` of every entry, `check_state` (path, check, message, line, notes, ok), and `confirmation_draft` for every area's list and three single IDs, with words holding a tab, a newline, `é`, and `𝔘`.
All 11 states agree on every key (170 confirmable IDs and 54 behind-area entries in the store; up to 7 problems a variant over checks 1, 2, 3, 7, and 8), except one parse problem's PyYAML message in the variant with an unclosed header, which is ruling d-p48gr1.
`confirmation_draft`'s refusals agree on U+0001, U+0085, U+2028, U+D800, U+007F, a newline in `when`, and pass U+FEFF, CRLF, and a tab in the words, each as `ValueError` with Python's message.

### Stamps (Review Focus 4)

`behindArea` over five decisions dated with the offsets `+01:00`, `+00:00`, `-00:45`, `+14:00`, and `+23:59`, two of them the same instant, gives Python's order, the same-instant pair by ID, under `TZ` set to UTC, Pacific/Kiritimati, America/Adak, and Asia/Kathmandu.

### Purity (Review Focus 5)

The five new modules use no `Date`, `process`, randomness, console, or timer (`grep` over `ts/src/core/confirmation.ts`, `order.ts`, `check-*.ts`), and take no default parameter or module constant from the environment; `MINUTE_FORMAT` is a format text, not a time (see 7b-D-1).

### The merge at 632c9eb

`git diff 0d1c6c5 632c9eb -- ts/src/core/index.ts ts/knip.json ts/tests/parity.json`: `index.ts` exports both lanes' names; `knip.json`'s `entry` lost `src/core/derive.ts` (7b) and gained `src/core/check-state.ts` and `tests/core/checks.ts` (8a); `parity.json` flips `test_check_state.py`, `test_confirmation.py`, and `test_order.py`, and leaves `checks.py` planned for 8b, as the brief says.

## Pass 2: practice

### 7b-P-1 · Minor · the added IndexError test does not assert the base class it exists for

Handle: `ts/tests/core/confirmation.test.ts:124-133`; `ts/src/core/confirmation.ts:8-10,52`.
The private `IndexError` extends `LookupError` so that a port of an `except LookupError` catches it as Python's would, but the test asserts only `toBeInstanceOf(Error)`, `name`, and `message` through a try and a sentinel throw.
Failure: `IndexError` changed to extend `Error` passes the test.
The path is unreachable from lodge 0.2's only caller, which refuses an empty list first (`src/lodge/app/confirm.py:64`), so the test pins Python's behaviour rather than a use.
Fix: `const call = () => confirmationDraft([], Scope.PRODUCT, "Read.", "now", "storage"); expect(call).toThrow(LookupError); expect(call).toThrow("list index out of range");`.

### 8a-P-1 · Minor · `oldDecision` casts where Python asserts

Handle: `ts/tests/core/checks.ts:23-25` against `tests/core/checks.py:42-45`.
Python's `assert isinstance(old, Decision)` fails loudly if `base_items` changes order; `baseItems()[2] as Decision` hands back an area or an entry silently.
Failure: a reorder of `baseItems` makes Task 8b's tests that read `oldDecision()` fail far from the cause, or pass on the wrong record.
Fix: `const old = baseItems()[2]; if (old?.kind !== "decision") throw new Error("expected Decision"); return old;`.

### 8a-P-2 · Minor · the added check 8 test duplicates Task 8c's carried tests

Handle: `ts/tests/core/check-state.test.ts:259-271`; `tests/core/test_check_links.py:64-85` (Task 8c, `parity.json:136-141`).
The added test asserts the two-entry cycle, the self link, and the missing target, which `test_two_entry_cycle_fails_check_8_on_both`, `test_rests_on_itself_fails_check_2`, and `test_unknown_rests_on_fails_check_2` carry in 8c; it is the only check 8 test until then, and it does not catch the mutual-reach mutation (`check-cycles.ts:61`, `&& reach.get(t)?.has(id)` dropped), which `test_three_entry_cycle_names_the_other_two` does in Python.
Failure: after 8c the same behaviour is pinned twice in two files, and a change to the message is edited in both.
Fix: Task 8c's brief deletes this test when it carries `test_check_links.py`; park until then.

## Pass 3: design

### 8a-D-1 · Important · `CheckResult.ok` is a stored field that later constructors must derive by hand

Handle: `ts/src/core/check-state.ts:7-11` (`readonly ok: boolean` on the interface) and `:147-153` (a getter on an object literal); the plan's Types rule (brief, Global Constraints) covers fields with defaults, not a `@property` (`src/lodge/core/check_state.py:20-22`).
Python's `ok` is computed from `problems` and cannot disagree with them; six places build a `CheckResult` (`src/lodge/core/check_change.py:52`, `src/lodge/app/state.py:69`, `src/lodge/app/reads.py:96`, `tests/core/test_views.py:132,148`, `tests/viewer/test_pages.py:167,171`, `tests/app/test_thread_fix_paths.py:46`), and in TypeScript each must write `ok` itself.
Failure, run in the scratch worktree: `const widened = { ...checkState(snapshotOf([])), problems: [problem({ path: "lodge/x.md", check: 2, message: "x" })] }` gives `widened.ok === true` with one problem, since the spread copies the getter's value as a data property; a hand-written `{ problems, notes, ok: … }` in Task 8b's `checkChange` or plan 2's `app` can likewise disagree, and `lodge check` would print `ok` and exit 0 over a failing store (`src/lodge/cli/commands.py:112`).
Task 8b, now in build, is the first other constructor.
Fix: a `checkResult(problems, notes)` beside the interface in `check-state.ts`, returning `{ problems, notes, ok: problems.length === 0 }` as plain data, used by `checkState` and by every later constructor, with the getter dropped; or a coordinator ruling that names another shape before 8b's `checkChange` is written.

### 8a-D-2 · Minor · the problem order and two de-duplications are pinned by no test, here or in Python, and Task 12 does not reach them

Handle: `ts/src/core/check-state.ts:142-146` (the sort), `:43` (`new Set(e?.restsOn)`), `:85` (`new Set(d.attachments)`); Task 12's `problems` key (plan, Task 12).
Mutations that survive every test of `ts/tests/core` touching them, each with its Python twin surviving all 1258 non-e2e Python tests (`uv run pytest -q tests -k "not e2e"`): the sort removed (`check-state.ts:142`, Python `check_state.py:37`), the path or the check number dropped from the comparison, the set over `restsOn` dropped (Python `:77`), and the set over `attachments` dropped (Python `:114`).
Task 12 compares `check_state`'s problems sorted, on this repository's store, which has none (the probe's unedited state: 0 problems), so it checks neither.
Failure: a later fix round replaces `byCodePoint` with `<` or drops the sort, or iterates `restsOn` without the set, and `lodge check` lists problems in another order than 0.2, or twice for a repeated link, with every gate green.
The probe above found today's code in agreement on the edited variants, so this is a guard for later rounds, not a present defect.
Fix: one new test (not carried, so it is seen failing against the sort removed) in a second file beside `check-state.test.ts` (which is at 281 lines), listed with it in `parity.json`, asserting the whole problem list for a state with problems on two paths and two check numbers, an entry resting twice on a missing ID, and a decision listing a missing attachment twice; or Task 12's dump gives the problems unsorted for a seeded variant as well as for the store.

### 7b-D-1 · Minor · `MINUTE_FORMAT` is a `strftime` pattern that no TypeScript code can apply

Handle: `ts/src/core/confirmation.ts:13`; its only Python readers, `src/lodge/app/confirm.py:74` and `src/lodge/app/threads.py:35`, call `w.clock.now().strftime(core.MINUTE_FORMAT)`.
JavaScript has no `strftime`, and `core` takes times as ISO stamps (Global Constraints, Times), so plan 2's port of `app/confirm.py` cannot use the constant as Python does.
Failure: a plan 2 builder formats the minute from a `Date` with local getters, and the quote's `when` changes with the machine's `TZ` (Review Focus 4), where lodge 0.2 writes it in the clock's offset.
Fix: plan 2's brief for `app/confirm.py` and `app/threads.py` says how the minute is formed from the clock's stamp (its first 10 characters, a space, then characters 11 to 16, in the stamp's own offset), keeping `MINUTE_FORMAT` exported for the `__all__` check of Task 11.

## Files read

- `CLAUDE.md`; `docs/superpowers/plans/2026-11-02-lodge-server-core.md` (Review Focus, Task 8a interfaces, Task 12); `task-7b-brief.md`, `task-8a-brief.md`, `task-7b-report.md`, `task-8a-report.md`, `task-5b-review.md` (C-1); `task-8b-brief.md` (searched for `CheckResult`, no hit).
- Decisions through `lodge show`: d-p48gr1, d-fbhdvf, d-g1hrmn, d-4m6m35, d-0q54zn, d-f18pz7, d-442r2f; `lodge search` for YAML messages.
- Python: `src/lodge/core/confirmation.py`, `order.py`, `check_state.py`, `check_areas.py`, `check_cycles.py`; `tests/core/test_confirmation.py`, `test_order.py`, `test_check_state.py`, `checks.py`; `src/lodge/app/confirm.py:40-80`, `src/lodge/app/state.py:60-80`, `src/lodge/app/reads.py:85-97`; parts of `snapshot.py`, `model.py`, `fields.py`, `derive.py`, `builders.py`, `test_check_links.py` (names).
- TypeScript at 632c9eb: `ts/src/core/confirmation.ts`, `order.ts`, `check-state.ts`, `check-areas.ts`, `check-cycles.ts`; `ts/tests/core/confirmation.test.ts`, `order.test.ts`, `check-state.test.ts`, `checks.ts`; the diffs of `index.ts`, `knip.json`, `parity.json`; parts of `derive.ts`, `derive-review.ts`, `snapshot.ts`, `stamps.ts`, `model.ts`, `fileformat.ts`.

## Files not read

- The Codex transcripts `task-7b-codex-final.txt` and `task-8a-codex-final.txt`.
- `ts/src/core/text.ts`, `yamlio.ts`, `drafts.ts`, and `ts/tests/core/builders.ts` beyond the calls the probes made through them.
- The rest of the plan, the probes folder, and the earlier reviews other than `task-5b-review.md`.
- I did not run `sh scripts/check.sh` or `sh scripts/check-ts.sh`; the dispatch reports the gate green at 632c9eb, and I ran only the four test files named above.
