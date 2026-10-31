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

## Fix round 1

Requirements: `task-6b-brief.md` and `task-6b-review.md`, with the requested socket-free short-reader test.
Task 7 remains in place.
No commit or staging was performed.
The pre-existing uncommitted `HTMLParser.handle_starttag` allowance in `vulture_allow.py` was preserved.

### Changes

- `src/lodge/viewer/server.py`: refuse a short body with 400 and "the form arrived incomplete; nothing was written", before calling the writer (I1).
  Reject repeated Host, Origin, Content-Length, and Content-Type headers with 400 on GET, HEAD, and POST, before reading the body (m1).
  Render every non-303 POST reply through the error page, carrying the optional back link (m2).
  Update the module docstring (m7).
- `src/lodge/viewer/writes.py`: `Reply` carries a plain reason and optional `back`, with escaping delegated to the page renderer (m2).
  Thread redirects use `Written.about`, retaining the submitted reference for the pre-write back link (m3).
- `src/lodge/viewer/pages.py`: error pages accept an optional back link and escape both the reason and the link (m2).
- `src/lodge/cli/parser.py`: add the specified HOST metavar and repeatable-host help (m6).
  This adds only one line to the current parser, staying within the brief's original eight-line budget.
- `tests/viewer/test_request_gate.py`: new in-memory handler tests for short reads, excessive declared lengths, repeated headers in both orders on GET and POST, and complete refusal pages (I1, I2, m1, m2).
  `BodyReader` records each requested read size; every refusal asserts zero publishes, and the length-limit and repeated-header tests assert no body read.
- `tests/viewer/test_post_gate.py`: cover malformed thread IDs on reply and close, origin-prefix attacks, and the exact missing-Origin reason with the key absent (I2, m8).
  Remove the artificial dispatch-and-timeout test (m4).
- `tests/viewer/test_post_routes.py`: test canonical redirects and quoted area redirects, and assert author, location, and minute on each reply and closing message (m3, m8).
  Existing refusal tests now inspect `Reply.back` because the server owns the HTML rendering.
- `tests/viewer/test_server.py`: rename the obsolete read-only test (m7).
- `vulture_allow.py`: allow the HTTP dispatch name, timeout, and parsed protocol attribute read by the standard library (m4).

### First failures and mutation evidence

Each mutation below was applied alone, its named test was run with `uv run pytest TEST -q`, and the source was restored in a `finally` block.
All mutant runs exited 1 through assertion failures, not collection or syntax errors.
The tests were retained, and the restored implementation passed afterwards.
The short-body, repeated-header, complete-page, and canonical-reference tests were also observed failing against the original implementation before their fixes.

| Test or strengthened cases | Mutation | Observed failing output |
| --- | --- | --- |
| `test_short_body_refused_without_writing` | Replace the short-body comparison with `if False` | Expected `400 Bad Request`, received `303 See Other`; `1 failed in 0.28s`. |
| `test_excessive_declared_length_refused_without_reading` | Replace the server's over-limit length branch with `elif False` | Expected HTTP 413, received 303 before the short-body fix; `1 failed in 0.25s`. |
| `test_bad_thread_id_refused_without_writing`, both actions and both IDs | Remove the whole thread-ID guard | Expected 400, received 404; `4 failed in 0.27s`. |
| Same ID test, `s-aaaaaa` | Remove only the `q-` prefix check | Expected 400, received 404; `2 failed, 2 passed in 0.30s`. |
| Same ID test, `q-11111` | Remove only the ID-shape check | Expected 400, received 404; `2 failed, 2 passed in 0.30s`. |
| `test_repeated_headers_refused`, four header names, two methods, and two orders | Replace the duplicate-count check with `if False` | Expected 400, received 303, 403, 404, or 415; `16 failed in 0.36s`. |
| `test_write_refusal_is_a_complete_page` | Send the reason directly instead of using `pages.error_page` | Missing `<!doctype html>`; `1 failed in 0.28s`. |
| `test_ask_redirect_uses_canonical_about` | Use raw `about` instead of `written.about` | Expected `/r/s-aaaaaa`, received `/r/S-AAAAAA`; `1 failed in 0.30s`. |
| `test_origin_needs_scheme_and_allowed_host`, the two new prefix attacks | Replace exact origin membership with `startswith` matching | Expected 403, received 303; `2 failed, 3 passed in 0.26s`. |
| `test_no_origin_refused` | Remove the empty-Origin branch | Expected `a write needs an Origin header`, received `this origin is not served`; `1 failed in 0.24s`. |
| `test_reply_and_close_redirect_to_the_thread` | Change reply and close `where` to `elsewhere` | Expected `lodge viewer`, received `elsewhere`; `1 failed in 0.27s`. |
| Same provenance test, closing message separately | Change `where` only when the action is `close` | Expected `lodge viewer`, received `elsewhere`; `1 failed in 0.30s`. |
| `test_area_redirect_quotes_area` | Remove `quote` from the area redirect | Expected `cold%20%26%20storage`, received `cold & storage`; `1 failed in 0.26s`. |

