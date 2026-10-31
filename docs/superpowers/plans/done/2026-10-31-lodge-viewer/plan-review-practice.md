# Plan review: practice and buildability

Plan: `docs/superpowers/plans/2026-10-31-lodge-viewer.md` (490 lines, branch `lodge-viewer`).
Angle: whether each task can be built by Codex from its own text plus the Global Constraints, in the sandbox, and whether the plan is proportionate.
Line handles are plan lines unless a path is given.

## Files read

- `CLAUDE.md`, the plan (all of it), the design `docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md` (all of it).
- `docs/superpowers/plans/2026-10-30-lodge-on-itself/task-5-report.md` (lines 95 to 135), `docs/superpowers/plans/2026-10-30-lodge-on-itself.md` (lines 70 to 76), `docs/superpowers/plans/2026-10-31-lodge-viewer/builder-check.md` (first 80 lines).
- `src/lodge/app/ports.py`, `src/lodge/app/lodge.py`, `src/lodge/app/reads.py` (lines 100 to 115), `src/lodge/cli/commands.py` (lines 1 to 60 and the `_read` helpers), `src/lodge/viewer/server.py`, `src/lodge/viewer/html.py` (top), `src/lodge/core/snapshot.py`, `src/lodge/core/check_change.py` (top), `src/lodge/core/yamlio.py` (end), `src/lodge/core/fields.py` (lines 120 to 144), `src/lodge/core/fileformat.py` (lines 30 to 60), `src/lodge/core/views.py` (parts), `src/lodge/hook/post_tool_use.py` (top), `src/lodge/main.py` (parts).
- `tests/structure_tables.py`, `tests/viewer/world.py`, `tests/gitstore/test_concurrent.py` (lines 20 to 70), `pyproject.toml` (vulture and pytest sections), `vulture_allow.py`.
- Line counts of every source module and of the test files the plan extends.

Not read: the remaining bodies of `src/lodge/core/*` beyond the parts above, `tests/structure_rules.py` and the other structure helpers, `advisor-ruling.md`, `advisor-runs.md`, the progress ledger beyond its first lines, `src/lodge/gitstore/*` bodies.
Not run: the plan's tests (none exist yet); I ran one probe, two same-named test files in two folders without `__init__.py`, in a scratch folder (finding B3).

## Blocking

### B1. Tasks cite Calls that the brief does not carry, and the builder needs them

The brief holds the task text and the Global Constraints (lines 19 and 20); "Calls made" (lines 34 to 59), "Spec" (line 14), and "Review Focus" (lines 61 to 67) are in neither.
A builder given Task 1 reads "`derived_order` follows Call 8" (line 101) and "each followed by Call 9's lines" (line 102), and has the placement algorithm and the cross-area line format nowhere in its text.
The same holds for these, each stated in full only in a Call:

- Task 3, line 185 ("Calls 1 to 3"): the escape rule for a message text line that reads `## Message <digits>` (Call 1, line 38) is in no task, yet `test_text_line_like_a_heading_round_trips` (line 220) pins it; `opened` as the sort key (Call 3) is only implied.
- Task 4, line 274 ("Messages per Call 16") and Task 6, line 364 ("per Call 13"), line 365 ("the routes of Call 12"): the four thread commit messages, "the writer's role in place of `author` from the command line", and the CR and whitespace rule for her words are only in Calls 13 and 16 (lines 40 and 43).
  Task 4 repeats half of Call 13 in line 273, Task 6 does not.
- Task 9, line 456 ("in the areas of Call 10"): which section's entries go into which of `model`, `writing`, `reading`, and `storage` is not said anywhere, only that those four are used (line 37).

Fix: before dispatch, inline each of these into the task that uses it (one sentence each; Calls 1, 8, 9, 10, 12, 13, and 16 at least), and add to the Global Constraints "the design is `docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md`; where it and a task disagree, the design wins and the builder reports it", since Tasks 6, 9, and 10 point at design line numbers (lines 363, 453, 460) and the brief has no path for it.
Then "Calls made" can stay as the author's check list and need not be in any brief.

