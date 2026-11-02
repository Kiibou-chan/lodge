# Planner brief: lodge server, build step 1

Write the implementation plan for build step 1 of the server design, in `docs/superpowers/plans/2026-11-02-lodge-server-core.md`, with its ledger `docs/superpowers/plans/2026-11-02-lodge-server-core-progress.md`, in the plan's worktree on branch `server-core`.

## Sources

- The authority for this plan: `docs/superpowers/specs/2026-11-02-lodge-server-design.md`, approved by the author 2026-11-02 13:52 ("Approved").
  Build step 1 is its section "Build order", item 1: the core in TypeScript (records, the check, threads, confirmations, the events table, the API, and the `lodge` command at parity with lodge 0.2, its tests carried over), the importer, export to git, and passkeys for one person.
- What records mean: `lodge spec`, read through lodge, as `CLAUDE.md` says; the server design changes where records live and the points in its section "The model", nothing else.
- Background: `docs/superpowers/specs/2026-11-02-lodge-server-architecture-options.md`, `docs/superpowers/specs/2026-11-01-lodge-server-needs.md`, and `docs/research/2026-11-02-server-*.md`.
- The behaviour to carry over: `src/lodge` and `tests/` (126 test files); lodge 0.2's tests are the specification of that behaviour.
- The format and the build conventions: `docs/superpowers/plans/done/2026-10-31-lodge-viewer.md` and its ledger; match them.

## What the plan must settle

1. Scope: all of build step 1, cut into stages that each end in working, tested software; if you judge it should be several plans, say so, cut it, and write the first plan in full and the rest as one paragraph each.
2. Layout: where the TypeScript lives in this repository while lodge 0.2's Python keeps working until a project has moved (design, "Moving from lodge 0.2").
3. The toolchain and the gate (the TypeScript `scripts/check.sh` equivalent): strict `tsc`, a formatter and linter, a dead-code check in place of Vulture, the test runner, and the structure rules of `tests/structure_rules.py` carried over (allowed imports, front doors, no cycles, modules of at most 300 lines, `core` pure, I/O confined), enforced by a dependency checker over the import graph (design, "Constraints").
   Available here: Bun 1.3.14, Node 26.10.0, npm 12.2.0.
   Settle Bun or Node for the server and tests by a probe, given that the runner and the command ship through `bun build --compile` (ARCH-2).
4. A parity table: each Python test file mapped to its TypeScript counterpart, or marked as changed by the design (with the design line) or out of scope for step 1.
5. The API's first shape, enough for the command, the importer, and the tests; the rest of the API is later steps.
6. Passkeys for one person, testable without a browser.

## Builders and their sandbox

- Builders are Codex (`codex exec`), one task per brief, as in the viewer plan; Codex sees its brief, `CLAUDE.md`, and the repository.
- In Codex's sandbox git's index is read-only and sockets are refused (viewer plan, "Global Constraints"); assume no network as well.
  So: a first setup task the coordinator runs outside the sandbox installs every dependency and commits the lockfile; server tests call the request handler directly without binding a socket; tests that need a socket are named, and the coordinator runs them.
- The coordinator (this session) runs the gate outside the sandbox after every task, commits, and pushes `server-core`; never `main`.

## Rules

- Rule every which-option question yourself, as `.claude/agents/planner.md` says, with `lodge add` (scope `process`, `work_item` the plan path), dry run first; the ledger gives each decision's ID.
  Only a value trade-off goes to the author, in `docs/superpowers/plans/2026-11-02-lodge-server-core/questions.md`.
- Public repository: no personal paths, machine names, or other projects' specifics; fixtures are a made-up project.
- Plan Markdown: British English, no em-dashes, the Oxford comma, one sentence per line.
- Commit the plan, the ledger, and this folder with explicit paths, and push `server-core` after each commit.
- Write your report incrementally to `docs/superpowers/plans/2026-11-02-lodge-server-core/planner-report.md`.
