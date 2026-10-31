# Plan review: correctness against the design and the code

Plan: `docs/superpowers/plans/2026-10-31-lodge-viewer.md` (branch `lodge-viewer`, commit 3311c74).
Angle: correctness against the design (`docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md`), the advisor's ruling d-7w5aq0, the specification in lodge, and the code under `src/lodge/` and `tests/`.
Plan line numbers below are those of the plan file at 3311c74; "design N" is a line of the design.
Every finding is agent text, for the author and the planner to check.

## Blocking

### B1. `read_rank` asks for an integer that the YAML loader never returns

Handle: plan lines 86 and 109; `src/lodge/core/yamlio.py:28-31` (`_TextLoader` has no implicit resolvers).
The loader turns every scalar into text, so `rank: 2` reads as the string `"2"`, exactly as `rank: "2"` does.
Verified by running `load_yaml('rank: 2\nb: "2"\nc: true\nd: 1.5\ne: -1')`, which gives `{'rank': '2', 'b': '2', 'c': 'true', 'd': '1.5', 'e': '-1'}`.
Failure: `read_rank` as specified ("int, not bool, >= 0") refuses every rank in every file, `write_area` with `rank: N` never reads back, so `test_rank_round_trips` cannot pass, and `test_rank_must_be_a_whole_number` asks to refuse `"2"`, which the loader cannot tell from `2`.
Fix: `read_rank(value: object) -> int` takes a `str` matching `[0-9]+` (optionally refusing a leading zero) and returns its `int`; anything else is a `FormatError` with key `rank`.
The test's cases become `-1`, `1.5`, `true`, `two`, and an empty string refused, and `2` and `"2"` both accepted as 2.

### B2. Check 6 on `rests_on` cannot refuse a target retired in the same add, which Review Focus 4 tests

Handle: plan line 139 ("retired in both states"), line 147 (`test_rest_on_entry_retired_in_the_same_add_is_refused`), line 66 (Review Focus 4); design 109.
A target retired by the same add is current in the published state, so "retired in both states" lets it pass, and the test that Review Focus 4 asks for fails.
The "both states" rule of `_links_to_dead` (`src/lodge/core/check_change.py:104-123`) exists so that a decision reviving an entry may edit it; for `rests_on` the matching rule is "retired in `after`", since a target revived in the same add is current there.
Fix: line 139 reads "for each target not in its published `rests_on` that is retired in `after`: `{e}: rests on {t}, which is retired`", and `test_new_rest_on_retired_entry_fails_check_6` keeps its value.

## Important

### I1. `hmac.compare_digest` on text raises on a non-ASCII token, a 500 where Review Focus 5 wants a 4xx

Handle: plan line 365 (`hmac.compare_digest`), line 375 (`test_token_compared_with_hmac`), line 67 (Review Focus 5).
Verified by running `hmac.compare_digest('é'*43, 'a'*43)`: `TypeError: comparing strings with non-ASCII characters is not supported`.
Failure: a form posted with `token=%C3%A9...` reaches `compare_digest` as text and raises, so the request ends in a 500, not the 403 the plan names.
Fix: compare `value.encode("utf-8")` with `gate.token.encode("ascii")`, and add `test_non_ascii_token_refused` (403, nothing written) to Task 6.

### I2. Two submissions at once both write: the stale check is not atomic with the publish

Handle: `src/lodge/viewer/server.py:21` (`ThreadingHTTPServer`); `src/lodge/gitstore/checkout.py:48-63` (`publish` rejects only when a path in `writes` changed); plan line 364 (`confirm`), line 63 (Review Focus 1).
The viewer answers requests in threads, and a double click sends two `POST /confirm` requests that run side by side.
Both read the state before either writes, both find the list current, and each publishes a new decision file under its own ID, so `CheckoutStore.publish` rejects neither; in branch mode the second is rejected on the moved tip, but `writes.add` retries without running the stale check again (`src/lodge/app/writes.py:58-66`).
The result is two author confirmations of the same decisions, the outcome Review Focus 1 exists to prevent; `test_second_identical_confirmation_is_stale` runs the two in sequence, so it passes anyway.
The same race opens a thread twice on a double click of "Raise a doubt".
Fix: `viewer/writes.py` holds one module-level `threading.Lock` around each write in `handle_post`, so the second request reads the state the first wrote and is stale.
Test without sockets: two threads call `handle_post` with the same body against one staged world whose store blocks the first `publish` until the second has entered; one publish, and the second answers `303` with `done=stale`.

