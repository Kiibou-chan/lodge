# Final fix wave 2 report

Implemented B-1, A-1, A-2 and B-2 on `server-store`.
Read `task-final-check.md` and the reasoning of ruling d-8v05kt before implementation. No subagents or new dependencies were used.

- B-1: confirmation lists, area lists, `Shown.confirmable` and confirmation validation now use the reading person's name. Only that person's non-imported confirmations remove decisions from their list, following `confirmedByPeople`. Agent reads pass no person. Added app regressions in which Ada then Bo confirm a decision touching both people's decisions, and Bo confirms a decision awaiting Ada before Ada confirms it. Both confirmations publish and the final awaiting map is empty.
- A-1: restored the canonical revision guard. The stale-base test reads the live head after publishing and refuses both its decimal-suffix spelling and its leading-space spelling without writing events.
- A-2: `ask` and `reply` forward only `where`, `when` and `commit`, with the thread writer's existing defaults. A run-time reply supplied `{ close: true } as never` leaves its thread open.
- B-2: marked the concurrent-writers parity row `changed`.

## Verification

Before implementation, the targeted run had 21 passes and four failures: both new person scenarios exposed the second person's missing confirmation availability, the reply closed its thread, and the live decimal revision spelling published. A separate run put the leading-space spelling first and also observed it publishing incorrectly. Thus both revision spellings were seen failing before the guard was restored.

After implementation, the targeted run passed all 44 tests. The final `sh scripts/check-ts.sh` passed Biome, TypeScript, dependency-cruiser (201 modules), knip and the full suite: 1,302 passed, 2 todo, 0 failed. `git diff --check` passed. Every changed TypeScript module remains below 300 lines.

A-3 and B-3 remain the coordinator's responsibility, as specified in the brief. The pre-existing untracked `final-fix-2-codex.log` was left out of this commit.
