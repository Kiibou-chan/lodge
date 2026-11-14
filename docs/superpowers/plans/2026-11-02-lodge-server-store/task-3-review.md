# Task 3 review

Commit under review: 817f49b on `server-store-a`, diffed against cd26279 (`git diff cd26279..817f49b`).
Gate: `sh scripts/check-ts.sh` in a detached scratch worktree at 817f49b exits 0, 967 pass, 0 fail, 2405 expect() calls, matching the report.
Mutations ran in that scratch worktree (`.claude/worktrees/review-t3`, removed afterwards), each reverted after its run; the branch under review was not edited.

## Correctness

### C1 · Important · nine carried `pytest.raises(LodgeError, match=…)` keep the pattern and drop the class

Handles: `ts/tests/app/writes-attach.test.ts:41-43`, `44-48`, `53-55`, `56-60`, `66-70`; `ts/tests/app/writes.test.ts:68-70`, `71`, `78`, `113-115`.
Python originals: `tests/app/test_writes_attach.py:42,45,52,57,65` and `tests/app/test_writes.py:76,78,85,150`, each `pytest.raises(LodgeError, match=…)`.
The plan's Global Constraints say a `pytest.raises` becomes `rejects.toThrow(Class)` with the pattern where Python matched one, and plan 1 ports it as two assertions (`ts/tests/core/search.test.ts:32-33`, `ts/tests/core/confirmation.test.ts:121-122`); this task does so only at `writes-attach.test.ts:74-83` and `writes.test.ts:65-67`.
Failure, run: replacing `LodgeError` with a plain `Error` at `ts/src/app/writes.ts:143` (`--attach needs…`), `:146` (`not a plain file name`), `:156` (`the new decision lists…`), `:174` (`no drafts to add`), or `:206` (`no unused ID…`) leaves every test passing (11 pass and 13 pass, 0 fail, five separate runs).
A plain `Error` carries no `exitCode`, so plan 3's command and API would answer a crash where lodge 0.2 answers exit 2 with the message, and no test of this plan would notice; Review Focus 1 names exactly this.
Fix: add `await expect(p).rejects.toThrow(LodgeError);` beside each of the nine, as `two_attachments_with_one_name_are_refused` does; or, since Tasks 4 to 6 carry many more `pytest.raises`, one helper in `ts/tests/app/support.ts`, `raises(promise, Class, pattern?)`, that asserts both, and use it here.

### Checked and clean

- `state.ts` against `src/lodge/app/state.py`, line for line: `readState` reads `trees()` then `freshness()` as Python does; `readChecked` passes `stampOf(clock.now())` as `check_change`'s `now` (plan 1, Task 8b), folds the change problems not already found, sorts by path, check, and message in code-point order, and builds the result through `checkResult` (`ts/src/app/state.ts:77`, d-snrhjs); `resolveRef` and `notFound` carry Python's messages, `strip`, and the fallback to every unreadable path.
- The fold's dedupe keys on `JSON.stringify` of the whole problem (`state.ts:68-72`), which is Python's dataclass equality (every field, and `stale` standing for the `StaleBase` class) as long as both sides are built by the same code; they are, since both come from `checkState` of the same snapshot (`ts/src/core/check-change.ts:26-31`), so no duplicate survives.
- `writes.ts` against `src/lodge/app/writes.py`, line for line, with the plan's readings: `afterNewest` (`writes.ts:161-172`) uses `instant`, `(newest - now.epochMs) / 1000 > WAITS`, `Math.floor(now.epochMs / 1000) * 1000 > newest`, and `clock.sleep(1 - (now.epochMs % 1000) / 1000)`; `applyDrafts` and `checkChange` take `stampOf(now)` from the one reading; the after-state is `tree({ rev, files, attachments })` (`writes.ts:88-94`); `_attached`'s `{name!r}` is `pyRepr(name)` (`:146`); the stale test is inline, `"stale" in p && p.stale === true` (`:182`), with nothing imported from `tests/` and no export added to `#core` (the diff touches no file of `ts/src/core`).
- Minting runs one draw per new decision draft, in draft order, each excluding the IDs drawn before it, as Python's `range(sum(…))` loop does; `CHECK_FAILED` carries `freshness` and `minted`, `DRY_RUN` `minted`, `UNCHANGED` neither, and a publish `paths`, as `writes.py:101-113` does.
- `lodge.ts` holds a `Wiring` and delegates `mint` and `add`, and neither `state.ts` nor `writes.ts` imports it.
- Every carried test exists by name: the six of `test_writes_attach.py` (the parametrised one with all six cases, `test.each(… .map((c) => [c]))`) and the thirteen of `test_writes.py` the plan lists; the six left for Task 4 are absent, and the `test_writes.py` row stays `planned`.
- Every operation is awaited, a rejection through `await expect(…).rejects`; `add_refuses_unreadable_or_unusable_drafts` awaits one rejected promise three times, which is sound.
- Apart from C1, each test asserts what its original does: `Map` equality (`writes.test.ts:87`) and `toContainEqual` (`:123-126`) compare contents in Bun (a probe with differing values and an extra field fails both), and `START` plus 999 ms stands for `microsecond=999_999` as the plan says.
- The red runs are genuine: the Codex log shows `SyntaxError: Export named 'Lodge' not found` with 9 pass, 2 fail, 2 errors (`task-3-codex.log:2426-2432`) after both test files were written and before `lodge.ts` existed.
- The report's mutation table is genuine: reversing the spread in each of the six default-filling functions, one at a time, fails `explicit_defaulted_fields_survive` (six runs); dropping `error.message` from the settings message and dropping `{ cause: error }` each fail `settings_error_preserves_the_full_message_and_cause`.
  The report says the cause code came before its test and was then shown red by mutation (`task-3-report.md:65-66`); that is a test-first slip, honestly reported, with no remaining effect.
