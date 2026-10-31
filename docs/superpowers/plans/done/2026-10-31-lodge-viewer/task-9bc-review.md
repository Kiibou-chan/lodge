# Review of Tasks 9b and 9c

Scope: commits d48a559 and ddd91c0, `git diff 65f9bd0 ddd91c0`, on branch `lodge-viewer`.
Angles, in order: correctness, practice, design.

Result: 0 Blocking, 3 Important, 8 Minor.

## Verified

- `uv run --frozen --quiet lodge check` prints `ok` at ddd91c0 (run in a detached scratch worktree, since removed).
- `lodge waiting` is empty in both groups.
- `lodge spec | grep -c ", changed since)"` prints 0.
  The two lines matching plain `changed since` are explanatory statements (s-7wbv0e, s-kba448), not marks.
- `lodge check --gate` prints `ok` with five "order changed" notes, which are the expected insertions.
- Builder gate re-run at ddd91c0: pytest `1366 passed` (without the socket-bound `tests/viewer/test_server.py` and `tests/e2e/test_view.py`, and the network-bound `tests/test_wheel.py`), `ruff check` clean, `mypy` clean.
- No decision file was modified in either commit (five added: d-68b0j2, d-6zyet3, d-m4ky49, d-7n4jyj, d-h3v99q), all `decided_by: coordinator`, none with a `quote`.
  No author decision was added or changed in 9b or 9c, and none is narrowed.
- No em-dashes, US spellings, or multi-sentence lines in the 46 added or modified record, report, and guide files; no personal paths in the diff; nothing under `.drafts/` is tracked.

## (1) Check 4 change against d-na1eg7

`src/lodge/core/check_entries.py:44-53` skips the "link changes more than rests_on / is new" refusal when another new decision of the same change lists the same entry with `edit` or `create`.
That is what d-na1eg7 says, and no more: a published decision cannot supply it (the loop is over `added`), a decision about another entry cannot (`c.entry == change.entry`), and the entry's own `edit` or `create` is still demanded by the first loop (lines 31-39).
The message and guide wording change with it (`src/lodge/cli/guide.md:44`, and the s-0yzshh edit).

Tests fail without the change: with `check_entries.py` restored from 65f9bd0, `tests/core/test_check_links.py` gives `6 failed, 9 passed`, as the 9b report says.
Four of the six are the two acceptance cases and the two reworded-message assertions; the two rejection cases fail only on the new message text, since refusal already worked before.

No finding on the code's behaviour.
Test and practice findings are M1 and M2 below.

## (2) The design is in lodge

I mapped every claim of design lines 21 to 141 against `lodge spec` (9a, 9b, and 9c together) and the 9c report's table.
Every claim has an entry; the omissions the 9c report names (headings, blank lines, the historical entry count, the rollout steps) are rollout or motivation, and I agree with them.
No entry says materially more than the design.
Gaps, all small: M5 and M6.

## (3) Contradictions with current records

I read level 1 of all 296 records and searched for "read-only", "seven", "7 checks", "two record kinds", "two kinds", "no confirmation step", "decision only", and similar.
"There is no confirmation step" is gone.
The seven-check statements d-3epcjd and d-4032xv, and d-zerbz9, are narrowed by d-6zyet3.
d-cg3nn3 is narrowed by d-3d4g9j and d-dyrpc6.
What remains is I1 and I2.

## (4) Attribution

Agent text never reads as hers: the new entries say "the author" in the third person and name d-9dqycj, d-g7xvwm, and d-s64jyh only as authority, with no quotation.
s-77krr7 and s-ycx03c state the verbatim rule.
No finding.

## (5) Prose rules

British English, no em-dashes, Oxford comma, and one sentence per line hold in every added or changed file I scanned (area `_area.md` intros aside, see I2).
No finding.

## (6) Gate state

As in "Verified".
No finding.

## Findings

### Important

