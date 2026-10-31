# Final review: lodge-viewer (tip 08e6be2), standing in for lodge-on-itself (47dcfa7 to f28eb5c)

Reviewer: the `reviewer` agent, by ruling d-mkstz5.
Scratch work ran in a detached worktree in the session scratchpad, removed at the end.
This file is written as the review goes; the verdict is at the end.

## Gate

`sh scripts/check.sh` at 08e6be2 in a clean scratch worktree: ruff format and ruff clean, mypy strict no issues in 194 files, vulture clean, 1392 tests passed (socket tests included), `lodge check --gate` ok.
The gate prints 25 `note:` lines, among them `area X: order changed` for purpose, model, reading, storage, and writing; item 5 below takes them.

## 1. Correctness across tasks: the write path end to end

Probe: a scratch repository with a bare remote, seeded through `lodge init` and `lodge add` (one coordinator decision creating A and B in `storage` and C in `reading`, B resting on A, C on B), `main` pushed, then a branch `work`; `lodge.main._make_lodge` as the viewer builds it, `writes.handle_post` for every write, `server.render` for every page, `git` and `lodge` read back after each step.
An unrelated file was staged first, to see that the viewer's commits leave it alone.

| Step | Seen |
| --- | --- |
| Decision page | the confirm form with "Your words" and "Confirm" |
| `POST /confirm` with words holding a quote, `#`, `<script>`, CRLF, and a line `## Reasoning` | 303 to `/r/d-…?done=committed`; HEAD "Author confirmation from the viewer: d-czptet", by the checkout's own identity, holding the one new decision file; the unrelated file still staged |
| The confirmation record | title "Confirms d-yrqbdn", statement "The author confirms d-yrqbdn.", reasoning equal to the quote's text, CR dropped and nothing else changed, `where` "lodge viewer", `when` the minute |
| The confirmed decision at level 1 | still `coordinator`, with "confirmed by the author (d-czptet)" |
| The same `POST` again (a double click) | 303 with `done=stale`, nothing written |
| Area page after that | no hidden `id`, so no form: nothing left to confirm |
| `POST /threads` doubt on A | 303 to `/r/A?done=committed#q-…`; commit "Thread q-…: doubt raised by author" |
| Marks | B and C both show "rests on A, in doubt" at level 1 (C two links down), and B's page shows it; `lodge waiting` lists the thread under "waiting for an agent" |
| Reply, then close with an empty field | two commits, "author reply" and "closed by author"; `lodge thread` ends "closed by author · … · lodge viewer" with no text, and no "Closed." anywhere |
| Reply after close | 400 "q-… is closed", nothing written |
| After close | the marks on B and C are gone; `lodge check` ok; `git status` shows only the unrelated staged file |

The pieces fit: the forms post what the routes read, the app writes through the ordinary add and check path, and `gitstore` commits only the named paths.

## 2. Security of viewer writes, and the must-nots

Raw-socket probes against `make_server` on port 0, in the same scratch repository, HEAD compared before and after:

| Request | Answer |
| --- | --- |
| two `Host`, two `Origin`, two `Content-Type`, two `Content-Length` | 400 each |
| `Host: 127.0.0.1.:PORT`; foreign `Host` on GET | 403 |
| `Origin: null`; `http://HOST@evil.example`; `http://HOST/` | 403 each |
| `Origin` in upper case | passes the gate (compared in lower case, as the plan says) |
| `Transfer-Encoding: chunked` without length | 411 |
| `Content-Length` `+5`, `-1` | 400; `99999999999999999999` 413 |
| `Content-Length: 0` | 403 (no token) |
| `text/plain`, `multipart/form-data` | 415 |
| length 40, five bytes sent, then half-close | 400, nothing written |
| no token in the body; token only in the query string | 403 |
| `/CONFIRM`, `/confirm/`, `//threads/q-…/reply`, `/threads/q-…/reply/`, a `..` path | 404 |
| `/threads/Q-AAAAAA/reply` | 400 |
| `OPTIONS` | 405 |
| a body promised and never sent | the connection closes after 10 seconds with no answer |

