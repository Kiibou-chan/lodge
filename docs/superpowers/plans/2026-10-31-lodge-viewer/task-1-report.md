# Task 1 report

Implemented area ranks, specification dependency links, reading orders, cross-area rendering, and shared-rank feedback.
No staging, commits, pushes, or record writes were performed.
The supplied brief was already untracked and is left unchanged.

## Changes per file

- `src/lodge/core/model.py`: appended optional `Area.rank` and default-empty `SpecEntry.rests_on`.
- `src/lodge/core/fields.py`: added `read_rank`, accepting textual non-negative integers without leading zeroes and reporting the `rank` key on rejection.
- `src/lodge/core/headers.py`: accepted and parsed both new fields, with specification IDs required in `rests_on`.
- `src/lodge/core/fileformat.py`: emitted non-empty `rests_on` and set `rank` immediately after the title, preserving legacy output when absent.
- `src/lodge/core/order.py`: added `Placement`, area sorting, written order, and depth-first dependency order with deterministic cycle fallback and the last-placed target as parent.
- `src/lodge/core/render.py`: added `Placed` and `SpecArea.placed`, retained written order in `entries`, rendered dependency order, and appended cross-area target lines after statements.
- `src/lodge/core/feedback.py`: added feedback only for written area paths whose rank is shared, with sorted names and Oxford commas.
- `src/lodge/core/check_change.py`: included rank changes in area notes.
- `src/lodge/core/__init__.py`: exported the new ordering, placement, and feedback interfaces.
- `src/lodge/app/writes.py`: appended area feedback using changed file paths, adding one line.
- `src/lodge/cli/parser.py`: updated the specification help verbatim.
- `tests/core/test_order.py`: added the nine ordering tests listed below.
- `tests/core/test_fileformat_links.py`: added the six format tests listed below, including parametrised values.
- `tests/core/test_area_feedback.py`: added shared, unshared, and unwritten rank feedback tests.
- `tests/core/test_render.py`: added four rendering and placement tests.
- `tests/core/test_check_change.py`: added the rank-change note test.
- `tests/app/test_writes.py`: added an application-level shared-rank feedback test.

## Test-first evidence

Tests were written before implementation.
The first combined run stopped during collection because the public `area_names` and `area_feedback` imports did not exist.
Imports were temporarily moved inside tests so every new test could execute before implementation, then restored to module scope after implementation.
Full local output is retained under `.drafts/task1-first.txt`, `.drafts/task1-red.txt`, `.drafts/task1-format-red.txt`, and `.drafts/task1-parent-red.txt`.
The draft files are ignored and are not deliverables to stage.

