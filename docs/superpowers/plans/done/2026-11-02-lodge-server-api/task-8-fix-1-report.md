# Task 8 fix 1 report

Fixed I-1, M-1, M-2, and M8-1 on `server-api-c`, starting at `2b63b73822aeebfe841738ff8e5ea9815352beb6`.
Read `CLAUDE.md`, the briefs, the required plan sections, both reviews, and the Task 6 and 7a reports.
`uv run --frozen --quiet lodge waiting` reported nothing waiting for either an agent or the author.

## I-1: re-export tags conceal unread names

Replaced all six statement-level tags in `ts/src/core/index.ts` and `ts/src/api/index.ts` with tags on individual specifiers, each on its own line immediately before the name.
Only the specifiers knip reported are tagged: `MINUTE_FORMAT`, `Imported`, `NumberHandle`, `Quote`, `Placement`, `Placed`, `headParts`, and `ServerParts`.
The exported names and structure rules are unchanged.

Before the fix, adding `export const ZZZ_UNREAD = "probe"` in `confirmation.ts` and re-exporting it in the tagged block made knip exit 0 with no output, reproducing the review's missed finding.
Removing the statement tags made knip exit 1 with these findings:

```text
Unused exports (4)
ZZZ_UNREAD     src/core/confirmation.ts:78:14
ZZZ_UNREAD     src/core/index.ts:5:3
MINUTE_FORMAT  src/core/index.ts:9:3
headParts      src/core/index.ts:76:3
Unused exported types (6)
ServerParts   type  src/api/index.ts:4:46
Imported      type  src/core/index.ts:34:8
NumberHandle  type  src/core/index.ts:37:8
Quote         type  src/core/index.ts:40:8
Placement     type  src/core/index.ts:53:8
Placed        type  src/core/index.ts:57:15
```

After the specifier tags and definition-tag removals, repeating the unread-export probe exited 1:

```text
Unused exports (2)
ZZZ_UNREAD  src/core/confirmation.ts:77:14
ZZZ_UNREAD  src/core/index.ts:5:3
```

Removed the probe and reran knip: exit 0, no findings.

## M-1 and M8-1: unnecessary definition tags

Removed each definition tag separately and ran `cd ts && bun --bun node_modules/knip/bin/knip.js` after every removal.
The following removals each exited 0 with no output, so each removal was retained:

| File | Definition tags removed |
|---|---|
| `ts/src/core/confirmation.ts` | `MINUTE_FORMAT` |
| `ts/src/core/model.ts` | `Quote`, `NumberHandle`, `Imported` |
| `ts/src/core/order.ts` | `Placement` |
| `ts/src/core/render.ts` | `Placed` |
| `ts/src/core/views.ts` | `headParts` |
| `ts/src/api/setup.ts` | `ServerParts` |

Individually removing the other three definition tags produced these exit-1 findings:

```text
Unused exported types (1)
Files  type  src/core/snapshot.ts:13:13

Unused exports (1)
THREADS  src/core/threads.ts:21:14

Unused exported types (1)
HeldMessage  interface  src/app/ports.ts:110:18
```

Restored each required tag immediately and reran knip after each restoration: exit 0, no findings each time.
Only `Files`, `THREADS`, and `HeldMessage` retain definition tags.
M8-1's four definitions are included in the eight removals above, with their required front-door specifier tags retained.
There is no failing application test for these redundant tags; the differential knip runs establish which tags are necessary.

## M-2: repeated signals force shutdown

`ts/src/api/serve.ts` now calls `server.stop(true)` when a signal arrives during graceful shutdown.
The first signal still calls `server.stop()` without arguments, and its promise still controls completion and signal-handler cleanup.

Added `ts/tests/api/serve.test.ts`, replacing `Bun.serve` with a fake server whose `stop()` returns a controlled promise.
No test opens a socket.
Both SIGINT then SIGTERM and SIGTERM then SIGINT assert the graceful call, force call, pending promise, and removal of both handlers after settlement.
A rejection test asserts handler removal and preservation of the original error.
The fake is restored and pending shutdown settled in `finally` blocks, including after an assertion failure.

Before changing `serve.ts`, `cd ts && bun test tests/api/serve.test.ts` exited 1:

```text
error: expect(received).toHaveBeenCalledTimes(expected)
Expected number of calls: 2
Received number of calls: 1

1 pass
2 fail
19 expect() calls
Ran 3 tests across 1 file.
```

Both signal-order cases failed at the second-call assertion.
After the change, the same command exited 0 with 3 passes, 0 failures, and 27 assertions.
The final gate's knip run also exited 0 with no findings.

## Validation and scope

The first full gate reached TypeScript and rejected the fake server's direct type assertion and unchecked listener-count array indexing.
Changed the fake's assertion to pass through `unknown` and made the count arrays readonly tuples, then formatted the test with Biome.
`sh scripts/check-ts.sh` subsequently exited 0: Biome with `--error-on-warnings`, TypeScript, dependency-cruiser, knip with no findings, and 1,811 passing tests across 162 files, with zero failures and 5,252 assertions.
Biome's 30 informational diagnostics are unchanged in severity and do not fail the gate.
`git diff --check` passed.
No structure check, dependency, gate script, or existing test changed.
M-3 remains parked, including the synchronous bind-error behaviour.
The existing unrelated untracked report files were left untouched.
