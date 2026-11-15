# Task 7a report

Implemented every non-server command through `run(argv, io)`, with requests sent only through `io.fetch`.
The client sends the project in JSON, sends the token only in `Authorization`, requires the matching `Lodge-Version`, decodes tagged maps and sets, and maps API errors to the prescribed sentences and exit codes.
The guide is embedded as text, and `#cli` exports `Io`, `run`, `fromWire`, `Call`, and `runThread` alongside the earlier tasks' exports.
`reply` and `close` send `thread: command.ref`.
No API source, `main.ts`, earlier report, brief, or review was changed.

## Workflow and verification

Read `CLAUDE.md`, the required plan sections, the inherited global constraints, the Python sources, and the carried tests before implementation.
`uv run --frozen --quiet lodge waiting` reported nothing waiting for either an agent or the author.
The coordinator ruled that the unavailable superpowers skill was a coordinator instruction, and authorised sole-builder, test-first work without delegation.
The initial required command, `cd ts && bun test tests/e2e tests/cli tests/parity.test.ts`, failed with 154 passes, 19 failures, and 18 module errors before the implementation existed.
The two former thread fix-path todos were also run before implementation and failed on the missing thread-output module.
The new dropped-name fixture failed before `rowMissing` learnt to exclude dropped names.
The client tests use the actual API envelope, `{error: {kind, message}, result}`, as `http.ts` provides it.
A later test, `thread_file_errors_are_cli_errors`, failed because returning the thread promise bypassed `run`'s catch; awaiting that promise fixed it.
`file_errors_keep_the_name_as_given` failed on absolute paths in errors for relative arguments before `run` restored their original spelling.

The first successful `sh scripts/check-ts.sh` finished with 1738 passes and no failures.
That gate included the widened parity checks, the wheel row restored to planned, and the two dropped lists needed by the already-changed rows.
The task's remaining parity rows were then written and the gate passed again with 1740 passes and no failures.
The final targeted run after the relative-path fix passed 246 tests with no failures.
The final `sh scripts/check-ts.sh` exited 0 with 1741 passes, 0 failures, no skips, and 4768 assertions across 147 files.
`git diff --check` also passed.
Biome is run by the gate with `--error-on-warnings`; its literal-key information messages are informational diagnostics.
All source and test modules stay within 300 lines.
No gate test opened a socket, and `LODGE_E2E_BINARY` was unset.
No package was added or installed.
The socket and binary path is implemented only behind `LODGE_E2E_BINARY` for S1; S1, Task 8, and the Coordinator step were not run.

The gate initially rejected a direct import of thread output helpers in the app test.
The coordinator explicitly ruled against exporting those helpers or the guide text, and directed that the orphaned-thread assertions run through `runThread` over a `Call` instead.
The app test retains its `MemoryStore` as `const store = project(); wired(store)` and passes the results through `toWire` and `fromWire`.
The guide is exposed by `run(["guide"], io)` only, as that ruling requires.

## Approval evidence

Each of these carried tests calls `seed` with `decidedBy: "author"`, asserts the add's exit 0 and empty error stream, matches its last held line exactly, approves through the registered person's session with the matching Origin, asserts `published`, and takes the decision ID from that approval:

- `search_shows_quote_of_author_decision`.
- `show_levels`.
- `spec_escapes_hash_lines_inside_a_statement`.
- `waiting`.
- `broken_agent_decision_warns_above_show`.

`waiting_groups_threads` separately asserts exit 0, empty error output, and the exact held-message line for its `--by author` question.
It approves that hold through the same session, asserts `published`, and uses the approval's thread ID in the original grouping assertions.
The server helper obtains this session by registering a passkey with `issueSetupCode` and `SoftAuthenticator`, then issues the `work` token through `token-issue`.
No synthetic session is inserted directly into the account store.

## Substitutions and parity changes by test

All carried commands run in process through `run` against their own `testServer()` and in-memory database, replacing the Python command's git-backed runtime as d-bwb1tt requires.
The default seed still creates the same three records, with the server's `published` outcome replacing `staged`; its ID reader takes the ID from that publication line.
The seed helpers and the tests consuming them retain their original record statements, filters, ordering, flags, and error assertions.

