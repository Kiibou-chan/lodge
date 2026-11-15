# Task 9 fix round 1 recheck

## Verdict

I1 (Important): **resolved**.
M1 (Minor): **resolved**.
No new Important or Minor finding was found in `git diff 2698ac9 d716ff2`.

Read `CLAUDE.md` first, the review, fix brief, fix report, recheck brief, and the plan's Global Constraints and Task 9.
`lodge waiting` reported nothing waiting for an agent or the author.
All tests, mutations, and additional probes ran in a detached scratch worktree at `d716ff2`, using the existing installed dependencies without installing packages.
Both mutations were restored before subsequent validation, and the scratch worktree and its probe files were removed afterwards.
Only this uncommitted report is written in the original worktree.
Nothing remained unsettled requiring a coordinator ruling.

## Important I1: resolved

**Handles:** `ts/src/api/page.js:25`, `ts/src/api/page.js:182`, and `ts/tests/api/page-session.test.ts:31`.
The shared response decoder resets signed-in state before decoding a 401 body, and still throws the server's JSON error for the existing error display.

**Mutation P1:** Remove only `if (response.status === 401) signedOut();` in scratch, then run `bun test --cwd ts tests/api/page-session.test.ts`.
Both required cases fail: zero passes, two failures, and 15 assertions.
`page_clears_signed_in_state_when_sign-out_returns_401` fails at `page-session.test.ts:77`: the secret is still non-empty instead of empty.
`page_clears_signed_in_state_when_issue-token_returns_401` fails at `page-session.test.ts:78`: `signed-in.hidden` is false instead of true.
Restoring the branch restores both passing cases.

**Probe P2:** Run the served script in `node:vm` with fetch bound to the actual in-process handler through `signed().call`, an in-memory database, and a DOM harness tracking every created element.
Seed a held decision with the existing synthetic draft fixture, issue a token through the page listener, and delete the session before firing each relevant control.
For `held`, expire the session immediately before forwarding that request during refresh, so the earlier `me`, `tokens`, and `projects` calls succeed.
For sign-out, token issuance, token revocation, approval, and held retrieval, assert the actual target response is 401, the signed-in section is hidden, signing-in controls are visible, person text is empty, and token and held lists have no children.
All five cases pass.
Each case also scans the text and value of every tracked element, including detached elements, for the previously issued secret; none retains it.
The two committed session tests additionally exercise registration through the existing software authenticator and the actual handler.

## Minor M1: resolved

**Handles:** `ts/src/api/http.ts:12`, `ts/src/api/http.ts:26`, and `ts/tests/api/page.test.ts:94`.
JSON and asset responses now use the same policy set, including `Referrer-Policy: no-referrer` and the exact planned CSP.

**Mutation P3:** Remove only the shared `Referrer-Policy` entry in scratch, then run `bun test --cwd ts tests/api/page.test.ts`.
The run gives five passes, five failures, and 66 assertions.
All three `json_<status>_carries_the_asset_policies` cases fail at `page.test.ts:111`, receiving null instead of `no-referrer`, for the 404, 400, and injected 500 paths.
The two existing asset-policy cases fail for the same missing header at `page.test.ts:20`.
Restore the entry: all ten page tests pass, including JSON body, status, referrer policy, and exact CSP assertions.

## Checks for newly introduced problems

- **JSON error remains visible after reset:** `ts/src/api/page.js:26`, `ts/src/api/page.js:45`, and `ts/src/api/page.js:239`.
  P2 asserts `status.textContent === "sign in again"` after each of the five 401 paths, including the refresh rejection from `held`.
  The reset does not swallow the JSON error or hide its status element, which is outside both view sections at `ts/src/api/page.html:11`.
- **Signed-out me clears stale content:** `ts/src/api/page.js:197`.
  P2 separately starts with an authenticated view, a displayed issued secret, token entries, and a held decision, deletes the session, and calls refresh.
  The actual `me` response is 200 with signed-out state, and all reset assertions and the all-element secret scan pass.
- **Secret removal:** `ts/src/api/page.js:183` and `ts/src/api/page.js:235`.
  P2 checks all tracked elements after each 401 and after signed-out `me`, as described above.
  Inspection confirms issuance writes the secret only to `#secret.textContent`; this diff adds no other secret sink.
- **JSON CSP preserves client reads:** `ts/src/api/http.ts:25`, `ts/src/api/http.ts:27`, `ts/src/api/page.js:26`, and `ts/src/cli/client.ts:34`.
  P2 runs successful page requests and JSON error decoding with the actual policy-bearing responses, also checking `Lodge-Version`.
  A separate actual-handler probe through `client` decodes a successful `waiting` result and the expected `no operation named missing` error.
  The JSON content type, version header, status, and result/error envelopes remain intact.
- **No test socket:** `ts/tests/api/page-session.test.ts:56` and `ts/tests/api/page.test.ts:108`.
  Run both test files with a scratch preload making `Bun.serve`, `Bun.listen`, `Bun.connect`, `Bun.spawn`, `Bun.spawnSync`, and global fetch throw.
  All 12 tests still pass with 99 assertions.
  Inspection confirms the VM fetch delegates to the in-process handler and both test files close their in-memory databases in `finally`.
- **300-line limit:** `ts/src/api/page.js:241`, `ts/src/api/http.ts:97`, `ts/tests/api/page.test.ts:117`, and `ts/tests/api/page-session.test.ts:88`.
  Direct line counts are respectively 241, 97, 117, and 88, and the gate's structure checks pass.
  No structure rule, import allowance, or dependency changes in the diff.
- **Public-repository hygiene:** `ts/tests/api/page-session.test.ts:53`, `ts/tests/api/page-session.test.ts:65`, `ts/tests/api/page.test.ts:103`, and `docs/superpowers/plans/done/2026-11-02-lodge-server-api/task-9-fix-1-report.md:1`.
  Inspection of the complete diff finds synthetic fixtures, the reserved `lodge.test` origin, and dynamically issued test secrets, with no personal path, machine name, embedded secret, or unrelated project's records.
  `git diff --check 2698ac9 d716ff2` passes.

## Validation and limits

The unmodified targeted run passes: 12 tests, zero failures, and 99 assertions across two files.
`sh scripts/check-ts.sh` passes, including Biome, TypeScript, dependency-cruiser, knip, and 1,823 tests with zero failures and 5,351 assertions across 164 files.
P2 passes all six view-reset cases and the additional CLI success/error probe.
Behavioural probes use a minimal DOM and the actual handler, with no socket or real browser.
The plan's coordinator browser and compiled-binary checks remain separate.
