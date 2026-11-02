# Plan recheck 1: plan 3, the API, sign-in, and the command

Rechecked: fix round 1, `git diff 1b4ba97 7dfdf40` on `server-api`, against `plan-review-correctness.md`, `plan-review-practice.md`, and `plan-fix-1.md`.
Plan 2 read at `61f87ad` of `origin/server-store` (and its later `c3541fc` for drift); plan 1 at `9e133ea` of `origin/server-core`.
"Plan line N" is a line of `docs/superpowers/plans/2026-11-02-lodge-server-api.md` at `7dfdf40`.
Written incrementally; the counts are at the end.

## Correctness review

### B-1 · Resolved (by d-4zg8q3, consumed)

Plan lines 22-23 and 29 consume d-4zg8q3: `main` prints through `process.stdout.write` and `process.stderr.write`, `api` logs only through `ApiOptions.log` (plan line 374), which `main` binds (line 581).
d-4zg8q3 (`lodge show d-4zg8q3` on `server-core`) narrows the rule to `fs`'s functions and methods on `Bun.file(…)`, so both calls pass once plan 1's fix wave lands it, which plan line 22 makes the plan's starting point.
Observation outside this diff: d-4zg8q3 cites `tests/structure_calls.py:331-371`, but that file is 251 lines on `server-core`; the argument holds at `tests/structure_calls.py:14-24` (`WRITE_ATTRS` has no `write`), so the coordinator may want the handle corrected.
Both reviews asked for an author ruling; d-4zg8q3 is the coordinator's, arguing it restores d-mfskz3's intent rather than adding an allowed edge; that classification is the coordinator's call, not this recheck's.

### I-1 · Resolved, differently but adequately

Plan line 145 (row) and line 539 (test) keep `check_and_gate`'s shape for `check` (exit 1, `check 3: ` with the ID) and `show` (`fails check`), through a new decision by `author` with no quote written by `handEdit`, which the store accepts since d-pmaw3a refuses only a changed decision file.
The review's expected gate exit 1 does not hold on one state: rerun of probe 8 in a scratch repository (lodge 0.2, the file committed to `main`) gives `check` exit 1 with `check 3: <id>: …`, `show` ending `· fails check`, and `check --gate` printing `ok`, then `note: already published, check 3: lodge/decisions/<id>-unquoted.md: …`, exit 0, exactly as plan line 539 asserts.
d-81ps01's handles hold: `src/lodge/core/check_change.py:37-41` (the `already published` note), `src/lodge/core/check_state.py:130-136` (check 3), design line 79.

### I-2 · Resolved

`seed` asserts the held line by pattern before approving (plan line 536); `TestServer.approve` throws unless `published` (line 520); `add-import`'s test asserts the held line, the approval's `published`, and `show`'s `imported` and `unquoted` (line 559, matching `tests/e2e/test_add_import.py:23-26`); `held.test.ts` asserts the provisional marks and the `note:` line directly above `dry run: nothing published`, each against a named mutation (line 560).
The 81-word statement draws `feedback: <id> (provisional): the statement is 81 words; …` as claimed: `decision_statement_words` defaults to 80 (`src/lodge/core/settings.py:14`), the line format is `src/lodge/cli/output.py:59`, and plan 2's Task 12b holds only an add whose check passes, which length feedback does not fail.

### I-3 · Resolved for plans 1 and 4, but see N-1

Plan line 511 scopes the three `ported_files_*` tests to `changed` rows with `plan` 2 or 3, so plan 1's structure rows and plan 4's hook rows are no longer checked by name.
The same widening reaches this plan's own `tests/test_wheel.py` row before Task 8 creates its file: New finding N-1.

### I-4 · Resolved

`Project.url` and "every expected line that names the server's URL reads `project.url`" (plan lines 532-533); `project({ unreachable })` throws in process and points at a closed loopback port in binary mode (lines 532, 534-535); `init_when_the_server_cannot_be_reached` asserts only the start `lodge: cannot reach <project.url>: ` and one line (line 541), which both modes give; S1 says no carried test skips and the ledger gives pass, skip, and fail counts (line 107).
`client.test.ts` and `thread-fix-paths.test.ts` sit outside `tests/e2e`, so S1's `bun test tests/e2e` does not reach them.

### I-5 · Resolved

