# Brief: Task 4 of `docs/superpowers/plans/2026-10-31-lodge-viewer.md`

You build Task 4 of the plan named above, in this repository, on its current branch.
Read `CLAUDE.md` first, then this brief; this brief is your requirements, with the exact values to use verbatim.
Read other parts of the plan only where this brief points to them by name.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Do not commit and do not push: the coordinator stages, runs `sh scripts/check.sh` outside the sandbox, commits, and pushes.
Tests that need sockets fail in your sandbox; run the rest, and name the socket-bound ones in your report.
Write your report to `docs/superpowers/plans/2026-10-31-lodge-viewer/task-4-report.md`: what you changed per file, each test you added with its first failing output, the commands you ran and their last lines, and anything you were unsure of.
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

### Task 4: Thread operations, and the store's commit

**Files:**
- Modify: `src/lodge/app/ports.py`, `src/lodge/app/results.py`, `src/lodge/app/lodge.py`, `src/lodge/app/reads.py` (`show` fills `threads`), `src/lodge/app/writes.py` (`_mint` renamed `mint_unused`; `Added.paths` filled), `src/lodge/app/__init__.py`, `src/lodge/gitstore/checkout.py` (at most 8 lines), `src/lodge/gitstore/branch.py`, `src/lodge/gitstore/setup.py`, `tests/app/fakes.py`, `tests/gitstore/test_concurrent.py` (`Interleaved.commit` delegates to `inner.commit`)
- Create: `src/lodge/app/threads.py`, `src/lodge/gitstore/commit.py`
- Test: `tests/app/test_thread_ops.py` (new), `tests/gitstore/test_commit.py` (new)

**Interfaces:**
- Consumes: Task 3's `Thread`, `Message`, `Raises`, `thread_path`, `write_thread`, `appended`, `clean_text`, `newest_last`, `Snapshot.threads`.
- Produces:
  ```python
  # ports.py
  class CommitOutcome(StrEnum):
      COMMITTED = "committed"; ON_BASE = "on the base branch"; DETACHED = "on a detached HEAD"
      IN_PROGRESS = "during a merge, rebase, cherry-pick, or revert"
      LOCKED = "git's index is locked by another process"; FAILED = "git could not commit"
  @dataclass(frozen=True) class Committed: outcome: CommitOutcome; detail: str = ""
  Store.commit(self, paths: Sequence[str], message: str) -> Committed
  # results.py
  @dataclass(frozen=True) class Written:
      ids: tuple[str, ...]; outcome: AddOutcome; check: CheckResult
      committed: Committed | None = None; about: str | None = None
  @dataclass(frozen=True) class ThreadList: items: tuple[Thread, ...]; titles: Mapping[str, str]; read: Read
  @dataclass(frozen=True) class ThreadShown: thread: Thread; about: Level1; read: Read
  @dataclass(frozen=True) class ThreadsWaiting:
      for_agent: tuple[Thread, ...]; for_author: tuple[Thread, ...]; titles: Mapping[str, str]; read: Read
  Added.paths: tuple[str, ...] = ()          # the files written, set when published or staged
  Shown.threads: tuple[Thread, ...] = ()     # the record's threads, newest last
  # lodge.py
  def ask(self, ref: str, raises: Raises, by: str, text: str, where: str | None = None,
          when: str | None = None, commit: bool = False) -> Written
  def reply(self, thread: str, by: str, text: str, where: str | None = None,
            when: str | None = None, commit: bool = False) -> Written
  def close(self, thread: str, by: str, text: str | None = None, where: str | None = None,
            when: str | None = None, commit: bool = False) -> Written
  def threads(self) -> ThreadList                  # open threads, newest last
  def thread(self, ref: str) -> ThreadShown        # a thread ID in any case; NotFound "no thread named X"
  def threads_waiting(self) -> ThreadsWaiting      # open; last message by author -> for_agent, else for_author
  # writes.py
  def mint_unused(ids: IdSource, prefix: Literal["d", "s", "q"], taken: Collection[str]) -> str
  # gitstore/commit.py
  def commit_paths(root: Path, base: str, paths: Sequence[str], message: str,
                   retry_seconds: float, sleep: Callable[[float], None] = time.sleep) -> Committed
  CheckoutStore(root, settings, common_dir, lock_wait_seconds, index_retry_seconds: float = 1.0)
  ```
- `titles` maps each thread's `about` ID to that record's title; `Written.about` is the thread's `about` for a thread write and None otherwise.
- Rules in `app/threads.py`, each refusal a `LodgeError` naming the fault:
  - the text follows the Global Constraints' CR rule and, for `ask` and `reply`, must not be empty (`the message is empty`);
  - `by` must be non-empty, and a `by` other than `author` holding "author" in any case is refused (`write author exactly, or use your own role`);
  - an author message needs `where` (`a message by author needs where, the place of the author's words`) and takes `when` from the clock's minute (`%Y-%m-%d %H:%M`) when none is given;
  - an agent message takes `when` from the clock (`isoformat(timespec="seconds")`) and may not carry `where` or `when` (`where and when are for messages by author`);
  - a `where`, `when`, or text that a header cannot carry (`write_thread` raises `ValueError`) is refused naming the field;
  - `ask` resolves `ref` with `resolve_ref` (an ID or a code), mints a `q-` ID with `mint_unused`, and stamps `opened` from the clock;
  - `reply` and `close` refuse a closed thread (`{q} is closed`); `close` takes the given text, cleaned the same way, or an empty text when none is given or the cleaned text is empty, appends it by the closer as the closing message, and sets `closed` (d-a3h9f3).
