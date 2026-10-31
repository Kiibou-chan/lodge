# Task 4 report

Status: DONE.

Implemented thread operations and explicit-path checkout commits on the current branch.
No staging, commits, pushes, or record-file writes were performed.

## Changes per file

| File | Change |
| --- | --- |
| `src/lodge/app/ports.py` | Added `CommitOutcome`, `Committed`, and `Store.commit`. |
| `src/lodge/app/results.py` | Added thread read/write results, `Shown.threads`, and `Added.paths`. |
| `src/lodge/app/lodge.py` | Exposed ask, reply, close, thread listing, thread display, and waiting groups. |
| `src/lodge/app/threads.py` | Added message validation, clock-derived timestamps, checked writes, three-attempt publication, optional commits, and thread reads. |
| `src/lodge/app/reads.py` | Filled each shown record’s threads, newest last, including closed threads. |
| `src/lodge/app/writes.py` | Renamed `_mint` to `mint_unused`, accepted the q prefix, and returned written paths including attachments after publication or staging. |
| `src/lodge/app/__init__.py` | Exported the new port and result types. |
| `src/lodge/gitstore/commit.py` | Added explicit-path commits with base-branch, detached-HEAD, and operation guards, one index-lock retry, ordinary hooks, checkout identity, and Git failure details. |
| `src/lodge/gitstore/checkout.py` | Delegated commits and accepted the retry interval; removed two redundant method docstrings to keep the net addition to eight lines. |
| `src/lodge/gitstore/branch.py` | Refused separate commits because publishing already commits. |
| `src/lodge/gitstore/setup.py` | Passed the optional retry interval to checkout stores. |
| `tests/app/fakes.py` | Recorded commits and exposed a configurable commit result. |
| `tests/gitstore/test_concurrent.py` | Delegated `Interleaved.commit` to its inner store. |
| `tests/app/test_thread_ops.py` | Added the required application tests, with metadata and whitespace parametrisation. |
| `tests/gitstore/test_commit.py` | Added the required real-repository commit tests, including real conflicting merge, revert, and cherry-pick operations. |

`writes.py` remains 214 lines, with no net addition.
`checkout.py` is 265 lines, eight more than its committed 257-line version.
Every source and test module passes the existing 300-line structure check.

## First failing outputs

Both new test files were written before production changes.
The combined first run stopped at collection because the commit API did not exist.
The application file was then run separately before implementation, yielding 31 failures.
Git tests shared the collection failure below; their individual bodies did not execute before implementation.

### Application tests

| Test | First failing output |
| --- | --- |
| `test_ask_writes_a_thread_file` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_ask_resolves_a_code` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_ask_on_an_unknown_ref_is_not_found` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_author_message_needs_where` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_author_when_defaults_to_the_minute` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_agent_message_may_not_carry_where` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_role_like_author_refused` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_empty_text_refused` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_text_loses_cr_and_outer_whitespace_only` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_unstorable_where_refused` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_reply_appends` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_reply_to_closed_thread_refused` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_close_appends_closed_by_the_closer` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_close_without_text_passes_the_check` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_close_with_text` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_rejected_publish_starts_again` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_commit_after_staged_when_asked` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_no_commit_unless_asked` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_no_commit_when_published` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_threads_lists_open_newest_last` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_thread_shows_one_thread` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_threads_waiting_groups` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_show_carries_the_records_threads` | `AttributeError: 'Lodge' object has no attribute 'ask'` |
| `test_added_paths_lists_the_files_written` | `AttributeError: 'Added' object has no attribute 'paths'` |
| `test_search_and_timeline_leave_threads_out` | `AttributeError: 'Lodge' object has no attribute 'ask'` |

Parametrised variants all failed in that run, including both role spellings, an empty role, empty text, both invalid metadata fields, and both closing-text variants.

### Git tests

| Test | First failing output |
| --- | --- |
| `test_commits_only_the_named_paths` | Collection: `ImportError: cannot import name 'CommitOutcome' from 'lodge.app'` |
| `test_commit_takes_the_checkouts_identity` | Collection: `ImportError: cannot import name 'CommitOutcome' from 'lodge.app'` |
| `test_no_commit_on_the_base_branch` | Collection: `ImportError: cannot import name 'CommitOutcome' from 'lodge.app'` |
| `test_no_commit_on_a_detached_head` | Collection: `ImportError: cannot import name 'CommitOutcome' from 'lodge.app'` |
| `test_no_commit_during_a_merge` | Collection: `ImportError: cannot import name 'CommitOutcome' from 'lodge.app'` |
| `test_no_commit_during_a_revert` | Collection: `ImportError: cannot import name 'CommitOutcome' from 'lodge.app'` |
| `test_no_commit_during_a_rebase` | Collection: `ImportError: cannot import name 'CommitOutcome' from 'lodge.app'` |
| `test_no_commit_during_a_cherry_pick` | Collection: `ImportError: cannot import name 'CommitOutcome' from 'lodge.app'` |
| `test_locked_index_retries_once_then_locked` | Collection: `ImportError: cannot import name 'CommitOutcome' from 'lodge.app'` |
| `test_lock_gone_on_retry_commits` | Collection: `ImportError: cannot import name 'CommitOutcome' from 'lodge.app'` |
| `test_other_failure_is_failed_with_gits_line` | Collection: `ImportError: cannot import name 'CommitOutcome' from 'lodge.app'` |

