# Task 10 fix round 1 report

Fixed C-I1, C-M1, and C-M2.
D-M1 remains with the coordinator for Task 11, as instructed.

## Changes

- `ts/tests/core/people-regressions.test.ts`: adapted all nine scratch probes into permanent tests with plan-style titles, using the synthetic person set `{ada}`.
- `ts/tests/core/people.test.ts`: asserted the exact missing-where write error, and extended `confirmation_draft_names_the_person` with `a: b` and `#ada`, checking quoted bytes and parsing the resulting record after supplying its ID and date.
- `ts/src/core/confirmation.ts`: emit a plain person name only when it matches the record writer's plain-scalar expression; quote other names with the existing YAML writer.

The separate regression file keeps each test file below 300 lines.
No earlier brief, report, review, Python source, parity row, or scratch probe was changed.

## Test-first evidence

Before the quoting fix, the two people test files produced `18 pass, 1 fail`.
`confirmation_draft_names_the_person` failed because it expected `decided_by: "a: b"` and received `decided_by: a: b`.
After the fix, both names parse back as their original strings, and the existing plain-name assertion remains green.

Each mutation below ran separately against the two people test files with `bun test tests/core/people.test.ts tests/core/people-regressions.test.ts` from `ts/`.
Each returned exit 1 with the named test failure, and each source was restored in a `finally` block before the next mutation.
The first ten rows cover all ten sites from C-I1.

| Source | Mutation | Failing test |
|---|---|---|
| `derive.ts` | confirmedBy reverted to author-only | `confirmable_and_confirmed_by_follow_the_person` |
| `derive.ts` | confirmedByHer reverted to author-only | `agent_replaces_a_decision_she_confirmed` |
| `derive.ts` | touchedByFlagged reverted to author-only | `touched_by_flagged_names_her_entry_edit` |
| `derive.ts` | undone later reverted to author-only | `agent_edit_after_she_replaced_an_agent_edit_flagged` |
| `derive.ts` | undone other reverted to author-only | `agent_edit_after_she_corrected_her_own_edit_flagged` |
| `derive.ts` | flagged skips reverted to author-only | `own_replacement_is_not_flagged`, `agent_edit_after_she_corrected_her_own_edit_flagged`, `no_edit_back_when_she_replaces_her_own` |
| `confirmation.ts` | confirmableIds reverted to author-only | `confirmable_and_confirmed_by_follow_the_person` |
| `feedback.ts` | edit-back own reverted to author-only | `edit_back_asked_of_a_person` |
| `feedback.ts` | edit-back replaced reverted to author-only | `no_edit_back_when_she_replaces_her_own` |
| `threads.ts` | written minute reverted to author-only | `person_message_writes_a_quoted_minute` |
| `threads.ts` | C-M2: changed the read-back error text | `person_message_needs_where_and_a_minute` |

For `touchedByFlagged`, the mutation supplies `{author}` to that call to `countsFor`, leaving all other calls unchanged.
For `undone later`, only the first matching call was mutated, leaving `cleared` unchanged.
For C-M2, changing only the error text proves that a different `ValueError` no longer satisfies the assertion.

## Validation

- `uv run --frozen --quiet lodge waiting`: nothing waiting for an agent or the author.
- `bunx biome format --write tests/core/people.test.ts tests/core/people-regressions.test.ts src/core/confirmation.ts`: formatted the changed files.
- Restored-source targeted tests: `19 pass, 0 fail`, 37 assertions across two files.
- Final gate: `sh scripts/check-ts.sh` exited 0: Biome, TypeScript, dependency checks, and knip passed; `951 pass, 0 fail`, 2327 assertions across 65 files.

All nine probe tests hold in TypeScript.
No unresolved implementation concerns.
