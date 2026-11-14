# Task 10 report

Implemented people in the core on `server-store-c`.
The task-specific permission to commit and push overrides the repeated sandbox-only global constraint in the brief.

## Changes by file

| File | Change |
|---|---|
| `ts/src/core/people.ts` | Internal `AUTHOR_ONLY` default and wording helpers, preserving the author wording. |
| `ts/src/core/snapshot.ts` | Required people on Tree and Snapshot, defaulted by tree(), propagated through load and thread parsing. |
| `ts/src/core/derive.ts` | Membership-based isAuthor with a trailing default, and people passed through confirmation and flag derivation. |
| `ts/src/core/check-state.ts` | Project people determine quote requirements and confirmation eligibility, with the required wording. |
| `ts/src/core/check-immutable.ts` | Published snapshot people determine whose reasoning changed. |
| `ts/src/core/views.ts` | Person decisions show their quote and imported unquoted flag. |
| `ts/src/core/threads.ts` | Trailing defaulted people on parseThread and writeThread, passed through message parsing and read-back. |
| `ts/src/core/confirmation.ts` | Snapshot people determine confirmable decisions, and a trailing person names confirmation drafts. |
| `ts/src/core/feedback.ts` | Edit-back feedback uses snapshot people, retaining the flag wording reserved for Task 13. |
| `ts/src/core/apply-state.ts` | Restored-state calculation retains the input tree's people. |
| `ts/scripts/differential.ts` | Tree construction uses tree(), and thread parsing and writing explicitly use snapshot people. |
| `ts/tests/core/builders.ts` | The literal Snapshot gets the existing author-only default. |
| `ts/tests/core/people.test.ts` | Ten new tests cover all nine wording rows, defaults, membership, thread read-back, and flag clearing. |

No public export was added.
Existing core test bodies are unchanged.
No parity rows belong to this task: these are new TypeScript requirements, and all applicable Python core rows are already ported under plan 1.
Their plan 1 task numbers were preserved.

## Test-first evidence

All ten tests were written before implementation.
`cd ts && bun test tests/core` first ended with `709 pass`, `10 fail`, and `Ran 719 tests across 55 files`.
The following table records each first failure, omitting generated fixture IDs.

| Test | First failure |
|---|---|
| `a_person_is_a_name_in_people` | Expected true for ada membership, received false. |
| `tree_defaults_to_lodge_0_2_people` | Expected Set containing author, received undefined. |
| `person_decision_needs_a_quote` | Expected the ada missing-quote problem, received an empty list. |
| `author_is_a_role_where_no_person_is_author` | Expected the project-person wording, received an empty list. |
| `confirms_is_for_a_person` | Expected “a person's decisions”, received “author decisions”. |
| `immutable_names_the_person` | Expected “decision of ada”, received “agent decision”. |
| `quote_and_unquoted_follow_the_person` | Expected the quote object, received null. |
| `person_message_needs_where_and_a_minute` | ValueError: the thread would not read back: when must be ISO 8601 with seconds and an offset. |
| `confirmation_draft_names_the_person` | Expected `decided_by: ada`, received `decided_by: author`. |
| `agent_change_to_a_persons_decision_is_flagged` | Expected the agent decision ID in awaitingAuthor, received an empty set. |

The immutable test was subsequently routed through the public checkChange API via the existing check helper to satisfy the front-door rule.
The final test also failed against the targeted mutation removing `published.people` from that isAuthor call: `0 pass`, `9 filtered out`, `1 fail`.
The mutation was reverted.
No carried test was ported or changed, so no carried-test mutation was required.
No test is inapplicable to TypeScript.

## Commands and results

| Command | Result or last lines |
|---|---|
| `cat docs/superpowers/plans/2026-11-02-lodge-server-store/task-10-brief.md`, then `cat CLAUDE.md` | Read requirements and repository instructions. |
| `uv run --frozen --quiet lodge waiting` | Both waiting lists: `nothing`. |
| `git status --short`, `git branch --show-current` | Branch `server-store-c`; pre-existing untracked task-10-codex.log left untouched. |
| `rg` and `cat` reads of core, tests, scripts, package.json, and parity.json | Located callers, existing defaults, dependencies, and parity rows. |
| `cd ts && bun test tests/core` before implementation | 709 pass, 10 fail. |
| `cd ts && bun test tests/core` during implementation | 691 pass, 28 fail, exposing a mechanical replacement error in thread writing, subsequently fixed. |
| `cd ts && bun test tests/core` after that fix | 719 pass, 0 fail, 1697 expect() calls. |
| `cd ts && bunx --no-install biome check --write` with explicit changed TypeScript paths | Formatted files; initial non-null assertion warning fixed. |
| `sh scripts/check-ts.sh` during development | First refused the non-null assertion warning; next refused an internal test import; both corrected. |
| `sh scripts/check-ts.sh` after corrections | Exit 0; 942 pass, 0 fail, 2313 expect() calls, 64 files. |
| `cd ts && bun test tests/core/people.test.ts -t immutable_names_the_person` with targeted mutation | 0 pass, 9 filtered out, 1 fail. |
| `rg -n 'isAuthor\(|parseThread\(|writeThread\(|tree\(|load\(' ts/src/core ts/scripts` | Audited every call; snapshot people propagate through core and differential thread operations. |
| `git diff -- ts/src/core`, `git diff --stat -- ts/tests/core` | Reviewed implementation and verified only the builder's literal Snapshot changed among carried core tests. |
| Final `sh scripts/check-ts.sh` | Exit 0; 942 pass, 0 fail. |

## Concerns and scope

None unresolved.
Person message minutes retain lodge 0.2's string behaviour; this task does not add stricter minute validation.
The differential script deliberately uses tree()'s author-only default for lodge's own records, as specified.
The whole Python gate, differential execution, merge, and ledger update remain the coordinator's work.
No package was installed, and no Python source, Python tests, earlier brief, report, or review was edited.
