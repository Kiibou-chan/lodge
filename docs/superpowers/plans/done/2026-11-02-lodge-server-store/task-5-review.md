# Task 5 review

Reviewed `57a93e0..26a57f9` in a scratch worktree at `26a57f9`, since removed.
Read: the brief, the report, the plan's Task 5, `tests/app/test_thread_ops.py`, `tests/app/test_thread_fix_paths.py`, the three new test files, `ts/tests/app/support.ts`, `ts/tests/app/fakes.ts` (START and clock), `ts/src/app/threads.ts`, `src/lodge/app/threads.py` (lines 25 to 40), `ts/tests/parity.json` diff.
Not read: `reads.ts`, `writes.ts`, and `state.ts` beyond the mutation targets; `ts/tests/core/applying.ts` beyond `present`.

## Pass 1: correctness

Every Python test is carried: 27 in `test_thread_ops.py` (15 in `thread-ops.test.ts`, 12 in `thread-ops-publish.test.ts`, counted against `grep -c "^def test_"`), plus `waiting_reads_one_snapshot` and the two `test.todo`s in `thread-fix-paths.test.ts`.
The split lines match the plan (`ask_writes_a_thread_file` to `close_with_text`; `rejected_publish_starts_again` to `three_rejections_are_a_conflict`).
Parametrised cases are all present (`where`/`when`, `Author`/`the author`/empty, `""`/whitespace, `where`/`when` unstorable, both `close_with_text` rows).
No assertion is weakened.
`raises` (`ts/tests/app/support.ts:40-47`) asserts class by `toThrow(errorClass)` and message by substring, which equals pytest `match` for every pattern used here (none contains a regex metacharacter).
Line-by-line comparison found these only as differences of form: `thread.about == written.about == "s-aaaaaa"` became two assertions covering the same chain; `START.isoformat(timespec="seconds")` became the literal `2026-10-29T09:30:00+01:00`, which equals `START` in `ts/tests/app/fakes.ts:24`; tuples and sets became arrays and `Set`s.
The deferrals are as the plan and d-rp74dr require: `thread-fix-paths.test.ts:5-6` holds the two `test.todo`s, and `ts/tests/parity.json` keeps the row `planned` with `plan: 3`.
`tests/parity.json` flips `test_thread_ops.py` to `ported` with both files and `task: ["5"]`.
No production file changed (`git diff --stat` lists tests, parity, report only).

Verified by running:
- `sh scripts/check-ts.sh` in the scratch worktree (node_modules symlinked from the build worktree): exit 0, `1153 pass`, `2 todo`, `0 fail`, `2847 expect() calls`, 84 files.
- Mutation spot-check, 20 mutations each applied alone and reverted: the 10 sampled from the builder's table all FAIL (messages `by`, REJECTED `continue`, `commit &&` guard, `ref.toLowerCase()`, `i < 3`, `waitingIn(state)`, `paths: []`, OPEN filter, `cleanText`, `record named`), and 9 of my own all FAIL (author `when ??`, closed-thread guard, `!text && !close`, `strip(by)`, role-like-author check, `closed by` description, lower-cased commit message, `opened: stampOf`, `about` lookup limited to decisions).
  One of my own mutations survived: finding 1.

1. **Minor** · `ts/tests/app/thread-ops.test.ts:46-52` (`author_message_needs_where`).
   Mutating `where === null || !strip(where)` to `where === null` at `ts/src/app/threads.ts:50` leaves all 21 tests in the file green, so a whitespace-only `where` from the author is untested.
   The Python original has the same gap (`src/lodge/app/threads.py:33` has `not where.strip()`, `test_thread_ops.py:49-51` omits it), so this is inherited, not introduced.
   Fix: parametrise `author_message_needs_where` over `undefined` and `"  "` (the plan allows a carried test to grow; run it red against that mutation).

## Pass 2: practice

2. **Minor** · `ts/tests/app/thread-ops.test.ts:150`, `thread-ops-publish.test.ts:125`, `thread-fix-paths.test.ts:21`.
   The same `required<T>` helper is pasted three times, and `Q`, `PATH`, and `opened()` twice (`thread-ops.test.ts:6-15`, `thread-ops-publish.test.ts:6-14`); `ts/tests/core/applying.ts:78` already exports `present<T>(value: T | undefined)`.
   Failure scenario: a later change to the helper (say, a clearer message) is made in one file and not the others.
   Fix: put `required` (null-aware) and the `opened` fixture in `ts/tests/app/support.ts`, import them in all three; the Python file kept them once.
3. **Minor** · `ts/tests/app/thread-ops.test.ts:55,65,75,91`.
   `test.each` rows share one title (`"agent_message_may_not_carry_where"` twice, and so on), so a failing row reports the name without saying which parameter.
   pytest's ids carry the parameter.
   Fix: add a `%j` or `%s` specifier to the four titles (names still start with the Python name, so the parity trace holds).

## Pass 3: design

No finding.
All three files are under 300 lines (153, 128, 24; `wc -l`), fixtures are the made-up storage project from `support.ts`, no personal paths or names (`grep` for `/home/`, `<user>`, `Svenja` in the three files is empty), and the tests import only through `#app` and `#core` plus test-local helpers.
Test-first is evidenced as the plan allows (d-mfayy5), by mutation.

## Report

4. **Minor** · `task-5-report.md` (Commands section).
   The mutation scripts (`/tmp/port5.py`, `/tmp/mutate5.py`, `/tmp/runmut5.py`) are not committed, so the 28-row table cannot be rerun from the repository; the report gives `2843 expect() calls` where the gate at the same commit prints `2847`; and "run again as the final validation command" gives no result line.
   I reran the table's sample myself (above), so the evidence holds; the gap is traceability only.
   Fix: next reports quote the final gate's last lines once, and keep the mutation list as a table of file, old text, new text (already done) rather than pointing at `/tmp`.
   Untracked `task-5-codex.log` and `task-5-codex-final.txt` sit beside the report in the build worktree and should not be committed.

Verdict: 0 Blocking, 0 Important, 4 Minor
