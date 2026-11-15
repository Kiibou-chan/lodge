# Task 8c report

Implemented the remaining comparison, link, and thread check tests, and restored the five deferred apply check assertions.
No production correction was needed: every carried assertion passes against the existing implementation.

## Changes per file

- `ts/tests/core/check-compare.test.ts`: added all 17 Python test names, including all three edited-field cases, with exact diagnostic and verdict assertions.
- `ts/tests/core/check-links.test.ts`: added all 13 Python test names, including both accounting cases and both text-field cases, preserving cycle paths, cycle membership, diagnostic text, and check numbers.
- `ts/tests/core/check-threads.test.ts`: added the 15 missing Python test names, including both stale-path cases, and retained Task 9a's two read-visibility cases.
- `ts/tests/core/apply.test.ts`: restored `checkChange(...).ok` for `new_decision_and_entry_and_area`, `retire_removes_from_order`, and `replacing_retirement_restores_order`, loading the union of original and emitted files exactly as Python does.
- `ts/tests/core/apply-edits.test.ts`: restored exactly `[5]` for the reasoning edit and a refused check result for the statement edit, again loading the merged tree.
- `ts/knip.json`: removed only `tests/core/checks.ts` from `entry`, since `REMEDY_CHECK_4` now has its reader.
- `ts/tests/parity.json`: changed only the comparison, link, and thread rows from `planned` to `ported`.
- `docs/superpowers/plans/2026-11-02-lodge-server-core/task-8c-report.md`: this report.

All changed test modules are below 300 lines.
No front-door export, production module, Python file, dependency, or reviewer report has a lasting change.
No staging, commit, push, installation, or network request was performed.

## Test-first mutation evidence

The tests were written before changing any implementation.
Since the implementation already exists, each carried test was run against a targeted mutation, restored in a `finally` block before the next mutation.
No mutation throws at a function entry or replaces an entire check function.
All 51 test names, covering 57 cases, failed against their final named mutations with exit 1.
All parameter cases failed individually, including the three edited fields, the two link accounting cases, the two unaccounted text fields, the two missing-thread paths, and the two read-visibility paths.
The ten other existing apply cases also passed in the restored focused run.

The command template was run from `ts/` for each row:

```sh
bun test ./tests/core/FILE.test.ts -t '^NAME(?: |$)'
```

The following rows give every test, the mutated source and expression, and the observed failure count.
These expressions refer to the original source before restoration.
Multiline expressions are flattened for readability.

