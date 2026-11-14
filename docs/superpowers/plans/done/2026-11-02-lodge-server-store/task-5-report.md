# Task 5 report

Implemented the carried thread tests without changing production code.
All fixtures use the synthetic storage project.

## Files changed

- `ts/tests/app/thread-ops.test.ts`: all 15 Python test names from `ask_writes_a_thread_file` through `close_with_text`, including every parameter case.
- `ts/tests/app/thread-ops-publish.test.ts`: all 12 remaining Python test names, covering publication retries, commits, reads, lists, waiting, and written paths.
- `ts/tests/app/thread-fix-paths.test.ts`: the shared-snapshot test and the two required command todos.
- `ts/tests/parity.json`: thread operations marked ported with both files and task 5; thread fix paths remains planned and moves to plan 3.
- This report records validation and mutation evidence.

## Test-first evidence

These tests carry Task 4 implementation, so the required red phase uses targeted mutations rather than missing implementation.
Each mutation was applied alone, its named test or parameter group was run, and the original source was restored in a finally block.
All 28 named tests or groups failed against their mutations.
No mutation remains in the working tree.
The mutations alter behaviour or diagnostics at their actual branch, never throw at a function entry.
The table names the mutation each test failed against, as permitted by the brief.

| Test or named parameter group | Targeted mutation | Observed result |
|---|---|---|
| ask_writes_a_thread_file | threads.ts: messages: [msg] → messages: [{ ...msg, by: "wrong" }] | FAIL, exit 1 |
| ask_resolves_a_code | threads.ts: question asked → question changed | FAIL, exit 1 |
| ask_on_an_unknown_ref_is_not_found | state.ts: `record named ${ref}` → `missing record ${ref}` | FAIL, exit 1 |
| author_message_needs_where | threads.ts: a message by author needs where → missing place | FAIL, exit 1 |
| author_when_defaults_to_the_minute | threads.ts: when ?? minuteOf(now) → when ?? stampOf(now) | FAIL, exit 1 |
| agent_message_may_not_carry_where | threads.ts: where and when are for messages by author → invalid metadata | FAIL, exit 1 |
| role_like_author_refused | threads.ts: write author exactly, or use your own role → invalid role | FAIL, exit 1 |
| empty_text_refused | threads.ts: the message is empty → empty message | FAIL, exit 1 |
| text_loses_cr_and_outer_whitespace_only | threads.ts: text = cleanText(text); → text = cleanText(text).replace("A  B", "A B"); | FAIL, exit 1 |
| unstorable_where_refused | threads.ts: throw new LodgeError(error.message); → throw new LodgeError("invalid metadata"); | FAIL, exit 1 |
| reply_appends | threads.ts: `${by} reply` → `${by} changed` | FAIL, exit 1 |
| reply_to_closed_thread_refused | threads.ts: `${thread.id} is closed` → `${thread.id} unavailable` | FAIL, exit 1 |
| close_appends_closed_by_the_closer | threads.ts: `closed by ${by}` → `closed differently by ${by}` | FAIL, exit 1 |
| close_without_text_passes_the_check | lodge.ts: close: true → close: false | FAIL, exit 1 |
| close_with_text | lodge.ts: text ?? "" → text === null ? "" : "Changed" | FAIL, exit 1 |
| rejected_publish_starts_again | threads.ts: if (outcome === PublishOutcome.REJECTED) continue; → if (outcome === PublishOutcome.REJECTED) break; | FAIL, exit 1 |
| commit_after_staged_when_asked | threads.ts: commit && outcome === PublishOutcome.STAGED → false && commit && outcome === PublishOutcome.STAGED | FAIL, exit 1 |
| no_commit_unless_asked | threads.ts: commit && outcome === PublishOutcome.STAGED → outcome === PublishOutcome.STAGED | FAIL, exit 1 |
| no_commit_when_published | threads.ts: commit && outcome === PublishOutcome.STAGED → commit | FAIL, exit 1 |
| threads_lists_open_newest_last | threads.ts: t.state === ThreadState.OPEN → t.state === ThreadState.CLOSED | FAIL, exit 1 |
| thread_shows_one_thread | threads.ts: ref.toLowerCase() → ref | FAIL, exit 1 |
| threads_waiting_groups | threads.ts: by === "author" → by !== "author" | FAIL, exit 1 |
| show_carries_the_records_threads | reads.ts: (t) => t.about === id → (t) => t.about !== id | FAIL, exit 1 |
| added_paths_lists_the_files_written | writes.ts: paths: [...files.keys(), ...placed.keys()] → paths: [] | FAIL, exit 1 |
| search_and_timeline_leave_threads_out | reads.ts: items: views(state, ids) → items: views(state, []) | FAIL, exit 1 |
| thread_about_a_missing_record_reads | threads.ts: : null, → : undefined, | FAIL, exit 1 |
| three_rejections_are_a_conflict | threads.ts: i < 3 → i < 2 | FAIL, exit 1 |
| waiting_reads_one_snapshot | reads.ts: waitingIn(state) → waitingIn(await readChecked(w)) | FAIL, exit 1 |

