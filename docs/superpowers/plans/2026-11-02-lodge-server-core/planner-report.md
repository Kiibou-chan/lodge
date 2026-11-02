# Planner report: lodge server, build step 1

Status: in progress.

## Read
- Brief, `CLAUDE.md`, planner agent, the server design, the architecture options, the feasibility research, the viewer plan and its ledger, `lodge spec` (763 lines), `lodge guide`, `lodge waiting` (nothing waiting).

## Probes (in the scratchpad, copied into `probes/` of this folder)
- Bun 1.3.14: `bun test` runs TypeScript, `bun:sqlite` through Kysely 0.29.7 with a small adapter, a fetch handler called without a socket, and a passkey registration and sign-in with a software authenticator (@simplewebauthn/server 14.0.3): all pass.
- `bun build --compile` makes a working binary for a command and for a `bun:sqlite` program (about 95 MB).
- Node 26 cannot import `bun:sqlite`, and Bun cannot import `node:sqlite`: one runtime for the server, the tests, and the binaries.
- TypeScript 7.0.2 has no JavaScript API (`createSourceFile` undefined), so dependency-cruiser refuses it; TypeScript 6.0.3 works with dependency-cruiser 18.6.0.
- dependency-cruiser enforces allowed imports, front doors (with `#pkg` subpath imports), cycles, and no `node:`/`bun:` modules in core.
- The `yaml` package (2.9.1, failsafe schema) differs from PyYAML: tags are warnings, control characters pass, two documents parse, and deep nesting does not fail; the TypeScript `yamlio` must add these refusals.
- `@noble/hashes` SHA-256 gives the same 12-character prefix as Python's `hashlib` (`87428fc52280` for "a\n").

## Rulings recorded (scope process, work item the plan)
- d-26dx04 four plans; d-h1f596 `ts/` layout; d-03xx0a Bun; d-4psbdv the gate's tools and pinning; d-k5swcq the package table; d-88p8h9 port first, then change; d-smx3xf a record event holds path and text; d-g7ynw0 the parity table as a checked file; d-sry12f the API's shape; d-yayhct passkeys; d-j3z85y her decisions first; d-xk6qtn `scripts/check.sh` runs both gates; d-2jk0mw no move in step 1; d-g3mbmc differential run; d-4k9wcr Kysely.
- All dry-run first; the "looks related" feedback on each named no decision that a process ruling replaces or narrows.

## Plan shape (decided, before writing)
- Twelve tasks: 1 her decisions (coordinator), 2 setup (coordinator), 3 structure and parity, 4 text, YAML, ids, dates, settings, model, 5 record files, 6 threads and snapshots, 7 derive, 8 the check, 9 reads, 10 drafts and feedback, 11 apply, 12 differential run.
- Parity table generated from `git ls-files tests` (126 rows): 47 in this plan (40 core, 7 structure), the rest Plans 2 to 4, changed, or later.

## Written
- Plan `docs/superpowers/plans/2026-11-02-lodge-server-core.md` (12 tasks, the parity table of 126 rows, the later plans as one paragraph each, the API's shape and passkeys settled for them).
- Ledger `docs/superpowers/plans/2026-11-02-lodge-server-core-progress.md`.
- Rulings d-458jhp (YAML refusals) and d-7tdgs5 (Biome width) added after the first fifteen; 17 in all.
- Test imports forced a regrouping: builders need thread files and snapshots, so `test_fileformat_links.py` moves to Task 6; drafts move to Task 5 so `test_confirmation.py` runs in Task 7; five carried tests that call a later task's module are `test.todo` until that task (named in Tasks 6 to 10), and a file with a todo stays `planned`.
- Gate: `sh scripts/check.sh` green (1399 passed, `lodge check --gate` ok) with the records staged.

## Concerns for the reviewers
- The tool layer turned `\uXXXX` escapes in written text into raw characters twice; fixed in the plan and `probes.md` by script, and a scan finds no raw BMP specials left in the plan folder or the new records.
- Task 1's `where` for her quotes is not in any document; the coordinator takes it from its session.
- The structure rules for packages that do not exist yet (`store`, `git`, `api`, `cli`, `hook`) are written now (d-k5swcq) and tested on planted trees only.
- Bun's runtime and `bun test` were not run inside Codex's real sandbox; probe 13 simulates read-only home and temporary folders only.
