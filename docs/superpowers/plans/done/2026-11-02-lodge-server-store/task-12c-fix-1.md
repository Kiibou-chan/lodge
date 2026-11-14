# Task 12c, fix round 1

Worktree `/var/tmp/lodge-server-store`, branch `server-store`.
Read `task-12c-review.md` in this folder; fix the findings below, test-first (each new or changed test seen failing against the mutation the review names), and keep every existing test passing.
Do not dispatch subagents.

1. I-1: add `a_relayed_close_is_held_and_closes_the_thread_at_approval` in `tests/app/held-messages-approve.test.ts` as the review describes (held `operation: "close"`, `text: null`; after `ada.approve` the thread is `closed`); M1, M2, M3, M14, and M25 must each fail.
2. I-2: assert the held answer's `ids` (the thread's ID for a reply or close, one `q-` ID for an ask) and `about` (`s-aaaaaa`); M5 and M6 must fail.
3. M-1: keep one open-hold check per attempt (extract `isOpen(w, seq)` or drop the top-of-loop one), with a test of the behaviour kept.
4. M-2: remove the unreadable unreachable `hold ${seq} is not an add` throw at `ts/src/app/held.ts:37` by narrowing without it.
5. M-3: extract the held branch of `writeMessage` (`threads.ts:147-165`) into `holdMessage`.
6. M-4 and M-5: two plain waiting tests; `relay()` returns `held` as a number; a second `where` value in the approval test.
7. M-6: one test whose ask `ref` is a title-style ref, if the code resolves refs that way; otherwise say in the report why not.

M-7 (check fails at approval) only if you can build it from an existing fixture; otherwise say so in the report.
Hard rules: modules at most 300 lines, British English, no em-dashes, no new dependency, run `sh scripts/check-ts.sh`.
Write `task-12c-fix-1-report.md` in this folder, commit with explicit paths (trailer `Co-Authored-By: Codex <noreply@openai.com>`), and push `server-store`.
