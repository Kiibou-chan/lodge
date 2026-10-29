### Task 5: The check

**Files:**
- Create: `src/lodge/core/check_state.py`, `src/lodge/core/check_change.py`
- Test: `tests/core/test_check_state.py`, `tests/core/test_check_change.py`

**Interfaces:**
- Consumes: Tasks 3 and 4.
- Produces:
  ```python
  @dataclass(frozen=True) class CheckResult: problems: tuple[Problem, ...]; notes: tuple[str, ...]
      @property def ok(self) -> bool
  def check_state(s: Snapshot) -> CheckResult                                   # 1, 2, 3, 7
  def check_change(published: Snapshot, after: Snapshot, settings: CoreSettings) -> CheckResult
  ```
- `check_change` reports every problem of 4, 5, 6 and those of 1, 2, 3, 7 that `after` has and `published` has not (compared by path, check, and message); problems already published become notes.
- Readings of the spec's checks:
  - 1: parse problems; `kind` matching the ID prefix; the file name starting with the ID; a new non-imported decision dated no later than a published decision it links to or shares an entry with.
  - 2: every ID in `changes`, `replaces`, `narrows`, `confirms` resolves to a record of the right kind; no two records share an ID, nor a code compared case-insensitively; every listed attachment exists; no published record ID is missing from `after`.
  - 3: an author decision without a quote, or with an empty `where` or `when`, unless imported; `confirms` on a non-author decision.
  - 4: for each entry ID new, changed in text, or newly retired, a decision new in this change lists it with `create`, `edit`, or `retire` respectively; imported entries exempt; a new imported record whose `imported_from.file` is not in `settings.import_sources`.
  - 5: a published decision whose header differs in any key; an author decision whose reasoning differs; an agent decision whose reasoning grew in words. An agent decision whose reasoning shrank is a note naming it.
  - 6: a record new in this change whose `narrows` or `confirms` names a decision replaced in `published`, or whose `changes` names an entry retired in `published` with an action other than `retire`; `replaces` is never a problem here.
  - 7: each area's `order` lists exactly the current entries of its folder, each once; every folder with entries has `_area.md`. A changed area title, intro, or order is a note.
- One problem per offending item (one per missing area-order entry, one per unresolved link), so a published problem's message stays stable when another one joins it. Messages name the record ID and the field, for example `d-3m8qk2: replaces d-8rw0te, which does not exist`.

- [ ] **Step 1: Write failing tests**, one minimal pair per rule above (a passing state and the same state with one defect), named `test_check_<n>_<defect>`, plus `test_clean_change_passes`, `test_replacing_a_decision_passes_check_6`, `test_published_problem_is_note_not_failure`, `test_shrunk_agent_reasoning_is_note`, `test_author_reasoning_edit_fails`, `test_area_intro_change_is_note`.
- [ ] **Step 2: Run**; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check.sh`; expected: green.
- [ ] **Step 5: Commit and push.**


## Carried from Task 4 (ledger `Ruling: I2,`)

- Check 1 also reports a new imported decision whose `changes` names an entry that a published non-imported decision already changed: `d-xxxxxx: imported, changes s-yyyyyy, which a live decision already changed`.
  Test: `test_check_1_import_changes_entry_changed_live`, plus the passing pair (an import changing an entry only imports changed).