- Review Focus 6: `app` reads no clock and no local zone; the only `Date` is `new Date(ms)` with UTC getters in `time.ts:6-8`, which the `calls.ts` rule allows.

## Practice

### The parked Task 2 Minors

All seven are fixed, each checked against `task-2-review.md`:

- P1: `explicit_defaulted_fields_survive` (`ts/tests/app/ports.test.ts:48-78`) passes each defaulted field to all six functions and asserts it survives; each of the six reversed spreads fails it (run).
- P2 and P3: `settings_error_preserves_the_full_message_and_cause` (`ts/tests/app/errors.test.ts:25-46`) asserts the whole message against the parser's own and the cause; `LodgeError` takes `ErrorOptions` (`ts/src/app/errors.ts:5-6`) and `coreSettings` passes `{ cause: error }` (`:20`), as `resolveRef` does (`ts/src/app/state.ts:90`).
- P4: `MemoryStore.attachmentTexts` filters on `ATTACHMENTS` of `#core` (`ts/tests/app/fakes.ts:60`).
- P5: one module-level `pad` (`ts/src/app/time.ts:3`), used for the offset (`:16`).
- P6: one comment per `Store` method, on `Clock.sleep` and `IdSource.entropy` (`ts/src/app/ports.ts:9,13,47-58`), and the line on `movesAfterRead` and `rejectNext` (`ts/tests/app/fakes.ts:26`); see PR1 for one that misstates.
- P7: `CountingIds(first = 1, step = 1)` with `next` a field (`ts/tests/app/fakes.ts:116-124`); the report records "six, not seven" itself (`task-3-report.md:30`), since earlier reports are history.

### PR1 · Minor · the comment on `gate` says it compares

Handle: `ts/src/app/ports.ts:56`, `// Compare the returned current tree; throw LodgeError if there is no published state.`, against `src/lodge/app/ports.py:60-62`, "What the gate compares for `current`, the tree `trees` returned".
Failure: `gate` compares nothing; it returns the states the gate compares, and `current` is the tree `trees()` returned, not a tree `gate` returns.
Task 7b's builder implements `SqliteStore.gate` from this line (P6's reason), and the plan's answer `gate({ published: current, checked: [["", current]] })` reads as wrong against it.
Fix: `// What the gate compares for current, the tree trees() returned; a LodgeError when there is no published state.`

### PR2 · Minor · `required` names the wrong thing, and the first new ID is looked up three times

Handle: `ts/src/app/writes.ts:224-227` throws `Error("missing applied record")`, called at `:86` and `:96` for `newIds[0]`, a minted ID, not a record.
Failure: should the invariant ever break (a change to `applyDrafts` that drops a new decision), the message points at the applied records when the missing value is the minted ID, and `required(newIds[0])` is spelled at two sites a reader must check agree.
Fix: `function required<T>(value: T | undefined, what: string): T` with `what` in the message, or one `const owner = newIds[0]` read once where attachments are placed.

### PR3 · Minor · `Lodge.add` leaves its return type to inference, and a test keeps optional chains after its guard

Handles: `ts/src/app/lodge.ts:14`, where `mint` beside it says `Promise<string>` and the plan's interface says `Promise<Added>`; `ts/tests/app/errors.test.ts:40,42`, `original?.message` after `:35` has already thrown on `undefined`.
Failure: none at run time; a later change to `writes.add`'s return type changes `#app`'s public signature without a line in `lodge.ts` saying so, and the `?.` suggests a case the guard has ruled out.
Fix: `): Promise<Added>` on `add`; `original.message` at both lines.

### Checked and clean

