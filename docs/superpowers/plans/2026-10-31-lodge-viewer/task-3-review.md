# Task 3 review: threads in core (commit 68c4572)

Reviewed the commit, not the working tree, in a scratch worktree of 68c4572 (removed afterwards).
Result: 0 Blocking, 3 Important, 7 Minor.
Gate on the commit: `ruff format --check`, `ruff check`, `mypy`, `vulture` clean; `pytest -q` without the two socket files, 1154 passed.

## Files read

Brief, report, the design's "Doubts and questions" (lines 75 to 100), d-7w5aq0 and d-a3h9f3 with `--reasoning`, the plan's Task 3 to 5 sections and Calls 13, 20, 27, 31.
Source at 68c4572: `core/threads.py`, `doubts.py`, `model.py`, `ids.py`, `fields.py`, `snapshot.py`, `check_state.py`, `check_change.py`, `check_immutable.py`, `derive.py`, `views.py` (flags, `failing_ids`, `unrecorded_problems`), `feedback.py`, `document.py`, `search.py`, `__init__.py`, `app/state.py`, `cli/output.py`.
Tests: the three new files and `tests/core/builders.py`.
Not read: Tasks 6 to 9 of the plan beyond grep hits, the viewer, `gitstore`, `tests/structure_*.py` (their result is the passing `tests/test_structure.py`).

## Correctness pass

Every requirement of the brief is implemented as written; I found no Blocking defect.
Verified by running probes against the commit:

- The example file is produced byte for byte, and a CRLF copy, a copy without the final newline, and a copy with extra trailing blank lines all read back equal.
- Round trip is exact for texts containing a lone CR, `---`, `## Message 3`, `\\## Message 3`, `  ## Message 2`, `by: x`, tabs, U+2028, a fenced heading, and a BOM; unwritable values (`where` with U+0001, `when` with LF, empty `where`) raise `ValueError` naming the key.
- Error lines are right (the line of the bad key in message 1 or 2, of an out-of-sequence heading, of an empty text, and of a YAML error inside a message).
- Check 1 gives `an author message needs where`, `messages are numbered 1, 2, 3, in order`, `a thread needs at least one message`, `about must name a decision or a specification entry`, and refuses unknown keys, bad `raises`, `state`, `opened`, `when`, and a closed thread with an empty middle message.
- Check 5 and `_missing` behave as listed; `appended` refuses a closed thread and an empty text without `close`.
- `doubt_marks` gives the listed marks, in the listed order, cycle-safe; a link-only decision marks nothing, a doubted creating decision still marks after a later edit, and a doubt on the latest editor marks the entry.
- The level 1 flag order is as the brief says.

### Important

**I1 · Brief-listed behaviour that no test pins (mutations survive)**
I changed the commit in a scratch worktree and ran `tests/core`; each of these mutations left all tests green:

- `src/lodge/core/threads.py:138`: delete `.replace("\r\n", "\n").strip()` from `appended`.
  The CR rule is a Global Constraint and the design's "never altered beyond the CR rule" must-not, and no test calls `appended` successfully with a CR or with outer whitespace.
- `src/lodge/core/threads.py:144`: make `appended` always set `ThreadState.OPEN`.
  `test_closing_passes` (`tests/core/test_check_threads.py:68`) cannot tell, because an open thread with a second message also passes every check; nothing asserts that `close=True` closes, or that a closing message may be empty.
- `src/lodge/core/threads.py:45`: replace `read_stamp` for `opened` by `read_str` (`opened` not a stamp is a listed check 1 case).
- `src/lodge/core/threads.py:79`: drop the stamp check on an agent's `when`.
- `src/lodge/core/threads.py:60`: drop `check_keys` on the message block (unknown message key is a listed check 1 case).
- `src/lodge/core/check_immutable.py:34`: drop `"opened"` from the immutable names (`{q}: opened of a published thread was changed` is a listed check 5 message, and it has no test although its four neighbours have).

Fix: add to `tests/core/test_thread_files.py` a `test_appended_cleans_the_text_and_closes` (`appended(t, message(text="a\r\nb \r\n  "))` has text `"a\nb"` and state open; with `close=True` and `text=" "` the last message has `text == ""` and the state is `CLOSED`), a parametrised `test_unreadable_header_values_are_problem_1` (bad `opened`, bad `raises`, bad `state`, bad agent `when`, an unknown message key, a missing `by`), and to `tests/core/test_check_threads.py` a `test_changing_opened_fails_check_5`.
Both files stay far below 300 lines.

**I2 · A loaded thread with a problem is invisible in reads**
`src/lodge/core/views.py:50-59` (`failing_ids`, `unrecorded_problems`) treat every path in `s.paths` as a record's, and threads now put theirs there.
Run against the commit: `check_state(snapshot_of(thread(about="s-zzzzzz")))` gives the check 2 problem, and `unrecorded_problems` returns `()` while `failing_ids` returns `{'q-001000'}`.
No read shows a thread as a record, so `app/state.py:55`, the `problem:` lines of `cli/output.py:26`, and the viewer's unrecorded banner (`viewer/html.py:97-101`) never mention it; only `lodge check` prints it.
A decision with the same fault shows "failing" on its page; a thread file with a wrong name or an unresolved `about` shows nothing.
Fix: in `unrecorded_problems` hold only the record paths, `held = {p for i, p in s.paths.items() if i not in s.threads}` (one line, inside the 12-line allowance for `views.py`), and add a test in `tests/core/test_check_threads.py` that the problem is in `unrecorded_problems`.
`lodge check` still prints it once, because `read_lines` prints the unrecorded ones and `check_lines` skips them.

