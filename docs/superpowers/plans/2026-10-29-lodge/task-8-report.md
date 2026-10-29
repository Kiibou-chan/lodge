# Task 8 report: application operations and ports

Status: DONE_WITH_CONCERNS.

## Built

- `src/lodge/app/`: `ports.py` (`PublishOutcome`, `Store`, `Clock`, `IdSource`), `errors.py` (`LodgeError` exit 2, `Conflict` exit 1, `core_settings`), `results.py` (`AddOutcome` with `DRY_RUN`, `Read`, `Shown`, `Listed`, `Added`), `state.py` (`Wiring`, `State`, `read_state`, `resolve_ref`), `reads.py`, `writes.py`, `lodge.py` (delegation only), front door `__init__.py`.
- Tests: `tests/app/{fakes,support,conftest}.py`, `test_reads.py` (21 cases with parametrisation), `test_writes.py`, `test_writes_retry.py`: 40 tests; whole suite 674 passed, `sh scripts/check.sh` green.
- Every test name in the brief exists, plus `test_add_date_and_check_time_from_one_reading`, `test_feedback_skips_edited_decisions`, `test_dry_run_publishes_nothing`, `test_dry_run_reports_feedback_and_check`.

## Test-first evidence

Before any source existed, all three test files failed at collection: `ImportError: cannot import name 'PublishOutcome' from 'lodge.app'`.
Afterwards six tests failed from test mistakes (a name clash between my `START` decision and the clock's `START`, an area without its file, a missing entry in a store, two message wordings spelled in digits); fixed in the tests or the messages.
Two mutations, each caught: `_written` without the "not an edited decision" test (`test_feedback_skips_edited_decisions` fails); reading the clock a second time for `check_change` (`test_add_date_and_check_time_from_one_reading` fails).

## Behaviour worth knowing

- `Lodge.add`: one `clock.now()` per attempt, used as the decisions' date (`isoformat(timespec="seconds")`, so truncated) and as `check_change`'s `now`; IDs are minted again on every attempt (a retry's decisions have new IDs); a rejected publish re-reads the store, at most three attempts, then `Conflict`.
- `StaleBase` in any problem makes the whole refusal a `Conflict`; every message line is `<source>[:line]: <message>`, one line per problem.
- Commit message: `lodge: add <ids joined by ", "> <first record's title>`; an add of areas alone reads `lodge: add areas`.
- `feedback` gets new decisions and every written entry (edited or new), never an edited decision.
- `waiting()` lists the decisions in `Derived.awaiting_author`, newest first; `timeline(limit)` all decisions, newest first.
- `spec(area)` and `draft("area:x")` raise `LodgeError` for an area with no file and no entries (spec) or no file (draft); `draft` adds `base:` after the opening `---`, and `name:` for an area, which `apply_drafts` needs.
- `check(gate=True)` is `check_change(published, current, settings, clock.now())`; `problems()` is `check(gate=False)`.
- `core_settings(table)` wraps `parse_core_settings` so a `SettingsError` becomes a `LodgeError` (".lodge.toml: ..."); the brief lists SettingsError among the conversions and `Lodge` itself never sees one, so the conversion lives where the composition root can call it.

## Concerns

1. Name clash with the structure test: `check_change`, `check_state`, `derive`, `feedback`, and `search` are both core functions and core module names, and `tests/structure_imports.py` reads `from lodge.core import derive` as the submodule, "past the front door".
   `app` therefore does `from lodge import core` and calls `core.derive(...)` and so on for those five; the rule is untouched.
   `cli`, `viewer`, and `hook` will meet the same thing; renaming the five modules in `core` would end it, which is the author's call.
2. `tests/app/conftest.py` puts `tests/core` on `sys.path` so the app tests reuse `builders` and `applying`; without it `pytest tests/app` alone fails (collection order).
3. `MemoryStore` models rejection by revision (`Tree.rev`), as the real stores will; `Tree.rev` is therefore read in the tests too.

## Fix round 1

Each new test failed first (9 failures against the unchanged code; the retry-refusal guard test passed from the start); 684 passed after.

- I1: `state.not_found` appends "; lodge could not read <paths>, which may hold it" (paths containing the lower-cased reference, else all unreadable files) at `show`, `draft`, `spec(area)`, and `draft("area:x")`; one parametrised test per site, plus the list-all case.
- M1: test renamed `test_draft_prints_file_with_base`.
- M2: `draft` uses `area_path(name)`.
- M3: `timeline(limit < 0)` is a `LodgeError`; `test_timeline_refuses_a_negative_limit`.
- M4: `add` keeps the first attempt's snapshot; a refusal on a retry naming an area or entry absent from it but present now is a `Conflict`; two tests (the race, and a retry refusal of something already there staying exit 2).
- M5: parked.
- M6: the `publish` docstring says REJECTED when a path in `writes`, or the branch tip, no longer matches `base`.
- M7: writes equal to the current file are dropped; with none left `publish` is not called and the outcome is `PUBLISHED` with the note "nothing changed" (a dry run stays `DRY_RUN`, a failing check `CHECK_FAILED`); two tests.

## Fix round 2

Each new test failed first (7 failures); 688 passed after.

- R1: `_raced` uses a header value as a key only when it is a string, so `name: [a, b]`, `id: [s-bbbbbb]`, and `id: {x: 1}` are `LodgeError` exit 2; `test_unhashable_names_are_usage_errors`, one case per shape.
- R2: `not_found` names only check 1 problems (files that failed to read), so a missing `_area.md` is not called unreadable; `test_not_found_does_not_call_a_missing_file_unreadable`.
- R3: the guard test is renamed `test_refusal_on_the_first_attempt_is_a_usage_error` and asserts `attempts == 0`; a refusal that appears only on a retry over unchanged records is not constructed.
