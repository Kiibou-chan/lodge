# Brief: Task 3 of `docs/superpowers/plans/2026-10-31-lodge-viewer.md`

You build Task 3 of the plan named above, in this repository, on its current branch.
Read `CLAUDE.md` first, then this brief; this brief is your requirements, with the exact values to use verbatim.
Read other parts of the plan only where this brief points to them by name.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Do not commit and do not push: the coordinator stages, runs `sh scripts/check.sh` outside the sandbox, commits, and pushes.
Tests that need sockets fail in your sandbox; run the rest, and name the socket-bound ones in your report.
Write your report to `docs/superpowers/plans/2026-10-31-lodge-viewer/task-3-report.md`: what you changed per file, each test you added with its first failing output, the commands you ran and their last lines, and anything you were unsure of.
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

### Task 3: Threads in core

**Files:**
- Modify: `src/lodge/core/model.py`, `src/lodge/core/ids.py`, `src/lodge/core/fields.py` (`read_stamp`; `ID_KIND` gains `"q": "thread"`), `src/lodge/core/snapshot.py`, `src/lodge/core/derive.py` (at most 6 lines), `src/lodge/core/check_state.py`, `src/lodge/core/check_change.py` (`_missing`), `src/lodge/core/check_immutable.py`, `src/lodge/core/views.py` (at most 12 lines), `src/lodge/core/feedback.py` (its `_ID` takes `q`), `src/lodge/core/__init__.py`, `tests/core/builders.py` (`thread(**kw)`, `message(**kw)`; `files_of` and `snapshot_of` take threads)
- Create: `src/lodge/core/threads.py`, `src/lodge/core/doubts.py`
- Test: `tests/core/test_thread_files.py` (new), `tests/core/test_check_threads.py` (new), `tests/core/test_doubts.py` (new)

**Interfaces:**
- Consumes: Task 2's `Derived.changed_by` without links, `rests_on`.
- Produces:
  ```python
  class Raises(StrEnum): DOUBT = "doubt"; QUESTION = "question"
  class ThreadState(StrEnum): OPEN = "open"; CLOSED = "closed"
  @dataclass(frozen=True) class Message: by: str; when: str; text: str; where: str | None = None
  @dataclass(frozen=True) class Thread:
      id: str; about: str; raises: Raises; state: ThreadState; opened: str; messages: tuple[Message, ...]
  def mint_id(prefix: Literal["d", "s", "q"], entropy: bytes) -> str   # is_id accepts q- too
  def read_stamp(value: object, key: str) -> str      # ISO 8601 with seconds and offset, as read_date
  THREADS = "lodge/threads/"
  def thread_path(thread_id: str) -> str              # f"lodge/threads/{thread_id}.md"
  def parse_thread(path: str, text: str) -> Thread | Problem
  def write_thread(thread: Thread) -> str             # ValueError when it would not read back unchanged
  def appended(thread: Thread, message: Message, close: bool = False) -> Thread
      # ValueError if the thread is closed, or if the text is empty and close is False
  def newest_last(threads: Iterable[Thread]) -> tuple[Thread, ...]   # by (datetime of opened, id)
  Snapshot.threads: Mapping[str, Thread] = field(default_factory=dict)  # paths hold thread paths too
  def doubt_marks(s: Snapshot, changed_by: Links) -> dict[str, tuple[str, ...]]
  Derived.doubts: Mapping[str, tuple[str, ...]]
  ```
- File shape: the header holds the record; the messages are the body, as design line 78 asks; `opened` is the time lodge wrote the first message, so threads sort newest last although an author's `when` is free text:
  ```
  ---
  id: q-4kq1zm
  kind: thread
  about: s-0abcde
  raises: doubt
  state: open
  opened: 2026-10-29T09:30:00+01:00
  ---

  ## Message 1

  by: author
  when: "2026-10-29 09:30"
  where: "lodge viewer"

  Is this still true?

  ## Message 2

  by: coordinator
  when: 2026-10-29T10:00:00+01:00

  It is; see d-3m8qk2.
  ```