## Commands and outcomes

- `uv run --frozen --quiet lodge waiting`: both queues ended with `nothing`.
- Repository reads used `cat`, `rg`, `sed`, and `head` to inspect the brief, instructions, source tests, application code, fixtures, parity entries, and gate script.
- `python /tmp/port5.py`: wrote the tests; exited 0.
- `cd ts && bun test tests/app/thread-*.test.ts`: `34 pass, 2 todo, 0 fail`.
- `python /tmp/mutate5.py`: prepared mutation cases and printed the application modules; exited 0.
- `python /tmp/runmut5.py`: final run printed exit 1 for each of the 28 named tests or groups.
  An initial run could not locate the unknown-reference diagnostic; its target was corrected to the actual interpolated expression and all mutations were rerun.
- `bunx biome check --write` and `bunx biome check --write --unsafe` on the three new test files: initial runs found formatting, unused imports, and non-null assertions.
  A mechanical helper conversion briefly introduced parse errors, which were corrected.
  Explicit fixture guards now avoid non-null assertions.
  Final formatter output: `Checked 3 files ... No fixes applied.`
- `cd ts && bunx tsc --noEmit -p .`: initial diagnostics identified an unused copied helper, the required tree revision, a malformed spread, and a nullable assertion type; all were corrected.
  Final run exited 0 without output.
- Explicit three-file `bun test` after those fixes: `34 pass, 2 todo, 0 fail`, 95 assertions.
- `sh scripts/check-ts.sh`: passed Biome, TypeScript, dependency-cruiser, knip, and the complete test suite.
  Last lines: `1153 pass`, `2 todo`, `0 fail`, `2843 expect() calls`, `Ran 1155 tests across 84 files.`
- `git diff -- ts/src/app`: empty, confirming restored application source.
- `wc -l ts/tests/app/thread-*.test.ts`: 24, 128, and 153 lines, all below 300.
- After updating parity and this report, `sh scripts/check-ts.sh` is run again as the final validation command before committing.
- Commit uses explicit task paths, the requested Svenja Kernig identity, and the Codex co-author trailer, then pushes `origin server-store-a`.

## Deferred tests and concerns

No assertion from the carried application tests is impossible in TypeScript.
Asynchronous calls are awaited, Python mappings and tuples become maps and arrays, and the start timestamp assertion retains the exact offset.
The two command tests, `orphaned_thread_outputs` and `run_thread_outcomes`, remain todos because their command consumers belong to plan 3, as d-rp74dr requires.
They are deferrals, not TypeScript limitations.

The opening brief explicitly authorises committing and pushing with a Codex trailer, overriding the repeated historical builder restriction and CLAUDE trailer.
The coordinator's whole-language gate, merge, and ledger update remain outside this task.
An existing untracked task log was left untouched.
There are no implementation concerns.
