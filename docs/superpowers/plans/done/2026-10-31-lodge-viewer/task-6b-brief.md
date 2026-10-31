# Brief: Task 6b of `docs/superpowers/plans/2026-10-31-lodge-viewer.md`

You build Task 6b of the plan named above, in this repository, on its current branch.
Read `CLAUDE.md` first, then this brief; this brief is your requirements, with the exact values to use verbatim.
Read other parts of the plan only where this brief points to them by name.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Do not commit and do not push: the coordinator stages, runs `sh scripts/check.sh` outside the sandbox, commits, and pushes.
Tests that need sockets fail in your sandbox; run the rest, and name the socket-bound ones in your report.
Write your report to `docs/superpowers/plans/2026-10-31-lodge-viewer/task-6b-report.md`: what you changed per file, each test you added with its first failing output, the commands you ran and their last lines, and anything you were unsure of.
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

### Task 6b: The viewer's write gate

**Files:**
- Modify: `src/lodge/viewer/server.py`, `src/lodge/viewer/html.py` (`page` takes a notice), `src/lodge/viewer/__init__.py` (docstring "The local web viewer"), `src/lodge/cli/parser.py` (`--allow-host` and the `view` help, at most 8 lines), `src/lodge/cli/commands.py`, `src/lodge/main.py`, `tests/viewer/world.py` (`staged_world`), `tests/viewer/test_server.py`, `tests/e2e/test_view.py`
- Create: `src/lodge/viewer/writes.py`
- Test: `tests/viewer/test_post_gate.py` (new), `tests/viewer/test_post_routes.py` (new)

**Interfaces:**
- Consumes: Task 6a's `Lodge.confirm`, `StaleList`; Task 4's `Lodge.ask`, `reply`, `close`, `Written`, `Committed`, `CommitOutcome`.
- Produces:
  ```python
  # viewer/writes.py
  MAX_BODY = 65_536
  NOTICES: Mapping[str, str]
  @dataclass(frozen=True) class Gatekeeper: token: str; hosts: frozenset[str]   # ValueError if len(token) < 32
  @dataclass(frozen=True) class Reply: status: HTTPStatus; text: str; location: str | None = None
  def allowed_hosts(port: int, extra: Sequence[str]) -> frozenset[str]   # lower case
  def done_code(written: Written) -> str
  def refuse_early(gate: Gatekeeper, headers: Mapping[str, str]) -> Reply | None  # the Host and Origin checks
  def handle_post(make_lodge: Callable[[], Lodge], gate: Gatekeeper, path: str,
                  headers: Mapping[str, str], body: bytes) -> Reply      # headers keyed in lower case
  # viewer/server.py
  def make_server(make_lodge: Callable[[], Lodge], port: int, *, token: str,
                  allow_hosts: Sequence[str] = ()) -> ThreadingHTTPServer
  def serve(make_lodge: Callable[[], Lodge], port: int, allow_hosts: Sequence[str], token: str) -> int
  def render(make_lodge: Callable[[], Lodge], url: SplitResult) -> tuple[HTTPStatus, str, str]  # was _render
  # html.py
  def page(title: str, body: str, read: Read, notice: str | None = None) -> str
  # cli
  View(port: int, allow_hosts: tuple[str, ...])   # run's view callable takes (port, allow_hosts)
  # tests/viewer/world.py
  def staged_world() -> tuple[Callable[[], Lodge], MemoryStore]   # one staged store behind every Lodge made
  ```
