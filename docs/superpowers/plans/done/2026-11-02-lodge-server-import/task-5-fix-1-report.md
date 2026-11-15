# Task 5 fix round 1 report

Both review findings are fixed on `server-import-import`.
Only author message identity lines change, and failures during server mapping or validation are attributed to `server`.

## Per-file changes

- `ts/src/app/importing.ts`: retains the unchanged source writer comparison, renders the mapped author messages through `writeThread`, and copies only their rendered `by` line into canonical message metadata in the source text.
  Non-author messages never enter the mapped writer, so identity collisions cannot rewrite their timestamps or other bytes.
  Canonical source writing escapes message-like body headings, which keeps the replacement confined to metadata.
  Source and mapped writer exceptions have separate catches, problem lists, stages, and refusal sentences.
  The remaining mapped-writer refusal reads `the server cannot write this file with the owner as its author: <writer error>`.
  The module has 200 lines.
- `ts/tests/app/importing.test.ts`: adds both requested regressions, with shared synthetic fixture and source-canonicality checks.
  The module has 260 lines.
- `docs/superpowers/plans/2026-11-02-lodge-server-import/task-5-fix-1-report.md`: records the changes, failing evidence, checks, and deviations.

## Test-first evidence

The first run of both new tests found a test-helper setup error before reaching the assertions: `TypeError: undefined is not an object (evaluating 'tree.files.keys')`.
The empty tree needed explicit `rev` and `files` arguments.
That helper was corrected and both tests were rerun against unchanged production code.

`role_collision_preserves_every_non_author_line` changes the first message to `by: ana`, adds `where: "chat"`, keeps its timestamp unquoted, and keeps the author reply.
It first verifies that source checking succeeds and the source writer reproduces the text exactly.
Its first substantive failing output was:

```text
error: expect(received).toBe(expected)
- when: 2026-11-02T18:56:30+01:00
+ when: "2026-11-02T18:56:30+01:00"
(fail) role_collision_preserves_every_non_author_line
```

`mapped_thread_failure_is_at_the_server_stage` uses the same role collision without adding `where`, again verifies source validity and canonicality, and expects a check 1 refusal at the thread path mentioning `where`.
Its first substantive failing output was:

```text
error: expect(received).toBe(expected)
Expected: "server"
Received: "lodge 0.2"
(fail) mapped_thread_failure_is_at_the_server_stage
```

The combined red run ended with `0 pass`, `16 filtered out`, `2 fail`, and `8 expect() calls`.
Both failures were observed before changing production code.

## Commands and results

- `uv run --frozen --quiet lodge waiting`: exit 0, ending `waiting for the author` and `nothing`; nothing was waiting for an agent either.
- `uv run --frozen --quiet lodge guide`: exit 0, ending with the exit-code guide.
- From `ts`, `bun test tests/app/importing.test.ts -t 'role_collision_preserves_every_non_author_line|mapped_thread_failure_is_at_the_server_stage'`: exit 1, with the two substantive failures quoted above after correcting the helper.
- From `ts`, `bun test tests/app/importing.test.ts tests/app/import-store.test.ts`: exit 0, ending `28 pass`, `0 fail`, `122 expect() calls`, and `Ran 28 tests across 2 files`.
- First `sh scripts/check-ts.sh`: exit 1 on formatting, ending `Found 2 errors`, `Found 30 infos`, and `error: script "check" exited with code 1`.
- From `ts`, `bunx biome check --write src/app/importing.ts tests/app/importing.test.ts`: exit 0, ending `Checked 2 files in 8ms. Fixed 2 files.`
- Final `sh scripts/check-ts.sh`: exit 0, ending `1891 pass`, `0 fail`, `6560 expect() calls`, and `Ran 1891 tests across 171 files`.
  Type checking, dependency checks, unused-code checks, and structure tests passed.
  Biome reported 30 informational diagnostics and no errors.
- `git diff --check`: exit 0, no output.
- `sh scripts/check.sh`: exit 0, including `1399 passed in 46.04s`, the lodge gate, and another TypeScript gate with `1891 pass` and `0 fail`.
  Its last differential lines were `418 records, 10 areas, 0 threads, 0 problems, 120 queries, 428 rewritten files`, `0 differences`, `1 pass`, `0 fail`, `7 expect() calls`, and `Ran 1 test across 1 file`.

## Deviations

The mapped writer now receives only author messages, and its output supplies only the replacement identity line.
This follows the coordinator's ruling that every other byte of a thread must be preserved.
The missing-`where` probe is consequently refused by server parsing rather than by the mapped writer, still at stage `server`.
No dependencies, structure rules, earlier briefs, earlier reports, reviews, or frozen documents changed.