`tokenId(entropy)` in `tokens.ts` (plan lines 381, 396) leaves `mintId` and `isId` alone; its test (line 403) expects `t-0z01za` for bytes `0, 31, 32, 33, 255, 10`, which is right for `ALPHABET[b % 32]` with `ALPHABET = "0123456789abcdefghjkmnpqrstvwxyz"` (`ts/src/core/ids.ts:3,11` on `server-core`).
One stale comment remains: New finding N-4.

### I-6 · Resolved

`setup` takes `https://<host>` and `http://localhost:<port>` only (plan line 444), `setup_refuses_a_bad_origin` gains both IP forms (line 458), and Task 3's `server.url` keeps the three loopback forms (line 276).

### I-7 · Resolved, with a Minor (N-5)

`held` answers each draft as `parseDraft` of `#core` reads it, or its `problem` and raw `text` (plan line 442), tested by `held_shows_the_drafts_as_core_reads_them` (line 457); `page.js` writes those fields with `textContent` (lines 608-609); Task 6 consumes `parseDraft` (line 417), exported by `ts/src/core/index.ts:12` on `server-core` as `parseDraft(source, text): Draft | Problem`.
So the page parses no YAML, which was the finding.

### I-8 · Resolved

d-1zmfdr replaces d-z1pncx (Calls made 2, plan line 53); `tokenOf` gives `null` when unset or empty (lines 264, 279, test line 284); the client sends no `Authorization` then (line 494) and the `unauthorised` sentence names both places (line 495, test `no_token_sends_no_authorization` line 543).
Handles checked: `docs/research/2026-11-02-server-feasibility.md:43` ("the session never sees the key"), design lines 49, 192, 213, and 299 say what d-1zmfdr cites them for.

### Minors M-1 to M-9 · Resolved as plan-fix-1 claims

M-1 plan lines 225 and 233; M-2 lines 117, 349, 397, 455; M-3 lines 346 and 349; M-4 line 431; M-5 lines 392, 402, 444, 458; M-6 line 31; M-7 line 508 (but see N-2 for the line 26 change made beside it); M-8 line 587; M-9 line 543.

## Practice review

### B-1 · Resolved (by d-4zg8q3, consumed)

As correctness B-1; `ApiOptions.log` (plan line 374) also answers practice M-5.

### I-1 · Resolved, with a Minor (N-3)

d-amxk94 replaces d-djh40k (Calls made 12, plan line 63); Task 8's Modify list reaches `core`, `app`, `store`, `cli`, `api`, and the test files knip names (line 573); line 588 tags what a front-door test or plan 4's table needs.
Handles checked: `front_door_exports_every_python_name` and `front_door_exports_nothing_else` exist for `#core` (`ts/tests/core/front-door.test.ts:69,74` on `server-core`) and are specified for `#app` (plan 2 at `61f87ad`, line 350); plan 4's table is at lines 65-83 of its plan on `origin/server-import` at `ae2db4e` (d-amxk94 cites lines 64-76 of an earlier version).

### I-2 · Resolved

The table of plan lines 39-45 puts `ts/tests/e2e/support.ts` into `entry` in Task 7a and out in Task 7b, both listing `ts/knip.json` (lines 468 and 552); Task 2's `index.ts` exports `ThreadCommand` (line 236).

### I-3 · Resolved

As correctness I-4.

### I-4 · Resolved

"Names consumed from plan 2" (plan lines 112-124) names `FixedClock.sleep` and `attachmentTexts`, and the coordinator's two steps before Task 4 (lines 98-101) merge plan 2 and diff the names, a mismatch being a fix round with plan 4 told.
Checked against plan 2 at `61f87ad`, "Interfaces for plans 3 and 4" (lines 86-185) and Tasks 2, 7a, 12a, and 12b: `Lodge`'s constructor and twenty-one operations, `Store.publish(base, writes, message, approves?)`, `trees`, `attachmentTexts`, `Projects`' four methods, `Actor`, `person`, `agent(role?)`, `actorText`, `stampOf`, the five errors, `coreSettings(table)`, `Held` with `person`, `seq`, `at`, `by`, and `drafts`, `AddOutcome.HELD`, `Added.awaits` and `held`, `openDatabase`, `SqliteProjects(database, clock)`, `SqliteStore`, `rebuild`, `appendEvents(tx, project, actor, at, events)` (line 383), `applyEvent`'s `heads` rule (line 387), `FixedClock(start, stepMs)` with `sleep` adding to `start` (line 255), `CountingIds`, `project()`, and `wired(store, clock, ids, actor = person("author"))` (line 550) all exist as the plan uses them.
One shape differs from plan line 388's wording: `check(gate: boolean)` takes `gate` positionally, not in an options object (plan 2 line 152); New finding N-6.
Plan 2 moved on after `61f87ad`: `c3541fc` replaces d-pmaw3a with d-j28rp0 (same rule, corrected claim), so every citation of d-pmaw3a in this plan (lines 32, 66, 119, 144, 145, 530) names a replaced decision; the coordinator's step 2 (line 101) is where that is caught, so this is no finding of its own.

