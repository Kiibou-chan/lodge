# Plan review, correctness angle: plan 3, the API, sign-in, and the command

Reviewed: `docs/superpowers/plans/2026-11-02-lodge-server-api.md` at 3e4c29c on `server-api`.
Written incrementally; the counts are at the end once the review is done.

## Findings

### B-1 · Blocking · `src/main.ts` cannot print through `process.stdout` and `process.stderr` under the structure test

Handle: plan line 539 (`run(argv, io)` of `#cli` with … `process.stdout` and `process.stderr`) and line 538 (`serverCommand`'s `io`); `ts/tests/structure/calls.ts:146-151` on `origin/server-core` (`writes` holds `write`, and any call whose last name is `write` outside `git` is `file writing outside git`); `ts/tests/structure/repository.test.ts:9` requires `callViolations` of the real tree to be empty.
Run: in a detached worktree at `origin/server-core`, `callViolations(plant({"src/main.ts": 'process.stdout.write("x"); …', "src/api/a.ts": 'process.stderr.write("x"); …'}))` gives `["src/api/a.ts:1: file writing outside git", "src/main.ts:1: file writing outside git"]`; `console.error`, `Date.now()`, `getTimezoneOffset`, and `crypto.getRandomValues` in `src/main.ts` are not reported.
Failure: Task 8's builder writes `io.out = (t) => process.stdout.write(t)` as the plan says, the gate fails on `real_tree_is_clean`, and the plan's own rule (line 27) makes the task stop BLOCKED for the author's call; `Bun.write(Bun.stdout, …)`, `console.write`, and `fs.writeSync(1, …)` are refused the same way, and `console.log` adds a line end, so `draft`'s `print(text, end="")` and every `io.out` text not ending in a line end cannot be printed byte for byte.
Fix: settle it in the plan before the build: either record an author decision allowing standard output and error writes in `src/main.ts` (and say whether `api` may write standard error, Task 5's "the error written to the server's standard error"), with a refusal and an allowed case added to `calls.test.ts`, or state a means the rules allow (for example `console.error` in `api`, and in `main` a `console.log` of each text whose last line end is cut, with the guarantee that every text `io.out` receives ends in `\n`, and a test of `draft` that holds it).

### I-1 · Important · `check_and_gate` keeps its name and tests something else, weaker

Handle: plan line 500 (`check_and_gate` "after a hand edit making a decision unreadable, that both print its `problem:` line and exit 1"); `tests/e2e/test_check_and_gate.py:5-21`; `src/lodge/core/check_immutable.py:1,16` (check 5 compares the published state with the state after); plan 2 at 7204ad3, Task 7b (`gate(current)` is `gate({ published: current, checked: [["", current]] })`).
Failure: the Python test edits the seeded decision's statement and asserts `check` starts `check 5: ` with the decision's ID, `show` of the decision holds `fails check`, and `check --gate`'s first line starts `check 5: ` with no `ok`.
On the server check 5 cannot fire (published is current), so the plan swaps in an unreadable file, which asserts a `problem:` line instead of a `check N:` line, drops the `show … fails check` assertion entirely, and duplicates `check_prints_unreadable_files_and_fails` of the same file.
A regression in which `show` stops flagging a record that fails a check, or `check --gate` prints `ok` above a failing check line, passes this test; plan 1's Porting rule asks such a test to be listed in the report "for the review and a coordinator ruling", and the parity row (line 120) names only the dropped test.
Fix: keep the Python shape with a state check the server still runs: the hand edit (through `handEdit`) rewrites the seeded decision so that it fails a state check (for example `decided_by: author` with no quote, check 3), then assert `check` exits 1 with nothing on `err` and starts `check 3: ` with the ID, `show` of the decision holds `fails check`, and `check --gate` exits 1, its first line `check 3: ` with the ID and no `ok`; add to the row's `why` that check 5 compares against a published state that is the current state on the server (design line 79).

### I-2 · Important · the held add's lines have no test, and `add-import` loses its outcome assertion

Handle: plan lines 141, 464, and 498; d-bwb1tt ("the carried test asserts the held add's lines and then the approval's"); `tests/e2e/test_add_import.py:23-26` (`added.out.splitlines()[-1].startswith("staged d-")`, then `show` of `added.out.split()[-1]`); Task 7a's and 7b's test lists (lines 502 and 512).
Failure: no test of the plan asserts the line `held for approval by <awaits> as hold <held>; nothing is current until they approve it` or the dry run's `note: <awaits> approves this add before it is current`; `seed` only reads a number from the last line, and `TestServer.approve` returns "the published IDs" without saying it requires the outcome `published`.
So a command that prints the held line wrongly (another person, no `(provisional)` marks, the wrong hold number that happens to parse), or prints the dry-run note in the wrong place, passes every gate test, and `add_import`'s Python assertion on the outcome line becomes no assertion at all on the command's output; this is the planner's own concern (`planner-report.md`, Concerns), and d-bwb1tt's text asks for the assertions the tasks leave out.
Fix: in Task 7b, `add-import.test.ts`'s `import_needs_the_flag_and_a_listed_source` asserts the add's last line equals `held for approval by author as hold 1; nothing is current until they approve it` (exit 0, nothing on `err`, as the Python asserts), then that the approval's outcome is `published` and its first `d-` ID is what `show` reads; `support.ts`'s `seed` asserts the same held line before approving; `TestServer.approve` throws unless the outcome is `published`; and one new test (Task 7b, `ts/tests/e2e/held.test.ts`, listed as new, not carried) asserts a dry run of a person's decision prints the `note:` line directly above `dry run: nothing published`, exit 0.

### I-3 · Important · Task 7a's parity rule breaks plan 1's `changed` rows and crashes on plan 4's

Handle: plan line 476 ("every other name of a `changed` row with `ts` files is checked as a `ported` row's is"); `ts/tests/parity.json` at `origin/server-core` holds `changed` rows with `ts` files for `tests/test_structure.py` and `tests/test_structure_io.py` (plan 1) and `tests/e2e/test_hook_feedback_after_hand_edits.py` and `tests/hook/test_post_tool_use.py` (plan 4); plan 2, Task 9, scopes its version of the rule to `plan` 2.
Run: `rowMissing` of `ts/tests/parity-names.ts` over those rows at `origin/server-core` gives 16 missing names for `tests/test_structure.py` (`submodule_through_front_door`, `relative_import`, …) and 13 for `tests/test_structure_io.py`, and throws `ENOENT` for a row whose `ts` file does not exist yet (`ts/tests/app/reads-published.test.ts` before plan 2 merges; plan 4's hook files throughout this plan).
Failure: the builder writes the rule as worded, `a_changed_row_keeps_every_name_it_does_not_drop` fails on plan 1's structure rows and errors on plan 4's rows, and the gate is red for reasons outside this plan.
Fix: scope the rule to `changed` rows with `plan` 3 (or to rows holding `dropped`), as plan 2 scoped its own, and say how plan 2's rule and this one merge in `parity.test.ts`.

### I-4 · Important · S1 cannot pass as written: binary mode rewrites the URL that tests assert, and cannot inject a throwing `fetch`

Handle: plan line 497 (binary mode serves on `127.0.0.1` port 0 and "writes that `http` URL into `.lodge.toml`"); line 500 (`init` asserts `created project <project> on <url>`; `init_when_the_server_cannot_be_reached` uses "a `fetch` that throws", expecting `lodge: cannot reach https://lodge.test: …`); line 86 (S1: "every carried command test passes with the compiled binary"); plan 1, "The rest of build step 1" (plan 3 ends when "the compiled binary runs them").
Failure: under `LODGE_E2E_BINARY` the binary uses the real `fetch` against `http://127.0.0.1:<port>`, so `init` prints that URL rather than `https://lodge.test`, and the unreachable-server test cannot hand the binary a throwing `fetch`; S1 then fails on tests that pass in the gate, and the plan's end condition is not met, or the coordinator edits tests during S1 with no brief.
`project.ts` (line 495) also offers no way for a test to replace the server's `fetch`, so the in-process form of that test has no seam either.
Fix: `Project` exposes `url` (the one written into `.lodge.toml`) and the URL-bearing assertions read it; `init_when_the_server_cannot_be_reached` points `.lodge.toml` at a port nothing listens on in binary mode (or `project({ fetch })` takes a replacement in process and the test is skipped with a named reason in binary mode, listed in the report); S1's expected counts say which tests, if any, it skips.

### I-5 · Important · `mintId("t", …)` does not type-check against plan 1's core

Handle: plan line 364 (`the ID mintId("t", random(8))`); `ts/src/core/ids.ts:8` at `origin/server-core` (`mintId(prefix: "d" | "s" | "q", entropy: Uint8Array)`), whose `isId` pattern is `^[dsq]-…`; Task 5's Files (line 329) do not list `ts/src/core/ids.ts`.
Failure: strict `tsc` refuses the argument `"t"`, so Task 5 either stops BLOCKED or edits `core` outside its brief; widening `mintId` would also leave `isId` refusing the token IDs it mints.
Fix: build the token ID in `api/tokens.ts` (`t-` and six characters of the same Crockford alphabet from `random(6)`), or list `ts/src/core/ids.ts` in Task 5 with the widened prefix and a test, and say whether `isId` stays `[dsq]`.

### I-6 · Important · `lodge server setup` accepts origins on which no passkey can be made

Handle: plan line 412 (`--origin`: `https://<host>` or `http://localhost:<port>` "(also `127.0.0.1` and `[::1]`)"); line 399 (relying party ID "the origin's host"); d-rn4qzq (origin fixed by the first setup); line 412 again (a server set up for another origin prints `lodge: the server is set up for …` and exits 2).
Failure: for `http://127.0.0.1:8787` or `http://[::1]:8787` the relying party ID is an IP address, which WebAuthn refuses as an RP ID (Web Authentication, `create()` step "If effectiveDomain is not a valid domain, throw SecurityError"; an IP address is not a valid domain), so `navigator.credentials.create` fails in every browser; the origin is then fixed for good and setup refuses to change it, so the data file is useless.
The software authenticator does not catch this: @simplewebauthn/server verifies any `expectedRPID` string, so every gate test passes (not run in a browser here; the claim rests on the specification).
Fix: `setup` accepts `https://<host>` and `http://localhost:<port>` only; `setup_refuses_a_bad_origin` gains `http://127.0.0.1:8787` and `http://[::1]:8787`; the command's `server.url` (d-z1pncx, Task 3) keeps all three loopback forms, since it makes no passkey.

### I-7 · Important · nothing produces the held drafts' titles, statements, and quotes the page must show

Handle: plan line 565 (the page shows each hold "with its drafts' titles, statements, and quotes"); line 566 (`page.js` is "plain JavaScript with no import"); line 410 (`held` answers "the open holds of `Lodge.held()`"); plan 2 at 7204ad3, `HeldDraft.drafts` is `readonly (readonly [string, string])[]`, raw draft texts; Task 9's tests (line 568) are text scans of the files.
Failure: the API answers raw Markdown with a YAML header, so `page.js` either shows the raw text or parses YAML by hand with no library; a hand parser that reads a title or quote differently from `#core`'s YAML layer shows the person words other than those the approval records, against the first must-not ("never show wrong information") at the one point where a person's decision is made; no gate test can see it, and S3 checks only that an approval happens.
Fix: Task 6's `held` answers, per hold, its `seq`, `at`, `by`, and per draft its file name, `kind`, `title`, statement, and quote (`text`, `where`, `when`) as `#core`'s draft parser reads them (an unparsable draft as its raw text with a flag), with a test in `person.test.ts` that the answer's title and quote equal the draft's; `page.js` writes those fields with `textContent`.

### M-1 · Minor · "unrecognized arguments" is argparse's top-level error, not the command's

Handle: plan line 196 (a usage error prints "the command's usage line, then `lodge <name>: error: <message>`"); line 203 (`extra_words_are_an_error` asserts only `unrecognized arguments: extra`).
Run: `uv run --frozen --quiet lodge thread q-aaaaaa extra` in a scratch repository prints `usage: lodge [-h] [--version] COMMAND ...` and `lodge: error: unrecognized arguments: extra`, since argparse reports leftover words from the top-level parser; `ambiguous option`, `invalid choice`, `expected one argument`, and the `--limit` lines print the command's usage and `lodge <name>:` (all of probe 6 reproduced, plus `search x --s y` giving `lodge search: error: ambiguous option: --s could match --scope, --status`).
Failure: the command prints `usage: lodge thread …` and `lodge thread: error: unrecognized arguments: extra`, two lines lodge 0.2 does not print (Review Focus 2), and the test passes.
Fix: the rule names the exception, and `extra_words_are_an_error` asserts the whole `err`.

### M-2 · Minor · `FixedClock` has no `advance`

Handle: plan line 365 (`world.ts` uses "plan 2's `FixedClock` … that `advance(seconds)` moves"); plan 2 at 7204ad3, Task 2 (`FixedClock(start: Now = START, stepMs = 0)` with `calls`, `slept`, `now()`, and `sleep(seconds)`).
Failure: the expiry tests of Tasks 5 and 6 (`setup_code_lasts_15_minutes`, `session_lasts_30_days`, `challenge_lasts_5_minutes`) call a method that does not exist, and `ts/tests/app/fakes.ts` is not in either task's Modify list.
Fix: say `await clock.sleep(seconds)` moves it (it adds to `start`), or list `fakes.ts` with an `advance` added.

### M-3 · Minor · spending a setup code is not required to be one transaction

Handle: plan line 316 (`spendSetupCode` "is true in the same case and then spends it"); line 400 (`register` spends after verifying); Task 4's test `setup_code_is_spent_once` is sequential.
Failure: two `register` calls with the same code, each with its own challenge, both read the code unspent across an `await` before either appends `setup-code-spent`, and two passkeys register on one code (Review Focus 3, "a setup code accepted twice").
Fix: `spendSetupCode` reads and appends in one Kysely transaction, and `setup_code_is_spent_once` adds two concurrent spends (`Promise.all`) of which exactly one is true.

### M-4 · Minor · the "user ID fixed per server" has no source

Handle: plan line 399 ("a user ID fixed per server"); `ServerSetup` (line 272) holds `origin`, `person`, and `at` only.
Failure: the builder draws it at random per `register-options`, so the person's second passkey carries another user handle and the authenticator lists two accounts for one person.
Fix: derive it (for example the first 16 bytes of SHA-256 of `origin` and `person`) or store it in `server-set-up`, with a test that two `register-options` answers give the same `user.id`.

### M-5 · Minor · `setup` does not check the person's name, and `project-create` on a server not set up has no answer

Handle: plan line 412 (`setup … --person NAME`, no check named); line 360 (`project-create`'s owner is `accounts.setup()`'s person); d-wx7d0f (`^[a-z][a-z0-9-]{0,31}$`).
Failure: `lodge server setup --person Ada` succeeds and fixes a name for good that `projects.create` later refuses, so `lodge init` fails for every project with a `usage` error naming the pattern; `project-create` on a handler whose `setup()` is `null` dereferences it and answers `internal`.
Fix: `setup` refuses a name outside d-wx7d0f's pattern (a case in `setup_refuses_a_bad_origin`'s neighbour test), and `project-create` answers `usage` with a sentence when the server is not set up.

### M-6 · Minor · the plan's own wording says the held approval is not a substitution

Handle: plan line 28 ("with the substitutions of d-bwb1tt only: … git … and the outcome `staged` is `published`") and line 54 ("beyond d-bwb1tt's two substitutions"); d-bwb1tt's text names a third, "a held add (d-znagqe) is approved through the person's session"; line 141 calls it "the model change, not a weakening".
Failure: a reviewer holding a carried test to line 28 flags `seed`'s approval as a weakening, and a builder reading line 54 believes only two changes are allowed.
Fix: name the third substitution in both places, with what it must assert (I-2).

### M-7 · Minor · the guide says nothing of held adds

Handle: plan lines 467 to 474 (the guide's changes); `src/lodge/cli/guide.md:55-58` ("Quoting the author") stays as it is.
Failure: an agent reading the guide learns that `decided_by: author` with a quote records the author's decision, adds it, and is surprised by `held for approval`; nothing tells it that a person's decision waits for that person's approval on the page.
Fix: fold a clause into line 55 or 57 (the guide is at its 60-line limit after the plan's changes: one line added after line 7, line 20 removed), saying that a decision of a person waits for that person's approval on the server's page and `add` prints `held for approval`; `guide_is_short_and_covers_the_write_path`'s new phrase can be that clause.

### M-8 · Minor · d-v9mw2d's test does not fail if `main.ts` forgets the call

Handle: plan line 544 (`yaml_logging_variables_are_cleared` tests `withoutYamlLogging` on a plain object); line 536 (`main.ts` calls it first); S2 (line 87) runs once, outside the gate.
Failure: a later edit of `main.ts` that drops or moves the call keeps the gate green.
Fix: a gate test that reads `src/main.ts` with TypeScript's parser and finds `withoutYamlLogging(process.env)` as its first statement, or `binary.test.ts` running the binary with both variables set on a command that reaches `loadYaml`, if one does on the command's side.

### M-9 · Minor · `kinds_map_to_exit_codes` lists seven codes for eight kinds

Handle: plan line 502 (`test.each` over the kinds: "2, 2, 2, 2, 1, 2, and 1 printing the result"); line 353 names eight kinds.
Failure: the builder guesses which kind is left out and which code goes with which, and a wrong pairing is written into the test.
Fix: write the pairs: `usage` 2, `unauthorised` 2, `forbidden` 2, `not-found` 2, `conflict` 1, `internal` 2, `check-failed` 1 with the result printed, and `no-project` in its own test.

### I-8 · Important · d-z1pncx rests on a cloud session seeing its token, which the research says it never does

Handle: d-z1pncx's reasoning ("a cloud session holds lodge's project token as a network secret of its environment, which reaches the session's environment"); `docs/research/2026-11-02-server-feasibility.md:43` ("a key Anthropic's proxy adds as a header to requests for the hosts it names; the session never sees the key"); `docs/superpowers/specs/2026-11-02-lodge-server-architecture-options.md:13` ("so the session never sees it"); design lines 62, 192, and 212 to 213 (cloud sessions use the `lodge` command); plan line 249 (`tokenOf` throws when `LODGE_TOKEN` is unset or empty).
Failure: in a cloud session `LODGE_TOKEN` is unset by design (must-not 6 and the research both keep the token out of the session), so every command that reaches the server stops with `LODGE_TOKEN is not set` before sending the request to which the proxy would add the header; the design's first way in for cloud sessions cannot work with the command this plan builds, and the ruling recorded in lodge carries a premise its own sources contradict.
Not checked: which header the proxy adds and whether it can be `Authorization: Bearer`; the research does not say.
Fix: `tokenOf` gives `null` when `LODGE_TOKEN` is unset, the client then sends no `Authorization`, and the server's `unauthorised` sentence names both routes; `token_comes_from_the_environment` keeps the set case and asserts the request carries no `Authorization` when unset; the reasoning of d-z1pncx is corrected by a new decision that narrows it (the planner's call, with the header question left open for step 4's cloud sessions).

## Checked and holding

- Probe 1 rerun (smol-toml 1.9.1, `integersAsBigInt: true`, Bun 1.3.14): every line as `probes.md` prints it; sixteen further cases (`+80`, `1_000`, `080`, `1__0`, a table twice, a key twice, a date, a time, a date-time, `nan`, `-0`, `0o17`, `[store` after `[server]`, `\u0000`, CRLF, a tab) are accepted or refused by smol-toml exactly as `tomllib` does, dates arriving as `TomlDate`, a `Date`; so d-dfkqec's conversion and `parseCoreSettings` of `origin/server-core` (`ts/src/core/settings.ts:35-63`) refuse `80.0`, `inf`, and a date with lodge 0.2's sentences.
- @simplewebauthn/server 14.0.3 under Bun (plan 1's software authenticator, extended): registration and sign-in pass with `expectedChallenge` as a function that spends the challenge, `requireUserVerification: true`, and an `http://localhost:8787` origin with RP ID `localhost`; the same response sent twice is refused; flags without UV are refused at registration (`0x41`) and at sign-in (`0x01`); an equal counter is refused (`esm/authentication/verifyAuthenticationResponse.js:186-192`: refused when `counter <= stored` unless both are 0, so "going back" includes standing still); another origin is refused.
- Probe 5 rerun: the compiled client against `Bun.serve` in the same process with an awaited `Bun.spawn` prints `async spawn: 0 200 0.3.0 {"a":"é😀"}`.
- Probe 6 rerun in a scratch repository: every line as printed, plus M-1.
- The names of plan 2 at 7204ad3 that the plan consumes exist with the signatures it uses (`Lodge`'s eighteen operations and `held`, `approve`, `decline`; `Projects`; `SqliteProjects(database, clock)`; `openDatabase`; `Actor`, `person`, `agent`, `actorText`; `coreSettings`; `stampOf`; `Forbidden`; `HeldDraft` and `Held`; `AddOutcome.HELD`; `Added.awaits` and `held`; `wired`, `project`, `CountingIds`), except `FixedClock.advance` (M-2).
- The carried tests that seed `decided_by="author"` (`test_search.py`, `test_spec.py`, `test_show_levels.py`, `test_waiting.py`, `test_same_second.py`, `test_broken_agent_decision_warns_above_show.py`) assert nothing on the seeding add's output beyond `code == 0` and the decision's ID, so approving the hold weakens none of them, provided `seed` and `approve` assert what I-2 asks; `test_same_second`'s `slept == [0.75]` survives, since neither the held add nor the approval meets an earlier decision in the same second; `test_waiting`'s first exact output survives, since plan 2's `waitingAll` does not list holds.
- The decisions against the design: d-p8jdqj, d-dfkqec, d-y0ppty (its claim that every `configure` precedes the store holds, `grep -n configure tests/e2e/*.py`), d-kt4jkq, d-3ywdhq, d-vfyex3 (`layoutViolations` allows only `src/main.ts` at the root), d-rn4qzq (but I-6 for IP origins), d-kky8qc, d-bwb1tt (but I-2), d-5kskm3 (probe 3 not rerun), and d-djh40k hold; d-z1pncx does not (I-8).
- The session cookie's flags, the `Origin` check, tokens and sessions stored as SHA-256 hashes, the setup code's 15 minutes and single use, the counter check, and the 422 answer each have a named test; the gaps are M-3 and I-6.

## Files read and not read

Read: the plan, its ledger, `planner-brief.md`, `planner-report.md`, `probes.md`, and `probes/{toml.ts,client.ts,serve-binary.ts,package.json}`; the server design in full; plan 1's Global Constraints, Calls made, Review Focus, "The rest of build step 1", "Settled for the later plans", its parity rows for `tests/e2e`, `tests/test_entry_point.py`, and `tests/test_wheel.py`, its probes 1 to 3, 13, and 25, and `probes/tests/passkey.test.ts`; plan 2 at 7204ad3, lines 17 to 260 and 341 to 600; `CLAUDE.md`; `tests/e2e/{conftest,support}.py` and the test files `add_attach`, `add_dry_run`, `add_failing_check_exits_1`, `add_import`, `add_new_decision_entry_area`, `add_non_string_scalar_exits_2`, `before_init_one_sentence_exit_2`, `broken_agent_decision_warns_above_show`, `check_and_gate`, `draft_then_add_edit`, `guide`, `help_lists_every_command`, `id`, `init`, `malformed_settings_one_sentence_exit_2`, `outside_repository_one_sentence_exit_2`, `same_second`, `search_limit`, `search_shows_unparsable_file`, `show_ambiguous_code_one_line`, `show_levels`, `threads`, and `waiting`; `tests/app/test_thread_fix_paths.py`; `src/lodge/cli/commands.py`, `threads.py:60-110`, `guide.md`; `src/lodge/main.py:20-70`; `src/lodge/core/settings.py:25-75`, `views.py:195-215`, `check_immutable.py:1-16`; `src/lodge/gitstore/settings.py:1-80`; at `origin/server-core`, `ts/src/core/{index,ids,settings}.ts`, `ts/tests/structure/calls.ts`, `ts/tests/parity.test.ts`, `ts/.dependency-cruiser.cjs`, `ts/knip.json`, `ts/package.json`; `docs/research/2026-11-02-server-feasibility.md:36-50`; the architecture options, line 13; the twelve rulings and d-v9mw2d with `lodge show --reasoning`.
Not read: plan 1's task bodies and ledger; plan 2's Tasks 3 to 6, 8, 9, 13, and 14 in full; `src/lodge/cli/{output,thread_output,parser}.py`; `src/lodge/app`; `tests/test_entry_point.py`, `tests/test_wheel.py`; `tests/e2e/test_search.py` and `test_spec.py` beyond a grep; `probes/text-import/`.
Not rerun: probes 2 (plan 2 not merged), 3, 4, and 7; nothing was run in a browser, so I-6 rests on the WebAuthn specification.

## Counts

Blocking 1 (B-1), Important 8 (I-1 to I-8), Minor 9 (M-1 to M-9).
