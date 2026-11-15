# Task 7b report

Carried the ten writing-test files into `ts/tests/e2e`, keeping every retained Python test name and assertion, including every parametrised case.
All commands run in process against `testServer()` through `run(argv, io)`.
Added the two prescribed held-add tests, a direct `paths()` regression test, and a request-boundary CRLF regression test.
The ten parity rows now have their prescribed statuses and dropped names, and `tests/e2e/support.ts` has left knip's entry exemptions because its deferred exports now have readers.

## Scope and rulings

Read `CLAUDE.md`, the plan header, both sets of Global Constraints, Task 7b, its parity rows, its brief, the Task 7a report and correctness review, the three helpers, and every named Python source.
Read d-bwb1tt and d-4qv0xb through `lodge show --reasoning`.
`lodge waiting` reported nothing waiting for an agent or the author.
The coordinator confirmed sole-builder, test-first work without delegation because the unavailable superpowers skill in the header is a coordinator instruction.
The user's explicit commit and push instruction governs this run.
Earlier briefs, reports, and reviews were not edited.

No CLI implementation fix was needed.
The sole helper fix is `ts/tests/e2e/server.ts:110`: `paths()` now returns the sorted union of tree-file paths and attachment-text paths.
Before that fix, `attachment_lands_beside_the_decision_in_checkout_mode` failed its attachment-path membership assertion, and `several_attachments_and_a_dry_run` found an empty attachment directory listing instead of the two names.
The coordinator explicitly authorised this helper change outside the original file scope, requiring a direct regression test and the existing `paths()` consumers to remain green.
`paths_lists_records_and_attachments_sorted` checks the union's four paths, order, attachment membership, decision count, and spec-file count.
Reverting the helper fix made that test fail at its expected length of four versus three (M19), and the fix was restored.
All existing e2e tests, including the earlier `paths()` consumers, pass.

## Substitutions and specified changes

Every carried test uses the in-memory store and handler instead of the Python git-backed runtime.
Publication lines retain the Python content with `published` replacing `staged`.
Where a Python assertion reads git or a record file, its replacement reads the server's store as follows.

| Test or group | d-bwb1tt substitution or d-4qv0xb change |
|---|---|
| `attachment_lands_beside_the_decision_in_checkout_mode` | Reads `lodge/attachments/<decision>/run.log` through `stored()` and compares LOG exactly, including CRLF and café; the staged-path assertion becomes membership of the store's paths. |
| `several_attachments_and_a_dry_run` | Checks no attachment paths after the dry run, then compares the exact stored directory names with `["notes.txt", "run.log"]`. |
| `attachment_that_is_not_utf8_is_refused` | Checks no attachment paths in the store after refusal. |
| `add_dry_run_publishes_nothing` | Compares store paths before and after instead of git status, and retains the search assertion. |
| `add_failing_check_exits_1` | Counts the store's spec/storage paths instead of staged paths, still requiring zero. |
| `add_new_decision_entry_area` | Counts the three stored record files instead of five staged files, since server init creates no `.gitkeep`; keeps the publication IDs, area note, show, and clean check assertions. |
| `draft_text_is_printed_without_an_extra_newline` | Finds the entry in store paths, reads its stored text, and requires the draft's newline count to be exactly the stored count plus one. |
| `import_needs_the_flag_and_a_listed_source` | Requires exit 0 and empty error output for `--import`, matches the exact final held line, approves through the registered person's session, requires `published` in the helper, takes the first decision ID from the approval, and checks both `imported` and `unquoted` through `show`. |
| `agent_edit_in_the_same_second_is_flagged` | Stands the server clock still before the author seed; the seed asserts its held line and approves through the person's session, taking the ID from the published approval; requires `slept` to equal `[0.75]`, then retains every waiting, show, and gate assertion. |
| `author_words_are_recorded_exactly` | Per d-4qv0xb and d-2v8vtk, matches the held line for the relayed question, approves through the person's session, requires `published` in the helper, and takes the question ID from that approval; asserts the command's exact author/time/place/text substring and loads the stored thread with `load(tree({rev: null, files: ...}))`, requiring message text `a\rb\nc\nd`. |
| Other successful add and thread carries | Retain their assertions with `published` substituted for `staged`; shared seeds use the same drafts and the existing server helper. |

