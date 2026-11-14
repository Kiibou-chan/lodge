# Task 3 recheck 1

Diff `2c294d6..a79cb49`.

- C1: fixed. `ts/tests/app/support.ts:36-43` adds `raises(promise, Class, pattern)`, which asserts class and pattern. All nine carried sites use it (`writes-attach.test.ts:41-52`, `:57-69`, `:72-80`, `:83-90`; `writes.test.ts:65-71`, `:79`, `:114-118`). No bare `rejects.toThrow` remains in either file.
- C1 probe, run in a detached scratch worktree at `a79cb49`, each reverted: `LodgeError` swapped for `Error` at `writes.ts:149`, `:152`, `:153`, `:162`, `:180`, `:212`. Every swap now fails a test (1, 6, 1, 1, 1, 1 failing), where the review saw 0.
- PR1: fixed. `ts/src/app/ports.ts:56` carries the suggested wording.
- PR2: fixed. `required(value, what)` at `ts/src/app/writes.ts:232-234`; call sites `:87`, `:101-102`, `:226-227` pass a name.
- PR3: fixed. `Promise<Added>` at `ts/src/app/lodge.ts:18`; `?.` removed at `ts/tests/app/errors.test.ts:40,42`.
- `sh scripts/check-ts.sh` passes: 967 pass, 0 fail, no dependency violations.
- No earlier brief, report, or review is edited; the diff touches only the new `task-3-fix-1-report.md` under the plan folder.
- New problems: none.

Blocking 0, Important 0
