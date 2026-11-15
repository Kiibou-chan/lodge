# Final fix wave 1

Branch: `server-import-final`.
The review findings below refer to the whole-branch Sonnet review supplied with the brief.
Commands prefixed with `bun` ran from `<worktree>/ts`; other commands ran from `<worktree>`.
Output excerpts omit timing and replace disposable paths with placeholders.

## Important I-1: force-push regression guard

`push_without_force` now puts a forwarding git shim first on `PATH`, logs the push arguments, and asserts the complete safe argument list.
This rejects `--force`, `-f`, lease flags, and `+` refspecs, including additions that would still produce a successful push.
The existing remote-content and unchanged-local-head assertions remain.
The test restores all three environment variables in `finally`, and uses the existing isolated temporary repositories.

The first shim attempt failed with `ENOENT: no such file or directory, open '<temporary-folder>/arguments'` because git receives `-C REPOSITORY` before the command.
The corrected shim checks argument three and logs after those two arguments.
With the requested mutation applied to the production push list, `bun test tests/git/export.test.ts` exited 1:

```text
error: expect(received).toEqual(expected)
    "push",
+   "--force",
    "--porcelain",
(fail) push_without_force
 22 pass
 1 fail
 44 expect() calls
Ran 23 tests across 1 file.
```

The mutation was reverted before any production refactoring.
The same command then exited 0:

```text
 23 pass
 0 fail
 47 expect() calls
Ran 23 tests across 1 file.
```

## Minor 1: shared export rules, types, and binding

Read `ts/tests/structure/{table,edges.test,layout.test,calls,guards}.ts` first.
There is no `ts/tests/structure_rules` path; the active table already allows both `git -> app` and `store -> app`.
No structure rule or allowed edge changed.
The app front-door inventory now names the shared path rule alongside the existing export helpers.
`app/export-rules.ts` owns the branch-name, remote-prefix, and outside-`lodge/` rules, plus the single `ExportTarget` and `ExportOutcome` definitions.
`git/export.ts` imports these through `#app`, and `store/sqlite-store.ts` uses the same path rule.
`Exporters` imports the same types internally.
Both Proxy bodies call one `boundMember` helper; existing receiver and publish-notification tests remain in force.

First added the shared-path-rule test through the app front door.
`bun test tests/app/exporting.test.ts` exited 1 before implementation:

```text
SyntaxError: Export named 'lodgePathProblem' not found in module '<worktree>/ts/src/app/index.ts'.
 0 pass
 1 fail
 1 error
Ran 1 test across 1 file.
```

After implementation, `bun test tests/app/exporting.test.ts tests/git/export.test.ts tests/store` exited 0:

```text
 159 pass
 0 fail
 515 expect() calls
Ran 159 tests across 20 files.
```

## Minor 3: refuse control characters when setting a target

`exportTargetProblem` rejects Unicode control characters in repository, branch, and remote before the other checks.
Tests include NUL, line breaks, tab, DEL, and a C1 control character.
API tests assert a 400 usage error and no stored target.
Git repository validity is still checked during export.

Before implementation, `bun test tests/app/exporting.test.ts` exited 1:

```text
Expected: "export-target: repository, branch, and remote must not contain control characters"
Received: null
 9 pass
 7 fail
 78 expect() calls
Ran 16 tests across 1 file.
```

The first API probe started the exporter on the invalid target and stalled while awaiting settlement.
It was stopped; the test now replaces the notification method, as the existing bad-target test does.
The repeated pre-fix `bun test tests/api/export-target.test.ts` exited 1:

```text
Expected: 400
Received: 200
 13 pass
 3 fail
 41 expect() calls
Ran 16 tests across 1 file.
```

## Minor 6: usage exit code

The round-trip script now exits 2 for an incorrect argument count, matching `CliError`.
Other failure exits remain 1.
First changed the three argument-count assertions to expect 2.
`bun test tests/api/round-trip-script.test.ts` exited 1:

```text
Expected: 2
Received: 1
 15 pass
 3 fail
 36 expect() calls
Ran 18 tests across 1 file.
```

## Minor 7: public documentation paths

Replaced the machine-layout prefixes in `plan-review-practice.md`, `plan-recheck-1.md`, and `preflight.md` with `<worktree>`.
The historical public-repository scan is described in words instead of retaining its machine-specific search expression.
Briefs and the ledger were left alone.
A Python assertion over the three named documents, searching for machine-layout prefixes, failed first with exit 1:

```text
AssertionError: plan-review-practice.md contains a machine-layout path
```

After the changes, the same assertion exited 0:

```text
3 documents pass: no machine-layout paths
```

## Plan 3 M-a: isolate challenge caps

