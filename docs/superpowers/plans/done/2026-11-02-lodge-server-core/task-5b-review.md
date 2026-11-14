# Task 5b review

Commit 7c3ab8b against 03ecac3, `ts/` only.
Probes ran in a detached scratch worktree at 7c3ab8b, its `ts/node_modules` a link to the build worktree's; the worktree is removed.

## Summary

0 Blocking, 0 Important, 7 Minor.
The port agrees with lodge 0.2 on every draft probed, and every carried text test is killed by a targeted mutation of the behaviour it names, so the builder's broad mutations hid no weak test.

## Correctness

Review Focus 1: every Python test of both files is carried by name with every case, the two-parameter list of `draft_syntax_problems` as `test.each([[a, b], …])`, the one-parameter lists wrapped (`fileformat-text.test.ts:58`, `:75`), each `pytest.raises` as `toThrow` with the class and the pattern, and each `in` on a message as `toContain`.
The `if (x.kind === "problem") expect(…)` guards are each preceded by an unguarded `expect(x.kind)`, so no assertion is skipped silently.

Review Focus 2, run: 58 drafts through `parse_draft` and `record_from_draft` in Python and through `parseDraft` and `recordFromDraft` in TypeScript, compared as normalised JSON (the draft's kind, header, body, and header text, then the record or problem).
The inputs hold U+001C (escaped and literal), U+0085, U+FEFF before, after, and inside `## Reasoning`, an astral character, a lone surrogate escape, a surrogate pair escape, CRLF throughout, a lone CR and U+2028 before a heading, a BOM before the fence, `--- ` and `---\r` fences, duplicate keys, a non-mapping header, `kind` quoted, capitalised, and as a list, a numeric key, a dated draft with and without `imported_from`, ids that match, differ, and differ in case, and spec and area drafts with the area or name given, missing, moved, malformed, and non-ASCII.
57 agree exactly; the one difference is a literal U+0085 in a quoted title, which PyYAML folds to a space and TypeScript keeps, both ending in `title must be a non-empty string` at line 3, a case ruling d-p48gr1 lists.
A second run of 24 non-string `id` values (numbers, floats, dates, booleans, nulls, infinities, nested lists and maps) gives the same message in both, since the failsafe schema reads every scalar as text.

### C-1 · Minor · the report's mutations show only that each test calls the function

Handle: `task-5b-report.md`, the table under "For each carried test below"; d-mfayy5.
Each named mutation throws at the top of `parseRecord`, `writeRecord`, `slug`, or `newRecordPath`, which fails any test that calls the function, including one whose assertions were all deleted, so the table is no evidence that a test detects what its name says.
Run: the targeted mutations below, each applied alone in the scratch worktree, run against the named test and then all of `tests/core` (243 tests), and reverted.

| Mutation | Named test | `tests/core` failing |
|---|---|---|
| `yamlio.ts:100` depth limit 100 to 100000 | `deep_nesting_is_problem_1` fails | 4, the nesting tests |
| `document.ts:45` `rstrip` to `strip` in `trimBlock` | `indentation_of_the_first_line_is_kept` fails | 3 |
| `document.ts:44` `!strip(lines[0]!)` to `!lines[0]!` | `blank_lines_around_a_block_are_dropped` fails | 1 |
| `fields.ts:29` `!strip(value)` to `!value` | `blank_required_string_is_problem_1` fails (2 cases) | 3 |
| `fields.ts:74` multiline allowance dropped | `quote_text_keeps_line_breaks_and_tabs` fails | 1 |
| `fileformat.ts:170` writer drops `LINE_BREAKS_AND_TABS` for `quote.text` | `quote_text_keeps_line_breaks_and_tabs` fails | 1 |
| `fileformat.ts:170` and `fields.ts:74` let `where` and `when` carry line breaks | `other_quote_parts_keep_the_control_character_ban` fails (2 cases) | not run |
| `yamlio.ts:20` U+2028 readable | `quote_text_still_refuses_other_control_characters` fails | 3 |
| `yamlio.ts:4` U+0001 added to `LINE_BREAKS_AND_TABS` | `quote_text_still_refuses_other_control_characters` fails | 1 |
| `yamlio.ts:15` `unreadableChar` iterates UTF-16 units | `json_dumps_default_escapes_read_back_as_emoji` fails | 3 |
| `yamlio.ts:22` surrogates readable | `lone_surrogate_escape_is_problem_1` fails | 1 |
| `fileformat.ts:103` `differing` returns `null` | `write_names_the_field_that_would_read_back_differently` fails | 1 |
| `fileformat.ts:66` seven slug words | `slug_is_capped_at_a_word_boundary` fails | 2 |
| `fileformat.ts:69` cut at 60 regardless of words | `slug_cut_never_splits_a_word_unless_one_word_is_too_long` fails | 2 |
| `fileformat.ts:68` `lastIndexOf("-", 61)` | `slug_cut_never_splits_a_word_unless_one_word_is_too_long` fails | 1 |
| `fileformat.ts:56` path from the uncapped words | `new_record_path_stays_short_for_long_titles` fails | 1 |

A writer-only change letting `quote.where` carry a line break leaves `other_quote_parts_keep_the_control_character_ban` passing, because the read-back check still refuses with a message naming `quote.where`; the ban is lost only when writer and reader both drop it, and then the test fails, so this is the Python test's design, not a weakness of the port.
Scenario if the report stands: the ledger records the d-mfayy5 step as done on evidence that would pass for an empty test, and a later reviewer relying on it misses a vacuous carried test.
Fix: replace the report's table with the one above (or the builder's own targeted mutations), and add to the next brief that a d-mfayy5 mutation changes the behaviour the test names, not the function's reachability.