The first over-limit test run exposed a test assumption about Python's reason phrase: Python 3.13 says `413 Content Too Large`.
The assertion was corrected to check status 413, then the actual guard-removal mutation was observed failing as recorded above.
The first static pass also found a BytesIO override annotation and standard-library attribute allowances; these were corrected without changing the security checks.
Removing the apparently unused `requestline` from the in-memory handler exposed a standard-library logging dependency in the next broad run (`19 failed, 1334 passed`), so it was restored and allow-listed.
The boundary mutations were rerun afterwards and failed through the expected assertions; the table records those valid runs.

### Validation

- Focused run: `uv run pytest tests/viewer/test_request_gate.py tests/viewer/test_post_gate.py tests/viewer/test_post_routes.py -q`, `58 passed in 0.35s`.
- Broad socket-free run: `uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py`, `1353 passed in 36.47s`.
- CLI run: `uv run pytest tests/e2e/test_view.py -q -k 'passes_the_port or allow_host'`, `5 passed, 2 deselected in 0.06s`.
- `uv run ruff format --check`: `433 files already formatted`.
- `uv run ruff check`: `All checks passed!`.
- `uv run mypy`: `Success: no issues found in 193 source files`.
- `uv run vulture`: exit 0, no output.
- `uv run lodge check --gate`: exit 0, `ok`, ending with `note: area writing: added`.
- `git diff --check`: exit 0, no output.
- Attempted `uv run pytest tests/viewer/test_server.py tests/e2e/test_view.py -q`: `19 failed, 6 passed in 1.14s`.
  All 18 socket-based viewer tests failed at socket creation with `PermissionError: [Errno 1] Operation not permitted`; the server-starting e2e test received the corresponding listen error.
  The coordinator must rerun those files outside the sandbox.
  The new request-boundary tests require no sockets.

### Finding left open

Minor m5 remains: extracting the routing helpers and separating commit-detail printing from `done_code` is a structural refactor across the lock, stale-list handling, and refusal back links.
It is outside the cheap fixes in this security round, and the existing routing behaviour remains covered.
I1, I2, m1, m2, m3, m4, m6, m7, and every m8 test gap are addressed.

Final restored-source builder gate:

```text
uv run ruff format --check && uv run ruff check && uv run mypy && uv run vulture && uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py && uv run lodge check --gate
433 files already formatted
All checks passed!
Success: no issues found in 193 source files
1353 passed in 35.50s
ok
note: area writing: added
```

The command exited 0; vulture produced no output.
The final selected CLI rerun gave `5 passed, 2 deselected in 0.06s`.
The restored focused tests gave `58 passed in 0.39s`.
A final rerun of the over-limit mutation, with the short-body fix present, received 400 rather than 413 (`1 failed in 0.28s`), confirming the server's early length check remains independently pinned.
All source mutations were restored before the final gate.
