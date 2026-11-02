# Plan fix round 1: plan 3, the API, sign-in, and the command

Planner, fix round 1, on `server-api` from 1b4ba97, answering `plan-review-correctness.md` (1 Blocking, 8 Important, 9 Minor) and `plan-review-practice.md` (1 Blocking, 7 Important, 7 Minor).
Plan 2 aligned against `origin/server-store` at 61f87ad, after its fix round (d-pmaw3a, d-vwsnz5, d-x6vaw8, d-d96y91, d-nf7wvx, d-thvvzx, and its ledger's alignment notes for plan 3).
Status: done; 33 findings: 30 fixed in the plan text, 2 (B-1 of each review) settled by the coordinator's d-4zg8q3 and consumed in Global Constraints, 1 rejected by d-zthdm7 (practice I-6), 0 parked.

## Findings

### Rulings recorded

- d-1zmfdr (replaces d-z1pncx): the command sends `LODGE_TOKEN` when set and no `Authorization` otherwise (correctness I-8).
- d-amxk94 (replaces d-djh40k): `includeEntryExports` tags what a front-door test or plan 4 needs, removes the rest (practice I-1).
- d-zthdm7 (narrows d-p8jdqj): Task 7a stays one task, with a function-to-test map (practice I-6, rejected split).
- d-svv7gv (narrows d-4psbdv): the age rule covers transitive packages through `ts/bunfig.toml` (practice I-7).
- d-81ps01 (narrows d-bwb1tt): carried tests that rewrote a decision or relayed a person's words do what the server allows (correctness I-1, and plan 2's d-pmaw3a and d-x6vaw8); probe 8 added to `probes.md`.

### Both reviews

- B-1 (correctness and practice): settled by the coordinator's d-4zg8q3; Global Constraints, first bullet: this plan starts from `server-core` after plan 1's fix wave lands it, `main` prints through `process.stdout.write` and `process.stderr.write`, `api` logs through `ApiOptions.log`; the Structure bullet says printing is not a file write; no task added.

### Plan 2 alignment (coordinator's message, `origin/server-store` 61f87ad)

- "Names consumed from plan 2": aligned at 61f87ad; adds `FixedClock.sleep` as the way time moves, `attachmentTexts`, `wired`'s actor, `applyEvent`'s `heads` rule, d-thvvzx, d-pmaw3a, d-x6vaw8 with STORE-1, and d-vwsnz5 in place of d-kj59bz (every citation changed).
- Parity rows: `test_broken_agent_decision_warns_above_show.py`, `test_check_and_gate.py`, `test_threads.py`, and `test_waiting.py` changed by d-81ps01; `test_add_import.py` names the held add; the held paragraph names the line asserted and STORE-1's B.

### Correctness review

- I-1: fixed per d-81ps01 and probe 8; parity row of `test_check_and_gate.py` rewritten; Task 7a's `check_and_gate` writes a new unquoted decision by `author` by hand and asserts `check` (exit 1, `check 3: ` with the ID), `show` (`fails check`), and `check --gate` (exit 0, `ok`, then `note: already published, check 3: ` with the path and ID); the review's expected gate exit 1 does not hold on one state (probe 8: lodge 0.2 with the file published prints `ok` and the note).
- I-2: Task 7a's `seed` asserts the held line by pattern before approving, and `TestServer.approve` throws unless `published`; Task 7b's `import_needs_the_flag_and_a_listed_source` asserts the held line, the approval's `published`, and `show` of the approved ID; new `ts/tests/e2e/held.test.ts` in Task 7b asserts the provisional marks and the dry run's `note:` line above `dry run: nothing published`, each against a named mutation; the hold number is asserted by pattern, since it is the hold's event `seq`, not 1.
- I-3: Task 7a's parity bullet widens plan 2's three `ported_files_*` tests to `changed` rows of plans 2 and 3, less `dropped`, so plans 1 and 4's `changed` rows are not checked by name; `dropped_names_are_python_tests_of_a_changed_row` replaces the old rule's test.
- I-4: Task 7a's `Project` gains `url`, and every URL-bearing expectation reads it; `project({ unreachable })` throws in process and, in binary mode, points at a loopback port opened and closed first; S1 says every carried test runs in both modes and the ledger gives pass, skip, and fail counts.
- I-5: Task 5's Interfaces gain `tokenId(entropy)` in `tokens.ts` (`t-` and six characters of `#core`'s alphabet, `mintId` and `isId` unchanged); `issueToken` uses it; test `token_id_is_spelled_as_an_id`.
- I-6: Task 6's `setup` takes `https://<host>` and `http://localhost:<port>` only; `setup_refuses_a_bad_origin` gains `http://127.0.0.1:8787` and `http://[::1]:8787`; Task 3's `server.url` keeps the three loopback forms.
- I-7: Task 6's `held` answers each draft as `parseDraft` reads it (`title`, `statement`, `quote`, or `problem` and raw `text`); test `held_shows_the_drafts_as_core_reads_them`; Task 9's `page.js` writes those fields.
- I-8: d-1zmfdr replaces d-z1pncx, following design lines 49, 192, and 213 and the research note's line 43, so no question for the author; Calls made 2; Task 3's `tokenOf` gives `null` when unset or empty, test `token_comes_from_the_environment`; Task 7a's client sends no `Authorization` without a token, test `no_token_sends_no_authorization`, and the `unauthorised` sentence names both places a token comes from.
- M-1: Task 2's usage-error bullet names the top-level `unrecognized arguments` line; `extra_words_are_an_error` asserts the whole `err`.
- M-2: Task 5's `world.ts` and Task 6's expiry tests move the clock with `FixedClock.sleep`.
- M-3: Task 4's `spendSetupCode` reads and appends in one transaction opening with a write (d-thvvzx); `setup_code_is_spent_once` adds two concurrent spends.
- M-4: Task 6's user ID is the first 16 bytes of SHA-256 of `<origin> <person>`; test `register_options_keep_one_user_id`.
- M-5: Task 6's `setup` checks the person's name (test `setup_refuses_a_bad_person`); Task 5's `project-create` on a server not set up is `usage` (test `project_create_before_setup_is_usage`).

