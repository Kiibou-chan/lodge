# Task 9 fix 1 report

Fixed I1 and M1 from `task-9-codex-review.md` on `server-api-d`, starting at `2698ac9`.
Read `CLAUDE.md`, the task briefs, and the plan's Global Constraints and Task 9 requirements.
`lodge waiting` reported nothing waiting for an agent or the author.
No unsettled design required a coordinator ruling.

## I1: Clear signed-in state on every 401

`ts/src/api/page.js` now checks for 401 in the shared `result` function before decoding the response body.
It calls one `signedOut` function to clear the issued secret, person text, token list, and held items, hide the signed-in section, and show the signing-in controls.
An ordinary signed-out `me` response uses the same reset.
The existing error handling still displays the server's error message.
No HTML hook was needed.

`ts/tests/api/page-session.test.ts` runs the served script in `node:vm` with a minimal DOM and fetch bound to the in-process handler through `ceremony().call`.
The existing software authenticator registers a passkey, and the handler supplies the session cookie.
Each case issues a token through the page listener, seeds an old held view, deletes the session, and invokes either the sign-out listener or the issuance listener.
The tests assert the actual 401, cleared secret and signed-in content, hidden signed-in section, visible signing-in controls, and `sign in again` message.
All requests stay in process, and each in-memory database closes in `finally`.

Before the fix, `bun test --cwd ts tests/api/page.test.ts tests/api/page-session.test.ts` failed both session cases:

- `page_clears_signed_in_state_when_sign-out_returns_401`: secret assertion expected an empty string and received the previously issued synthetic secret.
- `page_clears_signed_in_state_when_issue-token_returns_401`: `signed-in.hidden` expected `true` and received `false`.

After the fix, both cases pass.

## M1: Apply asset policies to JSON responses

`ts/src/api/http.ts` now shares the cache, content-type protection, referrer, and content security policy headers between assets and the JSON response helper.
The CSP remains verbatim as specified by the plan, and the referrer policy is `no-referrer`.
`ts/tests/api/page.test.ts` adds handler tests for `GET /missing` (404), `GET /api/v1/me` (400, `use POST`), and an injected unexpected setup error during `POST me` (500).
Each checks the status, error message, referrer policy, and exact CSP.

Before the fix, all three `json_<status>_carries_the_asset_policies` cases failed with `Expected: "no-referrer"`, `Received: null`.
The combined regression run before implementation had seven passes and five failures, with 85 assertions.
After the fix, all three policy cases pass.

## Validation

The targeted run passes: 12 tests, zero failures, and 99 assertions across two files.
`sh scripts/check-ts.sh` exits 0, including Biome, TypeScript, dependency-cruiser, knip, and 1,823 passing tests with zero failures and 5,351 assertions across 164 files.
Biome reports informational diagnostics only.
`git diff --check` passes.
The changed modules contain 241 lines (`page.js`), 97 (`http.ts`), 117 (`page.test.ts`), and 88 (`page-session.test.ts`).
No dependency or structure rule changed, no test opens a socket, and no earlier brief, report, or review was edited.
The VM harness exercises page behaviour with the real handler and software authenticator; real-browser coordinator checks remain separate.
