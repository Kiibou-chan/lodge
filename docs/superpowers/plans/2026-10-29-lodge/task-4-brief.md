### Task 4: Snapshot and derived facts

**Files:**
- Create: `src/lodge/core/snapshot.py`, `src/lodge/core/derive.py`
- Test: `tests/core/builders.py` (`decision(**kw)`, `entry(**kw)`, `area(**kw)`, `files_of(*records) -> dict[str, str]`), `tests/core/test_snapshot.py`, `tests/core/test_derive.py`

**Interfaces:**
- Consumes: Task 3.
- Produces:
  ```python
  Files = Mapping[str, str]     # store-relative POSIX path -> text
  @dataclass(frozen=True) class Tree: rev: str | None; files: Files; attachments: frozenset[str]
  @dataclass(frozen=True) class Snapshot:
      decisions: Mapping[str, Decision]; entries: Mapping[str, SpecEntry]; areas: Mapping[str, Area]
      paths: Mapping[str, str]; problems: tuple[Problem, ...]; attachments: frozenset[str]
  def load(tree: Tree) -> Snapshot
  @dataclass(frozen=True) class Derived:
      status: Mapping[str, Literal["current", "replaced", "retired"]]
      replaced_by: Mapping[str, tuple[str, ...]]; narrowed_by: Mapping[str, tuple[str, ...]]
      changed_by: Mapping[str, tuple[str, ...]]          # entry id -> decision ids, newest first
      confirmed_by: Mapping[str, tuple[str, ...]]
      awaiting_author: frozenset[str]
      touched_by_flagged: Mapping[str, tuple[str, ...]]  # target id -> flagged decisions touching it
  def derive(s: Snapshot) -> Derived
  def is_author(d: Decision) -> bool      # decided_by == "author"
  ```
- `load`: a path under `lodge/` that is not `lodge/decisions/*.md`, `lodge/spec/*/*.md`, a `.gitkeep`, or under `lodge/attachments/` is problem 1; a second file with an ID already seen is problem 2 naming both paths, and the first is kept.
- Ordering: by date (all aware after Task 3), ties by ID.
- Flag: an agent decision D is flagged when it replaces or narrows an author decision, or changes an entry whose latest change ordered before D was an author decision; when D is imported, only author decisions that are not themselves imported count. D is unflagged once any author decision lists it in `confirms` or `replaces`.

- [ ] **Step 1: Write failing tests:** `test_load_keeps_good_records_beside_problems`, `test_duplicate_id_is_problem_2_with_both_paths`, `test_stray_file_is_problem_1`, `test_attachments_listed_not_parsed`, `test_replaced_and_successor`, `test_narrowed_stays_current`, `test_retired_entry`, `test_changed_by_newest_first`, `test_agent_replacing_author_flagged`, `test_agent_narrowing_author_flagged`, `test_agent_after_author_edit_flagged`, `test_agent_after_agent_edit_not_flagged`, `test_flag_clears_on_confirm`, `test_flag_clears_on_author_replace`, `test_flag_shows_on_targets`, `test_imported_touching_only_imported_not_flagged`, `test_imported_replacing_live_author_decision_flagged`.
- [ ] **Step 2: Run**; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check.sh`; expected: green.
- [ ] **Step 5: Commit and push.**

