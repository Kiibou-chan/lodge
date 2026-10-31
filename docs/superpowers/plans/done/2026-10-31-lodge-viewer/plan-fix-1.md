# Plan fix round 1

Plan: `docs/superpowers/plans/2026-10-31-lodge-viewer.md`, from 3311c74, answering `plan-review-correctness.md` (C) and `plan-review-practice.md` (P), and applying the advisor's ruling d-a3h9f3 (`advisor-ruling-2.md`) on C-I13, C-I14, and the s-7ah5n7 part of C-I11.
Line numbers are those of the fixed plan.
Counts: 50 findings fixed; 5 declined, and 2 declined in part, each with a line in "Calls made".

## Changelog

| Finding | What changed | Plan line |
| --- | --- | --- |
| C-B1 | `read_rank` takes a text matching `0\|[1-9][0-9]*`, since the loader gives every scalar as text; tests accept `2` and `"2"`, refuse `-1`, `1.5`, `true`, `two`, `01`, `""` | 106, 117, 135 |
| C-B2 | Check 6 on `rests_on`: a target retired in `after` | 165 |
| C-I1 | the token is compared as UTF-8 bytes with `hmac.compare_digest`; `test_non_ascii_token_refused` | 441, 450 |
| C-I2 | one module-level `threading.Lock` around each viewer write; `test_two_concurrent_confirmations_write_once`; the thread part declined | 441, 451, 70 to 71 (Calls 23, 24) |
| C-I3 | `REVERT_HEAD` and `sequencer` mean in progress; outcome and notice say "or revert"; `test_no_commit_during_a_revert` | 271, 314, 319, 444 |
| C-I4, P-I3 | new test files for the near-full ones, and a Global Constraint naming them | 32, 97, 151, 464 |
| C-I5 | `do_POST` runs `refuse_early` (Host, Origin) before reading the length; the old POST test expects 403; the 411 test sends an allowed Host and Origin | 440, 446, 453 |
| C-I6, P-I2 | `_read` moves to a new `cli/files.py` imported by `commands.py` and `threads.py` | 329, 336 |
| C-I7, P-I5 | Task 6b's table fixes the routes' fields; Task 7 uses it; `test_rendered_forms_post_through_handle_post` | 433, 483, 493 |
| C-I8 | `--allow-host` tests and the `view(port, allow_hosts)` test in Task 6b, run with `-k` | 22, 452 |
| C-I9 | line 13's author decision speaks of an entry; the extension to decisions is in Task 9b's coordinator decision | 543, 553 |
| C-I10 | line 18's statement reads "does not show it as written by the author"; the Confirming decision names LODGE-6 | 549, 550 |
| C-I11 | Task 9b edits s-ms14fq, s-wcv4en, s-8f6scf, s-aw5a1j and narrows d-zerbz9, d-3epcjd, d-4032xv; the rule "narrows the coordinator decisions whose statements it makes false, never an author decision"; s-7ah5n7 gains one sentence per d-a3h9f3 | 538, 553, 555, 79 (Call 32) |
| C-I12 | each section's add is followed by a "changed since" pass, and the verification counts the marks | 539, 563 |
| C-I13 | per d-a3h9f3: a close without text writes a closing message with an empty text, read as "closed by BY"; "Closed." leaves the verbatim strings; check 1 and check 5 rules; tests in Tasks 3, 4, 5, and 7; the Task 9b entry on closing | 41, 78 (Call 31), 241, 243, 310, 344, 485, 494, 554 |
| C-I14 | per d-a3h9f3: the derived order is depth first, `under` the last target placed, `Placed.also`; tests; "also rests on" line in the viewer; Task 9c entry | 55 (Call 8), 115, 124 to 126, 131, 134, 487, 494, 558 |
| C-M1, P-I1 | `tests/gitstore/test_concurrent.py` in Task 4's Files, `Interleaved.commit` delegating | 260 |
| C-M2, P-I10 | Task 7 updates the calls in `test_pages.py` and `test_post_routes.py` | 464 |
| C-M3 | `staged_world()` in `tests/viewer/world.py` | 429, 451 |
| C-M4 | `parse_qs(..., errors="strict")`, 400 on `ValueError` and `UnicodeDecodeError`; two tests | 441, 450 |
| C-M5 | an `id` or `<q>` that is not an ID of its kind is 400; `Location` parts quoted | 441, 442 |
| C-M6 | a length not matching `[0-9]+` is 400; `_Handler.timeout = 10`; `test_negative_length_400` | 446, 453 |
| C-M7 | a field `write_thread` cannot carry becomes a `LodgeError`; `test_unstorable_where_refused`; a Global Constraint | 38, 308, 318 |
| C-M8 | declined: design line 100 gives threads checks 1, 2, and 5 only | 74 (Call 27) |
| C-M9, P-I11 | `opened` and an agent's `when` written plain; the example matches | 214 to 238 |
| C-M10, P-M4 | the `view` help, the viewer's docstring, and the 405 text drop "read-only"; Task 10 greps `src/` too | 401, 446, 447, 576 |
| C-M11 | Task 11 adds a coordinator process decision for the ranks | 585 |
| C-M12 | the coordinator's minutes for each quote; d-dyrpc6 and d-2hcgav not recorded again | 66 (Call 19), 543 to 549 |
| C-M13 | `behind_area` counts every entry of the area's folder, retired too; a test | 384, 391 |
| C-M14 | check 2 message reads "which does not exist" | 163 |
| C-M15 | `test_viewer_writes_only_new_decisions_and_thread_files`, `test_confirm_writes_only_a_new_decision_file`, `test_search_and_timeline_leave_threads_out` | 318, 392, 451 |
| C-M16 | `ID_KIND` gains `q`; `test_malformed_id_is_problem_1` | 186, 249 |
| P-B1 | every task repeats what it used from a Call (the derived order, cross-area lines, file shape and escape, `opened`, CR rule, commit messages, routes, areas by topic); the design path in Global Constraints | 18, 39 to 40, 124 to 127, 214 to 238, 302 to 314, 433 to 442, 536 |
| P-B2, P-M7 | the sandbox `lodge add` recipe, with absolute paths, the BLOCKED rule, and the coordinator's `git add lodge/` in Global Constraints | 25 to 27 |
| P-B3 | `tests/core/test_thread_files.py` and `tests/app/test_thread_ops.py`; a Global Constraint on unique basenames | 33, 188, 262 |
| P-I4 | a Global Constraint that every produced field is read in its task, and tests that read `Placed.also`, `titles`, `read`, `about`, `detail` | 34, 131, 318 |
| P-I5 | `spec_page` takes `order: Literal["dependency", "written"]`; `titles` keyed by the `about` ID | 302, 478 |
| P-I6 | Task 6 split into 6a (the confirmation) and 6b (the write gate) | 69 (Call 22), 360, 398 |
| P-I7 | Task 9 split into 9a, 9b, 9c, with shared rules and a count bound | 69 (Call 22), 523 to 564 |
| P-I8 | a `lodge waiting` baseline and a `diff`; the split declined | 516, 520, 73 (Call 26) |
| P-I9 | declined: Tasks 3 and 4 stay whole | 73 (Call 26) |
| P-M1 | declined: the Calls stay in the plan | 76 (Call 29) |
| P-M2 | every new test file marked "(new)" | the Files lists |
| P-M3 | the `test_server.py` lines named; a failing socket test returns as a fix round | 24, 453 |
| P-M5 | declined: `lodge draft q-…` already exits 2 | 75 (Call 28) |
| P-M6 | Task 10 orders the design's last line before the glob, and greps for dashes | 573, 576 |
| P-M8 | line 274's two sentences split; line 3 is the template's | 311 to 312 |
| P-M9 | Task 1 Step 4 checks the entry order unchanged too | 142 |
| P-M10 | declined: Task 11 stays apart from Task 10 | 77 (Call 30) |
