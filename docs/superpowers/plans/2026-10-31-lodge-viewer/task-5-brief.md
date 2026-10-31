# Brief: Task 5 of `docs/superpowers/plans/2026-10-31-lodge-viewer.md`

You build Task 5 of the plan named above, in this repository, on its current branch.
Read `CLAUDE.md` first, then this brief; this brief is your requirements, with the exact values to use verbatim.
Read other parts of the plan only where this brief points to them by name.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Do not commit and do not push: the coordinator stages, runs `sh scripts/check.sh` outside the sandbox, commits, and pushes.
Tests that need sockets fail in your sandbox; run the rest, and name the socket-bound ones in your report.
Write your report to `docs/superpowers/plans/2026-10-31-lodge-viewer/task-5-report.md`: what you changed per file, each test you added with its first failing output, the commands you ran and their last lines, and anything you were unsure of.
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

### Task 5: Thread commands, `waiting` in two groups, and the guide

**Files:**
- Modify: `src/lodge/cli/parser.py` (at most 12 lines: the import, the `Command` union, one call, the `waiting` help), `src/lodge/cli/commands.py` (`_read` moves out), `src/lodge/cli/output.py`, `src/lodge/cli/guide.md`, `src/lodge/hook/post_tool_use.py`, `tests/hook/test_post_tool_use.py`
- Create: `src/lodge/cli/threads.py` (the five commands' dataclasses, `add_thread_commands`, `run_thread`), `src/lodge/cli/thread_output.py`, `src/lodge/cli/files.py` (`read_file`, moved from `commands._read`, imported by `commands.py` and `threads.py`, so no import cycle)
- Test: `tests/e2e/test_threads.py` (new), `tests/e2e/test_waiting.py`, `tests/e2e/test_help_lists_every_command.py`, `tests/e2e/test_guide.py`

**Interfaces:**
- Consumes: Task 4's `Lodge.ask`, `reply`, `close`, `threads`, `thread`, `threads_waiting`, `Written`, `ThreadList.titles`, `ThreadsWaiting`.
- Produces: the commands `threads`, `thread REF`, `ask REF --kind {doubt,question} --by ROLE [--where W] [--when T] FILE`, `reply REF --by ROLE [--where W] [--when T] FILE`, `close REF --by ROLE [--where W] [--when T] [FILE]`; and
  ```python
  def read_file(name: str, not_utf8: str, exact: bool) -> str   # cli/files.py, as commands._read was
  def thread_head(t: Thread, title: str) -> str
  def thread_text(shown: ThreadShown) -> str
  def waiting_text(listed: Listed, waiting: ThreadsWaiting) -> str
  ```
- The command line refuses, exit 2: `--by author` without both `--where` and `--when` (`a message by author needs --where and --when, the place and time of the author's words`); `--where` or `--when` with another role (`--where and --when are for messages by author`).
- The message file is read with `read_file`, as drafts are; the command line never asks for a commit.
- Help lines: `threads` "list the open threads: doubts and questions on records"; `thread` "show one thread with its messages"; `ask` "open a thread on a record: a doubt or a question"; `reply` "add a message to an open thread"; `close` "close a thread, with a closing message"; `waiting` "list what waits: for an agent, then for the author".
- `thread_head`: `q-111111 · open · doubt · about s-aaaaaa · 2 messages · last by coordinator`, then the title line; `thread_text`: the head, a blank line, then per message a line `by · when` (with ` · where` when set), the text, and a blank line between messages; the last message of a closed thread gets the line `closed by BY · when` (with ` · where` when set) in place of `by · when`, and its text only when non-empty (d-a3h9f3).
- `waiting_text`: the read lines, then `waiting for an agent`, the heads or `nothing`, a blank line, `waiting for the author`, the level-1 blocks then the heads, or `nothing`.
- A write prints `published q-…` or `staged q-…`, or the check lines and `not published: the check failed` with exit 1; `threads` with none prints `no open threads`.
- The hook: a hand edit under `lodge/threads/` gets `THREAD_TEXT`, "{path} is a lodge thread file, and lodge owns it: do not edit it by hand. Add a message with `lodge reply Q --by ROLE FILE`, or close it with `lodge close Q --by ROLE`. " followed by `REVERSE`, in place of `RECORD_TEXT`, whose `lodge draft` refuses threads; test `test_thread_file_edit_names_reply_and_close`.
- `guide.md` gains under Reading: "Run `lodge waiting` at the start of a session, and answer what waits for an agent first." and "`lodge threads` lists the open doubts and questions, and `lodge thread Q` shows one."; under Writing: "`lodge ask REF --kind doubt|question --by ROLE FILE`, `lodge reply Q --by ROLE FILE`, and `lodge close Q --by ROLE [FILE]` write threads.", "Answer a doubt by acting with a decision whose reasoning names the thread, then reply naming the decision; close a thread only when the author asked for it.", and "Write `--by author` only with the author's words verbatim, with `--where` and `--when`."

- [ ] **Step 1: Write the failing tests.**
  - `test_threads.py`: `test_ask_reply_close_round_trip` (`ask` prints `staged q-…`; `threads` lists it; `reply`; `thread` shows both messages in order; `close` then `threads` prints `no open threads`; `thread` ends with the line `closed by coordinator · …`, and its output holds no "Closed."); `test_author_message_needs_where_and_when_exit_2`; `test_where_with_an_agent_role_exit_2`; `test_ask_on_unknown_ref_exit_2`; `test_thread_files_are_staged_not_committed` (`git diff --cached --name-only` lists `lodge/threads/q-…`, `HEAD` unchanged).
  - `test_waiting.py`: the existing test reads its decision block under `waiting for the author`; `test_waiting_groups_threads` (an author-last thread under `waiting for an agent`, an agent-last one under `waiting for the author`).
  - `test_help_lists_every_command.py`: the five new names.
  - `test_guide.py`: `test_guide_says_waiting_first`.
- [ ] **Step 2: Run** `uv run pytest tests/e2e/test_threads.py tests/e2e/test_waiting.py tests/e2e/test_help_lists_every_command.py tests/e2e/test_guide.py tests/hook/test_post_tool_use.py -q`; expected: FAIL.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the builder's gate; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.
