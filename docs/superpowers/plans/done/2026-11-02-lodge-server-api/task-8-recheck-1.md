# Task 8 recheck 1

Verdict: fix round 1 resolves all four answered findings without a new Important or Minor problem.
Reviewed `git diff 2b63b73 e4c2e5a` against the fix brief, fix report, original reviews, Task 8 brief, and plan constraints.
All executable checks and mutations ran in a detached scratch worktree at `e4c2e5a`, the range head, rather than the later working branch head.
Read `CLAUDE.md` first; `lodge waiting` reported nothing waiting for either an agent or the author.
M-3 remains parked by ruling and was not rechecked.

## Per-finding verdicts

| Finding | Severity | Verdict | Fix-head handles | Evidence |
|---|---|---|---|---|
| I-1 | Important | resolved | `ts/src/core/index.ts:8,34,38,42,56,62,86`; `ts/src/api/index.ts:7` | All six formerly statement-tagged re-export blocks expose a newly added unread export to knip, as detailed below. |
| M-1 | Minor | resolved | `ts/src/core/confirmation.ts:14`; `ts/src/core/model.ts:7,24,28`; `ts/src/core/order.ts:6`; `ts/src/core/render.ts:8`; `ts/src/core/views.ts:138`; `ts/src/api/setup.ts:5` | Restored the eight removed definition tags in scratch, then removed them one at a time, running knip after every removal; every run exited 0 with no output. |
| M-2 | Minor | resolved | `ts/src/api/serve.ts:15`; `ts/tests/api/serve.test.ts:30` | Unmodified tests pass; making the repeated signal do nothing fails both signal-order cases at the second-call assertion. |
| M8-1 | Minor | resolved | `ts/src/core/model.ts:7,24,28`; `ts/src/core/order.ts:6` | The four redundant definition tags are absent and included in the successful one-at-a-time knip removal probes for M-1. |

## Probe results

Every knip probe used exactly `cd ts && bun --bun node_modules/knip/bin/knip.js`.
The unmodified fix head exited 0 with no output, and the restored head did so again after the mutations.

For I-1, added `export const ZZZ_UNREAD = "probe"` to each defining module in turn and added its re-export to the corresponding block, preserving each existing tag's attachment to its named specifier.
Every run exited 1 and reported `ZZZ_UNREAD` at both the definition and the front door:

| Block | Definition reported | Re-export reported |
|---|---|---|
| confirmation | `ts/src/core/confirmation.ts:77` | `ts/src/core/index.ts:5` |
| model | `ts/src/core/model.ts:163` | `ts/src/core/index.ts:28` |
| order | `ts/src/core/order.ts:102` | `ts/src/core/index.ts:53` |
| render | `ts/src/core/render.ts:83` | `ts/src/core/index.ts:66` |
| views | `ts/src/core/views.ts:238` | `ts/src/core/index.ts:83` |
| setup | `ts/src/api/setup.ts:133` | `ts/src/api/index.ts:5` |

These are probe line numbers, including the temporary additions.
Each probe was restored before the next mutation.

For M-1 and M8-1, the restored eight-tag baseline was also silent before removing `MINUTE_FORMAT`, `Quote`, `NumberHandle`, `Imported`, `Placement`, `Placed`, `headParts`, and `ServerParts` successively.
As a control, separately removing each retained definition tag produced exit 1 with precisely its expected finding: `THREADS` at `ts/src/core/threads.ts:21`, `Files` at `ts/src/core/snapshot.ts:13`, and `HeldMessage` at `ts/src/app/ports.ts:110`.
Each required tag was restored immediately.

For M-2, `cd ts && bun test tests/api/serve.test.ts` passed all three tests with 27 assertions at the unmodified fix head.
Removed only `void server.stop(true)` from the repeated-signal branch, leaving its return in place, and ran the same command.
Both SIGINT then SIGTERM and SIGTERM then SIGINT failed at `ts/tests/api/serve.test.ts:30`: expected two stop calls, received one.
The mutated run exited 1 with one pass, two failures, and 19 assertions.
The rejection and cleanup case still passed.
Restored the source before the full gate.

## New-problem checks

No new Important or Minor findings.

All 11 retained `/** @public */` tags have an allowed justification.
The seven tagged core re-export names (`MINUTE_FORMAT`, `Imported`, `NumberHandle`, `Quote`, `Placement`, `Placed`, and `headParts`) and the definition-tagged `THREADS` and `Files` are in Python core's `__all__`, which `ts/tests/core/front-door.test.ts:76` requires.
`HeldMessage` is an allowed addition read by `ts/tests/app/front-door.test.ts:52`.
`ServerParts` is in plan 4's consumed-name table pasted into `task-8-brief.md`, in its `ts/src/main.ts` row.
No block-level public annotation remains.

Compared TypeScript checker export-name sets for each front door using the base and fix-head index files, including type exports and star exports.
`#core` is unchanged at 122 names, and `#api` is unchanged at 13 names.
The passing full gate also exercises both core and app front-door tests.

`ts/tests/api/serve.test.ts:11,50` replaces `Bun.serve` before either invocation of `listen`, returning a fake server with a controlled stop promise.
Signals are emitted in process; the tests open no socket, settle their pending promises, restore the spy, and check signal-handler cleanup.
The mutation run also exits normally after assertion failures, exercising its cleanup path.

All ten changed TypeScript files are within 300 lines, with `ts/src/core/views.ts` the largest at 236 lines and the new test at 69 lines.
The passing repository structure test checks the source and test size rules without any rule changes.
Reviewed the complete diff, including the fix report, for public-repository hygiene: no personal paths, machine names, secrets, or foreign project records were introduced, and the new test's values are synthetic.
`git diff --check 2b63b73 e4c2e5a` passed.

## Validation and workspace

`sh scripts/check-ts.sh` at restored `e4c2e5a` exited 0: Biome with `--error-on-warnings`, TypeScript, dependency-cruiser, knip with no findings, and 1,811 passing tests across 162 files, with zero failures and 5,252 assertions.
Biome emitted 30 informational diagnostics.
The scratch tracked diff was empty after restoration; the scratch worktree, probe changes, dependency symlink, and gate log were removed afterwards.
No source or test file in the review worktree was edited, and nothing was committed.
Only this uncommitted recheck report was written in the review worktree; the existing unrelated untracked reports were left untouched.
No unsettled question required a coordinator ruling.
