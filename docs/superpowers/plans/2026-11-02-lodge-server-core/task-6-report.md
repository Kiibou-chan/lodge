# Task 6 report

Implemented thread files, append operations, and snapshot loading on the current branch.
No commit or push was made, no package was installed, and no Python source or tests were edited.

## Changes by file

- `ts/src/core/threads.ts`: ports parsing, message metadata and line diagnostics, reversible heading escaping, writing with read-back validation, text cleaning, appending, paths, and ordering by instant and code point ID.
- `ts/src/core/snapshot.ts`: ports `Files`, `Tree`, its default-filling `tree` function, `Snapshot`, attachment paths, sorted loading, misplaced and stray file detection, duplicate problems, and retention of the first record.
- `ts/src/core/index.ts`: exports both new modules through `#core`.
- `ts/tests/core/builders.ts`: ports all externally read Python builders, including deterministic IDs, author quotes, files, snapshots, threads, and trees.
  `snapshotOf` takes an item array and an optional options object to represent Python positional items and keyword options.
- `ts/tests/core/thread-files.test.ts`: carries every Python thread file test name and parameter case, with the Task 10 test left as the required TODO.
- `ts/tests/core/snapshot.test.ts`: carries every Python snapshot test name, with the Task 9a test left as the required TODO.
- `ts/tests/core/fileformat-links.test.ts`: carries every Python fileformat link test and parameter case.
- `ts/tests/core/thread-text.test.ts`: adds the required newline-only escaping regression and an instant/code point ordering regression.
- `ts/knip.json`: removes document and fields from entry and adds builders for its future consumers.
- `ts/tests/parity.json`: marks builders and fileformat links as ported.
  Thread files and snapshot remain planned because their required future-task TODOs cannot pass the parity rule prohibiting TODOs in ported rows.

## Test-first evidence

All four new test modules were written before the implementation.
The first `cd ts && bun test tests/core` run ended with `252 pass`, `4 fail`, `4 errors`, and `Ran 256 tests across 18 files`.
Its module error was `SyntaxError: Export named 'writeThread' not found in module` at the core front door.
This missing export prevented collection of each new module, so it is the first failure for every active test listed below, including every parameter case.
The builders were consumed by those failing modules.

### `thread-files.test.ts`

- `thread_round_trips`.
- `empty_text_only_on_the_closing_message %p %p`.
- `written_shape_matches_the_example`.
- `text_line_like_a_heading_round_trips %p`.
- `yaml_and_markdown_specials_round_trip %p`.
- `author_message_needs_where`.
- `about_must_name_a_decision_or_entry`.
- `thread_needs_a_message`.
- `messages_numbered_in_order`.
- `body_text_before_first_message_refused`.
- `appended_refuses_a_closed_thread`.
- `newest_last_by_opened_then_id`.
- `load_reads_threads_and_their_paths`.
- `nested_file_under_threads_is_stray`.
- `appended_cleans_the_text_and_closes %p`.
- `write_text_error_names_the_field %p`.
- `message_without_metadata_names_the_message`.

### `snapshot.test.ts`

- `load_keeps_good_records_beside_problems`.
- `attachments_listed_not_parsed`.

### `fileformat-links.test.ts`

- `rests_on_round_trips`.
- `rank_round_trips`.
- `rank_reads_quoted_and_plain_alike %p`.
- `rank_must_be_a_whole_number %p`.
- `rests_on_holds_entry_ids_only`.
- `area_without_rank_writes_as_before`.

### `thread-text.test.ts`

- `escape_breaks_lines_at_newline_only`.

The carried fileformat tests were additionally run against a temporary mutation inserting `throw new Error("Task 6 carried-test mutation")` at the start of `parseRecord`, `parseArea`, `writeRecord`, and `writeArea`.
Every one of their 12 parameter-expanded cases failed: `0 pass`, `12 fail`, `Ran 12 tests across 1 file`.
The original file was restored immediately; it has no final diff.

`newest_last_uses_instants_and_code_point_ids` was added after the initial implementation and failed against its UTF-16 ID comparison: `1 pass`, `1 fail`, `Ran 2 tests across 1 file`.
After replacing that comparison with code point ordering, its run ended `2 pass`, `0 fail`.
The case also equates stamps with different offsets.

The required deferred titles are `thread_id_is_not_number_feedback` (Task 10) and `duplicate_id_marks_kept_record_failing` (Task 9a).
They are TODOs, not language incompatibilities.
No carried test is impossible in TypeScript, and no assertion was substituted for that reason.

## Commands and outcomes

- Read the brief, `CLAUDE.md`, the named Python implementations and tests, existing TypeScript interfaces, package manifest, parity checks, and gate script with `cat` and `rg`.
- `uv run --frozen --quiet lodge waiting`: `waiting for the author`, `nothing`; agents also had nothing waiting.
- `cd ts && bun test tests/core`, before implementation: `Ran 256 tests across 18 files`, with four module failures as above.
- `cd ts && bun test tests/core`, after implementation: `300 pass`, `2 todo`, `0 fail`, `Ran 302 tests across 18 files`.
- `cd ts && bun test tests/core/fileformat-links.test.ts`, with the carried-test mutation: `Ran 12 tests across 1 file`, all 12 failed.
- `cd ts && bun --bun x biome check --write .`: fixed formatting and imports, then identified template literal suggestions.
- `cd ts && bun --bun x biome check --write --unsafe tests/core/thread-files.test.ts`: applied those template literal fixes.
- `cd ts && bun --bun x tsc --noEmit -p .`: exit 0, no output.
- First `sh scripts/check-ts.sh`: exit 0; `477 pass`, `2 todo`, `0 fail`, `Ran 479 tests across 25 files`.
- `cd ts && bun test tests/core/thread-text.test.ts`: first `1 pass`, `1 fail`; after the comparator change, `2 pass`, `0 fail`, `Ran 2 tests across 1 file`.
- `cd ts && bun --bun x biome check --write src/core/threads.ts tests/core/thread-text.test.ts`: `Checked 2 files`, formatting fixed.
- Final `sh scripts/check-ts.sh`: exit 0; `478 pass`, `2 todo`, `0 fail`, `1483 expect() calls`, `Ran 480 tests across 25 files`.

## Concerns

No implementation uncertainty remains.
The gate emits existing knip configuration hints for script globs with no matches; these are informational and do not fail it.
The two deferred tests await the tasks explicitly named in the brief.
The coordinator still owns the whole Python and TypeScript gate outside the sandbox, staging, committing, and pushing.
