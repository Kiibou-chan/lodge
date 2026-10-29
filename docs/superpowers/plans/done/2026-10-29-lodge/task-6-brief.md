### Task 6: Search, references, level views, and the readable specification

**Files:**
- Create: `src/lodge/core/search.py`, `src/lodge/core/views.py`, `src/lodge/core/render.py`
- Test: `tests/core/test_search.py`, `tests/core/test_views.py`, `tests/core/test_render.py`

**Interfaces:**
- Consumes: Tasks 3 to 5.
- Produces:
  ```python
  @dataclass(frozen=True) class Filters:
      kind: Literal["decision", "spec"] | None = None; scope: Scope | None = None
      status: Literal["current", "replaced", "retired", "any"] = "current"
      area: str | None = None; decided_by: str | None = None
  class AmbiguousRef(LookupError)
  def resolve(s: Snapshot, ref: str) -> str | None        # ID or code, case-insensitive
  def search(s: Snapshot, d: Derived, query: str, filters: Filters, limit: int = 20) -> list[str]
  def related(s: Snapshot, d: Derived, decision: Decision, limit: int = 3) -> list[str]
  @dataclass(frozen=True) class Level1:
      id: str; kind: str; code: str | None; title: str; statement: str; status: str
      decided_by: str | None; date: str | None; scope: str | None; area: str | None
      flags: tuple[str, ...]
  @dataclass(frozen=True) class Level3:
      quote: Quote | None; numbers: tuple[NumberHandle, ...]; work_item: str | None
      attachments: tuple[str, ...]; imported_from: Imported | None
      links: tuple[tuple[str, str, str], ...]   # (relation, target id, target status)
  def failing_ids(s: Snapshot, result: CheckResult) -> frozenset[str]
  def unrecorded_problems(s: Snapshot, result: CheckResult) -> tuple[Problem, ...]   # no record behind them
  def level1(s: Snapshot, d: Derived, record_id: str, failing: frozenset[str]) -> Level1
  def level2(s: Snapshot, d: Derived, record_id: str) -> str
  def level3(s: Snapshot, d: Derived, record_id: str) -> Level3
  def format_level1(v: Level1) -> str
  def format_level3(v: Level3) -> str
  def render_spec(s: Snapshot, d: Derived, area: str | None = None) -> str
  ```
- `flags`, in this order when present: `replaced by <ids>`, `narrowed by <ids>`, `retired by <id>`, `awaiting the author`, `imported`, `unquoted`, `fails check`; so a narrowed decision never reads as plainly current.
- A specification entry's level 1 takes `decided_by` and `date` from its newest changing decision.
- `format_level1`, two lines: `d-3m8qk2 ITEM-1 · current · author · 2026-10-28 · process`, flags appended with ` · `; then the title, a blank line, the statement.
- `level2` of a decision is its reasoning; of an entry, the level-1 lines of `changed_by`.
- `level3.links` holds both directions: `changes`, `replaces`, `narrows`, `confirms`, `replaced by`, `narrowed by`, `changed by`, `confirmed by`.
- Search: an exact ID or code match first, then query-word overlap with the title (weight 3) and statement (weight 1), words lower-cased and split on non-letters; ties newest first.
- `related`: current decisions sharing an entry in `changes`, then search hits on title and statement scoring at least 2, excluding the decision itself.
- `render_spec`: areas in name order, `# <area title>`, the intro, then per current entry in order `## <title> (<id>)` and its statement.

- [ ] **Step 1: Write failing tests:** `test_resolve_case_insensitive`, `test_resolve_ambiguous_code_raises`, `test_search_title_over_statement`, `test_search_each_filter`, `test_search_hides_replaced_unless_asked`, `test_related_shared_entry_first`, `test_level1_status_who_flags`, `test_narrowed_decision_flagged_at_level1`, `test_replaced_decision_names_successor_at_level1`, `test_entry_level1_takes_who_from_latest_decision`, `test_unquoted_import_flags`, `test_failing_ids_maps_paths`, `test_unrecorded_problem_for_unparsable_file`, `test_level2_of_entry`, `test_level3_reverse_links_with_status`, `test_format_level1_exact_text`, `test_render_spec_skips_retired_follows_order`.
- [ ] **Step 2: Run**; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check.sh`; expected: green.
- [ ] **Step 5: Commit and push.**

