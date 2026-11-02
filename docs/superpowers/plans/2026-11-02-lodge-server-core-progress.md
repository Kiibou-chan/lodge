# Progress: docs/superpowers/plans/2026-11-02-lodge-server-core.md

Branch `server-core`; authority for the build: the server design, approved by the author 2026-11-02 13:52 ("Approved").
Briefs, reports, and reviews: `docs/superpowers/plans/2026-11-02-lodge-server-core/`; probes in `probes.md` there, their sources in `probes/`.

Plan: written by the planner from `planner-brief.md`; build step 1 cut into four plans, this the first, the other three a paragraph each (d-26dx04).
Ruling: the TypeScript code lives in `ts/` (d-h1f596).
Ruling: Bun runs the server, the tests, the gate's tools (`bun --bun run check`), and the binaries (d-xph4ac, replacing d-03xx0a in fix round 1).
Ruling: the gate is Biome, strict `tsc` 6.0.3, dependency-cruiser, knip, and `bun test` with a structure test; versions pinned at least two weeks old (d-4psbdv); knip leaves the front doors to a test against `__all__` until plan 3 (d-s2rdn2, narrowing it).
Ruling: the packages and their allowed imports, `#name` front doors, `core` importing only `yaml` and `@noble/hashes` (d-k5swcq).
Ruling: port at parity first, then the design's changes (d-88p8h9).
Ruling: a record's event holds its path and file text (d-smx3xf).
Ruling: the parity table is `ts/tests/parity.json`, checked by a test (d-g7ynw0).
Ruling: the API's first shape (d-sry12f); passkeys (d-yayhct); Kysely (d-4k9wcr); all for the later plans.
Ruling: her answers behind the design go into lodge first, as Task 1 (d-j3z85y).
Ruling: `scripts/check.sh` runs both gates (d-xk6qtn).
Ruling: no project moves during build step 1 (d-2jk0mw).
Ruling: the core port ends with a differential run on this repository's records, the writers included (d-0qmd10, replacing d-g3mbmc).
Ruling: the YAML layer refuses what PyYAML refuses and keeps the text's key order (d-bkc7md, replacing d-458jhp); Biome's width is 100 (d-7tdgs5).
No value trade-off for the author, so no `questions.md`.
Plan: reviews correctness 0B/7I/13M and practice 0B/11I/9M (`plan-review-correctness.md`, `plan-review-practice.md`, ad1b09a).
Plan: fix round 1 by the planner, every finding answered in `plan-fix-1.md`, probes 15 to 20 added; `planner-brief.md` names "the plan's worktree" instead of its folder.
Ruling: the structure rules bind `ts/src`, and each adapter keeps its lodge 0.2 package's permissions, `store` only `bun:sqlite` (d-x6f9za).
Ruling: Tasks 5, 7, 8, and 9 split into 5a and 5b, 7a and 7b, 8a, 8b, and 8c, and 9a and 9b, numbers kept (d-mfayy5).
Ruling: plan 3's `api` serves a minimal page for passkeys, agent tokens, and approving drafted decisions, until step 3's interface (d-jtxwg3).
Still no value trade-off for the author.
Plan: recheck 1 closed the 40 findings and found 3 new Important and 6 Minor (`plan-recheck-1.md`, b5c8ad5).
Plan: fix round 2 by the planner, every new finding and preflight mismatch answered in `plan-fix-2.md`, probes 21 to 25 added.
Ruling: an export first read in a later task waits in `ts/knip.json`'s `entry` from the task that creates it to the task that reads it (d-tha8st).
Ruling: `#core` exports `__all__`, the default-filling functions, and `errors.ts`, `text.ts`, and `stamps.ts`; `quoted` and `unreadableChar` stay inside the package (d-hshapm, narrowing d-s2rdn2).
Ruling: a planted tree copies the dependencies and is cruised with `preserveSymlinks` (d-bxcave).
Ruling: `text.ts` exports `PY_SPACE_CLASS` for Python's `\s` (d-87kzys).
Still no value trade-off for the author.