### I-5 · Resolved

As correctness I-5.

### I-6 · Rejected by d-zthdm7; the rejection holds

d-zthdm7's handles hold: `run` is one dispatching function at `src/lodge/cli/commands.py:41`, `run_thread` prints through `read_lines` (`src/lodge/cli/threads.py:90`), `tests/e2e/test_before_init_one_sentence_exit_2.py:6` runs `search`, `show`, `id`, and `check` in a 7a test, the four files are 374 lines (`wc -l`), and d-tha8st's reasoning gives the one-review-per-module argument.
The review's underlying risk, carried tests seen failing only by a missing module, is answered by Task 7a's Step 4 (plan line 546): a function-to-test map and a named mutation for any function no carried test pins.

### I-7 · Resolved

d-svv7gv; `ts/bunfig.toml` with `minimumReleaseAge = 1209600` (plan lines 65, 176, 183); Step 2 checks each version new in `ts/bun.lock` one request at a time (line 186); the merge of plan 2 regenerates the lock under it (line 100).
Not rerun here (no network): the review's own probe of Bun 1.3.14 honouring the key.

### Minors M-1 to M-7 · Resolved as plan-fix-1 claims

M-1 plan line 100; M-2 line 586; M-3 line 108; M-4 lines 16, 20, 452; M-5 lines 374, 400, 437; M-6 lines 96 and 600; M-7 line 227.
`plan-fix-1.md` files the correctness review's M-6 to M-9 under its "Practice review" heading, after the practice review's own M-6 and M-7, so two entries read "M-6" and two "M-7" there; the answers themselves are right.

## New findings

### N-1 · Important · Task 7a's widened parity check fails on this plan's `tests/test_wheel.py` row until Task 8

Handle: plan line 511 widens `ported_files_exist`, `ported_files_keep_every_python_test_name`, and `ported_files_hold_no_todo` to a `changed` row with `plan` 2 or 3 in Task 7a; `ts/tests/parity.json` on `origin/server-core` already holds `tests/test_wheel.py` as `{"status": "changed", "plan": 3, "ts": ["ts/tests/e2e/binary.test.ts"], …}`, and `ts/tests/e2e/binary.test.ts` is created by Task 8 (plan line 572); `rowMissing` reads each `ts` file with `readFileSync` (`ts/tests/parity-names.ts:50-52` on `server-core`).
Failure: at Task 7a's Step 4, `ported_files_exist` fails on `binary.test.ts` and `ported_files_keep_every_python_test_name` throws `ENOENT`, so the gate is red for a file two tasks away; Task 7a's builder either stops BLOCKED or edits the row, and plan line 593 ("flip `tests/test_wheel.py` to `changed` with its `dropped`") describes a flip that has already happened.
This is correctness I-3's failure again, with this plan's own row; the other two `changed` rows with `plan` 3 at `server-core` (`tests/e2e/test_check_and_gate.py` and `tests/e2e/test_init.py`) get their files in Task 7a itself and are safe.
Fix: either have Task 7a set `tests/test_wheel.py` back to `planned` with `plan` 3 (Task 8 then writes `changed` with `dropped` and its `why`, as line 593 says), or have the widened tests take only a `changed` row that holds a `dropped` key, every `changed` row of this plan writing `dropped` (empty for "dropped none") in its task's last step; name `ts/tests/parity.json`'s `test_wheel.py` row in Task 7a's text either way.

### N-2 · Important · the new guide line 26 breaks the carried `guide_says_waiting_first`, unlisted

