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
Ruling: a person is a member of the project, carried in `Tree.people`, lodge 0.2's words kept for `author` (d-kj59bz).
Ruling: a person's decision drafted by another is held whole until that person approves or declines it (d-znagqe, SRV-2).
Ruling: a review flag waits for each person whose decision raised it (d-4spcem).
Ruling: every write is already checked against the state it lands on, proved over the events store (d-fv20kp).
Ruling: projects and members are events behind a `Projects` port (d-wx7d0f).
Ruling: the import is checked by its own state check, since it publishes through the store (d-pprhpz, narrowing d-fv20kp after plan 4's d-y42b7b).
Alignment: plan 3 read at f2dcc72 (`origin/server-api`), plan 4 at 34c12f1 (`origin/server-import`); `Store.attachmentTexts` added for plan 4's export.
No value trade-off for the author, so no `questions.md`.
