# Task 7 report

Implemented the viewer's pages without staging, committing, or pushing.
No lodge records were added or changed.

## Changes per file

- `src/lodge/core/order.py`: added the frozen `Branch` and `rests_on_tree`, following dependencies to roots, retaining titles and statuses, omitting missing targets, and stopping ancestor cycles.
- `src/lodge/core/__init__.py`: exported `Branch` and `rests_on_tree`.
- `src/lodge/app/results.py`: added the defaulted `Shown.rests_on` and `Shown.supports` fields.
- `src/lodge/app/reads.py`: populated both fields from the same checked state used for the record.
- `src/lodge/viewer/forms.py`: added confirmation, doubt, question, reply, and optional closing-text forms, with relative POST actions and escaped hidden tokens and fields.
  Rendered threads have escaped message text and provenance, chronological order, open-thread controls, and a distinct closing heading without an empty paragraph.
- `src/lodge/viewer/spec.py`: added dependency and written specification views, area-preserving order links, linked area headings, capped indentation, additional and cross-area dependencies, and area confirmation lists and forms.
- `src/lodge/viewer/pages.py`: added record forms, thread sections, dependency trees, reverse dependencies, and the two waiting groups with linked thread heads, including state, message count, last sender, and record title.
  Re-exported `spec_page` for existing page callers.
- `src/lodge/viewer/server.py`: passed the live gate token through rendering, selected written order from the query, loaded the area confirmation list, and used the existing single-state `waiting_all` read.
- `src/lodge/viewer/style.css`: added five indentation steps, thread borders and spacing, notices, and textarea and form spacing within the existing palette.
  No inline styles were added.
- `tests/viewer/test_forms.py`: added the eight form tests named below and an HTML parser that extracts actions and fields for actual write-handler submissions.
- `tests/viewer/test_pages_threads.py`: added the ten page tests named below.
- `tests/core/test_order.py`: added the two tree tests named below.
- `tests/viewer/test_pages.py`: updated calls for the token, order, area, behind, and waiting interfaces.
  Updated the existing heading assertion from plain `Storage` to the required linked area heading.
- `tests/viewer/test_post_routes.py`: passed the token to the existing redirect-notice render test.
- `vulture_allow.py`: added the standard-library `HTMLParser.handle_starttag` callback to the existing callback allow-list.
  Vulture cannot infer that `HTMLParser.feed` dispatches to the overridden method in the new form tests.
  This is the only additional file outside the brief's implementation and test list.

No existing behavioural assertion outside the brief's files needed changing.
The pre-existing review and brief files were left untouched.
`ThreadShown.about` remains optional; this task reads a thread's own `about` identifier and does not assume the optional record exists.

## Test-first evidence

The first run of the required three-file command reported `17 failed, 14 passed in 0.47s`.
Three negative tests passed vacuously while there were no forms or threads, so their assertions were strengthened before implementation to require the expected thread or token-bearing forms as well.
The second pre-implementation run reported `20 failed, 11 passed in 0.47s`.
Every named new test then had a failing run before its implementation.
The replaced-decision case was subsequently strengthened to use a real replacement decision rather than only a non-confirmable result.

The following table records the first relevant failing assertion or exception for each new test, omitting repository-specific absolute paths.

| Test in `tests/viewer/test_forms.py` | Failing output |
| --- | --- |
| `test_confirm_form_on_a_confirmable_decision` | `AssertionError`: `action="/confirm"` absent |
| `test_no_confirm_form_on_author_confirmed_or_replaced_decisions` | `AssertionError`: hidden token absent |
| `test_doubt_and_question_forms_on_every_record` | `AssertionError: assert [] == ['doubt', 'question']` |
| `test_open_thread_has_reply_and_close` | `AssertionError`: `action="/threads/q-111111/reply"` absent |
| `test_closed_thread_has_neither` | `AssertionError`: `id="q-111111"` absent |
| `test_thread_text_is_escaped` | `AssertionError`: `&lt;script&gt;Why?&lt;/script&gt;` absent |
| `test_forms_post_to_relative_actions_only` | `AssertionError: assert 0 == 4` |
| `test_rendered_forms_post_through_handle_post` | `AssertionError: assert 0 == 3` |

| Test in `tests/viewer/test_pages_threads.py` | Failing output |
| --- | --- |
| `test_threads_newest_last` | `ValueError: substring not found` |
| `test_entry_tree_down_to_roots_and_one_level_up` | `AttributeError: 'Shown' object has no attribute 'rests_on'` |
| `test_spec_opens_by_dependency` | `TypeError: render() takes 2 positional arguments but 3 were given` |
| `test_spec_also_rests_on_line` | Same `TypeError` |
| `test_thread_closed_without_text_shows_closed_by_author` | `AssertionError`: `Closed by author` absent |
| `test_spec_as_written` | Same `TypeError` |
| `test_spec_cross_area_line` | Same `TypeError` |
| `test_area_page_lists_decisions_entries_and_hidden_ids` | Same `TypeError` |
| `test_area_page_without_unconfirmed_has_no_form` | Same `TypeError` |
| `test_waiting_page_has_both_groups` | Same `TypeError` |