### C-2 · Minor · `json_dumps_default_escapes_read_back_as_emoji` asserts the runtime and a tautology

Handle: `ts/tests/core/fileformat-text.test.ts:93-96`; Python `tests/core/test_fileformat_text.py:94`.
`expect(JSON.stringify(quote)).toBe(…)` tests Bun's `JSON.stringify`, not lodge, and `expect(escaped).toContain("\\ud83d")` checks a literal against itself and cannot fail.
Python's line checks that the input is what `json.dumps` gives an agent; the TypeScript literal is that input today (run: `json.dumps("Ship it \U0001f600")` is `"Ship it 😀"`), but nothing ties `escaped` to `quote`, so an edit of `quote` to another emoji leaves the test reading a stale escape.
Fix: build `escaped` with a three-line helper in the test that writes each UTF-16 unit above U+007F as `\uXXXX` (what `json.dumps` does with `ensure_ascii`), keep `expect(escaped).toContain("\\ud83d")` as the premise check, and drop the `JSON.stringify` assertion and its comment.

## Practice

### P-1 · Minor · two private `valueRepr` helpers with different rules

Handle: `ts/src/core/drafts.ts:93-102` and `ts/src/core/fileformat.ts:96-102`.
Both port Python's `!r` on a non-string value: the first writes arrays as lists and has `Map`, `True`, and `False`; the second writes arrays as tuples and, after Task 5a's fix C-2, the four dataclass reprs.
Scenario: Task 11 ports `apply.py`, which formats a header value with `!r` twice (`src/lodge/core/apply.py:147`, `area must be one name, not {area!r}`, and `:265`, `id {given!r} is not …`, both reachable with a list), copies whichever helper it finds first, and a list area prints as `('a', 'b')` where lodge 0.2 prints `['a', 'b']`.
The `true` and `false` branches of the drafts helper are unreachable through `parseDraft`, since the failsafe schema reads every scalar as a string (`ts/src/core/yamlio.ts:125`; run above: 24 non-string ids, none a boolean), and no probe reached the `null` branch.
Fix: one helper in a module of `core` that the front door does not re-export (so d-hshapm's export check is untouched), taking the sequence spelling as a parameter, used by both files; or, if kept apart, a one-line comment on each naming the other and why they differ.

### P-2 · Minor · facts in Python's docstrings are dropped

Handle: `ts/src/core/drafts.ts:27` and `:41`; Python `src/lodge/core/drafts.py:1`, `:36`, `:52-57`.
The rules of `record_from_draft` are not visible from its code: a new record is given a date and may carry its own only with `imported_from`; an existing record is given `date === null` and keeps its draft's date; a new entry or area names itself, an existing one is given `area`.
Scenario: a caller in plan 2 passes the current time for an existing decision, and the draft's own date is refused where lodge 0.2 keeps it.
Fix: a comment above `recordFromDraft` stating those three facts, and one above `parseDraft` that it checks only the syntax and the key names, as Task 5a's P-2 asks for its modules.

### P-3 · Minor · each refused write is run twice

Handle: `ts/tests/core/fileformat-text.test.ts:79-81`, `:86-88`, and `:116-118`.
Each case calls `writeRecord` once for `toThrow(ValueError)` and once for the pattern, the pattern Task 5a's review P-3 names.
Fix: use the `refused` helper that Task 5a's fix round adds, once it lands.

### P-4 · Minor · the key lists are mutable where Python has tuples

Handle: `ts/src/core/drafts.ts:15-19`; Python `src/lodge/core/drafts.py:20-24` (`dict[DraftKind, tuple[str, ...]]`); the Global Constraints' "a tuple becomes `readonly T[]`".
`KEYS` infers `{ decision: string[]; … }`, so a later `KEYS[kind].push(…)` in the module type-checks and widens every draft's allowed keys.
Fix: `const KEYS: { readonly [K in DraftKind]: readonly string[] } = { … }`.

## Design

The module boundary matches the brief: `drafts.ts` imports `splitDocument`, `problemFor`, `loadHeader`, `trimBlock`, and the three `*_KEYS`; `src/core/headers.ts` left `ts/knip.json`'s `entry` and `document.ts` and `fields.ts` stayed (`git show 7c3ab8b:ts/knip.json`); `#core` exports `Draft`, `parseDraft`, and `recordFromDraft`; `Draft` has no filler and a required `headerText`; both files are flipped to `ported`.
`Draft.kind` takes the values `decision`, `spec`, and `area` that the records use as their discriminant; no Python caller puts a `Draft` and a record in one union (`src/lodge/app/writes.py:168` and `src/lodge/core/apply.py` test `Draft` against `Problem` only), so this needs nothing now.

### D-1 · Minor · a TypeScript-only test sits among the carried ones unmarked

Handle: `ts/tests/core/drafts.test.ts:226-241` (`draft_non_string_id_is_reported`).
The parity test allows titles that Python lacks (`ts/tests/parity.test.ts:44-46` checks only that Python's names are present), so nothing tells a reader of the file which tests are carried.
Scenario: Task 12 or the final review counts the file's tests against `test_drafts.py`, finds 17 names for 16, and either looks for a Python test that does not exist or deletes a useful one.
Fix: a one-line comment above it, stating that it is TypeScript's own and pins Python's `repr` of a list and a mapping id.

## Files read

Read: `CLAUDE.md`; `task-5b-brief.md`, `task-5b-report.md`; the plan's Review Focus and the Global Constraints in the brief; `task-5a-review.md` (to keep findings apart) and `task-5a-fix-1.md`; decisions d-mfayy5, d-88p8h9, d-ca6wbw, and d-p48gr1 (with the U+0085 lines of `task-4-fix-1-report.md`); `lodge spec`, searched for drafts and must-nots; the whole diff (`ts/src/core/drafts.ts`, `index.ts`, `ts/knip.json`, `ts/tests/parity.json`, `ts/tests/core/drafts.test.ts`, `fileformat-text.test.ts`); `ts/src/core/document.ts`, `fileformat.ts`, `yamlio.ts`, and `fields.ts:1-75`; `src/lodge/core/drafts.py`, `document.py:31-50`, the `slug` lines of `fileformat.py`, `yamlio.py:82`; `tests/core/test_drafts.py`, `test_fileformat_text.py`; the draft callers in `src/lodge/app/writes.py` and `src/lodge/core/apply.py`; the assertions of `ts/tests/parity.test.ts`.

Not read: `task-5b-codex-final.txt`; `probes.md` and `probes/`; `ts/src/core/headers.ts`, `model.ts`, and `text.ts` beyond their behaviour in the runs; the rest of `fields.ts`; `ts/tests/core/samples.ts` beyond `document` and `replaced` as used; the gate (`sh scripts/check.sh`) was not rerun, the dispatch reporting it green.
