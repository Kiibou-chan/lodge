# Task 14, parked minors and closing edits

Worktree `/var/tmp/lodge-server-store`, branch `server-store`; `ts/knip.json` is already back to the two entry patterns (uncommitted, knip passes: commit it).
Each item below is a parked reviewer minor with its handle in the ledger `docs/superpowers/plans/2026-11-02-lodge-server-store-progress.md` and the named `task-N-review.md` in this folder; read the review for the item before touching it.
Test-first where an item changes behaviour; every existing test passes; no behaviour change otherwise.
Do not dispatch subagents.

1. Task 9: `checked-writes.test.ts:41` failing-confirmation leg reaches the check (it throws `StaleList` before `add` today); the `changed`-row predicate written three times in `parity.test.ts` (lines 41, 46, 50) becomes one function; `seed.ts` reuses `setup()` of `store/support.ts`.
2. Task 5: the repeated `required`, `Q`, `PATH`, and `opened` in test files and the shared `test.each` titles (`task-5-review.md`).
3. Task 6: the dead all-capitals branch in `front-door.test.ts`; `?.` on `decisions.get` in `behindArea`.
4. Task 11: a comment at `ts/tests/structure/calls.ts:172-178` naming the rule's limit (it is syntactic: aliased imports, `core["writeThread"](x)`, and `writeThread(x, undefined)` pass); single-pass filter instead of the `?? ""` sentinel at `ts/src/app/threads.ts:196-197`; the `new Forbidden("").exitCode` assertion in `ts/tests/app/people.test.ts:31` moves to an errors test or goes.
5. Task 12c: one test asking with the code ref `ITEM-1`, asserting the held `ref` is `s-aaaaaa`.
6. Skip: Task 5's whitespace-only author `where` (inherited from Python), Task 7a codec speed, Task 7b D-1, Task 12b M-6 and M-7 (plan 3).

Hard rules: modules at most 300 lines, British English, no em-dashes, no new dependency, run `sh scripts/check-ts.sh`.
Write `task-14-minors-report.md` in this folder, commit with explicit paths (trailer `Co-Authored-By: Codex <noreply@openai.com>`), and push `server-store`.
