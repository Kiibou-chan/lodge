# Brief: Task 6a of `docs/superpowers/plans/2026-10-31-lodge-viewer.md`

You build Task 6a of the plan named above, in this repository, on its current branch.
Read `CLAUDE.md` first, then this brief; this brief is your requirements, with the exact values to use verbatim.
Read other parts of the plan only where this brief points to them by name.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Do not commit and do not push: the coordinator stages, runs `sh scripts/check.sh` outside the sandbox, commits, and pushes.
Tests that need sockets fail in your sandbox; run the rest, and name the socket-bound ones in your report.
Write your report to `docs/superpowers/plans/2026-10-31-lodge-viewer/task-6a-report.md`: what you changed per file, each test you added with its first failing output, the commands you ran and their last lines, and anything you were unsure of.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.

## Global Constraints

- Builders are Codex (`codex exec`), one task per brief; a brief holds these constraints and its task, and Codex sees only its brief, `CLAUDE.md`, and the repository.
- The design is `docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md`, and "design line N" in a task is a line of that file; where the design and a task disagree, the design wins and the builder reports it.
- In Codex's sandbox git's index is read-only and sockets are refused (`docs/superpowers/plans/2026-10-30-lodge-on-itself/task-5-report.md`, lines 104 and 125): the builder never stages, commits, or pushes, and never needs a socket-bound test to pass.
- The builder's gate: `uv run ruff format --check && uv run ruff check && uv run mypy && uv run vulture && uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py && uv run lodge check --gate`; the two ignored files need sockets, apart from `tests/e2e/test_view.py::test_view_passes_the_port_to_the_viewer` and the tests a task names with it, which the builder runs with `uv run pytest tests/e2e/test_view.py -q -k NAME`.
- The coordinator's gate after every task: `sh scripts/check.sh` green outside the sandbox, then it stages with explicit paths, commits with `git -c user.name="Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, the message ending `Co-Authored-By: Claude <noreply@anthropic.com>`, and pushes `lodge-viewer` to `origin`; never `main`.
  A socket test that fails there goes back to the builder as a fix round, its output in the brief.
- `lodge add` in the sandbox: once per task, `mkdir -p .drafts/objects && cp "$(git rev-parse --absolute-git-dir)/index" .drafts/index`; then every `lodge add` (dry runs need none of this) runs as `GIT_INDEX_FILE="$PWD/.drafts/index" GIT_OBJECT_DIRECTORY="$PWD/.drafts/objects" GIT_ALTERNATE_OBJECT_DIRECTORIES="$(git rev-parse --path-format=absolute --git-common-dir)/objects" uv run --frozen --quiet lodge add FILE...`.
  When that fails, the builder stops with BLOCKED and the error, leaving the drafts and their dry-run output under `.drafts/`, and the coordinator runs the adds.
  The record files land in the working tree, and the coordinator stages them with `git add lodge/`.
- Test-first: each named test is written and seen failing before its code; every existing test keeps passing, edited only where a task says so.
- Structure (`tests/structure_rules.py`, `tests/structure_tables.py`, run by every pytest): allowed imports as `ALLOWED`; other packages import only from a package's `__init__.py`; no import cycles, within a package too; no module over 300 lines, tests included; `core` imports only `CORE_MODULES`; `subprocess` only in `gitstore`; file reads only in `gitstore` and `cli`, and `viewer` reads only its package data.
- `core` and `app` read no clock and no randomness: the time comes from `Clock`, IDs from `IdSource`; the viewer's token is minted in `src/lodge/main.py`.
- Modules near the limit take no new code: `core/apply.py` (277 lines), `gitstore/checkout.py` (257), `core/derive.py` (227), `core/views.py` (220), `cli/parser.py` (219), `app/writes.py` (213); new code goes in the new modules each task names, and a task that edits one of these adds at most the lines it states.
- Tests near the limit take no new tests: `tests/core/test_feedback.py` (282 lines), `tests/core/test_fileformat.py` (279), `tests/viewer/test_pages.py` (239); new tests go in the new files each task names, marked "(new)".
- `tests/`, `tests/core/`, and `tests/app/` are not packages, so a new test file's basename is unique across the three; two files of one name stop pytest at collection.
- Vulture scans `src` and `tests`; every produced name, field included, is read in the task that adds it, by its source or by one of its tests.
- Tests never touch a real repository: git only in `tmp_path` through the existing helpers (`tests/gitstore/repos.py`, `tests/e2e/conftest.py`), no network; fixtures are a made-up project (the `storage` area, transcripts), never her words or another project's records.
- User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line.
- Record files only through `lodge add`; drafts under `.drafts/` (git-ignored); `lodge add --dry-run` before every `lodge add`; a check line stops the task.
- Exit codes stay 0 done, 1 failed check or conflict, 2 usage or environment; no traceback reaches the user, so a `ValueError` from writing a file becomes a `LodgeError` naming the field.
- Text she types in the viewer, and every message text, loses a CR before each LF and the whitespace around it, nothing else, and must not then be empty, except a closing message's text.
- The viewer writes as `author` with `where` `lodge viewer` and `when` the clock's minute, `%Y-%m-%d %H:%M` (design lines 59 and 86).
- Every string the design fixes is used verbatim: "Your words", "Confirm", "Raise a doubt", "Ask a question", "Close", "lodge viewer", "in doubt", "question open", "As written", "By dependency", "Confirms d-xxxxxx", "Confirms the decisions behind area NAME", "The author confirms d-xxxxxx.", "Author confirmation from the viewer: d-xxxxxx", "Thread q-xxxxxx: author reply".

