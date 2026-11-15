# Task 5 review

Reviewed `59624c6` (`server-api-c`, on top of `fd14939`) against the plan's Task 5, Global Constraints, Calls made, and Task 6's Consumes.
Verdict: no Blocking findings; 3 Important, 6 Minor.
The gate is green in my own scratch worktree (`sh scripts/check-ts.sh` exit 0, 1480 pass, 2 todo, 0 fail), and a probe through the handler over a real seeded project returned 200 or the expected 4xx for every operation.

## Pass 1: correctness

Everything in the plan's Produces and routing text is implemented as spelled; the findings below are about what the tests leave unpinned, not about wrong behaviour.
Checked and found right:

- Routing: path is checked before method (`ts/src/api/http.ts:22-23`), as the brief says; content type and body checks follow the plan's sentences word for word; `/api/v1/constructor`, `toString`, and `__proto__` answer `not-found` through `Object.hasOwn` (`operations.ts:27`).
- Status mapping and headers: `statuses` (`errors.ts:2-11`) matches the plan; `mappedError` tests `Conflict` before `NotFound`, `Forbidden`, `LodgeError` (`errors.ts:22-29`); `internal` answers the fixed sentence and logs only the stack (`errors.ts:30`); every answer, the 401 and 404 included, carries the three headers (`http.ts:9-18`).
- 422: only `add`, `ask`, `reply`, `close` with `AddOutcome.CHECK_FAILED` answer 422 with the whole result (`http.ts:41-49`); a real failed `add` through the handler gives 422 and publishes nothing (`write.test.ts:16`).
- Every operation's fields and defaults against lodge 0.2's `Lodge` (`src/lodge/app/lodge.py:27-122`) and the TS `Lodge` (`ts/src/app/lodge.ts`): `search` limit 20 and filters default as `Filters` (`core/search.py:22-29`), `show`, `timeline` 50, `spec` area, `check(gate)` positional, `mint` prefix default `d`, `add` options, `ask`/`reply`/`close` with `where` and `when` and `close`'s nullable `text`; all sixteen pass through `operations.ts:93-143` as the plan and Python spell them.
- `project-create`: setup check, section/key words (`core/settings.py:30-35`), `parseCoreSettings`, existing-name check, then `projects.create(project, setup.person, settings)`; order and sentences as the plan (`operations.ts:61-81`); name refusal and `Conflict` fall through `mappedError`.
- Bearer auth: hash-only lookup (`auth.ts:13`), unknown or revoked is `unauthorised`, another project `forbidden`; `issueToken` spells `lodge_` plus 43 base64url characters, `t-` plus six alphabet characters (`tokens.ts:8-11`), stores `hashSecret(secret)` only, and the stored hash is checked by `bearer.test.ts:43`.
- Exports: `ts/src/api/index.ts` exports exactly `handler`, `ApiOptions`, `lodgesOver`, `hashSecret`, `issueToken`, `tokenId`, `toWire`, with the signatures of the plan's Produces (`options.ts:3-19` holds `ApiOptions` and `lodgesOver`).
  Plan 4's consumed names are therefore as spelled.

### I-1 (Important): "a `charset` parameter allowed" has no test

`ts/src/api/http.ts:25` is the only place the plan's rule lives, and `handler.test.ts:5-36` and `world.ts:32` send `application/json` bare.
Failure scenario: a later edit of line 25 to compare the whole header (mutation "charset param", run: all 85 tests still pass) makes `fetch(..., { headers: { "Content-Type": "application/json; charset=utf-8" } })`, which the page of Task 9 or the command of Task 7 may send, answer `usage` `send JSON`.
Fix: one row in `handler.test.ts`'s table (or a test beside it) with `application/json; charset=utf-8` and `Application/JSON`, expecting 200.

### I-2 (Important): the field-by-field checks have untested values

The plan asks for "a wrong type per field kind" and `search`'s filters checked (`operations.ts:46-52`); the tests (`operations.test.ts:29-42`) pin only one failing row per kind.
Mutations that all survive `bun test tests/api` (run by me, see the table below):

- `filters.kind`, `filters.scope`, and `filters.status` value checks removed (`operations.ts:46`, `48`, `51`): no test sends `kind: "other"`, `scope: "other"`, or `status: "other"`.
- `Number.isInteger` removed from `limit` (`args.ts:35`): `limit: 1.5` is untested (only `0` is).
- The pair shape (`args.ts:48`): `[["a","b","c"]]` and `[["a", 1]]` are untested (only `["x"]` is), so `drafts` and `attachments` could take a three-element pair or a non-string text and reach `Lodge.add`.
Failure scenario: a refactor of `Args.pairs` or `searchFilters` accepts a malformed value and the first symptom is a 500 or a wrong result in production, not a `usage` answer.
Fix: add those rows to the `arguments_are_checked` table (about six lines); each pins a line above.