- Each write reads the state, builds the thread file, and runs `core.check_change(load(published), after, settings, now, snapshot)`; a failing check returns `Written(…, AddOutcome.CHECK_FAILED, check)` and writes nothing.
  Otherwise it calls `store.publish(current, {path: text}, message)`, starting again on `REJECTED`, at most three times, then `Conflict`; on `STAGED` with `commit=True` it calls `store.commit((path,), message)`; the command line never passes `commit=True`.
- Commit and publish messages, `ROLE` being `by`: `Thread {q}: doubt raised by ROLE`, `Thread {q}: question asked by ROLE`, `Thread {q}: ROLE reply`, `Thread {q}: closed by ROLE`.
- `commit_paths`, in order: `git symbolic-ref --quiet --short HEAD` failing is `DETACHED`; the branch equal to `base` is `ON_BASE`; any of `git rev-parse --git-path` `MERGE_HEAD`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`, `rebase-merge`, `rebase-apply`, or `sequencer` existing is `IN_PROGRESS`; then `git commit --only --quiet -m MESSAGE -- PATHS`, with no identity of its own and no `--no-verify`, so the checkout's identity and hooks apply; stderr naming `index.lock` sleeps `retry_seconds` and tries once more, then `LOCKED`; any other failure is `FAILED` with git's first line as `detail`.
- `BranchStore.commit` raises `LodgeError("branch mode commits when it publishes")`; `MemoryStore` gains `commits: list[tuple[tuple[str, ...], str]]` and `commit_result: Committed`, default `Committed(CommitOutcome.COMMITTED)`.

- [ ] **Step 1: Write the failing tests.**
  - `test_thread_ops.py`: `test_ask_writes_a_thread_file` (one publish at `lodge/threads/q-111111.md`, read back: `about == "s-aaaaaa"`, `raises is Raises.DOUBT`, open, one message by `coordinator` at `START.isoformat(timespec="seconds")`, `written.about == "s-aaaaaa"`); `test_ask_resolves_a_code`; `test_ask_on_an_unknown_ref_is_not_found`; `test_author_message_needs_where`; `test_author_when_defaults_to_the_minute` (`"2026-10-29 09:30"`); `test_agent_message_may_not_carry_where`; `test_role_like_author_refused` (`"Author"`, `"the author"`); `test_empty_text_refused`; `test_text_loses_cr_and_outer_whitespace_only`; `test_unstorable_where_refused` (`"a\x01"`: `LodgeError`, nothing published); `test_reply_appends`; `test_reply_to_closed_thread_refused`; `test_close_appends_closed_by_the_closer` (the closing message's `text == ""`, its `by` the closer); `test_close_without_text_passes_the_check`; `test_close_with_text`; `test_rejected_publish_starts_again`; `test_commit_after_staged_when_asked` (author, `where="a session"`: `store.commits == [(("lodge/threads/q-111111.md",), "Thread q-111111: doubt raised by author")]`, `written.committed.detail == ""`); `test_no_commit_unless_asked`; `test_no_commit_when_published`; `test_threads_lists_open_newest_last` (`titles["s-aaaaaa"] == "Transcripts are kept"`, `read.freshness` set); `test_thread_shows_one_thread` (`shown.read.freshness` set); `test_threads_waiting_groups` (and its `titles` and `read`); `test_show_carries_the_records_threads`; `test_added_paths_lists_the_files_written`; `test_search_and_timeline_leave_threads_out`.
  - `test_commit.py` (a work branch in a `tmp_path` repository): `test_commits_only_the_named_paths` (another staged file stays staged: `git diff --cached --name-only` lists it alone); `test_commit_takes_the_checkouts_identity` (author is the repository's configured name); `test_no_commit_on_the_base_branch` (`ON_BASE`, the file still staged, `HEAD` unchanged); `test_no_commit_on_a_detached_head`; `test_no_commit_during_a_merge` (a real conflicting merge); `test_no_commit_during_a_revert` (a real conflicting revert; `REVERT_HEAD` still there after); `test_no_commit_during_a_rebase` (a `rebase-merge` folder at its git path); `test_no_commit_during_a_cherry_pick`; `test_locked_index_retries_once_then_locked` (`index.lock` present, `sleep` recorded once); `test_lock_gone_on_retry_commits` (the `sleep` given removes the lock); `test_other_failure_is_failed_with_gits_line`.
- [ ] **Step 2: Run** `uv run pytest tests/app/test_thread_ops.py tests/gitstore/test_commit.py -q`; expected: FAIL.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the builder's gate; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.