**I3 · The CR rule will exist twice**
The rule lives inline in `appended` (`threads.py:138`), but Task 4's `ask` (plan lines 303 to 310) builds the first message of a new `Thread` without `appended`, and the viewer's reply path needs the empty check before building anything.
Task 4 must therefore either duplicate the clean-up or import something Task 3 does not export.
Fix: in `threads.py` add `def clean_text(text: str) -> str: return text.replace("\r\n", "\n").strip()`, use it in `appended`, export it from `core/__init__.py`, and name it in Task 4's Consumes line; that also gives I1's test one place to pin.

## Practice pass

### Minor

**M1 · `doubt_marks` reads back its own output** (`src/lodge/core/doubts.py:34`)
`any(m.startswith("changed by ") for m in local)` decides `affected` from the text of the marks just built, so a reworded mark silently stops propagation.
The function is also 45 lines doing three jobs, with the open-doubt and open-question comprehensions (lines 12 to 21) repeated.
Fix: a helper `_open(s, kind)`, a boolean `changed` set beside `local`, and a second function for the `rests_on` walk (lines 41 to 56).

**M2 · `_messages` is one 60-line function with a nested error-line fix-up** (`src/lodge/core/threads.py:51-111`)
The `except FormatError` block re-derives a line from the key (lines 83 to 94), and `document.py` already has `_key_line` for the same job.
Fix: split out `_message(lines, first, end, offset)` returning a `Message`, and keep the loop and the numbering in `_messages`.

**M3 · `snapshot.py` idiom** (`src/lodge/core/snapshot.py:60` and `106-123`)
The thread path pattern is compiled inline in the loop, where the sibling patterns (`_AREA_FILE`, `_DECISION_FILE`, `_SPEC_FILE`) are module constants, and `_keep_thread` repeats `_keep_record`'s duplicate-ID branch.
Fix: a module-level `_THREAD_FILE`; let both keepers share one `_duplicate(kept, path, ident)` that returns the two problems.

**M4 · `write_thread` text errors do not name the field** (`src/lodge/core/threads.py:117-120`)
A text that does not read back (for example one with a trailing space, or an uncleaned CR) raises `the thread would not read back unchanged: messages or header`, while Task 4 (plan line 308) must refuse "naming the field".
Fix: compare per part in the read-back check and say `message N text` when the text differs; it also leaves `app/threads.py` nothing to guess.

**M5 · Exports nothing outside core uses** (`src/lodge/core/__init__.py:8,11`)
`doubt_marks` (imported by `derive.py` from its module) and `read_stamp` (imported by `threads.py` from `fields`) are exported, and no later task of the plan consumes either.
Fix: drop both from the front door, or keep them only if Task 4 is changed to use `read_stamp` for `--when`.

**M6 · Poor message for a message without a metadata block** (`src/lodge/core/threads.py:72`)
`## Message 2` directly followed by `## Message 3` reports `the header must be a mapping of keys to values`, which is the thread header's wording.
Fix: when `first == split`, raise `FormatError("a message needs by and when", ...)` with the heading's line.

**M7 · Weak or missing test details**
`tests/core/test_thread_files.py:155` asserts only `check == 1` for a nested file; also assert the message names the file as stray.
`feedback._ID` taking `q` (`src/lodge/core/feedback.py:15`) is pinned by no test (mutation back to `[ds]` leaves all green); one case in `tests/core/test_feedback.py` is not possible (282 lines), so put it in `tests/core/test_thread_files.py` or a new file.
`test_doubt_on_decision_marks_entries_it_created_and_last_changed` (`tests/core/test_doubts.py:57`) cannot tell "its `changed_by[0]`" from "any entry in `changed_by`" (mutation survives); add an entry edited by the doubted decision and then by a later, undoubted one, and assert it is not marked.

## Design pass

Task 4 to 7 consumption: everything in the plan's Interfaces block for Task 3 exists with the stated signature and is exported (`Raises`, `ThreadState`, `Message`, `Thread`, `mint_id("q")`, `read_stamp`, `THREADS`, `thread_path`, `parse_thread`, `write_thread`, `appended`, `newest_last`, `Snapshot.threads`, `doubt_marks`, `Derived.doubts`).
Two departures, both harmless: `Derived.doubts` is typed `Links` (the same mapping type), and `doubts.py` takes `Mapping[str, tuple[str, ...]]` instead of `Links` to avoid an import cycle with `derive.py`, which is the right call.
`derive.py` is 243 lines and `views.py` 238, both under 300 and within the stated additions (3 lines each).
Findings from this pass are I2 and I3 above.
One note for Task 6, not a defect: `viewer/html.py:18` links only `d-` and `s-` IDs, so a `q-` ID in a message is not linked; decide that deliberately there.
