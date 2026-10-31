# Task 2 review: the link action, the checks on rests_on, check 8, and what reads derive

Commit f23dd1d, diff `a3b7ebd..f23dd1d`, reviewed in a scratch worktree of the commit (removed).
Counts: Blocking 0, Important 1, Minor 8.

## Verified

- `uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py`: 1111 passed.
- `ruff format --check`, `ruff check`, `mypy`, `vulture`: clean.
- All 26 named tests exist, with the brief's names and values.
- Line allowances hold: `derive.py` 227 to 240 (limit 15), `views.py` 220 to 235 (limit 30); no module nears 300.
- Mutation probes, each run in the scratch worktree and reverted:
  - Counting `link` in `touches` fails 5 tests (`test_link_is_not_a_change`, `test_link_raises_no_flag`, three in `test_views_links.py`).
  - Dropping `target != record.id` or `target not in record.rests_on` in feedback fails `test_own_id_no_feedback` and `test_listed_named_entry_no_feedback`.
  - Dropping the `linked` clause in check 4 fails `test_link_changing_rests_on_only_passes`.
  - Ignoring `previous` in check 6 fails `test_kept_rest_on_retired_entry_passes_check_6`.
  - Making "changed since" always true fails `test_edit_with_unchanged_text_clears_changed_since`.
  - Removing the retired branch, or `who`, fails the retired-mark and cycle-in-one-add tests.
- The report's second concern (five tests that passed before the code): judged acceptable.
  Each of the five is killed by a mutation above, and each has a positive twin in the same file, so none is vacuous.
  The deviation from "see each test fail" is disclosed in the report and costs nothing.

## Blocking

None.

## Important

### I1. Level 3 labels the reverse of `rests_on` "supported by", which inverts its meaning

`src/lodge/core/views.py:133`, `tests/core/test_views_links.py:52`.
The brief says `("supports", x, status)` per `supports`, and plan Ruling 7 (plan line 54) fixes the label as "supports" because "supported by" would label the reverse wrongly.
`d.supports[B]` holds the entries that rest on B.
Probe: A has `rests_on: [B]`; `format_level3(level3(s, d, B))` prints `supported by: s-aaaaaa (current)`, which reads as "B is supported by A", the opposite of what the data says (B supports A).
A reader following the viewer's goal ("if it rests on another point that's also wrong") would read the dependency backwards.
The report's reasoning ("the design wins") does not hold here: the design's line 112 says "supports", only line 114 says "supported by", and the plan already ruled between them.
Fix: change the string at `views.py:133` to `"supports"` and the assertion at `test_views_links.py:52` to `("supports", "s-aaaaaa", "current")`.
Separately, design line 114 contradicts line 112 and Ruling 7; the author should correct it to "supports" (a design-text change, so the coordinator raises it, not the builder).

## Minor

### M1. A self-reference produces a malformed check 8 line

`src/lodge/core/check_cycles.py:22-28`.
For `s-aaaaaa` with `rests_on: [s-aaaaaa]` the gate prints `s-aaaaaa: rests_on itself` (check 2) and `s-aaaaaa: is in a cycle of rests_on links with ` (check 8), the second ending in "with " and an empty list.
The plan's definition ("reaches itself through one or more links") does include a self-loop, so this follows the letter, but the message is broken and the problem is reported twice.
Fix: skip an entry whose cycle has no other member (check 2 already names it), `if i in reach[i] and (others := ...)`, and add the self-loop case to `test_rests_on_itself_fails_check_2` as `not any(p.check == 8 ...)`.

### M2. Stale docstrings after check 8 and the new check 6 clause

`src/lodge/core/check_state.py:1` says "1, 2, 3, and 7"; `src/lodge/core/check_change.py:28` says "those of 1, 2, 3, and 7"; the `_links_to_dead` docstring (`check_change.py:105`) still describes only narrows, confirms, and edits of a retired entry.
Fix: add 8 to the first two, and "or newly rests on a retired entry" to the third.

### M3. The cycle tests do not pin "other members of its cycle"

`tests/core/test_check_links.py:84`.
Changing `if t != i and i in reach[t]` to `if t != i` in `check_cycles.py:26` leaves all 11 tests green.
A cycle entry that merely reaches a non-member would then list it, and an entry that only rests on a cycle would be unflagged and untested.
Fix: extend `test_three_entry_cycle_names_the_other_two` (or add a test) with `s-dddddd` resting on `s-aaaaaa` and `s-aaaaaa` also resting on `s-eeeeee`: expect exactly three check 8 problems, none naming d or e.

### M4. Duplicated "only rests_on differs" test and per-iteration recomputation in check 4

