# Progress: docs/superpowers/plans/2026-11-02-lodge-server-import.md

Branch `server-import`; authority for the build: the server design, approved by the author 2026-11-02 13:52 ("Approved").
Briefs, reports, and reviews: `docs/superpowers/plans/2026-11-02-lodge-server-import/`; probes in `probes.md` there, their sources in `probes/`, and the made-up lodge 0.2 store in `probes/zero-two-store/`.

Plan: written by the planner from `planner-brief.md`; thirteen tasks, Tasks 3 to 7 in parallel lanes once plan 2's `app` front door is merged, and Tasks 8 and 9 beside each other once plans 2 and 3 are merged.
Ruling: the import reads the repository on the server, for the signed-in person only (d-1skjw1).
Ruling: the import checks the store as lodge 0.2 does, then maps, into an empty project only (d-ag8p8h).
Ruling: the importer maps only `decided_by`, through the writer, and keeps thread messages (d-bh93bn).
Ruling: stored bytes decode in `text.ts`, and the importer refuses an attachment that is not UTF-8 (d-m31e0d, under d-0q54zn).
Ruling: the export writes only a branch of its own, without a work tree or force (d-pv341r).
Ruling: the export batches its writes in `app`, at most one commit a minute (d-srfxj8).
Ruling: the hook advises on every file under `lodge/` of a moved project, its paths resolved by `git` (d-va3j7x).
Ruling: the server design goes into lodge whole, each unbuilt claim naming its build step (d-yng7m8).
Question for the author: IMP-1 in `questions.md`, who the export names in `decided_by`; the plan follows design line 78 until she answers.