| Test | First failing output |
| --- | --- |
| `test_ranked_areas_first_then_by_name` | `ImportError: cannot import name 'area_names' from 'lodge.core'` |
| `test_shared_rank_ordered_by_name` | `ImportError: cannot import name 'area_names' from 'lodge.core'` |
| `test_folder_without_area_file_sorts_with_unranked` | `ImportError: cannot import name 'area_names' from 'lodge.core'` |
| `test_entry_after_what_it_rests_on` | `ImportError: cannot import name 'derived_order' from 'lodge.core'` |
| `test_no_links_keeps_written_order` | `ImportError: cannot import name 'derived_order' from 'lodge.core'` |
| `test_under_is_the_target_placed_last` | `ImportError: cannot import name 'derived_order' from 'lodge.core'` |
| `test_dependant_follows_what_it_rests_on` | `ImportError: cannot import name 'derived_order' from 'lodge.core'` |
| `test_cycle_falls_back_to_written_order` | `ImportError: cannot import name 'derived_order' from 'lodge.core'` |
| `test_retired_target_does_not_hold_an_entry_back` | `ImportError: cannot import name 'derived_order' from 'lodge.core'` |
| `test_rests_on_round_trips` | `TypeError: SpecEntry.__init__() got an unexpected keyword argument 'rests_on'` |
| `test_rank_round_trips` | `TypeError: Area.__init__() got an unexpected keyword argument 'rank'` |
| `test_rank_reads_quoted_and_plain_alike[2]` | `TypeError: Area.__init__() got an unexpected keyword argument 'rank'` |
| `test_rank_reads_quoted_and_plain_alike["2"]` | `TypeError: Area.__init__() got an unexpected keyword argument 'rank'` |
| `test_rank_must_be_a_whole_number[-1]` | Assertion rejected `unknown key 'rank'; the keys here are kind, title, order` |
| `test_rank_must_be_a_whole_number[1.5]` | Assertion rejected `unknown key 'rank'; the keys here are kind, title, order` |
| `test_rank_must_be_a_whole_number[true]` | Assertion rejected `unknown key 'rank'; the keys here are kind, title, order` |
| `test_rank_must_be_a_whole_number[two]` | Assertion rejected `unknown key 'rank'; the keys here are kind, title, order` |
| `test_rank_must_be_a_whole_number[01]` | Assertion rejected `unknown key 'rank'; the keys here are kind, title, order` |
| `test_rank_must_be_a_whole_number[""]` | Assertion rejected `unknown key 'rank'; the keys here are kind, title, order` |
| `test_rests_on_holds_entry_ids_only` | Assertion rejected `unknown key 'rests_on'; the keys here are id, kind, code, title, imported_from` |
| `test_area_without_rank_writes_as_before` | Passed before implementation, since this explicitly checks existing behaviour |
| `test_shared_rank_feedback` | `ImportError: cannot import name 'area_feedback' from 'lodge.core'` |
| `test_unshared_rank_no_feedback` | `ImportError: cannot import name 'area_feedback' from 'lodge.core'` |
| `test_unwritten_area_no_feedback` | `ImportError: cannot import name 'area_feedback' from 'lodge.core'` |
| `test_render_spec_follows_rank_then_derived_order` | `TypeError: Area.__init__() got an unexpected keyword argument 'rank'` |
| `test_render_spec_lists_cross_area_targets` | `TypeError: SpecEntry.__init__() got an unexpected keyword argument 'rests_on'` |
| `test_spec_view_places_with_depth_under_and_also` | `TypeError: SpecEntry.__init__() got an unexpected keyword argument 'rests_on'` |
| `test_cross_area_target_is_across_not_also` | `TypeError: SpecEntry.__init__() got an unexpected keyword argument 'rests_on'` |
| `test_area_rank_change_is_note` | `TypeError: Area.__init__() got an unexpected keyword argument 'rank'` |
| `test_add_area_sharing_a_rank_gives_feedback` | `LodgeError: a.md:5: unknown key 'rank'; the keys here are kind, title, order, name, base` |

The invalid-rank tests initially had an incorrect expected source line, which was corrected to line 4 before implementation and their rejection assertion strengthened to exclude unknown-key errors.
The invalid-link test initially accepted any problem, so its assertion was strengthened before implementation to require the entry-ID diagnostic.
The legacy-output test necessarily passed before implementation, rather than introducing an artificial failure.
The parent tests briefly followed the literal design wording, then were corrected after reading the cited ruling and rerun red before fixing the parent selection.
That run ended `2 failed, 17 passed in 0.20s`, with `s-aaaaaa` differing from expected `s-bbbbbb` in each parent assertion.

## Commands and results

Repository instructions, relevant source and test files, and the design's ordering lines were inspected with `cat`, `rg`, and `git diff`.
The following lists the substantive execution and validation commands, including failed runs.

