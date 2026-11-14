# Task 12a, fix round 1

Worktree `/var/tmp/lodge-server-store`, branch `server-store`.
Read `task-12a-review.md` in this folder; fix the findings below, test-first (each new or changed test seen failing against the src mutation the review names, or against the old test), and keep every existing test passing.
Do not dispatch subagents.

1. I-1: `a_settled_hold_cannot_be_declined` asserts the class `NotFound` as well as the message.
2. I-2: drop the `deleteFrom("held")` before `rebuild` in `holds_rebuild`, so `rebuild`'s own delete is tested.
3. I-3: one test with two projects (`projects.create("other", "ada")`, a store each): `held()` lists only its own holds, and `decline` and an approving `publish` with the other project's number answer `NotFound` and `REJECTED` and write no event.
4. I-4: add `decline` and an approving `publish` (with a held `seq`) to the `test.each` of `ts/tests/store/write-first.test.ts`, and a missing-project case for `hold` and `decline`.
5. P-M2: `MemoryStore.hold` takes its stamp from `stampOf(START)` instead of the literal.
6. P-M3: `MemoryStore` keeps `declined: [seq, reason][]`, with a test in `fakes-held.test.ts`.
7. P-M1: one `openHold(tx, project, seq)` used by `decline` and the approving `publish`.

Hard rules: modules at most 300 lines, British English, no em-dashes, no new dependency, run `sh scripts/check-ts.sh`.
Write `task-12a-fix-1-report.md` in this folder, commit with explicit paths (trailer `Co-Authored-By: Codex <noreply@openai.com>`), and push `server-store`.