| Tests | Store substitution or specified change |
|---|---|
| `init` | Checks the two prescribed server lines and an empty store path list, replacing the two staged `.gitkeep` paths; the server creates no such files. |
| `init_twice_is_refused` | Keeps exit 2 and empty output, with the prescribed sentence naming existing project `work`. |
| `init_when_the_server_cannot_be_reached` | Adds the prescribed one-line network error check with the project's URL. |
| `search_shows_unparsable_file` | Publishes the same broken file through `handEdit`, then checks the same problem prefix and first record line. |
| `show_ambiguous_code_one_line` | Publishes the same second decision through the store, then checks the original one-line error and both IDs. |
| `check_prints_unreadable_files_and_fails` | Publishes the same unreadable file through the store and still requires exactly one problem line and exit 1. |
| `check_and_gate` | Replaces the forbidden rewrite of a published decision with a new, unquoted author decision, using a minted ID; checks clean `ok`, check 3, the ID, `fails check`, and the passing gate's `already published` note exactly as d-4qv0xb specifies. |
| `broken_agent_decision_warns_above_show` | After the approved author seed, one publication writes a new broken decision and the edited entry, instead of publishing and then corrupting an immutable decision; retains the original problem prefix, entry line, and author quote assertions. |
| `waiting_groups_threads` | Replaces the ID formerly read from the author's immediate write with the approved held-message ID, retaining both groups' membership and ordering assertions. |
| Five author-seed tests listed above | Replace the immediate staged add with a held add and approval, retaining their original subsequent assertions. |
| `malformed_settings_one_sentence_exit_2` | Keeps all three Python inputs; `[store]` now reports unknown section, and the additional `80.0` case checks the exact whole-number sentence. |
| `help_lists_every_command`, `every_command_has_help` | Keep all available commands, omitting `view` until step 3 and `hook` until plan 4. |
| `version_works_anywhere` | Reads `ts/package.json`'s version instead of expecting Python's 0.2.0. |
| Guide tests | Compare the embedded server guide and retain the original shortness, vocabulary, introduction, heading spacing, and waiting-first assertions, with the specified server write-path and approval phrases. |
| `orphaned_thread_outputs` | Uses the existing `MemoryStore`, rewrites the thread's subject there, and checks the missing-subject line through both `threads` and `thread` commands, per the coordinator's front-door ruling. |
| `run_thread_outcomes` | Supplies the original fixed failed check and written result through a decoded `Call`, preserving the published line, failed-check message, suffix, and both exit codes. |

Dropped only `gate_passes_with_notes_for_new_records` and `init_in_an_unwritable_checkout` from this task's changed rows.
The former has no new unpublished records after a server seed; the latter tests checkout writes that server init does not perform.
All other Python test names are retained, including every case of each carried parametrisation.
The other carried tests require no assertion substitutions beyond their runtime and seed helpers.
The wheel row remains planned for Task 8.

## Output differences from lodge 0.2

- Init names the created project and server, followed by the unchanged `next: lodge guide` line; repeated init names the existing project, since the server owns its data.
- Successful writes say `published` where checkout mode said `staged`, since server publication makes records current immediately.
- A held add marks minted IDs provisional and ends with the prescribed approval sentence; a held thread message prints that sentence too, because an agent cannot publish the person's words without approval.
- A dry run awaiting a person prints the prescribed approval note before `dry run: nothing published`.
- The new invalid published decision in `check_and_gate` reports check 3, and the gate notes it as `already published` and passes, as d-4qv0xb and design line 79 specify.
- `[store]` is unknown in server settings, and `80.0` is refused as a whole-number setting, as d-1zmfdr and d-dfkqec specify.
- Help excludes the deferred commands, and version prints the package's 0.3.0, as d-sry12f and d-vfyex3 specify.
- The guide adds the server, token, and initial-settings paragraph; describes imported broken records instead of edited published decisions; removes the rewritten-branch advice; describes draft files, server publication, server checks, and the server clock; and explains held author adds and messages, using every replacement given by Task 7a.
- Client-only reachability, version, non-JSON, and authorisation errors use the plan's exact new sentences.

No other intentional output differences remain.
Relative file errors retain the argument's original name, draft text normalises line endings, and attachments and thread messages preserve exact line endings.

## Function-to-test map

Inline helpers are identified by their Python names even where their TypeScript implementation is part of their caller.

