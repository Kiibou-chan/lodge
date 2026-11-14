# Task 6 review: sign-in, the person's operations, and setting up the server

Commit 40d72e7 on `server-api-c` (on top of ddddaf6), reviewed in a detached scratch worktree.
Verdict: 0 Blocking, 5 Important, 14 Minor.
The code meets every rule I could trace to a plan sentence; the Important findings are four security-relevant rules that no test pins (each shown by a mutation that survives) and one interface mismatch with plan 4.

## Pass 1: correctness

I read the code against each ceremony rule and then ran 118 single-line mutations against `bun test tests/api`.
The unmutated gate is green: `sh scripts/check-ts.sh` in the scratch worktree gave 1559 pass, 2 todo, 0 fail, Biome with 12 infos only, dependency-cruiser clean, exit 0.

Rules found correct in the code and pinned by a failing mutation:

- user verification required at registration and sign-in (`requireUserVerification`, and `userVerification` at registration options);
- challenge spent on first use, dead at exactly 300 s and alive at 299 s (`expires > now`, `+ 300000`);
- setup code dead at 900 s, alive at 899 s, spent only by `register` (`register-options` twice with one code passes), lower-cased and stripped of hyphens and spaces, stored as a hash;
- one user handle (`SHA-256("<origin> <person>")[0..16]`), attestation `none`, relying party name and ID, `excludeCredentials`;
- counter going back refused, stored counter written through `usePasskey`;
- library message only in the log (`log-echo` and `log-removed` both fail);
- cookie attributes (each of `HttpOnly`, `Secure`, `SameSite=Strict`, `Path=/`, `Max-Age` fails separately), 30-day lifetime to the second, session stored as its hash, 32 bytes, sign-out clearing the cookie and ending the session;
- Origin check (absent and foreign both refused), `Authorization` winning over a cookie on a record operation;
- person-only operations refused for an agent token, including the null-project path (`project !== null` guard);
- `held` filtered to the signed-in person and ordered; the draft summaries through `parseDraft` and `recordFromDraft` with the placeholder rules (own id, own area, `d-000000`, `s-000000`, `held`, area `null` for decisions and areas); `approve` 422 for an added outcome; `decline` answering `null`;
- setup sentences for the mismatch, the registered passkey, `serve` not set up, the default host and port, exit codes 0 and 2.

I also checked `issueSetupCode` against a reference base-32 of the first 100 bits of the entropy `01 02 … 0d`: both give `04106-1050R-3GG28-A1C60`.
I confirmed by probe that a request with neither a setup code nor a session is refused 401 by `register-options` (see I-1 for why no test says so).

### Important

**I-1. No test refuses a registration that has neither a setup code nor a session.**
`ts/src/api/passkeys.ts:51-54`: when `setupCode` is null the only guard is `await sessionActor(options, request)`.
Mutation: delete that line (`reg-session-required`); all 164 tests still pass.
The plan's tests cover the positive path (`signed_in_person_adds_a_passkey`) and a wrong code (`wrong_setup_code_is_refused`, a non-null code), never the null code without a session.
Failure scenario: a later refactor of `registrationAccess` lets anyone call `register-options` and `register` with no credentials, add their own passkey, and receive a session, which is a full takeover of the server, and the suite stays green.
Fix: in `passkeys.test.ts`, one test that `register-options` and `register` with `{}` and with an expired or unknown cookie answer 401, and with a valid cookie but no Origin answer 403.

**I-2. Nothing asserts that `sign-in` starts a session.**
`ts/src/api/passkeys.ts:175`.
Mutation: return `{ result: null }` without the cookie (`nocookie-signin`); all tests pass.
Every sign-in test asserts only the status (`passkeys.test.ts:53-56`, `:135`, `:142`); only registration's cookie is inspected.
Failure scenario: sign-in verifies the passkey, bumps the counter, and gives the person no cookie, so the person can never sign in again after the first session ends.
Fix: in `register_with_the_setup_code_then_sign_in`, take `Set-Cookie` from the sign-in answer, assert the cookie shape, and assert `me` with it is `signedIn: true`.

