# Task 14 minors report

Completed the selected parked minors after reading the Task 5, 6, 9, 11 and 12c reviews and the progress ledger.

- Task 9: replaced the stale-confirmation leg with a separate SQLite test whose future-dated agent decision reaches the write check, returns `CHECK_FAILED`, and leaves events unchanged. One `held` predicate selects parity rows; its plan list preserves plan 1 file-existence coverage without imposing test-name parity on rewritten structure rules. A planted plan 2 changed row proves missing names fail. `seeded` reuses `setup`, whose project and owner parameters retain their defaults.
- Task 5: shared null-aware `required`, `Q`, `PATH` and `opened` in app test support; parametrised titles include the input, including `close_with_text`.
- Task 6: removed the dead capitals branch and redundant optional/default handling in the front-door test. `behindArea` explicitly refuses a missing decision rather than hiding a broken invariant.
- Task 11: documented the syntactic people-call rule's limits; waiting threads are partitioned in one pass without an empty-string sentinel; removed the misplaced `Forbidden` class assertion.
- Task 12c: added an ask using `ITEM-1` on an entry, asserting the held reference is `s-aaaaaa`. This fixture gives the entry the code without the existing decision's conflicting code.

`ts/knip.json` already has exactly the two requested entry patterns and was clean on arrival: commit `8e501b5` already committed that edit. No further knip change was needed.

The brief's skipped items remain deferred: whitespace-only author where, codec speed, Task 7b D-1, and Task 12b M-6/M-7. No dependencies added; every TypeScript module remains at most 300 lines.

## Verification

The new confirmation and code-reference tests were added before the refactors and pass against the existing implementation. No intended valid-state behaviour changed. Targeted mutations were applied individually and restored, running the named suites with `bun test` from `ts`:

| File:line | Old text | New text | Result |
| --- | --- | --- | --- |
| `ts/src/app/writes.ts:129` | `if (!check.ok)` | `if (false)` | Store checked-writes suite fails, including the new confirmation test |
| `ts/src/app/threads.ts:95` | `ref: raises !== null ? thread.about : thread.id,` | `ref: raises !== null ? "ITEM-1" : thread.id,` | New code-reference test fails |
| `ts/tests/parity.test.ts:15` | `return row.status === "ported" \|\| (row.status === "changed" && plans.includes(row.plan ?? 0));` | `return row.status === "ported";` | New changed-row fixture test fails |

Final `sh scripts/check-ts.sh`: exit 0. Biome, TypeScript, dependency-cruiser and knip pass. Final test output:

```text
1289 pass
2 todo
0 fail
3336 expect() calls
Ran 1291 tests across 104 files. [4.05s]
```

`git diff --check` passes. The session log is excluded from the commit.
