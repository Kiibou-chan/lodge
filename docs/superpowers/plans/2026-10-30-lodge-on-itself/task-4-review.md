# Task 4 review: build rulings as decisions

Range: f1a6288..2e035c5 on `lodge-on-itself` (62 imports, 2 live replacements).
Result: 0 Blocking, 6 Important, 5 Minor.

## How it was checked

- Text: a script paired each of the 62 coordinator imports with its done ledger line (statement against the "what", reasoning against the "why" and the cost), then every pair was read side by side.
- Dates: a bare clone of the old-history bundle in the scratch directory, and a script taking, for each of the 62 lines, the author date of the first commit whose ledger holds the text up to "; why:"; all 62 compared with the record dates.
  The sample the dispatch named (25, 29, 34, 45, 60, 61, 77, 100, 114, 124, 127, 130, 134, 151, 169, 174, 182, 187, 188, 196, 202, 211) is inside that run.
- Classification: later ledger lines (185 to 222), `final-wave-brief.md`, `final-wave-b1-report.md`, and the code the rulings name.
- Reads: `uv run lodge show … --reasoning --provenance` on the replaced, replacing, and contested records; `uv run lodge search` on "her text", "viewer exemption", "signal handler", "push rejected remote", "final fix wave"; `uv run lodge waiting`; `uv run lodge check` (ok).

## Pass 1: correctness

