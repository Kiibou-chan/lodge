# Task 4 review

Reviewer: `reviewer` (Opus), commit 9f47e33 on `server-store-a`, diff `9c84418..9f47e33`.
Scope: Task 4 of the plan, Global Constraints, Review Focus 1 and 6, and the coordinator's `ok`-key rule (D1 of `task-3-review.md`).

## Correctness

### C1 (Important): `not_found_names_the_files_lodge_cannot_read` asserts less than its Python original

Handle: `ts/tests/app/reads-checks.test.ts:110`, against `tests/app/test_reads.py:248`.
Python matches the regular expression `no .* named .*; lodge could not read {path}`, so it holds the `no <what>; ` prefix of the message; the port matches only the substring `lodge could not read ${path}`.
Failure scenario, run in a scratch worktree: dropping `no ${what}; ` from the unreadable branch of `notFound` (`ts/src/app/state.ts:101`) leaves `bun test tests/app` at 81 pass, 0 fail; the same mutation of `src/lodge/app/state.py:98` fails all four cases of the Python test (`4 failed, 30 passed`).
This is Review Focus 1 and the Porting constraint ("asserting no less").
Fix: pass the Python pattern as a regular expression, `new RegExp(\`no .* named .*; lodge could not read ${path}\`, "u")`, or the literal prefix for each case (`no record named d-aaaaaa; lodge could not read ${path}` and `no area named ghost; …`), and see it fail against the mutation above.

### C2 (Important): `message` checks `by` and `where` with `String.trim`, not Python's `str.strip`

Handle: `ts/src/app/threads.ts:46` and `ts/src/app/threads.ts:51`, against `src/lodge/app/threads.py:28` and `:33`.
`trim` and `str.strip` disagree on what is space: `trim` strips U+FEFF, which Python keeps, and keeps U+001C to U+001F and U+0085, which Python strips.
`#core` already exports `strip`, which strips exactly Python's set (`PY_SPACE_CLASS`, `ts/src/core/text.ts:2-14`), and `state.ts:97` of the same package uses it.
Failure scenario, run against both implementations with `wired(project()).ask("s-aaaaaa", Raises.QUESTION, by, "Why?", { where })`:

| `by`, `where` | lodge 0.2 | this port |
|---|---|---|
| `"\u001c"`, none | `LodgeError: by needs a non-empty role` | `LodgeError: by: U+001C cannot be written in a header` |
| `"author"`, `"\u0085"` | `LodgeError: a message by author needs where, …` | `LodgeError: where: U+0085 cannot be written in a header` |
| `"﻿"`, none | published, `q-111111` | `LodgeError: by needs a non-empty role` |

The third row changes an outcome, not only a message, and plan 3's API passes `by` and `where` from a request body.
Fix: `if (!strip(by))` and `if (where === null || !strip(where))` with `strip` of `#core`; Task 5's thread tests may carry a case, but none of lodge 0.2's tests pins it, so a new test here (one row per line above) is the way to see it fail first.

### C3 (Minor): `not_found_does_not_call_a_missing_file_unreadable` no longer asserts the class `NotFound`

Handle: `ts/tests/app/reads-checks.test.ts:131-132`, against `tests/app/test_reads.py:270-272`.
Python asserts `pytest.raises(NotFound)` and then the exact message; the port asserts the message twice and never the class, so a `LodgeError` with that message passes.
`show_unknown_ref_is_an_error` (`ts/tests/app/reads.test.ts:34-38`) holds the class for the same branch of `notFound`, so no mutation I can name escapes both; the finding is the Porting rule, not a hole.
Fix: `await raises(call, NotFound, "no record named d-zzzzzz")` on one promise, then the exact-message check on it.

### Verified, no finding

