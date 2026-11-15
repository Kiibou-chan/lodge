# Task 6 fix round 1 report

Addressed both Important findings from the Sonnet Task 6 review in `ts/tests/app/exporting.test.ts`.
Production code required no change.

## Changes

- I-1: added `export_files_include_attachments_stored_separately`, using the seven synthetic non-attachment files in `Tree.files`, the attachment path in `Tree.attachments`, and its text in a separate map.
  The expected export includes every file, the attachment text, and both empty keep files.
- I-2: strengthened `wrapped_store_tells_the_exporter_after_a_publish` to assert that one hold exists before the approving publish and that `await inner.held()` is empty afterwards.

## Test-first evidence

The regression assertions were added before running either mutation or the passing suite.
Both mutations ran in a disposable TypeScript source copy created with `tempfile.TemporaryDirectory`, which uses `mkdtemp`, with the existing dependencies linked into that copy.
The copied module was restored after each mutation, and the temporary directory was removed on completion.
The lane's production files were never mutated.

| Mutation in the disposable copy | Result |
|---|---|
| Delete `...attachmentTexts,` from `exportFiles` | Exit 1; `16 pass`, `1 fail`; the new separate-attachment test failed because the attachment was absent. |
| Replace `inner.publish(...args)` with `inner.publish(args[0], args[1], args[2])` | Exit 1; `16 pass`, `1 fail`; the approving publish test failed because the hold remained open. |

Each mutation ran `bun test tests/app/exporting.test.ts tests/app/exporters.test.ts` from the copied TypeScript directory.
Neither failure required changing production code because the existing implementation already satisfies both assertions.

## Validation

| Command | Result |
|---|---|
| `cd ts && bun test tests/app/exporting.test.ts tests/app/exporters.test.ts` | Exit 0; `17 pass`, `0 fail`, and `86 expect() calls`. |
| `sh scripts/check-ts.sh` | Exit 0; `1999 pass`, `0 fail`, and `6958 expect() calls` across 181 files; formatting, types, dependency rules, and unused-code checks passed. |
| `git diff --check` | Exit 0. |

Earlier briefs, reports, and reviews remain untouched.
The coordinator's parked findings remain outside this fix round.
There are no unresolved questions or known concerns within this scope.
