# Task 7a fix round 1 report

C-1 and C-2 are fixed, together with the local Minor findings.
No commit, push, dependency installation, or network operation was performed.
The front door, parity table, and knip configuration are unchanged.

## Findings

- C-1: added `orders_by_instant_across_offsets_then_by_id` in `derive.test.ts`, using the in-memory builder with reverse ID insertion order and mixed offsets.
  Dropping the ID tie-break and comparing dates as text each fail this test independently, as recorded below.
- C-2: `derive-links.test.ts` and `doubts.test.ts` now use `builders.snapshotOf` with arrays, preserving insertion order and avoiding file loading.
  `derivation.ts` accepts only records and areas again.
  Removing the supports sort fails `supports_is_the_reverse_of_rests_on`, as recorded below.
  The updated doubt tests pass, including the two tests which later work has already implemented on this branch.
- C-3: no code change was requested.
  This report uses mutations inside the ordering and supports logic, rather than a throw at function entry.
- P-1: restored the `Derived` contract comment, including ordering, known records, and revival semantics, and comments on imported flag eligibility and skipped undone changes.
  Existing review flag, imported decision, and revival tests pass in the core suite.
  Comments have no separate failing test.
- P-2: asserted the known `Decision` lookup in `doubts.ts` and removed its unreachable optional chain; used the `files` property shorthand in `derive.test.ts`.
  Existing doubt and unparsable-entry tests pass.
  These equivalent clean-ups have no separate failing test.
- D-1: folded `derive-review.ts` into `derive.ts` and removed the former module.
  Restored separate `cleared` and `followsAuthorChange` helpers, with `cleared` comparing decision order directly through the existing comparator.
  `derive.ts` is 238 lines, below the 300-line limit.
  Existing clearing and undone-change tests pass in the core suite.
- D-2: left for the coordinator because its requested fix belongs in Task 7b's brief, outside Task 7a's authorised files.
  The comparator remains private, with C-1 now pinning its ordering behaviour.

## Mutation evidence

Each mutation was applied alone to `derive.ts`, tested, and restored in a `finally` block before the next mutation.
The following command was run for each mutation, with `NAME` set to `orders_by_instant` for the first two and `supports_is_the_reverse` for the third:

```sh
cd ts && bun test tests/core/derive.test.ts tests/core/derive-links.test.ts -t NAME
```

All three commands exited 1 with `error: expect(received).toEqual(expected)`.

| Mutation | Failing test | Expected list | Received list | Last summary |
| --- | --- | --- | --- | --- |
| `return at - bt` | `orders_by_instant_across_offsets_then_by_id` | d-dddddd, d-cccccc, d-bbbbbb, d-aaaaaa | d-dddddd, d-cccccc, d-aaaaaa, d-bbbbbb | 0 pass, 21 filtered out, 1 fail, 1 expect() calls |
| `return byCodePoint(a.date, b.date) || byCodePoint(ai, bi)` | `orders_by_instant_across_offsets_then_by_id` | d-dddddd, d-cccccc, d-bbbbbb, d-aaaaaa | d-bbbbbb, d-cccccc, d-aaaaaa, d-dddddd | 0 pass, 21 filtered out, 1 fail, 1 expect() calls |
| Replace `[...s.entries.keys()].sort(byCodePoint)` with `s.entries.keys()` | `supports_is_the_reverse_of_rests_on` | s-bbbbbb, s-cccccc | s-cccccc, s-bbbbbb | 0 pass, 21 filtered out, 1 fail, 1 expect() calls |

The last lines were respectively `Ran 1 test across 2 files. [48.00ms]`, `[50.00ms]`, and `[48.00ms]`.

## Commands and results

- `uv run --frozen --quiet lodge waiting`: exit 0; both agent and author queues reported `nothing`.
- `cd ts && bun test tests/core/derive.test.ts tests/core/derive-links.test.ts tests/core/doubts.test.ts`: exit 0; `31 pass`, `0 fail`, `66 expect() calls`, `Ran 31 tests across 3 files. [133.00ms]`.
- The three mutation commands above: exit 1 each, with the expected assertion failures.
- `cd ts && bunx --no-install biome check --write src/core/derive.ts src/core/doubts.ts tests/core/derive.test.ts tests/core/derive-links.test.ts tests/core/doubts.test.ts tests/core/derivation.ts`: exit 0; `Checked 6 files in 15ms. Fixed 3 files.`
- `cd ts && bun test tests/core`: exit 0; `548 pass`, `1 todo`, `0 fail`, `1444 expect() calls`, `Ran 549 tests across 37 files. [1146.00ms]`.
- `git diff --check`: exit 0, no output.
- Read-only inspection used `cat`, `rg`, `git status --short`, `git diff`, and `wc -l`; no source outside Task 7a was changed.

The final gate result follows.

`sh scripts/check-ts.sh`: exit 0.

```text
[32m✔[39m no dependency violations found (96 modules, 303 dependencies cruised)

Configuration hints (2)
scripts/*.ts       knip.json  Refine entry pattern (no matches)  
scripts/**/*.ts    knip.json  Refine project pattern (no matches)
bun test v1.3.14 (0d9b296a)

 725 pass
 1 todo
 0 fail
 1950 expect() calls
Ran 726 tests across 44 files. [2.35s]
```
