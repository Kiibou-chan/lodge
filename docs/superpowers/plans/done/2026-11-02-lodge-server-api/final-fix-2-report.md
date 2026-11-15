# Final fix 2: held content and credential presence

Branch: `server-api`.
Ruling: `d-b7328n`, read with its reasoning before implementation.
Every new regression case was run and seen to fail against the old implementation before production code changed.
Positive controls for real credentials and unchanged held messages passed before and after the fixes.

## I-1: full held draft and attachment text

Every typed draft returned by `held` now includes its original `text`, alongside the existing typed fields.
Both problem branches retain their original text behaviour.
A held add now includes `attachments` as `{name, text}` pairs, or an empty list when none were held.
The attachment text comes directly from `Held.attachments`.
`app/writes.ts` already saves the attachment pairs when holding an add, `store/sqlite-store.ts` returns them, and `Lodge.held()` exposes them unchanged.
No app interface or export needed widening.

The regression publishes an agent decision, then holds the agent's add of a decision with `decided_by: ada`, `replaces: [d-111111]`, a reasoning section, and one attachment.
The person's `held` answer is checked for the exact original draft, the replacement header, the reasoning, the attachment name and text, and the unchanged typed fields.
Separate entry, area, and problem cases verify original text and empty attachments.
The existing typed-draft and edit tests now expect the additional text field.
The held-message tests check the entire existing message shape with exact equality.

Before implementation, the focused run reported these failures:

```text
(fail) held decision includes its full text and attachment text
Expected draft text containing replaces: [d-111111] and ## Reasoning; received no text field.
(fail) held draft carries its own text and empty attachments entry.md
(fail) held draft carries its own text and empty attachments area.md
Expected original text; received typed fields only.
(fail) held draft carries its own text and empty attachments bad.md
Expected: []
Received: undefined
```

A second run, still before implementation, put the attachment assertion first in the decision regression to observe that omission independently:

```text
(fail) held decision includes its full text and attachment text
Expected: [{ name: "note.txt", text: "Supporting notes.\n" }]
Received: undefined
3 pass, 4 fail
```

After implementation, all held-content, typed-draft, edit, problem, and held-message checks pass.

## M-b: non-empty credentials before body reading

The early presence check now requires the same non-empty bearer syntax used by authentication, or a non-empty `lodge_session` value.
Empty cookies, empty authorisation headers, bare `Bearer`, and malformed authorisation values receive the existing 401 response with `sign in, or send an agent token` before JSON reading.
No session implementation change was needed.

The regression cases set `Cookie: lodge_session=`, `Authorization: Bearer `, an empty `Authorization`, and `Authorization: x`, each with a throwing body reader.
Before implementation, each failed with:

```text
Expected: 401
Received: 400
```

The old presence check allowed the body reader to run and mapped its exception to the JSON error.
After implementation, all four cases return the exact existing 401 error and verify that the reader was never called.
A real agent token and a real session both continue to answer 200.
The existing Basic-authorisation test now expects the early presence check's message, since the brief requires a bearer value or session before reading the body.
Unknown non-empty bearer tokens still reach authentication and keep their existing token-specific error.

## Validation

The initial focused run completed with 7 passing tests and 9 failing tests across three files.
After implementation, the focused run across four files completed with 19 passing tests, 0 failures, and 78 assertions.
Including the bearer tests, the final focused run completed with 27 passing tests, 0 failures, and 96 assertions across five files.
All tests call the handler directly with in-memory storage and open no socket.
No dependency, structure rule, `#api` export, or signature changed.
Every touched TypeScript module is fewer than 300 lines.
`git diff --check` passes.
The whole `sh scripts/check.sh` gate was started in the background without `nohup`.
The first attempt exposed `Response.json()` being typed as `unknown` in the new test; using the existing `.text().then(JSON.parse)` pattern fixed the type errors.
The second attempt found the Basic-authorisation test's stale message expectation, with 1861 TypeScript tests passing and one failing; the expectation was updated as described above.
The final whole-gate run exited 0.
Python: 1399 passed.
TypeScript: 1862 passed, 0 failed, with 6436 assertions.
Dependency checks and knip passed.
Differential comparison: 120 queries, 409 rewritten files, 0 differences.
Differential integration: 1 passed, 0 failed.
