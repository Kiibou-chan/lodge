### Task 7: Feedback on writes, and applying drafts

**Files:**
- Create: `src/lodge/core/feedback.py`, `src/lodge/core/apply.py`
- Test: `tests/core/test_feedback.py`, `tests/core/test_apply.py`

**Interfaces:**
- Consumes: Tasks 3, 4, 6.
- Produces:
  ```python
  @dataclass(frozen=True) class Feedback: record_id: str; message: str
  def feedback(added: Sequence[Record], after: Snapshot, d: Derived, length: LengthGuidance) -> list[Feedback]
  @dataclass(frozen=True) class Applied: files: dict[str, str]; ids: tuple[str, ...]
  def apply_drafts(current: Snapshot, tree: Tree, drafts: Sequence[Draft], new_decision_ids: Sequence[str],
                   date: str, importing: bool) -> Applied | list[Problem]
  ```
- `feedback` rules: title over `title_chars`; statement over its kind's word guidance; reasoning over `reasoning_words`; a decision with neither `replaces` nor `narrows` while `related` finds any, listing them with titles and asking whether it replaces or narrows one; a number token (`\b\d+(?:[.,]\d+)*\s?%?`) outside backticks while `numbers` is empty, ignoring IDs, codes, and ISO dates; a decision `derive` flags, saying it will wait for the author. Words split on whitespace.
- `apply_drafts` returns only the files to write: new decisions (ID and date filled), new and edited entries at their fixed paths, area files (new from area drafts; existing ones with new entries appended to `order` and retired entries removed). A decision draft with an existing ID is an edit of that decision, judged by check 5 (only an agent decision's reasoning may shrink); a new decision draft carries no ID. Problems, each naming the draft's source: a decision draft whose ID does not exist; a draft with `imported_from` when not `importing`; a new non-imported decision draft with `date` (an edit draft from `lodge draft` keeps the published `date`, and check 5 judges it); an entry statement containing a line `## Reasoning`; an edit whose `base` differs from `content_hash` of the file in `tree` (message names both); a new entry in an area that neither exists nor has an area draft; a new entry without `area`; an entry draft whose ID exists but whose `area` differs.

- [ ] **Step 1: Write failing tests:** one per feedback rule with its exact message, `test_clean_decision_no_feedback`, `test_numbers_in_backticks_ignored`, `test_feedback_on_decision_with_changes_and_related`; for `apply_drafts`: `test_new_decision_and_entry_and_area`, `test_edit_keeps_path_even_if_title_changes`, `test_stale_base_is_problem_naming_both`, `test_retire_removes_from_order`, `test_import_needs_flag`, `test_date_in_new_draft_refused`, `test_decision_reasoning_edit_keeps_date_and_passes`, `test_entry_statement_with_reasoning_heading_refused`, `test_entry_without_area_refused`, `test_area_change_refused`.
- [ ] **Step 2: Run**; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check.sh`; expected: green.
- [ ] **Step 5: Commit and push.**


## Carried from Tasks 4 and 5 (ledger)

- Task 4 M2 and N2: `derive` orders decisions by date, then ID, and every new decision of one add has the same `date`.
  `apply_drafts` therefore assigns `new_decision_ids` in ascending order to the new decision drafts in draft order, so decisions of one add order as written.
  Test: `test_new_ids_ascend_in_draft_order` (pass the IDs unsorted; the first draft gets the smallest).
- Task 5 ruling: check 7 wants the area order to list exactly the current entries, so a retirement removes the entry from its area's `order` in the same change (already in this brief).
