# Task 6 review

Commit a73a148 against a8b5bc4, `ts/` only.
Probes ran in a detached scratch worktree at a73a148, its `ts/node_modules` a link to the build worktree's; the worktree is removed when the review ends.

## Summary

0 Blocking, 0 Important, 9 Minor.
`writeThread` agrees with lodge 0.2 byte for byte on 1207 threads built from the repository's records and edge text, `parseThread` on 2399 texts apart from YAML parser wording, and `load` on the repository's records and two variant trees, order included; a targeted mutation kills every carried and new test but one, `UNESCAPE` with the `m` flag (C-2).
The two `test.todo`s are allowed: both sit in rows still `planned`, and each waits on code a later task ports.

## Correctness

### The two `test.todo`s

`ported_files_hold_no_todo` binds only `ported` rows (plan line 414), and the builder left `tests/core/test_thread_files.py` and `tests/core/test_snapshot.py` at `planned` (`ts/tests/parity.json`), flipping only `builders.py` and `test_fileformat_links.py`, as Step 4 of the brief says.
The plan's parity table gives both rows two tasks, `Tasks 6 and 9a` and `Tasks 6 and 10` (plan lines 194 and 195), and the later tasks flip them (plan lines 656 and 699), so a todo in either file is allowed until then.
Both wait on code no earlier task has ported: `duplicate_id_marks_kept_record_failing` (`tests/core/test_snapshot.py:79-86`) calls `check_state`, `failing_ids`, `unrecorded_problems`, and `level1`, the last three of `views.py`, which Task 9a ports (plan line 651); `thread_id_is_not_number_feedback` (`tests/core/test_thread_files.py:198-201`) calls `feedback`, which Task 10 ports.
Since neither row is `ported`, the parity test checks no name in either file at this task; every Python name was checked by hand instead: all 20 of `test_thread_files.py` and all 6 of `test_snapshot.py` are titles in the TypeScript files.

### Writer and reader against lodge 0.2 (Review Focus 2 and 7)

This repository holds no thread file under `lodge/` at a73a148, on any branch (`git log --all -- 'lodge/threads/*'` is empty), so the byte comparison ran on threads built from the repository's records instead, as test input only.
Run: `ts/probe/gen.py` in the scratch worktree builds 1207 threads: for each of the 359 files under `lodge/`, one thread whose messages carry the file's body trimmed (one by `coordinator`, one by `author` with its title as `where`), one with the body untrimmed, and one with the header text; then edge cases as message text (U+2028 and a lone CR before `## Message 1`, `\## Message 2`, `\\## Message 3`, a heading after `\n`, U+2029, U+0085, U+001C, U+FEFF, an astral character, a lone surrogate, CRLF, a tab, `## Message ٢`, an empty and a blank text, each alone and as the closing message of a closed thread), awkward `where`, `when`, and `by` values, offsets `+00:60` and `-23:59`, `2026-02-30`, a bare day, `Z`, bad `about`, `raises`, and `state`, and a thread with no message.
`write_thread` in Python and `writeThread` in TypeScript then wrote each, the result compared as the text or as the error's class and message.
All 1207 agree: 794 texts byte for byte, 413 refusals with the same `ValueError` message.
Run: each of the 794 written texts and 1600 perturbations of the first 400 (a line deleted, a CR appended, `## Message 2` or a blank line or `where: x` or `when: [a, b` inserted, a line indented, `Message 1` renumbered `01`) and 5 malformed files, 2399 in all, parsed by `parse_thread` and `parseThread` and compared as normalised JSON.
2262 agree exactly; the 137 others are all `the header is not valid YAML` problems whose parser message differs (ruling d-p48gr1), 41 of them with a different line (finding C-3).
Run: `parse_thread`'s and `parseThread`'s problems agree on path, check, message, and line for every non-YAML refusal, including the line of `a message needs by and when`, of a misnumbered heading, of an unknown message key, and of a bad `when`.
Run: `load` in Python and TypeScript on three trees compared as ordered JSON (each map as its items in order, the problems as a list): the repository's 359 files under `lodge/` (221 decisions, 126 entries, 10 areas, 0 problems); the same with the 794 written threads and a listed attachment (1141 paths); and the records with a duplicated decision in a later and an earlier sorting path, an entry in `lodge/decisions/`, a decision under `lodge/spec/zzz/`, a nested and a duplicated thread, strays (`lodge/notes.txt`, `lodge/threads/.md`, a path ending `\n`, `_area.md.md`, an astral, a U+FFFF, and a non-ASCII name), `.gitkeep` files, an attachment that looks like a record, and paths outside `lodge/` (13 problems).
All three agree exactly, problem order and insertion order included.

