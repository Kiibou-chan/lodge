# Plan fix round 5: plan 2 against plan 1's final fix wave

Planner, fix round 5, on `server-store` from 0244e79, bringing the plan's text to plan 1 as it stands at `origin/server-core` 4f5d5fb (its final fix wave and `plan-2-writes-handoff.md`).
Status: done.

## Changes

- Re-pinned: the Global Constraints name plan 1's final state as 4f5d5fb, and every `ts/` line this plan cites is at that commit (Tasks 10 and 13 cite it for `derive.ts`, 238 lines, `isAuthor` at line 153).
- `apply-areas.ts` no longer exists: Task 10 now names `ts/src/core/apply-state.ts`, whose `restored` builds the after-state with `tree({ … })` at line 68; `differential.ts`'s `Tree` literal is at line 43.
- `isStale`: Task 3 ports `any(isinstance(p, StaleBase) for p in problems)` (`src/lodge/app/writes.py:174`) as plan 1's marker test, `"stale" in p && p.stale === true` (`ts/tests/core/applying.ts:83-85`), written inline in `writes.ts`, with no new `#core` export.
- `checkResult` (d-snrhjs): a Global Constraint, and Tasks 3 (`state.ts`, `src/lodge/app/state.py:69`) and 4 (`reads.ts`, `src/lodge/app/reads.py:96`), build every check result through `checkResult` of `#core`.
- The new rules in `core` only (`ts/tests/structure/calls.ts` and `guards.ts`): a Global Constraint states them and names the tasks that edit `ts/src/core`, Tasks 7a, 10, and 13 (a guarded `catch`, no `ok` key outside `check-state.ts`, regular expressions with `u` and without `m` or Python shorthands, and no `sort()` or `toSorted()` without a comparator); `app` and `store` are not bound by them.
- `ts/bunfig.toml` (`minimumReleaseAge = 1209600`, fourteen days): Task 1 says Kysely 0.29.7 resolves under it, `npm view kysely@0.29.7 time` giving `2026-10-17T15:49:31.265Z`, 16 days before 2026-11-02, and 0.29.8 (`2026-11-01T02:05:55.068Z`) being too new.

## For plans 3 and 4

Nothing they consume from plan 2 changed.
