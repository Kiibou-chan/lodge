# Final fix 1: unauthenticated request hardening

Branch: `server-api`.
The three branch-end findings were raised from Minor to Important by the build session.
All regression tests were written and run against the old implementation before the production changes.
The initial focused run finished with 4 passing tests and 29 failing tests across four files.
Positive controls and the expiry control already passed, as expected.

## 1. Body before authentication

`handler` now refuses non-public operations without either an `Authorization` header or a `lodge_session` cookie before calling `request.json()`.
It returns the existing 401 response, including its existing message.
Unrelated cookies do not bypass the check.
The shared internal `MAX_REQUEST_BODY_SIZE` constant is 8 MiB, used both by `Bun.serve` and the handler's early `Content-Length` check.
Oversize requests use the existing `usage`/400 wire error, as the coordinator approved; no new error kind was introduced.

Before the fix, both missing-credential cases failed with `Expected: 401`, `Received: 400` because the throwing JSON reader was called.
Both oversize cases failed with expected message `the body exceeds 8 MiB`, received `the body is not JSON`.
Both mocked-server signal cases failed because `Bun.serve` lacked `maxRequestBodySize`.
After the fix, these tests pass, including the assertions that the throwing reader was never called.
An ordinary authenticated add still publishes successfully, with an advertised length equal to the limit.
Existing JSON-format tests now carry credentials so they continue to reach their intended validation.
The existing shutdown test also cleans up its signal handlers when an assertion fails.
No test opens a socket; `Bun.serve` is mocked.

## 2. Challenge map

`remember()` caps the internal map at 1000 entries and evicts its oldest insertion when full.
Expiry pruning stops at the first live challenge rather than scanning all live entries on every call.
Spending a challenge still checks its expiry and removes it.

Before the fix, `1001 sign-in options retain exactly the newest 1000 challenges` failed on the first challenge with `Expected: 401`, `Received: 200`.
After the fix, the first challenge is refused and every remaining challenge, including the last, succeeds through the real sign-in ceremony.
This verifies exactly 1000 spendable challenges without exposing the map.
The separate five-minute expiry test and the existing ceremony expiry tests also pass.

## 3. Token text and actor lines

`issueToken` now validates project and non-null role with the store's existing project-name pattern.
The rule moved unchanged to `app/project-name.ts`, is exported through `#app`, and is reused by both the API and the store.
Labels must contain 1 to 80 characters and no Unicode control characters or line separators.
Failures use `usage`, covering direct callers and the `token-issue` operation.
`actorText` now refuses control characters and line separators with `LodgeError`, preventing already-issued malformed roles from forging an event actor line.

Before the fix, all seven invalid shapes resolved through `issueToken` instead of rejecting, and all seven API cases returned 200 instead of 400.
The shapes cover newline in role, invalid role pattern, newline in label, control character in label, 81-character label, empty label, and invalid project text.
All seven direct actor-text control cases failed because no exception was thrown.
The legacy-token add regression returned 200 instead of 400.
After the fix, every rejection passes, ordinary token text remains accepted, and the legacy-token test verifies that no forged actor event was stored.

The coordinator authorised the minimal changes outside the API directories: the shared app rule and front-door export, its exact expected-export-list update, store reuse, and the actor-text guard.
The allowed dependency table already permits both API and store imports from app; it was not changed.
The coordinator explicitly ruled to preserve issuance for projects awaiting creation, because that supports the designed token bootstrap flow.
The existing token bootstrap test remains unchanged.
The invalid-project creation test now uses the person's session so it still exercises the store's original validation and message.
No dependency, existing API signature, or `#api` export changed.

## Validation

The whole `sh scripts/check.sh` gate was launched in the background without `nohup`.
Gate result: exit 0.
Python: 1399 passed.
TypeScript: 1853 passed, 0 failed, including all new regression tests.
The dependency checks and knip passed.
Differential comparison: 120 queries, 408 rewritten files, 0 differences.
Differential integration: 1 passed, 0 failed.
`git diff --check` passes, and every touched source and test module remains below 300 lines.
