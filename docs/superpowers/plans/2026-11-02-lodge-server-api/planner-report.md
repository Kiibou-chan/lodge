# Planner report: plan 3, the API, sign-in, and the command

Written incrementally; newest state last.

## Status

- Sources read: the brief, `CLAUDE.md`, the server design, plan 1 in full (Global Constraints, Calls made, the rest of build step 1, Settled for the later plans, Parity table), plan 1's ledger on `origin/server-core` (through Task 8a, d-xdqsmf, d-442r2f), the rulings the brief names (`lodge show --reasoning`), `src/lodge/cli`, `src/lodge/app`, `src/lodge/main.py`, and every file of `tests/e2e`, `tests/test_entry_point.py`, and `tests/test_wheel.py`.
- Plan 2 (`origin/server-store`) is not pushed yet; its brief says `app` keeps lodge 0.2's names in camelCase, so this plan plans against those.
- Probes run in a scratch copy of `ts/` (see `probes.md` in this folder).
- Draft 1 under way: header, Global Constraints, Calls made (as RULE-* placeholders until the `lodge add` runs), Review Focus, lanes, coordinator checks, names consumed from plan 2, parity rows, and Tasks 1 to 3 written.
- Probe findings that shape the plan: `Bun.TOML.parse` gives 80 for `80.0` and accepts `[store` with no bracket, smol-toml with `integersAsBigInt` tells integers from floats (probe 1); `page.html` as a text import needs a cast, `page.js` a declaration (probe 3); a `Bun.spawnSync` of a client against a server in the same process never returns (probe 5).
- Plan 2 aligned against `7204ad3` of `origin/server-store` (its "Interfaces for plans 3 and 4"): async `Lodge` with options objects, `Actor` and held adds (`approve(seq)`, `decline`, `held`), `Forbidden` as 403, `Projects`, `openDatabase`, `SqliteProjects`; d-rp74dr's two thread tests are Task 7a's; hand edits go through `Store.publish` (d-pprhpz).
- Task 4 extends plan 2's packages: `Projects.create(project, owner, settings)`, `settings`, and `names`; `SqliteAccounts` over the accounts' events (project `""`), one migration after plan 2's.
- Twelve rulings recorded: d-p8jdqj, d-z1pncx, d-dfkqec, d-y0ppty, d-kt4jkq, d-3ywdhq (narrows d-sry12f), d-vfyex3 (narrows d-yayhct), d-rn4qzq, d-kky8qc, d-bwb1tt, d-5kskm3, d-djh40k (narrows d-s2rdn2); `lodge check` ok.
- Ledger written; no value trade-off, so no `questions.md`.

## Status: done

Ten tasks: 1 (coordinator setup), lanes A (2), B (3), C (4, 5, 6) in parallel, Task 4 after plan 2 merges; main line 7a, 7b, 8; lane D (9) beside 7a to 8, its browser check S3 after 8.

## Concerns

- A carried test whose seed is `decided_by: author` now gets a held add and approves it (d-znagqe, d-bwb1tt); the held add's output lines are new, so those tests assert more than lodge 0.2's and the parity rows say so; a reviewer should check that no assertion is weakened.
- Task 4 adds to plan 2's `Projects` port and schema; if plan 2 changes `create`'s signature or its migrations during its build, Task 4's brief follows the merged code.
- Task 9 (S3) needs a real browser with a passkey or a virtual authenticator; the coordinator runs it.
