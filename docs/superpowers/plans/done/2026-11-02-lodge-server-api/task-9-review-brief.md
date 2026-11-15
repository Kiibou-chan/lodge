Read `CLAUDE.md` in this worktree first.

Outcome: a read-only correctness review of the range `aabdc5f..8d80ad5` (Task 9 of `docs/superpowers/plans/done/2026-11-02-lodge-server-api.md`, report `docs/superpowers/plans/done/2026-11-02-lodge-server-api/task-9-report.md`), written to `docs/superpowers/plans/done/2026-11-02-lodge-server-api/task-9-codex-review.md`.

Scope: edit no source or test file; the review file is the only file you write; run mutations only in a scratch copy (`git worktree add` under a temporary folder, removed afterwards).

Evidence to check against: the plan's "### Task 9" section in full (headers, the sections of `page.html`, the operations `page.js` calls and their request and response shapes in `ts/src/api/operations.ts`, `passkeys.ts`, `person.ts`, and `http.ts`), probe 3 of `probes.md`, the viewer interaction design's rules the plan cites (d-jtxwg3), and the rulings of the report (GET `/api/v1/*` keeps 400 "use POST"; one `@ts-expect-error` on the `./page.js` import).
Look for: a header differing from the plan on either route, or missing on the not-found and error paths; `page.js` calling an operation or a path outside the plan's list, sending a non-POST, or using one of `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval`, `Function(` (mutate the script to add one and run `page.test.ts`); base64url conversion of the WebAuthn options and credentials against what `passkeys.ts` encodes and decodes (the field names for `register` and `sign-in`, including `transports` and `authenticatorAttachment`), a secret shown once and never stored in the DOM after dismissal or in `localStorage`, a held message or add shown with text set through `textContent`, approve and decline sending the hold's number as the server expects, the 401 handling that returns to the signed-out view; a CSP-breaking inline style or script in `page.html`; the page and script depending on a network origin other than its own; the `@ts-expect-error` comment stating a fact and not hiding another error; a structure check loosened; the 300-line limit; a test that opens a socket.

Findings: Important or Minor, each with file and line and a probe or failing test, none without; list what you checked and found sound.

Done when the file is written; commit it with explicit paths as `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, and push `server-api-d`.
Unsettled design goes to the ask tool.
