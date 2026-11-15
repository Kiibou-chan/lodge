Correctness review of Task 7b, range `47afa32..026243d`, dated 2026-11-15.

**Result: 0 Important findings, 0 Minor findings.**
The carried assertions, prescribed changes, helper correction, parity rows, and mutation evidence satisfy the reviewed brief and Task 7b.

Read `CLAUDE.md` first, ran `lodge waiting` (nothing waiting), and read the plan's Global Constraints, parity table, Task 7b, review brief, and build report.
Read d-bwb1tt and d-4qv0xb through `lodge show --reasoning`.
Compared all ten carried files with the worktree's lodge 0.2 `tests/e2e/test_*.py`, including their helpers, every assertion, and every parameter value.
The ten rows retain 36 Python test functions, yielding 38 carried test cases, and drop exactly the three names prescribed by the plan.
The four additional tests bring Task 7b to 42 cases across eleven test files.

**Checked and found sound**

Paths in this table are relative to `ts/tests/e2e/`; the Python counterpart has the same name with underscores and the `test_` prefix.

| File | Assertions and substitutions checked |
|---|---|
| `add-attach.test.ts` | Exact stored `LOG`, including CRLF and café, attachment-path membership, provenance, clean check, dry-run non-publication, exact two-name attachment listing, invalid UTF-8 refusal and absence of attachments, two-decision refusal, missing-file diagnostic and single newline, unlisted-attachment refusal, and the negative search assertion all remain. |
| `add-bad-yaml-exits-2-naming-file-and-line.test.ts` | Both tests retain exit codes, empty output where required, the filename prefix, the single diagnostic newline, and the alternative line-3 or line-4 assertion. |
| `add-dry-run.test.ts` | All four tests retain outcomes, store-state equality and negative search, failed-check lines, exact final two lines, non-empty feedback/check selections, provisional marks on every selected line, and absence of provisional marks on the subsequent real add. |
| `add-failing-check-exits-1.test.ts` | Exit 1 with empty errors, exact failed outcome, check 4 naming the entry, and zero stored spec/storage paths preserve the Python assertions. |
| `add-import.test.ts` | Flag refusal and unlisted-source failure remain; the permitted import requires exit 0, empty errors, the exact final held line, approval through the person's session, a published approval outcome, the first approved decision ID, and both `imported` and `unquoted` through `show`. |
| `add-new-decision-entry-area.test.ts` | Publication prefix and entry membership, area note, three stored records in place of five staged paths including `.gitkeep`, successful show and clean check, feedback ordering, usage, missing-file and UTF-8 diagnostics, unchanged outcome, and absence of `note: nothing changed` remain. |
| `add-non-string-scalar-exits-2.test.ts` | Exact filename/line prefix, `title`, single diagnostic newline, empty output and exit 2 remain; YAML `no` still succeeds and appears on the exact shown line. |
| `draft-then-add-edit.test.ts` | Draft prefixes and ID, successful publication and edited text, area draft, exact unknown-record result, stored-text newline count plus one, decision immutability note, empty entry-draft errors, and help text all remain. |
| `same-second.test.ts` | The server clock stands still before the author seed; the seed checks the held line and approves it through the registered person's session; `[0.75]`, the negative assertion before the author group, the following current/coordinator line, both shown flags, and a successful gate remain. |
| `threads.test.ts` | Ask/reply/close outcomes, listing counts, message presence and order, closure line, absence of `Closed.`, all three missing-provenance combinations and exact grammar message, agent-role refusal, unknown-reference diagnostic without `usage:`, both reply/close cases, and both missing/non-UTF-8 file cases remain. |

`threads.test.ts:120` retains the exact author/time/place/text substring, including the lone carriage return.
At `threads.test.ts:125`, the stored thread is loaded with `load(tree({ rev: null, files: ... }))` and its first message must equal `a\rb\nc\nd`.
The relayed question checks the held line, approves it through the person's session, and takes its question ID from that published approval, as d-4qv0xb requires.
`server.ts:78` establishes that session through the software-authenticator registration flow, and `server.ts:94` asserts the approval outcome before returning IDs.

All three new ordering comparisons preserve Python's raising `index` semantics.
`add-new-decision-entry-area.test.ts:46` requires a non-empty feedback list, its expected first prefix, and membership before `indexOf`.
`same-second.test.ts:21` requires the author heading before locating it and checking the preceding slice.
`threads.test.ts:28` requires both message texts before comparing their indices.
Negative assertions were checked individually, including both provisional-mark exclusions, no search matches, no attachment paths, no unchanged note, no unknown-reference usage text, no synthetic close message, and no flagged decision before the author group.

