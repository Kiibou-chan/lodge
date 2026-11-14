# Task 12b report

Implemented the application flow for a person's decisions drafted by another actor.

## Changes by file

| File | Change |
| --- | --- |
| `ts/src/app/awaits.ts` | Finds the other person named by new decisions, and refuses an add naming two other people. |
| `ts/src/app/held.ts` | Lists open holds, authorises approval and decline, cleans decline reasons, and delegates approval to the add attempts as the named person. |
| `ts/src/app/writes.ts` | Holds the entire checked request, reports provisional IDs and the awaited person, refreshes the hold before every approval attempt, and publishes with the approval number atomically. Refreshes once more after the final rejection so a settled hold raises `NotFound`. |
| `ts/src/app/write-attachments.ts` | Moves the existing attachment validation unchanged into its own module, keeping `writes.ts` comfortably below 300 lines. |
| `ts/src/app/results.ts` | Adds `AddOutcome.HELD`, `Approved`, and nullable `Added.awaits` and `Added.held` defaults. |
| `ts/src/app/lodge.ts` | Delegates `held`, `approve`, and `decline`. |
| `ts/tests/app/held-support.ts` | Shares synthetic decision drafts, two project owners, and wiring between the test files. |
| `ts/tests/app/held.test.ts` | Adds the seven holding and dry-run tests. |
| `ts/tests/app/held-approve.test.ts` | Adds the five required approval and decline tests, and one final-rejection race regression. |
| `ts/tests/app/ports.test.ts` | Carries the defaults test with both new fields explicitly expected as null. |
| This report | Records implementation, failing evidence, validation, and scope. |

`ts/src/app/index.ts` already exports all of `results.ts`, so `Approved` and the new result fields are available through `#app` without changing it.
No Python parity rows belong to this task: these are new server behaviours, with no Python source tests to flip.
No dependency was added or installed.
No earlier brief, report, review, Python implementation, Python test, or lockfile was changed.

## First failing evidence

The initial `cd ts && bun test tests/app` ran before implementation and finished with `171 pass`, `2 todo`, and `13 fail`.
Every required new test and the modified defaults test failed.

| Test | First failure or targeted mutation |
| --- | --- |
| `an_agents_add_of_a_persons_decision_is_held` | Expected the new outcome, which was initially undefined; received `published`. |
| `another_persons_add_is_held` | Expected `awaits: ada`; the result had no such field. |
| `a_dry_run_names_who_must_approve` | Expected `awaits: ada` and `held: null`; both fields were missing. |
| `a_held_add_is_not_current` | Expected `show` to reject; its promise resolved because the decision had been published. |
| `a_persons_own_decision_is_not_held` | Expected nullable approval fields; both fields were missing. |
| `an_add_for_two_people_is_refused` | Expected a rejected promise; the add resolved. |
| `a_failing_check_is_not_held` | `TypeError: lodge.held is not a function`. |
| `the_person_approves_and_it_becomes_current` | `TypeError: ada.approve is not a function`. |
| `another_person_or_an_agent_cannot_approve` | `TypeError: wired(...).approve is not a function`. |
| `approval_runs_the_check_again` | Initially `TypeError: ada.approve is not a function`. The final fixture retires a referenced entry between hold and approval and asserts check 6. Against a targeted mutation that bypassed failed checks only for approvals, it failed with expected `check failed`, received `published`. The mutation was reverted. |
| `a_declined_hold_cannot_be_approved` | `TypeError: ada.decline is not a function`. |
| `decline_needs_the_person_and_a_reason` | `TypeError: lodge.decline is not a function`. |
| `default_filling_functions_fill_python_defaults` | Expected `awaits: null` and `held: null`; received neither field. |
| `a_hold_settled_during_the_last_rejection_is_not_found` | Expected `nothing is held under number 1`; received the three-publication-rejections conflict message. Added the final hold refresh after observing this failure. |

The first approval recheck fixture wrote malformed text to a path the loader ignored.
It therefore incorrectly received `published` after implementation.
Replaced it with the required real intervening retirement and check 6 assertion, and proved that assertion against the targeted mutation above.

## Commands and outcomes

| Command | Last output or outcome |
| --- | --- |
| `cat docs/superpowers/plans/2026-11-02-lodge-server-store/task-12b-brief.md` | Read the requested brief first. |
| `cat CLAUDE.md` | Read repository instructions before implementation. |
| `uv run --frozen --quiet lodge waiting` | `waiting for the author` / `nothing`; the agent queue was also empty. |
| Repository searches, source reads, `git status --short`, and `git branch --show-current` | Confirmed existing hold machinery and branch `server-store`; the pre-existing untracked Codex log was left alone. |
| `cd ts && bun test tests/app` before implementation | `171 pass`, `2 todo`, `13 fail`; `Ran 186 tests across 20 files`. |
| `cd ts && bun test tests/app` after initial implementation | `183 pass`, `2 todo`, `1 fail`; the recheck fixture needed correction. |
| `cd ts && bun test tests/app/held*` after fixture correction | `12 pass`, `0 fail`; `Ran 12 tests across 2 files`. |
| `cd ts && bun test tests/app/held-approve.test.ts` with the new race regression | `12 pass`, `1 fail`; the helper was then still imported from a test file, so that command also registered the holding tests. |
| `cd ts && bunx --no-install biome check --write ...` on changed TypeScript files | Formatting and import organisation completed without warnings. |
| `cd ts && bunx --no-install tsc --noEmit -p .` | Exit 0, no output. |
| `cd ts && bun test tests/app` after the race fix and helper extraction | `185 pass`, `2 todo`, `0 fail`; `Ran 187 tests across 20 files`. |
| `cd ts && bun test tests/app/held-approve.test.ts --test-name-pattern approval_runs_the_check_again` against the targeted mutation | `0 pass`, `5 filtered out`, `1 fail`; expected `check failed`, received `published`. |
| `sh scripts/check-ts.sh` | Exit 0: Biome, TypeScript, dependency-cruiser, knip, and Bun tests passed; `1266 pass`, `2 todo`, `0 fail`; `Ran 1268 tests across 100 files`. |

The final validation command is `sh scripts/check-ts.sh`, rerun after writing this report.
The authorised commit includes explicit task paths and the Codex co-author trailer, followed by `git push origin server-store`.

## Limits and uncertainties

No required test is impossible in TypeScript.
The two existing command todos remain for plan 3, as the brief requires.
Approving a thread-message hold deliberately raises the specified temporary error until Task 12c.
The coordinator's whole Python and TypeScript gate and ledger update remain outside this task.
The brief's opening task-specific instruction to commit and push takes precedence over its repeated generic builder restriction against those actions.
No outstanding implementation uncertainty remains.
