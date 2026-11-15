# Final check, fix wave 2

Worktree `/var/tmp/lodge-server-store`, branch `server-store`.
Read `task-final-check.md` in this folder; fix the findings below, test-first (each new test seen failing before its code), and keep every existing test passing.
Do not dispatch subagents.

1. B-1 (Important), ruling d-8v05kt (read it with `uv run --frozen --quiet lodge show d-8v05kt --reasoning`): give `confirmableIds` (`ts/src/core/confirmation.ts:16-25`), `behindArea`, `Shown.confirmable` (`ts/src/app/reads.ts:57`), and the expected ids in `ts/src/app/confirm.ts:40` the person; drop a decision only when a confirmation by that person names it (the reading `confirmedByPeople` of `ts/src/core/derive-flags.ts:30`). Pass `w.actor.name` from `confirm.ts` and the reading actor's name from `reads.ts`.
   Tests in `ts/tests/app/people.test.ts` through `Lodge.confirm`: (a) two people, `d-bbbbbb` touching `ada`'s and `bo`'s decisions, `ada` confirms then `bo` confirms, both `published`, `derive(...).awaiting` empty at the end; (b) one decision awaiting `ada`, `bo` confirms first, `ada` can still confirm.
2. A-1: restore the guard in `ts/src/store/sqlite-store.ts` as `if (base.rev === null || String(Number(base.rev)) !== base.rev) return PublishOutcome.REJECTED;`; add to the stale-base test one case spelling the live head as `${rev}.0` (and `" 2"`-style), read after the first publish.
3. A-2: in `Lodge.ask` and `Lodge.reply` (`ts/src/app/lodge.ts:73-89`) pass `{ where, when, commit }` only; add a run-time test that a `reply` given `{ close: true } as never` leaves the thread open.
4. B-2: set the concurrent-writers row in `ts/tests/parity.json` (about line 565) to `"status": "changed"`.

A-3 and B-3 are the coordinator's.
Hard rules: modules at most 300 lines, British English, no em-dashes, no new dependency, run `sh scripts/check-ts.sh`.
Write `final-fix-2-report.md` in this folder, commit with explicit paths (trailer `Co-Authored-By: Codex <noreply@openai.com>`), and push `server-store`.