| Test file and Python test name without `test_` | Targeted mutation in `ts/src/core/` | Failure evidence |
| --- | --- | --- |
| `check-compare.test.ts`: `check_4_new_entry_without_a_decision` | `check-entries.ts`: `if (before === undefined) wanted.push` → `if (before === undefined && entry.id !== "s-bbbbbb") wanted.push`. Skip create accounting for the new entry. | `1 fail`, exit 1 |
| `check-compare.test.ts`: `check_4_new_entry_listed_with_the_wrong_action` | `check-entries.ts`: `if (before === undefined) wanted.push` → `if (before === undefined && entry.id !== "s-bbbbbb") wanted.push`. Skip create accounting for the new entry. | `1 fail`, exit 1 |
| `check-compare.test.ts`: `check_4_published_decision_does_not_count` | `check-state.ts`: `return decisions(after).filter((d) => !published.decisions.has(d.id));` → `return decisions(after);`. Count published decisions as new accounting decisions. | `1 fail`, exit 1 |
| `check-compare.test.ts`: `check_4_edited_entry_without_a_decision` | `check-entries.ts`: `else if (!equal(before, entry)) wanted.push` → `else if (equal(before, entry)) wanted.push`. Invert edit detection, missing the changed fields. | `3 fail`, exit 1 |
| `check-compare.test.ts`: `check_4_imported_entry_edit_needs_a_decision` | `check-entries.ts`: `else if (!equal(before, entry)) wanted.push` → `else if (equal(before, entry)) wanted.push`. Invert edit detection, missing the changed fields. | `1 fail`, exit 1 |
| `check-compare.test.ts`: `check_4_imported_from_added_to_a_live_entry_is_an_edit` | `check-entries.ts`: `else if (!equal(before, entry)) wanted.push` → `else if (equal(before, entry)) wanted.push`. Invert edit detection, missing the changed fields. | `1 fail`, exit 1 |
| `check-compare.test.ts`: `check_4_laundering_over_two_changes_fails_at_each_step` | `check-entries.ts`: `else if (!equal(before, entry)) wanted.push` → `else if (equal(before, entry)) wanted.push`. Invert edit detection, missing the changed fields. | `1 fail`, exit 1 |
| `check-compare.test.ts`: `check_4_imported_from_removed_is_an_edit` | `check-entries.ts`: `else if (!equal(before, entry)) wanted.push` → `else if (equal(before, entry)) wanted.push`. Invert edit detection, missing the changed fields. | `1 fail`, exit 1 |
| `check-compare.test.ts`: `check_4_entry_moved_to_another_area_is_an_edit` | `check-entries.ts`: `else if (!equal(before, entry)) wanted.push` → `else if (equal(before, entry)) wanted.push`. Invert edit detection, missing the changed fields. | `1 fail`, exit 1 |
| `check-compare.test.ts`: `check_4_edited_entry_with_a_decision_passes` | `check-entries.ts`: `!listed.has(`${id}:${action}`)` → `!(action !== Action.EDIT && listed.has(`${id}:${action}`))`. Ignore edit decisions when accounting for edits. | `1 fail`, exit 1 |
| `check-compare.test.ts`: `check_4_imported_entry_edit_through_an_import_passes` | `check-entries.ts`: `!listed.has(`${id}:${action}`)` → `!(action !== Action.EDIT && listed.has(`${id}:${action}`))`. Ignore edit decisions when accounting for edits. | `1 fail`, exit 1 |
| `check-compare.test.ts`: `check_4_retired_entry_without_a_retiring_decision` | `check-entries.ts`: `if (now.get(id) === "retired" && was.get(id) !== "retired")` → `if (now.get(id) === "current" && was.get(id) !== "retired")`. Look for retirement accounting on current entries instead of retired entries. | `1 fail`, exit 1 |
| `check-compare.test.ts`: `check_4_retired_entry_with_a_decision_passes` | `check-entries.ts`: `!listed.has(`${id}:${action}`)` → `!(action !== Action.RETIRE && listed.has(`${id}:${action}`))`. Ignore retire decisions when accounting for retirement. | `1 fail`, exit 1 |
| `check-compare.test.ts`: `check_4_new_imported_entry_needs_no_decision` | `check-entries.ts`: `before === undefined && entry.importedFrom !== null` → `before === undefined && entry.importedFrom === null`. Invert imported-entry exemption. | `1 fail`, exit 1 |
| `check-compare.test.ts`: `check_4_create_for_an_entry_that_exists` | `check-entries.ts`: `change.action === Action.CREATE && published.entries.has(change.entry)` → `change.action === Action.CREATE && !published.entries.has(change.entry)`. Invert existing-entry detection for create. | `1 fail`, exit 1 |
| `check-compare.test.ts`: `check_4_import_from_an_unlisted_file` | `check-entries.ts`: `!settings.importSources.includes(source.file)` → `settings.importSources.includes(source.file)`. Invert import source membership. | `1 fail`, exit 1 |
| `check-compare.test.ts`: `check_4_published_import_from_an_unlisted_file_is_left_alone` | `check-entries.ts`: `.filter((id) => !published.entries.has(id))` → `.filter((id) => published.entries.has(id))`. Validate old imported entries instead of only new ones. | `1 fail`, exit 1 |
| `check-links.test.ts`: `link_changing_rests_on_only_passes` | `check-entries.ts`: `linksOnly && action === Action.EDIT && listed.has(`${id}:${Action.LINK}`)` → `linksOnly && action === Action.CREATE && listed.has(`${id}:${Action.LINK}`)`. Allow link accounting for creates rather than edits. | `1 fail`, exit 1 |
| `check-links.test.ts`: `rests_on_change_without_decision_fails_check_4` | `check-entries.ts`: `? "edit or link" : action` → `? "edit" : action`. Omit link from the rests_on-only edit remedy. | `1 fail`, exit 1 |
| `check-links.test.ts`: `edit_may_change_rests_on` | `check-entries.ts`: `!listed.has(`${id}:${action}`)` → `!(action !== Action.EDIT && listed.has(`${id}:${action}`))`. Ignore edit accounting for rests_on edits. | `1 fail`, exit 1 |
| `check-links.test.ts`: `link_changing_the_statement_fails_check_4` | `check-entries.ts`: `else if (!onlyRestsOnDiffers(before, entry))` → `else if (onlyRestsOnDiffers(before, entry))`. Invert detection of link changes that modify text. | `1 fail`, exit 1 |
| `check-links.test.ts`: `link_without_another_decision_accounting_for_text_fails` | `check-entries.ts`: `else if (!onlyRestsOnDiffers(before, entry))` → `else if (onlyRestsOnDiffers(before, entry))`. Invert detection of link changes that modify text. | `2 fail`, exit 1 |
| `check-links.test.ts`: `link_for_a_new_entry_fails_check_4` | `check-entries.ts`: `if (before === undefined) reason =` → `if (before !== undefined) reason =`. Invert new-entry detection for link diagnostics. | `1 fail`, exit 1 |
| `check-links.test.ts`: `unknown_rests_on_fails_check_2` | `check-state.ts`: `else if (!s.entries.has(target))` → `else if (s.entries.has(target))`. Invert rests_on target existence detection. | `1 fail`, exit 1 |
| `check-links.test.ts`: `rests_on_itself_fails_check_2` | `check-state.ts`: `if (target === id) yield` → `if (target !== id) yield`. Invert self-link detection. | `1 fail`, exit 1 |
| `check-links.test.ts`: `two_entry_cycle_fails_check_8_on_both` | `check-cycles.ts`: `if (targets.has(id) && others.length)` → `if (!targets.has(id) && others.length)`. Invert cycle reachability condition. | `1 fail`, exit 1 |
| `check-links.test.ts`: `three_entry_cycle_names_the_other_two` | `check-cycles.ts`: `if (targets.has(id) && others.length)` → `if (!targets.has(id) && others.length)`. Invert cycle reachability condition. | `1 fail`, exit 1 |
| `check-links.test.ts`: `new_rest_on_retired_entry_fails_check_6` | `check-change.ts`: `standing.get(target) === "retired"` → `standing.get(target) === "current"`. Check new rests_on links against current rather than retired targets. | `1 fail`, exit 1 |
| `check-links.test.ts`: `kept_rest_on_retired_entry_passes_check_6` | `check-change.ts`: `!previous.includes(target) && standing.get(target)` → `previous.includes(target) && standing.get(target)`. Reject kept links rather than new links to retired entries. | `1 fail`, exit 1 |
| `check-links.test.ts`: `link_with_another_decision_accounting_for_text_passes` | `check-entries.ts`: `other.id !== d.id &&` → `other.id === d.id &&`. Count the link decision itself rather than the separate accounting decision. | `2 fail`, exit 1 |
| `check-threads.test.ts`: `open_thread_passes_every_check` | `check-immutable.ts`: `if (!equal(now.messages.slice(0, old.messages.length), old.messages))` → `if (equal(now.messages.slice(0, old.messages.length), old.messages))`. Invert published-message equality so unchanged threads fail. | `1 fail`, exit 1 |
| `check-threads.test.ts`: `unresolved_about_fails_check_2` | `check-state.ts`: `if (!s.decisions.has(t.about) && !s.entries.has(t.about))` → `if (s.decisions.has(t.about) && s.entries.has(t.about))`. Invert unresolved about detection. | `1 fail`, exit 1 |
| `check-threads.test.ts`: `duplicate_thread_id_fails_check_2` | `snapshot.ts`: `if (kept !== undefined) {` → `if (kept === undefined && paths.has(parsed.id)) {`. Fail to detect an already registered duplicate ID. | `1 fail`, exit 1 |
| `check-threads.test.ts`: `file_name_must_start_with_the_id` | `check-state.ts`: `if (name !== `${r.id}.md` && !name.startsWith(`${r.id}-`))` → `if (name === `${r.id}.md` && !name.startsWith(`${r.id}-`))`. Require the exact valid filename before reporting a bad name. | `1 fail`, exit 1 |
| `check-threads.test.ts`: `appending_a_message_passes` | `check-immutable.ts`: `now.messages.slice(0, old.messages.length)` → `now.messages.slice(0, old.messages.length + 1)`. Include the appended message when comparing the immutable prefix. | `1 fail`, exit 1 |
| `check-threads.test.ts`: `closing_passes` | `check-immutable.ts`: `now.messages.length <= old.messages.length` → `now.messages.length >= old.messages.length`. Reject a close with an appended message. | `1 fail`, exit 1 |
| `check-threads.test.ts`: `editing_a_published_message_fails_check_5` | `check-immutable.ts`: `if (!equal(now.messages.slice(0, old.messages.length), old.messages))` → `if (equal(now.messages.slice(0, old.messages.length), old.messages))`. Invert immutable-message-prefix comparison. | `1 fail`, exit 1 |
| `check-threads.test.ts`: `removing_a_message_fails_check_5` | `check-immutable.ts`: `if (!equal(now.messages.slice(0, old.messages.length), old.messages))` → `if (equal(now.messages.slice(0, old.messages.length), old.messages))`. Invert immutable-message-prefix comparison. | `1 fail`, exit 1 |
| `check-threads.test.ts`: `changing_about_fails_check_5` | `check-immutable.ts`: `if (old[name] !== now[name])` → `if (old[name] === now[name])`. Invert immutable thread header comparison, missing about changes. | `1 fail`, exit 1 |
| `check-threads.test.ts`: `changing_raises_fails_check_5` | `check-immutable.ts`: `if (old[name] !== now[name])` → `if (old[name] === now[name])`. Invert immutable thread header comparison, missing raises changes. | `1 fail`, exit 1 |
| `check-threads.test.ts`: `changing_opened_fails_check_5` | `check-immutable.ts`: `if (old[name] !== now[name])` → `if (old[name] === now[name])`. Invert immutable thread header comparison, missing opened changes. | `1 fail`, exit 1 |
| `check-threads.test.ts`: `reopening_fails_check_5` | `check-immutable.ts`: `if (now.state === ThreadState.OPEN)` → `if (now.state === ThreadState.CLOSED)`. Detect closed rather than reopened threads. | `1 fail`, exit 1 |
| `check-threads.test.ts`: `message_after_closing_fails_check_5` | `check-immutable.ts`: `if (now.messages.length > old.messages.length)` → `if (now.messages.length < old.messages.length)`. Detect removed rather than added messages after closing. | `1 fail`, exit 1 |
| `check-threads.test.ts`: `closing_without_a_message_fails_check_5` | `check-immutable.ts`: `now.messages.length <= old.messages.length` → `now.messages.length < old.messages.length`. Allow closing with an unchanged message count. | `1 fail`, exit 1 |
| `check-threads.test.ts`: `missing_published_thread_fails_check_2` | `check-change.ts`: `...published.threads.keys(),` → `...after.threads.keys(),`. Enumerate after threads instead of published threads when finding missing IDs. | `2 fail`, exit 1 |
| `apply.test.ts`: `new_decision_and_entry_and_area` | `check-change.ts`: `instant(d.date) > instant(now)` → `instant(d.date) >= instant(now)`. Treat a date equal to the add time as a future date. | `1 fail`, exit 1 |
| `apply.test.ts`: `retire_removes_from_order` | `check-change.ts`: `instant(d.date) > instant(now)` → `instant(d.date) >= instant(now)`. Treat a date equal to the add time as a future date. | `1 fail`, exit 1 |
| `apply.test.ts`: `replacing_retirement_restores_order` | `check-change.ts`: `instant(d.date) > instant(now)` → `instant(d.date) >= instant(now)`. Treat a date equal to the add time as a future date. | `1 fail`, exit 1 |
| `apply-edits.test.ts`: `decision_reasoning_edit_keeps_date_and_fails_check_5` | `check-immutable.ts`: `["reasoning", "reasoning"],` → `(remove this field)`. Omit reasoning from immutable decision fields. | `1 fail`, exit 1 |
| `apply-edits.test.ts`: `decision_edit_changing_statement_is_judged_by_the_check` | `check-immutable.ts`: `["statement", "statement"],` → `(remove this field)`. Omit statement from immutable decision fields. | `1 fail`, exit 1 |
| `check-threads.test.ts`: `thread_problems_are_visible_in_reads` | `views.ts`: `[...s.paths].filter(([id]) => !s.threads.has(id))` → `[...s.paths].filter(([id]) => s.threads.has(id))`. Treat thread paths as recorded paths, hiding their problems from reads. | `2 fail`, exit 1 |