## Commands and results

| Command | Last lines or result |
| --- | --- |
| `uv run pytest tests/app/test_thread_ops.py tests/gitstore/test_commit.py -q`, before implementation | `ERROR tests/gitstore/test_commit.py`; `1 error in 0.26s`. |
| `uv run pytest tests/app/test_thread_ops.py -q`, before implementation | `31 failed in 0.32s`. |
| `uv run pytest tests/app/test_thread_ops.py tests/gitstore/test_commit.py -q`, after implementation | `42 passed in 1.23s`. |
| `uv run ruff format`, initial formatting | `5 files reformatted, 410 files left unchanged`. |
| Initial `uv run ruff check` | Three errors: export sorting, a regex literal, and an overly broad exception assertion; all corrected. |
| Initial `uv run mypy` | `Found 7 errors in 3 files (checked 176 source files)`; corrected annotations and typed the mixed record mapping. |
| `uv run ruff check --fix`, followed by `uv run ruff format` | Export sorting fixed; formatting corrected three long lines; `2 files reformatted, 413 files left unchanged`. |
| `uv run mypy`, after corrections | `Success: no issues found in 176 source files`. |
| `uv run vulture`, each run | No output, exit 0. |
| `uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py` | `1201 passed in 31.74s`. |
| Full builder gate, in the exact brief order | `415 files already formatted`; `All checks passed!`; `Success: no issues found in 176 source files`; `1201 passed in 31.93s`; lodge check exited 0. |
| `uv run lodge check --gate`, the gate’s final command | `ok`, followed by area-added notes, ending `note: area writing: added`. |
| `uv run pytest tests/e2e/test_view.py -q -k "test_view_passes_the_port_to_the_viewer or test_view_outside_a_repository_is_one_sentence"` | `2 passed, 1 deselected in 0.56s`. |
| `uv run --frozen --quiet lodge show d-a3h9f3 --reasoning` | Confirmed the recorded ruling that closing without text appends an empty closing message. |
| `git diff --check` | No output, exit 0. |

The full builder gate was:

```sh
uv run ruff format --check && uv run ruff check && uv run mypy && uv run vulture && uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py && uv run lodge check --gate
```

Inspection commands used `cat`, `rg`, `sed`, `wc -l`, `git status --short`, `git diff`, and `tail` for requirements, implementation, test helpers, structure rules, and captured outputs.
Edits were made using Python and shell heredocs, followed by Ruff formatting.

## Socket-bound tests left for the coordinator

The builder gate excluded `tests/viewer/test_server.py` and the socket-bound `tests/e2e/test_view.py::test_view_serves_the_project_until_interrupted`.
The two socket-free tests in the latter file passed separately.
The excluded server tests are:

- `test_server_routes`
- `test_pages_are_html_and_style_is_css`
- `test_search_filters_arrive_from_the_query`
- `test_a_fresh_lodge_for_each_request`
- `test_lodge_error_is_a_page_with_its_message`
- `test_other_failures_are_a_plain_500`
- `test_unreadable_file_banner_reaches_the_browser`
- `test_only_reads_are_served`
- `test_response_headers_lock_the_page_down`
- `test_bound_to_loopback_only`
- `test_serve_reports_a_port_in_use_as_one_sentence`
- `test_serve_announces_the_address_and_stops_on_interrupt`
- `test_closing_the_server_waits_for_a_request_that_is_running`

## Concerns and interpretation

The frozen design’s line 85 says the default closing text is “Closed.”.
The brief explicitly requires empty text and cites d-a3h9f3; reading that decision confirmed that it supersedes the default wording to avoid inventing author words.
The implementation follows that ruling.
`test_thread_shows_one_thread` explicitly asserts `shown.about.id == "s-aaaaaa"`.

No implementation concerns remain.
The coordinator still needs to run `sh scripts/check.sh` outside the sandbox, stage explicit paths, commit, and push as directed by the brief.
Pre-existing untracked planning material was left untouched.