### B2. The temporary-index recipe is in Task 8 only, and Tasks 9 and 11 point at it

Call 21 (line 58) says "(Global Constraints, Task 8)", but the Global Constraints (lines 17 to 32) hold no such line; the recipe is at line 431, inside Task 8.
Tasks 9 and 11 say only "`lodge add` in the sandbox as in Task 8" (lines 452 and 485).
Their briefs hold their own task text, so a builder of Task 9 or 11 runs a plain `lodge add`, hits the read-only index (`task-5-report.md:125-127`), and has no recipe or BLOCKED rule to fall back on.
Fix: move the recipe, the BLOCKED rule, and the "coordinator then runs `git add lodge/`" sentence into the Global Constraints, and make Tasks 8, 9, and 11 say "as in the Global Constraints".

### B3. Two new test modules share a basename in folders without `__init__.py`: pytest stops at collection

Task 3 creates `tests/core/test_threads.py` (line 220) and Task 4 creates `tests/app/test_threads.py` (line 279).
`tests/core/` and `tests/app/` have no `__init__.py`, and `pyproject.toml` sets no import mode, so both import as top-level `test_threads`.
I reproduced the case in a scratch folder: the second file gives "import file mismatch" and `Interrupted: 1 error during collection`, which fails the whole pytest step of the builder's gate for Task 4 and the coordinator's `scripts/check.sh`.
No existing test basename repeats across two such folders today (`test_search.py` repeats only against `tests/e2e`, which is a package).
`tests/e2e/test_threads.py` (line 311) is safe, being in a package.
Fix: name them `tests/core/test_thread_files.py` and `tests/app/test_thread_ops.py`, and add to the Global Constraints "a new test file's basename is unique outside `tests/e2e`, `tests/gitstore`, `tests/hook`, and `tests/viewer`".

## Important

### I1. Adding `Store.commit` breaks a test double the plan does not list

`tests/gitstore/test_concurrent.py:30` defines `Interleaved`, a hand-written `Store` (`trees`, `freshness`, `gate`, `publish`), passed to `lodge_over(store: Store, …)` (line 58 of that file).
Task 4 adds `Store.commit` to the protocol (line 245), so mypy strict fails on that file, and `uv run mypy` is in the builder's gate (line 21).
Task 4's file list (lines 231 to 234) names only `tests/app/fakes.py` among test doubles.
Fix: add `tests/gitstore/test_concurrent.py` to Task 4's Modify list with "`Interleaved.commit` delegates to `inner.commit`".

### I2. `run_thread` in `cli/threads.py` needs `commands._read`, which would make an import cycle

Task 5 puts `run_thread` in `src/lodge/cli/threads.py` (line 290) and says "the message file is read as drafts are (`commands._read`)" (line 302).
`commands.py` must import `run_thread` to dispatch, so `threads.py` importing `commands._read` is a cycle, which `tests/test_structure.py` refuses, and `_read` is private to its module (`src/lodge/cli/commands.py:117`).
Fix: say "move `_read` to a new `src/lodge/cli/files.py` (in the Create list), imported by `commands.py` and `threads.py`" or "`run_thread` takes the file text as an argument and `commands.py` reads it".

### I3. Three existing test files would pass 300 lines

The limit counts tests (line 24).
`tests/core/test_fileformat.py` is 279 lines and gets five tests (line 109); `tests/core/test_feedback.py` is 282 and gets three in Task 1 (line 111) and three in Task 2 (line 150); `tests/viewer/test_pages.py` is 239 and gets eight (line 416).
At eight or more lines a test, each ends above 300, and the structure test fails.
Fix: name new files in the plan: `tests/core/test_fileformat_links.py`, `tests/core/test_area_feedback.py`, `tests/core/test_feedback_links.py`, `tests/viewer/test_pages_threads.py`; or state the rule "a test file that would pass 280 lines gets a new sibling named for the new topic".