HEAD was unchanged after every probe.
Mutations run in the scratch worktree, each against `tests/viewer`, `tests/app`, and `tests/e2e/test_view.py`, each caught by at least one failing test: dropping the body size check, the thread-ID check, the short-body check, `Origin` from the repeated-header list, the write lock, the strip in `clean_text`, and admitting an `ftp` origin.
The page policy (`default-src 'none'`, `form-action 'self'`, `frame-ancestors 'none'`), `Referrer-Policy: no-referrer`, and `Cache-Control: no-store` keep the token from leaking through a script, a referrer, or a cache.

Must-not 1: the confirmed decision keeps `decided_by`, and the confirmation's title and statement are lodge's fixed text (seen above).
Must-not 2: every author record and message the viewer writes takes its text from the form, and a close with an empty field writes an empty text; no code path supplies author text (`src/lodge/viewer/writes.py:137`, `:153`, `:170`; `src/lodge/app/threads.py:22-40`).
Must-not 3: a doubt writes only its thread file (`test_viewer_writes_only_new_decisions_and_thread_files`, and the probe's commits each hold one file).

## Fix rounds rechecked

Each Important a per-task review raised, against the fix its report's "Fix round 1" names, by the test it added (present in `tests/`, and green in the gate) and, for the write gate, by my own mutations above.

| Task | Finding | Closed by | State |
| --- | --- | --- | --- |
| 1 | I1 depth first untested; I2 retired filter unpinned | `test_dependants_follow_depth_first`, `test_diamond_uses_last_placed_target_at_depth_two`, strengthened retired test (`tests/core/test_order.py`) | closed |
| 2 | I1 "supported by" | level 3 reads "supports" (`tests/core/test_views_links.py`) | closed |
| 3 | I1 unpinned guards; I2 thread problems invisible; I3 CR rule twice | guard tests with recorded mutants; `test_thread_problems_are_visible_in_reads`; one `core.clean_text`, used by `app/threads.py:25` and `app/confirm.py:58` | closed |
| 4 | I1 orphan thread `KeyError` | ruling d-wez56g, `ThreadShown.about` optional, `test_thread_about_a_missing_record_reads`, `test_orphaned_thread_post_does_not_fail` | closed |
| 5 | I1 lone CR; I2 guide; I3 author read-back | `read_file(exact=True)`, `test_author_words_are_recorded_exactly`, `test_guide_restores_introduction_and_heading_spacing` | closed |
| 6a | I1 untested rules; I2 `## Reasoning`; I3 lock not documented | mutation table in the report; `confirm`'s docstring (`src/lodge/app/confirm.py:52-57`) | closed |
| 6b | I1 short body; I2 refusals untested | `test_short_body_refused_without_writing`, `test_bad_thread_id_refused_without_writing`; my mutations agree | closed |
| 7 | I1 exponential tree; I2 vulture | `test_rests_on_tree_expands_a_shared_dependency_once`, `test_shared_dependency_page_stays_small`; vulture clean | closed |
| 8 | I1 tie read as "changed since"; I2 missed links | `test_same_second_change_does_not_mark_changed_since`; ten links; one link deferred (item 3 below) | closed but one link outstanding |
| 9a | I1 d-s69cq4 narrows d-mzkt6e | see item 3 | checked there |

The 9b and 9c review (`task-9bc-review.md`, committed after this branch's tip as fb7f80c) is not rechecked here; its three Importants go to the same fix wave, and item 3 confirms the two I could reproduce.

## 3. Records

Read through lodge only: `lodge spec` whole (761 lines), every current decision's title and statement, the 35 decisions this branch adds with `--reasoning`, the author decisions with `--provenance`, and `lodge check`.

- `lodge check` prints ok; the gate's `--gate` run is ok.
- 171 decisions, 126 entries, no threads; 37 author decisions, and in every one the reasoning equals the quote's text (compared by script through `read_state`); no role other than `author` contains "author".
- The six author decisions of Task 9a hold her words alone in quote and reasoning; their statements are agent text under her label, as LODGE-8 (d-9vxkjw) allows, and Task 9a's review m4 already offers her the choice to soften two of them.
- I could not check the minutes of her quotes (09:34 to 09:47 on 2026-10-30) against the session, which I do not have; the ledger says the coordinator read them off the session's stamps.
- The narrowings the plan asks for are in place: d-6zyet3 narrows d-zerbz9, d-3epcjd, and d-4032xv; d-3d4g9j narrows d-cg3nn3; d-mzkt6e is no longer narrowed.
- The two contradictions the 9b and 9c review names reproduce: d-vme42w is current and unnarrowed while s-582qav now says the viewer writes, and the area intros print "The two record kinds" (model) and "the seven checks" (writing) above entries saying three and eight.

The remaining record findings are listed under Findings.
The `area X: order changed` notes of the gate are right: the order lines of purpose, model, reading, storage, and writing differ between `f28eb5c` and the tip (checked with `lodge draft area:NAME` in a worktree of each), because Tasks 9a to 9c added entries to them; Task 11's builder read them as Task 11's own, and they clear when the branch merges.

## 4. Practice and design

- Structure: the structure test passes; the largest modules are `core/apply.py` (277 lines), `gitstore/checkout.py` (267), `core/derive.py` (243), and `core/views.py` (240), all under 300; `subprocess` stays in `gitstore`, and `secrets` in `main.py`.
- Dead code: vulture is clean; the allow-list gains five `http.server` names and `HTMLParser.handle_starttag`, each read by the standard library.
- Guide: 60 lines, and every command and rule it states matches the code (`src/lodge/cli/guide.md`; the check 4 sentence matches `src/lodge/core/check_entries.py:43-66`).
- README: matches the code except the `--allow-host` example (Findings).
- Prose: no em-dash or en-dash in `README.md`, `CLAUDE.md`, `src/`, the design, the plan, or the ledger; one sentence per line holds in the README and guide.

## 5. Parked items

| Item | Recommendation | Why |
| --- | --- | --- |
| Task 6b m5: `handle_post` is one 100-line function with a nested helper (`src/lodge/viewer/writes.py:87-190`) | Fix now, in the fix wave | It is the security gate; split into the gate (token and form parsing, returning the fields or a `Reply`) and one function per route, so each route's refusals read alone. My mutations of the gate (item 2) are each caught, so the split is safe to make under the existing tests. |
| lodge-on-itself Task 5 M1: statements opening "M3", "I1", "N1" with no review file (d-04jnwq, d-0cj3bn, d-kanyrm, d-eae44h, d-74sttc) | Leave | Published on `main`, so the fix is five replacing decisions; they are process rulings of a finished plan, read only for their own subject, and the ledger lines beside them name the review files. |
| M2: two fragment reasonings (d-x4spd2, d-74sttc) | Leave | As M1; the titles carry the subject. |
| M3: times without dates in d-wfxez9 | Leave | The record's own date and the ledger give the day. |
| M4: rulings dated the day they were added | Leave | As the plan specified; replacing twelve records to re-date them costs more than the timeline order is worth. |
| Task 11's order-change notes | Nothing to fix | They are right against the published state and clear at merge (item 3). |

The lodge-on-itself ledger also carries two findings for "the next code plan" that this plan did not take: the viewer-exemption minors R1 to R3 and the aliased `datetime` minor (d-t22n7w, `tests/structure_calls.py:161-165`), and a finished plan's process rulings still showing `current`.
Both stay open; neither blocks this merge.

## Findings

### Blocking

None.

### Important

**I1. s-2bzwzv states the wrong indent rule for the dependency view.**
s-2bzwzv (created by d-7n4jyj, Task 9c) says "Each entry is indented under the first entry it rests on in the area".
The code indents an entry under the last of its same-area targets to be placed (`src/lodge/core/order.py:38-65`), as the advisor's ruling d-a3h9f3 and the plan's Call 8 require, and `tests/core/test_order.py:44-48` pins it: C resting on A and B sits under B, with A on an "also rests on" line.
Scenario: she opens "By dependency", sees C under B, and either judges the view broken or confirms the area `reading` with a statement that contradicts what the page in front of her shows (s-q4s548: lodge must not show wrong information).
Fix: a coordinator decision that edits s-2bzwzv's third sentence to "Each entry is indented under the last of its same-area dependencies to be placed, so it always sits under an entry it rests on; its other same-area dependencies appear on an "also rests on" line, and cross-area ones as "rests on s-xxxxxx (area)"." with d-a3h9f3 in its reasoning; the decision that fixes `task-9bc-review.md` I1 and I2 can carry it.

### Confirmed from `task-9bc-review.md` (not counted again here)

- I1: d-vme42w is current and false (`lodge show d-vme42w` has no "narrowed by", while s-582qav and s-dm37qr say the viewer writes).
- I2: the area intros print "The two record kinds" (model) and "the seven checks" (writing), against s-a67fqm and s-j70a0k.

### Minor

**m1. The README's `--allow-host` example never matches a browser behind a proxy on port 443.**
`README.md:153` gives `lodge view --allow-host proxy:443`.
A browser omits the default port in both `Host` and `Origin`, so a proxy at `https://proxy/` sends `Host: proxy` (or the upstream's `127.0.0.1:PORT`) and `Origin: https://proxy`; neither equals `proxy:443` (`src/lodge/viewer/writes.py:58-66`), and every page and write answers 403.
Not run against a real proxy; the claim rests on the origin serialisation rule and the exact comparison in the code.
Fix: say the value is the `Host` the browser sends, port left out when it is the scheme's default, with `--allow-host lodge.example` for a proxy on 443 and `--allow-host lodge.example:8443` for one on another port.

**m2. Two of the six in-progress markers have no test.**
`src/lodge/gitstore/commit.py:24-31` checks `rebase-apply` and `sequencer`, and no test creates either; deleting both lines leaves `tests/gitstore/test_commit.py` at 15 passed (run in the scratch worktree).
Scenario: a later edit drops `sequencer`, and a viewer write commits in the middle of a stopped multi-commit revert, which Call 25 exists to prevent.
Fix: parametrise `test_no_commit_during_a_rebase` (`tests/gitstore/test_commit.py:94-97`) over `rebase-merge`, `rebase-apply`, and `sequencer`.

**m3. s-mc9n8a leaves out the revert.**
It lists "a merge, rebase, or cherry-pick"; the code (`src/lodge/gitstore/commit.py:24-31`), the notice (`src/lodge/viewer/writes.py:21-23`), and `README.md:157` add the revert, and the code a stopped sequence (Call 25).
Fix: edit s-mc9n8a to "during a merge, rebase, cherry-pick, or revert, or while a sequence of picks or reverts is stopped", naming Call 25 of the plan in the reasoning.

**m4. s-r7c3wn gives the wrong mark for the dependants of a doubted decision's entries.**
It says a doubt on a decision marks the entries it created or last changed "and their dependants" as "changed by d-xxxxxx, in doubt"; the code marks those dependants "rests on s-y, in doubt" (`src/lodge/core/doubts.py:44-59`), as the plan's Task 3 says.
Fix: "A doubt on a decision marks the entries it created or last changed as "changed by d-xxxxxx, in doubt", and the entries resting on them, directly or further down, as "rests on s-xxxxxx, in doubt"."

**m5. The link left over from Task 8 can be added now.**
Task 8 deferred s-j5ttw1 resting on s-aq3a5k until Task 9a's entries were published; by d-na1eg7, d-s69cq4's edit of s-j5ttw1 in this change already lets a `link` pass, and a dry run of that link in the scratch worktree printed no check line.
Fix: add the link decision in the fix wave, which closes Task 8's I2 on this branch.

**m6. Five entries carry a narrowing mark although what they say still holds.**
s-07ar34 and s-rger6n ("its decision narrowed by d-3d4g9j, d-dyrpc6"), s-gg9chm (d-dyrpc6), s-fdzcr2 and s-zv83s7 (d-6zyet3): each decision was narrowed for a viewer or check claim that these entries do not make (no server, soft limits, the viewer and the gate agree, IDs, the same change).
The marks are true of the decisions, so this is not wrong information, but she meets them on the pages she is about to confirm.
Fix: one coordinator decision listing the five with `edit`, text unchanged, one reason line each (s-sjqg5k), or a ledger line telling her why they are there.

**m7. d-3d4g9j still calls the implementation "approved", and can still be corrected in place.**
Task 9a's review m2 left it because "nothing can be edited", but d-3d4g9j is unpublished until this branch merges; a dry run of `lodge draft d-3d4g9j` with "approved" changed to "built" passes with only the immutability note, and d-38xscb ruled that unpublished records are fixed through `lodge draft` and `lodge add`.
Fix: change the word before the merge; after it, only a narrowing decision can.

**m8. The list join with the Oxford comma is written twice.**
`src/lodge/core/confirmation.py:47-52` repeats `src/lodge/core/feedback.py:151-154` (`_listed`).
Fix: one helper in `core`, used by both.

**m9. A refused write is headed "Cannot show this page".**
`src/lodge/viewer/server.py:73-77` renders every non-303 write answer through `pages.error_page` (`src/lodge/viewer/pages.py:118-122`), so empty words or a failed check reads as a page that could not be shown.
Fix: give `error_page` a heading parameter and pass "Nothing was written" for write refusals.

**m10. The area form's note speaks of one decision.**
`src/lodge/viewer/forms.py:6-9` says "The decision stays the agent's" on an area page whose form confirms up to nine decisions (writing has nine today).
Fix: the plural, "The decisions stay the agents'", when more than one ID is listed.

**m11. `CLAUDE.md` names only the first design as frozen.**
`CLAUDE.md:8` and `CLAUDE.md:33` name the first design and the done ledger; `.lodge.toml` freezes the viewer design too, and that document's last line says so.
Fix: name both designs in both lines.

## Before and after the merge

- The plan's own close-out stays: once merged, the same branch moves the plan, its ledger, and its folder to `docs/superpowers/plans/done/` (`CLAUDE.md`).
- Her confirmation, Task 3 of the earlier plan, should run with the viewer on a work branch: on `main` every write is staged and not committed (s-mc9n8a, `src/lodge/gitstore/commit.py:22-23`), so a session in another worktree would not see it.

## Verdict

0 Blocking, 1 Important, 11 Minor of my own; two Importants of `task-9bc-review.md` reproduced and its third not rechecked.
The code is ready: the gate is green with the socket tests, the write path works end to end against real git, and the write gate refused every malformed or foreign request I sent.
Merge into `main` after one fix wave that fixes I1 and the two reproduced 9b and 9c Importants in the records, decides 9b and 9c's I3, and takes the cheap Minors (m2 to m5, m7, m10, m11); a recheck of that wave's records and of m2's test is enough, and the merge itself waits for the author's go.

## Files read

Read: `CLAUDE.md`; the viewer design; the plan whole; its ledger; the per-task reviews of Tasks 1 to 9a and 9b with 9c; the "Fix round 1" sections of the reports of Tasks 1 to 7 and 9a; the lodge-on-itself ledger and its Task 5 review's Minors; `README.md`; `lodge guide`; `lodge spec` whole; every current decision's statement; this branch's 35 decisions with reasoning; `src/lodge/viewer/{writes,server,forms,spec}.py`, the diff of `src/lodge/viewer/pages.py`; `src/lodge/app/{threads,confirm}.py`; `src/lodge/core/{threads,confirmation,doubts,check_cycles}.py`, the diff of `src/lodge/core/check_entries.py`, the head of `src/lodge/core/order.py` and `src/lodge/core/yamlio.py`; `src/lodge/gitstore/commit.py` and the diffs of `checkout.py` and `branch.py`; `src/lodge/main.py`; `vulture_allow.py`'s diff; `.lodge.toml`; the test helpers `tests/viewer/world.py`, `tests/app/fakes.py`, `tests/e2e/conftest.py`, `tests/e2e/support.py`, `tests/gitstore/repos.py`, and parts of `tests/e2e/test_threads.py`, `tests/core/test_order.py`, `tests/gitstore/test_commit.py`.

Not read: the reports' sections before "Fix round 1", the briefs, the Codex final texts, the advisor files, `plan-review-*.md`, `plan-fix-1.md`, `plan-recheck-1.md`; `src/lodge/cli/` apart from the guide; `src/lodge/core/{views,derive,render,check_state,check_immutable,check_change,fields,fileformat}.py` and their diffs; the hook; most new test files beyond the names of their tests; record files by hand (none).