Handle: plan line 506 (new in this round) replaces guide line 26 with ``Only the author writes `--by author`, signed in on the server's page; …``; `tests/e2e/test_guide.py:46-60` (`test_guide_says_waiting_first`) asserts the old line 26 verbatim, "Write `--by author` only with the author's words verbatim, with `--where` and `--when`.", at line 58; the parity row of `test_guide.py` (plan line 147) changes only `guide_is_short_and_covers_the_write_path`.
Failure: the carried `guide_says_waiting_first` fails against the new guide, so Task 7a's builder weakens or rewrites its assertion with no row naming it, which is Review Focus 1's first item, or stops BLOCKED.
Fix: keep line 26 as lodge 0.2 has it and put the refusal in a clause of line 25 or 27 (the guide stays at 60 lines), or keep the new line and add to the row's `why` that `guide_says_waiting_first` asserts the new line 26 in place of the old (d-x6vaw8, with STORE-1's option B restoring it).

### N-3 · Minor · Task 8's brief points at plan 4's plan by a path that is not on `server-api`

Handle: plan line 588 names `docs/superpowers/plans/2026-11-02-lodge-server-import.md` with no branch; the file exists only on `origin/server-import` (`ls docs/superpowers/plans/` at `7dfdf40` has no such file), while d-amxk94's own reasoning says "on `origin/server-import`".
Failure: Task 8's Codex builder, reading the worktree, finds no table, and either stops BLOCKED or removes `#cli`'s `readSettings`, `CliError`, `parse`, and `Command`, which plan 4 consumes (its plan, line 81 at `ae2db4e`) and which no file of this plan reads through `#cli`.
Fix: name the branch in line 588 and have the coordinator paste plan 4's table of that day into Task 8's brief, since plan 4 keeps moving (its table grew from lines 64-76 to 65-83 since d-amxk94 cited it).

### N-4 · Minor · `AgentToken.id`'s comment still says `mintId`

Handle: plan line 311 (`readonly id: string; // t-xxxxxx, from mintId`) against lines 381 and 396 (`tokenId`, with `mintId`'s prefix staying `d`, `s`, or `q`).
Failure: a Task 4 builder copying the interface comment reaches for `mintId("t", …)`, which `tsc` refuses (correctness I-5), or a reviewer flags the mismatch.
Fix: `// t-xxxxxx, from tokenId (Task 5)`.

### N-5 · Minor · `held`'s `title` and `quote` are read from `parseDraft`'s raw header, which types nothing

Handle: plan line 442 (`title` the header's `title`, `quote` the header's `quote` as `{text, where, when}` or `null`); `parseDraft` returns `Draft { kind, header: ReadonlyMap<string, unknown>, body, … }` and checks only key names (`ts/src/core/drafts.ts:21-38` on `server-core`); the typed reading is `recordFromDraft` (`:39-55`); `statement` is said to be "the body", which for a decision also holds `## Reasoning`.
Failure: the builder must convert `unknown` header values (a quote whose `when` YAML reads as a date, a title that is a number) to the answer's shape with no rule, and the page's "statement" shows the reasoning too; the page still shows nothing a hand parser invented, so the harm is small.
Fix: say the decision's `title`, `statement`, and `quote` come from `recordFromDraft(draft, "", null, null)` when it gives a `Decision`, and otherwise the draft's raw text with the `problem` it gives.

### N-6 · Minor · `check` is not an options-object operation

Handle: plan line 388 ("each optional argument in its options object") and line 389 (`check` (`gate` false)); plan 2's `check(gate: boolean)` at `61f87ad`, line 152, takes `gate` positionally.
Failure: none at run time, since `tsc` refuses `check({ gate })`; one wasted builder iteration.
Fix: write `check` (`gate` false, passed positionally) in line 389.

## Counts

Findings rechecked: correctness 1 Blocking, 8 Important, 9 Minor, all resolved (I-1 differently but adequately, B-1 by d-4zg8q3); practice 1 Blocking, 7 Important, 7 Minor, all resolved but I-6, whose rejection by d-zthdm7 holds.
Not resolved: 0.
New: 0 Blocking, 2 Important (N-1, N-2), 4 Minor (N-3 to N-6).
Probe rerun: probe 8 in a scratch repository under `/var/tmp`, removed afterwards; no scratch worktree was made.
