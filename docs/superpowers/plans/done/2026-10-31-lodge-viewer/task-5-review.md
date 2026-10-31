# Task 5 review

Reviewed commit 2bafed4 (`git diff 29976d1 2bafed4 -- src tests`), in a detached scratch worktree of that commit.
Passes in order: correctness, practice, design.

Counts: Blocking 0, Important 3, Minor 7.

## Gate and probes I ran

- `uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py` passes (the whole run, no failures); `ruff format --check`, `ruff check`, `mypy`, and `vulture` are clean.
- A scratch e2e test (deleted afterwards) drove `ask`, `reply`, `close`, `thread`, `threads`, and `waiting` through `main` in a seeded project.
- Not run: `tests/viewer/test_server.py` and `tests/e2e/test_view.py::test_view_serves_the_project_until_interrupted` (sockets); `sh scripts/check.sh` (the coordinator's gate).
- The check-failed branch of `run_thread` could not be reached from the command line in any probe, so it is unrun.

## What is right

- Exit codes and refusals match the brief: `--by author` without both flags, and `--where` or `--when` with another role, exit 2 with the brief's two sentences verbatim; an unknown thread or record exits 2 with a one-line `lodge:` error and no usage text.
- `waiting` prints the two groups in the brief's order, with `nothing` for an empty group and a blank line between them; the author group lists the level-1 blocks before the thread heads (`thread_output.py:35`).
- `thread` ends a closed thread with `closed by coordinator · …` and holds no "Closed." (probe confirmed; a closing message with text shows it under that line).
- Threads are staged and never committed by the command line; `HEAD` is unchanged.
- The hook routes `lodge/threads/` to `THREAD_TEXT` through `is_relative_to(data_root / "threads")`, so `lodge/threadsfoo/` would not match.
- Structure rules hold: `parser.py` grows by six lines and loses two (limit 12) and stays at 227 lines; no module is near 300; no import cycle.
- The coordinator's two `test_same_second.py` edits are sound (see Minor 7).

## Important

### I1. A lone CR in a message file becomes an LF, so the author's text is not recorded exactly

- Handle: `src/lodge/cli/threads.py:99` calls `read_file(command.file, "not UTF-8 text", False)`; `src/lodge/cli/files.py:11` then uses `Path.read_text`, which applies universal newlines.
- Scenario: a file holding `indented\rlone CR` is stored as two lines (probe: the thread file read `indented\nlone CR`).
  The brief says message text loses "a CR before each LF and the whitespace around it, nothing else", and `core.clean_text` (`src/lodge/core/threads.py:141`) already removes `\r\n` itself.
  So `--by author` text from a file with old-Mac or pasted CRs is altered before lodge sees it, which breaks "records her text exactly".
- Fix: read the message file with `exact=True` (`read_bytes().decode("utf-8")`, as attachments are) and let `clean_text` do the one permitted change.
  Add a test that a file containing `a\rb` and `c\r\nd` is stored as `a\rb` and `c\nd`.
  The brief's phrase "as drafts are" names `read_file`, not its `exact` flag, so this does not contradict it.

### I2. The guide loses two introductory sentences and every blank line after a heading to stay under 60 lines

- Handle: `src/lodge/cli/guide.md:2` and the headings at lines 6, 17, and 54; the cap is `tests/e2e/test_guide.py:18` (`<= 60`).
- Scenario: the builder deleted "lodge holds a project's decisions and specification entries." and "An area is a named group with a title, an intro, and the order of its entries." (`git diff 29976d1 2bafed4 -- src/lodge/cli/guide.md`).
  The guide now says "belongs to an area" and later "an area draft has `kind: area`" with no definition of an area anywhere, and the first line an agent reads no longer says what lodge holds.
  The brief asked only for additions; the report mentions the trim but does not name the area sentence.
  The new Reading lines also sit above a blank line, so that section now has a one-line paragraph break in its middle, while every heading lost its blank line.
- Fix: this is the author's call, since the cap is an existing test.
  Either raise the cap (the guide gains 6 lines) and restore the two sentences and the heading spacing, or keep the cap and fold the two Reading sentences into existing lines (for example append `lodge threads` and `lodge thread Q` to the "read" sentence at line 9) and restore at least the area sentence.
  The brief's Reading and Writing sentences must stay verbatim either way.

### I3. No test reads an author message back, so the feature in the Review Focus is unpinned

- Handle: `tests/e2e/test_waiting.py:47` and `tests/e2e/test_threads.py` (the round trip uses only agent roles).
- Scenario: the only author-role success path creates a thread and checks the group it lands in; nothing asserts that `thread` prints `author · WHEN · WHERE` with her text exactly, or that the stored file holds her words.
  The ` · where` suffix branch (`thread_output.py:23`) is therefore run by no assertion, and I1 passed unnoticed.
  Also untested: the `published q-…` outcome line, the check-failed path with exit 1 and `not published: the check failed` (`threads.py:107`), a missing or non-UTF-8 message file, and `reply` or `close` on an unknown or closed thread.
- Fix: add to `tests/e2e/test_threads.py` (99 lines, room for about 200):
  `test_author_words_are_recorded_exactly` (ask `--by author --where chat --when "2026-10-31 12:00"` with a CRLF, multi-line file; `thread` shows `author · 2026-10-31 12:00 · chat` then the text; the thread file holds the same text);
  `test_reply_to_unknown_or_closed_thread_exit_2`;
  `test_missing_message_file_exit_2`.
  For the check-failed branch, a unit test of `run_thread` with a stub `Lodge` returning `Written(..., AddOutcome.CHECK_FAILED, ...)` is enough.

## Minor

1. `src/lodge/cli/thread_output.py:10`: a thread with one message prints `1 messages`.
   The brief pins only `2 messages`.
   Fix: `f"{n} message{'s' if n != 1 else ''}"` and extend `test_ask_reply_close_round_trip` to assert `1 message ·` after the ask.
2. `src/lodge/cli/commands.py:80`: `waiting` makes two store reads (`lodge.waiting()` and `lodge.threads_waiting()`), each with its own freshness line, deduplicated with `dict.fromkeys` in `thread_output.py:37`.
   A write landing between the reads shows decisions and threads from different snapshots, and in branch mode two different freshness lines would both print.
   Fix: one app call returning both groups (a Task 4 follow-up), after which `waiting_text` takes one `Read`.
3. `src/lodge/hook/post_tool_use.py:74`: `"threads"` is a bare string, where `ATTACHMENTS` is a named constant beside it.
   Fix: a `THREADS = "threads"` constant next to `ATTACHMENTS`.
4. `src/lodge/cli/threads.py:63`: `--by`, `--where`, and `--when` have no `help=`, while the other options in `parser.py` do, so `lodge ask --help` does not say that `--where` and `--when` are for author messages.
   Fix: one-line help strings, for example `--where`: "for --by author: where the words were said".
5. `src/lodge/cli/threads.py:90` re-dispatches with an `isinstance` chain on the same five classes that `commands.py:82` already matched, and `Ask`, `Reply`, and `Close` repeat four fields.
   Not wrong; a `match` in `run_thread` would read like its caller, and the three dataclasses could share a base.
6. `src/lodge/cli/thread_output.py:21`: `thread_text` joins the head, `"\n\n"`, and the messages inside another `"\n".join`, which is harder to read than building the body once.
   `README.md:45` still describes `waiting` as "agent decisions that wait for the author"; Task 10's README list already covers `waiting` in two groups, so no action beyond keeping that line.
7. Tests for the grouping are looser than the brief's wording.
   `tests/e2e/test_waiting.py:50` splits on the second heading but never checks that `waiting for an agent` comes first or that the level-1 blocks precede thread heads in the author group.
   `tests/e2e/test_same_second.py:26` and `:43` find the decision after the `waiting for the author` heading (a correct, robust update of the old position assertions) but would also pass if the decision were listed in both groups.
   Fix: assert `out.index("waiting for an agent") < out.index("waiting for the author")`, and add one author-group assertion with a flagged decision and an agent-last thread together.

## Design: what Tasks 6 to 10 consume

- Task 6a to 7 call the app (`Lodge.ask`, `reply`, `close`, `threads`, `thread`, `threads_waiting`), not the Task 5 functions; the plan names none of `thread_head`, `thread_text`, `waiting_text`, or `read_file` outside Task 5 (`git grep` in the plan), so nothing downstream breaks.
- The viewer will need the same author-provenance rule (`where` and `when` required for the author) that `_message_command` holds in the command line; it sets them itself (`lodge viewer`, the clock's minute), so there is no coupling to remove.
- Task 10's README, `CLAUDE.md`, and freeze line are unaffected; the design document edit at line 85 (d-a3h9f3) is consistent with the code.
- Plan assumption met: `commands._read` moved to `cli/files.py` with no cycle (`files` imports only `lodge.app`).

## Files read

`CLAUDE.md`, `task-5-brief.md`, `task-5-report.md`, the full `git diff 29976d1 2bafed4 -- src tests` (all 18 files), `src/lodge/cli/{commands,parser,threads,thread_output,files,output,guide}`, `src/lodge/app/threads.py`, `src/lodge/app/lodge.py`, `src/lodge/app/results.py`, `src/lodge/app/reads.py`, `src/lodge/core/threads.py` (`clean_text`), `src/lodge/hook/post_tool_use.py`, `src/lodge/main.py`, `tests/e2e/{conftest,support,test_threads,test_waiting,test_same_second,test_guide}.py`, `tests/hook/test_post_tool_use.py`, the design lines on threads and waiting, the plan's Tasks 5 and 10 and its grep for Task 5 names.

Not read: the spec `docs/superpowers/specs/2026-10-29-lodge-design.md` beyond what the design and brief quote; `src/lodge/gitstore`; `tests/structure_rules.py` (run, not read); the Task 6 to 9 briefs.
