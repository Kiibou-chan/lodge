### Task 3: Records, identifiers, settings, and the file format

**Files:**
- Create: `src/lodge/core/model.py`, `src/lodge/core/ids.py`, `src/lodge/core/settings.py`, `src/lodge/core/yamlio.py`, `src/lodge/core/fileformat.py`, `src/lodge/core/drafts.py`
- Test: `tests/core/test_ids.py`, `tests/core/test_settings.py`, `tests/core/test_yamlio.py`, `tests/core/test_fileformat.py`, `tests/core/test_drafts.py`

**Interfaces:**
- Produces (exported from `lodge.core`):
  ```python
  class Scope(StrEnum): PRODUCT = "product"; PROCESS = "process"
  class Action(StrEnum): CREATE = "create"; EDIT = "edit"; RETIRE = "retire"
  @dataclass(frozen=True) class Quote: text: str; where: str; when: str
  @dataclass(frozen=True) class Change: entry: str; action: Action
  @dataclass(frozen=True) class NumberHandle: value: str; handle: str
  @dataclass(frozen=True) class Imported: file: str; heading: str
  @dataclass(frozen=True) class Decision:
      id: str; title: str; scope: Scope; decided_by: str; date: str; statement: str
      reasoning: str = ""; code: str | None = None; changes: tuple[Change, ...] = ()
      replaces: tuple[str, ...] = (); narrows: tuple[str, ...] = (); confirms: tuple[str, ...] = ()
      work_item: str | None = None; quote: Quote | None = None
      numbers: tuple[NumberHandle, ...] = (); attachments: tuple[str, ...] = ()
      imported_from: Imported | None = None
  @dataclass(frozen=True) class SpecEntry:
      id: str; area: str; title: str; statement: str
      code: str | None = None; imported_from: Imported | None = None
  @dataclass(frozen=True) class Area: name: str; title: str; intro: str; order: tuple[str, ...]
  Record = Decision | SpecEntry
  @dataclass(frozen=True) class Problem: path: str; check: int; message: str; line: int | None = None
  def mint_id(prefix: Literal["d", "s"], entropy: bytes) -> str
  def is_id(text: str) -> bool
  @dataclass(frozen=True) class LengthGuidance: title_chars: int = 100
      decision_statement_words: int = 80; spec_statement_words: int = 150; reasoning_words: int = 1000
  @dataclass(frozen=True) class CoreSettings: length: LengthGuidance; import_sources: tuple[str, ...]
  class SettingsError(ValueError)
  def parse_core_settings(table: Mapping[str, object]) -> CoreSettings   # [length], [import]
  def load_yaml(text: str) -> object       # every scalar a str
  def parse_record(path: str, text: str) -> Record | Problem
  def parse_area(path: str, text: str) -> Area | Problem
  def write_record(record: Record) -> str
  def write_area(area: Area) -> str
  def new_record_path(record: Record) -> str
  def slug(title: str) -> str
  def content_hash(text: str) -> str      # first 12 hex characters of SHA-256 of the UTF-8 text
  @dataclass(frozen=True) class Draft:
      kind: Literal["decision", "spec", "area"]; header: Mapping[str, object]; body: str; source: str
  def parse_draft(source: str, text: str) -> Draft | Problem   # syntax and key names only
  def record_from_draft(draft: Draft, id: str, date: str | None, area: str | None) -> Record | Area | Problem
  ```
