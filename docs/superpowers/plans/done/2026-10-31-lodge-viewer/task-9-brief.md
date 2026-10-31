# Brief: Task 9a of `docs/superpowers/plans/2026-10-31-lodge-viewer.md`

You build Task 9a of the plan named above, in this repository, on its current branch.
Read `CLAUDE.md` first, then this brief; this brief is your requirements, with the exact values to use verbatim.
Read other parts of the plan only where this brief points to them by name.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Do not commit and do not push: the coordinator stages, runs `sh scripts/check.sh` outside the sandbox, commits, and pushes.
Tests that need sockets fail in your sandbox; run the rest, and name the socket-bound ones in your report.
Write your report to `docs/superpowers/plans/2026-10-31-lodge-viewer/task-9a-report.md`: what you changed per file, each test you added with its first failing output, the commands you ran and their last lines, and anything you were unsure of.
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

### Tasks 9a, 9b, and 9c: This design into lodge

Each of the three is its own brief, build, and review, in this order, and each holds the rules below as well as its own part.

**Files:** records via `lodge add`; report `docs/superpowers/plans/2026-10-31-lodge-viewer/task-9-report.md`, which each part extends.

**Interfaces:**
- Consumes: Tasks 1 to 8; the design; d-7w5aq0; the records named below.
- Produces: six author decisions, six coordinator decisions, their entries, and the edits and narrowings below; about 20 to 40 new entries in all.

Rules for every part:
- `lodge add` as in the Global Constraints.
- A coordinator decision per design section, `decided_by: coordinator`, `scope: product`, creating the entries for its section's claims, one per claim a reader would look up on its own, within 150 words, saying what holds now, each with `rests_on` where it would not hold without another entry (Task 8's rule).
- An entry's area by its topic: Goals, Non-goals, and Must nots in `purpose`; a record kind, a field, or an action in `model`; a check, feedback, the review flag, or what waits in `writing`; the viewer, `lodge spec`, or a read in `reading`; where files live or how the store commits in `storage`.
- Its reasoning carries the section's reasons, names d-7w5aq0 for each claim the design marks **[advisor]**, and says which claims are the coordinator's calls.
- It narrows the coordinator decisions whose statements it makes false, never an author decision, and answers any other "looks related" feedback with no.
- After each section's add, `uv run lodge spec | grep 'changed since'`: each entry that still holds is listed in the next decision of the same part with `edit`, its text unchanged, and one reasoning line saying why it holds (design line 113); an entry that no longer holds is edited.
- Each part's report section: each new entry with its decision and the design lines it holds; each edited entry with the sentence that changed; each narrowed decision with why.

**Task 9a: her quotes, the Goals, and Confirming.**
- First six author decisions, one per quote of design lines 13 to 18, never lines 12 and 19, which d-dyrpc6 and d-2hcgav already record: `decided_by: author`, `scope: product`, `quote: {text: <only the words inside the quotation marks, verbatim>, where: "lodge build session", when: <below>}`, reasoning equal to the quote text and nothing else, and a statement saying only what the words settle:
  - line 13, `when: "2026-10-30 09:41"`: a doubt or question about an entry is raised and answered on that entry;
  - line 14, `when: "2026-10-30 09:41"`: entries are ordered or arranged by their dependencies;
  - line 15, `when: "2026-10-30 09:43"`: the arrangement shows what rests on what, so a wrong point resting on another wrong point shows;
  - line 16, `when: "2026-10-30 09:46"`: points resting on a wrong one are retired or corrected as appropriate;
  - line 17, `when: "2026-10-30 09:47"`: the author, an agent, or both work that out;
  - line 18, `when: "2026-10-30 09:37"`: confirming a record does not show it as written by the author, and who wrote what stays visible.
- Then the decision for Goals, Non-goals, and Must nots (design lines 21 to 47), then the one for Confirming (design lines 48 to 73), which edits s-j5ttw1 (no "There is no confirmation step"; a confirmation is a separate author record) and says in its reasoning that LODGE-6 (d-8nkamy) still makes a confirmed decision count as hers for the review flag.

**Task 9b: Doubts and questions, and Rests on.**
- The decision for Doubts and questions (design lines 75 to 100) says in its reasoning that threads reach decisions too, the extension of her words on entries (d-7w5aq0, design line 78); it edits s-a67fqm (three record kinds), s-evv024 (`lodge/threads/`), s-0s9m2d (the two groups of what waits), s-ms14fq (check 5 covers threads), s-wcv4en (level 1 carries the marks as well as any review flag), and s-7ah5n7 (one sentence after its first: a thread, a doubt or question on a decision or entry with its messages, is not such a kind: it holds no claim of its own, and what it settles enters lodge as a decision; its statement otherwise unchanged).
  Its entry on closing states that a close without text appends a closing message with no text, shown as "closed by" its writer, not design line 85's "Closed."; its reasoning names d-a3h9f3 for that entry and for the s-7ah5n7 edit, and names the line 13 author decision of Task 9a for the s-7ah5n7 edit.
- The decision for Rests on (design lines 102 to 114) edits s-0yzshh (the `link` action), s-01k42c (a `link` raises no flag), s-j70a0k (eight checks), s-edgt71 (all eight), s-8f6scf (`rests_on` is stored on the entry), and s-aw5a1j (check 6 covers an entry edited in the change), and narrows d-zerbz9, d-3epcjd, and d-4032xv, the coordinator decisions behind "links on the decision only" and "seven checks".

**Task 9c: Arrangement and Security.**
- The decision for Arrangement (design lines 116 to 122) edits s-v022r0 (areas by rank, entries after what they rest on); its entry on the dependency view states "dependants follow what they rest on, siblings in the area's order", and its reasoning names d-a3h9f3.
- The decision for Security (design lines 124 to 132) edits s-dm37qr, s-582qav, and s-nzhyh3 (the viewer writes confirmations and threads only).
- The report closes with every design line from 21 to 141 mapped to an entry or named as left out, with the reason.

- [ ] **Step 1 (each part):** `uv run lodge id s` per new entry; drafts of the new and edited entries and the decision; dry-run; add; the "changed since" pass.
- [ ] **Step 2: Verify (each part)** `uv run lodge check` prints `ok`; `uv run lodge spec | grep -c 'changed since'` prints 0, or the report names each remaining mark and why; in 9a, `uv run lodge search --by author --limit 50` lists the six and `uv run lodge show s-j5ttw1` no longer holds "There is no confirmation step"; in 9c, `uv run lodge spec --area reading` names the viewer's writes.
- [ ] **Step 3: Coordinator (each part):** `git add lodge/`, `sh scripts/check.sh`, commit, push.
