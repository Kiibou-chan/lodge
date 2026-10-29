# Final wave B2 report

Items 11 to 20 of Part B, built test-first where behaviour changed.
`sh scripts/check.sh` is green: 1061 tests, structure tests included.

| Item | What changed | Test |
| --- | --- | --- |
| 11, D9 | `core.head_parts(v)` returns the header's parts; `views._head` and the viewer's `meta` both use it. A refactor, existing tests stay green. | `tests/viewer/test_pages.py`, `tests/core/test_views.py` (unchanged) |
| 12, D10 | `core.attachment_path(decision_id, name)` and `core.ATTACHMENTS` in `core/snapshot.py`, used by `snapshot`, `check_state`, `app/writes`, `gitstore/trees` and `checkout`, and the viewer's provenance. The hook's relative `attachments` segment is a folder name under the data root, not this path, and stays. A refactor. | existing tests |
| 13, D11 | `core.level2_views` returns the `Level1` views behind an entry's level 2 (`level2` text is built from it); `Shown.changing` carries them and the viewer renders them with `_results`, so each line shows its status once. | `test_level2_views_of_entry_are_level1_views_newest_first`, `test_show_of_an_entry_carries_the_deciding_views_with_its_reasoning`, `test_entry_reasoning_renders_the_deciding_decisions_as_results`; `test_record_page_flags_and_both_link_directions` now checks the entry's own header flags |
| 14, Task 7 N1 | The ID refusal tells upper case, wrong prefix, and wrong form apart and names the expected prefix and form. | `test_id_of_the_wrong_shape_says_so` |
| 15, Task 8 M5, R4 | Feedback "d-aaaaaa is already replaced by d-bbbbbb" (several: listed with "and"), not for a decision only this one replaces. The entry branch of `_raced` has its test; replacing the branch by `elif False:` made it fail, restored it passes. | `test_replacing_a_decision_another_decision_already_replaced_says_so`, `test_replacing_a_decision_only_this_decision_replaces_is_silent`, `test_entry_created_by_another_add_is_a_conflict` |
| 16, Task 9 M1 | New temporary files are created with `os.open(..., O_CREAT \| O_EXCL \| O_NOFOLLOW, 0o666)` under a random name, so the umask is never read by setting it; an existing file's mode is copied with `fchmod` as before. | `test_a_new_record_gets_the_umask_mode_without_the_umask_being_read` |
| 17, Task 10 N1, N2 | The guide says the listed attachment name is the file's own name, and that a decision dated more than three seconds ahead is not waited for (check 1 refuses a related change). `_after_newest` waits only when the newest decision is at most `_WAITS` seconds ahead. The guide stays at 60 lines. | `test_a_decision_far_ahead_of_the_clock_is_not_waited_for`, `test_a_decision_a_few_seconds_ahead_of_the_clock_is_waited_for` |
| 18, Task 11 N1, N2 | `render_spec` escapes `#` lines indented up to three spaces and lines of only `=` or `-`. `Read.statuses` carries every record's status; flag IDs on search, timeline, waiting and spec rows are links with their status. | `test_render_spec_escapes_indented_hashes_and_underline_headings`, `test_flag_ids_on_list_and_spec_rows_are_links_with_their_status` |
| 19, Task 12 N1 | `hook.run(..., cwd)` and `respond(..., cwd=)`: a relative path without a payload `cwd` starts from the process folder for both `context` and `respond` (`main` passes it, `None` if the folder is gone). | `test_relative_path_without_a_payload_folder_is_read_from_the_process_folder` |
| 20 | The `Derived` docstring says its maps hold known records only; a project-named constant in the core test helpers is `IMPORTED`. Text only. | none |

## Notes

- Item 17: the brief's "says so otherwise" is met by the guide sentence and by check 1's own message naming the date; no new add output was added.
- The working tree held an uncommitted ledger edit before this round; it was left alone and not committed.

## Closing round (four Minors)

- B1 Minor 1: `_Server.daemon_threads = False`, so `server_close()` in the existing `finally` waits for running request threads and their lock `finally` blocks run. Test `test_closing_the_server_waits_for_a_request_that_is_running` (a 0.3 s wait; failed before the change).
- B1 Minor 2: `output._marked` marks minted IDs inside check messages on a dry run. Test `test_dry_run_marks_new_decision_ids_provisional_on_check_lines`; the real add prints no mark.
- B2 Minor 1: `test_entry_reasoning_renders_the_deciding_decisions_as_results` asserts the linked "awaiting the author on d-cccccc" text inside the reasoning; with `_NONE` at `pages.py` it failed, restored it passes.
- B2 Minor 2: `guide.md:50` ends "tell the author"; the guide stays at 60 lines.
