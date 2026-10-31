# Task 3 report

Implemented threads in core on top of Tasks 1 and 2.
No staging, commits, pushes, or record writes were performed.

## Changes per file

- `src/lodge/core/model.py`: Added Raises, ThreadState, Message, and Thread as immutable model values.
- `src/lodge/core/ids.py`: Accepted q identifiers and allowed mint_id to mint them.
- `src/lodge/core/fields.py`: Added the thread ID kind and read_stamp for a timestamp with seconds and an offset.
- `src/lodge/core/threads.py`: Added thread paths, parsing, canonical writing, reversible heading escaping, message validation with problem lines, appending, closing, and chronological ordering.
- `src/lodge/core/doubts.py`: Added local doubt and question marks, decision-to-entry marks for creation and the latest change, and cycle-safe transitive dependency marks sorted by ID.
- `src/lodge/core/snapshot.py`: Added Snapshot.threads with an empty default, loaded flat thread files and paths, and reported duplicate IDs while retaining the first file.
- `src/lodge/core/check_state.py`: Checked thread file names and unresolved about targets.
- `src/lodge/core/check_change.py`: Included published threads in missing-record checks, using the loaded model mappings rather than paths.
- `src/lodge/core/check_immutable.py`: Checked immutable thread metadata, published message prefixes, reopening, appending after closure, and closing without another message.
- `src/lodge/core/derive.py`: Added Derived.doubts and populated it through doubt_marks, adding three lines.
- `src/lodge/core/views.py`: Added confirmation flags and doubt marks after awaiting-author flags and before dependency flags, adding three lines.
- `src/lodge/core/feedback.py`: Excluded q identifiers from number feedback.
- `src/lodge/core/__init__.py`: Exported the new model values, stamp reader, thread operations, and doubt derivation.
- `tests/core/builders.py`: Added synthetic message and thread builders and extended files_of, snapshot_of, and tree_of to accept threads.
- `tests/core/test_thread_files.py`: Added file-shape, round-trip, invalid-file, appending, ordering, loading, and stray-file tests.
- `tests/core/test_check_threads.py`: Added check 1, 2, and 5 tests and a stale-path regression variant for missing threads.
- `tests/core/test_doubts.py`: Added local, propagated, cycle, confirmation, and flag-order tests.

## Test-first evidence

All named tests were written before implementation.
`uv run pytest tests/core -q` initially stopped at collection with `3 errors in 0.48s`.
Consequently, the first failure for each test below was its module import failure, rather than an assertion failure.
The shared first failing output is reproduced once per file and applies to every test listed under it.

### tests/core/test_thread_files.py

```text
E   ImportError: cannot import name 'message' from 'builders'
```

- `test_thread_round_trips`.
- `test_empty_text_only_on_the_closing_message`.
- `test_written_shape_matches_the_example`.
- `test_text_line_like_a_heading_round_trips`.
- `test_yaml_and_markdown_specials_round_trip`.
- `test_author_message_needs_where`.
- `test_malformed_id_is_problem_1`.
- `test_about_must_name_a_decision_or_entry`.
- `test_thread_needs_a_message`.
- `test_messages_numbered_in_order`.
- `test_body_text_before_first_message_refused`.
- `test_appended_refuses_a_closed_thread`.
- `test_newest_last_by_opened_then_id`.
- `test_load_reads_threads_and_their_paths`.
- `test_nested_file_under_threads_is_stray`.

### tests/core/test_check_threads.py

```text
E   ImportError: cannot import name 'message' from 'builders'
```

- `test_open_thread_passes_every_check`.
- `test_unresolved_about_fails_check_2`.
- `test_duplicate_thread_id_fails_check_2`.
- `test_file_name_must_start_with_the_id`.
- `test_appending_a_message_passes`.
- `test_closing_passes`.
- `test_editing_a_published_message_fails_check_5`.
- `test_removing_a_message_fails_check_5`.
- `test_changing_about_fails_check_5`.
- `test_changing_raises_fails_check_5`.
- `test_reopening_fails_check_5`.
- `test_message_after_closing_fails_check_5`.
- `test_closing_without_a_message_fails_check_5`.
- `test_missing_published_thread_fails_check_2`.

### tests/core/test_doubts.py

```text
E   ImportError: cannot import name 'thread' from 'builders'
```

