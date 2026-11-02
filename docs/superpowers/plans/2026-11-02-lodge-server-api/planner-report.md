# Planner report: plan 3, the API, sign-in, and the command

Written incrementally; newest state last.

## Status

- Sources read: the brief, `CLAUDE.md`, the server design, plan 1 in full (Global Constraints, Calls made, the rest of build step 1, Settled for the later plans, Parity table), plan 1's ledger on `origin/server-core` (through Task 8a, d-xdqsmf, d-442r2f), the rulings the brief names (`lodge show --reasoning`), `src/lodge/cli`, `src/lodge/app`, `src/lodge/main.py`, and every file of `tests/e2e`, `tests/test_entry_point.py`, and `tests/test_wheel.py`.
- Plan 2 (`origin/server-store`) is not pushed yet; its brief says `app` keeps lodge 0.2's names in camelCase, so this plan plans against those.
- Probes run in a scratch copy of `ts/` (see `probes.md` in this folder).
- Draft 1 under way: header, Global Constraints, Calls made (as RULE-* placeholders until the `lodge add` runs), Review Focus, lanes, coordinator checks, names consumed from plan 2, parity rows, and Tasks 1 to 3 written.
- Probe findings that shape the plan: `Bun.TOML.parse` gives 80 for `80.0` and accepts `[store` with no bracket, smol-toml with `integersAsBigInt` tells integers from floats (probe 1); `page.html` as a text import needs a cast, `page.js` a declaration (probe 3); a `Bun.spawnSync` of a client against a server in the same process never returns (probe 5).
