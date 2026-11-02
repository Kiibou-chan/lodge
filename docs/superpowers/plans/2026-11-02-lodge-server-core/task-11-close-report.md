# Task 11 closing report

Status: DONE_WITH_CONCERNS.

## Changes

- Added `ts/tests/core/front-door.test.ts` with `front_door_exports_every_python_name` and `front_door_exports_nothing_else`.
  The tests read Python's `__all__`, convert snake_case names to camelCase, and use TypeScript's parser and checker to enumerate front-door exports, including types, wildcard exports, and aliases.
  Extra exports must originate in `errors.ts`, `text.ts`, or `stamps.ts`, or be a named constructor defined alongside its exported interface.
  The constructor allowance includes `checkResult` under ruling d-qe513h.
- `ts/src/core/index.ts` needed no lasting changes: the merged front door already meets both tests.
- `ts/tests/parity.json` needed no changes: every plan 1 row is `ported` or `changed`.
  The remaining 40 `planned` rows comprise 10 in plan 2, 27 in plan 3, and 3 in plan 4.
- `ts/knip.json` needed no changes: its entry is already `["tests/**/*.test.ts", "scripts/*.ts"]`.
- Added this report.

No review files were edited, and no commit, push, installation, or network operation was performed.

## First failing evidence

The tests initially passed against the already merged implementation.
Before accepting them, each was run against a mutation of `index.ts`, as allowed for tests over previously ported code.
Both mutations were restored immediately, and no implementation changes were required.

Removing `applyDrafts` from the explicit export failed with exit 1:

```text
bun test v1.3.14 (0d9b296a)

tests/core/front-door.test.ts:
66 |   );
67 | }
68 | 
69 | test("front_door_exports_every_python_name", () => {
70 |   const actual = new Set(exports.map((symbol) => symbol.name));
71 |   expect(names.filter((name) => !actual.has(name ?? ""))).toEqual([]);
                                                               ^
error: expect(received).toEqual(expected)

- []
+ [
+   "applyDrafts",
+ ]

- Expected  - 1
+ Received  + 3

      at <anonymous> (ts/tests/core/front-door.test.ts:71:59)
(fail) front_door_exports_every_python_name [0.94ms]

 1 pass
 1 fail
 2 expect() calls
Ran 2 tests across 1 file. [990.00ms]
```

Adding `export { compareOrderKeys } from "./derive.ts"` failed with exit 1:

```text
bun test v1.3.14 (0d9b296a)

tests/core/front-door.test.ts:
72 | });
73 | 
74 | test("front_door_exports_nothing_else", () => {
75 |   expect(
76 |     exports.filter((s) => !expected.has(s.name) && !isAllowedExtra(s)).map((s) => s.name),
77 |   ).toEqual([]);
         ^
error: expect(received).toEqual(expected)

- []
+ [
+   "compareOrderKeys",
+ ]

- Expected  - 1
+ Received  + 3

      at <anonymous> (ts/tests/core/front-door.test.ts:77:5)
(fail) front_door_exports_nothing_else [3.65ms]

 1 pass
 1 fail
 2 expect() calls
Ran 2 tests across 1 file. [806.00ms]
```

## Commands and results

- `uv run --frozen --quiet lodge waiting`: `waiting for the author`, `nothing`; the agent queue was also empty.
- `uv run --frozen --quiet lodge show d-442r2f --reasoning`: confirmed the checks belong in this closing step after lane merges.
- `uv run --frozen --quiet lodge show d-qe513h --reasoning`: confirmed the shared `checkResult` constructor.
- `cd ts && bun test tests/core/front-door.test.ts`: `2 pass`, `0 fail`, `2 expect() calls`, across one file.
- The same command under each mutation: `1 pass`, `1 fail`, `2 expect() calls`, across one file.
- Python parity inspection: `Plan 1 incomplete: []`; planned counts `{1: 0, 2: 10, 3: 27, 4: 3}`.
- `grep -c '"planned"' ts/tests/parity.json`: `40`.
- `cd ts && bunx --no-install biome check --write tests/core/front-door.test.ts`: `Checked 1 file in 6ms. No fixes applied.`
- `cd ts && bunx --no-install tsc --noEmit -p .`: exit 0, no output.
- `cd ts && bunx --no-install knip`: exit 0, no unused exports.
  Its last lines were the two configuration hints below.
- Final verification command: `sh scripts/check-ts.sh`, with its output captured in `/tmp/task-11-close-gate.log`.
  The final gate result and last lines follow below.

## Concerns

Knip reports two configuration hints because `scripts/*.ts` and `scripts/**/*.ts` currently match no files.
The required entry patterns are retained, and there are no unused-export findings.
No test needed a TypeScript behaviour exception, and no missing TypeScript counterpart was found.

## Final gate result

`sh scripts/check-ts.sh` exited 0.
It was the last verification command run.
Its last lines were:

```text
bun test v1.3.14 (0d9b296a)

 851 pass
 0 fail
 2154 expect() calls
Ran 851 tests across 56 files. [3.08s]
```
