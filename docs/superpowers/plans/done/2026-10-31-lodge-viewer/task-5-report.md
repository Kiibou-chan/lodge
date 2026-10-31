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

## Fix round 1

Applied d-wez56g together with Task 4, preserving the committed Task 6a and Task 6b behaviour.
No commit or push was made.

### Findings and changes

- I1: message files use `read_file(..., exact=True)`, leaving CRLF cleaning and outer whitespace removal to `core.clean_text`.
  A lone CR survives both storage and command output.
- I2: restored both introductory sentences and blank lines after every heading.
  Kept all five required Reading and Writing sentences verbatim, the REF definition, the command descriptions, and the existing 60-line limit.
  The guide is 60 lines: the example uses a compact YAML flow mapping, the changes/rests_on advice shares one sentence, and the stray Reading paragraph break is gone.
- I3: added author provenance and exact text round-trip assertions, unknown and closed reply/close refusals, missing and non-UTF-8 message-file refusals, and direct run_thread coverage of PUBLISHED and CHECK_FAILED output and exit codes.
- M1: thread heads use singular `1 message` and plural `2 messages`.
- M2: `waiting` calls `Lodge.waiting_all` once; both groups share the same checked snapshot, and output reads freshness from its single Read.
  Existing `waiting` and `threads_waiting` app methods remain available for downstream callers.
- M3: the hook uses a named THREADS constant beside ATTACHMENTS.
- M4: --by, --where, and --when have help strings explaining the role and author provenance.
- M5: the three write commands inherit their four common fields from MessageCommand, and write dispatch uses match.
- M6: thread_text builds its body once before joining the read lines.
  The README change remains assigned to Task 10, exactly as the review requests.
- M7: grouping tests assert heading order, absence of decisions and threads in the wrong group, and decision blocks before thread heads in the author group.
  Both same-second tests now reject duplicate placement in the agent group.
- Task 4 I1: thread_head accepts a missing title and prints the separate line `about ID, not found`; thread_text handles an absent about view, and list/waiting callers use titles.get without an empty-string fallback.

### Failing-first evidence

Before implementation, `uv run pytest tests/app/test_thread_ops.py tests/gitstore/test_commit.py tests/e2e/test_threads.py tests/e2e/test_guide.py -q` returned `6 failed, 58 passed in 3.23s`.
The Task 5 failures were:

- Strengthened `test_ask_reply_close_round_trip`: `1 message ·` absent because the head said `1 messages`.
- `test_author_words_are_recorded_exactly`: the displayed words contained LF instead of the required lone CR.
  The fixture contains both `a\rb` and CRLF-separated lines; the final assertions check the author, timestamp, place, displayed text, and stored parsed text.
- `test_guide_restores_introduction_and_heading_spacing`: the introductory lodge sentence was absent.
  The final test also checks the area definition, every heading's following blank line, and the unchanged line limit.

`test_orphaned_thread_outputs` first failed with KeyError before the app fix.
A further run against a faulty formatter that embedded `about ID, not found` in the head instead of giving it a separate line returned `1 failed in 0.21s`.
The formatter was then corrected.

For new or strengthened tests whose behaviour already worked, temporary faulty variants proved the assertions before the final implementation:

| Test | Faulty variant | First result |
| --- | --- | --- |
| `test_reply_to_unknown_or_closed_thread_exit_2`, reply and close | Let unknown/closed thread errors escape as RuntimeError | 2 failed |
| `test_missing_message_file_exit_2`, missing and non-UTF-8 | Let file errors escape as RuntimeError | 2 failed |
| `test_run_thread_outcomes`, PUBLISHED and CHECK_FAILED | Print staged for published and return 0 for failed checks | 2 failed |
| `test_waiting` and `test_waiting_groups_threads` | Swap the group headings | 2 failed |
| Both same-second waiting tests | Also place author-waiting decisions in the agent group | 2 failed |

The initial outcome-test draft had an invalid CheckResult fixture.
That fixture was corrected before the deliberate output mutations; the fixture error is not counted as failing-first evidence.
Every temporary source mutation was restored after its test run.
The new command-outcome and orphan-formatter tests live in `tests/app/test_thread_fix_paths.py` so they can reuse the synthetic app ports without adding a package or duplicating fixtures.

### Verification

- Focused regression command covering app threads, command outcomes, real commits, CLI threads, waiting, same-second ordering, guide, and viewer POST routes: `85 passed in 4.21s`.
- `sh scripts/check.sh`: format, lint, strict typing, and vulture passed; pytest ended `19 failed, 1303 passed in 35.83s`.
  All 19 failures were socket permission failures in this sandbox, so the script stopped before the lodge gate.
  A coordinator run outside the sandbox is still required.
- The socket-bound failures were `tests/e2e/test_view.py::test_view_serves_the_project_until_interrupted` and these tests in `tests/viewer/test_server.py`:
  `test_server_routes`, `test_pages_are_html_and_style_is_css`, `test_search_filters_arrive_from_the_query`, `test_a_fresh_lodge_for_each_request`, `test_lodge_error_is_a_page_with_its_message`, `test_other_failures_are_a_plain_500`, `test_unreadable_file_banner_reaches_the_browser`, `test_only_reads_are_served`, `test_response_headers_lock_the_page_down`, `test_bound_to_loopback_only`, `test_serve_reports_a_port_in_use_as_one_sentence`, `test_serve_announces_the_address_and_stops_on_interrupt`, `test_closing_the_server_waits_for_a_request_that_is_running`, `test_post_through_the_socket_redirects`, `test_put_answers_405_allowing_post`, `test_allow_host_is_served`, `test_post_without_length_411`, and `test_negative_length_400`.

- Final builder gate: `uv run ruff format --check && uv run ruff check && uv run mypy && uv run vulture && uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py && uv run pytest tests/e2e/test_view.py -q -k 'not serves_the_project' && uv run lodge check --gate` passed.
  Its last results were `428 files already formatted`, `All checks passed!`, `Success: no issues found in 188 source files`, vulture exit 0, `1297 passed in 35.20s`, `6 passed, 1 deselected in 0.35s`, and `ok` with area-added notes.
  This final run includes the shared command-field refactor and the separate missing-subject line.
- No review finding is left unresolved within this round's scope; the README wording remains scheduled for Task 10 as the review directs.