- Writing: `opened` and an agent's `when` are written plain, as a decision's `date` is; `by` plain when it matches `[A-Za-z0-9][A-Za-z0-9._-]*`, else with `yamlio.quoted`; an author's `when` and `where` with `yamlio.quoted`; the text through `trim_block`.
- Reading: a line exactly `## Message <n>` starts message `n`; the lines up to the first blank line are its YAML block; the rest up to the next heading is its text.
- The escape: on write, a text line matching `^\\*## Message [0-9]+$` gets one more leading backslash; on read, a line matching `^\\+## Message [0-9]+$` loses one; so every text reads back exactly.
- Check 1 (a parse problem, with the key where one applies): unknown header or message key; a malformed `id` (`q-BAD`); `about` not a `d-` or `s-` ID (`about must name a decision or a specification entry`); `raises` or `state` outside its values; `opened` not a stamp; no message (`a thread needs at least one message`); a message heading out of sequence (`messages are numbered 1, 2, 3, in order`); text before `## Message 1`; a message without `by` or `when`; an author message without `where` (`an author message needs where`); an empty message text, except on the last message of a closed thread (its closing message, d-a3h9f3); the file name not starting with the ID; a file in a folder under `lodge/threads/` (stray).
- Check 2: `{q}: about {t}, which does not exist`; a duplicate thread ID as for records; a published thread missing from `after` (`_missing`).
- Check 5 (`check_immutable`), comparing a published thread with its `after` self: `{q}: about of a published thread was changed`; `{q}: raises of a published thread was changed`; `{q}: opened of a published thread was changed`; `{q}: a published message was changed or removed; messages are only appended`; `{q}: a closed thread was opened again`; `{q}: a message was added after the thread was closed`; `{q}: a thread was closed without a closing message` when the published thread is open, the one in `after` is closed, and it has no message the published one lacks.
- An open thread fails no check.
- `doubt_marks`, per record: `in doubt` when an open doubt is about it; `question open` when an open question is; on an entry, `changed by {d}, in doubt` per doubted decision that lists it with `create` or is its `changed_by[0]`, by ID; on an entry, `rests on {y}, in doubt` per entry `y` reached through one or more `rests_on` links (cycle-safe) that is itself in doubt or changed by a doubted decision, by ID; questions never propagate.
- Level 1 flags, after the "awaiting the author" flags and before Task 2's rests-on flags: `confirmed by the author ({ids})` on a decision in `d.confirmed_by`, the confirming IDs joined with ", ", then the `d.doubts` marks in the order above.

- [ ] **Step 1: Write the failing tests.**
  - `test_thread_files.py`: `test_thread_round_trips` (multi-line text, an agent and an author message, and a closed thread whose closing message has no text); `test_empty_text_only_on_the_closing_message` (an empty text on an earlier message, or on the last message of an open thread, is problem 1); `test_written_shape_matches_the_example` (the example above, byte for byte); `test_text_line_like_a_heading_round_trips` (texts `## Message 2` and `\## Message 2` read back exact); `test_yaml_and_markdown_specials_round_trip` (Review Focus 2: `a: "b" # c`, `<script>`, `## Reasoning`); `test_author_message_needs_where`; `test_malformed_id_is_problem_1` (`id: q-BAD`, no exception); `test_about_must_name_a_decision_or_entry` (`q-…` is problem 1); `test_thread_needs_a_message`; `test_messages_numbered_in_order`; `test_body_text_before_first_message_refused`; `test_appended_refuses_a_closed_thread`; `test_newest_last_by_opened_then_id`; `test_load_reads_threads_and_their_paths`; `test_nested_file_under_threads_is_stray`.
  - `test_check_threads.py`: `test_open_thread_passes_every_check`; `test_unresolved_about_fails_check_2`; `test_duplicate_thread_id_fails_check_2`; `test_file_name_must_start_with_the_id`; `test_appending_a_message_passes`; `test_closing_passes`; `test_editing_a_published_message_fails_check_5`; `test_removing_a_message_fails_check_5`; `test_changing_about_fails_check_5`; `test_changing_raises_fails_check_5`; `test_reopening_fails_check_5`; `test_message_after_closing_fails_check_5`; `test_closing_without_a_message_fails_check_5`; `test_missing_published_thread_fails_check_2`.
  - `test_doubts.py`: `test_open_doubt_marks_its_record`; `test_closed_doubt_marks_nothing`; `test_question_open_mark_and_no_propagation`; `test_doubt_reaches_entries_resting_on_it_further_down` (c rests on b rests on a, doubt on a: `"rests on s-a…, in doubt"` on b and c); `test_doubt_on_decision_marks_entries_it_created_and_last_changed`; `test_doubt_on_decision_reaches_what_rests_on_its_entries`; `test_cycle_of_rests_on_does_not_hang`; `test_confirmed_decision_shows_confirmation_and_keeps_decided_by` (`"confirmed by the author (d-bbbbbb)" in flags`, `decided_by == "coordinator"`); `test_flag_order` (one entry with `awaiting the author on …`, `in doubt`, `rests on …, retired`, `imported`, in that order).
- [ ] **Step 2: Run** `uv run pytest tests/core -q`; expected: the new tests FAIL.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the builder's gate; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.
