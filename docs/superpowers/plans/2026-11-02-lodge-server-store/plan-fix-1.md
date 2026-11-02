# Plan fix round 1: plan 2, the events store and the operations

Planner, fix round 1, on `server-store` from be72406, answering `plan-review-correctness.md` (0 Blocking, 9 Important, 10 Minor) and `plan-review-practice.md` (0 Blocking, 7 Important, 9 Minor).
Status: in progress.

## Rulings recorded

- d-pmaw3a (replaces d-pprhpz, narrows d-fv20kp): `SqliteStore.publish` refuses what lodge 0.2's `check_writes` refuses, a path holding a surrogate, and a changed text for an existing decision file; it runs no other check (I-7, I-8, M-7).
- d-vwsnz5 (replaces d-kj59bz): a person is an owner of the project; `isAuthor`, `parseThread`, and `writeThread` take the people as a defaulted trailing parameter; a name the records use as a role cannot join (I-3, I-6, I-9, P-I3).
- d-x6vaw8: only a person writes a thread message under their own name; the author is asked STORE-1 in `questions.md` (I-5).
- d-d96y91 (narrows d-t7er56): a lane's tests call only what its waits provide; a ported function's new parameter has a default; Task 12 splits into 12a and 12b (I-2, P-I1, P-I2, M-3, P-I6, M-10, P-I7).
- d-nf7wvx: a dependency-cruiser rule `store-imports` (P-M9; probe 9).
- d-thvvzx: a store transaction that reads before it writes opens with a write, and a hold settles once (I-1, M-8).

## Findings