- `reads.ts` and `threads.ts` against `src/lodge/app/reads.py` and `threads.py` line by line: each branch, message, retry count, `about`, outcome mapping, and the `commit` only on `STAGED` agree.
- Newest first (`ts/src/app/reads.ts:146-156`): `instant(b) - instant(a) || byCodePoint(b, a)` is Python's `(datetime, id)` with `reverse=True`; equal instants at different offsets tie on the instant and fall to the ID, as aware `datetime`s compare.
- `found` (`ts/src/app/reads.ts:98-111`): keyed by `JSON.stringify([path, check, line, message])`, labels appended in `base.checked` order, a repeated problem in one state labelled twice as Python's `setdefault(...).append` does; the sort is `_by_position`'s, stable on ties as `sorted` is.
- `checkResult(problems, [...notes])` at `ts/src/app/reads.ts:123`; notes deduplicated in first-seen order as `dict.fromkeys` does.
- `draft` (`ts/src/app/reads.ts:125-145`): `String.replace` with a string pattern replaces the first `---\n`, as `replace(…, 1)`; its replacement holds no `$` pattern, since an area name is lower-case words and hyphens (`ts/src/core/fields.ts:145`) and the hash is hex.
- Review Focus 6: `threads.ts` stamps an author's message with `minuteOf(now)` and every other stamp with `stampOf(now)`; `reads.ts` passes `stampOf(w.clock.now())` to `checkChange`; neither file names `Date`.
- Every carried test `await`s each operation; every `rejects` is awaited (`raises` in `ts/tests/app/support.ts:36-43` awaits both).
- Each of the 24 tests of `test_reads.py`, the six of `test_writes.py`, and the six of `test_writes_dates.py` exists by name; apart from C1 and C3, each asserts what its original does (parametrised cases complete: eight reads, four not-found calls).
- The mutation table is genuine: in a scratch worktree, the sleep skipped fails five date tests and `staged_second_edit_builds_on_first`; the sleep fixed at one second and the whole-second comparison made on milliseconds each fail `add_sleeps_to_the_next_whole_second`; two waits instead of three fail `a_decision_a_few_seconds_ahead_of_the_clock_is_waited_for`; the far-ahead shortcut removed fails `a_decision_far_ahead_of_the_clock_is_not_waited_for`; `Conflict` replaced by `LodgeError` fails `add_stale_base_conflicts_writes_nothing`; the changed-files filter removed fails `unchanged_draft_publishes_nothing` and `only_changed_files_are_published`; the failing-check branch removed fails `cycle_made_in_one_add_is_refused` and `feedback_skips_edited_decisions_which_the_check_refuses`.
- The brief's example mutation `> WAITS` read as `>= WAITS` (`ts/src/app/writes.ts:171`) survives every test, here and in lodge 0.2, since no test sits three seconds ahead; the builder rightly did not list it, and no carried test can change that.
- The `ok`-key rule (D1): with `pure &&` put back to `pkg === "core" &&` at `ts/tests/structure/calls.ts:96`, the four refusing fixtures fail (31 pass, 4 fail), as the report says; a planted `{ ok: true }` in `ts/src/app/time.ts` fails `repository_has_no_violations` with `build check results through checkResult`.
- `sh scripts/check-ts.sh` at 9f47e33 in a scratch worktree: exit 0, 1018 pass, 0 fail.

## Practice

### P1 (Minor): the `ok`-key rule misses a template-literal key, and its fixtures accept any violation

Handle: `ts/tests/structure/calls.ts:101-102` and `ts/tests/structure/core-rules.test.ts:63-71`.
The computed-key branch accepts only `ts.isStringLiteral`, so ``{ [`ok`]: true }`` passes: planted in `ts/src/app/time.ts`, `bun test tests/structure` reports no violation (verified in a scratch worktree).
The gap is plan 1's, now extended to `app`; it is narrow, since nobody writes that by accident.
The fixtures assert `callViolations(…).length > 0`, so a fixture refused by another rule (an `import.meta`, a banned global) would pass for the wrong reason.
Fix: test the name with `ts.isStringLiteralLike(name.expression)`, which covers both literal kinds, add the template-literal fixture, and assert the message, `violations.some((v) => v.endsWith("build check results through checkResult"))`, rather than the count.

### P2 (Minor): `test_writes.py`'s parity row names Task 4 alone

Handle: `ts/tests/parity.json:50-51`.
Thirteen of its nineteen tests were Task 3's and six are Task 4's; plan 1's rows ported over two tasks name both (`"task": ["8a", "8b"]` at `ts/tests/parity.json:86`, and four more).
Failure scenario: Task 14's closing check, or anyone tracing a test to the review that passed it, is sent to Task 4's review for the thirteen tests Task 3's review covered.
Fix: `"task": ["3", "4"]`.

### P3 (Minor): the new `Lodge` methods have no return types, and two parameters are renamed

Handle: `ts/src/app/lodge.ts:23-74`, `ts/src/app/reads.ts:61` and `:92`.
"Interfaces for plans 3 and 4" fixes each signature (`search(…): Promise<Listed>`, `check(gate: boolean): Promise<readonly [CheckResult, Read]>`, …), but the port leaves every new method, and `waitingAll` and `check` of `reads.ts`, to inference, so an edit to `reads.ts` changes `#app`'s public surface with no type error at the change; `reply` and `close` name their first parameter `ref` where the interface and `lodge.py:80,91` say `thread`.
Fix: annotate each method with the interface's return type and name the parameter `thread`.

### P4 (Minor): fallbacks that turn an impossible case into a misleading one