- `load_yaml`: a `yaml.SafeLoader` subclass with every implicit resolver removed, so `yes`, `14:14`, `2026-10-29`, `~`, and `1234` all load as strings; `parse_record` then reports problem 1 for a field of the wrong shape.
- Text normalisation: `\r\n` becomes `\n` before parsing and hashing.
- `write_record` is a small emitter, not `yaml.safe_dump`: keys in the order below, absent keys omitted; IDs, codes, enums, and dates unquoted; every free-text value (titles, quote text, where, and when, work item, number values and handles, import heading) written as a JSON string (`json.dumps(value, ensure_ascii=False)`), which YAML reads back unchanged; lists of IDs as `[a, b]`; each change as `  - {entry: s-…, action: edit}`; the quote as a flow mapping. `write_record(parse_record(p, t)) == t` holds for every canonical file. Decision example, statement above `## Reasoning`:
  ```markdown
  ---
  id: d-3m8qk2
  kind: decision
  code: ITEM-1
  title: "Whole transcripts are kept before a session is archived"
  scope: process
  decided_by: author
  date: 2026-10-28T23:48:10+01:00
  changes:
    - {entry: s-4kq1zm, action: edit}
  replaces: [d-8rw0te]
  quote: {text: "Record it.", where: "first session", when: "2026-10-28 23:48"}
  ---

  One to three sentences stating the decision.

  ## Reasoning

  Why, in a few hundred words at most.
  ```
  Key order for decisions: `id`, `kind`, `code`, `title`, `scope`, `decided_by`, `date`, `changes`, `replaces`, `narrows`, `confirms`, `work_item`, `quote`, `numbers`, `attachments`, `imported_from`. Specification entry: `id`, `kind: spec`, `code`, `title`, `imported_from`; body is the statement; path `lodge/spec/<area>/<id>-<slug>.md`, area from the folder. Area file `lodge/spec/<area>/_area.md`: `kind: area`, `title`, `order`; body is the intro. Decision path `lodge/decisions/<id>-<slug>.md`. `slug` lower-cases, keeps `[a-z0-9]` runs, joins at most six words with `-`.
- A `code` must match `[A-Za-z0-9][A-Za-z0-9._-]*`, and any header string holding a C0 or C1 control character is problem 1, since YAML cannot read some of them back.
- The statement is everything above the first line reading `## Reasoning`; `write_record` raises `ValueError` for a statement containing such a line.
- `date` must match ISO 8601 with seconds and an offset; a date-only value is accepted only with `imported_from` and becomes `<date>T00:00:00+00:00`. A draft additionally accepts `area` (specification entries), `base`, and, for area drafts, `name`.

- [ ] **Step 1: Write failing tests:**
  - `test_mint_id`: `mint_id("d", bytes(8)) == "d-000000"`; `mint_id("s", b"\xff" * 8) == "s-zzzzzz"`; `is_id("d-3m8qk2")`; not `is_id("d-3m8qkI")`, not `is_id("x-3m8qk2")`.
  - `test_settings_defaults_when_empty`, `test_settings_reads_every_key`, `test_settings_rejects_unknown_key_naming_it` (`[length]\ntitle = 5` names `length.title`).
  - `test_yaml_scalars_stay_strings` for `yes`, `no`, `on`, `~`, `null`, `14:14`, `2026-10-29`, `1234`, `0x10`.
  - `test_decision_round_trips_both_ways` (every field set, and required only), `test_written_text_matches_example` (the literal above), `test_round_trip_survives_hostile_strings` (`No`, `null`, `a: b`, `# x`, `"`, `\\`), `test_bad_code_is_problem_1`, `test_control_character_is_problem_1`, `test_write_refuses_reasoning_heading_in_statement`.
  - `test_crlf_text_parses_and_hashes_as_lf`.
  - `test_spec_entry_takes_area_from_folder`.
  - Problem 1 cases: `test_missing_fence`, `test_bad_yaml_with_line`, `test_unknown_key_named` (`replace:`), `test_missing_required_field` (each of `title`, `scope`, `decided_by`, `date`, empty statement), `test_bad_scope_or_action`, `test_non_string_where_string_expected` (a list as `title`), `test_date_without_offset`, `test_date_only_without_import`.
  - `test_imported_date_only_normalised`.
  - Drafts: `test_draft_without_id_or_date`, `test_draft_keeps_header_and_body`, `test_record_from_draft_fills_id_date_area`, `test_draft_carries_base_and_area`, `test_area_draft`, `test_draft_non_utf8_is_problem` (text with a surrogate from `errors="surrogateescape"`).
- [ ] **Step 2: Run** `uv run pytest tests/core -q`; expected: FAIL on imports.
- [ ] **Step 3: Implement** the six modules.
- [ ] **Step 4: Run** `sh scripts/check.sh`; expected: green.
- [ ] **Step 5: Commit and push.**

