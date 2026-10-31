# Plan recheck 1

Plan: `docs/superpowers/plans/2026-10-31-lodge-viewer.md` at 61d91d1, the fix `git diff 4b57001 61d91d1`.
Answers: every Blocking and Important of `plan-review-correctness.md` (C) and `plan-review-practice.md` (P), and the three rulings of `advisor-ruling-2.md` (d-a3h9f3).
Plan line numbers are those of the fixed plan.
Every line is agent text, for the author and the planner to check.

## Counts

- Findings rechecked: 30 (C: 2 Blocking, 14 Important; P: 3 Blocking, 11 Important), plus the 3 rulings.
- Closed: 32 (29 findings, 3 rulings), of which two are closed with a declined part that is sound (C-I2 thread part, P-I8 split).
- Open: 0.
- Declined and accepted: 1 whole (P-I9), plus the two declined parts above.
- New Blocking: 0.
- New Important: 1 (N1).

## Blocking

- C-B1: closed. `read_rank` takes text matching `0|[1-9][0-9]*` (106, 121), and the tests accept `2` and `"2"` and refuse `-1`, `1.5`, `true`, `two`, `01`, `""` (135).
- C-B2: closed. Check 6 refuses a target "retired in `after`" that is not in the published `rests_on` (165), and the same-add test is at 173.
- P-B1: closed. Each task repeats what it used of a Call: derived order (124 to 126), cross-area lines (127), file shape and escape (212 to 240), `opened` (212), CR rule (39), messages (313), routes (431 to 442), areas by topic (536); the design path is at 20.
- P-B2: closed. The recipe, the BLOCKED rule, and the coordinator's `git add lodge/` are Global Constraints (25 to 27), with `--path-format=absolute`; Tasks 8, 9, and 11 point to them (509, 534, 583).
- P-B3: closed. `tests/core/test_thread_files.py` and `tests/app/test_thread_ops.py` (188, 262); the basename rule is at 33.
  I ran `find tests -name 'test_*.py'` for repeated basenames: only the existing `test_search.py` repeats, and no new name collides in `tests/`, `tests/core/`, or `tests/app/`.

## Important

- C-I1: closed (441, 450). UTF-8 bytes against `gate.token.encode("ascii")` under `hmac.compare_digest`, and `test_non_ascii_token_refused`.
- C-I2: closed with a sound partial decline. The lock is at 441 and the test at 451; a doubt sent twice opening two threads (Call 24, line 71) is visible and closable, so declining that part is adequate.
- C-I3: closed (271, 314, 319, 444). `REVERT_HEAD` and `sequencer` join the in-progress paths, and `test_no_commit_during_a_revert` uses a real revert.
- C-I4, P-I3: closed (32, 97, 151, 189, 464). The new files carry the near-full tests, and the Global Constraint names the three full files.
  Sizes checked: `tests/core/test_render.py` 118, `test_check_change.py` 166, `tests/app/test_writes.py` 171, `tests/hook/test_post_tool_use.py` 242, `tests/viewer/test_server.py` 186; each stays under 300 with the stated additions.
- C-I5: closed (440, 446, 453). `refuse_early` runs before the length is read, the old POST test expects 403, and the 411 test sends an allowed Host and Origin.
- C-I6, P-I2: closed (329, 336). `read_file(name, not_utf8, exact)` matches the signature of `commands._read` (`src/lodge/cli/commands.py:117`), so the move is mechanical and the import graph has no cycle.
- C-I7, P-I5: closed (433 to 438, 483, 493). The table fixes every field, Task 7 uses it, `test_rendered_forms_post_through_handle_post` joins forms to handler, `order: Literal[...]` replaces `written`, and `titles` is keyed by the `about` ID (302).
- C-I8: closed (22, 447, 452, 454). The three `test_view.py` tests run with `-k "passes_the_port or allow_host"`, which matches all three names.
- C-I9: closed (544). The statement speaks of an entry, and the extension to decisions sits in the coordinator decision (553).
- C-I10: closed (549, 550). The statement reads "does not show it as written by the author", and the Confirming decision names LODGE-6.
- C-I11: closed (538, 550, 553, 555). The edits and narrowings the review listed are all in Tasks 9a and 9b, and the rule narrows coordinator decisions only.
  The s-7ah5n7 part is closed by d-a3h9f3 below.