Handle: `ts/src/app/reads.ts:152`, `ts/tests/app/reads-checks.test.ts:78-79`.
`decisions.get(b)?.date ?? ""` makes a missing decision a `ValueError: not a stamp: ` from `instant` instead of naming the ID, where Python raises `KeyError` with it; in the test, `?? ""` turns a missing file into an empty expectation rather than a failure that says so.
Fix: in `reads.ts`, throw an `Error` naming the ID, as `draft` does at `:138`; in the test, type the pairs `as const` so that `prefix` and `ref` are strings, and fail on a missing file.

### P5 (Minor): the report's mutation table names each mutation, not the line it changed

Handle: `docs/superpowers/plans/2026-11-02-lodge-server-store/task-4-report.md:59-72`.
"cycle check bypassed" or "whole-second ordering reversed" leaves the reader to guess the edit; I reproduced the table from my own mutations (Verified, above), which agree, but a later reader cannot rerun the report's.
Fix: none for this task beyond a column of `file:line` and the edited expression in later reports.

## Design

### D1 (Minor): `writeMessage` takes `close` as a positional boolean after its options object

Handle: `ts/src/app/threads.ts:66-74`, called at `ts/src/app/lodge.ts:64`.
Python's `write` has `where`, `when`, and `commit` without defaults and `close` with one (`src/lodge/app/threads.py:43-54`); the port moves the first three into an options object and leaves the defaulted `close` positional after it, the reverse of d-vd3175's shape, and `writeMessage(…, options, true)` reads as an unnamed flag.
Task 12c extends this function with the held message (plan, Task 12c; d-2v8vtk), so the next parameter lands after `close` or in a second object.
Fix: `close` into `MessageOptions` (`{ where, when, commit, close }`), with `lodge.ts` passing `{ ...options, close: true }`.

### Design checks, no finding

- Imports: `reads.ts → threads.ts → writes.ts → state.ts`, as Python's; `lodge.ts` imports both by namespace; dependency-cruiser reports no cycle, and the later chain `held.ts → threads.ts → writes.ts` of the plan's lanes stays acyclic.
- `threads.ts` builds the after-state with `tree({ … })` (`:112-118`), so Task 10's `people` field compiles; `writeThread(thread)` keeps one argument, so lane C's defaulted `people` merges either way.
- `knip.json` takes out all three entries the plan names; the gate's knip step reports no unused export, so each of `readChecked`, `resolveRef`, `notFound`, `mintUnused`, `project`, `FIRST`, and `ENTRY` now has its reader.
- Every file in the diff is under 300 lines (largest `ts/tests/app/writes.test.ts`, 250; `ts/tests/structure/calls.ts`, 243).
- The parity row of `test_reads.py` names both files.

## Files read

Read: `CLAUDE.md`; `lodge spec` (first 150 lines); the plan's header, Global Constraints, Review Focus, Interfaces, and Tasks 1 to 4; `task-4-brief.md`; `task-4-report.md`; d-vd3175 and d-snrhjs through `lodge show`; `src/lodge/app/reads.py`, `threads.py`, `lodge.py`, and line 98 of `state.py`; `tests/app/test_reads.py`, `test_writes_dates.py`, and the six tests and header of `test_writes.py`; `ts/src/app/reads.ts`, `threads.ts`, `lodge.ts`, `state.ts`, and `writes.ts` (lines 73-135, 167-189, 232); `ts/tests/app/reads.test.ts`, `reads-checks.test.ts`, `writes-dates.test.ts`, `support.ts`, and the diff of `writes.test.ts`; `ts/tests/structure/calls.ts` (lines 1-140) and the diff of `core-rules.test.ts`; the diffs of `ts/knip.json` and `ts/tests/parity.json`; `ts/src/core/stamps.ts:24-39`, `text.ts:1-21,94-99`, `model.ts:122-128`.

Not read: `ts/src/app/results.ts`, `ports.ts`, `errors.ts`, and `time.ts` (Task 2's, checked by `tsc` through the gate); `ts/tests/app/fakes.ts`; the rest of `ts/tests/structure/`; `task-3-review.md` beyond its D1 and verdict; `task-4-codex.log`; the rest of `lodge spec`.

Scratch worktree: `/var/tmp/lodge-server-store/.claude/worktrees/t4-review`, detached at 9f47e33, removed when done.

## Verdict

0 Blocking, 2 Important (C1, C2), 7 Minor (C3, P1, P2, P3, P4, P5, D1).
The coordinator's `ok`-key rule holds for `app`, with the template-literal gap of P1.
Task 4 needs one fix round for C1 and C2 before it merges, and that round can take the Minors in the same files.
