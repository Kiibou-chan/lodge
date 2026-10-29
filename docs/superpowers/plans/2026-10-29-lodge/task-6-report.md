# Task 6 report: search, references, level views, readable specification

Status: DONE_WITH_CONCERNS.

## Built

- `src/lodge/core/search.py`: `Filters`, `AmbiguousRef`, `resolve`, `search`, `related`.
- `src/lodge/core/views.py`: `Level1`, `Level3`, `failing_ids`, `unrecorded_problems`, `level1`, `level2`, `level3`, `format_level1`, `format_level3`.
- `src/lodge/core/render.py`: `render_spec`.
- All exported through `lodge.core`; tests in `tests/core/test_{search,views,render}.py` (all 17 brief tests plus a few extra: awaiting flag on a touched entry, empty query, limit, unknown link target, `format_level3`, render without an area file).

## Test-first

With the three modules and the `__init__` exports removed, the three new test files fail at collection (`ImportError: cannot import name 'AmbiguousRef' from 'lodge.core'`, and `lodge.core.render`/`views` missing).
After implementing, two of my own tests failed on wrong expectations (search order with the entry newest by its retiring decision; an author first change flagging the later agent change), both fixed in the tests.
`sh scripts/check.sh`: green, 566 passed.

## Calls made where the brief is silent

1. `Filters`: a record lacking the attribute fails the filter. `area` matches entries only, `scope` decisions only; `decided_by` works for both (an entry takes it from its newest changing decision, as level 1 does).
2. Empty query (no letters): returns every record the filters allow, newest first, so the CLI can list by filter alone. A query that is exactly an ID or code is matched case-insensitively and placed first, only when it passes the filters.
3. Words are `[^\W\d_]+` on the lower-cased text, literally "split on non-letters": digits are separators, so `ITEM-1` yields `item`.
4. Ties and the date of an entry: the date of its newest changing decision; an entry with none sorts last. Then by ID.
5. `related` returns decisions only (shared entry in `changes`, newest first; then hits scoring at least 2, by score then newest). The query for the second part is the decision's title and statement words.
6. `awaiting the author` is shown both on the flagged decision (`awaiting_author`) and on what it touched (`touched_by_flagged`), per the spec's Review flag, with the same text.
7. `retired by <id>` is the newest decision in `changed_by` with a retire change for that entry.
8. `format_level1` header: `<id>[ <code>] · status · who · date (day only) · scope-or-area · flags`, parts that are `None` omitted.
9. `level2` of an entry: for each decision of `changed_by`, newest first, the header line and the title (no statement), blocks separated by a blank line; `fails check` is not shown there (no `failing` argument).
10. `level3.links`: unknown target IDs get status `unknown`; `changes` carries no action (the tuple has no slot for it). `format_level3`: one line per present field (`quote:`, `numbers:`, `work item:`, `attachments:`, `imported from:`), then one `<relation>: <id> (<status>)` line per link.
11. `render_spec`: areas by name, including areas that only entries mention (title is the name); entries listed in the area's `order` first, any current entry not in the order after, by ID; output ends in one newline, `""` when nothing renders.

## Concerns

- `related`'s threshold of 2 uses unfiltered word overlap, so two decisions sharing any two common words ("the", "is") in their statements already qualify; the Related-decision feedback will be noisy on real text. A stop-word list or minimum word length would fix it, but changes the plan's ranking, so left for a ruling.
- Call 1 (area and scope filters exclude the other kind) is my reading of the spec's filter list; a viewer that wants decisions "in an area" would need `related`-style lookup via `changes`.

## Fix round 1

Test-first: the new and changed tests failed (21 failures) before the code; `sh scripts/check.sh` green after, 579 passed.

- B1: `Level1.quote` added; an entry takes it from its newest changing decision when that is the author's; `format_level1` prints `quote: "<text>" (<where>, <when>)` after the statement.
- I1: `render_spec(s, d, failing, area=None)`; every flag of an entry goes in its heading as `## <title> (<id> · <flags>)`.
- I2: `level2(s, d, record_id, failing)` passes `failing` to the heads; an entry whose newest changing decision fails carries `decision fails check` (last in the flag order).
- I3: `load` files the duplicate-ID problem against both paths; `test_duplicate_id_marks_kept_record_failing` goes through `load` and `check_state`; `test_duplicate_id_is_problem_2_with_both_paths` and `test_check_2_duplicate_id_from_load_is_reported` (now `[2, 2]`) changed to the two-path behaviour. The dropped file's path is still an unrecorded problem.
- I4: no change in this task.
- I5: a query with only whitespace lists by filters; any other query without searchable words returns only the exact ID or code match.
- I6: `its decision replaced by <ids>` and `its decision narrowed by <ids>` after `retired by`.
- Search words ruling: runs of letters or digits, function words dropped (list in `src/lodge/core/words.py`); `related` also drops pure-digit words.
- M1: `awaiting the author on <ids>` on touched records, bare on the flagged decision.
- M2: ties by larger ID (sort on `(date, id)`, reversed), for `search` and `related`.
- M3: level-3 relation `changes (create|edit|retire)`, one link per distinct change.
- M4: an entry without a changing decision prints `no decision` in the who slot.
- M5: `Filters.area` matches a decision when an entry it changes is in that area.
- Also: `test_flag_order_in_full` pins the full flag order; the new level 1 and 2 tests live in `tests/core/test_views_trust.py` (the 300-line limit).