`src/lodge/core/check_entries.py:32` and `:49`.
`replace(before, rests_on=entry.rests_on) == entry` is written twice, and the first is recomputed inside the `for action, verb in wanted` loop though it does not depend on `action`.
Fix: a module function `_only_rests_on_differs(before: SpecEntry | None, entry: SpecEntry) -> bool`, called once per entry before the loop; the second site becomes `elif not _only_rests_on_differs(before, entry)`.

### M5. "Changed since" re-implements `derive._order` and `_flags` grows a nested block

`src/lodge/core/views.py:200-211`.
The `(datetime.fromisoformat(date), id)` pair is `derive._order`, written out twice more, in an awkwardly wrapped comparison.
`_flags` is now about 45 lines with a four-level nesting.
Fix: make `_order` public as `order_key(d: Decision)` in `derive.py` and move the block to `_rests_on_flags(s, d, record, who) -> list[str]` in `views.py`: `if order_key(latest) > order_key(who)`.
Mind the 15-line allowance on `derive.py` (the rename adds none).

### M6. Entry-ID regex written inline instead of beside `_ID`

`src/lodge/core/feedback.py:48`.
`_ID` at line 15 is `\b[ds]-[0-9a-hjkmnp-tv-z]{6}\b`; the new `\bs-...` is a second literal in a function body, and Task 3 will extend `_ID` only (plan line 186), leaving the two to drift.
The new block also sits in `_messages`'s `else`, while the decision branch has its own `_decision_messages`.
Fix: a module constant `_ENTRY_ID = re.compile(r"\bs-[0-9a-hjkmnp-tv-z]{6}\b")` and a `_entry_messages(record, after, length)` generator mirroring `_decision_messages`.

### M7. Guide stays at 60 lines by removing the blank lines around the fenced example

`src/lodge/cli/guide.md:30-31` and `:40-41`.
The fence now abuts the preceding and following prose lines.
CommonMark allows it, but agents read this file as plain text and the example no longer stands apart; the report lists the removal but not as a concern.
The cap is `tests/e2e/test_guide.py:18` (`<= 60`), and raising a limit is the author's call.
Fix: restore the blank lines and make room by merging two existing lines of equal subject (for example lines 29 and 30, both about what `add` does), or ask the author to raise the cap to 62.

### M8. Smaller test points

- `tests/core/test_derive_links.py:8,17` and `tests/core/test_views_links.py:18` use `Action("link")` and `Action(later)` where `Action.LINK` reads better; `test_check_links.py:18` does the same through a string parameter.
- `tests/app/test_writes.py:210` asserts only `any(p.check == 6 ...)`; assert the message `s-bbbbbb: rests on s-aaaaaa, which is retired` so another check 6 cannot satisfy it.
- `check_cycles` is exported from `src/lodge/core/__init__.py:5` with no consumer outside core (the plan lists the file, but `check_areas` is not exported); drop it unless a later task imports it.

## Design

The interfaces the plan lists are all produced as named (`Action.LINK`, `Derived.linked_by` newest first, `Derived.supports` by ID with known entries only, `check_cycles(s)` run by `check_state`).
Later tasks consume them as expected: Task 3's flag order ("before Task 2's rests-on flags") matches the position in `_flags`; Task 7's `Shown.supports` reads `d.supports`; Task 8's one-decision-per-area `link` lists pass check 4 and check 6 as written.
The one boundary breach is I1: the string a later reader sees is the string Ruling 7 forbids.
`check_cycles` builds its `Problem` by hand rather than through `problem_at` (`check_cycles.py:25`), the same as `check_areas`, because `problem_at` lives in `check_state` and an import would cycle; acceptable and consistent.
Check 8 is quadratic in entries (`reach` for every entry); fine at 82 entries, worth a comment only if the store grows to thousands.

## Files read

`CLAUDE.md`, the brief, the report, the plan (Task 2, Calls made, Tasks 3, 7, 8 interfaces), the design lines 100 to 123, the full diff of f23dd1d, and at the commit: `check_entries.py`, `check_cycles.py`, `check_change.py`, `check_state.py`, `derive.py`, `views.py`, `feedback.py`, `guide.md`, the five new test files, and the diffs to `tests/app/test_writes.py` and `tests/e2e/test_guide.py`.

## Files not read

`task-2-codex-final.txt`, `task-3-brief.md`, `tests/structure_rules.py`, `tests/structure_tables.py` (the structure tests ran and passed), the viewer and `app` packages, and the spec (`docs/superpowers/specs/2026-10-29-lodge-design.md`; the plan's rulings and the design were the authority for this task).
`tests/e2e/test_view.py` and `tests/viewer/test_server.py` were not run (sockets).