### I3. A viewer commit during a conflicted revert concludes the revert

Handle: plan line 275 (`MERGE_HEAD`, `CHERRY_PICK_HEAD`, `rebase-merge`, `rebase-apply`), line 280 (the tests); design 69.
Verified in a scratch repository (git 2.56.0, `GIT_CONFIG_GLOBAL=/dev/null`): after `git revert` stopped on a conflict, `git commit --only --quiet -m viewer -- lodge/threads/q.md` exited 0, made the commit, and removed `REVERT_HEAD`, with the conflicted file still unmerged.
Failure: the author's revert in progress loses its state, and `git revert --continue` no longer knows what it was doing; the plan's list does not name `REVERT_HEAD`, and the `sequencer` folder of a multi-commit pick or revert is missing too.
Fix: add `REVERT_HEAD` and `sequencer` to the git paths that mean `IN_PROGRESS`, word the outcome "during a merge, rebase, cherry-pick, or revert" (plan line 242 and the `staged-in-progress` notice, line 367), and add `test_no_commit_during_a_revert` (a real conflicting revert) to `tests/gitstore/test_commit.py`.

### I4. Three test files the plan extends would pass 300 lines

Handle: `tests/core/test_feedback.py` (282 lines, 23 tests), `tests/core/test_fileformat.py` (279 lines, 18 tests), `tests/viewer/test_pages.py` (239 lines, 21 tests); plan lines 109, 111, 150, and 416; `tests/structure_tables.py:29` (`MAX_LINES = 300`, tests included, plan line 24).
At about 12 lines a test, Tasks 1 and 2 add six tests to `test_feedback.py` (about 354 lines), Task 1 adds five to `test_fileformat.py` (about 340), and Task 7 adds eight to `test_pages.py` (about 330).
Failure: `tests/test_structure.py` fails in the builder's gate, and the builder must move tests the plan placed.
Fix: put the new tests in new files: `tests/core/test_feedback_links.py` (Tasks 1 and 2), `tests/core/test_fileformat_links.py` (Task 1), and `tests/viewer/test_pages_links.py` (Task 7), and name them in each task's Files.

### I5. The existing `POST` test is told to expect 403, but the plan's `do_POST` answers 411 first

Handle: plan line 369 (`do_POST` reads `Content-Length`, missing is 411, before `handle_post`), line 376 ("the existing test that expected 405 on `POST` now expects 403 without an `Origin`"); `tests/viewer/test_server.py:113-115` and its `get` helper (lines 31-42), which sends no body and no `Content-Length`.
Failure: the coordinator's socket run of `test_only_reads_are_served` fails with 411, a test the builder cannot run (plan line 21).
Fix: either the test expects 411, or (better, so that no foreign page makes the server read a body) `do_POST` runs the `Host` and `Origin` checks of `handle_post` before reading the length, and the test keeps 403; the plan says which, and `test_post_without_length_411` sends an allowed `Host` and `Origin`.

### I6. Reading the message file through `commands._read` closes an import cycle

Handle: plan line 290 (`cli/threads.py` holds `run_thread`), line 302 ("read as drafts are (`commands._read`)"); `src/lodge/cli/commands.py:20-38` imports `lodge.cli.parser`; `tests/structure_imports.py:24-60` adds every intra-package edge to the cycle graph.
`commands.py` must import `run_thread` from `cli/threads.py`, and `parser.py` must import the thread dataclasses from it; if `cli/threads.py` imports `_read` from `commands.py`, the modules form the cycle `commands -> threads -> commands`, which `tests/test_structure.py` refuses.
Fix: `commands.py` reads the file and passes its text to `run_thread`, or `_read` moves to a new `cli/files.py` that both import; the plan says which.

