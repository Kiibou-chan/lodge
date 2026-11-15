# Planner brief: lodge server, build step 1, plan 2: the events store and the operations

Write plan 2 of build step 1 of the server design in `docs/superpowers/plans/2026-11-02-lodge-server-store.md`, with its ledger `docs/superpowers/plans/2026-11-02-lodge-server-store-progress.md` and this folder, in the worktree `/var/tmp/lodge-server-store` on branch `server-store`.
Plan 1 (`docs/superpowers/plans/2026-11-02-lodge-server-core.md`) is being built now on branch `server-core`; this plan starts from plan 1's finished core, and its build begins after plan 1 merges into this branch.

## Sources

- The authority: `docs/superpowers/specs/2026-11-02-lodge-server-design.md`, approved by the author 2026-11-02 13:52 ("Approved"); her answers behind it are author decisions (`uv run --frozen --quiet lodge search --by author`).
- Plan 1, which decides the layout, toolchain, gate, structure rules, parity table, and conventions this plan must follow: read its Global Constraints, "Calls made", "The rest of build step 1" (plan 2's paragraph is this plan's scope), "Settled for the later plans", and "Parity table" in full, and its ledger `docs/superpowers/plans/2026-11-02-lodge-server-core-progress.md` for the rulings made during its build so far.
- What plan 1's core exports: `ts/src/core/index.ts` and the parity table `ts/tests/parity.json` at this branch's commit; the rest of the core is the port at parity of `src/lodge/core` (Tasks 7a to 11 of plan 1), with the Python names in camelCase, so plan against those names.
- What records mean: `lodge spec`, read through lodge.
- The behaviour to carry over: `src/lodge` and `tests/`; lodge 0.2's tests are its specification.

## Scope

Plan 2's paragraph in plan 1: the `store` package (one append-only SQLite events table through Kysely over `bun:sqlite`, d-4k9wcr, a record's event holding its path and file text, d-smx3xf, current state and query tables rebuilt from the events); `app` ported from `src/lodge/app` at parity over a storage port whose current and published states are one state (design line 79), with the app tests carried and `test_reads_published.py` and `test_writes_retry.py` changed as the parity table says; then, as tasks of their own with new tests (d-88p8h9), the design's model changes: `decided_by` names a person or an agent role, a person's decision drafted by a session waits for that person's approval (SRV-2, design line 75), a review flag on a person's decision clears only when that person confirms (design line 77), and the check runs on every write and refuses with `lodge add`'s feedback (design line 79).
It ends when the carried app tests and the new model tests pass in process, with no HTTP.
Plans 3 and 4 are being planned at the same time from `app`'s port at parity; keep `app`'s public names those of `src/lodge/app` in camelCase, and name every addition in the plan's Interfaces so they can read it.

## Rulings made during plan 1's build that bind this plan

- d-mfskz3: the call rules refuse `Date` without `new` in `core` and `app`, and every file-writing form outside `git`.
- d-s5s2c3: `fetch` is allowed in `api`, `cli`, and `hook`, and refused in `store` and `git`.
- d-f18pz7: the TypeScript gate fails on Biome warnings.
- d-p48gr1, d-fbhdvf, d-g1hrmn, d-4m6m35: the YAML layer's listed differences from PyYAML, the decimal code point in the unreadable-character message, bare days ordering as midnight UTC, and ranks beyond a safe integer refused.
- d-0q54zn: the first TypeScript code that decodes a stored file's bytes maps each byte b of an invalid UTF-8 sequence to U+DC00 + b, as Python's `surrogateescape` does, and `contentHash` encodes U+DC80 to U+DCFF back to that byte; if this plan's store decodes bytes, it is this plan's.
Read each with `uv run --frozen --quiet lodge show <id> --reasoning`.

## Builders and their sandbox

- Builders are Codex (`codex exec`), one task per brief, as in plan 1; Codex sees its brief, `CLAUDE.md`, and the repository, with no network, a read-only git index, and no sockets (plan 1, Global Constraints).
- A first setup task the coordinator runs outside the sandbox adds this plan's dependencies to `ts/package.json` and commits `ts/bun.lock`, each pinned to an exact version at least two weeks old (d-4psbdv); tests that need a socket are named, and the coordinator runs them.
- The coordinator runs `sh scripts/check.sh` outside the sandbox after every task, commits, and pushes; never `main`.
- Size tasks as plan 1 does after d-mfayy5: each one review's worth, about one Python module group, with its carried tests; and say in the plan which tasks can run in parallel, from the import graph.

## Rules

- Rule every which-option question yourself, as `.claude/agents/planner.md` says, with `lodge add` (scope `process`, `work_item` the plan path), dry run first; the ledger gives each decision's ID.
  Only a value trade-off goes to the author, in `docs/superpowers/plans/2026-11-02-lodge-server-store/questions.md`.
- Public repository: no personal paths, machine names, or other projects' specifics; fixtures are a made-up project.
- Plan Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; never write raw U+200B, U+2028, or U+2029 (check with `grep -nP '[\x{200B}\x{2028}\x{2029}]'`).
- Work only in `/var/tmp/lodge-server-store`; commit the plan, the ledger, this folder, and your `lodge/` records with explicit paths (`git -c user.name="Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Claude <noreply@anthropic.com>`), and push `server-store` to `origin` after each commit.
- Write your report incrementally to `docs/superpowers/plans/2026-11-02-lodge-server-store/planner-report.md`.
