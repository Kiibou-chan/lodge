# Final review fix round

Scope: the dispatched small fix round, with no new feature or re-measurement.
The scrubbed review is `final-review.md`, committed first as cc282be and pushed to `read-speed-build`.
PUB-1 is already addressed by e346776; this round preserves it.
The coordinator's decisions in 84e8cd3 were read through `uv run --frozen --quiet lodge show d-cqr414 d-3ck8km d-bbhak7 d-n65rhr --reasoning`.
`lodge waiting` reports nothing waiting for an agent.

## Items

- DEC-1: Task 9, Task 10a, and invariant 4 now cite d-cqr414 and state that every write checks used pages, clearing when over cap after a kept state or at least a tree's file count of inserted units since the last clear.
  The cap formula and 1,900-byte allowance are unchanged.
- DEC-2: Global Constraints, calls 9, 10, and 21, and Task 9 now cite d-3ck8km for one file per build, WAL, `synchronous=NORMAL`, explicit transactions, and pruning with sidecars under the exclusive lock.
  Call 25 records SECOND-1 as d-n65rhr.
  The progress ledger lists all three final-review decisions from 84e8cd3.
  The non-report-file sweep used `rg -n 'd-gvz66f|d-4n5tr6|synchronous=FULL|generation' docs/superpowers/plans/2026-10-31-lodge-at-scale -g '!*-report.md' -g '!plan-report.md'`.
  Current design statements in `plan-fix-2.md`, `plan-fix-3.md`, and `plan-fix-5.md` are rewritten in place; remaining matches describe replaced decisions, Before columns, dated review evidence, or withdrawn proposals.
  The active plan has no match for any of those four patterns.
- STAT-1: Task 8c's R11-B rule names d-bbhak7: writes preserving size, timestamps, and inode, such as a shared memory-map write, remain unseen until stat changes or git's index is refreshed.
  The exact-reader exception is reflected in Global Constraints and call 22.
  The README does not enumerate stale cases, so it needs no stale-case sentence.
- DOC-1: the Reading paragraph states once that deleting the common-directory index folder is safe at any time, with space returning when open connections close.
  Disposable read index links to Reading and keeps the lock-file detail.
- DOC-2: every actual step checkbox in Tasks 1 to 12, including Tasks 8a to 8c, 9c, and 10a to 10c, is ticked against the ledger: 92 complete, zero unchecked task steps.
  The introductory checkbox syntax example remains an example.
- FIX-1: `test_stored_row_without_threads_is_refused` keeps a complete state, removes its encoded `threads` field, writes the malformed row into SQLite, and decodes the persisted value through the production codec.
  It requires `ValueError: invalid cached arity` and verifies `index.state` returns a miss.
  The requested mutant gave `StoredState.threads` the default `()` and removed the codec arity check; the new test failed with `IndexError`, and both mutations were reverted.
  No production change is needed: the existing codec already refuses this row.
- TEST-1: `test_clear_wal_bounded` now asserts a non-empty WAL of at most 16 MiB after the clear commits and before the TRUNCATE checkpoint.
  It runs on this machine; only `test_secure_delete_off` retains the SQLite-default capability skip, after asserting the connection pragma is 0.
  The additional mutant changed the connection's `secure_delete=OFF` to `ON`; the WAL assertion failed at 21,226,272 bytes, proving the bound can fail, and the mutation was reverted.
  The existing production code passes both regressions.

## Validation

`git diff --check` passes, the review copy matches the scrubbed source byte for byte, and the added-text scan finds no personal paths or em-dashes.
The source mutations are fully reverted (`git diff --quiet -- src` passes).

Targeted command: `uv run --frozen pytest tests/gitstore/test_index_db.py tests/gitstore/test_index_states.py tests/app/test_index_review_facts.py tests/core/test_codec.py -q -rs`.
Result: `76 passed, 1 skipped in 1.29s`.
Skip: `SQLite does not default secure_delete to 1; pragma assertions passed`.

Mutation failure output excerpts, with temporary fixture paths omitted for the public repository:

```text
$ uv run --frozen pytest tests/gitstore/test_index_states.py::test_stored_row_without_threads_is_refused -q
        with pytest.raises(ValueError, match="invalid cached arity"):
>           decode(stored_raw)
tests/gitstore/test_index_states.py:28:
>           raw = values[i]
E           IndexError: list index out of range
src/lodge/core/codec.py:166: IndexError
FAILED tests/gitstore/test_index_states.py::test_stored_row_without_threads_is_refused
1 failed in 0.71s

$ uv run --frozen pytest tests/gitstore/test_index_db.py::test_clear_wal_bounded -q
>       assert 0 < Path(str(filename(tmp_path)) + "-wal").stat().st_size <= 16777216
E       AssertionError: assert 21226272 <= 16777216
tests/gitstore/test_index_db.py:197: AssertionError
FAILED tests/gitstore/test_index_db.py::test_clear_wal_bounded - AssertionErr...
1 failed in 0.80s
```

An initial invocation set `LODGE_INDEX=off` globally and exited 1: `19 failed, 2219 passed, 2 skipped in 210.37s (0:03:30)`.
Those end-to-end tests expect an index to be created and retained, which that environment setting disabled.
The normal frozen gate, `UV_FROZEN=1 sh scripts/check.sh`, exits 0 without that override.
Formatting: `693 files already formatted`; Ruff: `All checks passed!`; strict mypy: `Success: no issues found in 301 source files`; Vulture: silent.
Result line: `2238 passed, 2 skipped in 212.54s (0:03:32)`.
`lodge check --gate`: `ok`, with the existing `note: area storage: order changed`.
The two capability skips are libyaml being present and SQLite not defaulting secure_delete to 1; the WAL-bound regression runs and passes.

All dispatched items are complete, with no NEEDS_CONTEXT item or new concern.
No benchmark or timing table was rerun or changed.
