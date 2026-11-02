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
Plan: recheck 2 closed 8 of 9 and narrowed N2 to N2-r, with 3 new Minor (`plan-recheck-2.md`, 2e7acf6).
Plan: fix round 3 by the planner, N2-r, m-a, m-b, m-c, and the preflight mismatches answered in `plan-fix-3.md`, probes 26 and 27 added.
Ruling: a dataclass gets a default-filling function only where a Python call leaves a default out; `Draft` and `Snapshot` get none, and `#core` exports nine (d-ca6wbw, narrowing d-hshapm).
Still no value trade-off for the author.
Plan: recheck 3 by the coordinator on 2e7acf6..6e9c0f7: N2-r closed, every `Snapshot(` call passes all seven fields (`tests/core/builders.py:94`, `src/lodge/core/snapshot.py:70`) and the only core `Draft(` call passes all five (`src/lodge/core/drafts.py:45`; `cli/parser.py:216` is the command's own `Draft`), the front-door test names the nine (plan line 716), and no U+200B, U+2028, or U+2029 is in the plan or ledger; 0 Blocking, 0 Important open.
Preflight: the tables of `plan-recheck-1.md` and `plan-recheck-2.md`, with their mismatch rows answered in `plan-fix-2.md` and `plan-fix-3.md`.
Task 1: the author's eight answers behind the server design, as author decisions: d-8kasej (ARCH-1), d-b1yjpp (ARCH-2), d-d3js00 (ARCH-3), d-khew4n (export), d-ffk7wy (ARCH-4), d-wc9wt2 (SRV-1), d-zzfmj2 (SRV-2), d-5ps72w (approved); where "lodge build session", the session's name in the earlier author records, minutes checked against the transcript; SRV-2 quotes her whole answer; every "looks related" answered no (d-j3z85y); lodge check ok. Task 1: complete.
Task 2: toolchain and gate by the coordinator; `bun install` then `--frozen-lockfile` clean, Biome formatted `package.json`; Biome 2.5.15 deprecates `rules.recommended`, so `biome.json` uses `"preset": "recommended"` (`biome migrate` wrote `"none"`, corrected, and a `debugger` probe fails the lint); knip reported no unused dev dependency, so `ignoreDependencies` holds only `yaml` and `@noble/hashes`; check-ts exit 0, without Bun "bun is not installed" exit 2, check.sh exit 0, no range in `package.json`. Task 2: complete.
Task 3: built by Codex (471b8ca), gate green outside the sandbox (143 TS tests); the builder added a `test:structure` script to `ts/package.json`, for the review.
Task 3: review 1 Blocking, 5 Important, 9 Minor (`task-3-review.md`); parity.json matches the plan on all 126 rows. Ruling: I4 and I5 conflict with the plan's lists, and the rules they carry win (d-mfskz3). Ruling: `fetch` allowed in `api`, `cli`, and `hook` only (d-s5s2c3, m1). Fix round 1 by Codex on every finding.
Task 4: built by Codex (bba4a92), gate green outside the sandbox (225 TS tests); the builder lists the known differences (digits, casefold, repr, the nesting bound) in `task-4-report.md`.
Task 3: fix round 1 by Codex (30557fe): every finding fixed, `allowed-imports` and `front-door` built from `table.ts`, gate green (259 TS tests); recheck 1: 15 of 15 closed, no new Blocking or Important (`task-3-recheck-1.md`).
Parked (Task 3, Minor): config and test both read `PACKAGES`, so a wrong edge in `table.ts` passes; a test pinning the table to d-k5swcq goes to the next round touching `ts/tests/structure/`.
Task 3: complete.
Task 4: review 1 Blocking, 6 Important, 8 Minor (`task-4-review.md`); 29 mutations each turned a test red, and the stated code-point differences hold exactly. Ruling: the YAML layer keeps the enumerated refusals and lists its other differences from PyYAML (d-p48gr1, narrowing d-bkc7md, C-2). Ruling: the unreadable-character message names the decimal code point (d-fbhdvf, C-3). Ruling: plan 3's entry point clears `LOG_TOKENS` and `LOG_STREAM` (d-v9mw2d, C-6; for plan 3's brief). Ruling: a bare day orders as midnight UTC (d-g1hrmn, D-1). Fix round 1 by Codex after Task 5a.
Task 5a: built by Codex (1d57ad1), gate green outside the sandbox (356 TS tests); the builder flags `contentHash` of a lone surrogate and ranks beyond a number's precision, for the review.
Task 4: fix round 1 by Codex (77993a1), gate green (379 TS tests); recheck running.
Task 4: recheck 1: 15 of 15 closed, no new Blocking or Important (`task-4-recheck-1.md`); N-1 (Minor): `fileformat.test.ts:160` feeds an escaped newline where Python feeds a literal one, a listed YAML difference under d-p48gr1; parked for Task 5a's fix round to list it among that file's tests that cannot hold.
Task 4: complete.
