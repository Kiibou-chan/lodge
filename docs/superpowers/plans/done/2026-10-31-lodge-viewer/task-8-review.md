# Task 8 review

Commit fbc4759, reviewed in the worktree on branch `lodge-viewer`.
Counts: 0 Blocking, 2 Important, 3 Minor.

## Verified

- `uv run --frozen --quiet lodge check` prints `ok`.
- `lodge waiting` prints nothing waiting for an agent or the author.
- The seven decisions (d-r64643, d-ke9sgb, d-en18e8, d-mcx8tx, d-0my06b, d-j9d4va, d-96n7j6) are `decided_by: coordinator`, scope product, list only `link` changes, and carry no quote.
- Each statement is the brief's sentence ("Entries of area NAME list the entries they rest on."), so none reads as the author's.
- The reasoning of each has one `s-a rests on s-b: reason.` line per link, 27 lines for 27 links, matching the table in the report.
- Each of the 20 spec files gains exactly one inserted line (`git show --stat fbc4759`).
- `lodge show s-hfjr1m --provenance` still gives "changed by: d-1x1mgv", so a `link` does not count as a change to the entry.
- The four ID-naming entries (s-dm37qr, s-hfjr1m, s-m83kjq, s-582qav) carry their links, and the seven check entries rest on s-j70a0k.
- No cycle: the new edges all run from the narrower entry to the broader one, and `lodge check` would refuse a cycle.

## Important

### I1. A "changed since" mark was created on s-hfjr1m

- Handle: `uv run --frozen --quiet lodge spec | grep -c 'changed since'` prints 1; the heading reads `Write feedback advises and does not refuse (s-hfjr1m · rests on s-edgt71, changed since)`.
- The brief requires 0 and the report does not mention it.
- Cause: `_rests_on_flags` (`src/lodge/core/views.py:218-226`) compares `order_key` of s-edgt71's latest changing decision (d-4032xv) with s-hfjr1m's (d-1x1mgv).
  Both carry `date: 2026-10-30T01:26:19+01:00`, so the random ID breaks the tie (`src/lodge/core/derive.py:101-102`) and d-4032xv sorts later.
- It is a tie artefact, not a real staleness: d-1x1mgv's reasoning cites d-4032xv, so it was written knowing it.
- Failure scenario: the viewer and every read show a doubt-style mark on a current entry that nobody can clear, which is the "reads as less settled than it is" outcome s-q4s548 forbids.
- Fix, coordinator's choice:
  - (a) a ruling in the ledger that the mark is a same-second tie and is accepted, with a note for the final review; or
  - (b) a coordinator decision that edits s-hfjr1m (`changes` action `edit`, same statement or a clarified one) dated after d-4032xv, which clears the mark through `who` moving forward; or
  - (c) tie-break `order_key` on something other than the random ID, which is a spec-level change and goes to the author.
- Do not drop the s-hfjr1m to s-edgt71 link: the statement names s-edgt71 by ID, so the brief's rule requires it.

### I2. The term-use ground is applied to some terms and not to others, leaving the model area without any inbound link

The rule (brief, Task 8) includes "uses a term only B defines".
The builder applied it to reading levels, length guidance, the review flag, and the published state, but not to the record fields that only the model area defines.
The report says "model" has no links and drops only model-to-model proposals (s-q10vh5 to s-a67fqm, s-fmwe04 to s-s3z6ea), never testing the field-defining entries.
Clear misses, each with the term the statement uses:

| Entry | Should rest on | Term in the statement |
| --- | --- | --- |
| s-fmwe04 | s-0yzshh | "names it in `replaces`" |
| s-q10vh5 | s-0yzshh | "lists it in `changes` as retired" |
| s-x84e3h | s-f859z1 | "`imported_from`" |
| s-hfjr1m | s-f859z1 | "lack a `numbers` handle" |
| s-hfjr1m | s-0s9m2d | "will raise a review flag" (s-dm37qr, s-dfejrb and s-0s9m2d already rest on the flag entries) |
| s-j5ttw1 | s-aq3a5k | "`decided_by: author`" and "the required quote" |
| s-sgprxs | s-aq3a5k | "`work_item`" |
| s-0s9m2d | s-0yzshh | "`confirms` or `replaces`" |
| s-edgt71 | s-q23m04 | "the Store port gives the current and the published snapshot" |

- Failure scenario: someone retires or rewrites s-0yzshh (for example renames `confirms`) and no entry shows "changed since", so s-fmwe04, s-q10vh5, and s-0s9m2d silently describe a field that no longer exists.
- Fix: one more decision in each of the model, writing, rollout, and storage areas (`link` only, same form as the seven), or a recorded rule in the ledger that field names do not count as terms for linking, so that the missing ones are a decision and not an oversight.
- Mind I1 when adding to s-hfjr1m: s-f859z1 and s-0s9m2d must not have a changing decision later than d-1x1mgv, or a second mark appears; check with `grep -c 'changed since'` after the dry run.

## Minor

### M1. s-dm37qr omits s-v022r0 and s-8f6scf

Its statement lists "the rendered specification" (the term s-v022r0 introduces) and "links in both directions" (the rule of s-8f6scf).
The builder dropped these as independent restatements (report, "Proposals dropped"), which is defensible, but then the statement's own list is half linked: s-3n0ndk, s-wcv4en and s-0s9m2d are, these two are not.
Fix: link both in the reading decision, or state in the ledger why the list is linked by search and review only.

### M2. "First user" and "the pilot" are used by many entries and linked by none

s-kcvh60 defines "the first user", and s-5gmxyx step four defines the pilot.
s-3ht96p, s-ph9z0t, s-fehz74, s-yrz8fz, s-h12s8w, s-awc4kb, s-x84e3h, and s-t7qz74 use one or both.
Linking all of them would swamp the graph, so this is a policy gap and not a defect.
Fix: a line in the ledger saying that glossary-level terms (the first user, the pilot) do not make a link, so I2's rule is stated once.

### M3. Reasons are thin for three links

- s-dm37qr rests on s-0s9m2d: "shows the awaiting-author list defined by its review rule" does not say why s-dm37qr would not hold without it; the viewer list is also stated in s-dm37qr itself.
- s-fehz74 rests on s-wcv4en: "sets guidance for the three defined reading levels" restates the title.
- s-edgt71 rests on s-j70a0k: "applies its seven checks" is the whole reason, with no mention that the numbers 4, 5, and 6 come from the check's order.
The links hold; only the one-clause reasons are weak.
Fix: reword in the next decision touching those entries (decisions are immutable, so not in place).

## Files read

- `docs/superpowers/plans/2026-10-31-lodge-viewer/task-8-brief.md`, `task-8-report.md`.
- The whole specification through `lodge spec`; the seven new decisions through `lodge show --provenance` and `--reasoning`; s-hfjr1m, s-edgt71, s-fehz74 and d-1x1mgv, d-4032xv through `lodge show`.
- `src/lodge/core/views.py:180-240`, `src/lodge/core/derive.py:101-108`.
- `git show --stat fbc4759` and the ledger line it adds.

## Files not read

- Record files directly (by rule).
- The dry-run and add outputs under `.drafts/task8/`, which are git-ignored and not in the commit.
- The untracked decisions d-1bnqj5, d-9dqycj, d-cvtrj6, d-g7xvwm, d-rnjh2s, d-s64jyh and the Task 9 brief, which belong to later work.
- I did not run `sh scripts/check.sh`; I did not re-run the builder's pytest gate.
