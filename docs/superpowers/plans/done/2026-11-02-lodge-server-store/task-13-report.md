# Task 13 report

Implemented review flags per person.

## Files

- `ts/src/core/derive-flags.ts`: moved flag derivation into an internal module and applied the existing imported, undone, preceding-change, and clearing rules separately for each person, collecting outstanding names in code-point order.
- `ts/src/core/derive.ts`: added `Derived.awaiting`, retained `awaitingAuthor` as its keys, and delegated review derivation and the flagged decisions' preceding-edit lookup.
- `ts/src/core/people.ts`: added shared person-list wording with the Oxford comma and the legacy `the author` special case.
- `ts/src/core/views.ts`: named outstanding people on decisions and touched records, and grouped confirmation IDs by person in code-point order.
- `ts/src/core/feedback.ts`: named the outstanding people while preserving lodge 0.2's author wording.
- `ts/src/core/fileformat.ts` and `confirmation.ts`: exported and reused `PLAIN`, removing the inline duplicate requested by the coordinator.
- `ts/tests/core/flags-people.test.ts`: added all eight required tests.

## Test-first evidence

Ran `cd ts && bun test tests/core` before implementation.
The last lines were `753 pass`, `8 fail`, and `Ran 761 tests across 58 files.`
All existing core tests passed.
The eight new tests failed as follows.

| Test | First failing output |
| --- | --- |
| `flag_waits_for_the_person_whose_decision_it_touches` | Expected a map containing the agent decision and `["ada"]`; received `undefined`. |
| `another_persons_confirmation_leaves_it` | Expected a set containing the agent decision; received `Set {}`. |
| `that_persons_confirmation_clears_it` | Expected `Map {}`; received `undefined`. |
| `that_persons_replacement_clears_it` | Expected `Map {}`; received `undefined`. |
| `touching_two_people_waits_for_both` | `TypeError: undefined is not an object (evaluating 'derive(s).awaiting.get')`. |
| `a_confirmed_agent_text_counts_for_its_confirmer` | `TypeError: undefined is not an object (evaluating 'derive(s).awaiting.get')`. |
| `feedback_names_who_it_waits_for` | Expected `this decision will wait for ada: it takes effect at once, and a later decision of ada that confirms or replaces it clears the flag`; received the author wording. |
| `confirmed_by_names_each_person` | Expected confirmations grouped as `confirmed by ada (...) and bo (...)`; received `confirmed by the author (...)`. |

No Python tests were newly carried by Task 13, and no parity rows belong to this task, so `ts/tests/parity.json` is unchanged.
No required test is impossible in TypeScript.
Existing tests were retained unchanged and run throughout.

## Commands and results

- `cat docs/superpowers/plans/2026-11-02-lodge-server-store/task-13-brief.md`, followed by `cat CLAUDE.md`: read the requirements and repository instructions.
- `uv run --frozen --quiet lodge waiting`: both agent and author queues reported `nothing`.
- Repository reads, `rg`, `git status --short`, `git branch --show-current`, and `git diff --check`: inspected the implementation and verified branch `server-store-c`, with no whitespace errors.
- `cd ts && bun test tests/core` before implementation: `753 pass`, `8 fail`.
- `cd ts && bun test tests/core` after implementation: `761 pass`, `0 fail`.
- `cd ts && bunx biome check --write` on the eight touched TypeScript files: `Checked 8 files`, formatting fixed in six.
- First `sh scripts/check-ts.sh`: dependency check rejected a test import through `src/core/settings.ts`; changed it to the `#core` front door.
- Second `sh scripts/check-ts.sh`: TypeScript reported `Cannot find name 'lengthGuidance'`; corrected the front-door import.
- `cd ts && bunx biome check --write tests/core/flags-people.test.ts`: `Checked 1 file`, no fixes applied.
- Final `sh scripts/check-ts.sh`: exit 0, no dependency violations, `1032 pass`, `0 fail`, `2529 expect() calls`, `Ran 1032 tests across 73 files.`

## Scope and concerns

No unresolved implementation concerns.
The task-specific instruction to commit and push `server-store-c` takes precedence over the repeated global builder restriction against doing so.
The whole Python gate and differential run remain the coordinator's step, as the brief specifies.
The pre-existing untracked `task-13-codex.log` is excluded from the commit.