- `test_open_doubt_marks_its_record`.
- `test_closed_doubt_marks_nothing`.
- `test_question_open_mark_and_no_propagation`.
- `test_doubt_reaches_entries_resting_on_it_further_down`.
- `test_doubt_on_decision_marks_entries_it_created_and_last_changed`.
- `test_doubt_on_decision_reaches_what_rests_on_its_entries`.
- `test_cycle_of_rests_on_does_not_hang`.
- `test_confirmed_decision_shows_confirmation_and_keeps_decided_by`.
- `test_flag_order`.

The missing-thread test later gained a `stale_path=True` variant before correcting the implementation.
Its first failing output was:

```text
FAILED tests/core/test_check_threads.py::test_missing_published_thread_fails_check_2[True]
E       assert False
1 failed, 1 passed, 13 deselected in 0.18s
```

The first implementation run also exposed an incorrect test fixture in `test_open_thread_passes_every_check`.
Its area omitted the entry from its order, giving `s-aaaaaa: is not listed in the order of area storage` and `1 failed, 556 passed in 2.18s`.
The new fixture was corrected to list the entry, without changing any pre-existing test.

## Commands and outcomes

- Read `CLAUDE.md`, the Task 3 brief, the named design sections, the core source, the existing check helpers, and the structure tables with `cat`, `sed`, and `rg`.
- `git status --short` initially showed only the untracked Task 3 brief.
- Created the new tests with a temporary Python script, then ran `uv run pytest tests/core -q`: `3 errors in 0.48s`, as documented above.
- Created and updated implementation files with temporary Python scripts, then ran `uv run pytest tests/core -q`: `1 failed, 556 passed in 2.18s`, from the fixture issue above.
- `uv run ruff check` initially ended `Found 22 errors.`, covering imports and formatting in the new code.
- `uv run ruff check --fix` and `uv run ruff format` corrected those issues, the latter ending `7 files reformatted, 404 files left unchanged`.
- `uv run mypy`: `Success: no issues found in 172 source files`.
- `uv run vulture`: no output, exit 0.
- `uv run pytest tests/core tests/test_structure.py -q`: `596 passed in 2.49s`.
- The first complete builder gate passed with `1153 passed in 31.03s`, followed by `lodge check --gate` printing `ok` and area-added notes, ending `note: area writing: added`.
- `uv run pytest tests/e2e/test_view.py -q -k test_view_passes_the_port_to_the_viewer`: `1 passed, 2 deselected in 0.50s`.
- `git diff --check`: no output, exit 0.
- Reviewed `git diff`, `git diff --numstat`, and module line counts; all changed modules and new test files remain under 300 lines.
- `uv run pytest tests/core/test_check_threads.py -q -k missing` before the stale-path correction: `1 failed, 1 passed, 13 deselected in 0.18s`.
- The first gate rerun after adding that variant stopped at an import-order error, `Found 1 error.`, which `uv run ruff check --fix` fixed.

Final builder gate command:

```sh
uv run ruff format --check && uv run ruff check && uv run mypy && uv run vulture && uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py && uv run lodge check --gate
```

Final result: exit 0.
Format ended `411 files already formatted`, lint ended `All checks passed!`, mypy ended `Success: no issues found in 172 source files`, and vulture produced no output.
Pytest ended `1154 passed in 31.28s`.
The lodge gate printed `ok` and ended `note: area writing: added`.
The corrected missing-thread selection ended `2 passed, 13 deselected in 0.08s`.
Final `git diff --check` produced no output and exited 0.
Final `git status --short` contained the intended source, test, and report changes, the original untracked brief, and an unrelated untracked Task 1 review, which was left untouched.

## Boundaries and uncertainties

No implementation uncertainty remains.
The report explicitly records that the initial test-first failures occurred at collection.
The core permits an empty final closing message as required by the brief; a future command-line caller supplies the design’s default `Closed.` text.
The doubt helper uses the structural Mapping type of Links rather than importing derive.Links, avoiding a module cycle.

Socket-bound tests were excluded as instructed:

- All tests in `tests/viewer/test_server.py`.
- `tests/e2e/test_view.py::test_view_serves_the_project_until_interrupted`.

The port-forwarding test in the excluded end-to-end file was run separately as required.
The remaining excluded test, `test_view_outside_a_repository_is_one_sentence`, is not socket-bound but is outside the separate selection named by this brief.
The coordinator still needs to run `sh scripts/check.sh` outside the sandbox.