**I1. d-vme42w is current and now false.**
`d-vme42w` (coordinator, 2026-10-30) says "The entry on the viewer says it is read-only for now and that editing from it is a goal for later", and its only change is an edit of s-582qav.
After d-6zyet3 and d-m4ky49, s-582qav and s-dm37qr say the viewer writes confirmations and threads, so the decision's statement is false; no decision narrows or replaces it (`lodge show d-vme42w` has no "narrowed by").
The brief requires narrowing the coordinator decisions whose statements the part makes false; 9b rewrote s-582qav and s-dm37qr (reported as a concern) but did not narrow d-vme42w.
Related: d-x42f0x ("The viewer is local, read-only") is narrowed only by the author's d-dyrpc6, which covers confirming, so nothing coordinator-side records that threads also end its "read-only" claim.
Fix: one coordinator decision with `narrows: [d-vme42w, d-x42f0x]`, reasoning that the viewer now writes author confirmations and threads (s-dm37qr, s-582qav, d-h3v99q), that d-2hcgav still holds (editing remains later), and that the rest of d-x42f0x (local, started from the command line, the listed reads) stands.
No author decision is narrowed.

**I2. Two area introductions contradict current entries.**
`lodge/spec/model/_area.md:8` reads "The two record kinds, ...", against s-a67fqm ("three kinds of record").
`lodge/spec/writing/_area.md:8` reads "... the seven checks, and the review flag.", against s-j70a0k ("eight checks") and d-6zyet3.
Both print in `lodge spec` (lines 86 and 624 of my dump) and in the viewer as the area's one-line intro.
Fix: `lodge draft area:model` and `lodge draft area:writing`, change to "The three record kinds, their fields, ..." and "..., the eight checks, ...", and add them with the next coordinator decision (the I1 fix can carry them).

**I3. The reasoning of d-68b0j2 and d-6zyet3 does not carry the design's reasons.**
The brief says each decision's reasoning "carries the section's reasons".
d-68b0j2 (six lines) and d-6zyet3 (six lines plus four reaffirmation lines) give attributions (d-7w5aq0, d-a3h9f3, d-9dqycj, d-na1eg7) and list the coordinator's calls, but drop the why of the design's choices.
Missing: messages are never edited so a thread records what was said (design 79); a doubt on a decision must show on the specification because she reads there (design 93); entries only, not decisions, may be rested on (design 104); a `link` neither floods `lodge waiting` nor clears the warning it exists for (design 107).
d-7n4jyj and d-h3v99q are better (the browser-sends-Origin reason, the trust-boundary reason), though d-h3v99q omits why the host check stays whole-header (proxies on another port need `name:port`, design 129).
Entry text carries some of this (s-wvza5q has the cycle reason), but Task 10 freezes the design file, so the rest would live only in git history.
Fix: `replaces` on two decisions is heavy for this, so put the missing reasons as reasoning lines in the decision that carries the I1 fix, naming d-68b0j2 and d-6zyet3, or accept the gap with a ledger `Ruling:` line (what: reasons stay in the frozen design; why: the entries state the rules; cost if wrong: a reader of lodge alone cannot see why).

### Minor

**M1. The new tests do not pin the narrow reading of d-na1eg7.**
Two mutations of `check_entries.py:44-53` still pass all 15 tests in `tests/core/test_check_links.py`.
Dropping `other.id != d.id` lets one decision listing both `link` and `edit` for the entry exempt itself.
Widening the action set to `(EDIT, CREATE, LINK, RETIRE)` lets two `link` decisions exempt each other while the text changed, which is the failure d-na1eg7 names ("a `link` with no such decision still fails").
Fix: add two cases to `test_link_without_another_decision_accounting_for_text_fails`: a second decision listing only `link` for the entry, and one decision listing `link` and `edit` for the entry (decide whether the latter should pass, then pin it).

**M2. The exemption is a nested `any(any(...))` inside the loop.**
`check_entries.py:44-53` is hard to read at a glance, in a function that already does three jobs.
Fix: extract `_accounted_for_by_another(added, d, entry_id) -> bool`, beside the existing `_only_rests_on_differs`.