The initial date mutation changed `>` to `<`, and the three accepting apply tests survived it because their dates equal `NOW`.
That mutation supplied no failing evidence and was discarded.
The replacement mutation changes `>` to `>=`, incorrectly rejecting a date equal to the add time.
Each of those three tests then failed at its restored check assertion, after its existing apply assertions had passed.
The remaining two apply mutations remove only the specific immutable field being checked, so their failure is also at the restored assertion.

## Commands and results

Read-only inspection used `cat`, `rg`, `sed`, `wc -l`, `git status --short`, and `git diff` for the brief, `CLAUDE.md`, the named Python tests, relevant TypeScript modules, the Task 11 report, and gate configuration.
An exploratory read used guessed module filenames that do not exist; `rg --files` located the actual `check-entries.ts`, `check-change.ts`, and `check-immutable.ts` files.
An initial knip edit attempted a repository-relative path while already inside `ts/`, raised `FileNotFoundError`, and changed nothing; the corrected edit used the repository root.
The cloud runtime skill was read, but no `environment_status` tool is available in this session's tool catalogue.
No runtime or network operation was needed.

- `uv run --frozen --quiet lodge waiting`: exited 0; both agent and author waiting lists ended with `nothing`.
- Focused `bun test` on `check-compare`, `check-links`, `check-threads`, `apply`, and `apply-edits`: `67 pass`, `0 fail`, `89 expect() calls`, `Ran 67 tests across 5 files`.
- The temporary Python mutation harness ran the per-name command above, saved each output, restored each source immediately, and finished with `51 thread_problems_are_visible_in_reads 1`.
- Focused `bun test` after restoration: `67 pass`, `0 fail`, `89 expect() calls`, `Ran 67 tests across 5 files`.
- `bun --bun x biome check --write` over the five test files and knip configuration: `Checked 6 files`, `Fixed 5 files`.
- First `sh scripts/check-ts.sh`: TypeScript reported TS2769 for the optional first element of the expected verdict array and optional map lookups in the cycle expectation.
The expected verdict helper now returns a one-element tuple, and cycle expectations narrow the builder-populated path values to strings.
These are test typing corrections, with no behavioural change.
- `sh scripts/check-ts.sh` before flipping parity: exited 0; `774 pass`, `1 todo`, `0 fail`, `2020 expect() calls`, `Ran 775 tests across 46 files`.
Dependency-cruiser reported no dependency violations, and knip reported no unused export.
Knip emitted its existing unmatched `scripts/*.ts` and `scripts/**/*.ts` configuration hints, which do not fail the gate.

## TypeScript differences and concerns

No carried test or assertion is impossible in TypeScript, and none was weakened or omitted.
Immutable dataclass replacement becomes object spread; snapshots and trees use maps; times remain explicit offset-bearing strings; Python tuple and list comparisons use value equality.
The thread read-visibility test remains implemented, rather than TODO, because Task 9a is already merged, as the coordinator's brief states.
No task-specific TODO remains.
The one TODO in the full suite belongs to earlier work.
No correctness uncertainty remains from the carried tests.
The coordinator still owns the full Python and TypeScript gate outside the sandbox, and staging, committing, and pushing.

## Final gate

`sh scripts/check-ts.sh` was the final validation command, after all test, knip, and parity changes, and exited 0.
Its final lines were:

```text
774 pass
1 todo
0 fail
2026 expect() calls
Ran 775 tests across 46 files. [1.92s]
```

Biome checked 91 files without changes, TypeScript passed, dependency-cruiser found no violations across 99 modules and 316 dependencies, and knip found no unused export.
The parity tests now verify every Python name in all three newly ported rows.
Only this report's final results were filled in after that gate.
