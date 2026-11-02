# Plan recheck 2: plan 3, the API, sign-in, and the command

Rechecked: fix round 2, `git diff 5be9524 57c582c` on `server-api`, against `plan-recheck-1.md` (N-1 to N-6) and `plan-fix-2.md`.
"Plan line N" is a line of `docs/superpowers/plans/2026-11-02-lodge-server-api.md` at `57c582c`; plan 1 read at `7d5ecbc` of `origin/server-core`.

## Findings of recheck 1

### N-1 · Resolved

Plan line 511: before the widening, Task 7a sets `tests/test_wheel.py`'s row back to `planned` with `plan` 3, the same `ts` and `why`, so the widened `ported_files_*` tests never read `ts/tests/e2e/binary.test.ts` before Task 8 creates it; Task 8's Step 4 (plan line 594) then makes it `changed` with its `dropped`, a real flip.
`planned_rows_name_a_plan` (`ts/tests/parity.test.ts` on `server-core`) accepts the row, since it keeps `plan` 3.

### N-2 · Resolved

Plan line 506: guide line 26 stays as lodge 0.2 has it, which `guide_says_waiting_first` asserts verbatim (`tests/e2e/test_guide.py:58`), and the refusal moves into a clause of line 24.
No carried test asserts line 24 (`grep -rn "write threads\|lodge ask REF" tests/` finds nothing), and a clause adds no line, so the guide stays at 60.

### N-3 · Resolved

Plan line 589 names plan 4's plan on `origin/server-import`, says it is not in the worktree, and has the coordinator paste its table as of the brief's day into Task 8's brief.

### N-4 · Resolved

Plan line 311 reads `// t-xxxxxx, from tokenId (Task 5)`.

### N-5 · Not resolved: the fix shows every held decision, and every entry with an `id`, as a problem

The signature exists as the fix uses it: `recordFromDraft(draft: Draft, id: string, date: string | null, area: string | null): Record | Area | Problem` (`ts/src/core/drafts.ts:42-47` on `origin/server-core` at `7d5ecbc`), exported through `ts/src/core/index.ts:12`.
But the arguments `"", null, null` (plan line 442) make it give a `Problem` for the drafts the page exists to show:
- a decision: `withId` adds `id: ""`, `withDate` adds no date when `date` is `null`, and `decisionFrom` requires both (`ts/src/core/headers.ts:56` `readId(requireField(header, "id"), "id", "d")` and `:61` `readDate(requireField(header, "date"), …)`);
- an entry whose draft holds its `id`, as every new entry does (`lodge id s`, guide line 28; `entry_text` of `tests/e2e/support.py:24-25`): `withId` throws ``id 's-…' differs from the id '' lodge gave this draft`` (`drafts.ts`, `withId`).
Run, in a scratch worktree at `origin/server-core` (removed afterwards): `parseDraft` then `recordFromDraft(d, "", null, null)` of `seed`'s decision draft with its quote gives `problem id must be a non-empty string`, and of an entry draft with `id: s-aaaaaa` and `area: storage` gives `problem id 's-aaaaaa' differs from the id '' lodge gave this draft`.
Failure: `held` answers every held decision as `{name, problem: "id must be a non-empty string", text}`, so the page shows the person an error in place of the title, statement, and quote they are asked to approve, at the one point where a person's decision is made (design must-not 1, "never show wrong information"), and `held_shows_the_drafts_as_core_reads_them` (plan line 457) cannot pass as written, so Task 6 stops BLOCKED.
Fix: pass the draft's own `id` when its header holds a string, otherwise a placeholder of the draft's kind (`d-000000` or `s-000000`), the hold's `at` as `date`, and `null` as `area`; the same run then gives a `decision` with `title`, `statement` `Transcripts are kept.` (reasoning apart), and `quote` `{text: "Keep them.", where: "chat", when: "2026-10-29 10:00"}`, and a `spec` with its own `id`, `area`, `title`, and `statement`.
Say in plan line 442 that a placeholder ID or date never reaches the answer (it holds `title`, `statement`, and `quote` only), and add to `held_shows_the_drafts_as_core_reads_them` a decision without `id` and an entry with one, both answered without `problem`.
Severity: Important.

### N-6 · Resolved

Plan line 389: `check` (`gate` false, passed positionally, as plan 2's `check(gate)` takes it).

## Citations

- d-j28rp0 in place of d-pmaw3a: plan lines 32, 66, 119, 144, 145, and 531; `git grep` finds no d-pmaw3a left in the plan; d-j28rp0 is current on `server-store` (`lodge show d-j28rp0`, narrowed by d-n9nm8h, which does not touch `publish`'s refusal of a changed decision).
- d-d0vca9 in place of d-4zg8q3: plan lines 22, 29, 374, and 583; no d-4zg8q3 left; d-d0vca9 is current on `server-core` with the same statement, and its reasoning now cites `tests/structure_calls.py:14-38`, which holds (recheck 1's note on the old handle is answered).
- Left as written, rightly: d-81ps01's and d-amxk94's reasoning (records do not change); `probes.md:36` still names d-pmaw3a in probe 8's last sentence, a dated probe note, not a citation the plan argues from.

## New findings

None beyond N-5's, which is the fix's own defect and is recorded there.
`plan-fix-1.md` now files the correctness review's M-6 to M-9 under "Correctness review, remaining", and the ledger gains two accurate lines.

## Counts

Rechecked: N-1 to N-6 and the two renamed rulings.
Resolved: 5 (N-1, N-2, N-3, N-4, N-6); citations: both renamings complete.
Not resolved: 1, N-5, Important (the fix's `recordFromDraft(draft, "", null, null)` turns every held decision into a problem).
New: 0 Blocking, 0 Important, 0 Minor.