### Stamps (Review Focus 4)

`opened` of `+00:60` and `-23:59` is written and read as lodge 0.2 does, and `2026-02-30T10:00:00+01:00`, a bare day, and `Z` are refused with the same message.
Run: `newest_last` and `newestLast` on 14 threads (`+00:60`, `-00:01`, `-00:00`, `0001-01-01T00:00:00+23:59`, `9999-12-31T23:59:59-23:59`, 29 February, five instants equal at different offsets, and the tie broken among `q-Z`, `q-a`, `q-ab`, `q-é`, `q-` U+E000, and `q-` U+10000) give the same order.
The written threads and the three trees give byte-identical TypeScript output under `TZ` set to `Pacific/Kiritimati`, `America/St_Johns`, and `UTC`; neither new module names `Date`.

### Carried tests against targeted mutations (Review Focus 1)

The report's evidence for the carried `fileformat-links.test.ts` is a `throw` at the top of `parseRecord`, `parseArea`, `writeRecord`, and `writeArea`, which Task 5b's review (C-1) showed proves only that a test calls the function.
Each mutation below was applied alone in the scratch worktree, run against the named test (`bun test <file> -t '^name( |$)'`) and then all of `tests/core` (303 tests), and reverted; the new tests over `threads.ts` and `snapshot.ts` were mutated the same way, since a missing export, their first failure, says nothing of what they assert.

| Mutation | Named test, failing cases | `tests/core` failing |
|---|---|---|
| `fileformat.ts:185` join `", "` to `","` | `rests_on_round_trips` 1 | 1 |
| `headers.ts:110` `restsOn` drops its first ID | `rests_on_round_trips` 1 | 1 |
| `fileformat.ts:47` `rank !== null` to truthy | `rank_round_trips` 1 | 1 |
| `fields.ts:160` `readRank` gives `null` for 0 | `rank_round_trips` 1 | 1 |
| `fields.ts:160` `readRank` returns the string | `rank_reads_quoted_and_plain_alike` 2 | 4 |
| `fields.ts:153` pattern `^-?[0-9]+$` | `rank_must_be_a_whole_number` 2 | 2 |
| `headers.ts:121` rank error rethrown as a bare `Error` | `rank_must_be_a_whole_number` 6 | 8 |
| `headers.ts:110` `rests_on` prefix `"s"` to `"d"` | `rests_on_holds_entry_ids_only` 1 | 2 |
| `fileformat.ts:47` always writes `rank` | `area_without_rank_writes_as_before` 1 | 4 |
| `threads.ts:97` `where: null` | `thread_round_trips` 1 | 2 |
| `threads.ts:62` every message of a closed thread is closing | `empty_text_only_on_the_closing_message` 1 | 1 |
| `threads.ts:118` `when` always quoted | `written_shape_matches_the_example` 1 | 3 |
| `threads.ts:20` `ESCAPE` without `\\*` | `text_line_like_a_heading_round_trips` 1 | 1 |
| `threads.ts:19` any `## ` line is a heading | `yaml_and_markdown_specials_round_trip` 1 | 1 |
| `threads.ts:86` author check off | `author_message_needs_where` 1 | 1 |
| `threads.ts:28` `readId` to `readStr` | `malformed_id_is_problem_1` 1 | 1 |
| `threads.ts:32` `q-` allowed in `about` | `about_must_name_a_decision_or_entry` 1 | 1 |
| `threads.ts:51` no-message check removed | `thread_needs_a_message` 1 | 1 |
| `threads.ts:55` numbering check off | `messages_numbered_in_order` 1 | 1 |
| `threads.ts:52` stray-text check off | `body_text_before_first_message_refused` 1 | 1 |
| `threads.ts:147` closed check removed | `appended_refuses_a_closed_thread` 1 | 1 |
| `threads.ts:158` ID tie-break dropped | `newest_last_by_opened_then_id` 1 | 2 |
| `snapshot.ts:92` thread paths not kept | `load_reads_threads_and_their_paths` 1 | 1 |
| `snapshot.ts:64` thread pattern `.+` | `nested_file_under_threads_is_stray` 1 | 1 |
| `threads.ts:144` CRLF kept | `appended_cleans_the_text_and_closes` 1 | 1 |
| `threads.ts:82` message `checkKeys` removed | `unreadable_header_values_are_problem_1` 1 | 1 |
| `threads.ts:130` message number off by one | `write_text_error_names_the_field` 2 | 2 |
| `threads.ts:77` line `+ 1` | `message_without_metadata_names_the_message` 1 | 1 |
| `threads.ts:20` `ESCAPE` with the `m` flag | `escape_breaks_lines_at_newline_only` 1 | 1 |
| `threads.ts:21` `UNESCAPE` with the `m` flag | `escape_breaks_lines_at_newline_only` survives | 0 (finding C-2) |
| `threads.ts:158` stamps compared as text | `newest_last_uses_instants_and_code_point_ids` 1 | 1 |
| `threads.ts:158` IDs compared with `<` | `newest_last_uses_instants_and_code_point_ids` 1 | 1 |
| `snapshot.ts:72` parse problems dropped | `load_keeps_good_records_beside_problems` 1 | 1 |
| `snapshot.ts:84` duplicate check off | `duplicate_id_is_problem_2_with_both_paths` 1 | 1 |
| `snapshot.ts:52` paths read in reverse | `duplicate_id_is_problem_2_with_both_paths` 1 | 1 |
| `snapshot.ts:96` `.gitkeep` not exempt | `stray_file_is_problem_1` 1 | 1 |
| `snapshot.ts:76` folder check off | `record_in_the_wrong_folder_is_problem_1` 1 | 1 |
| `snapshot.ts:51` listed attachments ignored | `attachments_listed_not_parsed` 1 | 1 |
| `snapshot.ts:55` found attachments not added | `attachments_listed_not_parsed` 1 | 1 |

