# Final fix wave report

No commit was made.
All requested findings are fixed; verification results follow below.
Records were read through lodge, drafted under `.drafts/fix-wave/`, dry-run first, and added using the Global Constraints sandbox index and object-directory recipe.
The real index was not staged.

| Finding | Change | Records |
| --- | --- | --- |
| Final I1 | Indentation now names the last same-area dependency placed, other same-area dependencies on the also-rests-on line, and cross-area links separately; reasoning names d-a3h9f3. | s-2bzwzv, d-azeks4 |
| 9b/9c I1 | Coordinator narrowing covers both obsolete read-only claims, retains local operation and reads, and explicitly leaves editing for later under d-2hcgav. | d-vme42w, d-x42f0x, d-azeks4 |
| 9b/9c I2 | Area drafts change the model introduction to three record kinds and the writing introduction to eight checks. | area:model, area:writing, d-azeks4 |
| 9b/9c I3 | Unpublished decisions amended through lodge drafts: append-only messages preserve what was said; decision doubts reach the specification because the author reads there; entries hold current claims whereas decisions record changes; link-only changes neither flood waiting nor clear freshness warnings. | d-68b0j2, d-6zyet3 |
| Final m2 | Commit-marker test parametrised over rebase-merge, rebase-apply, and sequencer; removing the latter two guards produces two failures. | None |
| Final m3 | Unsafe commit description includes revert and a stopped sequence of picks or reverts, with Call 25 as its reason. | s-mc9n8a, d-azeks4 |
| Final m4 | Decision doubt marks distinguish directly changed entries from their dependants. | s-r7c3wn, d-azeks4 |
| Final m5 | Deferred dependency added with action link; trusting and displaying the author label relies on its defined fields. | s-j5ttw1 rests on s-aq3a5k, d-azeks4 |
| Final m7 | Unpublished reasoning says built instead of approved, amended through lodge draft. | d-3d4g9j |
| Final m10 | Confirm form uses “The decisions stay the agents'” for multiple IDs and retains the singular for one ID. | None |
| Final m11 | Both frozen designs named in both CLAUDE.md passages. | None |
| Task 6b parked m5 | handle_post delegates form validation to _parse_form and routes to _Post methods, with shared field access and result handling; lodge creation, locking, refusals, and redirects retain their order. | None |

The first dry run advised adding number handles for plan Call 25, Task 3, and Task 8; these were added before the clean dry run and real add.
No check line appeared in either dry run.
Area rank, order, and introduction notes describe differences against the published state.
The unpublished-decision immutability advice is expected; the changes pass the publication check against main, under the user's explicit instruction and d-38xscb's unpublished-record rule.

## Failing outputs

The behaviour change was tested before implementation:

```text
uv run pytest tests/viewer/test_forms.py -q
FAILED tests/viewer/test_forms.py::test_confirm_note_matches_number_of_decisions
E assert 'The decisions stay the agents' in '<form ... The decision stays the agent&#x27;s ...'
1 failed, 8 passed
```

The new marker cases also reject the review's mutation, with the production guards restored immediately afterwards:

```text
uv run pytest tests/gitstore/test_commit.py -q -k during_a_rebase
FAILED tests/gitstore/test_commit.py::test_no_commit_during_a_rebase[rebase-apply]
FAILED tests/gitstore/test_commit.py::test_no_commit_during_a_rebase[sequencer]
E AssertionError: assert CommitOutcome.COMMITTED is CommitOutcome.IN_PROGRESS
2 failed, 1 passed, 14 deselected
```

Focused checks after implementation:

```text
uv run pytest tests/viewer/test_post_gate.py tests/viewer/test_post_routes.py tests/viewer/test_forms.py tests/gitstore/test_commit.py -q
65 passed
```

## Final verification

The plan's sandbox gate is green: ruff format, ruff, mypy strict (194 source files), vulture, pytest excluding the two socket-bound files (1369 passed, 1 network-dependent wheel test skipped), and lodge check --gate (ok).
The selected non-socket viewer command tests also pass: `uv run pytest tests/e2e/test_view.py -q -k 'passes_the_port or allow_host_is_repeatable or allow_host_with_space'` gives 5 passed, 2 deselected.
`git diff --check` is clean.
`lodge spec` has zero `rests on ..., changed since` marks; both groups of `lodge waiting` are empty.
There was no need to reaffirm any dependent entry.

The full `sh scripts/check.sh` was attempted as well.
Its static checks pass, but sockets are prohibited in this sandbox, as the plan warns: 19 failed, 1375 passed, 1 skipped.
The e2e server test gets exit 2 instead of 0 when lodge cannot bind; the server tests raise `PermissionError: [Errno 1] Operation not permitted` when constructing a socket.
The wheel test skips because network access is unavailable.
The full gate still needs an outside-sandbox run by the coordinator; no test or check was weakened to conceal this environment limit.

```text
FAILED tests/e2e/test_view.py::test_view_serves_the_project_until_interrupted
FAILED tests/viewer/test_server.py::test_server_routes - PermissionError: [Er...
FAILED tests/viewer/test_server.py::test_pages_are_html_and_style_is_css - Pe...
FAILED tests/viewer/test_server.py::test_search_filters_arrive_from_the_query
FAILED tests/viewer/test_server.py::test_a_fresh_lodge_for_each_request - Per...
FAILED tests/viewer/test_server.py::test_lodge_error_is_a_page_with_its_message
FAILED tests/viewer/test_server.py::test_other_failures_are_a_plain_500 - Per...
FAILED tests/viewer/test_server.py::test_unreadable_file_banner_reaches_the_browser
FAILED tests/viewer/test_server.py::test_post_without_origin_and_other_methods_refused
FAILED tests/viewer/test_server.py::test_response_headers_lock_the_page_down
FAILED tests/viewer/test_server.py::test_bound_to_loopback_only - PermissionE...
FAILED tests/viewer/test_server.py::test_serve_reports_a_port_in_use_as_one_sentence
FAILED tests/viewer/test_server.py::test_serve_announces_the_address_and_stops_on_interrupt
FAILED tests/viewer/test_server.py::test_closing_the_server_waits_for_a_request_that_is_running
FAILED tests/viewer/test_server.py::test_post_through_the_socket_redirects - ...
FAILED tests/viewer/test_server.py::test_put_answers_405_allowing_post - Perm...
FAILED tests/viewer/test_server.py::test_allow_host_is_served - PermissionErr...
FAILED tests/viewer/test_server.py::test_post_without_length_411 - Permission...
FAILED tests/viewer/test_server.py::test_negative_length_400 - PermissionErro...
19 failed, 1375 passed, 1 skipped
```

Status: DONE_WITH_CONCERNS, solely for the unavailable outside-sandbox full-gate verification.
No requested finding remains unfixed.
Other findings omitted from the user's requested wave remain parked in their original reviews.
