# Task 5 report

Implemented on `lodge-on-itself`, without committing or pushing.

## Changes by file

- `.claude/settings.json`: added the README PostToolUse hook with matcher `Edit|Write|MultiEdit` and command `uv run --frozen --quiet lodge hook post-tool-use`.
- `.lodge.toml`: added exactly the design document and the completed build ledger to `[hook] frozen`.
- `docs/superpowers/specs/2026-10-29-lodge-design.md`: added the specification and decisions pointer at the top before adding the frozen configuration.
- `CLAUDE.md`: made `lodge spec` the authority, directed decision reads through lodge, identified author decisions with `decided_by: author`, explained that the entries await her confirmation, and replaced ledger-only rulings with `lodge add` and an ID in the ledger.
  Joined wrapped prose to follow the Markdown sentence rule.
- `.claude/agents/builder.md`: changed the authority and added lodge reading and authorship instructions.
- `.claude/agents/planner.md`: changed the authority and replaced ledger-only rulings with process decisions and ledger IDs.
- `.claude/agents/reviewer.md`: changed the authority and added lodge reading and authorship instructions.
- `.claude/agents/rechecker.md`: added the lodge authority, reading, and authorship instructions.
- `.claude/agents/integrator.md`: changed the authority and replaced ledger-only rulings with process decisions and ledger IDs.
- `docs/superpowers/plans/2026-10-30-lodge-on-itself-progress.md`: appended the live decision ID to each of its 12 ruling lines.
- `lodge/decisions/`: created 12 live coordinator decisions through `lodge add`, with scope `process` and `work_item: docs/superpowers/plans/2026-10-30-lodge-on-itself.md`.
  The statements hold the rulings, and the reasoning holds the reasons and costs if wrong.
  Quoted author words remain attributed inside coordinator reasoning.
- `docs/superpowers/plans/2026-10-30-lodge-on-itself/task-5-report.md`: this report.

## Rulings and IDs

Ruling: the plan is written by the coordinator and reviewed once by one reviewer covering both angles (correctness against the spec, then practice and design); why: the plan changes no code, every record it adds passes lodge's own gate, and the weekly budget has about 2% left before the author's stop; cost if wrong: a plan defect surfaces in a task review instead, one fix round later. (d-026tsm)
Ruling: M3, no LODGE-3 replacement; why: LODGE-4 (d-y8p15p) already narrows LODGE-3, and `lodge show LODGE-3` prints `narrowed by d-y8p15p`, which is what holds; cost if wrong: LODGE-3's "private" reads as narrowed, not replaced. (d-04jnwq)
Ruling: M9, her decisions at done ledger lines 4, 217, and 220 are imported as author decisions; why: Rollout 2 puts lodge's own decisions into lodge, and a coordinator ruling that the tag waits for her go is incomplete without her go; cost if wrong: three more records. (d-0cj3bn)
Ruling: the coordinator makes fix round 1 itself, and Task 1 starts before a recheck; why: the fixes are plan text taken from the review's own fix lines, and Task 1 does not depend on SPEC-1; cost if wrong: a plan defect surfaces in Task 1's review. (d-1xbm73)
Ruling: the fix round edits the unpublished Task 1 and 2 records through `lodge draft` and `lodge add` (with `--import` for the four Task 1 decisions that become imports dated from done ledger lines 210 to 215), never by resetting the branch; why: the published state is 47dcfa7, so check 5 does not yet hold these records, and a reset would force-push the work branch; cost if wrong: if lodge refuses changing a record's origin, those four stay live and get a replacing import, one more record each. (d-38xscb)
Ruling: one fix round takes I1 to I9 and M1 to M11 on the Task 2 builder, resumed; why: it knows the 82 entries, and weekly usage is at 94% against the author's stop at 95%; cost if wrong: a fresh builder would have re-read the spec. (d-4e25kk)
Ruling: the coordinator rechecked fix round 2 itself; why: N1 was the only Important, and a script listing every author record the fix cites with its quote showed each quote holding the words cited (d-14vk9b, d-7v4crf, d-pf8xm9, d-rkcb17, d-c6n1ng, d-9k0dfe for "very important" only, d-n30kqr for the size only); cost if wrong: a Minor left in decision wording, still open to the final review. (d-74sttc)
Ruling: I2, a ruling is dated by the first commit whose ledger line holds it with the same substance; a later edit that only renames a word (line 187, "handoff" to "brainstorm" in the redaction commit) does not re-date it; why: the date says when the ruling was made, and the redaction made no ruling; cost if wrong: line 187 sorts before her answer to D13, which it preceded in fact. (d-eae44h)
Ruling: I1, d-dhz8an narrows d-rvb42r instead of replacing it; why: the routing it records (D1 and D13 go to the author) was carried out and only its stated reason fails, after LODGE-8 (d-9vxkjw); cost if wrong: a reader of d-rvb42r follows "narrowed by" to the correct reason, not a replacement. (d-kanyrm)
Ruling: the coordinator rechecked Task 4's fix round 1 itself; why: each of the six Important findings has one observable result, and `lodge show` gave each (d-rvb42r narrowed by d-dhz8an and dated 19:32:58, d-z727gh dated 22:43:31, d-226x4j replaced by d-t22n7w, d-g2p3ng, d-xd09bw, and d-fx4xv3 narrowed), with `lodge check` ok; cost if wrong: a wording Minor in the new decisions, still open to the final review. (d-wfxez9)
Ruling: Task 3 waits until the viewer can confirm, and Task 5 runs now, making lodge the authority with the entries unprotected until she confirms; why: she wants to confirm through the viewer (d-dyrpc6) and asked on 2026-10-31 at 00:47 for the work to go on overnight, "Can you just go through this"; cost if wrong: an agent edit to an entry before her confirmation goes unflagged, though each entry's history still names the decision behind it. (d-x1aacr)
Ruling: Codex builds the tasks from here on, Claude agents review, and the coordinator commits and pushes; why: her words on 2026-10-31 at 00:48, "Use codex for implementing where applicable"; cost if wrong: a Codex run that misreads a brief costs one fix round, caught by the review. (d-x4spd2)

