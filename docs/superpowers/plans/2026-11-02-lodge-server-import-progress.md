# Progress: docs/superpowers/plans/2026-11-02-lodge-server-import.md

Branch `server-import`; authority for the build: the server design, approved by the author 2026-11-02 13:52 ("Approved").
Briefs, reports, and reviews: `docs/superpowers/plans/2026-11-02-lodge-server-import/`; probes in `probes.md` there, their sources in `probes/`, and the made-up lodge 0.2 store in `probes/zero-two-store/`.

Plan: written by the planner from `planner-brief.md`; thirteen tasks (1 to 10, 11a, 11b, and 11c); after Task 1 four lanes run at once (2 then 3; 4; 5; 6 then 7), each from the plan 2 task the lanes table names, then 8 beside 9 once plans 2 and 3 are merged.
Ruling: the import reads the repository on the server, for the signed-in person only (d-1skjw1).
Ruling: the import checks the store as lodge 0.2 does, then maps, into an empty project only (d-ag8p8h).
Ruling: the importer maps only `decided_by`, through the writer, and keeps thread messages (d-bh93bn).
Ruling: stored bytes decode in `text.ts`, and the importer refuses an attachment that is not UTF-8 (d-m31e0d, under d-0q54zn).
Ruling: the export writes only a branch of its own, without a work tree or force (d-pv341r).
Ruling: the export batches its writes in `app`, at most one commit a minute (d-srfxj8).
Ruling: the hook advises on every file under `lodge/` of a moved project, its paths resolved by `git` (d-va3j7x).
Ruling: the server design goes into lodge whole, each unbuilt claim naming its build step (d-yng7m8).
Question for the author: IMP-1 in `questions.md`, who the export names in `decided_by`; the plan follows design line 78 until she answers.
Ruling: the importer maps `decided_by` and thread messages by `author` to the owner, through the writers (d-83kt6y, replacing d-bh93bn: plan 2's core reads a message as a person's only when its `by` is a member, probe 7).
Ruling: the importer reads stored bytes through plan 2's codec and refuses no file for its bytes (d-ryss91, replacing d-m31e0d: plan 2's Task 7 builds the codec and stores bytes in a `blob`).
Ruling: the export batches in `app` through the clock's sleep, reading every file of the project (d-sj6hmf, replacing d-srfxj8: plan 2's `Clock` has `sleep`).
Ruling: the import publishes the store's files through the project's store, by its one owner, not through `Lodge.add`, which mints IDs and dates (d-y42b7b).
Ruling: the hook's settings parse in `app`, its context is built in `cli` with `git`'s functions as parameters, and `lodge hook` runs through a function of `Io` that `main` builds (d-bs5mm8).
Ruling: the export target is an `export-target` event, a wrapped store tells the exporter after each published write, and `main` joins `git`'s and `cli`'s reading of a 0.2 store (d-j5s0h0).
Alignment: plan 2 at 7204ad3 (`origin/server-store`), whose d-pprhpz records d-y42b7b from its side and whose `Store.attachmentTexts()` replaces the store function d-sj6hmf asked for; plan 3 at f2dcc72 (`origin/server-api`, Tasks 1 to 9 drafted); the names taken are the plan's table "Names this plan consumes from plans 2 and 3".
Open with plans 2 and 3: plan 3's `project-create` does not say that it makes the person the project's owner in plan 2's `Projects`, which Task 8's import needs, and plan 3's `lodgeFor` gives plan 2's `Lodge` no actor (plan 2, Task 11); Task 8 stops BLOCKED if the merged code leaves the owner out.