| Python function | TypeScript implementation | Carried line assertions or mutation-backed tests |
|---|---|---|
| `output.is_decision_file` | `isDecisionFile` | M01, `draft_decision_note_and_exact_text`, including a decision-like body in a spec. |
| `output.read_lines` | `readLines` | `search_shows_unparsable_file`, `check_prints_unreadable_files_and_fails`; M02 also pins freshness. |
| `output.listed_text` | `listedText` | `search`, `search_without_hits`, `search_limit_says_what_it_left_out`. |
| `output.shown_text` | `shownText` | `show_levels`, `show_entry_reasoning_lists_its_decisions`; M04 pins exact section separation. |
| `output.check_lines` | `checkLines` | `check_and_gate`, `check_prints_unreadable_files_and_fails`, `run_thread_outcomes`; M05 pins comparison of all problem fields. |
| `output.added_lines` | `addedLines` | Seed publication IDs and held-line assertions; M06 and `add_awaits_output` pin publication and approval formatting, while M07 pins failed dry-run lines. |
| `output._marked` | `marked` | M07, M08, M09, `add_output_marks_ids_with_unicode_boundaries_and_escapes`. |
| `output._blocks` | Inline in `listedText` | M03 and `search` require the blank line between blocks. |
| `output._section` | `section` | M10 and `show_levels` pin headings; `shown_sections_keep_blank_lines` pins separation. |
| `output._where` | `where` | M11 and `search_shows_unparsable_file` require the problem's line number. |
| `thread_output.thread_head` | `threadHead` | M12 and `orphaned_thread_outputs`; waiting tests pin group placement, and `thread_wire_prints_closed_messages_exactly` pins the full head. |
| `thread_output.thread_text` | `threadText` | `orphaned_thread_outputs`; M13 and `thread_wire_prints_closed_messages_exactly` pin exact messages, provenance, and closing prefix. |
| `thread_output.waiting_text` | `waitingText` | M14, `waiting`, and `waiting_groups_threads`. |
| `commands.run` | `run` | Init, help, guide, ID, search, show, spec, check, waiting, malformed settings, and outside-repository carries; M15 pins init's server line. |
| `commands._add` | Add branch in `run` | Seed publication and held lines; M06, M07, and both `add_awaits_output` cases. |
| `commands._check` | Check branch in `run` | `check_and_gate`, `check_prints_unreadable_files_and_fails`, and `check_deduplicates_every_problem_field`. |
| `commands._read_drafts` | Draft mapping in `run` | M16 and `add_sends_draft_names_and_exact_attachments` pin original names and normalised text; `files_are_read_in_command_order` pins precedence. |
| `commands._read_attachments` | Attachment mapping in `run` | M17 and M18, `add_sends_draft_names_and_exact_attachments`, pin base names and exact text. |
| `threads.run_thread` | `runThread` | `orphaned_thread_outputs`, `run_thread_outcomes`, and the waiting carries; M19 pins the reply/close request field and M20 pins failed-write exit 1. |

`heldLine` is the additional shared formatter required by the server design, pinned by the five author-seed carries, `waiting_groups_threads`, and `add_awaits_output`.
Thread grammar and argument-building functions were already implemented by Task 2 and are not newly ported here.

## Mutation runs

Every mutation below was applied alone, its named tests were run, the failing result was observed, and the source was restored in a `finally` block.
All killed mutations exited 1.

| Run | Deliberate defect | Observed failing test |
|---|---|---|
| M01 | Invert decision-header detection. | `draft_decision_note_and_exact_text` |
| M02 | Drop the freshness line. | `check_deduplicates_every_problem_field` |
| M03 | Use one newline between listed blocks. | `search` |
| M04, first run | Use one newline between shown sections. | Survived the carried `show_levels` assertions; no claim of coverage was made from that run. |
| M04, second run | Repeat the same mutation after adding the exact-spacing assertion. | `shown_sections_keep_blank_lines` |
| M05 | Ignore path when comparing already-shown problems. | `check_deduplicates_every_problem_field` |
| M06 | Replace the publication line, including its IDs, with `published`. | `search`, `search_by_code_and_filters`, `search_without_hits`, `search_bad_filter_is_a_usage_error` |
| M07 | Suppress provisional suffixes in problem messages. | `add_output_marks_ids_with_unicode_boundaries_and_escapes` |
| M08 | Stop escaping IDs in the marking pattern. | `add_output_marks_ids_with_unicode_boundaries_and_escapes` |
| M09 | Replace Unicode word boundaries with ASCII boundaries. | `add_output_marks_ids_with_unicode_boundaries_and_escapes` |
| M10 | Replace a shown section's heading with `Wrong`. | `show_levels` |
| M11 | Omit a problem's line number. | `search_shows_unparsable_file` |
| M12 | Replace the orphan subject fallback with `unknown`. | `orphaned_thread_outputs` |
| M13 | Remove the last closed message's `closed by ` prefix. | `thread_wire_prints_closed_messages_exactly` |
| M14 | Rename the agent waiting group. | `waiting` |
| M15 | Remove the URL from init's first line. | `init` |
| M16 | Read drafts exactly instead of normalising their CRLF. | `add_sends_draft_names_and_exact_attachments` |
| M17 | Send an attachment's full path instead of its base name. | `add_sends_draft_names_and_exact_attachments` |
| M18 | Normalise attachment text as a draft. | `add_sends_draft_names_and_exact_attachments` |
| M19 | Send `ref` instead of `thread` on replies and closes. | `reply_and_close_use_thread_and_exact_messages` |
| M20 | Return 0 for a failed thread write. | `run_thread_outcomes` with `check failed`, 1 |

The final green gate runs after all mutations have been reverted.