## Draft feedback

Every add attempt had a preceding dry run, with no check failures.
The related-decision questions were answered as neither replacement nor narrowing: these rulings govern this plan's particular review, import, fixing, dating, sequencing, and dispatch choices, rather than rewriting the related product or earlier process decisions.
In particular, the I1 ruling records the relationship already made by d-dhz8an; it does not itself narrow d-rvb42r again.
The Task 3 deferral governs this plan, rather than changing the author's viewer decisions.
Figures 2%, 82, 94%, and 95% carry handles to the source ledger rulings.
The remaining numerical feedback concerns task, line, check, and finding labels, a commit identifier, or quoted times, rather than figures needing numerical evidence.
Drafts and captured verification output are under git-ignored `.drafts/`.

## Hook verification

Each probe piped synthetic PostToolUse JSON with tool name `Edit`, an absolute file path, and this worktree as `cwd` into `uv run --frozen --quiet lodge hook post-tool-use`.
No actual record edit was made.
All four commands exited 0 with empty stderr.

`lodge/decisions/d-026tsm-review-the-plan-once-with-one.md` stdout, verbatim:

```json
{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "lodge/decisions/d-026tsm-review-the-plan-once-with-one.md is a lodge record file, and lodge owns it: do not edit it by hand. Run `lodge draft REF` (or `lodge draft area:NAME`) to get it as a draft outside `lodge/`, edit the draft, check it with `lodge add --dry-run FILE`, then publish it with `lodge add FILE`. Reverse your own edit now: put back exactly the text you replaced, with the same tool. Do not run `git checkout`, `git restore`, `git stash`, or `git clean` on this file, since they also discard changes that are not yours. If you cannot restore it exactly, tell the author."}}
```

`docs/superpowers/specs/2026-10-29-lodge-design.md` stdout, verbatim:

```json
{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "docs/superpowers/specs/2026-10-29-lodge-design.md is frozen: lodge holds its content now, so do not edit it. Record the change as a new decision instead: write a draft (`lodge guide` shows the draft format), check it with `lodge add --dry-run FILE`, then publish it with `lodge add FILE`. If the author asked for this edit, tell her the file is frozen and ask before reversing it. Otherwise reverse your own edit now: put back exactly the text you replaced, with the same tool. Do not run `git checkout`, `git restore`, `git stash`, or `git clean` on this file, since they also discard changes that are not yours. If you cannot restore it exactly, tell the author."}}
```

`docs/superpowers/plans/done/2026-10-29-lodge/task-5-brief.md` stdout, verbatim:

Empty output (zero bytes).

`src/lodge/main.py` stdout, verbatim:

Empty output (zero bytes).

The worktree without `.venv` case was skipped as the brief instructs.

## Instruction grep

Command: `git grep -n '2026-10-29-lodge-design.md\|Ruling:' -- CLAUDE.md .claude`.

```text
CLAUDE.md:7:The design document (`docs/superpowers/specs/2026-10-29-lodge-design.md`) is frozen history.
```

The sole remaining hit explicitly identifies the design document as frozen history, not authority.
No ledger-only `Ruling:` instructions remain.

## Gate

```text
FAILED tests/viewer/test_server.py::test_search_filters_arrive_from_the_query
FAILED tests/viewer/test_server.py::test_a_fresh_lodge_for_each_request - Per...
FAILED tests/viewer/test_server.py::test_lodge_error_is_a_page_with_its_message
FAILED tests/viewer/test_server.py::test_other_failures_are_a_plain_500 - Per...
FAILED tests/viewer/test_server.py::test_unreadable_file_banner_reaches_the_browser
FAILED tests/viewer/test_server.py::test_only_reads_are_served - PermissionEr...
FAILED tests/viewer/test_server.py::test_response_headers_lock_the_page_down
FAILED tests/viewer/test_server.py::test_bound_to_loopback_only - PermissionE...
FAILED tests/viewer/test_server.py::test_serve_reports_a_port_in_use_as_one_sentence
FAILED tests/viewer/test_server.py::test_serve_announces_the_address_and_stops_on_interrupt
FAILED tests/viewer/test_server.py::test_closing_the_server_waits_for_a_request_that_is_running
14 failed, 1056 passed, 1 skipped in 39.81s
```

The full script exited 1: 14 socket-dependent viewer tests failed because the sandbox denies socket creation (`PermissionError: [Errno 1] Operation not permitted`).
The run passed 1,056 tests and skipped one; formatting, lint, and strict typing passed before pytest.
The script therefore did not reach its final lodge gate, which was run separately:

```text
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
note: uncommitted record changes in lodge/; commit them before you push
```

## Concerns and limits

The normal Git metadata directory is read-only in this environment, so the first real add failed while acquiring the index lock and rolled back its record writes.
A fresh dry run and successful add used a temporary Git index and object directory under `.drafts/`, with the repository's objects available as alternates.
The records exist in the working tree, but the coordinator must stage them in the normal index before committing.
No repository records were edited by hand.
No commits or pushes were made.
Author confirmation remains deferred as instructed, so the entries are still unprotected by her confirmation.
No additional uncertainty about the requirements remains.

An unrelated untracked `docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md` appeared during verification and was left untouched.
