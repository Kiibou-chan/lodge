### Task 8: Application operations and ports

**Files:**
- Create: `src/lodge/app/ports.py`, `src/lodge/app/errors.py`, `src/lodge/app/lodge.py` (the `Lodge` class, delegating), `src/lodge/app/reads.py`, `src/lodge/app/writes.py`
- Test: `tests/app/fakes.py` (`MemoryStore(staged: bool = False)`, `FixedClock`, `CountingIds`), `tests/app/test_reads.py`, `tests/app/test_writes.py`

**Interfaces:**
- Consumes: `lodge.core`.
- Produces (exported from `lodge.app`):
  ```python
  class PublishOutcome(StrEnum): PUBLISHED = "published"; STAGED = "staged"; REJECTED = "rejected"
  class Store(Protocol):
      def trees(self) -> tuple[Tree, Tree]: ...   # (current, published) from one read
      def freshness(self) -> str | None: ...
      def publish(self, base: Tree, writes: Mapping[str, str], message: str) -> PublishOutcome: ...
  class Clock(Protocol): def now(self) -> datetime: ...      # timezone-aware
  class IdSource(Protocol): def entropy(self) -> bytes: ...
  class LodgeError(Exception): exit_code: int = 2
  class Conflict(LodgeError): exit_code = 1
  class AddOutcome(StrEnum): PUBLISHED = "published"; STAGED = "staged"; CHECK_FAILED = "check failed"
  @dataclass(frozen=True) class Read: freshness: str | None; unrecorded: tuple[Problem, ...]
  @dataclass(frozen=True) class Shown: level1: Level1; level2: str | None; level3: Level3 | None; read: Read
  @dataclass(frozen=True) class Listed: items: tuple[Level1, ...]; read: Read
  @dataclass(frozen=True) class Added: ids: tuple[str, ...]; feedback: tuple[Feedback, ...]
      check: CheckResult; outcome: AddOutcome
  class Lodge:
      def __init__(self, store: Store, clock: Clock, ids: IdSource, settings: CoreSettings) -> None
      def search(self, query: str, filters: Filters) -> Listed
      def show(self, ref: str, reasoning: bool = False, provenance: bool = False) -> Shown
      def waiting(self) -> Listed
      def timeline(self, limit: int = 50) -> Listed
      def spec(self, area: str | None = None) -> tuple[str, Read]
      def problems(self) -> tuple[CheckResult, Read]
      def mint(self, prefix: Literal["d", "s"]) -> str
      def draft(self, ref: str) -> str            # ref: an ID, a code, or "area:<name>"
      def add(self, drafts: Sequence[tuple[str, str]], importing: bool = False) -> Added
      def check(self, gate: bool) -> tuple[CheckResult, Read]
  ```
- Every read runs `check_state` on the snapshot it loads and passes `failing_ids` to `level1`; `Read.unrecorded` carries the problems with no record behind them, so files that fail to parse are never silent.
- `AmbiguousRef`, `SettingsError`, and unknown references become `LodgeError` (exit 2) with one sentence.
- `add`: parse drafts (any problem: `LodgeError` naming source and line, nothing written); read `store.trees()` once; mint IDs for new decisions; `apply_drafts` (problems: `LodgeError`, or `Conflict` for a stale base); build `after` from `current` plus the writes; `check_change(published, after)`; if it fails, `Added` with `CHECK_FAILED` and nothing published; else `store.publish(current_tree, writes, "lodge: add <ids> <first title>")`; on `REJECTED`, start again from reading the trees, at most three attempts, then `Conflict`. Notes go into `Added.check.notes`.
- `mint` draws again on a clash with any existing ID, at most ten times. The date is `clock.now()` to the second with offset.

- [ ] **Step 1: Write failing tests** against the fakes. `MemoryStore` holds one tree (branch-like) or a working and a published tree (`staged=True`); it can be told to reject the next N publishes and, on each rejection, to apply a concurrent change first (another entry in the same area, or an edit of the entry being edited). Tests: `test_show_resolves_code_and_levels`, `test_search_listed_with_read`, `test_unparsable_file_reported_by_every_read`, `test_waiting_lists_flagged`, `test_add_new_decision_entry_area`, `test_add_fills_id_and_date_from_ports`, `test_add_stale_base_conflicts_writes_nothing`, `test_add_failing_check_publishes_nothing`, `test_add_returns_feedback_and_notes`, `test_add_retry_keeps_concurrent_entry` (both entries in the area order afterwards and `check_state` clean), `test_add_retry_concurrent_edit_of_same_entry_conflicts`, `test_add_gives_up_after_three`, `test_ref_moving_between_reads_retries` (a fake whose tip moves after `trees()` and before `publish`), `test_staged_second_edit_builds_on_first` (`staged=True`: two consecutive edits of one entry, the second drafted after the first was added, both visible), `test_mint_skips_taken`, `test_draft_prints_file_with_base`, `test_draft_area`.
- [ ] **Step 2: Run**; expected: FAIL.
- [ ] **Step 3: Implement**, `reads.py` and `writes.py` each under 300 lines, `lodge.py` only delegating.
- [ ] **Step 4: Run** `sh scripts/check.sh`; expected: green.
- [ ] **Step 5: Commit and push.**


## Carried from Tasks 5 to 7 (ledger rulings, binding)

- `check_change` is `check_change(published, after, settings, now)` (Task 5 I2): `add` passes `self.settings` and `now`.
  `now` is read no earlier than the reading that dates the new decisions (Task 5 N2): take one `clock.now()` reading per attempt and use it both as the decisions' date and as `now`.
  Test: `test_add_date_and_check_time_from_one_reading` (a clock that advances a second per call; the add passes).
- `apply_drafts` raises `ValueError` unless it gets exactly one new ID per decision draft without an `id`: mint exactly that many (Task 7).
  `StaleBase` (a `Problem` subclass from `lodge.core`) becomes `Conflict`; every other problem becomes `LodgeError`.
- `feedback` gets the new decisions and every written entry, never an edited decision (Task 7 M11).
  Test: `test_feedback_skips_edited_decisions`.
- `add(drafts, importing=False, dry_run=False)` (Task 7 I2): a dry run parses, applies, checks, and computes feedback exactly as a real add, and never calls `store.publish`.
  `AddOutcome` gains `DRY_RUN = "dry run"`; a dry run whose check fails still reports `CHECK_FAILED`.
  Tests: `test_dry_run_publishes_nothing`, `test_dry_run_reports_feedback_and_check`.
- `Level1` carries `quote` (Task 6 B1); `Read.unrecorded` is what Tasks 10 and 11 print above every read (Task 6 I4).
