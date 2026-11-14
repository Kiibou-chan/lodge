# Task 2 review

Commit under review: 5ebe9f5 on `server-store-a`, diffed against `server-store` (`git diff server-store..server-store-a -- ts`).
Gate: `sh scripts/check-ts.sh` in `/var/tmp/lodge-store-a` exits 0, 941 pass, 0 fail, 2328 expect() calls.
Probes and mutations ran in a detached scratch worktree at 5ebe9f5, removed afterwards; the branch under review was not edited.

## Correctness

No Blocking or Important finding.

What was verified, and how:

- `stampOf` and `minuteOf` (`ts/src/app/time.ts:3-20`) agree with Python's `datetime.isoformat(timespec="seconds")` and `strftime("%Y-%m-%d %H:%M")` on 2000 generated instants from 1938 to 2065 (negative `epochMs` included) at offsets from -18:00 to +18:00 with a millisecond fraction: 0 mismatches (bun dump compared in `python3`).
  Review Focus 6 holds: the offset is the clock's, the minute is local to it, and `app` reads no local zone (the `calls.ts` rule at `ts/tests/structure/calls.ts:144-152` covers `Date` and the local getters in `app`).
- `FixedClock.sleep` (`ts/tests/app/fakes.ts:109-112`) with Task 3's `1 - (epochMs % 1000) / 1000` lands on a whole second for every one of the 1000 millisecond residues at `START`'s magnitude, so the float `seconds * 1000` does not leave a fractional `epochMs` for `_after_newest`'s floor.
- `MemoryStore` (`ts/tests/app/fakes.ts:18-90`) matches `tests/app/fakes.py:225-290` method by method: `trees` reads before it lands a move, `publish` lands through `land`, which is `fakes.py:273-277`'s inline update, and `gate`, `commit`, `freshness`, and the fields carry their Python values.
- `CountingIds.entropy` (`ts/tests/app/fakes.ts:113-120`) refuses a value outside 0 to 255, as Python's `bytes([value])` does, where `Uint8Array.fill` would wrap silently.
- The errors (`ts/src/app/errors.ts:3-14`) carry exit codes 2, 2, 1, 1, the class name as `name` through `new.target`, and the inheritance of `src/lodge/app/errors.py:8-25`; `coreSettings` rethrows anything not a `SettingsError`, as the plan's catch rule asks.
- `ports.ts` and `results.ts` hold every name, field, and outcome text of `ports.py`, `results.py`, and the plan's "Interfaces for plans 3 and 4" as of Task 2, `Store` with the five methods and `attachmentTexts` and no `approves`, and `AddOutcome` without `HELD`.
- The plan's tests are all present under the plan's titles (`time.test.ts`, `ports.test.ts`, `errors.test.ts`), each first seen failing on the missing `#app` (report lines 24-38), which the Global Constraints count as failing.

## Practice

### P1 · Minor · the default-filling test passes when a default overwrites a passed value

Handle: `ts/tests/app/ports.test.ts:22-46`, against `ts/src/app/ports.ts:34-36,42-44` and `ts/src/app/results.ts:17-19,36-38,48-52,60-62`.
Failure: I reversed the spread in all six functions (`{ ...value, detail: "" }` and the like) and `bun test tests/app` still gave 9 pass, 0 fail.
A `written({ …, about: "s-aaaaaa" })` would then return `about: null`, caught only when Task 5 carries `test_thread_ops.py:33`, and `added`'s `freshness`, `minted`, and `paths` are asserted by no app test in `tests/app/test_writes*.py`.
Fix: in the same test, call each function once more with its defaulted fields given (`committed({ outcome, detail: "x" }).detail === "x"`, and so on) and assert they survive.

### P2 · Minor · the settings error's message is checked only for its prefix

Handle: `ts/tests/app/errors.test.ts:19-22`, against `ts/src/app/errors.ts:20`.
Failure: mutating the message to `` `.lodge.toml: ` `` (dropping `error.message`) leaves both tests passing (ran it), so a port that lost the reason, which `src/lodge/app/errors.py:33` carries as `{error}`, goes unnoticed; removing the rethrow guard at `errors.ts:19` also survives (ran it), but that one cannot be reached without injecting a failing parser, so I do not ask for it.
Fix: assert the whole message, `".lodge.toml: " + m`, where `m` is the message `parseCoreSettings` throws for the same table, caught in the test.

### P3 · Minor · the settings error loses its cause

Handle: `ts/src/app/errors.ts:4-7,20`.
Failure: Python raises `LodgeError(...) from error` (`src/lodge/app/errors.py:33`), so the `SettingsError` stays reachable as `__cause__`; `LodgeError`'s constructor takes only a message, so no caller, plan 3's API included, can reach the original error or chain one.
Fix: `constructor(message: string, options?: ErrorOptions) { super(message, options); … }` and `throw new LodgeError(…, { cause: error })`.

### P4 · Minor · the attachments folder is written out instead of taken from the core

Handle: `ts/tests/app/fakes.ts:51`, duplicating `ATTACHMENTS` of `ts/src/core/snapshot.ts:31`, exported through `#core`.
Failure: a change to the folder in the core leaves `MemoryStore.attachmentTexts` answering with nothing, and no test reads it until plan 4.
Fix: import `ATTACHMENTS` from `#core` and filter on it.