### Practice review

- I-2: Global Constraints gain "Exports read in a later task" with `ts/tests/e2e/support.ts` (into `entry` in Task 7a, out in Task 7b); Task 2's `index.ts` exports `ThreadCommand`.
- I-4: "Names consumed from plan 2" names `FixedClock.sleep` and `attachmentTexts`, aligned at 61f87ad; "Order and lanes" gains the coordinator's step before Task 4's brief (merge plan 2, then diff the names against the merged code and plan 2's rulings, a mismatch being a fix round with plan 4 told).
- I-5: as correctness I-5.
- I-7: d-svv7gv; Task 1 creates `ts/bunfig.toml` with `minimumReleaseAge = 1209600`, and its Step 2 checks each version new in `ts/bun.lock` against its publication date; plan 1's lock is left to plan 1 (named in the report).
- M-1: "Order and lanes", step 1 before Task 4: merge plan 2 keeping both sides of `ts/package.json`, regenerate `ts/bun.lock` under `ts/bunfig.toml`, `--frozen-lockfile`, `sh scripts/check.sh`.
- M-3: S1 gains the `server setup`, `server serve`, and `curl … /api/v1/me` check of the binary's own socket.
- M-4: plan 1's paths written under `docs/superpowers/plans/done/` (header, Global Constraints, Task 6's `authenticator.ts`, and `probes.md`'s header).
- M-5: `ApiOptions.log` (Task 5); `main` binds it to `process.stderr.write`; Tasks 5 and 6 log through it; `unexpected_error_is_internal_without_detail` reads the world's log.
- M-6: "Order and lanes": lane D is rebased onto `server-api` after Task 8 merges and its gate rerun before review.
- M-7: Task 2: help bodies follow argparse's layout at 80 columns as far as the carried tests and probe 6 check, other differences listed in the report.

### Correctness review, remaining

- M-6: Global Constraints' Porting bullet and Review Focus 1 name d-bwb1tt's third substitution (the held add approved, with the held line asserted) and d-81ps01's changes.
- M-7: Task 7a's guide changes: line 55 says such an add waits for the author's approval and prints `held for approval`, which `guide_is_short_and_covers_the_write_path` looks for; line 26 says only the author writes `--by author` (d-x6vaw8); the count of lines is unchanged.
- M-8: Task 8's `environment.test.ts` gains `main_clears_yaml_logging_first`, which reads `src/main.ts` with TypeScript's parser.
- M-9: Task 7a's `kinds_map_to_exit_codes` names each kind with its code.

### Practice review, remaining

- I-1: d-amxk94 replaces d-djh40k; Calls made 12; Task 8's tagging bullet and Modify list widened to `core`, `app`, `store`, `cli`, `api`, and the test files knip names.
- I-3: as correctness I-4.
- I-6: rejected by d-zthdm7 (every cut leaves `run` with stand-ins or ports `output.py` across two tasks); Calls made 13; Task 7a's Step 4 report maps each ported function to its pinning tests, with a named mutation for any function none pins.
- M-2: Task 8's `binary.test.ts` removes its folder in `afterAll`.