**M3. The viewer's token and Origin entries are filed in `writing`.**
s-q42qd7 and s-rpn77e are in `lodge/spec/writing/`, while s-704ssg (the host rule, same design section) and s-bet2rj are in `reading`.
The brief files "the viewer" under `reading` and `writing` for "a check, feedback, the review flag, or what waits"; these are request checks of the viewer, not lodge checks.
A reader looking for the viewer's write rules finds them in two areas.
Fix: move both to `reading` with an area edit in a decision, or record the choice in the ledger.

**M4. Claims are stored twice.**
Check 6's `rests_on` clause is in s-aw5a1j (last sentence) and s-wvza5q (third sentence).
The two waiting groups are in s-0s9m2d (last sentence) and s-nda0br.
The link exception to check 4 is in s-0yzshh and s-7wbv0e (the same sentence).
Checks 1, 2, and 5 for threads are in s-3e6zp3, and check 5 also in s-ms14fq.
The brief requires the edits to s-0yzshh, s-0s9m2d, s-aw5a1j, and s-ms14fq, so the duplication follows the brief, but s-4ykcm0 says no link is stored twice and the same reasoning applies to claims.
Fix: keep the required edits and make each new entry say only what the edited entry does not (s-wvza5q drops the check 6 sentence; s-nda0br is the single home of the groups, with s-0s9m2d pointing to it).

**M5. s-7wbv0e adds scope to design line 107.**
"preserving warnings during dependency migration" narrows a general rule (design: a `link` "neither floods `lodge waiting` nor clears the warning the links exist for") to the migration.
Fix: reword to "so adding links neither raises a flag nor clears a 'changed since' warning".

**M6. Two small design statements have a weak entry or none.**
Design line 54: the form's note that a caveat such as "read, not fully understood" belongs in the field is not in s-arr325 (a 9a entry, but the 9c coverage map claims lines 50 to 54 are covered).
Design line 138 (agents read open threads first; the guide and project instructions say so): only s-c8hrye mentions `lodge waiting` and "session instructions", and no entry says the guide does.
Fix: add the caveat clause to s-arr325 and one sentence to s-c8hrye or s-nda0br naming the guide.

**M7. The reports cite files that are not in the repository.**
The 9b and 9c reports point at `.drafts/task9b/...` and `.drafts/task9c/...` (git-ignored) for failing output, dry runs, and spec snapshots; I could not read them.
The one count I could check, I reproduced: 6 failed, 9 passed.
Fix: copy the failing-test log into `docs/superpowers/plans/2026-10-31-lodge-viewer/` or quote it in the report.

**M8. Text outside lodge still states old behaviour.**
`README.md:101` at ddd91c0 reads "The viewer is local and read-only" (Task 10 has an uncommitted change in the working tree that I did not review).
`docs/superpowers/plans/2026-10-31-lodge-viewer.md:162` and `task-2-brief.md:55` give the old check 4 messages, without "in another decision of this change".
Fix: confirm Task 10's README change covers line 101; leave the plan lines as history or add a one-line note naming d-na1eg7.

## Files read

Read in full or in the relevant part: `src/lodge/core/check_entries.py`, `tests/core/test_check_links.py`, `src/lodge/core/check_immutable.py` (lines 30-50), the check 4 and guide diffs, the Task 9 brief, the design, `task-9b-report.md`, `task-9c-report.md`, the progress ledger diff, `lodge guide`, `lodge spec` (whole), `lodge show` for d-na1eg7, d-68b0j2, d-6zyet3, d-m4ky49, d-7n4jyj, d-h3v99q, d-9dqycj, d-a3h9f3, d-dyrpc6, d-vme42w, d-x42f0x, d-cg3nn3, d-g7xvwm, d-s64jyh, s-2bzwzv, and s-v022r0, level 1 of all 296 records, and the heads of `lodge/spec/model/_area.md` and `lodge/spec/writing/_area.md`.

Not read: record files by hand (lodge only, except the two `_area.md` intros, which lodge prints), `task-9b-codex-final*.txt`, `task-9c-codex-final.txt`, the `.drafts/` logs (git-ignored), the uncommitted Task 10 changes, `tests/viewer/test_server.py` and `tests/e2e/test_view.py` (socket-bound, not run), `tests/test_wheel.py` (needs the network).
