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
