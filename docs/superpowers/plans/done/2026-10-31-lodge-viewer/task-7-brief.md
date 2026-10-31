# Brief: Task 7 of `docs/superpowers/plans/2026-10-31-lodge-viewer.md`

You build Task 7 of the plan named above, in this repository, on its current branch.
Read `CLAUDE.md` first, then this brief; this brief is your requirements, with the exact values to use verbatim.
Read other parts of the plan only where this brief points to them by name.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Do not commit and do not push: the coordinator stages, runs `sh scripts/check.sh` outside the sandbox, commits, and pushes.
Tests that need sockets fail in your sandbox; run the rest, and name the socket-bound ones in your report.
Write your report to `docs/superpowers/plans/2026-10-31-lodge-viewer/task-7-report.md`: what you changed per file, each test you added with its first failing output, the commands you ran and their last lines, and anything you were unsure of.
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

### Task 7: The viewer's pages

**Files:**
- Modify: `src/lodge/viewer/pages.py`, `src/lodge/viewer/server.py`, `src/lodge/viewer/style.css`, `src/lodge/app/results.py` (`Shown.rests_on`, `Shown.supports`), `src/lodge/app/reads.py`, `src/lodge/core/order.py`, `src/lodge/core/__init__.py`, `tests/viewer/test_pages.py` and `tests/viewer/test_post_routes.py` (their calls pass `token`)
- Create: `src/lodge/viewer/forms.py` (the confirm, thread, reply, and close forms), `src/lodge/viewer/spec.py` (the specification and area pages)
- Test: `tests/viewer/test_forms.py` (new), `tests/viewer/test_pages_threads.py` (new), `tests/core/test_order.py`

**Interfaces:**
- Consumes: Tasks 1 to 6b: `SpecArea.placed`, `Placed`, `Shown.threads`, `Shown.confirmable`, `Lodge.behind_area`, `Behind`, `Lodge.threads_waiting`, `ThreadsWaiting.titles`, `Gatekeeper.token`, `handle_post`, and Task 6b's route and field table.
- Produces:
  ```python
  # core/order.py
  @dataclass(frozen=True) class Branch: id: str; title: str; status: str; children: tuple["Branch", ...]
  def rests_on_tree(s: Snapshot, d: Derived, entry_id: str) -> tuple[Branch, ...]  # down to the roots, cycle-safe
  # app
  Shown.rests_on: tuple[Branch, ...] = (); Shown.supports: tuple[Level1, ...] = ()
  # viewer
  def record_page(shown: Shown, token: str) -> str
  def spec_page(areas: tuple[SpecArea, ...], read: Read, token: str,
                order: Literal["dependency", "written"], area: str | None,
                behind: tuple[Behind, ...]) -> str           # order "written" when the query has order=written
  def waiting_page(listed: Listed, waiting: ThreadsWaiting) -> str
  render(make_lodge, url, token: str)       # the token reaches every page with a form
  ```
- Every form is `method="post"` with a relative `action`, a hidden `token`, and exactly the fields of Task 6b's table; every text she typed or an agent wrote is escaped with `html.e`.
- Decision page, when `confirmable`: a text area named `words`, labelled "Your words", required, beside it "The decision stays the agent's, and your words are kept exactly as written, so a caveat such as "read, not fully understood" belongs here.", a hidden `id`, and a button "Confirm".
- Every record page: below the record, its threads newest last, each a `<section class="thread" id="q-…">` with a heading "Doubt q-…" or "Question q-…" and its state, each message's `by`, `when`, and `where`, and the text as paragraphs, the closing message of a closed thread headed "Closed by BY" with its `when` and `where`, and no paragraph when its text is empty (d-a3h9f3); while open, a reply text area with button "Reply" and a form with button "Close" and an optional text area; then the forms "Raise a doubt" and "Ask a question", each a text area and a hidden `about` and `kind`.
- Entry page: "Rests on", nested lists down to the roots, and "Rests on it", one level from `supports`, each item a link with its status.
- Specification page: "By dependency" by default (`placed`, each entry in a `div` of class `depth-N`, `N = min(depth, 5)`, one line "also rests on" with links to `also`, and to `under` too when the depth is over 5, when either applies, and a line `rests on <link> (area)` per cross-area target), "As written" with `?order=written` (`entries`); both links on the page keep `area`; each area heading links to `/spec?area=NAME`.
- Area page (`/spec?area=NAME`), when `behind` is non-empty: above the entries, "Decisions behind this area, not yet confirmed", each decision a link with its title and the entries it changes with their areas, then one form with a hidden `area`, a hidden `id` per listed decision, and the field and button of the decision page.
- Waiting page, titled "Waiting": "Waiting for an agent" (`for_agent`), then "Waiting for the author" (the flagged decisions, then `for_author`); each thread a link to `/r/{about}#{q}` with its head and the title from `titles`.
- `style.css`: `.depth-1` to `.depth-5` (indent steps), `.thread`, `.notice`, and form spacing, within the existing look; no inline style, since the policy forbids it (`POLICY`).

- [ ] **Step 1: Write the failing tests.**
  - `test_forms.py`: `test_confirm_form_on_a_confirmable_decision` (`action="/confirm"`, `name="token" value="T…"`, "Your words", "Confirm", the note text); `test_no_confirm_form_on_author_confirmed_or_replaced_decisions`; `test_doubt_and_question_forms_on_every_record`; `test_open_thread_has_reply_and_close`; `test_closed_thread_has_neither`; `test_thread_text_is_escaped` (`<script>` appears as `&lt;script&gt;`); `test_forms_post_to_relative_actions_only`; `test_rendered_forms_post_through_handle_post` (each form of a decision page, an area page, and an entry page with an open thread: its `action` and field names read from the HTML, filled, and passed to `handle_post` against `staged_world()`, each answering 303).
  - `test_pages_threads.py`: `test_threads_newest_last`; `test_entry_tree_down_to_roots_and_one_level_up`; `test_spec_opens_by_dependency` (written a, b, c, with c resting on a: the order a, c, b, c in `depth-1`); `test_spec_also_rests_on_line` (an entry with a second same-area target shows "also rests on" with its link); `test_thread_closed_without_text_shows_closed_by_author` (closed from the viewer with the field empty: the page shows "Closed by author", and the thread file's closing message holds no text); `test_spec_as_written`; `test_spec_cross_area_line`; `test_area_page_lists_decisions_entries_and_hidden_ids`; `test_area_page_without_unconfirmed_has_no_form`; `test_waiting_page_has_both_groups`.
  - `test_order.py`: `test_rests_on_tree_reaches_the_roots`; `test_rests_on_tree_stops_on_a_cycle`.
- [ ] **Step 2: Run** `uv run pytest tests/viewer/test_forms.py tests/viewer/test_pages_threads.py tests/core/test_order.py -q`; expected: FAIL.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the builder's gate; expected: green; the coordinator runs the socket tests and opens one decision, one entry, `/spec`, an area page, and `/waiting` in a browser, recording what it saw in the report.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.