### I7. The form field names are fixed by neither task, and no test joins the forms to the handler

Handle: plan line 365 ("then the routes of Call 12"), line 405 ("fields as Task 6 reads them"), line 407 (the doubt and question forms: "each a text area and a hidden `about` and `kind`"); the reply and close text fields have no name anywhere.
Task 6's builder picks the names in `handle_post`, Task 7's builder writes the forms, and each sees only its brief (plan line 19); Task 6's tests build bodies by hand, Task 7's tests read HTML, and the socket tests post no form.
Failure: a form whose text area is named `text` posts to a handler that reads `words` or `message`; every viewer write then answers 400, and no test fails.
Fix: Task 6 fixes every field: `token`, `words`, `id` (repeated), `area`, `about`, `kind`, `text` (doubt, question, reply, and close); Task 7 adds `test_rendered_forms_post_through_handle_post`, which reads each form's `action` and field names from the rendered page, fills them, and passes them to `handle_post` against a staged world (no socket), asserting a `303`.

### I8. `--allow-host` parsing has no test, and the test that pins the `view` callable is not in Task 6

Handle: plan line 370 (whitespace, `/`, or empty is a usage error), line 323 (Files), lines 373 to 376 (tests); `tests/e2e/test_view.py:55-69` calls `run(argv, unused, never, view, ...)` with `view(port: int)`.
Failure: the usage errors the design's host rule depends on (design 129) are untested, and `test_view_passes_the_port_to_the_viewer` breaks on the new `(port, allow_hosts)` callable; the builder's gate ignores `tests/e2e/test_view.py` (plan line 21), although this test needs no socket.
Fix: Task 6 lists `tests/e2e/test_view.py`, updates that test to `view(port, allow_hosts)`, adds `test_allow_host_is_repeatable_and_passed` and `test_allow_host_with_space_slash_or_empty_exits_2`, and the builder runs this one test with `-k` despite the file-level ignore.

### I9. Task 9 puts the agent's widening into an author decision's statement

Handle: plan line 453 ("a doubt or question about a record is raised and answered on that record (line 13)"); design 13: "what do I do with an entry I have doubts/a question about?"
Her words name an entry; threads on decisions are the agent's and the advisor's extension (design 78, "[advisor: not a thread]").
Failure: an author decision, which lodge shows at level 1 as hers with her quote beside it (LODGE-2, d-qsfjqa), states that doubts reach every record, which she did not say; must-not 1 of the design and LODGE-8 (d-9vxkjw) both keep agent claims out of what reads as hers.
Fix: the statement reads "a doubt or question about an entry is raised and answered on that entry"; the extension to decisions goes in the coordinator decision for Doubts and questions, with its reason.

### I10. Task 9's statement for line 18 reads against LODGE-6

Handle: plan line 453 ("confirming a record does not mark it as hers, and who wrote what stays visible (line 18)"); `uv run lodge show LODGE-6` (d-8nkamy, an author decision): "A decision the author confirmed counts as the author's for the review flag."
Her words are "marked as mine" in the sense of who wrote it; the plan's "does not mark it as hers" also reads as "does not count as hers", which LODGE-6 says it does, and Task 9 forbids narrowing an author decision (plan line 457).
Failure: two current author decisions that read as contradicting each other at level 1, which s-q4s548 (lodge must not show wrong information) rules out.
Fix: the statement reads "confirming a record does not show it as written by the author; who wrote what stays visible", and the coordinator decision for Confirming says in its reasoning that LODGE-6 still makes a confirmed decision count as hers for the review flag.

### I11. Task 9 misses current records the design contradicts, and its blanket "replaces and narrows nothing" leaves stale decisions current

