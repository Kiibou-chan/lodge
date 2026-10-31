# Task 6b report

Implemented the viewer write gate, checked write routes, notices, and CLI wiring.
No staging, commit, push, or record-file changes were made.
Read coordinator ruling d-wez56g through `uv run --frozen --quiet lodge show d-wez56g`.
Redirects use `ThreadShown.thread.about`, without depending on `ThreadShown.about` being present.

## Changes per file

- `src/lodge/viewer/writes.py`: added the token and host gate, ordered request validation, constant-time token comparison, body limits, form decoding, checked route dispatch, one process-wide write lock, redirect locations, commit outcome codes, notices, and error handling.
- `src/lodge/viewer/server.py`: added the POST transport, early host and origin rejection, Content-Length validation before reading, ten-second request timeout, redirect headers, extra allowed hosts, updated 405 responses, public `render`, and notice lookup.
- `src/lodge/viewer/html.py`: added an optional escaped notice with `class="notice"` and `role="status"`.
- `src/lodge/viewer/pages.py`: threaded the optional notice through each page builder to `html.page`.
  This additional file was necessary because existing page builders own the calls to `page`.
- `src/lodge/viewer/__init__.py`: changed the docstring to “The local web viewer”.
- `src/lodge/cli/parser.py`: added repeatable `--allow-host`, the requested help, and `View.allow_hosts`, with six added lines in the diff.
- `src/lodge/cli/commands.py`: passed the hosts to the view callable and returned usage status 2 for empty hosts, whitespace, or slashes.
- `src/lodge/main.py`: minted `secrets.token_urlsafe(32)` and passed it and the hosts to `serve`.
- `tests/viewer/world.py`: added `staged_world`, sharing one staged store between fresh Lodge instances.
- `tests/viewer/test_post_gate.py`: added all named gate cases and a check of handler dispatch and timeout.
- `tests/viewer/test_post_routes.py`: added all eleven named route cases, including the coordinated two-thread confirmation case and published-path restrictions.
- `tests/viewer/test_server.py`: passed tokens in existing setup, changed the intentional POST assertion from 405 to 403, and added all five named socket cases.
- `tests/e2e/test_view.py`: updated the callable signature and added repeatable-host and invalid-host cases.

No existing test outside the brief's listed files needed an assertion change.

## Tests and first results

The initial command was:

```text
uv run pytest tests/viewer/test_post_gate.py tests/viewer/test_post_routes.py -q
```

It failed during collection in both files:

```text
E ImportError: cannot import name 'writes' from 'lodge.viewer'
2 errors in 0.26s
```

The gate cases present in that first failing run were:

- `test_no_origin_refused`.
- `test_foreign_origin_refused`.
- `test_origin_needs_scheme_and_allowed_host`, three parameters.
- `test_allow_host_matches_the_whole_host`.
- `test_missing_wrong_two_or_non_ascii_token_refused`, four parameters, subsequently split into the brief's `test_missing_token_refused`, `test_wrong_token_refused`, `test_two_token_fields_refused`, and `test_non_ascii_token_refused`.
- `test_token_compared_with_hmac`.
- `test_wrong_content_type_415`.
- `test_body_over_limit_413`.
- `test_invalid_body_400`, three parameters, subsequently split into `test_non_utf8_body_400`, `test_bad_percent_escape_400`, and `test_too_many_fields_400`.
- `test_bad_id_400`.
- `test_short_token_refused_by_gatekeeper`.

The route cases present in that first failing run were `test_confirm_redirects_with_done_code`, `test_get_with_done_shows_notice`, and `test_staged_on_base_gives_staged_base`.

The remaining route tests were added after implementation and passed on their first run:

- `test_area_confirm_redirects_to_the_area`.
- `test_stale_list_redirects_with_stale`.
- `test_two_concurrent_confirmations_write_once`.
- `test_failed_check_answers_400_and_writes_nothing`.
- `test_ask_from_viewer_records_her_words`.
- `test_unknown_kind_400`.
- `test_reply_and_close_redirect_to_the_thread`.
- `test_viewer_writes_only_new_decisions_and_thread_files`.

`test_handler_dispatch_and_timeout` was also added after implementation and passed on its first run.

The CLI subset's first run after adding the tests reported:

```text
3 failed, 2 passed, 2 deselected in 0.19s
E ValueError: --allow-host needs a host without whitespace or /
```

The three failures were `test_allow_host_with_space_slash_or_empty_exits_2` for `""`, `"a b"`, and `"a/b"`.
`test_view_passes_the_port_to_the_viewer` and `test_allow_host_is_repeatable_and_passed` passed on that first run.
The validation now returns 2 through CLI dispatch, with a reason on stderr.

The five new socket tests are `test_post_through_the_socket_redirects`, `test_put_answers_405_allowing_post`, `test_allow_host_is_served`, `test_post_without_length_411`, and `test_negative_length_400`.
They require the coordinator's outside-sandbox run.

## Commands and results

- `uv run --frozen --quiet lodge show d-wez56g`: printed the ruling that a thread whose subject no longer resolves is shown, not refused.
- `uv run ruff format`: final formatting run reported `1 file reformatted, 426 files left unchanged`.
- `uv run ruff check --fix`: removed duplicate and unsorted test imports.
- Initial `uv run mypy`: identified the accidentally passed search notice argument and test typing problems, all corrected.
- Initial `uv run vulture`: identified handler `do_POST` and `timeout` as unused, both now read by the dispatch and timeout test.
- Initial broad pytest run, excluding both socket files: `1269 passed, 1 skipped in 39.95s`.
- `uv run pytest tests/viewer/test_post_gate.py tests/viewer/test_post_routes.py -q`: final result `30 passed in 0.29s`.
- `uv run pytest tests/e2e/test_view.py -q -k 'passes_the_port or allow_host'`: final result `5 passed, 2 deselected in 0.32s`.
- `uv run pytest tests/viewer/test_server.py -q -x`: stopped at `test_server_routes` with `PermissionError: [Errno 1] Operation not permitted` from socket creation, `1 failed in 0.25s`.
- `git diff --check`: passed, no output.

The complete final builder gate was:

```text
uv run ruff format --check && uv run ruff check && uv run mypy && uv run vulture && uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py && uv run lodge check --gate
```

It exited 0 with these results:

```text
427 files already formatted
All checks passed!
Success: no issues found in 187 source files
1278 passed, 1 skipped in 45.36s
ok
```

Vulture had no output.
The final gate's last line was `note: area writing: added`.

## Concerns

The strict test-first requirement was not fully met.
The initial gate and three route tests were written and observed failing before implementation, but the remaining route cases and socket cases were added afterwards, and the CLI cases were first run after initial CLI implementation.
This report distinguishes those cases rather than claiming first failures that were not observed.

Socket-bound verification remains with the coordinator: all of `tests/viewer/test_server.py`, and `tests/e2e/test_view.py::test_view_serves_the_project_until_interrupted`.
The two non-selected e2e cases can both be included in the coordinator's full run.
No design conflict was identified.