- Structure: `sh scripts/check-ts.sh` passes dependency-cruiser (`app` imports only `#core`; no cycle, so `state.ts` and `writes.ts` import nothing of `lodge.ts`), and the largest new file is `writes.ts` at 227 lines.
- `ts/knip.json`'s `entry` gains `src/app/state.ts`, `src/app/writes.ts`, and `tests/app/support.ts` and loses `tests/app/fakes.ts`, as the plan's table says (d-tha8st).
- `ts/tests/parity.json` flips `tests/app/conftest.py`, `tests/app/support.py`, and `tests/app/test_writes_attach.py` to `ported` with `"task": ["3"]`, and leaves `tests/app/test_writes.py` `planned` for Task 4.
- No `Date` and no clock in `app` beyond `time.ts`; check results through `checkResult` (`state.ts:77`); the stale marker inline (`writes.ts:182`).
- The catch in `resolveRef` (`state.ts:86-91`) opens with the rethrow guard, though the rule binds only `core`.
- `ts/src/app/state.ts:74-76` writes out the order of `compareProblems` (`ts/src/core/check-state.ts:149-153`), which `#core` does not export; lane A edits no file of `ts/src/core`, so this is an observation for the next task that edits `#core`'s front door, not a finding.
- No personal path in the untracked `task-3-codex.log` or `task-3-codex-final.txt` (grep for a home folder or the user's name: none).

## Design

### D1 · Minor · the plan's rule that `app` builds check results through `checkResult` has no test

Handle: `ts/tests/structure/calls.ts:95-107` reports an object literal with an `ok` key only when `pkg === "core"`; the plan's Global Constraints extend the rule to `app` (d-snrhjs), and nothing checks it there.
Failure: Task 4 ports `src/lodge/app/reads.py:96`, the second `CheckResult(…)` in `app`; a `{ problems, notes, ok: … }` literal in `reads.ts` would pass the gate, and an `ok` that disagrees with `problems` would reach `lodge check`, which s-q4s548 forbids ("lodge must not show wrong information").
This task complies (`state.ts:77`), so the finding is the missing guard, not this task's code.
Fix: widen the condition to `pkg === "core" || pkg === "app"`, keeping the one exemption `src/core/check-state.ts`, with an `app` case in `ts/tests/structure/core-rules.test.ts`; it tightens a rule rather than loosening one, but it lies outside Task 3's files, so the coordinator places it, most naturally in Task 4's brief.

### Observations, no severity

- Boundaries hold as the plan draws them (d-t7er56): `Wiring` lives in `state.ts`, `lodge.ts` holds one and delegates, and `writes.ts` reads `state.ts` only.
- `writes.ts` is at 227 of 300 lines, and Tasks 11 and 12b extend it (plan line 189); the attachment checks (`attached` and `requireListed`, `writes.ts:135-159`) are the natural seam if a split is needed, which the Task 11 and 12b briefs could name.
- `AddOptions` (`writes.ts:37-41`) types `Lodge.add`'s options but is not exported through `#app`; plan 3 can write the options inline, as the plan's interface does, and Task 6's front-door test settles the surface.
- `afterNewest`'s `now.epochMs % 1000` (`writes.ts:168`) is negative for an instant before 1970, so it would sleep past the next whole second where Python's non-negative `microsecond` would not; no clock this plan uses is that early.
- For the coordinator, repeated from Task 2's review: the brief still says the builder never commits or pushes (`task-3-brief.md:20`) while telling it to commit and push (`:10`); Codex followed `:10` and said so (`task-3-report.md:4,98-99`), and `origin/server-store-a` holds 817f49b.

## Files

Read: `CLAUDE.md`; `lodge spec` (Purpose and the start of Constraints); the plan's header, Global Constraints, "Exports read in a later task", Calls made, Review Focus, and Task 3 (lines 1-83 and 281-310); `task-3-brief.md`; `task-3-report.md`; `task-2-review.md`; the whole diff `cd26279..817f49b`; `src/lodge/app/state.py`, `writes.py`, `lodge.py:1-66`, `ports.py:25-125`; `tests/app/support.py`, `conftest.py`, `test_writes.py`, `test_writes_attach.py`, `fakes.py:280-320`; `ts/src/app/*.ts`; `ts/tests/app/support.ts`, `writes.test.ts`, `writes-attach.test.ts`, `fakes.ts:26-133`; `ts/src/core/index.ts:1-60`, `model.ts:115-135`, `check-change.ts:1-60`, `check-state.ts:1-25,145-153`, `apply.ts:1-40`, `stamps.ts:15-40`, `text.ts:1-25`; `ts/tests/structure/calls.ts:88-115`; `task-3-codex.log` around lines 2380-2432 and by grep.
Not read: the rest of `lodge spec`, the design documents, the probes, plan Tasks 4 to 14 beyond line 189, plan 1's hand-off, `ts/src/core` beyond the lines named, `src/lodge/app/reads.py`, `threads.py`, `confirm.py`, and the rest of the Codex log.

Verdict: 0 Blocking, 1 Important (C1), 4 Minor (PR1, PR2, PR3, D1); the seven parked Task 2 Minors are fixed; Task 3 needs one fix round for C1 before it merges.
