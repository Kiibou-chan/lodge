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
Task 5b: built by Codex (7c3ab8b), gate green outside the sandbox (419 TS tests); Biome warns 16 times without failing.
Task 5a: review 0 Blocking, 2 Important, 8 Minor (`task-5a-review.md`); writers agree with lodge 0.2 byte for byte on all 354 records under `lodge/`. Ruling: a rank beyond a safe integer is refused (d-4m6m35, C-1). Ruling: stored bytes decode as `surrogateescape` does, in the later plan that first decodes them (d-0q54zn, C-3; for the briefs of plans 2 and 4). Ruling: the gate fails on Biome warnings (d-f18pz7). Fix round 1 by Codex, with the parked Minors of Tasks 3 and 4.
Task 5a: fix round 1 by Codex: every finding fixed, ranks beyond a safe integer refused, Biome warnings 0 under `--error-on-warnings`, the Task 3 table pinned (`ts/tests/structure/table.test.ts`), and Task 4's N-1 listed; gate green (429 TS tests). For Task 6's brief: `fields.ts` exports `require` as a field reader, and a call named `require` is dynamic code to the structure rule, so it is imported as `requireField`.
Task 5a: recheck 1: 14 of 14 closed, the five whitespace mutants each killed, no new Blocking or Important (`task-5a-recheck-1.md`).
Task 5a: complete.
Task 5b: review 0 Blocking, 0 Important, 7 Minor (`task-5b-review.md`); 57 of 58 edge drafts agree with lodge 0.2 exactly, the 58th under d-p48gr1; a targeted mutation kills each carried text test (the review's table replaces the report's).
Parked (Task 5b, Minor): C-1, C-2, P-2, P-3, P-4, and D-1 to the next round touching `drafts.ts`, `fileformat.ts`, or their tests; P-1 (one `valueRepr` for `drafts.ts` and `fileformat.ts`) to Task 11, whose `apply.py` port needs it.
Task 5b: complete.
Task 6: built by Codex (a73a148), gate green outside the sandbox (480 TS tests, 2 `test.todo` for the review); a first Codex run hung on standard input from 17:54 to 18:32 and was rerun with stdin closed.
Author decision d-xdqsmf ("Yes, parallelise", 18:40): after Task 7a the remaining tasks run in lanes by the import graph (7b, 8a, and 11 at once; then 8b to 8c beside 9a, 9b, and 10), each in its own worktree merged into `server-core`; plans 2 to 4 are planned now on branches `server-store`, `server-api`, and `server-import`.
Task 7a: built by Codex (1660e45), gate green outside the sandbox (531 TS tests, 4 `test.todo`). Ruling: Task 11 runs in a lane now, its front-door test, `planned` check, and knip `entry` restore in a closing step after the lanes merge (d-442r2f).
Task 6: review 0 Blocking, 0 Important, 9 Minor (`task-6-review.md`); `writeThread` matches lodge 0.2 byte for byte on 1,207 threads built from the repository's records; the two `test.todo` are allowed, their files staying `planned` until Tasks 9a and 10.
Parked (Task 6, Minor): C-2 (`UNESCAPE` with the `m` flag passes all tests) and the other Minors to the next round touching `threads.ts` or `snapshot.ts`; C-3 (YAML refusals at another line than PyYAML's, not listed under d-p48gr1) to the final fix wave.
Task 6: complete.
Task 7b: built by Codex in lane `server-core-t7b` (48e4a51), gate green; merged into `server-core`.
Task 8a: built by Codex (b5f9f0b), gate green (595 TS tests after the 7b merge).
Task 8b: built by Codex (c3a811e), gate green.
Task 11: built by Codex in lane `server-core-t11` (854bebe); five apply tests lack their `checkChange` assertions, which wait for the closing step (`task-11-report.md`, lines 141 to 156); merged.
Task 9a: built by Codex in lane `server-core-t9a` (9e40182); `check-threads.test.ts` holds 9a's view test only, and its row stays `planned` for Task 8c's fifteen names; merged; gate green at 73ab440 (725 TS tests).
Task 7a: review 0 Blocking, 2 Important, 5 Minor (`task-7a-review.md`); `derive` matches lodge 0.2 on the repository's 222 decisions and 126 entries and on 6,000 random stores under three time zones. Fix round 1 by Codex in a lane (C-1, C-2, test-only, and the Minors).
Task 7a: fix round 1 by Codex in lane `server-core-t7afix` (5a24b52): C-1 and C-2 fixed with failing-first evidence, `derive-review.ts` folded back; gate green (726 TS tests); D-2 answered by ruling d-qe513h.
Task 7b and 8a: review (`task-7b-8a-review.md`): 7b 0 Blocking, 0 Important, 2 Minor; 8a 0 Blocking, 1 Important (D-1, `ok` a getter on a literal), 3 Minor; both cores agree on the store and 10 edited variants. Ruling: one comparator of order keys exported from `derive.ts`, and a `checkResult` constructor (d-qe513h). Fix round 1 by Codex in a lane on 8a-D-1, 7a-D-2, and the Minors of 7b and 8a.
Task 7b: complete (its Minors go into the 8a fix round).
Task 7a: recheck 1: 6 closed, 0 open, D-2 handed to the 8a fix round under d-qe513h (`task-7a-recheck-1.md`); the fix merges with the 8a fix lane.
Task 7a: complete.
Task 8c: built by Codex (5cace5c): the 51 carried names each fail against a targeted mutation; Task 11's five `checkChange` assertions and 9a's fifteen thread-check names restored; gate green.
Task 9b: built by Codex in lane `server-core-t9b` (c54d421); merged.
Task 10: built by Codex (616b872), gate green.
Task 8a: fix round 1 by Codex in lane `server-core-t8afix` (f344014), with 7a D-2 and 7b's Minors, under d-qe513h; the builder stopped on two tests importing `checkResult` past `#core`, and the coordinator exported it through `#core` (`CheckResult` is in `__all__`, so the closing front-door test allows it as its constructor); merged with the 7a fix at d625cf3, gate green (849 TS tests).
Task 11: closing step by Codex (d-442r2f): `front-door.test.ts` written and seen failing both ways, no plan 1 row `planned` (40 `planned` rows, all of plans 2 to 4), `ts/knip.json`'s `entry` back to Task 2's two patterns; gate green (851 TS tests).
Task 8c and 9b: review (`task-8c-9b-review.md`): 8c 0 Blocking, 0 Important, 1 Minor; 9b 0 Blocking, 0 Important, 3 Minor; Python and TypeScript agree on all 5,984 values over the repository's 350 records and an edge-text copy (`render_spec` byte for byte, search over 69 queries and 19 filters).
Parked (8c and 9b, Minor) for the final fix wave: 9b-C-1 (a carried render assertion weaker than Python's, `indexOf` against `text.index`), 9b-C-2, 9b-P-1, and 8c-P-1.
Task 8c: complete.
Task 9b: complete.
Task 12: built by Codex in lane `server-core-t12`, merged (9ac3208); the coordinator ran `sh scripts/differential.sh` outside the sandbox: "350 records, 10 areas, 0 threads, 0 problems, 112 queries, 360 rewritten files", "0 differences"; the store holds no threads, so the thread code rests on the carried tests and Task 6's comparison over 1,207 built threads.
Task 8b, 9a, and 11: review (`task-8b-9a-11-review.md`): 8b 0 Blocking, 0 Important, 3 Minor; 9a 0, 0, 2; 11 0, 0, 5; Python and TypeScript agree byte for byte over 2,745 `checkChange` cases, 921 level states, and 1,539 `applyDrafts` cases, the 44 PyYAML message differences under d-p48gr1; 32 of 50 targeted mutations fail a carried test, ten of the survivors caught by tests later tasks carry.
Parked (8b, 9a, and 11, Minor) for the final fix wave: 8b-P-1, 8b-P-2, 8b-D-1, 9a-P-1, 9a-D-1, 11-P-1, 11-P-2, 11-D-1 (a `catch` rule in `ts/tests/structure/calls.ts` for the `ValueError`-only catch at `apply.ts:163-164` and `apply-areas.ts:53-54`), 11-D-2, 11-D-3.
Ruling for the final fix wave: d-d0vca9 (replaces d-4zg8q3): the file-writing rule in `ts/tests/structure/calls.ts` reports `write`, `writev`, and their `Sync` forms only as functions imported from `fs`, and `.write`, `.writer`, `.delete` only on a `Bun.file(…)` call (plans 3 and 4 depend on it); also check each locked package's age against plan 3's `minimumReleaseAge` (d-svv7gv).
Task 8b: complete.
Task 9a: complete.
Task 11: complete.
Task 10, Task 12, and the 8a fix round: review (`task-10-12-8afix-review.md`): Task 10 0 Blocking, 0 Important, 2 Minor, Python and TypeScript `feedback` and `area_feedback` agreeing on 2,426 comparisons; Task 12 0, 0, 2; the 8a fix closes 8a-D-1, 8a-P-1, 8a-D-2, 7b-P-1, 7b-D-1, and 7a-D-2, leaves 8a-P-2 open, and adds 3 Minor.
Ruling: d-snrhjs (narrows d-qe513h and d-ca6wbw): `checkResult` is a constructor of `#core`'s front door; answers 8afix-D-1.
Parked (Tasks 10 and 12, the 8a fix round, Minor) for the final fix wave: 12-D-1 first (the differential never compares thread files, `differential.ts:65-73`, `differential_dump.py:65-76`, yet prints "N threads"; compare them, with a made-up store holding threads, or stop counting them), 12-D-2 (`bun test` needs `uv` on PATH), 10-P-1, 10-D-1 (21 surviving `feedback.ts` mutations, each surviving Python too), 8a-P-2 (the duplicate check 8 test at `check-state.test.ts:259`), 8afix-D-2, 8afix-P-1; noted, not raised: a read-only `TMPDIR` breaks the structure tests.
Task 10: complete.
Task 12: complete.
Task 8a: complete.
Final review (`final-review.md`, 782bb67): 0 Blocking, 3 Important, 3 Minor; ruling d-4vhjtt (narrows d-d0vca9): an `open` without a flag is a read (F-1).
Final fix wave, part A (structure rules) by Codex (`final-fix-a.md`, `final-fix-a-report.md`): d-d0vca9, d-4vhjtt, F-2, F-4, 11-D-1, 8afix-D-2, F-6 patterns; Task 3's `PACKAGES` Minor already pinned by `package_edges_match_ruling`.
Ruling: the new catch-guard, `ok`-literal, and portable-pattern rules apply to `core` only, not `app` or the adapters (`ts/tests/structure/core-rules.test.ts`) — plans 2 to 4 were reviewed without them, and catching an error to answer it or an `ok` field in an HTTP answer is ordinary in `api` and `cli` — cost if wrong: plan 2's `app` may use a non-portable pattern; its review catches it, and plan 2 may extend the rule to `app`. Gate green (889 TS tests).
Final fix wave, part B (parked Minors) by Codex (`final-fix-b.md`, `final-fix-b-report.md`): 12-D-1 (thread files in the differential, with a made-up store of two threads; a `writeThread` mutation now reports two differences), 12-D-2 (`differential.integration.ts` out of `bun test`'s default set, run by `scripts/differential.sh`), F-5, 10-D-1 (21 mutations killed), every Parked Minor, 11-P-2 and the `core` sort check; `apply-areas.ts` folded into `apply.ts` and `apply-state.ts` (11-P-1); a supplement for plan 2's writes port in `plan-2-writes-handoff.md` (11-D-2, `isStale`); the coordinator reverted Codex's edits to earlier task briefs and reports, which stay as history. Coordinator gate outside the sandbox: Python 1,399 passed, 924 TS tests, "354 records, 10 areas, 0 threads, 0 problems, 113 queries, 364 rewritten files", "0 differences".
F-3 (final review): the coordinator added `ts/bunfig.toml` with `minimumReleaseAge = 1209600` (d-svv7gv, moved here from plan 3's Task 1 so plans 2 to 4 build on a lock that holds it) and re-resolved `ts/bun.lock` from scratch: exactly four versions changed, `unbash` 6.0.3 to 6.0.0, `@types/node` 26.6.6 to 26.6.5, `tslib` 2.9.1 to 2.8.1, `@napi-rs/wasm-runtime` 1.2.6 to 1.2.5; gate green (Python 1,399 passed, 924 TS tests, 0 differences).
