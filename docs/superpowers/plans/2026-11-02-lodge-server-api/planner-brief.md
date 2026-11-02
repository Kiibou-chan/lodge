# Planner brief: lodge server, build step 1, plan 3: the API, sign-in, and the command

Write plan 3 of build step 1 of the server design in `docs/superpowers/plans/2026-11-02-lodge-server-api.md`, with its ledger `docs/superpowers/plans/2026-11-02-lodge-server-api-progress.md` and this folder, in the worktree `/var/tmp/lodge-server-api` on branch `server-api`.
Plan 1 (`docs/superpowers/plans/2026-11-02-lodge-server-core.md`) is being built now on branch `server-core`; this plan starts from plan 1's finished core, and its build begins after plan 1 merges into this branch.

## Sources

- The authority: `docs/superpowers/specs/2026-11-02-lodge-server-design.md`, approved by the author 2026-11-02 13:52 ("Approved"); her answers behind it are author decisions (`uv run --frozen --quiet lodge search --by author`).
- Plan 1, which decides the layout, toolchain, gate, structure rules, parity table, and conventions this plan must follow: read its Global Constraints, "Calls made", "The rest of build step 1" (plan 3's paragraph is this plan's scope), "Settled for the later plans", and "Parity table" in full, and its ledger `docs/superpowers/plans/2026-11-02-lodge-server-core-progress.md` for the rulings made during its build so far.
- What plan 1's core exports: `ts/src/core/index.ts` and the parity table `ts/tests/parity.json` at this branch's commit; the rest of the core is the port at parity of `src/lodge/core` (Tasks 7a to 11 of plan 1), with the Python names in camelCase, so plan against those names.
- What records mean: `lodge spec`, read through lodge.
- The behaviour to carry over: `src/lodge` and `tests/`; lodge 0.2's tests are its specification.

## Scope

Plan 3's paragraph in plan 1: the `api` package (`POST /api/v1/<operation>` with JSON, d-sry12f, a `fetch` handler the tests call without a socket), bearer tokens for agents and passkeys and a session cookie for the one person (d-yayhct, probe 2); the `cli` package, the `lodge` command at parity with lodge 0.2 talking to the server, with the command tests carried (each against an in-process server), shipped as one binary through `bun build --compile`; and as its last task the minimal page (d-jtxwg3) for registering a passkey, signing in, agent tokens, and approving drafted decisions, imported into `api` as text.
It must settle how the command refuses `title_chars = 80.0` as lodge 0.2 does (`src/lodge/core/settings.py:55`; `Bun.TOML.parse` gives 5 for 5.0).
It ends when the carried command tests pass against the server, the compiled binary runs them, and the coordinator has registered, signed in, issued a token, and approved a drafted decision through the page in a real browser.
Plan 2 (the `store` and `app` packages) is being planned at the same time on branch `server-store`; plan against `app`'s port at parity of `src/lodge/app` (the `Lodge` operations, in camelCase) plus plan 2's model changes as plan 1's paragraph names them, and read plan 2's file with `git show origin/server-store:docs/superpowers/plans/2026-11-02-lodge-server-store.md` when it is pushed, to align names before you finish.

## Rulings made during plan 1's build that bind this plan

- d-mfskz3: the call rules refuse `Date` without `new` in `core` and `app`, and every file-writing form outside `git`.
- d-s5s2c3: `fetch` is allowed in `api`, `cli`, and `hook`, and refused in `store` and `git`.
- d-f18pz7: the TypeScript gate fails on Biome warnings.
- d-p48gr1, d-fbhdvf, d-g1hrmn, d-4m6m35: the YAML layer's listed differences from PyYAML, the decimal code point in the unreadable-character message, bare days ordering as midnight UTC, and ranks beyond a safe integer refused.
- d-v9mw2d: the server's entry point deletes `LOG_TOKENS` and `LOG_STREAM` from its environment before it serves, with a test, since the `yaml` package prints header text when either is set.
Read each with `uv run --frozen --quiet lodge show <id> --reasoning`.

## Builders and their sandbox

- Builders are Codex (`codex exec`), one task per brief, as in plan 1; Codex sees its brief, `CLAUDE.md`, and the repository, with no network, a read-only git index, and no sockets (plan 1, Global Constraints).
- A first setup task the coordinator runs outside the sandbox adds this plan's dependencies to `ts/package.json` and commits `ts/bun.lock`, each pinned to an exact version at least two weeks old (d-4psbdv); tests that need a socket are named, and the coordinator runs them.
- The coordinator runs `sh scripts/check.sh` outside the sandbox after every task, commits, and pushes; never `main`.
- Size tasks as plan 1 does after d-mfayy5: each one review's worth, about one Python module group, with its carried tests; and say in the plan which tasks can run in parallel, from the import graph.

## Rules

- Rule every which-option question yourself, as `.claude/agents/planner.md` says, with `lodge add` (scope `process`, `work_item` the plan path), dry run first; the ledger gives each decision's ID.
  Only a value trade-off goes to the author, in `docs/superpowers/plans/2026-11-02-lodge-server-api/questions.md`.
- Public repository: no personal paths, machine names, or other projects' specifics; fixtures are a made-up project.
- Plan Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; never write raw U+200B, U+2028, or U+2029 (check with `grep -nP '[\x{200B}\x{2028}\x{2029}]'`).
- Work only in `/var/tmp/lodge-server-api`; commit the plan, the ledger, this folder, and your `lodge/` records with explicit paths (`git -c user.name="Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Claude <noreply@anthropic.com>`), and push `server-api` to `origin` after each commit.
- Write your report incrementally to `docs/superpowers/plans/2026-11-02-lodge-server-api/planner-report.md`.