The person's session is established by the existing software-authenticator registration flow, not by inserting a session into the accounts store.
The new held-add tests intentionally inspect the held or dry-run answer without approving it.
No Task 7b test rewrites a published decision.
The two new-file changes of d-4qv0xb for `check_and_gate` and `broken_agent_decision_warns_above_show` remain in Task 7a and are untouched; this task applies its relayed-message change above.

Dropped exactly the three names prescribed by the plan: `attachment_lands_on_the_branch_in_branch_mode`, `agent_edit_in_the_same_second_publishes_in_branch_mode`, and `thread_files_are_staged_not_committed`.
Their changed parity rows explain that the server has no branch mode or staged thread files.
No other Python test name or parametrised case was dropped.
The author-message grammar test retains all three missing-provenance combinations and the exact Python message.
Ordering comparisons assert the compared text or list item's presence before using `indexOf`, preserving Python's raising `str.index` behaviour.
Output line assertions use `splitLines` without stripping trailing spaces.

## Mutation definitions

Each mutation was applied alone, its targeted tests were run, failure was observed, and the source was restored in a `finally` block.
All killed runs exited 1, and the final gate ran after every mutation was reverted.
Mutation handles refer to the restored source.

| Mutation | Deliberate defect and handle |
|---|---|
| M01 | `ts/src/cli/commands.ts:64`: send the attachment's full path instead of its base name. |
| M02 | `ts/src/cli/commands.ts:67`: omit the attachment-specific UTF-8 explanation. |
| M03 | `ts/src/cli/commands.ts:153`: replace the caught error's message with `mutated error`, losing the original filename, line, or diagnostic. |
| M04 | `ts/src/cli/commands.ts:44`: replace the grammar error output with `mutated`, losing usage or provenance requirements. |
| M05 | `ts/src/cli/client.ts:55`: throw a CLI error for the 422 `check-failed` answer instead of returning its decoded result. |
| M06 | `ts/src/cli/output.ts:86`: print `dry run: published`. |
| M07 | `ts/src/cli/output.ts:67`: use an empty provisional-ID set, removing provisional marks from feedback and check lines. |
| M08 | `ts/src/cli/output.ts:85`: replace the dry-run approval note with `note: omitted`. |
| M09 | `ts/src/cli/output.ts:77`: print only `published`, losing the publication IDs. |
| M10 | `ts/src/cli/output.ts:70`: replace the feedback prefix with `wrong`. |
| M11 | `ts/src/cli/output.ts:78`: print `changed` for the unchanged outcome. |
| M12 | `ts/src/cli/commands.ts:110`: surround printed draft text with a wrong prefix and an extra newline. |
| M13 | `ts/src/cli/output.ts:41`: replace the shown level-one block with `mutated`. |
| M14 | `ts/src/cli/threads.ts:35`: print `written` in place of the thread's publication outcome. |
| M15 | `ts/src/cli/threads.ts:22`: strip carriage returns from the message before sending it, corrupting the author's words. |
| M16b | `ts/src/cli/files.ts:31`: have `readDraft` keep CRLF instead of normalising it. |
| M17 | `ts/src/cli/output.ts:82`: shorten the held add's last line to `held`. |
| M18 | `ts/src/cli/threads.ts:35`: shorten the held thread answer to `held`. |
| M19 | `ts/tests/e2e/server.ts:112`: omit attachment paths from `paths()`, reverting the helper fix. |