**I-3. The setup code's randomness is not pinned beyond a character-class regex.**
`ts/src/api/setup.ts:127-146`; the world's `random` fills every byte of a call with one value (`ts/tests/api/world.ts`, `fill(++counter)`), and `setup_prints_a_code` matches only `[0-9A-HJKMNP-TV-Z]{5}(-…){3}` (`setup.test.ts:259`).
Mutations that pass all tests: `& 31` to `& 15` (each character carries 4 bits, 80 bits instead of the 100 of d-yayhct); two letters of the alphabet swapped; `options.random(13)` to `random(14)`.
Failure scenario: someone shortens the entropy and the 15-minute window to a guessable space with no test failing.
Fix: a test with a `random` returning the bytes `1..13` and the exact code `04106-1050R-3GG28-A1C60` (verified above against an independent computation), and one with all bytes `0xff` giving `ZZZZZ-ZZZZZ-ZZZZZ-ZZZZZ`.

**I-4. "Authorization wins over a cookie" is pinned on one path of three.**
`authorization_makes_an_agent_request` (`session.test.ts:253`) uses `projects`.
The explicit guards at `ts/src/api/passkeys.ts:52` (`register` with a session) and `:177` (`sign-out`) can each be deleted with all tests green (`reg-agent`, `signout-agent`).
Failure scenario: a request carrying an agent token and the person's cookie adds a passkey to the person's account, or ends the person's session; both are the person's operations that the rule exists to keep from an agent request.
Fix: two cases beside `authorization_makes_an_agent_request`: a token plus the cookie on `register` with `{response}` and on `sign-out`, both refused (`unauthorised` and `forbidden` as the code gives them), the session still live afterwards.

**I-5. The 422 for a person's operation is decided in `http.ts`, where plan 4 expects `person.ts` to decide it.**
`ts/src/api/http.ts:49-57` reads `result["added"] ?? result["written"] ?? result` and tests `outcome === CHECK_FAILED`; `personOperation` (`ts/src/api/person.ts:61`) returns only the bare result.
Plan 4 (`origin/server-import`, Task 8, "The operations") adds `import` and `export-target` to `person.ts` only (its Modify list has no `http.ts`), whose `importOperation` answers `{ checkFailed, result }` with no `outcome`, "answered 422 as `person.ts` answers `approve`'s `CHECK_FAILED`".
Failure scenario: plan 4's builder adds the two cases to `personOperation`, an import whose check fails answers 200 with `{checkFailed: true, …}` instead of 422, and plan 4's `failing_store_answers_check_failed` fails, or the builder edits `http.ts` outside its file list.
Fix: have `personOperation` return `{ result, checkFailed }` (approve, confirm and held fill it from their outcomes) and `http.ts` answer 422 from `checkFailed` alone; plan 4 then plugs in by names only, as its Call 12 (d-s83a6e) says.
Plan 4's other consumed names are where the plan puts them: `ApiOptions` stays in `options.ts`, `isPersonOperation` and the `fields` table are in `person.ts`, and the dispatch is the `switch` plan 4 extends.

### Minor

**M-1. A challenge's kind is not pinned.** `passkeys.ts:41` (`issued?.kind === kind`); deleting it passes all tests (`chal-kind`).
The plan says the registration verifier accepts only a challenge "issued for registration".
Impact is low (a sign-in challenge is public but registering needs a code or a session); fix: one test that a challenge from `sign-in-options` is refused by `register` and the reverse.

**M-2. Options not pinned:** `allowCredentials` (`passkeys.ts:149`), `userVerification: "required"` at `sign-in-options` (`:150`), and the counter stored at registration (`:140`; the software authenticator always registers at 0).
Mutations `allow`, `uv-option-auth`, `addpasskey-counter` pass.
Fix: assert both in `sign-in-options`' answer; let `SoftAuthenticator.create` take a counter and assert the stored one.

**M-3. Challenge pruning is untested** (`passkeys.ts:46`, `chal-prune` passes); see also M-9 on why it matters.

