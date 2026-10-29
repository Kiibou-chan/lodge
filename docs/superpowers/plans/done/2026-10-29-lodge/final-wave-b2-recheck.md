# Final wave, Part B2: recheck

Checked at da49d8c in a scratch copy (the scratch directory); the build worktree was not touched.
In the copy: format, ruff, mypy, vulture and 1061 tests pass (the gate step needs a git repository, so it was not run).

## Answered (fix reverted in the copy, test failed)

- 13, D11 (`viewer/pages.py:28-31`, `views.py:98`): reverting to the CLI text fails `test_entry_reasoning_renders_the_deciding_decisions_as_results`; each line shows its status once (run).
- 14: the three wordings in `apply.py:258-273` read correctly (not reverted).
- 15 (`feedback.py:78-83`, `writes.py:184`): removing the message fails `test_replacing_a_decision_another_decision_already_replaced_says_so`; `elif False:` in `_raced` fails `test_entry_created_by_another_add_is_a_conflict`.
- 16 (`checkout.py:170-190`): putting the umask read back fails `test_a_new_record_gets_the_umask_mode_without_the_umask_being_read`.
- 17 (`writes.py:148-151`): removing the early return fails `test_a_decision_far_ahead_of_the_clock_is_not_waited_for`.
- 18 (`render.py:10,63`, `pages.py` rows): the old regex fails `test_render_spec_escapes_indented_hashes_and_underline_headings`; dropping the statuses fails `test_flag_ids_on_list_and_spec_rows_are_links_with_their_status`.
- 19 (`post_tool_use.py:63,89,95`): reverting either the `respond` or the `run` half fails `test_relative_path_without_a_payload_folder_is_read_from_the_process_folder`.
- 11, 12, 20: refactors and text; suite green, no em-dashes in added text.

## Minor 1. No test pins the flags on the deciding decisions in an entry's reasoning

Handle: `tests/viewer/test_pages.py` (`test_record_page_flags_and_both_link_directions` now cuts the page at `<details` and checks the entry's own header only).
Scenario (run): replacing `shown.read` by `_NONE` in `pages.py:29` (`_results(shown.changing, "", ...)`) leaves all 37 viewer tests green, though the page then shows `awaiting the author on d-cccccc` without the link and status inside the reasoning.
Fix: in `test_entry_reasoning_renders_the_deciding_decisions_as_results`, assert the linked flag text (`awaiting the author on <a href="/r/d-cccccc">d-cccccc</a> <span class="status">current</span>`) appears inside `reasoning`.

## Minor 2. Item 17's last clause ends the guide line with "the author should know"

Handle: `src/lodge/cli/guide.md:50` (the guide is at its 60-line cap).
Scenario: the line tells an agent that the author should know but not to tell her; every other guide line addressing the author says "tell the author".
Fix: end with "tell the author", in the same line.

## Judged

- Item 17 "says so otherwise": the guide line plus check 1's message (`check_change.py:90`, "dated <date>, no later than <target>") is adequate for a related change; an unrelated change adds a decision dated before the newest, which nothing reports, but check 1 does not require it, so I raise no finding.