- C-I12: closed (539, 562). A "changed since" pass follows each section, and the verification counts the marks or names each remaining one.
- C-I13: closed by d-a3h9f3, see below.
- C-I14: closed by d-a3h9f3, see below.
- P-I1 (with C-M1): closed (260). `Interleaved.commit` delegates to `inner.commit`.
- P-I4: closed (34, 131, 318). Every produced field I traced has a reader in its own task: `Placed.depth`, `under`, and `also` in `test_render.py`; `Written.about`, `ThreadList.titles`, and `read`, `ThreadShown.read`, `ThreadsWaiting.titles` and `read` in Task 4's tests; `Committed.detail` and `Added.paths` in Task 4's tests.
  `ThreadShown.about` has no named assertion, which is Minor (M-a).
- P-I6: closed (360 to 457). Task 6a and Task 6b split cleanly, see "Produces and Consumes".
- P-I7: closed (523 to 564). Three parts, shared rules, a bound of "about 20 to 40 new entries" (531), and each part's verification.
- P-I8: closed with a sound partial decline. The baseline and `diff` are at 516 and 520; keeping Task 8 whole (Call 26, line 73) is adequate because a link is a reversible `link` edit.
- P-I9: declined, accepted. Call 26 says Tasks 3 and 4 stay whole because each pair shares one data type; the practice review itself ranked this the lesser split.
- P-I10 (with C-M2): closed (464). Task 7 updates the calls in `test_pages.py` and `test_post_routes.py`.
- P-I11 (with C-M9): closed (212 to 238). `opened` and an agent's `when` are plain, an author's `when` and `where` are quoted, and the example matches the rule.

## The three rulings of d-a3h9f3

- I13, a close without text: closed, applied in every place the ruling listed.
  Call 31 (78); check 1's exception (241); check 5's new rule (243); `close` and `appended` (206, 310); `thread_text` and the CLI output (344, 351); the viewer's "Closed by BY" (485); tests in Tasks 3, 4, 5, and 7 (249, 250, 318, 351, 494); the Task 9b entry (554); no "Closed." in the Global Constraint strings (41).
  The check 5 clause cannot misfire on a new thread, since it needs a published open thread.
- I14, the dependency order: closed, and I traced the algorithm by hand against the tests.
  `test_entry_after_what_it_rests_on` (written a, b, c; a on c) gives b, c, a with `a` under c.
  `test_under_is_the_target_placed_last` (d on a and b) gives a, b, d with d under b and `also == (a,)`.
  `test_dependant_follows_what_it_rests_on` (c on a) gives a, c, b.
  `test_spec_opens_by_dependency` (494) uses the same a, c, b case, and the "also rests on" line and the depth over 5 rule are at 487.
  A cycle falls back to the first unplaced entry, so the function ends.
- s-7ah5n7: closed (553, 554, 79). The sentence is added in Task 9b, its reasoning names d-a3h9f3 and the line 13 author decision, and Task 9 no longer waits on her.

## Declines in "Calls made", checked

- C-M8 (check 3 for thread messages), Call 27: sound.
  The design gives a thread checks 1, 2, and 5 (design line 100, read), the app refuses the role, and the hook advises against hand edits.
- P-M5 (`lodge draft q-…`), Call 28: sound.
  `resolve` looks only at `s.decisions` and `s.entries` (`src/lodge/core/search.py:36-45`) and `reads.draft` goes through `resolve_ref`, which raises `NotFound` for any other ID, so a thread ID already exits 2.