### P5 · Minor · two-digit padding written three ways in twenty lines

Handle: `ts/src/app/time.ts:5,7,15`.
Failure: none at run time (probe above); `stampOf`'s offset repeats `String(...).padStart(2, "0")` twice on one 150-character line beside the `pad` closure that `localParts` keeps to itself, which makes the offset arithmetic the hardest line of the file to read.
Fix: hoist `pad` to module scope and write the offset as `${sign}${pad(Math.floor(offset / 60))}:${pad(offset % 60)}`.

### P6 · Minor · the ports' contracts are not carried

Handle: `ts/src/app/ports.ts:8-13,45-55`, against `src/lodge/app/ports.py:79-118`; `ts/tests/app/fakes.ts:18,91,99`, against `tests/app/fakes.py:226-230,294,312`.
Failure: Task 7b's builder implements `SqliteStore` against `Store` with no statement in the code that `publish` answers REJECTED when a path in `writes` or the tip no longer matches `base`, that `gate` throws a `LodgeError` when there is no published state, that `commit` leaves other staged files staged, or that `IdSource.entropy` gives at least six bytes; the plan's interface block keeps only the last.
Plan 1 carried docstrings as one-line comments where they state a fact (`ts/src/core/snapshot.ts:14,37`), so this is not a broken rule, but these are the contracts the second store implements.
Fix: one fact comment per method of `Store`, `Clock.sleep`, and `IdSource.entropy`, and on `MemoryStore` the line saying how `movesAfterRead` and `rejectNext` land another session's change.

### P7 · Minor · two small departures from the plan's names and the report's count

Handle: `ts/tests/app/fakes.ts:102-105` names `CountingIds`'s first parameter `next` where the plan (plan line 269) and `tests/app/fakes.py:314` name it `first`; `task-2-report.md:16` says "all seven default-builder checks", and `ports.test.ts:26-45` has six, one per function.
Failure: none at run time, since every call is positional; a reader matching the plan's `CountingIds(first = 1, step = 1)` or the report's count against the code finds neither.
Fix: `constructor(first = 1, public step = 1) { this.next = first; }` with `next` a field, and "six" in the report.

Checked and clean: no earlier brief, report, or review edited (`git show --stat 5ebe9f5` touches only `task-2-report.md` in the plan folder); `ts/knip.json` gains exactly `tests/app/fakes.ts`; `ts/package.json` gains `#app` and no dependency; `ts/tests/parity.json` flips `tests/app/fakes.py` to `ported` with `"task": ["2"]`; no file near 300 lines; no personal path in the code or the untracked Codex logs.

## Design

No Blocking or Important finding.

- Boundaries hold: `app` imports only `#core` (`app-imports` rule, `ts/.dependency-cruiser.cjs`), `time.ts` depends on `ports.ts` and not the reverse, and `results.ts` takes `Committed` from `ports.ts` as `results.py` does.
- `name` through `new.target.name` (`errors.ts:6`) gives Task 11's `Forbidden` its name without a line of its own, which suits the plan better than core's per-class `override name` field (`ts/src/core/settings.ts:3`).
- Observation, no severity: knip never reports an unused export reached through `#app`'s `export *` front door (an unused `export const` appended to `src/app/ports.ts` is not reported, while one appended to `tests/core/builders.ts` is), as for `#core`; so `#app`'s surface has no unused-export guard until Task 6's `front_door_exports_nothing_else` (plan Task 6), and the plan's d-tha8st table rightly lists only `tests/app/fakes.ts` for Task 2.
- Observation for the coordinator, no severity: the brief tells the builder to commit and push (`task-2-brief.md:10`) while its repeated Global Constraints say the builder never stages, commits, or pushes (`task-2-brief.md:20`); Codex followed line 10 under d-94tynf and said so (`task-2-report.md:65`), so later briefs could drop the stale bullet.

## Files

Read: `CLAUDE.md`; the plan's header, Global Constraints, Calls made, Review Focus, Interfaces, Tasks and lanes, and Tasks 1 to 3 (lines 1-300) and Task 6's test bullet; `task-2-brief.md`; `task-2-report.md`; the whole Task 2 diff; `src/lodge/app/errors.py`, `ports.py`, `results.py`; `tests/app/fakes.py`; `src/lodge/app/writes.py:80-160`; `tests/app/test_writes.py:25-45`; `tests/app/test_writes_dates.py:20-75`; `ts/src/core/snapshot.ts:13-36`; `ts/tests/core/builders.ts:80-119`; `ts/tests/structure/calls.ts:30-170`; `ts/.dependency-cruiser.cjs`; `ts/knip.json`; `ts/tsconfig.json`; `ts/tests/parity.json:1-12`; lodge `d-ca6wbw`, `d-tha8st`.
Not read: `lodge spec` in full, the probes, the plan's Tasks 4, 5, and 7a to 14, plan 1's ledger and hand-off, the untracked `task-2-codex.log` beyond a grep for personal paths, and the rest of `ts/src/core`.

Verdict: 0 Blocking, 0 Important, 7 Minor; Task 2 may merge, the Minors parked for Task 3, which touches `fakes.ts`, `ports.test.ts`'s neighbours, and `errors.ts`'s callers.