- The routes and their form fields, which Task 7's forms use as given:

  | Route | Fields |
  | --- | --- |
  | `POST /confirm` | `token`, `words`, `id` (one or more), `area` (from an area's page only) |
  | `POST /threads` | `token`, `about`, `kind` (`doubt` or `question`), `text` |
  | `POST /threads/<q>/reply` | `token`, `text` |
  | `POST /threads/<q>/close` | `token`, `text` (empty means none) |

- `refuse_early`: a `Host` not in `gate.hosts` is 403; no `Origin` is 403 (`a write needs an Origin header`); an `Origin` other than `http://` or `https://` followed by an allowed host, compared in lower case, is 403.
- `handle_post`, in order: `refuse_early`; a `Content-Type` other than `application/x-www-form-urlencoded` (parameters allowed) is 415; a body over `MAX_BODY` is 413; a body that is not UTF-8 is 400; `parse_qs(text, keep_blank_values=True, max_num_fields=200, errors="strict")`, a `ValueError` or `UnicodeDecodeError` being 400; anything but exactly one `token` field whose UTF-8 bytes equal `gate.token.encode("ascii")` under `hmac.compare_digest` is 403 (`this form is stale or from elsewhere; reload the page`); an `id` that is not a `d-` ID, or a `<q>` that is not a `q-` ID, is 400; then the route, writing as `author` with `where` `lodge viewer` and `commit=True`, under one module-level `threading.Lock` held from the route's first read to its last write, so a second request reads what the first wrote.
- Answers: a write answers `303` with `Location` `/r/{id}?done={code}` for a single confirmation, `/spec?area={area}&done={code}` for an area, the same two with `done=stale` on `StaleList`, and `/r/{about}?done={code}#{q}` for a thread write; each path part goes through `urllib.parse.quote(part, safe="")`; a failed check, a refused input, or empty words is 400 with the reason, a link back to the form's page, and nothing written; `NotFound` is 404; anything else is 500 with the error on stderr.
- `NOTICES`: `committed` "Written and committed."; `published` "Written and published."; `staged` "Written and staged, not committed."; `staged-base` "Written and staged, not committed: this checkout is on the base branch."; `staged-detached` "Written and staged, not committed: HEAD is detached."; `staged-in-progress` "Written and staged, not committed: a merge, rebase, cherry-pick, or revert is in progress."; `staged-locked` "Written and staged, not committed: git's index is locked by another process."; `staged-failed` "Written and staged, not committed: git could not commit; the terminal running lodge view says why."; `stale` "The list changed since the page was loaded, so nothing was written; check the new list."
  A `FAILED` commit's detail goes to stderr.
- `render` reads `done` and passes `NOTICES.get(code)` to `page`, shown as `<p class="notice" role="status">`; an unknown code shows nothing.
- `server.py`: `do_POST` runs `refuse_early` first, then reads `Content-Length` (missing 411, not `[0-9]+` 400, over `MAX_BODY` 413, the body unread in each), then calls `handle_post`, and sends `Location` on a 303; `_Handler.timeout = 10`, so a stalled body never holds the server; `PUT`, `PATCH`, `DELETE`, and `OPTIONS` stay 405 with `Allow: GET, HEAD, POST`; the `GET` host check uses `gate.hosts`; the 405 page reads "this address takes no such request".
- `lodge view --allow-host HOST`, repeatable: a value with whitespace or `/`, or empty, is a usage error, exit 2; the `view` help reads "serve the viewer on this machine: read, confirm, and raise doubts"; `main.py` mints `secrets.token_urlsafe(32)` and passes it to `serve`.

- [ ] **Step 1: Write the failing tests.**
  - `test_post_gate.py` (no socket): `test_no_origin_refused`; `test_foreign_origin_refused`; `test_origin_needs_scheme_and_allowed_host` (`ftp://127.0.0.1:8787` and `http://127.0.0.1:8788` refused, `https://localhost:8787` accepted); `test_allow_host_matches_the_whole_host` (`proxy.example:443` allowed, Host `proxy.example` refused); `test_missing_token_refused`; `test_wrong_token_refused`; `test_two_token_fields_refused`; `test_non_ascii_token_refused` (403, no exception); `test_token_compared_with_hmac` (a spy on `writes.hmac.compare_digest` is called); `test_wrong_content_type_415`; `test_body_over_limit_413`; `test_non_utf8_body_400`; `test_bad_percent_escape_400` (`words=%FF`); `test_too_many_fields_400`; `test_bad_id_400`; `test_short_token_refused_by_gatekeeper`.
  - `test_post_routes.py` (no socket; `staged_world()`): `test_confirm_redirects_with_done_code` (303, `Location == "/r/d-cccccc?done=committed"`); `test_area_confirm_redirects_to_the_area`; `test_stale_list_redirects_with_stale`; `test_two_concurrent_confirmations_write_once` (two threads, the store's first `publish` held until the second thread has entered `make_lodge`, which it calls before taking the write lock: one publish, one `done=committed`, one `done=stale`); `test_failed_check_answers_400_and_writes_nothing`; `test_ask_from_viewer_records_her_words` (message by `author`, `where == "lodge viewer"`, `when == "2026-10-29 09:30"`, text as typed); `test_unknown_kind_400`; `test_reply_and_close_redirect_to_the_thread`; `test_viewer_writes_only_new_decisions_and_thread_files` (for each route, every published path is a thread path or a decision path absent before); `test_staged_on_base_gives_staged_base` (`commit_result = Committed(CommitOutcome.ON_BASE)`); `test_get_with_done_shows_notice` (`render(make, urlsplit("/r/d-aaaaaa?done=committed"))` holds "Written and committed.").
  - `tests/e2e/test_view.py`: `test_view_passes_the_port_to_the_viewer` takes `view(port, allow_hosts)`; `test_allow_host_is_repeatable_and_passed`; `test_allow_host_with_space_slash_or_empty_exits_2`; the builder runs these three with `-k`.
  - `tests/viewer/test_server.py` (sockets; the coordinator runs them): `running` (line 20) and the direct calls at lines 135, 148, 158, and 170 pass a token; `test_only_reads_are_served` expects 403 for a `POST` without an `Origin`; new `test_post_through_the_socket_redirects`; `test_put_answers_405_allowing_post`; `test_allow_host_is_served`; `test_post_without_length_411` (allowed `Host` and `Origin`); `test_negative_length_400`.
- [ ] **Step 2: Run** `uv run pytest tests/viewer/test_post_gate.py tests/viewer/test_post_routes.py -q` and `uv run pytest tests/e2e/test_view.py -q -k "passes_the_port or allow_host"`; expected: FAIL.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the builder's gate and the `-k` run; expected: green; the coordinator runs `uv run pytest tests/viewer/test_server.py tests/e2e/test_view.py -q` outside the sandbox.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.