Text: all 62 statements are the ledger's "what" and all reasoning its "why" and cost, word for word apart from the first capital and the closing full stop; nothing is added except line 34's "The builder's ruling, adopted:" (the ledger's own words), line 77's sentence on the missing reason, and line 211's pointer to d-9vxkjw.
Dates: 61 of 62 match the bundle rule; line 211 does not (I3).
Replacements: d-71vj1t and d-cvnk95 state what holds, and their handles resolve (`src/lodge/app/results.py:15`, `tests/app/test_writes.py:155`, `final-wave-b1-report.md` item 4, done ledger lines 201 and 210).
Public repository: no personal paths, machine names, or private details in the 64 new files (`grep -lE '/home|/tmp|/root|<account name>|<machine name>'` over them: none).

### I1 (Important): d-rvb42r stays current with a reason LODGE-8 contradicts

Handle: `lodge/decisions/d-rvb42r-final-review-d1-and-d13-go.md`, reasoning line 1, "the spec and the brainstorm are her text"; d-9vxkjw (LODGE-8), "Nothing is my text except than quotes, everything else was written by an agent."; task-4-report.md, Concerns 3.
Scenario: `lodge show d-rvb42r` prints `current · coordinator · … · imported` and, one step down, a reason saying the spec and the brainstorm are her text.
An agent reading it treats the specification or the brainstorm as her words, for example quoting a spec sentence as hers, which is the attribution LODGE-8 forbids and Review Focus 2 names.
The report classifies the line as closed process because the routing was carried out, but nothing in lodge marks the reason as overturned, so the record reads as standing.
Fix: a live coordinator decision that narrows d-rvb42r (or replaces it, if the plan's "replace" for overturned rulings is held to): D1 and D13 went to the author and she answered them (d-qbfdqt, d-gqyp3n); the reason that the spec and the brainstorm are her text does not hold, since d-9vxkjw makes only her quotes her text.
Record the choice of `narrows` over `replaces` as a ledger ruling, since the plan names only replacement.

### I2 (Important): line 187 dated from the redaction commit, after her answer to D13

Handle: d-rvb42r `date: 2026-10-29T22:20:16+01:00`; old history `2baa98c` (22:20:16, "Redact private details: plans, ledger, reviews, spec, test format") changed only "the handoff" to "the brainstorm", twice; the ruling first appears at `bee7114` (19:32:58); d-gqyp3n, her answer to D13, is dated 22:12.
Scenario: the timeline shows "D13 goes to the author" eight minutes after her answer to D13, and after the 19:32 to 20:30 rulings that followed it (task-4-report.md, order check), which is the out-of-order dating Review Focus 3 guards against.
The plan's rule, applied literally, gives 22:20, but the 22:20 change is the redaction her 22:12 ruling ordered, not a change to the ruling.
Fix: date d-rvb42r 2026-10-29T19:32:58+01:00 (bee7114) and record in the ledger: `Ruling: a ruling reworded only by the redaction commit 2baa98c keeps its earlier date; why: the redaction carried out d-gqyp3n and changed no ruling; cost if wrong: one ruling dated by its first wording.`
The other rewritten lines (60, 124, 127, 169) changed what they ruled before 22:20, so the rule's later date is right for them.

### I3 (Important): line 211 dated from the move to `done/`, an hour late

Handle: d-z727gh `date: 2026-10-29T23:42:13+01:00` (47dcfa7, "Task 14 complete; plan, ledger, and folder moved to done/"); `git log --format='%h %aI' -S'Ruling: every author record' -- docs/superpowers/plans/2026-10-29-lodge-progress.md` gives 5f31126 at 2026-10-29T22:43:31+01:00, an ancestor of HEAD, whose ledger holds the line verbatim.
Scenario: the ruling that settles LODGE-8's records sorts after LODGE-10 (d-z8jm5y, 22:46), LODGE-9 (d-qbfdqt, 22:47), the merge go (d-axaz9w, 22:49), and the tag go (d-fw070q, 23:33), so a reader of the timeline sees the author records re-added after the release they shipped in.
The report's "Line 211 was added after the squash and takes the current history's commit 47dcfa7" took the commit from the file's `done/` path, which only exists from the move.
Fix: date d-z727gh 2026-10-29T22:43:31+01:00 and correct the report's row and its date-rule paragraph to 5f31126.

### I4 (Important): line 45 is not closed process; R1 to R3 are still open

Handle: d-226x4j, "R1 to R3 wait for the final fix wave rather than a third round"; `final-wave-brief.md` items A1 to A7 and B1 to B23 name no `structure_calls.py` item; done ledger lines 41 to 44 (R1 to R3 and the aliased `datetime` minor) and 208 ("Final wave: complete."); task-4-report.md, Concerns 1, which says they are still open.
Scenario: `lodge search "viewer exemption"` puts d-226x4j first, `current`, saying the minors wait for a wave that ran and ended without them; a reader concludes the viewer-exemption gaps (`files(...).joinpath(p).open('w')` passing in `viewer`, `tests/structure_calls.py:161-165`) were dealt with.
The ruling's outcome never happened, so "closed process: the wave ran" misstates it; by the report's own rule (a later event replaces the outcome for the case ruled on) it is overturned by the final wave running without them.
Fix: classify line 45 as overturned (the final wave, done ledger lines 192 to 208, `final-wave-brief.md`), and replace d-226x4j with a live coordinator decision: R1 to R3 and the aliased `datetime` minor (done ledger lines 41 to 44) were not taken by the final wave and wait for the next code plan; add the four to this plan's ledger as a finding for the next code plan.

### I5 (Important): three standing rulings no longer describe the code, and lodge does not say so

Handles:
- d-g2p3ng (line 151), "`add` waits … until its date is after the newest decision in the current tree, so no two adds share a second"; `src/lodge/app/writes.py:141-157` waits at most `_WAITS` (3) times and not at all when the newest decision is more than three seconds ahead (Final wave B2 item 17).
- d-xd09bw (line 196), "defers the exit while a git child runs"; `src/lodge/gitstore/git.py:50` defers only when the main thread runs git (Final wave B1 item 21, from `final-wave-a-recheck-2.md` M1).
- d-fx4xv3 (line 134), "returns `REJECTED` when the branch moved"; `src/lodge/gitstore/plumbing.py:80-81` counts a moved branch that contains the commit as landed (Final wave B1 item 2, G3).
Scenario: an agent changing signal handling reads d-xd09bw, the only record lodge holds on it, and restores the deferral for every thread, which brings back the bug B1 item 21 fixed (`lodge view` not stopping on SIGTERM).
The refinement list that warns about this is in task-4-report.md, which lodge does not hold, and Task 5 sends agents to lodge.
d-g2p3ng is also bounded by d-gmtkw4 (line 154), which lodge holds, but the three-second rule is in no record.
Fix: one live coordinator decision per ruling, each with `narrows` naming it, stating what holds now and citing the final-wave item and the code line above; reclassify the three as "narrowed" in the report, a fourth class beside standing, overturned, and closed process.
The other refinements (61, 73, 87, 160, 168) only add cases the ruling left open, and its text still holds, so they need nothing.

## Pass 2: practice

Titles are within 100 characters and name the task; no em-dashes and no American spellings in the 64 files (grep); one sentence per line holds; scope, `work_item`, and `decided_by` are uniform (64 each).

### M1 (Minor): capitalising the first letter breaks three handles

Handle: d-8j1502 reasoning "Task-6-review.md, I5 and the ruling section."; d-n8ecsn reasoning "Task-12-review.md, Minors, each run."; d-6c610m reasoning "Spec:174 makes …".
Scenario: `ls docs/superpowers/plans/done/2026-10-29-lodge/Task-6-review.md` fails on a case-sensitive file system, and a grep for `spec:174` misses d-6c610m.
Once published the reasoning is immutable (d-z8jm5y, LODGE-10), so the fix costs a replacing decision per record after the merge.
Fix: leave a line that starts with a file name or a handle in its ledger case (`task-6-review.md, …`), or prefix "See ".

### M2 (Minor): line 25 drops the problem it rules on

Handle: done ledger line 25, middle cell "`test_wheel` runs `uv build`, which may fetch the build backend; CLAUDE.md says tests use no network"; d-02htqk carries only the last cell.
Scenario: a reader of d-02htqk does not see that the ruling is an exception to the repository's no-network rule for tests (`CLAUDE.md`, Hard rules), and may take the network use as unremarkable elsewhere.
Fix: open the reasoning with the middle cell, verbatim.

### M3 (Minor): a figure without a `numbers` handle

Handle: d-5qyhyw (line 84) reasoning "`related`'s threshold of 2"; `src/lodge/core/search.py:16`, `_RELATED_WORDS = 2`; task-4-report.md, Feedback answered, "all 42 notes are labels".
Scenario: the threshold changes in code and nothing in lodge points from the ruling to the constant; the plan's Global Constraints give a figure its file and item as handle.
Fix: `numbers: [{value: "2", handle: "src/lodge/core/search.py, _RELATED_WORDS"}]`.

## Pass 3: design

Search finds rulings by their statement words: "viewer exemption", "signal handler", "final fix wave", and "push rejected remote" put the ruling first or second; the task-prefixed titles disambiguate the reused review labels (I1, M4, B1).
`lodge waiting` is empty and `lodge check` is ok, so the imports raise no flag.

### I6 (Important): the line-handle note points to files no reader can open

Handle: the note "Line handles such as spec:N refer to the files at this ruling's date." on all 62; d-5fazhr "(spec:208)" and d-6c610m "Spec:174"; done ledger line 210, "Commit hashes cited above refer to the history before the rewrite, kept only on the author's machine".
Run: `sed -n 174p` of the frozen spec prints the review-flag sentence and `sed -n 208p` a code fence; in the bundle, 30f919b's spec:174 is the LODGE-2 safeguard ("the required quote … shows at level 1") and 02e3292's spec:208 is the `lodge/attachments/<id>/` line, now spec:212.
Scenario: a reader follows spec:174 from d-6c610m into the frozen spec, the only version in this repository, lands on the review flag, and misreads why the quote sits at level 1.
The note is true but names a version that exists only in a bundle outside the repository, so it cannot be followed; and once published it is immutable on 62 records (LODGE-10), so a wrong note costs 62 replacements.
The plan handles (plan:51, plan:283-286, plan:307, plan:380) still resolve in `done/2026-10-29-lodge.md` to the text the rulings cite; only the two spec handles drifted.
Fix: in d-5fazhr and d-6c610m, add the section and the text beside the handle (for example "spec:208, Storage, the `lodge/attachments/<id>/` line"); change the note to "Line handles such as spec:N refer to the files at this ruling's date, in the history before the squash, which this repository does not hold; the section named beside a handle is the way in."

### M4 (Minor): bare report names do not say where they live

Handle: 19 report and review names in reasoning (`task-5-review.md`, `lodge-round-recheck.md`, `final-wave-brief.md`, …) and `same_second.sh`, which is not in the repository.
Scenario: a reader of d-5jhhrs, whose only content is a pointer to `task-5-review.md`, has to guess the folder; `git ls-files | grep same_second` finds nothing.
Fix: one line in each record's reasoning, or in the note of I6: "Report and review names are files in `docs/superpowers/plans/done/2026-10-29-lodge/`; probe scripts were scratch and are not kept."

### M5 (Minor): closed-process and standing rulings read alike

Handle: task-4-report.md, Classification (8 closed process); `lodge show d-nzkm9r` and `lodge show d-fz6gnk` both print `current · coordinator · … · imported`.
Scenario: a reader cannot tell from lodge that "Task 13 creates no tag" was carried out and binds nothing now, while "the builder's command-line choices stand" still describes the code.
Fix: none needed in lodge 0.1 beyond I4 and I5; note it as input for the next code plan (a process ruling with a finished `work_item` could show as such).

## Files

Read: `CLAUDE.md`; `.claude/agents/reviewer.md`; the plan (whole); its ledger (whole); `task-4-report.md`; the done ledger (lines 1 to 46 and 185 to 222, and every ruling line); `final-wave-brief.md` (lines 1 to 80); `final-wave-b1-report.md` (item 4); the 64 new record files (through the pairing script and `lodge show`); `src/lodge/app/writes.py:135-165`; `src/lodge/gitstore/git.py:30-70`; `src/lodge/gitstore/plumbing.py:40-100`; `src/lodge/core/derive.py:150-220`; `src/lodge/core/search.py:16,84-92`; spec lines 174, 208, 212 now and in the bundle.
Not read: the other done reports and reviews in full (only grepped), the Task 1 and 2 records, the rest of `src`.
No scratch worktree was needed; the bundle clone in the scratch directory was removed after the date run.