### I-3 (Important): the test-first evidence ties no test to behaviour

The hard rule is to see each new test fail before its code (`CLAUDE.md`, Hard rules).
The report's table (`task-5-report.md`, "Test-first evidence") gives `Missing #api` for every test of six files: one module-not-found failure shared by all, which shows nothing about any single test failing for the right reason.
`explicit.test.ts` (121 lines, 14 cases, the file that kills most of the default-and-option mutations below) was written after the implementation, as the report says, and its only failure evidence is a mutation that throws before `Lodge` is built (`operations.ts`, `operate`), which fails every test that reaches a handler, so it distinguishes none of them.
The `file:line` handles in the report are real (I checked each against the test files), but they name no behavioural mutation.
Fix: no code change; the coordinator records that the evidence is thin and relies on the mutation table below, which does tie tests to lines.
For later tasks, the brief should require one named mutation per test row, not a first failure.

## Mutations run

Each applied to one line of `ts/src/api` in a detached scratch worktree, `bun test tests/api`, reverted after (script and output in my scratch directory, not in the repository).

| Mutation | File:line | Result |
|---|---|---|
| content type compared whole (no `split(";")`) | `http.ts:25` | SURVIVED (I-1) |
| content type not lower-cased | `http.ts:26` | SURVIVED (Minor M-2) |
| `Number.isInteger` removed | `args.ts:35` | SURVIVED (I-2) |
| pair length check removed | `args.ts:48` | SURVIVED (I-2) |
| pair element type check removed | `args.ts:48` | SURVIVED (I-2) |
| `filters.kind` check removed | `operations.ts:46` | SURVIVED (I-2) |
| `filters.scope` check removed | `operations.ts:48` | SURVIVED (I-2) |
| `filters.status` check removed | `operations.ts:51` | SURVIVED (I-2) |
| unknown `filters.<key>` check removed | `operations.ts:36` | killed, `arguments_are_checked` |
| map keys not encoded | `wire.ts:5` | SURVIVED (M-4) |
| Bearer regex unanchored | `auth.ts:12` | SURVIVED (M-1) |
| `token.revoked !== null` removed | `auth.ts:14` | SURVIVED, equivalent: `SqliteAccounts.tokenFor` already filters revoked (`ts/src/store/accounts.ts:121`) |
| `in` for `Object.hasOwn` | `operations.ts:27` | SURVIVED (M-4); with `in`, `/api/v1/constructor` would reach `...(fields[operation] ?? [])` at `operations.ts:30` with a function, which I expect to answer 500 (not run) |
| another project's token check removed | `auth.ts:16` | killed, `token_reaches_only_its_project` |
| `close` dropped from the 422 list | `http.ts:42` | killed, `whole_failed_result_is_preserved close` |
| `nosniff` header removed | `http.ts:15` | killed |
| `Cache-Control` removed | `http.ts:14` | killed |
| path check removed | `http.ts:22` | killed, `other_paths_are_not_found` |
| `where` forced null | `operations.ts:92` | killed (4 tests) |
| `close` text forced null | `operations.ts:133` | killed |
| `attachments` required | `operations.ts:117` | killed (4 tests) |
| unknown-section wording dropped | `operations.ts:69` | killed |
| `parseCoreSettings` call removed | `operations.ts:72` | killed |
| existing-name check removed | `operations.ts:77` | killed |
| not-set-up check removed | `operations.ts:63` | killed |
| owner not the set-up person | `operations.ts:79` | killed |
| stack not logged | `errors.ts:30` | killed |
| SHA-256 replaced by SHA-1 | `tokens.ts:6` | killed |
| 16 entropy bytes for the secret | `tokens.ts:18` | killed |
| `issued` stamp wrong | `tokens.ts:24` | killed |
| `timeline` default 51 | `operations.ts:104` | killed |
| `check` gate forced false | `operations.ts:110` | killed |

## Pass 2: practice

Clean: no file over 300 lines (largest `operations.ts`, 145), no change to `ts/knip.json`, `ts/tests/structure`, `.dependency-cruiser.cjs`, or `biome.json` (diff stat), no dependency added (`package.json` gains only `#api`; `bun.lock` untouched), no socket or process (grep of the diff for `Bun.serve`, `listen(`, `Bun.spawn`, `node:net`: none), fixtures synthetic (`ada`, `lodge.test`, `work`), no em-dashes in the report, no comments in `src/api`, the commit is by the project identity with the trailer the brief names.
Biome reports seven infos (`useLiteralKeys`) in new files at `args.ts:34`, `http.ts:44`, `operations.ts:50`; `noPropertyAccessFromIndexSignature` makes bracket access required, and the gate passes with warnings fatal, so no finding.

### M-1 (Minor): the bearer scheme is case-sensitive and untested