Every carried assertion asserts what the Python one does: `==` as `toEqual` or `toBe`, `isinstance(…, Problem)` as an unguarded `kind` check before any cast, `pytest.raises(ValueError)` as `toThrow(ValueError)`, `match="message 1 text"` as both the class and `/message 1 text/u`, and every parametrised case present, the one-parameter lists wrapped (`thread-files.test.ts:91`, `:95`, `:140`, `:155`; `fileformat-links.test.ts:16`, `:24`).

### C-1 · Minor · the report's evidence is again whole-function throws, and it omits five tests

Handle: `task-6-report.md`, "Test-first evidence"; Task 5b's C-1, parked for `drafts.ts` and `fileformat.ts` only, so this task's brief did not carry it.
The carried-test evidence repeats the top-of-function `throw`, and the per-test list leaves out `malformed_id_is_problem_1`, `unreadable_header_values_are_problem_1`, `duplicate_id_is_problem_2_with_both_paths`, `stray_file_is_problem_1`, and `record_in_the_wrong_folder_is_problem_1`, though all five are in the files and pass.
Scenario: a later builder copies a carried test with an assertion dropped, the top-of-function throw still fails it, and the report reads as evidence that it detects its behaviour.
Fix: the table above replaces the report's evidence for this task; the coordinator adds to the Global Constraints of the briefs still to write that the mutation for a carried test changes the behaviour its title names, not the function's entry.

### C-2 · Minor · no test holds `UNESCAPE` to line breaks at `\n`

Handle: `ts/src/core/threads.ts:21`; `ts/tests/core/thread-text.test.ts:5-11`; brief, "`_ESCAPE` and `_UNESCAPE` … are `re.MULTILINE` patterns, so they follow the Global Constraints' rule".
`UNESCAPE` is right today, but with the `m` flag it survives every test in `tests/core` (row above), since `escape_breaks_lines_at_newline_only` writes no backslash for it to strip.
Run: with that mutation, `writeThread` refuses messages lodge 0.2 writes, `x` U+2028 `\## Message 1`, `y` CR `\## Message 2`, and `a` U+2029 `\\## Message 3`, each with `the thread would not read back unchanged: message 1 text`, where unmutated TypeScript and Python write all three identically.
Fix: a second case in `escape_breaks_lines_at_newline_only` (or a sibling test) with `x \\## Message 1\ny\r\\## Message 2` as text, asserting the written text holds it unchanged and reads back equal.

### C-3 · Minor · out of scope: YAML refusals at a different line from PyYAML's

