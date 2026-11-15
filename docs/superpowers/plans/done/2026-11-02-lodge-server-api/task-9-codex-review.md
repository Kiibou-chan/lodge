# Task 9 correctness review

Reviewed `aabdc5f..8d80ad5` against the full Task 9 section and Global Constraints, probe 3, d-jtxwg3 read through `lodge show`, the report's coordinator rulings, and the operation implementations in `operations.ts`, `passkeys.ts`, `person.ts`, and `http.ts`.
The result is one Important and one Minor finding.
Only this review is changed in the original worktree.
All mutations and extra probes ran in a temporary detached worktree at `8d80ad5`, removed after review.

## Findings

### Important I1: A 401 leaves the signed-in view and potentially its secret visible

**Handles:** `ts/src/api/page.js:26`, `ts/src/api/page.js:43`, and `ts/src/api/page.js:211`.
`result` throws on 401 without changing authentication state, and `action` merely writes the error message.
The sign-out handler reaches `refresh`, which clears the secret and hides the signed-in view, only after a successful sign-out response.
An expired or deleted session therefore leaves the person looking at signed-in controls with no visible sign-in button, and an attempted sign-out can leave the issued token secret in the DOM.

**Probe P1:** Execute the served script in a scratch `node:vm` context with a minimal DOM implementing `textContent`, `hidden`, children, and event listeners.
Bind its fetch to `ceremony().call` from `ts/tests/api/signed.ts`, forwarding the session cookie returned by the actual handler.
Use the existing software authenticator for the navigator credential methods, register, and issue a token for `work`.
Delete the session through `accounts.endSession(hashSecret(cookieValue))`, then invoke the page's sign-out listener.
The actual handler returns 401, and the observed state is `signedIn.hidden === false`, `signingIn.hidden === true`, and the issued secret remains in `#secret.textContent`.
Assertions requiring the signed-out view and an empty secret would fail.
A separate expired-session token-issuance attempt likewise leaves the signed-in view visible and displays only `sign in again`; that handler clears the old secret before its request.
Successful sign-out does clear the secret and return to the signed-out view.
Handle 401 centrally by clearing sensitive page state and presenting the signed-out controls, including when sign-out itself returns 401.

### Minor M1: JSON not-found and error responses omit referrer policy and CSP

**Handles:** `ts/src/api/http.ts:16` and `ts/src/api/http.ts:86`.
The JSON response helper includes `Cache-Control: no-store` and `X-Content-Type-Options: nosniff`, but lacks `Referrer-Policy` and `Content-Security-Policy`.

**Probe P2:** Call `world().fetch(new Request("https://lodge.test/missing"))` from `ts/tests/api/world.ts` and inspect the response headers.
The response is 404 JSON with no-store, nosniff, and `Lodge-Version: 0.3.0`; both policy header lookups return null.
GET `/api/v1/me` gives the ruled 400 `use POST` response with the same omissions.
For the unexpected-error path, replace the scratch world's `options.accounts.setup` with an async function throwing `Error("synthetic failure")`, then POST `me` with no bearer token.
The response is 500 `internal` with the same missing policy headers.
The coordinator ruled through `coord.ask_coordinator` that Task 9 specifies these policies only for the two assets, so this is a Minor hardening observation outside its required asset contract, not an Important plan violation.

## Checked and found sound

- Both GET assets return 200 with the exact planned content types, no-store, nosniff, no-referrer, and verbatim CSP.
  P2 inspected both responses directly, and the two policy tests pass.
  Unknown non-API GET paths remain 404; API GET retains 400 `use POST`, as the report's ruling requires.
- The HTML has `lang="en-GB"`, title `lodge`, one deferred external `/page.js` script, and all planned registration, sign-in, sign-out, additional-passkey, token, and per-project approval sections.
  Inspection and `page_loads_only_its_script` found no inline script, event handler, style, or external origin.
- All thirteen named operations are exactly the plan's list.
  Every fetch uses a literal same-origin `/api/v1/<operation>` path and the shared JSON POST options, with `credentials: "same-origin"`.
  There is no import, external asset, or other network-origin dependency in the page or script.
  Request and response fields match the public ceremony and person-operation dispatchers; the script does not call the general operations in `operations.ts`.