**M-4. Person operations: fields no test reads.** In `person.ts`: `by` and `raises` of a held message (`:51-55`), the decline `reason` (`:107`), `confirm`'s `area` (`:96`), `token-issue`'s `role` (`:77`), the `no-project` refusal (`:90`), `seq` validation (`:104`), the unknown-field refusal (`:70`), the second `problem` case (`:31`), and a message approval answering 422 (`http.ts:49`, `h-422` passes).
All are in the plan's text; each mutation passes.
Fix: one assertion each, in the existing tests where the data is already built (`held_lists_a_relayed_message` can `toMatchObject` `by` and `raises`).

**M-5. `serverCommand` details unpinned.**
The `serving <origin> on http://<host>:<port>` line (`setup.ts:237`), `--help` (`:171`), port bounds 1 and 65535 (`:229`), a duplicated flag and a value starting `--` (`:193`), a mismatch of the origin alone (`:211`, the test changes the person only), `http://localhost` with no port and `https://127.0.0.1` (the IP and port clauses are covered only by cases the `http` clause already refuses), and a hyphen or a 32-character name (`:205`).
Each mutation passes; fix with one case each in `setup.test.ts`.

**M-6. A bad person name prints the usage line first.** `setup.ts:185-186` prefixes `usage: lodge server {setup,serve} [options]\n` to every `fail`, including the person-name sentence (`:205-208`), where the plan says it prints `lodge: the person's name must be …` and exits 2.
`setup_refuses_a_bad_person` uses `toContain` (`setup.test.ts:311`), which hides the extra line.
Fix: print the sentence alone, and assert the whole text with `toBe`, as `serve_needs_setup` does.

**M-7. `me` answers 403 on a server not set up when the browser holds a stale cookie.**
`passkeys.ts:80-82` calls `sessionActor`, which refuses a missing setup with `forbidden` (`session.ts:195`), and `:85` rethrows it.
Probe: a world with no setup, `me` with `Cookie: lodge_session=stale` and any Origin answers 403 instead of `{setUp: false, signedIn: false}`.
Failure scenario: after the data file is recreated, the page's first call fails instead of showing the setup form.
Fix: `me` answers `signedIn: false` for every refusal of `sessionActor`, or checks `setup` first.

**M-8. A duplicate credential is accepted.** A signed-in `register` of the credential ID already held answers 200 and the list stays at one passkey (probe; `excludeCredentials` is advisory).
Not examined further whether the stored key is replaced; fix: refuse a known ID with the fixed sentence, with a test.

**M-9. Unauthenticated log forging and memory growth.**
`passkeys.ts:65` logs the library's message, which holds the client-supplied origin verbatim: a `sign-in` carrying a known credential ID (public in `sign-in-options`) and `origin: "https://x\nFORGED LOG LINE"` put `Unexpected authentication response origin "https://x\nFORGED LOG LINE", …` in the log (probe, 401 answered).
Also `sign-in-options` is public and each call adds a challenge held 5 minutes, pruned only by the next `remember` (`:44-48`), with no cap.
Fix: log `JSON.stringify(message)` truncated, and cap the challenge map (refuse or drop the oldest beyond, say, 1000).

**M-10. Test-first.** The M1 to M4 and M5 tests were written after the code and checked by mutation (report, "Test-first evidence"), which CLAUDE.md's "see each new test fail before its code" does not allow; the evidence is honest and the mutations were real, so this is a note for the next round.

## Pass 2: practice

Checked: no em-dashes and no personal paths, machine names, or secrets in the diff (`git diff … | grep`); British English in strings; every module at most 300 lines (largest `passkeys.ts`, 182); no `Bun.serve`, socket, `git`, or network use in the tests (`listen` is a recording fake); `ts/package.json` and the lockfile untouched; fixtures synthetic; the commit's trailer is the builder's (`Codex`), as the brief says.

**M-11. Duplication in `http.ts`.** The 422 body literal `{ error: { kind: "check-failed", message: "the check failed" }, result }` appears twice (`:51-57`, `:69-72`), and plan 4 adds a third caller.
Fix: one `checkFailed(result)` helper; this goes with I-5.