`auth.ts:12` `/^Bearer (\S+)$/u`: `bearer <token>` answers 401 (probe), though RFC 7235 section 2.1 makes the scheme case-insensitive.
No test sends a malformed header (`Basic x`, `Bearer x y`), so the anchors are unpinned (mutation survived).
Fix: `/^Bearer (\S+)$/iu` and a three-row test.

### M-2 (Minor): `.toLowerCase()` on the content type is untested

`http.ts:26`; folded into the I-1 fix.

### M-3 (Minor): the `Proxy` fake `Lodge` and the cases are duplicated

`operations.test.ts:10-20`, `explicit.test.ts:71-81`, and `explicit.test.ts:102` build the same recording `Proxy`; `each_operation_reaches_lodge` and `explicit_arguments_reach_lodge` are the same test over two tables (`operation-cases.ts`, `explicit.test.ts:6-67`).
Fix: a `fakeLodge(answer)` in `world.ts` and one table with a defaults column and an explicit column.

### M-4 (Minor): small gaps that no test pins

`wire.ts:5` encodes a map's key with `toWire(k)` but only string keys are tested (`wire.test.ts:7,23`), so a mutation to `[k, toWire(v)]` survives; `operations.ts:27` `Object.hasOwn` against `in` is not pinned by any test (`/api/v1/constructor` answering 404 is the case; today the code is right, my probe gave 404).
Fix: a `Map` with a `Set` key in `wire.test.ts`; an operation named `constructor` in the `unknown_operation_is_not_found` row.

### M-5 (Minor): `searchFilters` re-implements `Args`

`operations.ts:33-60` builds a second `Args`, then a local `nullable` (`:38-43`) that does what `Args.nullable` does with a `filters.` prefix on the message, and hand-rolls the three value checks that `Args.choice` does for `prefix` and `raises`.
Fix: give `Args` a field-name prefix and use `nullable` and `choice` (about 15 lines fewer); optional.

### M-6 (Minor): the accepted fields are listed twice

`operations.ts:7-25` (`fields`, used by `known`) and the reads in the switch (`:93-143`) are two lists that must agree; a field listed but never read is accepted and silently ignored (no test would notice).
Fix: let `known` run after the reads, comparing against the names the reads touched, or a test that every listed field of each operation is read; optional.

## Pass 3: design

- Boundaries and coupling: `options.ts` is a file the plan does not list (it lists seven); it breaks the `tokens.ts` to `http.ts` cycle `ApiOptions` would otherwise make, the report says so, and `index.ts` re-exports exactly the Produces.
  No finding.
- No secret or request detail leaves: the log receives only the stack of an unexpected error (`errors.ts:30`); `Authorization` is read in `auth.ts` alone and no code path puts it in an answer; an agent's own project name appears in the 403 message as the plan spells it.
  Probe over malformed drafts (bad YAML, NUL, path-like names, empty `by`) gave 4xx answers with no log lines.
- Task 6 builds on this as the plan says it will: `http.ts:38` demands `project` as a string for every operation and `operationArgs` (`operations.ts:26-32`) knows only the record operations, so Task 6's public ceremonies (`me`, `register-options`, `sign-in-options`), which have no `project`, mean Task 6 must restructure both before adding any person operation.
  The plan lists `http.ts`, `operations.ts`, and `auth.ts` under Task 6's Modify, so this is expected, not a finding; the brief for Task 6 should say it.
- Note for Task 8 (not a Task 5 defect): `request.json()` (`http.ts:31`) buffers the whole body before any authentication, so the size limit is whatever `Bun.serve` sets (`maxRequestBodySize`); worth naming in Task 8's brief.
- Plan rule with no test: "a charset parameter allowed" (I-1); everything else the plan states for Task 5 has at least one test, and the Review Focus items that apply (authorisation, secrets) are pinned by `bearer.test.ts:21,30,43` and `handler.test.ts:64`.

## Files read

`CLAUDE.md`; the plan (header, Global Constraints, Calls made, Review Focus, Order and lanes, Names consumed from plan 2, Tasks 5 and 6); `task-5-brief.md`, `task-5-report.md`; every file of `git diff fd14939 59624c6` under `ts/src/api` and `ts/tests/api`, plus `package.json`; `ts/src/app/lodge.ts`, `accounts.ts`, `errors.ts`, `index.ts`; `ts/src/core/search.ts` (`filters`) and `settings.ts` (head); `ts/src/store/accounts.ts` (`tokenFor`); `src/lodge/app/lodge.py` (operations), `src/lodge/core/settings.py`, `src/lodge/core/search.py` (`Filters`); `tests/e2e/support.py` (seed).
Not read: `lodge` records through `lodge show` (I read the plan's wording instead of d-sry12f and d-3ywdhq directly), the design document, Task 4's files beyond `tokenFor`, `ts/tests/structure/`, and `task-5-codex-final.txt`.
Not verified: behaviour under a real socket (outside the task), and Task 6's integration.