- P1 registered, signed out, signed in, and added a passkey through the actual handler and existing software authenticator.
  The navigator stubs asserted binary challenges, registration user ID, excluded credential IDs, and allowed credential IDs before creating native-shaped credential objects from the authenticator's JSON.
  The server accepted the script's re-encoded responses.
  Registration sends `setupCode` and `response`; sign-in sends `response`.
  Credential fields include `id`, base64url `rawId`, `type`, `clientExtensionResults`, and top-level `authenticatorAttachment`.
  Registration preserves `clientDataJSON`, `attestationObject`, and `response.transports`; authentication preserves `clientDataJSON`, `authenticatorData`, `signature`, and nullable `userHandle`.
  Explicit round-trip assertions also passed for bytes `[0, 255, 254, 253, 128]`, exercising URL alphabet substitutions and unpadded base64url.
- A scratch DOM probe rendered decision statements and quotes, area introductions, malformed drafts with their raw text, and held messages with operation, reference, text, provenance, and time.
  An `<img src=x onerror=alert(1)>` marker remained text, with no image element created.
  Approve and decline event probes recorded `{project:"work",seq:7}` and `{project:"work",seq:8,reason:"Reason"}` respectively, matching `person.ts`'s numeric `seq` contract.
  Approval displayed the returned published ID; inspection also verified the message approval's `written.ids` branch against `app/results.ts`.
- Issuance reads `issued.secret` from the single issuance response; the token-list response supplies metadata only.
  There is no `localStorage`, `sessionStorage`, cookie write, secret URL, or secret logging in the script.
  Refresh and subsequent issuance clear the previous secret; successful sign-out clears it too.
  The coordinator ruled that the plan does not require a separate dismissal control and accepts this lifetime, subject to clearing on sign-out and 401.
  The 401 exception is I1.
- The script contains none of `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval`, or `Function(`.
  Appending `document.body.innerHTML = "mutation";` only in scratch and running `bun test tests/api/page.test.ts` produced six passes and one failure in `script_writes_no_html` at `ts/tests/api/page.test.ts:53`.
  The mutation was restored, and all seven tests passed again.
- Probe 3's HTML text import, cast, JavaScript text declaration, and string assignment are present.
  The single `@ts-expect-error` states the factual same-stem resolution issue.
  Removing only that comment in scratch and running `tsc --noEmit -p .` produced exactly one diagnostic: `src/api/page.ts(2,8): error TS1192: Module '.../api/page' has no default export.`
  No other error appeared; restoring the comment restores the passing check.
  The diagnostic number differs from the report's historical TS2613, but confirms the same resolution issue.
- No structure rule, import allowance, size limit, lint configuration, dependency, or API front-door export changed in the reviewed range.
  The existing handler test changes only its obsolete root not-found fixture to `/missing`, retaining its assertions as authorised.
  The new script is 232 lines, the HTML 37, the wrapper eight, the declaration four, and the new tests 93; `http.ts` is 94 lines.
  All remain below 300 lines.
- The page tests call the in-process handler with an in-memory database and close it.
  Running all seven with a scratch preload that throws from `Bun.serve`, `Bun.listen`, `Bun.connect`, and global `fetch` still passed with 61 assertions.
  No changed test opens a socket.

## Validation and limits

The unmodified scratch checkout passed `bun test tests/api/page.test.ts`: seven passes, zero failures, and 61 assertions.
`sh scripts/check-ts.sh` exited 0, including Biome, TypeScript, dependency-cruiser, knip, and the suite: 1,818 passes, zero failures, and 5,313 assertions across 163 files in this environment.
Biome emitted informational diagnostics only.
Existing installed dependencies were linked into scratch; no package was installed or changed.
Extra review probes were outside the source and test directories and were added after the gate run.
This review exercised DOM behaviour with a minimal VM harness and WebAuthn with the software authenticator, not a real browser.
The coordinator's compiled-binary and real-browser S2/S3 checks remain separate, as the plan and report state.
