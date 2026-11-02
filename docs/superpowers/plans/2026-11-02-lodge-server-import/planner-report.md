# Planner report: plan 4 of build step 1

Status: done; the plan is written and aligned, ready for its review.

## The plan

Thirteen tasks: 1 to 10, 11a, 11b, and 11c.
Task 1 is the coordinator's (merge plan 1, generate the made-up 0.2 store's fixture with `probes/fixture.py`).
After Task 1 four lanes run at once, each from the plan 2 task the lanes table names: Task 2 then 3 (`git`), Task 4 (`hook`), Task 5 (`app`, the import), and Task 6 then 7 (`app` and `store`, the export).
Tasks 8 (`api`, `main`) and 9 (`cli`, `main`) run beside each other once plans 2 and 3 are merged; then Task 10, the round trip, and Tasks 11a to 11c in order.

## Aligned against

Plan 2 at `origin/server-store` 7204ad3 and plan 3 at `origin/server-api` 3e4c29c, both still being planned.
The names taken from them are the plan's table "Names this plan consumes from plans 2 and 3"; plan 2's d-pprhpz records the import's path through `Store.publish` from its side, matching d-y42b7b.

## Rulings recorded

Current: d-1skjw1, d-ag8p8h, d-83kt6y, d-ryss91, d-y42b7b, d-pv341r, d-sj6hmf, d-j5s0h0, d-va3j7x, d-bs5mm8, d-yng7m8 (`lodge check`: ok after each add).
Replaced while aligning with plan 2: d-bh93bn by d-83kt6y, d-m31e0d by d-ryss91, d-srfxj8 by d-sj6hmf.

## Concerns for the coordinator

- Task 6's `exportingProjects` wraps plan 2's `Projects`; plan 3's Task 4 adds `settings` and `names` to it, whose forwarding Task 8 adds, so a later addition to `Projects` needs the same line.
- d-sj6hmf says the export reads attachments "through a function `store` adds"; plan 2 now adds `Store.attachmentTexts()` to the port for this, so the plan uses that.

## For the author

IMP-1 in `questions.md`: under design line 78 the export names a person in `decided_by` and in thread messages, and lodge 0.2 then fails check 3 on each of her confirmations and cannot read her thread messages (probes 3 and 7), against design line 284's "reads like a lodge 0.2 store".