Handle: `ts/src/core/yamlio.ts` (Task 4), reached through `loadHeader` at `ts/src/core/threads.ts:81` and in every record header.
Run: `load_header("a: b\n  c: d")` gives line 3 in Python and 2 in TypeScript, `"a: b\nc: d\n  e: f"` 4 against 3; in the parse run above, 41 of the 137 YAML-message differences also differ in line, by 1 to 5, all where PyYAML reports `mapping values are not allowed here` or `could not find expected ':'` at the token and the `yaml` package at the node's start.
d-p48gr1 lists the YAML differences it allows, and a line moved is not among them, while Review Focus 3 asks for each refusal with its line.
Scenario: a hand edit indents a header key, and `lodge check` points at the line above it.
Fix: route to the next round touching `yamlio.ts`: either take PyYAML's line where the `yaml` package's error names the offending token, or list the difference under d-p48gr1 with a test pinning the TypeScript line.

## Practice

### P-1 · Minor · two private copies of `byCodePoint`

Handle: `ts/src/core/threads.ts:162-170` (`compareIds`) and `ts/src/core/snapshot.ts:35-43` (`compare`), each line for line the exported `byCodePoint` of `ts/src/core/text.ts:94-102`, which the Global Constraints make the home of Python's string semantics.
Scenario: a later fix to code-point ordering (a lone surrogate, say) lands in `text.ts` and its test, and the thread order and the snapshot's path order keep the old rule unseen.
Fix: import `byCodePoint` from `./text.ts` in both modules and delete the copies.

### P-2 · Minor · `load` folds lodge 0.2's helpers into one loop

Handle: `ts/src/core/snapshot.ts:44-99` against `src/lodge/core/snapshot.py:13-16` and `:75-125`.
Python names the four path patterns and keeps an area, a record, and a thread through `_keep_area`, `_keep_record`, `_keep_thread`, and `_duplicate`; the port inlines the patterns and merges the three into one 55-line branch with five `continue`s, where the misplaced-record rule becomes `parsed.kind !== "thread" && path.startsWith("lodge/decisions/") !== (parsed.kind === "decision")` and the area pattern moves ahead of the thread pattern.
The behaviour is the same (the differential run above, and the patterns are disjoint), but a reader checking the port against Python has to re-derive each rule.
Scenario: Task 12's differential or a later fix flags a snapshot difference, and the reviewer must untangle the merged branch before the Python helper it corresponds to is even found.
Fix: name `THREAD_FILE`, `DECISION_FILE`, `AREA_FILE`, and `SPEC_FILE`, and port the three keepers and `duplicate` as module functions, in Python's order.

### P-3 · Minor · facts in Python's docstrings are dropped

Handle: `ts/src/core/snapshot.ts:12-19` and `:44`, `ts/tests/core/builders.ts:91`; Python `src/lodge/core/snapshot.py:1`, `:31`, `:50`, `tests/core/builders.py:91`.
Lost are what `rev` is (the revision the files were read at, `null` for a tree not read from git), that `load` turns a file that does not read or repeats an ID into a problem and keeps the first, and that `snapshotOf` holds its items as given without reading files, so that a test can build defects a store could not hold.
Scenario: a plan 2 caller, building `Tree` from the events store (d-smx3xf), cannot tell from the type what `rev` should carry.
Fix: one comment each, stating the fact, as Task 5a's P-2 and Task 5b's P-2 ask for their modules.

### P-4 · Minor · four test details differ from the Python without changing a case

Handle: `ts/tests/core/thread-files.test.ts:23` and `:44`; `ts/tests/core/snapshot.test.ts:32-37`, `:52`, and `:57`; `ts/tests/core/thread-files.test.ts:158-159`.
`String.prototype.replace` with a string pattern replaces the first occurrence where Python's `str.replace` replaces all; each of the ten patterns occurs once in the default thread, and `q-4kq1zm` once in `EXAMPLE` (counted in the scratch worktree), so no case changes, but the reader has to check that.
`.sort()` without a comparator orders `[path, check]` pairs by the UTF-16 units of `"path,check"`, against the Global Constraints' rule that strings sort by code point; harmless for these ASCII paths.
`stray_file_is_problem_1` gives the two `.gitkeep` files `"x"` where Python gives `""`.
`write_text_error_names_the_field` runs each refused write twice to assert the class and the pattern, as Task 5b's P-3 found.
Fix: `replaceAll`; sort by `byCodePoint` on the path, then the check; `""` for the `.gitkeep` files; capture the error once and assert `toBeInstanceOf(ValueError)` and its message.

## Design