The coordinator chose separate registration and sign-in maps, each capped at 1000 with oldest eviction.
A proposed refusal at the sign-in cap was rejected because an unauthenticated flood could then prevent every sign-in until expiry.
The regression test keeps a pending registration, issues 1001 unauthenticated sign-in options, and completes the registration.
No ceremony request or response shape changes.
This protects registration from the shared-cap problem; a flood can still evict older sign-in challenges within their own cap, as explicitly ruled.

Before implementation, `bun test tests/api/passkeys.test.ts` exited 1:

```text
Expected: 200
Received: 401
(fail) sign_in_flood_does_not_evict_pending_registration
 24 pass
 1 fail
 1064 expect() calls
Ran 25 tests across 1 file.
```

After the control-character, usage-exit, and challenge changes, `bun test tests/app/exporting.test.ts tests/api/export-target.test.ts tests/api/round-trip-script.test.ts tests/api/passkeys.test.ts` exited 0:

```text
 75 pass
 0 fail
 1245 expect() calls
Ran 75 tests across 4 files.
```

## Plan 3 M-c: JSON body for oversized adds

First added live fixed-length and chunked overflow tests, an exactly-at-limit successful add, and a bounded-reader cancellation test.
Before implementation, `bun test tests/api/body-transport.test.ts` exited 1:

```text
Expected: "application/json; charset=utf-8"
Received: null
(fail) live add returns JSON for oversized fixed and chunked bodies and accepts the limit
Expected: 413
Received: 400
(fail) chunked overflow stops reading and cancels the source
 0 pass
 2 fail
 3 expect() calls
Ran 2 tests across 1 file.
```

A live Bun probe confirmed that its body limit bypasses both the fetch handler and error hook.
The coordinator approved disabling that limit and enforcing the unchanged `MAX_REQUEST_BODY_SIZE` in the handler.
Bun 1.3.14 treats `maxRequestBodySize: 0` as a rejecting limit, so the final setting is `Infinity`.
The handler rejects an oversized Content-Length early and otherwise reads into one cap-sized byte buffer, retaining at most that buffer and the current chunk before decoding.
Overflow stops reading, cancels the source, and returns status 413 with the usual usage error JSON and content type.
The cancellation test reads nine 1 MiB chunks, cancels, and never reads the remainder.

Bun 1.3.14 also exhibited a connection-pool problem after early rejection: its client reused an oversized request's connection and the next request received a bare 400 before the handler.
The coordinator approved `Connection: close` on JSON 413 responses and explicit `keepalive: false` on the oversized transport probes.
The live test checks both oversized responses and then a successful add on a new connection with exactly 8 MiB of JSON and trailing whitespace.
The existing handler-only Content-Length tests now expect 413 too.

`bun test tests/api/body-transport.test.ts tests/api/body-limits.test.ts tests/api/serve.test.ts` exited 0:

```text
 15 pass
 0 fail
 69 expect() calls
Ran 15 tests across 3 files.
```

## Verification and deviations

Biome ran with `--error-on-warnings`.
Its first formatting pass caught an untyped test local; TypeScript caught the moved internal type imports and environment index access, all corrected.
The final standalone `bunx tsc --noEmit -p .` exited 0 with no output.
No dependencies were added, no subprocess API beyond `Bun.spawnSync` was introduced, and no record files or frozen documents were edited.
The shared rules add no import edge, and all modules stay within 300 lines.
The coordinator confirmed that moving the plan, ledger, and folder to `done/` waits until merge, after recheck.

The first full `sh scripts/check.sh` run exited 1 at the app front-door inventory:

```text
+ [
+   "lodgePathProblem",
+ ]
(fail) front_door_exports_nothing_else
 2150 pass
 1 fail
 8420 expect() calls
Ran 2151 tests across 192 files.
error: script "check" exited with code 1
```

Updated the explicit API inventory for the new shared helper; the test still rejects any other unexpected export.
Final `sh scripts/check.sh` exited 0.
The Python stage passed 1399 tests, and `lodge check --gate` printed `ok` with the existing area-addition and order notes.
Biome reported 49 informational suggestions and no errors or warnings; TypeScript and knip passed, and dependency-cruiser found no violations.
The final output was:

```text
 2151 pass
 0 fail
 8420 expect() calls
Ran 2151 tests across 192 files.
625 records, 12 areas, 0 threads, 0 problems, 172 queries, 637 rewritten files
0 differences
bun test v1.3.14 (0d9b296a)

 1 pass
 0 fail
 7 expect() calls
Ran 1 test across 1 file.
```

`git diff --check` exited 0 with no output.
The final documentation scan found no machine-layout prefixes or em dashes in the three cleaned documents or this report.

## Left parked

Review minor 2 beyond M-a and M-c remains parked: role-not-a-project-name refusal at write time, concurrent passkey-counter regression, per-request `tokenFor` scanning, expired session rows, no fetch timeout, and synchronous listen failure on an occupied port.
Review minors 4 (mixed export snapshots), 5 (hook-context validation), 8 (test-world composition duplication), and 9 (person-authorised absolute server paths) remain parked.