**M-12. `passkeys.ts` is one 110-line closure** (`:69-181`) of `if (operation === …)` blocks, and `fields` tables are repeated in `passkeys.ts:23` and `person.ts:8`.
Fix: one function per ceremony operation in a map keyed by name; not needed for this task to merge.

**M-13. Tests that fold several named tests into one `test.each` with `if (name === …)` branches** (`passkeys.test.ts:60-74`, `:81-110`, `:125-144`; `person.test.ts:201-248`), which makes each case read as a maze and its title a lie when a branch is skipped.
The `(await (await w.call(…)).text().then(JSON.parse)).result` shape is repeated about 30 times; a `result(response)` helper in `signed.ts` would remove it.

**M-14. Files outside the plan's list, disclosed in the report and checked here.**
`ts/src/api/webcrypto.d.ts` declares eight browser crypto types as globals for the whole program (the plan expects strict `tsc` to accept the library; without the file `tsc` fails in `@peculiar/x509`, verified by deleting it); and `ts/.dependency-cruiser.cjs` gains `enhancedResolveOptions` so the library's `helpers` subpath resolves.
Neither loosens a limit, an allowed edge, or a rule (the gate is green and no rule file under `ts/tests/structure/` changed), so no author decision is needed; the global shim could instead sit in a `ts/types/` folder named in `tsconfig`, which keeps `src/api` free of program-wide declarations.

## Pass 3: design

- Exports are the plan's Produces: `ServerParts`, `ServerIo`, `serverCommand`, `issueSetupCode` through `#api` (`index.ts`); `ApiOptions` and the Task 5 names are unchanged.
  `CeremonyAnswer` is exported from `passkeys.ts` but read nowhere else.
- No secret in a log, answer, or the repository: the session secret, setup code, and token secret leave only in the one answer that issues them (`token-issue`), `register` and `sign-in` answer `null`, `tokens` lists no hash or secret (tested), the library message is the only text logged from a ceremony (but see M-9).
  Sessions and setup codes are stored as `hashSecret` of the secret; challenges live in memory only.
- The 5-minute challenge store belongs to one `handler` (`http.ts:11`, `passkeys(options)` once per handler), as the plan says.
- Person operations dispatch before `operationArgs`, so `operations.ts` is unchanged although the plan lists it under Modify; the report says so and the choice is sound.
- Plan rule no test enforces: "a token may call `project-create` for its own project's name only" is Task 5's; the new `authenticate(…, null)` path cannot reach it, since `project-create` is dispatched after the person branch only when it is not a person operation (checked by reading `http.ts:46-62`).
- See I-5 for the one boundary that plan 4 depends on.

## Files read

Read in full: `ts/src/api/{passkeys,session,person,setup,auth,http,index,args,tokens,webcrypto.d}.ts`; `ts/tests/api/{authenticator,signed,person-fixtures,passkeys.test,session.test,person.test,person-messages.test,person-drafts.test,setup.test,world}.ts`; `ts/.dependency-cruiser.cjs` and `ts/knip.json` diffs; the plan's header, Global Constraints, Calls made, Names consumed, Task 5 and Task 6; `task-6-brief.md`; `task-6-report.md`; `/var/tmp/lodge-server-api/CLAUDE.md`; lodge decisions d-rn4qzq, d-kt4jkq, d-yayhct, d-jtxwg3; plan 4's Task 8 section on `origin/server-import`.
Not read: `ts/src/api/{operations,errors,wire,options}.ts` beyond grep, `ts/src/store/accounts.ts` beyond `addPasskey`, `ts/src/app/*`, the Task 2 and 3 files in lanes A and B, the `-codex-final.txt` transcripts, plans' earlier reviews, `lodge spec` in full.
Not run: the coordinator's S1 to S3 checks (they need a socket, a binary, a browser), and the real `@simplewebauthn/server` against a browser authenticator; every ceremony claim above rests on the software authenticator.
