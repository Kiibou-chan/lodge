# Progress: docs/superpowers/plans/2026-11-02-lodge-server-store.md

Branch `server-store`; authority for the build: the server design, approved by the author 2026-11-02 13:52 ("Approved").
Briefs, reports, and reviews: `docs/superpowers/plans/2026-11-02-lodge-server-store/`; probes in `probes.md` there, their sources in `probes/`.

Plan: written by the planner from `planner-brief.md`, 15 tasks (1 to 14, Task 7 split into 7a and 7b) in three lanes (A: Tasks 2 to 6; B: 7a, 7b, and 8; C: 10 and 13); probes 1 to 8 in `probes.md`.
Ruling: the ports are asynchronous, and the clock gives milliseconds with an offset (d-59q4jc).
Ruling: the `Store` port keeps lodge 0.2's methods, and the SQLite store gives one state (d-ae1vn5).
Ruling: events hold file bytes in a `blob`, decoded as `surrogateescape` (d-0q54zn now this plan's), and a write is a compare-and-set on the project's newest event (d-wje1cn).
Ruling: a defaulted Python parameter becomes a field of one trailing options object (d-vd3175).
Ruling: three lanes, and `Lodge` ported a method at a time (d-t7er56).
Ruling: two tests of `test_thread_fix_paths.py` wait for plan 3, whose row it becomes (d-rp74dr).
Ruling: a person's decision drafted by another is held whole until that person approves or declines it (d-znagqe, SRV-2).
Ruling: a review flag waits for each person whose decision raised it (d-4spcem).
Ruling: every write is already checked against the state it lands on, proved over the events store (d-fv20kp).
Ruling: projects and members are events behind a `Projects` port (d-wx7d0f).
Alignment: plan 3 read at f2dcc72 (`origin/server-api`), plan 4 at 34c12f1 (`origin/server-import`); `Store.attachmentTexts` added for plan 4's export.
One value trade-off waits for the author: STORE-1 in `questions.md` (d-x6vaw8).
Plan: reviews correctness 0B/9I/10M and practice 0B/7I/9M (`plan-review-correctness.md`, `plan-review-practice.md`). Fix round 1 by the planner.
Fix round 1 (`plan-fix-1.md`): all 35 findings answered, 19 of correctness and 16 of practice.
Ruling: the store refuses what lodge 0.2's stores refuse, a path holding a surrogate, and a decision file's new text, a re-rendered decision with unchanged fields included; the import is checked by its own state check (d-j28rp0, replacing d-pmaw3a and so d-pprhpz, whose cost the correctness review showed false, and narrowing d-fv20kp).
Ruling: a person is an owner of the project, carried in `Tree.people` and as a defaulted parameter, lodge 0.2's words kept for `author`, and a name the records use as a role cannot join (d-vwsnz5, replacing d-kj59bz).
Ruling: only a person writes a thread message under their own name (d-x6vaw8); the value trade-off is the author's, STORE-1 in `questions.md`, and the plan follows its option A until she answers.
Ruling: a lane's tests call only what its waits provide, a new parameter of a function another lane calls has a default, and Task 12 splits into 12a and 12b (d-d96y91, narrowing d-t7er56).
Ruling: the rule `store-imports` holds `store` to Kysely and `bun:sqlite` (d-nf7wvx, probe 9).
Ruling: a store transaction that reads before it writes opens with a write, and a hold is approved or declined once (d-thvvzx).
Lanes: Task 9 waits for 6 and 8; Task 11 for 9 and 10; Task 12 is 12a (after 11) and 12b (after 12a); lanes A, B, and C keep their tasks.
Alignment for plan 3 (`origin/server-api` 3e4c29c): an agent token writing `by: <person>` in a thread is `Forbidden` (d-x6vaw8), so the carried command tests writing `--by author` with where and when (`author_words_are_recorded_exactly`, `waiting_groups_threads`) change or write through the person's session; `publish` refuses a changed decision file (d-j28rp0), so `handEdit` of an existing decision (`broken-agent-decision-warns-above-show`) is refused; `Tree.people` are the owners and `confirm` refuses a non-owner (d-vwsnz5); `applyEvent` updates `heads` for every kind but `project`, never upserting, so account events of the empty project add no row; `approval_runs_the_check_again` is in Task 12b.
Alignment for plan 4 (`origin/server-import` 6c6322c): plan 2's Task 12 is 12a (the `Store` methods its export wrapper passes on) and 12b (the operations); `parseThread` and `writeThread` keep their names with `people` defaulted; `publish` refuses a path holding a surrogate, so the import of a lodge 0.2 store with a non-UTF-8 file name fails at `publish` unless plan 4's check refuses it first.
Fix round 2 (`plan-fix-2.md`): the recheck's five findings answered; `awaits.ts` cuts the cycle between `held.ts` and `writes.ts` in Task 12b; d-j28rp0 replaces d-pmaw3a; lanes unchanged.