The plan's interfaces hold: `#core` exports exactly the fourteen names the brief lists for Task 6, `Tree` has the brief's shape with `tree` filling `attachments`, `Snapshot` has no default-filling function and a required `threads`, `threads.ts` imports `keyLine`, `loadHeader`, and `readStamp` as Step 3 says, and `ts/knip.json`'s `entry` drops `document.ts` and `fields.ts` and gains `tests/core/builders.ts`.
The Global Constraints' table names only `treeOf` (Task 11) as the later reader of `builders.ts`, but `snapshotOf` has no reader in Task 6 either, since its one Python caller here is the todo `thread_id_is_not_number_feedback`; its first reader is `test_doubts.py:93` (Task 7a), well before Task 11 takes the file out of `entry`, so nothing breaks.

### D-1 · Minor · `writeThread`'s read-back check lists its fields by hand

Handle: `ts/src/core/threads.ts:127-140` against `src/lodge/core/threads.py:128` (`if back != thread`, the whole dataclass), and `ts/src/core/fileformat.ts:119-124`, where the record writers compare through `READ_BACK_FIELDS`, which `read_back_fields_cover_model` (`ts/tests/core/read-back-fields.test.ts:7`) pins to the model's keys.
Run: `writeThread` on a thread carrying an extra `person` field and a message carrying an extra `approvedBy` returns text holding neither, where Python's equality would refuse a field the writer drops.
Scenario: plan 2's model changes give `Message` or `Thread` a field, the writer is not taught it, and every reply is stored without it and without an error.
Fix: add `thread` and `message` lists to `READ_BACK_FIELDS`, extend the pin test to a thread and a message, and compare through them, or compare with a deep equality over all keys but `kind`.

### D-2 · Minor · `snapshotOf`'s `paths` cannot be `null`

Handle: `ts/tests/core/builders.ts:93-97` against `tests/core/builders.py:88` (`paths: dict[str, str] | None = None`); the Global Constraints: "`X | None` becomes `X | null`, never `undefined`".
Python callers pass `None` explicitly: `snapshot_of(paths={t.id: "lodge/threads/old.md"} if stale_path else None)` (`tests/core/test_check_threads.py:125`) and likewise at `:144`.
Scenario: Task 8c ports those two lines as `{ paths: stalePath ? new Map(…) : null }`, which `tsc` refuses, and the builder either reshapes the carried call or edits `builders.ts` in a task that does not list it.
Run: `snapshotOf([], { paths: stale ? new Map() : null })` under the project's `tsconfig.json` gives TS2322, `Type 'null' is not assignable to type 'ReadonlyMap<string, string> | undefined'`.
Fix: `paths?: ReadonlyMap<string, string> | null`; `options.paths ?? []` already reads `null` as empty.

The specification's thread rules hold in the port: `appended` keeps every earlier message and adds one (s-yj4r17, "Messages are appended and never edited"), and a closing message may be empty (s-4wna3s).

## Files read

Read: `CLAUDE.md`; `task-6-brief.md`, `task-6-report.md`, the Review Focus and the parity rows and Tasks 6, 9a, and 10 of `2026-11-02-lodge-server-core.md`, C-1 and P-2 of `task-5b-review.md`, the YAML findings of `task-4-review.md` and `task-4-fix-1-report.md`, and the ledger's tail; `lodge spec` (thread rules), d-p48gr1, d-fbhdvf, and d-g1hrmn through `lodge show`; the whole diff of `ts/` (`threads.ts`, `snapshot.ts`, `index.ts`, `builders.ts`, the four test files, `knip.json`, `parity.json`); Python `src/lodge/core/threads.py`, `snapshot.py`, the `Thread`, `Message`, `Area`, and `Problem` classes of `model.py`, `read_stamp` and `FormatError` of `fields.py`, `key_line` of `document.py`, `quoted` of `yamlio.py`, and `tests/core/builders.py`, `test_thread_files.py`, `test_snapshot.py`, and `test_fileformat_links.py`; TypeScript `FormatError`, `readStamp`, and `readRank` of `fields.ts`, `keyLine` of `document.ts`, `instant` and `orderInstant` of `stamps.ts`, `byCodePoint` of `text.ts`, the default-filling functions of `model.ts`, `READ_BACK_FIELDS`, `differing` of `fileformat.ts`, `read-back-fields.test.ts`, and the readers of `parity-names.ts` (run, not read whole).
Not read: the rest of `fileformat.ts`, `headers.ts`, `drafts.ts`, and `yamlio.ts` beyond the lines named, `parity.test.ts`, the structure tests, `codex-final` transcripts, and the design documents.
