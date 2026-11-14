# Task 12c report

Implemented held thread messages and approval through the existing publication transaction.

## Files

| File | Change |
| --- | --- |
| `ts/src/app/threads.ts` | Validate and check relayed messages before holding them; retain cleaned text, place, and minute; return provisional question IDs; publish approvals with their hold number; retry rejected publications and detect settled holds, including on the last attempt. |
| `ts/src/app/held.ts` | Approve messages through the shared thread writer as the authorised person, preserving place and minute. |
| `ts/src/app/results.ts` | Add `Written.awaits` and `Written.held`, defaulting both to null. |
| `ts/tests/app/ports.test.ts` | Assert the two new defaults. |
| `ts/tests/app/held-messages-support.ts` | Synthetic project with ada and bo, shared actors, and a reviewer question. |
| `ts/tests/app/held-messages.test.ts` | Relay holding, published waiting state, own messages, and refusal ordering. |
| `ts/tests/app/held-messages-approve.test.ts` | Message approval, approval-time question minting, decline, authorisation, closed threads, and settlement during the final retry. |
| `ts/tests/store/held-messages.test.ts` | SQLite approval writes one file event and one approval event through one publication call with the hold number. |

Waiting functions remain based on published messages.
No parity rows belong to these new plan-specific tests, so parity.json is unchanged.
No dependencies were added or installed.

## Test-first evidence

The initial app and store run, before implementation, ended with `272 pass`, `2 todo`, and `11 fail`.
The three existing refusal behaviours passed on arrival and were subsequently tested against targeted mutations, each reverted immediately.

| Test | First failure or targeted mutation |
| --- | --- |
| `an_agent_relaying_a_persons_words_is_held` | Expected held result with awaits and held; received published result without the fields. |
| `the_thread_still_waits_for_the_person` | Expected the question in forAuthor; received an empty list after immediate publication. |
| `a_persons_thread_still_waits_for_an_agent` | Expected last published text `Why?`; received `Yes.`. |
| `a_persons_own_message_is_published_at_once` | Expected null awaits and held; fields absent. |
| `the_person_approves_and_the_message_is_published` | `NotFound: nothing is held under number undefined`. |
| `a_relayed_question_mints_its_thread_at_approval` | Expected `held for approval`; received `published`. |
| `decline_publishes_nothing` | `NotFound: nothing is held under number undefined`. |
| `another_person_or_an_agent_cannot_approve_a_message` | Expected Forbidden; received NotFound because no message was held. |
| `approval_after_the_thread_closed_leaves_it_held` | Expected `q-111111 is closed`; received `nothing is held under number undefined`. |
| `default_filling_functions_fill_python_defaults` | Expected two null fields; received neither. |
| `a_relayed_message_lands_with_its_approval` | `NotFound: nothing is held under number undefined`. |
| `one_person_cannot_write_as_another` | Replaced other-person Forbidden with a message hold; test failed because the operation resolved. |
| `a_relay_without_where_is_refused_as_lodge_0_2_refuses_it` | Held the message before validating where; refusal still occurred, but the empty-holds assertion failed. |
| `a_relay_to_a_closed_thread_is_refused` | Held the message before the closed-thread refusal; the empty-holds assertion failed. |
| `a_hold_settled_on_the_last_attempt_is_not_found` | Expected NotFound; received Conflict with `other changes reached the store three times; nothing was written, so try again`. |

An additional mutation disabling where validation also made its refusal test fail.
All mutations were reverted.
No test is incompatible with TypeScript.
The SQLite fixture uses seeded's existing owner `author`; app fixtures use ada and bo as specified.

## Commands and results

| Command | Last result |
| --- | --- |
| `uv run --frozen --quiet lodge waiting` | Nothing waiting for either actor. |
| `bun test tests/app tests/store`, before implementation | `Ran 285 tests across 36 files`, 272 pass, 2 todo, 11 fail. |
| Same command, after implementation | `Ran 285 tests across 36 files`, 283 pass, 2 todo, 0 fail. |
| Individual refusal mutation runs | Each ended with 0 pass and 1 fail. |
| `sh scripts/check-ts.sh`, first run | Biome formatting errors; no implementation or rule changes needed. |
| `bun x biome check --write` on changed TypeScript files | Formatting fixed; subsequent check reported no fixes applied. |
| `sh scripts/check-ts.sh`, after formatting | 1284 pass, 2 todo, 0 fail; no dependency violations. |
| Final-retry test before its fix | 0 pass, 1 fail; Conflict instead of NotFound. |
| `bun test tests/app/held-messages-approve.test.ts`, after retry fix | 6 pass, 0 fail, 18 expect calls. |
| Final `sh scripts/check-ts.sh` | 1285 pass, 2 todo, 0 fail; Biome, TypeScript, dependency-cruiser, and knip pass. |

## Scope and concerns

No unresolved implementation concerns.
The two existing todo tests remain deferred to plan 3.
The parked Task 12b concerns, actor-wide held listing and duplicate holds on retried adds, remain untouched as instructed.
The coordinator's whole Python and TypeScript gate, merge, and ledger update are outside this task.
The brief's task-specific instruction to commit and push takes precedence over its repeated sandbox-era prohibition.
