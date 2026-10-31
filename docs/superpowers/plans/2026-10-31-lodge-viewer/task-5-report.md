# Task 5 report

Implemented the thread commands, waiting groups, hook advice, and guide updates without staging, committing, or pushing.

## Changes by file

- `src/lodge/cli/threads.py`: five command dataclasses, grammar registration, author provenance validation, file reads, app dispatch, and write outcomes.
- `src/lodge/cli/files.py`: shared `read_file`, moved unchanged from `commands._read`.
- `src/lodge/cli/thread_output.py`: thread heads, ordered messages, closing attribution, and both waiting groups.
- `src/lodge/cli/parser.py`: thread command import, command union, registration call, and waiting help, with six added lines and two removed lines.
- `src/lodge/cli/commands.py`: dispatches thread commands, reads files through the shared helper, and combines decision and thread waiting results.
- `src/lodge/cli/output.py`: removes the obsolete ungrouped waiting empty message.
- `src/lodge/cli/guide.md`: adds every required sentence and trims two introductory sentences and four blank lines to retain the existing 60-line limit.
- `src/lodge/hook/post_tool_use.py`: thread edits receive `THREAD_TEXT` and the existing reversal instructions.
- `tests/e2e/test_threads.py`: round trip, provenance errors, unknown reference, and staging without committing.
- `tests/e2e/test_waiting.py`: updates the existing expectation for grouped output and tests author-last and agent-last thread placement.
- `tests/e2e/test_help_lists_every_command.py`: adds all five commands to listing and per-command help coverage.
- `tests/e2e/test_guide.py`: checks the new reading and writing guidance.
- `tests/hook/test_post_tool_use.py`: checks thread-specific reply, close, and reversal advice.

## Test-first evidence

All required tests were written and run before implementation.
The initial command was `uv run pytest tests/e2e/test_threads.py tests/e2e/test_waiting.py tests/e2e/test_help_lists_every_command.py tests/e2e/test_guide.py tests/hook/test_post_tool_use.py -q`.
Its last line was `15 failed, 53 passed in 1.78s`.
The complete first output is retained locally in `.drafts/task-5-first-tests.txt`.

| Test | First failure output |
| --- | --- |
| `test_ask_reply_close_round_trip` | `AssertionError: Result(code=2` and `invalid choice: 'ask'` |
| `test_author_message_needs_where_and_when_exit_2` | Expected `a message by author needs --where and --when, the place and time of the author's words`, received `invalid choice: 'ask'` |
| `test_where_with_an_agent_role_exit_2` | Expected `--where and --when are for messages by author`, received `invalid choice: 'ask'` |
| `test_ask_on_unknown_ref_exit_2` | `assert ('s-aaaaaa' in` the invalid-command error |
| `test_thread_files_are_staged_not_committed` | `AssertionError: Result(code=2` and `invalid choice: 'ask'` |
| Updated `test_waiting` | `AssertionError: assert 'nothing wait... the author\n' == 'waiting for ...or\nnothing\n'` |
| `test_waiting_groups_threads` | `assert 2 == 0` with `invalid choice: 'ask'` |
| Extended `test_help_lists_every_command` | `AssertionError: threads` |
| `test_every_command_has_help[threads]` | `assert (2 == 0)` with `invalid choice: 'threads'` |
| `test_every_command_has_help[thread]` | `assert (2 == 0)` with `invalid choice: 'thread'` |
| `test_every_command_has_help[ask]` | `assert (2 == 0)` with `invalid choice: 'ask'` |
| `test_every_command_has_help[reply]` | `assert (2 == 0)` with `invalid choice: 'reply'` |
| `test_every_command_has_help[close]` | `assert (2 == 0)` with `invalid choice: 'close'` |
| `test_guide_says_waiting_first` | `assert 'Run lodge waiting ...' in` the old guide, with backticks around the command in the actual assertion |
| `test_thread_file_edit_names_reply_and_close` | `AssertionError: assert 'is a lodge thread file' in` the record advice |

## Commands and results

- Read the brief, `CLAUDE.md`, cloud runtime skill, affected source and tests, and relevant design passages using `cat`, `sed`, and `rg`.
- `uv run --frozen --quiet lodge show d-a3h9f3 --reasoning` confirmed that the recorded ruling supersedes the design's old default closing text.
- `git status --short`, `git diff --stat`, and `git diff --numstat src/lodge/cli/parser.py` inspected changes without changing the index.
- `uv run ruff format`: initially `10 files reformatted, 409 files left unchanged`.
- The first implementation test run ended `1 failed, 67 passed in 2.20s`, because the guide had grown to 66 lines.
- The first builder gate stopped at ruff with `Found 2 errors`, both import ordering.
- `uv run ruff check --fix`: `Found 2 errors (2 fixed, 0 remaining)`.
- A compact union experiment using `Union` failed `UP007`; it was replaced with grouped `|` unions within the parser edit budget.
- Final `uv run ruff format --check`: `419 files already formatted`.
- Final `uv run ruff check`: `All checks passed!`.
- Final `uv run mypy`: `Success: no issues found in 180 source files`.
- Final `uv run vulture`: exit 0, no output.
- `uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py`: `2 failed, 1227 passed in 34.29s`.
- `uv run pytest tests/e2e/test_threads.py tests/e2e/test_waiting.py tests/e2e/test_help_lists_every_command.py tests/e2e/test_guide.py tests/hook/test_post_tool_use.py tests/test_structure.py -q`: `107 passed in 2.36s`.
- `uv run pytest tests/e2e/test_view.py -q -k test_view_passes_the_port_to_the_viewer`: `1 passed, 2 deselected in 0.28s`.
- `uv run pytest tests/e2e/test_view.py -q -k test_view_outside_a_repository_is_one_sentence`: `1 passed, 2 deselected in 0.32s`.
- `uv run lodge check --gate`: exit 0, `ok`, ending with `note: area writing: added`.

## Concerns and coordinator work

Two existing assertions outside the permitted test files still require the old waiting layout: `tests/e2e/test_same_second.py::test_agent_edit_in_the_same_second_is_flagged` expects the decision at the start, and `test_agent_edit_in_the_same_second_publishes_in_branch_mode` expects it on line two after freshness.
Both receive the correct decision under `waiting for the author`.
I have requested permission to update those assertions and have left the file unchanged pending an answer, because the brief permits existing test edits only where named.

The design at line 85 says a missing closing text becomes `Closed.`, but the brief cites ruling `d-a3h9f3`, which expressly supersedes that advisor addition with an empty closing message.
Implementation follows that recorded ruling and the brief.
No new record was necessary and no `lodge add` was run.

Socket-bound checks deferred to the coordinator are `tests/viewer/test_server.py` and the socket-serving test `tests/e2e/test_view.py::test_view_serves_the_project_until_interrupted`.
Both non-socket tests from the excluded view file were run separately and passed.
The coordinator must run `sh scripts/check.sh` outside the sandbox, stage explicit paths, commit, and push.
