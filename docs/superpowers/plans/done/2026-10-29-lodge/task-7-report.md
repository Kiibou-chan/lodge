# Task 7 report: feedback on writes, and applying drafts

Status: DONE_WITH_CONCERNS.

## Built

- `src/lodge/core/feedback.py` (107 lines): `Feedback(record_id, message)` and `feedback(added, after, d, length)`.
- `src/lodge/core/apply.py` (217 lines): `Applied(files, ids)`, `StaleBase` (a `Problem` subclass), and `apply_drafts(current, tree, drafts, new_decision_ids, date, importing)`.
- Exported through `lodge.core`: `Feedback`, `feedback`, `Applied`, `StaleBase`, `apply_drafts`.
- Tests: `tests/core/test_feedback.py` (18), `tests/core/test_apply.py` (13), `tests/core/test_apply_refusals.py` (14), shared helpers in `tests/core/applying.py`; `tests/core/builders.py` gains `tree_of`.
- The existing file writers do all serialising (`write_record`, `write_area`); `record_from_draft` builds every record and turns format errors into problems.

## Test-first evidence

Both new test files first failed at collection, before any implementation existed:

- `ImportError: cannot import name 'Feedback' from 'lodge.core'` (test_feedback.py).
- `ImportError` for `Applied`, `apply_drafts` (test_apply.py).

After the first implementation, 6 apply tests failed from test mistakes only (a string `scope`, a bare `"x"` path to `parse_area`, an area folder missing from a path); fixed in the tests.
`test_words_split_on_whitespace` had a miscount in the test (5 words, not 6); fixed.

## Behaviour worth knowing

- Feedback messages are my wording; the brief fixes the rules, not the text (all in `feedback.py`, one test each).
- Number rule: decisions only (an entry has no `numbers` key to satisfy it); the brief's `\s?%?` is written `(?:\s?%)?` so a bare number does not swallow a following space; hidden before matching: backtick spans and fenced blocks, ISO dates, IDs, codes such as `ITEM-1`.
- Related rule runs when the decision has neither `replaces` nor `narrows`, through `related`; the flag rule reads `Derived.awaiting_author`.
- `apply_drafts` ID assignment: `new_decision_ids` sorted ascending, handed to id-less decision drafts in draft order (`test_new_ids_ascend_in_draft_order`).
- Written files: new and edited decisions and entries (edits keep their path), area drafts, and any area whose order gains a new entry or loses a retired one; an untouched area is not written (`test_untouched_area_not_written`).
- New entries are appended to the order only when the area draft does not already list them.
- Problems name the draft's `source`, all with check 1; they are collected across all drafts, none stops the others.

## Concerns

1. `StaleBase` subclass of `Problem`: Task 8 needs to tell a stale base (`Conflict`, exit 1) from other problems (`LodgeError`, exit 2); `isinstance(p, StaleBase)` does that.
2. An edit draft (existing ID) without `base` is a problem (not in the brief): otherwise an edit could overwrite a concurrent change unseen.
3. `imported_from` outside `--import` is refused for new records, and for an edit only when the draft changes the record's `imported_from`; the literal rule would forbid editing any imported entry, since `lodge draft` prints its `imported_from`.
4. `apply_drafts` raises `ValueError` when `len(new_decision_ids)` differs from the number of id-less decision drafts; Task 8's `add` must mint exactly that many (`kind == "decision"` and no `id` key).
5. `Applied.ids` lists decisions and entries in draft order, including edited ones; area drafts have no ID and are not listed.

## Fix round 1

Each fixed finding had its test fail first (the new tests failed against the unchanged code: the `TypeError` for I1, the old messages for the wording ones); check 5 is untouched and no dry run is built (Task 8).

- I1: only string area names are collected, so `name: [storage]` and `name: {a: b}` reach `record_from_draft` and become problem 1; `test_area_name_not_a_string_is_problem`.
- I2: the related and numbers messages now name the remedy as a change to the draft before it is added ("If so, set replaces or narrows in the draft before adding it"; "before adding the draft, give each one as `numbers: ...`"); one test pins each text.
- M1: only codes held by a record of the after state are hidden, compared case-insensitively; `test_number_in_a_word_that_is_not_a_code_is_flagged` (`top-10` and `Python-3` flagged) and the `item-1` case.
- M2: an entry created and retired in one add stays out of the area order; `test_entry_created_and_retired_in_one_add_not_in_order`.
- M3: `base` on a draft that creates a decision, an entry, or an area is refused, naming what does not exist; three tests.
- M4: the related message names both IDs ("does d-cccccc replace or narrow d-aaaaaa?", plural "any of them"); the two related tests pin it.
- M5: the numbers message shows the handle shape and "a record and key or a runnable command"; `test_number_without_handle`.
- M6: the stale-base message ends "make the change on that print, and add it"; `test_stale_base_message_says_to_redo_the_change`.
- M7: an edit that changes `imported_from` gets "this draft changes imported_from of <id>; keep it as lodge draft printed it", for entries and decisions; two tests.
- M8: a wrong-shape `id` ("id 'S-BBBBBB' is not a specification entry ID; IDs are lower case, like s-4kq1zm", also for an ID of the other kind or an empty one) and a non-string `area` ("area must be one name, not ['storage']") have their own messages; `test_id_of_the_wrong_shape_says_so`, `test_area_of_the_wrong_shape_says_so`.
- M9: the `isinstance(d, Decision)` assertion in `test_one_call_covers_every_added_record` is gone.
- M10 and M11: not in this round (ledger; Task 8's brief).