### Task 6a: The confirmation in core and app

**Files:**
- Modify: `src/lodge/app/errors.py` (`StaleList`), `src/lodge/app/results.py` (`Behind`, `Shown.confirmable`), `src/lodge/app/lodge.py`, `src/lodge/app/reads.py` (`show` fills `confirmable`), `src/lodge/app/__init__.py`, `src/lodge/core/__init__.py`
- Create: `src/lodge/core/confirmation.py`, `src/lodge/app/confirm.py`
- Test: `tests/core/test_confirmation.py` (new), `tests/app/test_confirm.py` (new)

**Interfaces:**
- Consumes: Task 4's `Written`, `Committed`, `Added.paths`, `Store.commit`; Task 3's level-1 confirmation mark.
- Produces:
  ```python
  # core/confirmation.py
  VIEWER = "lodge viewer"
  def confirmable_ids(s: Snapshot, d: Derived) -> frozenset[str]   # agent, current, not in confirmed_by
  def behind_area(s: Snapshot, d: Derived, area: str) -> tuple[str, ...]
  def confirmation_draft(confirms: Sequence[str], scope: Scope, words: str, when: str,
                         area: str | None) -> str                   # ValueError on a character a header cannot carry
  # app
  class StaleList(Conflict)
  @dataclass(frozen=True) class Behind: decision: Level1; entries: tuple[tuple[str, str], ...]  # (entry, area)
  Shown.confirmable: bool = False
  Lodge.confirm(self, ids: Sequence[str], words: str, area: str | None = None, commit: bool = False) -> Written
  Lodge.behind_area(self, name: str) -> tuple[Behind, ...]         # NotFound for an unknown area
  ```
- `behind_area`: the confirmable decisions that list an entry of the area's folder, current or retired, with `create`, or are its `changed_by[0]`, ordered by `(datetime.fromisoformat(date), id)` (design line 51); `Behind.entries` lists every entry the decision's `changes` names that exists, once, in order, with its area.
- `confirmation_draft` (design lines 56 to 61): `kind: decision`, title `Confirms {id}` or `Confirms the decisions behind area {area}`, `scope`, `decided_by: author`, `confirms: [ids]`, `quote: {text: words, where: "lodge viewer", when: when}` with `yamlio.quoted`; body `The author confirms {listed}.` (`d-a`, `d-a and d-b`, or `d-a, d-b, and d-c`), then `## Reasoning`, then the words.
- `confirm`: the words follow the Global Constraints' CR rule, empty refused (`your words are required; nothing was written`); the expected list is `behind_area` for an area, else `(ids[0],)` when exactly one ID was given and it is confirmable; any other set of IDs raises `StaleList("the list changed since the page was loaded; nothing was written")`.
  Scope is `product` when any listed decision is, else `process`; `when` is the clock's minute; a `ValueError` from the draft is a `LodgeError` (`your words hold a character lodge cannot store`).
  The draft goes through `writes.add(w, [(VIEWER, draft)], False, False)`, so it writes only one new decision file; on `STAGED` with `commit=True`, `store.commit(added.paths, f"Author confirmation from the viewer: {added.ids[0]}")`.

- [ ] **Step 1: Write the failing tests.**
  - `test_confirmation.py`: `test_confirmable_ids_skip_author_confirmed_and_replaced`; `test_behind_area_lists_creators_and_last_changers_oldest_first`; `test_behind_area_includes_the_retirer_of_a_retired_entry`; `test_confirmation_draft_single` (parsed with `parse_draft` and `record_from_draft`: title `Confirms d-aaaaaa`, statement `The author confirms d-aaaaaa.`, `reasoning == words`, `quote.where == "lodge viewer"`); `test_confirmation_draft_area_lists_with_the_oxford_comma`.
  - `test_confirm.py`: `test_confirm_one_decision` (one author decision published, `confirms` the agent decision, `quote.when == "2026-10-29 09:30"`); `test_confirm_writes_only_a_new_decision_file` (every published path is under `lodge/decisions/` and absent before); `test_confirmed_decision_keeps_decided_by_and_clears_its_flag`; `test_scope_product_when_any_listed_is_product`; `test_scope_process_when_all_are_process`; `test_area_confirms_exactly_the_listed`; `test_stale_area_list_writes_nothing` (`StaleList`, `store.publishes == []`); `test_second_identical_confirmation_is_stale` (Review Focus 1); `test_words_required`; `test_words_with_specials_kept_verbatim` (Review Focus 2); `test_words_with_unstorable_character_refused` (`"\x00"`: `LodgeError`, nothing published); `test_commit_after_staged` (`store.commits == [((path,), "Author confirmation from the viewer: d-111111")]`); `test_behind_area_lists_entries_in_other_areas`; `test_show_marks_confirmable`.
- [ ] **Step 2: Run** `uv run pytest tests/core/test_confirmation.py tests/app/test_confirm.py -q`; expected: FAIL.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the builder's gate; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.