| Test in `tests/core/test_order.py` | Failing output |
| --- | --- |
| `test_rests_on_tree_reaches_the_roots` | `ImportError: cannot import name 'rests_on_tree' from 'lodge.core'` |
| `test_rests_on_tree_stops_on_a_cycle` | Same `ImportError` |

After implementation, the required three-file run reported `31 passed in 0.39s`.
The form round-trip test extracts and submits all three decision-page forms, the area confirmation form, and all four entry-page forms with an open thread, using a fresh `staged_world()` for each action, and requires a 303 response and the exact expected field names.
The empty-close test also checks that the parsed closing message has no text and the stored thread contains no invented `Closed.` message.

A later review strengthened `test_waiting_page_has_both_groups` to require the thread state, message count, and last sender before implementing those head details.
It failed with `AssertionError` on `"open" in text and "1 message" in text and "last by reviewer" in text`, reporting `1 failed, 9 deselected in 0.28s`.
The first attempted edit missed the target string and the rerun still failed, reporting `1 failed, 9 passed in 0.36s`.
The corrected edit passes.

## Commands and results

Read-only inspection used `cat`, `rg`, `sed`, `git diff`, `git status --short`, and `wc -l` on the brief, `CLAUDE.md`, the interaction design, the existing interfaces, tests, and structure rules.
The new source modules contain 71 and 59 lines; the modified pages module contains 173 lines, and the existing page tests contain 246 lines.
No structure limit was relaxed.

- `uv run pytest tests/viewer/test_forms.py tests/viewer/test_pages_threads.py tests/core/test_order.py -q`: red and green results recorded above; latest result `31 passed in 0.39s`.
- `uv run ruff format`: final edit run `1 file reformatted, 431 files left unchanged`.
- Initial `uv run ruff check`: `Found 5 errors`, covering import order, local imports, and a long line.
  `uv run ruff check --fix` fixed import order; formatting and explicit line splitting resolved the remaining long lines.
- Initial `uv run mypy`: one error because the local order variable inferred `str` rather than the required literal union.
  Added its literal annotation; latest output `Success: no issues found in 192 source files`.
- Initial `uv run vulture`: `tests/viewer/test_forms.py:17: unused method 'handle_starttag' (60% confidence)`.
  Added the callback allow-list entry; subsequent runs produced no output and exited successfully.
- `uv run pytest tests/viewer/test_forms.py tests/viewer/test_pages_threads.py tests/core/test_order.py tests/viewer/test_pages.py tests/viewer/test_post_routes.py -q`: `70 passed in 0.78s` before the final waiting-head refinement.
- `uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py`: first broad run `1327 passed in 35.71s`.
- `uv run pytest tests/e2e/test_view.py -q -k 'test_view_passes_the_port_to_the_viewer or test_allow_host_is_repeatable_and_passed or test_allow_host_with_space_slash_or_empty_exits_2 or test_view_outside_a_repository_is_one_sentence'`: `6 passed, 1 deselected in 0.35s`.
- `git diff --check`: no output, successful.

Final builder gate result is recorded below.

## Coordinator checks and concerns

The socket-bound `tests/viewer/test_server.py` and `tests/e2e/test_view.py::test_view_serves_the_project_until_interrupted` are left for the coordinator outside the sandbox.
All six socket-free cases in the latter file were run explicitly.
The coordinator still needs to run `sh scripts/check.sh` and open one decision, one entry, `/spec`, an area page, and `/waiting` in a browser, recording those observations here.
No browser or socket-server verification is claimed by this report.

The specification renderer consumes the existing `Placed` structure and its existing parent selection without changing Tasks 1 to 6b's ordering algorithm.
No other implementation uncertainty remains.

## Final builder gate

Ran the brief's complete builder gate after the final source and test changes:

```sh
uv run ruff format --check && uv run ruff check && uv run mypy && uv run vulture && uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py && uv run lodge check --gate
```

It exited 0 with these final outputs:

```text
432 files already formatted
All checks passed!
Success: no issues found in 192 source files
1327 passed in 35.50s
ok
note: area constraints: added
note: area hook: added
note: area levels: added
note: area model: added
note: area purpose: added
note: area reading: added
note: area rollout: added
note: area storage: added
note: area structure: added
note: area writing: added
```

Vulture produced no output and exited 0.
The area notes above are informational output from the existing repository state.