- `uv run pytest tests/core/test_order.py tests/core/test_fileformat_links.py tests/core/test_area_feedback.py tests/core/test_render.py tests/core/test_check_change.py tests/app/test_writes.py -q`: first ended `2 errors in 0.28s`; after deferring imports, ended `28 failed, 45 passed in 0.39s`; final focused run ended `73 passed in 0.23s`.
- `uv run pytest tests/core/test_fileformat_links.py -q`: before implementation, ended `11 failed, 1 passed in 0.19s`; the corrected and strengthened assertions were also run red before implementation.
- `uv run pytest tests/core/test_order.py tests/core/test_render.py -q`: corrected parent assertions ended `2 failed, 17 passed in 0.20s` before their fix.
- `uv run ruff format`: reformatted nine files initially; later reported `401 files left unchanged`.
- `uv run ruff check --fix`: initial run fixed unused imports but reported local-import errors; imports were restored to module scope, and the last fix run ended `Found 3 errors (3 fixed, 0 remaining).`.
- `uv run ruff format --check`: `401 files already formatted`.
- `uv run ruff check`: `All checks passed!`.
- `uv run mypy`: `Success: no issues found in 162 source files`.
- `uv run vulture`: exited successfully with no output.
- `uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py`: `1084 passed, 1 skipped in 42.00s`.
- `uv run lodge check --gate`: `ok`, followed by the repository's existing area-added notes, ending `note: area writing: added`.
- `uv run pytest tests/e2e/test_view.py -q -k test_view_passes_the_port_to_the_viewer`: `1 passed, 2 deselected in 0.50s`.
- `uv run --frozen --quiet lodge guide`: read the writing and reading rules.
- `uv run --frozen --quiet lodge show d-a3h9f3` and the same with `--reasoning`: read the cited dependency-indent ruling.
- `uv run lodge spec > .drafts/task1-spec.txt`: exited successfully.
- `git show HEAD:src/lodge/core/render.py > .drafts/task1-original-render.py`, followed by a local Python comparison using the original renderer through the CLI: `Specification output is byte-for-byte unchanged from HEAD render_spec.`.
- `uv run pytest tests/e2e/test_view.py -q -k test_view_outside_a_repository_is_one_sentence`: `1 passed, 2 deselected in 0.28s`.
- `git diff --check`: exited successfully with no output.

## Interpretation and remaining checks

Design line 120 says the first target supplies the indent, whereas the brief specifies the last-placed target and cites `d-a3h9f3`.
Reading that ruling and its reasoning resolved the apparent conflict: it explicitly replaces the agent-chosen tie and indent rules with the depth-first arrangement implemented here.
The final implementation and assertions follow the brief exactly, including `under == b` and `also == (a,)` for an entry resting on a and b.
No new ruling or record was needed.

The builder gate excludes the socket-bound server tests in `tests/viewer/test_server.py` and `tests/e2e/test_view.py::test_view_serves_the_project_until_interrupted`.
The non-socket port-routing test was run separately as required.
The other test in the ignored end-to-end file, `test_view_outside_a_repository_is_one_sentence`, is excluded by the prescribed command but does not require a socket, so it was also run separately and passed.
The coordinator must run `sh scripts/check.sh` outside the sandbox before staging, committing, and pushing.

## Fix round 1

Addressed both Important findings and all nine Minor findings using the stated cheap fixes.
Design notes D1 to D3 are unchanged, as requested.
No staging, commits, pushes, or record writes were performed.

### Findings and changes

- I1: added `test_dependants_follow_depth_first` with written A, B, C, D, B and C resting on A, and D resting on B, asserting A, B, D, C and every depth and parent.
  Added `test_diamond_uses_last_placed_target_at_depth_two`, asserting D is at depth 2 under C when it rests on B and C.
- I2: strengthened `test_retired_target_does_not_hold_an_entry_back` with unrelated live C, written A, C, and assertions for both order and A's root placement.
- M1: added `test_retired_same_area_target_is_not_also`, with live A, retired B, and C resting on both.
- M2: retained the brief's explicit inclusion of each cross-area entry target, including retired entries, and pinned that decision with `test_retired_cross_area_target_remains_across`.
  The test checks both the structured link and the rendered line.
- M3: took the review's cheap documentation option, adding a comment that recursion depth is bounded by the number of current entries in an area.
  The traversal remains recursive; very large chains can still exceed Python's recursion limit.
