# Brief: Task 10 of `docs/superpowers/plans/2026-10-31-lodge-viewer.md`

You build Task 10 of the plan named above, in this repository, on its current branch.
Read `CLAUDE.md` first, then this brief; this brief is your requirements, with the exact values to use verbatim.
Read other parts of the plan only where this brief points to them by name.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Do not commit and do not push: the coordinator stages, runs `sh scripts/check.sh` outside the sandbox, commits, and pushes.
Tests that need sockets fail in your sandbox; run the rest, and name the socket-bound ones in your report.
Write your report to `docs/superpowers/plans/2026-10-31-lodge-viewer/task-10-report.md`: what you changed per file, each test you added with its first failing output, the commands you ran and their last lines, and anything you were unsure of.
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

### Task 10: The documents

**Files:**
- Modify: `README.md`, `CLAUDE.md`, `docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md` (one line at the end), `.lodge.toml` (`[hook] frozen`)

- `README.md`: What it holds (threads; `rests_on`); Reading (`threads`, `thread`, `waiting` in two groups, `spec` by rank and dependency); Writing (`rests_on`, the `link` action, `ask`, `reply`, `close`, author messages with `--where` and `--when`, threads stage like `add`); the check (eight checks, and which a thread can fail); The viewer (no longer read-only: confirming and threads; the token, `Origin`, and `--allow-host`; commits in checkout mode and when it does not commit); every command and string as built, read from `uv run lodge --help` and the code.
- `CLAUDE.md`: a line "Run `uv run --frozen --quiet lodge waiting` at the start of a session and answer what waits for an agent first."
- The design document gets its last line first, "Its content now lives in lodge (`lodge spec`, `lodge show`); this document is frozen."; only then does `.lodge.toml`'s `frozen` gain `"docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md"`, so the hook does not fire on that edit.

- [ ] **Step 1:** Edit the four files in that order.
- [ ] **Step 2: Verify** every command the README names runs (`uv run lodge <command> --help` exits 0); `git grep -n 'read-only' -- README.md src/` names nothing about the viewer; `git grep -nP '\x{2014}|\x{2013}' -- README.md CLAUDE.md` prints nothing; `printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"},"cwd":"%s"}' "$PWD/docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md" "$PWD" | uv run --frozen --quiet lodge hook post-tool-use` prints the frozen-file feedback.
- [ ] **Step 3: Coordinator:** `sh scripts/check.sh`, commit, push.
