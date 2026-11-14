# Task 11 report

Implemented people in the operations and the store.

## Changes per file

| File | Change |
| --- | --- |
| `ts/src/app/errors.ts` | Added `Forbidden`, inheriting exit code 2 and the public export through the existing wildcard in `index.ts`. |
| `ts/src/app/state.ts` | Required an actor in `Wiring`. |
| `ts/src/app/lodge.ts` | Required the fifth constructor argument and passed it into the wiring. |
| `ts/src/app/confirm.ts` | Refused agents and people outside the owners, and passed the actor's name to `confirmationDraft`. |
| `ts/src/app/threads.ts` | Used snapshot people for message validation, serialisation, and waiting classification, refused impersonation by another person, and preserved people in the checked after-state. |
| `ts/src/app/writes.ts` | Preserved current people in the checked after-state. |
| `ts/src/store/read-tree.ts` | Read project owners into tree people within the same transaction. |
| `ts/tests/app/fakes.ts` | Added the `people` option, defaulting to author, and preserved it in current, published, and gate trees. |
| `ts/tests/app/support.ts` | Defaulted the actor to `person("author")` and passed it to `Lodge`. |
| `ts/tests/app/people.test.ts` | Added the eight requested operation tests, including both actor refusal cases. |
| `ts/tests/store/people.test.ts` | Added owner membership and stale revision tests. |
| `ts/tests/app/confirm.test.ts` | Added the three parked confirmation edge tests. |
| `ts/tests/structure/calls.ts` | Rejected calls of `isAuthor`, `parseThread`, or `writeThread` outside core with fewer than two arguments. |
| `ts/tests/structure/people-calls.test.ts` | Tested all three names with zero arguments, one argument, a qualified receiver, explicit people, and the core exemption. |

No direct `new Lodge` existed outside `wired`, so changing that helper covered the store tests too.
No parity rows belong to this task: these are new server people tests, and existing Python parity rows retain their earlier task attribution.
No Python test cannot hold in TypeScript as a result of this task.

## Test-first evidence

The first combined app/store run failed with 221 pass, 2 todo, 2 fail, and 1 error.
The error was the missing `Forbidden` export, after which adding its declaration let every new operation test execute and fail before the implementation.

| Test or named group | First failing output or targeted mutation |
| --- | --- |
| `confirm_writes_the_persons_decision` | Expected `ada`, received `author`. |
| `an_agent_cannot_confirm` | Initially the agent case of `actor_cannot_confirm`: expected rejection, received a resolved promise. |
| `a_person_not_among_the_people_cannot_confirm` | Initially the cy case of `actor_cannot_confirm`: expected rejection, received a resolved promise. |
| `a_persons_message_needs_where` | Expected rejection, received a resolved promise. |
| `author_is_a_role_where_no_person_is_author` | Expected `name a person of the project exactly, or use your own role`, received the old author where refusal. |
| `a_person_writes_only_as_themselves` | The allowed ada setup failed with `where and when are for messages by author`. |
| `a_persons_question_waits_for_an_agent` | Ada's question failed with `where and when are for messages by author`. |
| `an_agent_edit_of_a_persons_entry_waits` | Expected the feedback predicate to be true, received false. |
| `owners_are_the_people_of_the_tree` | Expected ada in both trees, received the default author set. |
| `a_new_member_moves_the_rev` | Passed existing code first; mutation omitted head revision updates for member events in `events.ts`: expected `rejected`, received `published`; 0 pass, 1 fail. |
| `people_required_outside_core`, each of the three function names | Before adding the rule, expected a violation, received an empty array; 0 pass, 3 fail. |
| `empty_confirmation_ids_are_stale` | Mutation removed `!expected.length` from the stale guard: received the unstorable-character error instead of `StaleList`; 0 pass, 1 fail. |
| `same_length_wrong_area_subset_is_stale` | Mutation replaced the subset predicate with false: expected rejection, received a resolved promise; 0 pass, 1 fail. |
| `confirmation_defaults_to_no_commit` | Mutation changed the default commit option to true: expected null, received a committed result; 0 pass, 1 fail. |

All targeted mutations were reverted immediately after their individual runs.
The impersonation test uses deferred operations to attach rejection assertions before starting each asynchronous call.
The two actor confirmation cases were split into their requested individual titles after the initial failing parametrised run.
Existing tests were retained without reducing assertions.

## Commands and outcomes

| Command | Outcome or last lines |
| --- | --- |
| `uv run --frozen --quiet lodge waiting` | Nothing waiting for an agent or the author. |
| `uv run --frozen --quiet lodge show d-wz7fc2 --reasoning` | Read the recorded requirement for the people call structure check. |
| `cd ts && bun test tests/app tests/store` before implementation | 221 pass, 2 todo, 2 fail, 1 error. |
| `cd ts && bun test tests/app/people.test.ts` after declaring `Forbidden` only | 0 pass, 8 fail. |
| `cd ts && bun test tests/structure/people-calls.test.ts` before the rule | 0 pass, 3 fail. |
| Targeted mutation runs using `bun test <file> --test-name-pattern <title>` | Each of the four mutations produced 0 pass, 1 fail. |
| `rg -n 'writeThread\(|isAuthor\(|parseThread\(' ts/src/app` | The sole call is `writeThread(thread, s.people)` in `threads.ts`. |
| `cd ts && bunx biome check --write` on changed TypeScript files | Formatting applied; subsequent checks found no fixes needed. |
| First `sh scripts/check-ts.sh` | TypeScript rejected readonly arrays passed to mutable-array assertion overloads in two new assertions; fixed by spreading expected IDs. |
| `git diff --check` | No output, exit 0. |
| Final `sh scripts/check-ts.sh` | Exit 0; Biome, TypeScript, dependency-cruiser, knip, and Bun tests passed; 1234 pass, 2 todo, 0 fail, 3136 assertions, 1236 tests across 96 files. |

## Scope and concerns

No unresolved implementation concerns.
Agent relays of a person's messages still publish immediately as this task specifies; Task 12c introduces holds.
The two existing todos remain deferred command tests for plan 3.
The parked Task 9 minors concern files this implementation did not need to edit, so they remain parked.
No packages were installed, no historical briefs or reviews were edited, and no coordinator gate or ledger update was performed.
The pre-existing untracked `task-11-codex.log` was left outside the commit.