The preliminary M16 run of the CRLF-preserving `readDraft` mutation survived the carried draft-edit test, even with a CRLF draft variant, because the server also normalises input.
No coverage is claimed from that run; the carried input was restored.
The additional `draft_crlf_is_normalised_before_request` forwards requests to the real handler and checks the request's draft text, so M16b fails directly at that boundary.

## Per-test Python and mutation evidence

Each row names the Python function carried by the identically titled TypeScript test, omitting only Python's `test_` prefix in the TypeScript title.
Both cases of each parametrised test below were observed failing under the listed mutation: `reply` and `close`, and `missing` and `non-utf8`.
The TypeScript counterpart is the parity row's file, with underscores changed to hyphens.

| Python test | Failing mutation and source handle |
|---|---|
| `tests/e2e/test_add_attach.py::test_attachment_lands_beside_the_decision_in_checkout_mode` | M01, `ts/src/cli/commands.ts:64` |
| `tests/e2e/test_add_attach.py::test_several_attachments_and_a_dry_run` | M01, `ts/src/cli/commands.ts:64` |
| `tests/e2e/test_add_attach.py::test_attachment_that_is_not_utf8_is_refused` | M02, `ts/src/cli/commands.ts:67` |
| `tests/e2e/test_add_attach.py::test_attach_with_two_new_decisions_is_refused` | M03, `ts/src/cli/commands.ts:153` |
| `tests/e2e/test_add_attach.py::test_attach_with_a_missing_file_is_refused` | M03, `ts/src/cli/commands.ts:153` |
| `tests/e2e/test_add_attach.py::test_decision_that_does_not_list_the_attachment_is_refused` | M03, `ts/src/cli/commands.ts:153` |
| `tests/e2e/test_add_bad_yaml_exits_2_naming_file_and_line.py::test_add_bad_yaml_exits_2_naming_file_and_line` | M03, `ts/src/cli/commands.ts:153` |
| `tests/e2e/test_add_bad_yaml_exits_2_naming_file_and_line.py::test_add_missing_fence_exits_2` | M03, `ts/src/cli/commands.ts:153` |
| `tests/e2e/test_add_non_string_scalar_exits_2.py::test_add_non_string_scalar_exits_2` | M03, `ts/src/cli/commands.ts:153` |
| `tests/e2e/test_add_new_decision_entry_area.py::test_add_missing_file` | M03, `ts/src/cli/commands.ts:153` |
| `tests/e2e/test_add_new_decision_entry_area.py::test_add_file_that_is_not_utf8` | M03, `ts/src/cli/commands.ts:153` |
| `tests/e2e/test_add_import.py::test_import_needs_the_flag_and_a_listed_source` | M03, `ts/src/cli/commands.ts:153` |
| `tests/e2e/test_draft_then_add_edit.py::test_draft_of_an_unknown_record` | M03, `ts/src/cli/commands.ts:153` |
| `tests/e2e/test_threads.py::test_ask_on_unknown_ref_exit_2` | M03, `ts/src/cli/commands.ts:153` |
| `tests/e2e/test_threads.py::test_reply_to_unknown_or_closed_thread_exit_2` | M03, `ts/src/cli/commands.ts:153` |
| `tests/e2e/test_threads.py::test_missing_message_file_exit_2` | M03, `ts/src/cli/commands.ts:153` |
| `tests/e2e/test_add_new_decision_entry_area.py::test_add_without_a_file_is_a_usage_error` | M04, `ts/src/cli/commands.ts:44` |
| `tests/e2e/test_threads.py::test_author_message_needs_where_and_when_exit_2` | M04, `ts/src/cli/commands.ts:44` |
| `tests/e2e/test_threads.py::test_where_with_an_agent_role_exit_2` | M04, `ts/src/cli/commands.ts:44` |
| `tests/e2e/test_add_failing_check_exits_1.py::test_add_failing_check_exits_1` | M05, `ts/src/cli/client.ts:55` |
| `tests/e2e/test_add_dry_run.py::test_add_dry_run_failing_check_exits_1` | M05, `ts/src/cli/client.ts:55` |
| `tests/e2e/test_add_import.py::test_import_from_an_unlisted_source_fails_the_check` | M05, `ts/src/cli/client.ts:55` |
| `tests/e2e/test_add_dry_run.py::test_add_dry_run_publishes_nothing` | M06, `ts/src/cli/output.ts:86` |
| `tests/e2e/test_add_dry_run.py::test_dry_run_marks_new_decision_ids_provisional` | M07, `ts/src/cli/output.ts:67` |
| `tests/e2e/test_add_dry_run.py::test_dry_run_marks_new_decision_ids_provisional_on_check_lines` | M07, `ts/src/cli/output.ts:67` |
| `tests/e2e/test_add_new_decision_entry_area.py::test_add_new_decision_entry_area` | M09, `ts/src/cli/output.ts:77` |
| `tests/e2e/test_add_new_decision_entry_area.py::test_add_prints_feedback_before_the_outcome` | M10, `ts/src/cli/output.ts:70` |
| `tests/e2e/test_add_new_decision_entry_area.py::test_add_nothing_changed` | M11, `ts/src/cli/output.ts:78` |
| `tests/e2e/test_draft_then_add_edit.py::test_draft_then_add_edit` | M12, `ts/src/cli/commands.ts:110` |
| `tests/e2e/test_draft_then_add_edit.py::test_draft_of_an_area` | M12, `ts/src/cli/commands.ts:110` |
| `tests/e2e/test_draft_then_add_edit.py::test_draft_text_is_printed_without_an_extra_newline` | M12, `ts/src/cli/commands.ts:110` |
| `tests/e2e/test_draft_then_add_edit.py::test_draft_of_a_decision_says_decisions_are_immutable` | M12, `ts/src/cli/commands.ts:110` |
| `tests/e2e/test_add_non_string_scalar_exits_2.py::test_yaml_words_that_look_like_values_stay_text` | M13, `ts/src/cli/output.ts:41` |
| `tests/e2e/test_same_second.py::test_agent_edit_in_the_same_second_is_flagged` | M13, `ts/src/cli/output.ts:41` |
| `tests/e2e/test_threads.py::test_ask_reply_close_round_trip` | M14, `ts/src/cli/threads.ts:35` |
| `tests/e2e/test_threads.py::test_author_words_are_recorded_exactly` | M15, `ts/src/cli/threads.ts:22` |