### I4. Vulture will flag produced fields that nothing reads until a later task

Vulture runs at `min_confidence = 60` over `src` and `tests` (`pyproject.toml:38-40`), which reports unread dataclass attributes.
Line 27 says to use each name or list it in `vulture_allow.py`, but no task lists any entry.
Examples: `Placed.depth` and `Placed.under` (line 94; `render_spec` prints no indentation, Task 7 first reads them); `ThreadList.titles` and `.read`, `ThreadShown.read`, `ThreadsWaiting.titles` and `.read`, `Written.about` (lines 249 to 253; Tasks 5 and 6 read them, and Task 4's tests, lines 279 to 280, assert none of them).
Fix: in each Produces block add "read first by Task N; the task's tests assert it" and name the test, or give the `vulture_allow.py` line (`Placed.depth  # noqa: B018  read by Task 7`, as the file does today).

### I5. Task 7 and Task 6 leave two interfaces and the form field names unsaid

- `spec_page(areas, read, token, written, area, behind)` (line 400): `written` is never defined.
  The text at line 409 suggests "the `?order=written` flag", but a builder cannot tell that from the signature.
  Fix: `by_dependency: bool` or `order: Literal["dependency", "written"]`, with one sentence.
- Task 6 says the routes read the form (line 365) but names no field, and Task 7 says its forms use "fields as Task 6 reads them" (line 405).
  Only Task 7 names `words`, `id`, `area`, `about`, `kind`, `token` (lines 406 to 407, 410), and the text field of the reply, close, and raise forms is named nowhere.
  A Task 6 builder invents the names that Task 7 then has to match.
  Fix: a table in Task 6: route, fields (`token`, `words`, repeated `id`, `area` for `/confirm`; `token`, `about`, `kind`, `text` for `/threads`; `token`, `text` for reply and close), and Task 7 refers to that table.
- `ThreadList.titles` and `ThreadsWaiting.titles` (lines 250 to 253) have no key: keyed by thread ID or by `about` ID?
  Fix: "keyed by the `about` ID, the title of that record".

### I6. Task 6 is two deliverables and too large for one build and one review

It modifies 16 files and creates 3 (lines 323 to 324), across `core`, `app`, `viewer`, `cli`, and `main`, with 26 named tests plus 5 socket tests.
Two reviewable parts: (a) the confirmation (`core/confirmation.py`, `app/confirm.py`, `StaleList`, `Behind`, `Shown.confirmable`, `Lodge.confirm`, `Lodge.behind_area`; tests `test_confirmation.py`, `test_confirm.py`); (b) the write gate (`viewer/writes.py`, `server.py` `do_POST`, `html.page` notice, `--allow-host`, `main.py` token; tests `test_writes.py`, `test_server.py`).
(b) is where the security review focus (lines 63 to 67) lies and deserves its own review.
Fix: split into 6a and 6b; 6b consumes 6a's `Lodge.confirm`.
This makes twelve tasks, and Call 22 (line 59) says why the count grew once already.

### I7. Task 9 is too large and has no stop short of the whole

It writes 6 author decisions, 6 coordinator decisions, "one entry per claim a reader would look up" for six design sections (the first design needed 40 to 70 entries for a comparable size, `2026-10-30-lodge-on-itself.md:74`), edits 14 named entries plus "any further entry", and a report mapping design lines 21 to 141 (lines 450 to 460).
It would be several hours of Codex output under one review, and a failure at the last section loses the lot (drafts stay, but the report and the checks are all at the end, Step 3).
Fix: split by sections into 9a (the six author decisions, then Goals, Non-goals, Must nots, and Confirming, with the `s-j5ttw1` edit), 9b (Doubts and questions, Rests on, with their five edits), 9c (Arrangement and Security, with `s-v022r0`, `s-dm37qr`, `s-582qav`, `s-nzhyh3`), each with its own part of the report and `lodge check` at its end.
Also state a count bound ("about 30 to 50 entries in all") so a reviewer can tell a thin result from a padded one.

### I8. Task 8 puts judgment over 82 entries in one run

The rule for a link (line 432) is sound but is applied by Codex to every entry of ten areas in one go, with the only per-link check being the reviewer's reading of the report table (line 436).
Step 4's "no new flagged decision" (line 441) has no baseline: `lodge waiting` before the task is not recorded.
Fix: a Step 0 "save `uv run lodge waiting` to `.drafts/waiting-before.txt`", and compare with `diff`; and split the task in two by areas (for example `purpose`, `constraints`, `model`, `levels`, `writing` and `reading`, `hook`, `storage`, `structure`, `rollout`), so a rejected link set costs half the work.
Because a link is only an edit with `link` and is reversible, the split is the lighter fix; I would not add a step.

### I9. Tasks 3 and 4 each hold two independent deliverables

- Task 3 (lines 159 to 226): the thread record (model, `threads.py`, parse and write, snapshot, checks 1, 2, 5) and the doubt marks (`doubts.py`, `derive`, `views` flags, `confirmed by` flag).
  The second needs only a `Thread` value, not the file format.
- Task 4 (lines 228 to 284): `Store.commit` with `gitstore/commit.py` (git state logic, 10 tests against real repositories) and the thread operations in `app/threads.py` (21 tests against `MemoryStore`).
  They share only `Committed`.
Each pair is two diffs a reviewer reads with different questions.
Fix: split Task 3 into 3a (format and checks) and 3b (doubts and flags), and Task 4 into 4a (`Store.commit` and `commit_paths`) and 4b (thread operations); or accept the size and say so under "Calls made".
Of the four splits proposed here (6, 9, 3, 4) I would take 6 and 9 first; 3 and 4 are the lesser.

### I10. Task 7 breaks existing tests it does not list

Task 7 changes `record_page` and `spec_page` to take a token (line 399 to 400) and `render` to take `token` (line 403).
The existing `tests/viewer/test_pages.py` calls `record_page(shown)`, and Task 6's own new `test_get_with_done_shows_notice` (line 375) calls `render(world, urlsplit(…))`, which Task 7 then changes.
Line 27 allows editing existing tests only "where this plan changes the behaviour it pins", but neither task says to update these calls.
Fix: in Task 7 add "update the calls in `tests/viewer/test_pages.py` and `tests/viewer/test_writes.py` to pass `token`", or give `token` a default of `""` in `render` and the page functions' tests.

### I11. The thread file shape contradicts its own writing rule

Line 211 says "`when` and `where` with `yamlio.quoted`", which always JSON-quotes (`src/lodge/core/yamlio.py:77-82`), but the shape at line 207 shows the agent's `when: 2026-10-29T10:00:00+01:00` unquoted, and line 193 shows `opened:` unquoted.
A builder who follows the shape fails a round-trip test, or one who follows the rule fails any byte-for-byte test the reviewer writes against the shape.
Fix: "`opened` and an agent's `when` are written plain, as `date` is for a decision; an author's `when` and `where` with `yamlio.quoted`", and correct the example to match.

## Minor

- **M1.** Line 9 and line 12: "Stack"/"Architecture" paragraphs are fine, but "Calls made" is about 1,800 words of which the builder needs perhaps a fifth (see B1); the "why" and "cost if wrong" parts belong in the ledger as `Ruling:` lines per `CLAUDE.md` ("Build process").
  Moving them would take the plan from 490 lines to about 440 and make it proportionate to the code it asks for.
- **M2.** Lines 124 and 76: test files `test_check_links.py`, `test_derive_links.py`, `test_check_threads.py` (and others) are created by the tasks but only some carry "(new)"; mark each new file, since a builder may look for an existing one.
- **M3.** Task 6 says only that `running` in `tests/viewer/test_server.py` passes a token (line 323); the direct calls `make_server(world, 0)` and `serve(world, port)` at `test_server.py:135, 148, 158, 170` need the new arguments too.
  Mypy catches it, so the builder can find it; name the lines anyway.
  Also say who fixes a failure the coordinator finds in the socket tests (line 379): a fix round with the failing output in the brief.
- **M4.** The `view` help line "serve the read-only viewer on this machine" (`src/lodge/cli/parser.py:132`) is not updated by Task 6 or Task 10; add it to Task 6 with a `test_help_lists_every_command` assertion, or to Task 10 Step 2's grep.
- **M5.** Line 307 says the hook text replaces `RECORD_TEXT`, "whose `lodge draft` refuses threads", but no task makes `lodge draft q-…` refuse: `reads.draft` (`src/lodge/app/reads.py:103-115`) resolves any ID in `s.paths`, which after Task 3 includes threads.
  Add to Task 5: `lodge draft q-…` exits 2 with "threads are written with lodge reply and lodge close", and a test.
- **M6.** Task 10 line 474: "added before the glob" has no referent in this design (it has no glob).
  If it means "edit the design before adding it to `[hook] frozen`", say that order; and add to Step 2 a grep that the README and `CLAUDE.md` additions hold no em-dash and no American spelling, since the prose rules are the only part of Task 10 a test cannot check.
- **M7.** Line 431: `git rev-parse --git-common-dir` prints a relative path (`.git`) in a main checkout; in `GIT_ALTERNATE_OBJECT_DIRECTORIES` that resolves against the object directory.
  Use `git rev-parse --path-format=absolute --git-common-dir` and `--absolute-git-dir`.
- **M8.** Prose rules in the plan: no em-dashes or en-dashes found (checked by script); British English held (no American spellings found); lines 3 and 274 hold two sentences each ("Messages per Call 16." trails line 274), and the Calls (lines 38 to 59) are single sentences strung with semicolons, which keeps the rule to the letter but not its aim; line 274 is the one to split.
  Public-repository rules hold: no personal path, machine name, or other project's record in the plan; fixtures are the made-up `storage` project.
- **M9.** Task 1 Step 4 (line 116) expects `uv run lodge spec` "alphabetically still", true while no entry has `rests_on`; say "and the entry order unchanged" so the check is whole.
- **M10.** Task 11 is ten rank lines (lines 481 to 490).
  It is right to keep apart from Task 8 (records with a decision versus presentation without), but it can share a coordinator round with Task 10 since both are last and small; optional.

## Checked and found sound

- Sandbox verification: each task's builder gate excludes only the two socket files (line 21), and the socket tests of Tasks 6 and 7 are handed to the coordinator (lines 379 and 420).
  Task 4's real-git tests (`test_commit.py`) and Task 5's e2e tests run in `tmp_path` repositories, as the existing gitstore and e2e tests do, so they pass in the sandbox.
- The coordinator/builder split of staging, commit, and push (lines 20 and 22) matches `CLAUDE.md` and the Task 5 report.
- Module-size guards (line 26) are consistent with the line counts: `views.py` 220 plus 30 plus 12, `parser.py` 219 plus 12 plus 8, and `derive.py` 227 plus 15 plus 6 all stay under 300.
- The records tasks give the draft shapes (Task 8, line 434; Task 9, lines 453 to 457) and mark agent text (`decided_by: coordinator`, "answers feedback with no", no author decision replaced).
  The author decisions use her words verbatim from a named design line with an honest `when` range (Call 19), so agent text does not read as hers.
- Plan length against code: 490 lines for roughly 30 new modules and about 200 named tests is proportionate; it is not a transcript, apart from M1.