Handle: plan lines 457 to 459.
Found by reading `uv run lodge spec` and the decision files:
- s-8f6scf ("Links go one way in the files: they are written on the decision") and its decision d-zerbz9 ("Links are written on the decision only"): `rests_on` is written on the entry.
- d-3epcjd ("has seven checks") and d-4032xv ("Reads and the viewer run all seven checks"): both current, while s-j70a0k and s-edgt71 become eight.
- s-aw5a1j (check 6: "A record added in this change"): the design extends check 6 to an entry edited in the change (design 109).
- s-ms14fq (check 5: "An existing decision ... fails"): check 5 now covers threads (design 80).
- s-wcv4en (level 1 lists "any review flag"): level 1 now carries "in doubt", "question open", "confirmed by the author", and the rests-on marks, none a review flag.
- s-7ah5n7 ("Out of scope for now are ... other kinds of project knowledge beyond decisions and specification entries ... conversation logs as provenance"), whose reason is her quote in the first design (`docs/superpowers/specs/2026-10-29-lodge-design.md:46`): "What and how that might be useful would have to be evaluated (first on the past and then in a pilot)."
Failure: after Task 9, `lodge search` returns current decisions saying seven checks and links only on decisions, and an entry still puts a third record kind out of scope; the brief's rule that nothing contradicts a current record without a decision that replaces, narrows, or retires it fails.
Fix: Task 9's Rests on decision edits s-8f6scf and s-aw5a1j and narrows d-zerbz9, d-3epcjd, and d-4032xv (coordinator decisions, so no author decision is touched); Doubts and questions edits s-ms14fq and s-wcv4en; s-7ah5n7 goes to the author as a question, since a thread being a kind of knowledge or not is hers to say (CLAUDE.md, "one that changes what the spec says goes to the author"), and Task 9 does not run until she answers or the plan records her ruling.
Line 457 reads "It narrows the coordinator decisions whose statements it makes false, never an author decision."

### I12. Task 9 leaves "changed since" marks on every entry resting on an entry it edits

Handle: plan line 432 (Task 8: "each check's entry rests on s-j70a0k"), line 458 (Task 9 edits s-j70a0k, s-0yzshh, s-dm37qr, and others), line 140 (the mark), line 464 (Task 9's verification).
Task 8 links the seven check entries to s-j70a0k; Task 9 then edits s-j70a0k, so all seven show "rests on s-j70a0k, changed since" at level 1, in `lodge spec`, and in the viewer, and the same holds for whatever rests on each other edited entry.
Failure: the first thing she sees in the viewer after the build is a field of warnings that the build itself caused, not a change she must weigh.
Fix: after each section's decision, Task 9 runs `uv run lodge spec | grep 'changed since'` and, for each entry that still holds, lists it with `edit`, text unchanged, in that same decision with one reasoning line (the design's rule, design 113), or edits it; the verification step adds "`uv run lodge spec | grep -c 'changed since'` prints 0, or the report names each remaining mark and why".

### I13. A thread closed without text records lodge's "Closed." as the author's message