- M4: deduplicated targets in `_area` with `dict.fromkeys`, preserving their original order for both `also` and `across`.
  Added `test_duplicate_targets_are_shown_once` covering both link collections.
  Parsing remains unchanged, as the review explicitly offers display deduplication as an alternative.
- M5: documented `Placement`, `Placed`, `area_names`, `written_order`, and `derived_order`, and corrected `SpecArea` to distinguish written entries from derived placements.
- M6: renamed the cross-area generator variable to `other`.
- M7: renamed `visit`'s parameter to `under` and removed the alias.
- M8: built a single `shown` dictionary of level-one entries and reused its values for written entries and derived placements.
- M9: removed empty lines immediately after test signatures in `test_order.py`, `test_area_feedback.py`, and the shared-rank application test.

### Regression failures before restoring or fixing the code

Each row was run individually with `uv run pytest FILE::TEST -q` against its stated faulty variant, before restoring production code.
Every run below exited 1 with `1 failed`; these were assertion failures, not collection or environment errors.
The duplicate-link test failed against the original faulty rendering code before its fix.
Full output is retained in ignored `.drafts/task1-fix-*.txt` files; the decisive failing output is recorded here.

| Finding and test | Faulty variant | Failing output |
| --- | --- | --- |
| I1: `test_dependants_follow_depth_first` | Queue-based breadth-first traversal | `At index 2 diff: 's-cccccc' != 's-dddddd'`; `1 failed in 0.24s` |
| I1: `test_diamond_uses_last_placed_target_at_depth_two` | Parent selected as first placed dependency rather than last | `At index 3 diff: (2, 's-bbbbbb') != (2, 's-cccccc')`; `1 failed in 0.18s` |
| I2: `test_retired_target_does_not_hold_an_entry_back` | Removed `if t in ordered` target filter | `assert ('s-cccccc', 's-aaaaaa') == ('s-aaaaaa', 's-cccccc')`; `1 failed in 0.18s` |
| M1: `test_retired_same_area_target_is_not_also` | Removed `d.status.get(t) == "current"` from `also` | `At index 1 diff: ('s-bbbbbb',) != ()`; `1 failed in 0.19s` |
| M2: `test_retired_cross_area_target_remains_across` | Added current-status filter to `across` | `assert () == (('s-bbbbbb', 'other'),)`; `1 failed in 0.19s` |
| M4: `test_duplicate_targets_are_shown_once` | Original renderer without deduplication | `assert ('s-aaaaaa', 's-aaaaaa') == ('s-aaaaaa',)`; `1 failed in 0.19s` |

An initial attempted breadth-first mutant still visited grandchildren before siblings and passed the new test.
It was replaced by an actual queue-based breadth-first traversal, producing the I1 failure above.
All temporary production mutations were restored with `finally` blocks before applying the fixes.
No additional tests were added or strengthened for the documentation, variable naming, blank-line, or level-one reuse changes.

### Validation

- `uv run pytest tests/core/test_order.py tests/core/test_render.py -q`: `24 passed in 0.10s` after restoration and fixes.
- `uv run ruff format --check`: `411 files already formatted`.
- `uv run ruff check`: `All checks passed!`.
- `uv run mypy`: `Success: no issues found in 172 source files`.
- `uv run vulture`: exit 0, no output.
- `uv run lodge check --gate`: `ok`, followed by the existing area-added notes.
- `uv run pytest tests/e2e/test_view.py -q -k 'test_view_passes_the_port_to_the_viewer or test_view_outside_a_repository_is_one_sentence'`: `2 passed, 1 deselected in 0.30s`.
- `uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py`: `1159 passed in 31.31s`, including the committed Task 2 and Task 3 tests.
- `git diff --check`: exit 0, no output.

The socket-bound `tests/viewer/test_server.py` and `tests/e2e/test_view.py::test_view_serves_the_project_until_interrupted` remain excluded by the sandbox gate prescribed in the brief.
The coordinator's full socket-capable gate remains outstanding.
