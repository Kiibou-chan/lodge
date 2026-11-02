# Planner report: plan 3, the API, sign-in, and the command

Written incrementally; newest state last.

## Status

- Sources read: the brief, `CLAUDE.md`, the server design, plan 1 in full (Global Constraints, Calls made, the rest of build step 1, Settled for the later plans, Parity table), plan 1's ledger on `origin/server-core` (through Task 8a, d-xdqsmf, d-442r2f), the rulings the brief names (`lodge show --reasoning`), `src/lodge/cli`, `src/lodge/app`, `src/lodge/main.py`, and every file of `tests/e2e`, `tests/test_entry_point.py`, and `tests/test_wheel.py`.
- Plan 2 (`origin/server-store`) is not pushed yet; its brief says `app` keeps lodge 0.2's names in camelCase, so this plan plans against those.
- Probes run in a scratch copy of `ts/` (see `probes.md` in this folder).
