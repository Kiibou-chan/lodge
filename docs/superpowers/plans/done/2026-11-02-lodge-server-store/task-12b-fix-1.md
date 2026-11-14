# Task 12b, fix round 1

Worktree `/var/tmp/lodge-server-store`, branch `server-store`.
Read `task-12b-review.md` in this folder; fix the findings below, test-first (each new or changed test seen failing against the mutation the review names), and keep every existing test passing.
Do not dispatch subagents.

1. I-1: tests that a hold keeps its `attachments`, `importing`, and `message` (hold an add carrying attachments and a message, approve it, and see the approved result carry them; the review's mutation storing `attachments: []` must fail).
2. M-1: one test holds two adds and expects `held()` in `seq` order; one assertion that `AddOutcome.HELD` equals `"held for approval"`.
3. M-2: `decline(seq, " ")` by the wrong actor rejects with `Forbidden`; `another_persons_add_is_held` expects `by: "bo"` for a person drafter.
4. M-3: keep the per-attempt open-check and add a test that a hold settled after the first rejected attempt stops at the second (`store.attempts` is 1); drop the re-parse of the drafts in the loop if nothing uses it.
5. M-4: drop the unreachable `request.approves === null` clause at `ts/src/app/writes.ts:177`.
6. M-5: pass `w` at `ts/src/app/held.ts:29` and drop the unused `person` import if it becomes unused.

M-6 and M-7 are plan 3's; leave them.
Hard rules: modules at most 300 lines, British English, no em-dashes, no new dependency, run `sh scripts/check-ts.sh`.
Write `task-12b-fix-1-report.md` in this folder, commit with explicit paths (trailer `Co-Authored-By: Codex <noreply@openai.com>`), and push `server-store`.
