# Progress: docs/superpowers/plans/2026-11-02-lodge-server-api.md

Branch `server-api`; authority for the build: the server design, approved by the author 2026-11-02 13:52 ("Approved").
Briefs, reports, and reviews: `docs/superpowers/plans/2026-11-02-lodge-server-api/`; probes in `probes.md` there, their sources in `probes/`.

Plan: written by the planner from `planner-brief.md`, 10 tasks (1 to 9, Task 7 split into 7a and 7b) in four lanes (A: Task 2; B: Task 3; C: Tasks 4 to 6; D: Task 9 beside 7a to 8), the main line 7a, 7b, and 8; probes 1 to 7 in `probes.md`.
Ruling: ten tasks in lanes by the import graph (d-p8jdqj).
Ruling: the command names its server and project in `.lodge.toml` and takes its token from `LODGE_TOKEN` (d-z1pncx).
Ruling: `.lodge.toml` is parsed with smol-toml and `integersAsBigInt`, so `title_chars = 80.0` is refused with lodge 0.2's sentence (d-dfkqec).
Ruling: a project's length and import settings live on the server, given once by `lodge init`, in plan 2's `project` event (d-y0ppty).
Ruling: agent tokens are per project, with an optional role, issued by the person, whose operations need the person's session (d-kt4jkq).
Ruling: the wire keeps TypeScript names, tags maps and sets, answers a failed check whole, and carries the version (d-3ywdhq, narrowing d-sry12f).
Ruling: `lodge` is one program, `lodge server` going to `api` (d-vfyex3, narrowing d-yayhct).
Ruling: sign-in fixes origin and person at setup, requires user verification, and keeps sessions 30 days (d-rn4qzq).
Ruling: the command's grammar is a small parser of its own, written to argparse's messages (d-kky8qc).
Ruling: the carried command tests run in process against the handler, and through the binary on a socket (d-bwb1tt).
Ruling: the page, its script, and the guide are text imports (d-5kskm3).
Ruling: knip checks the front doors from this plan on, unread core names of `__all__` marked public (d-djh40k, narrowing d-s2rdn2).
Alignment: plan 2 read at 7204ad3 (`origin/server-store`); Task 4 extends plan 2's `Projects` and store with the accounts' events and the project's settings.
No value trade-off for the author, so no `questions.md`.
Plan: reviews correctness 1B/8I/9M and practice 1B/7I/7M (`plan-review-correctness.md`, `plan-review-practice.md`).
Fix round 1 by the planner (`plan-fix-1.md`): 30 fixed, B-1 of both settled by the coordinator's d-4zg8q3 (recorded on `server-core`), 1 rejected, 0 parked.
Ruling: the command sends `LODGE_TOKEN` when set and no `Authorization` otherwise, for a cloud environment's network secret (d-1zmfdr, replacing d-z1pncx).
Ruling: knip's `includeEntryExports` tags what a front-door test or plan 4 needs and removes the rest (d-amxk94, replacing d-djh40k).
Ruling: Task 7a stays one task, its report mapping each ported function to the tests that pin it (d-zthdm7, narrowing d-p8jdqj; rejects practice I-6).
Ruling: the two-week age holds for transitive packages, through `ts/bunfig.toml` (d-svv7gv, narrowing d-4psbdv).
Ruling: carried tests that rewrote a decision or relayed a person's words do what the server allows (d-81ps01, narrowing d-bwb1tt; probe 8).
Alignment: plan 2 read at 61f87ad (`origin/server-store`), after its fix round: d-pmaw3a, d-vwsnz5, d-x6vaw8 (STORE-1 pending, option A followed), d-thvvzx, `FixedClock.sleep`, `attachmentTexts`, and `applyEvent`'s `heads` rule.
No value trade-off for the author, so no `questions.md`.
Recheck 1 (`plan-recheck-1.md`): 33 resolved; new 0B/2I/4M.
Fix round 2 by the planner (`plan-fix-2.md`): 6 fixed; `tests/test_wheel.py` back to `planned` in Task 7a; guide line 26 kept; d-j28rp0 and d-d0vca9 cited in place of d-pmaw3a and d-4zg8q3.
Fix round 3 by the planner (`plan-fix-2.md`, Round 3): N-5 fixed with the recheck's verified `recordFromDraft` arguments.