`held.test.ts:23` uses the prescribed author decision, quote, and 81-word statement.
It requires exit 0, empty errors, the exact final held line, at least one ID-bearing line, a provisional suffix on every ID occurrence above that line, and the exact feedback prefix naming the 81-word statement.
`held.test.ts:43` requires exit 0, empty errors, and the exact final approval-note and dry-run lines.
Both tests fail under their prescribed output mutations.

The range changes no file under `ts/src/cli`.
Its only helper implementation change is `server.ts:110`, adding attachment-text keys to the sorted paths returned from the store.
Reverting that behaviour makes the two original attachment tests fail at `add-attach.test.ts:33` and `add-attach.test.ts:55`, and the direct regression fail at `add-attach.test.ts:109` with three paths instead of four.
This independently reproduces the report's justification for the fix.

All ten `ts/tests/parity.json` rows match the plan's final statuses, counterpart paths, dropped names, and reasons.
The only dropped names are `attachment_lands_on_the_branch_in_branch_mode`, `agent_edit_in_the_same_second_publishes_in_branch_mode`, and `thread_files_are_staged_not_committed`.
The seven other rows are `ported`, with the permitted store/publication/approval substitutions.
`ts/knip.json:2` removes the support entry exemption exactly when `document`, `entryText`, and `areaText` gain their Task 7b readers.
The parity checks and knip pass in the full gate.

**Independent execution evidence**

All executable review probes ran in a detached temporary git worktree at `026243d`, using the existing dependencies without installing packages.
`LODGE_E2E_BINARY` was unset in every run.
Mutations were applied individually and restored before the next mutation; every targeted invocation exited 1 at an assertion in its selected test.
For each report mapping, the command was `bun test tests/e2e/<file>.test.ts --test-name-pattern '^<test_name>( |$)'` from `ts/`.
The following table uses the mutation definitions and per-test mappings in `task-7b-report.md`.

| Mutation | Independently observed failures |
|---|---|
| M01, full attachment path | Both named attachment tests fail. |
| M02, shortened UTF-8 explanation | The invalid attachment test fails. |
| M03, replaced caught diagnostic | All thirteen named test functions fail, including both reply/close and both missing/non-UTF-8 cases, totalling fifteen failing cases. |
| M04, replaced grammar error | All three named tests fail. |
| M05, throw for `check-failed` | All three named tests fail. |
| M06, false dry-run publication line | `add_dry_run_publishes_nothing` fails. |
| M07, empty provisional set | Both carried provisional tests and `held_add_marks_its_ids_provisional` fail. |
| M08, omitted approval note | `dry_run_of_a_persons_decision_names_who_approves` fails. |
| M09, missing publication IDs | `add_new_decision_entry_area` fails. |
| M10, wrong feedback prefix | `add_prints_feedback_before_the_outcome` fails. |
| M11, changed instead of unchanged | `add_nothing_changed` fails. |
| M12, wrong draft prefix and extra newline | All four named draft tests fail. |
| M13, replaced level-one block | The YAML-word and same-second tests fail. |
| M14, wrong thread publication outcome | `ask_reply_close_round_trip` fails. |
| M15, stripped message carriage returns | `author_words_are_recorded_exactly` fails. |
| M16b, preserve draft CRLF | `draft_crlf_is_normalised_before_request` fails at its request-body equality assertion. |
| M17, shortened held-add line | The import test fails. |
| M18, shortened held-thread line | The exact-author-words test fails. |
| M19, tree-only paths | The direct paths regression and both original attachment tests fail. |

There were 44 filtered invocations and 46 failing test executions, including the parameterised cases and the two additional original-test probes for M19.
No claimed mutation survived.
The report explicitly disclaims coverage from its preliminary M16 run; M16b's request-boundary assertion supplies the claimed coverage.

With all mutations restored, `bun test tests/e2e` passed: 106 tests, 0 failures, and 849 assertions.
`sh scripts/check-ts.sh` then exited 0: 1,804 tests, 0 failures, and 5,208 assertions across 159 files, including formatting/lint, type checking, dependency rules, knip, structure checks, and parity checks.

A separate scratch-only preload made `Bun.serve` and global `fetch` throw, and recorded `node:fs` file reads and existence checks while running the eleven Task 7b test files.
All 42 tests passed, with 364 assertions; all 618 recorded file reads/existence checks were inside freshly created temporary `lodge-e2e-*` fixture folders.
Static inspection also confirms `project.ts:96` creates a synthetic `.git` directory, `server.ts:46` opens SQLite with `:memory:`, and requests use the injected handler.
The new tests perform no git subprocess calls and contain no binary-mode override.
The existing conditional socket branch is reserved for the coordinator's `LODGE_E2E_BINARY` run, as the plan requires.

The temporary worktree and probe artefacts were removed after verification.
Only this review file is added to the reviewed worktree.