- P-M1, Call 29, and P-M10, Call 30: sound, both are proportion calls with the cost stated.

## Produces and Consumes after the splits

- 6a to 6b: `Lodge.confirm(ids, words, area, commit)`, `StaleList`, and `Written` are produced in 6a (381) and consumed in 6b (406).
- 6a to 7: `Behind`, `Shown.confirmable`, and `Lodge.behind_area` are produced in 6a and consumed in 7 (467).
- 6b to 7: `Gatekeeper.token`, `handle_post`, the route table, and `staged_world` are produced in 6b and consumed in 7 (467, 493); 7 changes `render` to take a token and lists the two test files whose calls it updates (462).
- 6a's draft goes through `writes.add(w, [(VIEWER, draft)], False, False)` (388), which matches `add(w, drafts, importing, dry_run, attachments=())` at `src/lodge/app/writes.py:46-52`.
- 9a, 9b, 9c: an entry created in a later part is never referenced by an earlier one, since each part's entries rest only on entries that exist.
  The six coordinator decisions are spread 1 (9a, Goals), 1 (9a, Confirming), 2 (9b), 2 (9c), which matches "six" at 531.
- Module budgets: `core/feedback.py` 179 plus about 30, `core/derive.py` 227 plus 21, `core/views.py` 220 plus 42, `cli/parser.py` 219 plus 20 all stay under 300.

## New problems

### Important

N1. The minute for the line 18 quote lies outside the range the design gives.
Handle: plan line 66 (Call 19) and 549 (`when: "2026-10-30 09:37"`); design line 10 ("Her words (2026-10-30, 09:41 to 09:47)").
Failure: an author decision is immutable (check 5), so a minute that is wrong needs her replacement, and 09:37 is earlier than d-dyrpc6's 09:41, the first of the quotes, while the design lists the line 18 quote last.
The plan says the coordinator read the minutes from the session, but names no transcript handle, and C-M12 asked for the check to be noted in the ledger.
Fix: Call 19 names where each minute was read (session file and line, or the message it came from), and either the minute is corrected into the range or the design's range note is corrected in the same task; without a handle, the task records the range end, `09:47`, which the design supports.

### Minor

- M-a. Global Constraint 39 says every message text "must not then be empty" (line 39), but a closing message has an empty text (310, 241).
  Fix: "must not then be empty, except a closing message".
- M-b. `test_two_concurrent_confirmations_write_once` (451) holds the first publish "until the second request has started", but under the lock the second request never reaches `publish`.
  Fix: say the second thread signals from `make_lodge`, called before the lock is taken, or that the test releases the first publish after a short wait; otherwise the test either hangs or passes without the lock.
- M-c. `src/lodge/app/writes.py` (213) is in the near-limit list, and Task 4 renames `_mint` and fills `Added.paths` without a stated line budget (260, 31).
  Fix: "at most 8 lines" in Task 4's Files.
- M-d. `ThreadShown.about` (280) has no assertion in `test_thread_shows_one_thread`; vulture may flag it.
  Fix: add `shown.about.id == "s-aaaaaa"` to that test.
- M-e. In each of Tasks 9a to 9c the last section's "changed since" pass has no later decision in the same part to carry its `edit` lines (539).
  The verification allows a named remaining mark (563), so this is adequate; the report line should say which part's decision will clear it.

## Files read

`CLAUDE.md`, `plan-fix-1.md`, `advisor-ruling-2.md`, both review files, the whole fixed plan (lines 1 to 590), design lines 8 to 20 and 96 to 101.
Code: `src/lodge/cli/commands.py:100-125`, `src/lodge/app/writes.py:46-52`, `src/lodge/app/reads.py:103-115`, `src/lodge/app/state.py:81-92`, `src/lodge/core/search.py:28-50`, line counts of every `src` module and the named test files.
I ran no tests; the plan has none yet, and I made no worktree.