Handle: plan line 273 (`close` appends "the given text or `Closed.`, by the closer"), line 301 and line 407 (the close form's optional text); design 81 ("An author message's text is her words, verbatim") against design 85 ("with the text 'Closed.' when none is given").
Failure: a close from the viewer with the field empty writes a message `by: author` whose text she did not type, the case design must-not 2 and LODGE-8 forbid, and a reader of the thread file cannot tell it from her words.
The design holds both rules, so this goes to the author.
Fix: the plan records a ruling and asks her; the cheapest form is that a close without text writes no text field and lodge shows "Closed." in reads, which needs check 1's "an empty message text" (plan line 212) to allow exactly the closing message.

### I14. The dependency view indents entries under an entry they do not rest on

Handle: plan line 101 (`depth` is `depth(under) + 1`), line 45 (Call 8, ties in the written order), line 409 (`depth-N` classes); design 118 and 120.
With an area written a, b, c, where c rests on a and b rests on nothing, Call 8 gives the order a, b, c with b at depth 0 and c at depth 1, so c is drawn indented directly beneath b.
Failure: the page reads as "c rests on b", a wrong dependency shown, against s-q4s548 and Goal 3; the design's tie rule (written order) and its indentation rule pull apart here, so this goes to the author.
Fix until she rules: each indented entry in the viewer carries one line "rests on s-a" naming its `under`, and `test_spec_opens_by_dependency` uses the a, b, c case with that line asserted; the alternative, placing an entry's dependants right after it, breaks "ties kept in the area's own order" and needs her.

## Minor

### M1. `Store.commit` breaks mypy on a test wrapper that Task 4 does not list

Handle: plan line 245 (`Store.commit`), line 231 (Files); `tests/gitstore/test_concurrent.py:30-55`, a store wrapper passed where `Store` is expected (`lodge_over(store: Store, ...)`, line 58).
Failure: mypy strict reports the wrapper as not a `Store`, and the builder edits a test the plan did not name.
Fix: list `tests/gitstore/test_concurrent.py` in Task 4's Files, its wrapper forwarding `commit` to `inner`.

### M2. Task 7 changes `render`'s signature under a Task 6 test

Handle: plan line 356 (`render(make_lodge, url)`), line 375 (`test_get_with_done_shows_notice` calls `render(world, urlsplit(...))`), line 403 (`render(make_lodge, url, token: str)`).
Failure: Task 7 breaks a Task 6 test it does not list.
Fix: Task 6 defines `render(make_lodge, url, token: str = "")`, or Task 7 lists `tests/viewer/test_writes.py`.

### M3. The viewer's `world()` has no staged store and no handle on it

Handle: plan line 375 ("`world()` and a staged `MemoryStore`"); `tests/viewer/world.py:33-37` builds a non-staged `MemoryStore` inside and returns only the `Lodge`.
Failure: with `world()` as it is, outcomes are `PUBLISHED`, so `test_confirm_redirects_with_done_code` gets `done=published`, and no test can read `store.publishes` or set `commit_result`.
Fix: Task 6 lists `tests/viewer/world.py` and gives it `staged_world() -> tuple[Callable[[], Lodge], MemoryStore]`, one store shared by every `Lodge` it makes.

### M4. `parse_qs` can still raise or silently alter her words

Handle: plan line 365 (`parse_qs(keep_blank_values=True, max_num_fields=200)`), line 67 (Review Focus 5).
`parse_qs` raises `ValueError` past `max_num_fields`, and decodes percent escapes with `errors="replace"` by default, so `%FF` inside a valid UTF-8 body becomes U+FFFD in her words without a refusal.
Fix: call it with `errors="strict"`, answer 400 on `ValueError` and `UnicodeDecodeError`, and add `test_too_many_fields_400` and `test_bad_percent_escape_400`.

### M5. A stale single confirmation redirects to an ID taken from the form

Handle: plan line 366 ("`/r/{id}?done=stale`"; "IDs and area names come from lodge, never from the form, once resolved"); `http.server.BaseHTTPRequestHandler.send_header` writes the value as given.
Failure: an `id` that does not resolve is stale by line 364 and goes into `Location` unresolved; a value holding a line break splits the header.
The token and `Origin` checks limit this to someone who can already write, so the cost is low.
Fix: refuse with 400 an `id` that is not a `d-` ID (`is_id`) before anything else, and quote every path part of `Location` with `urllib.parse.quote(..., safe="")`.

### M6. A negative length and a stalled body are not covered

Handle: plan line 369; `src/lodge/viewer/server.py:23` (`daemon_threads = False`), `tests/viewer/test_server.py:161-186` (closing waits for a running request).
`int("-1")` parses, and a client that sends `Content-Length: 100` and no body blocks its handler thread on the read, which `server_close` then waits for, so Ctrl-C does not stop `lodge view`.
Fix: a length that is not `[0-9]+` is 400, and `_Handler.timeout` is set (10 seconds, say), with `test_negative_length_400`.

### M7. A `--where` that a header cannot carry ends in a traceback

Handle: plan line 178 (`write_thread` raises `ValueError`), lines 273 to 274 (the app's rules map no `ValueError`), line 31 (no traceback reaches the user).
`yamlio.quoted` refuses a control character (`src/lodge/core/yamlio.py:77-82`), so `lodge reply q-x --by author --where $'a\x01' --when now FILE` raises from `write_thread`.
Fix: `app/threads.py` turns that `ValueError` into a `LodgeError` naming the field, with `test_unstorable_where_refused`.

### M8. A hand-written thread message by `Author` fails no check

Handle: plan line 212 (check 1 for threads), line 57 (Call 20 refuses such a role only in the app); `src/lodge/core/check_state.py:110-115` (check 3 for decisions).
Failure: a hand edit that adds a message `by: The Author` passes the gate, while the same `decided_by` fails check 3.
Fix: check 3 extends to thread messages with the same test and message, and `test_role_like_author_fails_check_3` joins `test_check_threads.py`.

### M9. The thread file example contradicts its own quoting rule

Handle: plan line 207 (`when: 2026-10-29T10:00:00+01:00`, unquoted) against line 211 ("`when` and `where` with `yamlio.quoted`", which always writes a JSON string).
Fix: the example shows `when: "2026-10-29T10:00:00+01:00"`, or line 211 says an agent's stamp is written plain.

### M10. User-facing text still calls the viewer read-only

Handle: `src/lodge/cli/parser.py:132` ("serve the read-only viewer on this machine"), `src/lodge/viewer/__init__.py:1` ("The read-only local web viewer"), `src/lodge/viewer/server.py:37` ("this viewer only reads"); plan line 478 greps `README.md` only.
Fix: Task 6 changes the `view` help to "serve the viewer on this machine: read, confirm, and raise doubts", and Task 10's check becomes `git grep -n 'read-only' -- README.md src/` naming nothing about the viewer.

### M11. The area ranks are an agent call with no record in lodge

Handle: plan line 47 (Call 10, the ranks follow the first design's section order), line 486 ("needs no decision").
lodge allows the add, but the reason for the order then lives only in this plan, which moves to `done/`.
Fix: Task 11's add carries one coordinator decision, `scope: process`, title "Area ranks follow the first design's sections", whose reasoning names `docs/superpowers/plans/2026-10-30-lodge-on-itself.md:73`; it changes no entry.

### M12. The six quotes' text and time come from a secondary source the builder cannot check

Handle: plan line 453 and Call 19 (line 56); design 3 (written on 2026-10-31 from a brainstorm) and design 10 (all six dated 2026-10-30, 09:41 to 09:47); d-dyrpc6's quote carries the exact minute, 09:41.
Lines 15 to 18 read as answers to brainstorm questions, which the design says ran on 2026-10-31; I could not verify either date, since the session record is not in the repository.
An author decision is immutable once added (check 5), and only she can replace it.
Fix: before Task 9's first add, the coordinator, not Codex, checks each quote's text and minute against the session transcript, gives each its own `when` where the transcript shows it, and notes the check in the ledger.

### M13. The area list leaves out a decision whose last change retired an entry of the area

Handle: plan line 362 ("list a current entry of the area with `create`, or are its `changed_by[0]`"); design 51 ("created or last changed an entry in the area").
Failure: an agent decision that retired an entry of the area is never offered for confirmation on that area's page.
Fix: drop "current" from line 362 for the entry, or record a ruling that retirements are confirmed one by one on their decision's page.

### M14. Two check 2 messages for `rests_on` differ from the existing wording

Handle: plan line 137 (`rests_on {t}, which is not a specification entry`); `src/lodge/core/check_state.py:84` (`{key} {target}, which does not exist`); plan line 109 (a `d-` ID in `rests_on` is already problem 1, through `read_ids(..., "s")`).
Only an `s-` ID that does not exist reaches check 2, so "which does not exist" is the true message.
Fix: line 137 reads `{e}: rests_on {t}, which does not exist`.

### M15. Nothing tests that a viewer write touches only a new decision or one thread file

Handle: design 131 ("the viewer never edits an existing decision, entry, or area file"); plan lines 364 and 365; design 90 (search and the timeline leave threads out), for which no test is named either.
Fix: Task 6's `test_writes.py` asserts, for each route, that every path in `store.publishes` is a thread path or a decision path absent from the store before; Task 4 adds `test_search_and_timeline_leave_threads_out`.

### M16. `ID_KIND` has no entry for `q`

Handle: `src/lodge/core/fields.py:15` (`ID_KIND = {"d": ..., "s": ...}`), read by `read_id` (line 99); plan line 160 (Task 3 modifies `fields.py` for `read_stamp` only).
Failure: `read_id(value, "id", "q")` in `parse_thread` raises `KeyError` on a malformed thread ID, which `read_with` does not catch, so `load` fails on one bad file.
Fix: Task 3 adds `"q": "thread"` to `ID_KIND` and a test with a thread file whose `id` is `q-BAD`.

## Coverage of the design

Every requirement of the design has a task that builds it, with the gaps named above: the revert case of design 69 (I3), the writes limit of design 131 (M15), threads left out of search and the timeline (design 90, M15), and the host rule's parsing (design 129, I8).
Produces against Consumes, task by task, agree on names and types apart from M2 and I7.
The new modules the plan places (`core/order.py`, `core/check_cycles.py`, `core/threads.py`, `core/doubts.py`, `core/confirmation.py`, `app/threads.py`, `app/confirm.py`, `gitstore/commit.py`, `viewer/writes.py`, `viewer/forms.py`, `viewer/spec.py`, `cli/threads.py`, `cli/thread_output.py`) import only what `tests/structure_tables.py` allows, apart from the cycle risk of I6; the modules near the limit stay under 300 lines with the stated budgets (`core/views.py` 220 plus 42, `core/derive.py` 227 plus 21).
The records tasks write agent text as the author's only in I9 and I10, and their quotes' exactness rests on M12.

## Files read

`CLAUDE.md`; the design; `advisor-ruling.md`; `builder-check.md` (first 60 lines); the plan; `uv run lodge spec`; `lodge show` of d-dyrpc6, d-2hcgav, d-7w5aq0, LODGE-6, LODGE-8, LODGE-2, d-3epcjd, d-n30kqr, d-zerbz9, d-x42f0x, d-4032xv, d-4dp4gm, s-7ah5n7, and the eleven entries the design lists; `lodge/decisions/` d-cg3nn3, d-z727gh, d-vme42w; `docs/superpowers/specs/2026-10-29-lodge-design.md` (grep only); `docs/superpowers/plans/2026-10-30-lodge-on-itself.md:68-78`.
Code: `tests/structure_rules.py`, `tests/structure_tables.py`, `tests/structure_calls.py`, `tests/structure_imports.py`; `src/lodge/app/{ports,results,errors,__init__,writes,lodge,state}.py`, `src/lodge/app/reads.py:1-60`; `src/lodge/core/{model,derive,views,check_change,check_state,headers,fields,document,snapshot,ids,check_immutable,render,yamlio}.py`, `src/lodge/core/check_entries.py:1-56`, `src/lodge/core/fileformat.py`, `src/lodge/core/feedback.py:1-60`, `src/lodge/core/apply.py:212-246` and its messages; `src/lodge/viewer/{server,__init__}.py`, `src/lodge/viewer/html.py:1-80`; `src/lodge/gitstore/{checkout,__init__,plumbing,trees,git,lock}.py`, `src/lodge/gitstore/setup.py:1-60`; `src/lodge/main.py`; `src/lodge/cli/commands.py`, `src/lodge/cli/parser.py:72-180`; `src/lodge/hook/post_tool_use.py:1-40`; `tests/app/fakes.py`, `tests/viewer/{world,conftest,test_server}.py`, `tests/app/conftest.py`, `tests/gitstore/test_concurrent.py:35-75`, `tests/e2e/test_view.py` (grep); `vulture_allow.py` (head), `scripts/check.sh`.
Not read: `src/lodge/core/{search,drafts,settings,words,check_areas}.py`, `src/lodge/app/reads.py:61-127`, `src/lodge/viewer/pages.py`, `src/lodge/viewer/style.css`, `src/lodge/cli/output.py`, `src/lodge/cli/guide.md`, `src/lodge/gitstore/{branch,published,accepted,settings,errors}.py`, the rest of `tests/` beyond the line counts, `advisor-runs.md`, the progress ledger, and README.md.
