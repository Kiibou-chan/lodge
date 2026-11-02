# Progress: docs/superpowers/plans/2026-11-02-lodge-server-core.md

Branch `server-core`; authority for the build: the server design, approved by the author 2026-11-02 13:52 ("Approved").
Briefs, reports, and reviews: `docs/superpowers/plans/2026-11-02-lodge-server-core/`; probes in `probes.md` there, their sources in `probes/`.

Plan: written by the planner from `planner-brief.md`; build step 1 cut into four plans, this the first, the other three a paragraph each (d-26dx04).
Ruling: the TypeScript code lives in `ts/` (d-h1f596).
Ruling: Bun runs the server, the tests, and the binaries (d-03xx0a).
Ruling: the gate is Biome, strict `tsc` 6.0.3, dependency-cruiser, knip, and `bun test` with a structure test; versions pinned at least two weeks old (d-4psbdv).
Ruling: the packages and their allowed imports, `#name` front doors, `core` importing only `yaml` and `@noble/hashes` (d-k5swcq).
Ruling: port at parity first, then the design's changes (d-88p8h9).
Ruling: a record's event holds its path and file text (d-smx3xf).
Ruling: the parity table is `ts/tests/parity.json`, checked by a test (d-g7ynw0).
Ruling: the API's first shape (d-sry12f); passkeys (d-yayhct); Kysely (d-4k9wcr); all for the later plans.
Ruling: her answers behind the design go into lodge first, as Task 1 (d-j3z85y).
Ruling: `scripts/check.sh` runs both gates (d-xk6qtn).
Ruling: no project moves during build step 1 (d-2jk0mw).
Ruling: the core port ends with a differential run on this repository's records (d-g3mbmc).
Ruling: the YAML layer refuses what PyYAML refuses (d-458jhp); Biome's width is 100 (d-7tdgs5).
No value trade-off for the author, so no `questions.md`.
