# Final fix wave 1 report

Completed I-1, I-2, I-3, M-1, M-5, M-6, and the four requested M-7 assertions.
The remaining review findings are outside this round.

## Changes

- Added one staged-drift fixture over `MemoryStore`, with decisions absent from current files but present in the published tree.
  Both `ask` and `reply` return `CHECK_FAILED` without attempting publication.
  An `add` of a decision rewrite already present in current also returns `CHECK_FAILED` without attempting publication.
- Added a two-project isolation test covering current and published trees, owners, project members, and attachment texts.
  Own files below and above the attachment range distinguish both range bounds.
- Added `lodge/a\b` to the path refusals.
- Removed the redundant `base.rev` format guard, retaining the existing stale and malformed revision rejection test and the transactional revision comparison.
- Added assertions for ascending held-event order, sorted member names, an empty publish preserving the head revision, and `storeFor` attributing a file event to the supplied actor.
  The member test reverses unordered SQLite queries to distinguish explicit sorting from incidental index order.
- Moved `close` into an internal writer options type.
  Public `ask`, `reply`, and `close` options no longer accept it.
  `Lodge.close` supplies the flag, and internal approval replay retains the held close operation.

## Test-first evidence

Each mutation below was applied individually, its targeted tests run and observed failing, and the original source restored.
No mutation remains in the worktree.

| Mutation | Result |
| --- | --- |
| Ignore the thread check | Fails |
| Use current as the thread check baseline | Fails |
| Use current as the add check baseline | Fails |
| Remove the tree files project filter | Fails |
| Remove the tree owners project filter | Fails |
| Remove the project members filter | Fails |
| Remove the attachment project filter | Fails |
| Remove the attachment lower bound | Fails |
| Remove the attachment upper bound | Fails |
| Remove the backslash refusal | Fails |
| Reverse held-event order | Fails |
| Remove member sorting | Fails |
| Set the touched revision to zero | Fails |
| Replace the supplied store actor with author | Fails |

Before the options change, `tsc` failed with three unused `@ts-expect-error` directives, demonstrating that all three public methods accepted `close`.
After the change, those compile-time regression assertions pass.
The head-revision test uses the public store interface, preserving the front-door import rule.

## Validation

`sh scripts/check-ts.sh` passes: Biome, TypeScript, dependency-cruiser (201 modules, no violations), knip, and Bun tests.
Bun reports 1299 passing tests, 2 existing todo tests, and 0 failures across 108 files.
`git diff --check` passes.
No dependency was added, and all changed modules remain below 300 lines.