The import carry also fails M17 at its held-line match, and the exact-author-words carry also fails M18 at its held-line match.
The new `held_add_marks_its_ids_provisional` fails M07 and requires at least one minted-ID line, the exact 81-word feedback prefix with its provisional mark, a provisional suffix on every ID occurrence before the last line, exit 0, empty errors, and the exact final held line.
The new `dry_run_of_a_persons_decision_names_who_approves` fails M08 and requires exit 0, empty errors, and the exact final approval-note and dry-run lines.
The two additional regression tests fail M16b and M19 respectively, as detailed above.

## Verification

The required first `cd ts && bun test tests/e2e` run had 101 passes and three failures: two exposed the helper omission, and one exposed an incorrect Tree-constructor call in the new test, corrected to the actual object interface.
The first complete `sh scripts/check-ts.sh` before writing the parity rows exited 0 with 1,803 passes.
After writing the parity rows and removing the support entry exemption, the final `sh scripts/check-ts.sh` exited 0 with 1,804 passes, no failures or skips, and 5,208 assertions across 159 files.
This includes Biome with `--error-on-warnings`, TypeScript, dependency-cruiser, knip, the structure checks, the parity checks, and all earlier tests.
The final e2e-only run before the final two additional presence assertions had 106 passes and no failures; the complete final gate includes those assertions.
All source and test modules remain within 300 lines; the longest new test file is 158 lines.
`git diff --check` passed.
`LODGE_E2E_BINARY` was unset, no gate test opened a socket, and no package was installed or added.
The Coordinator step and socket/binary checks were not run.
