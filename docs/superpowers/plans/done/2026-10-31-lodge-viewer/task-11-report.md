# Task 11 report

Status: DONE_WITH_CONCERNS.
No source code or tests changed, and nothing was committed or pushed.
The real Git index was not used for recording; the add used the Global Constraints' alternate index and object directory recipe.

## Changes per file

Each area came from `lodge draft area:NAME`, with only `rank: N` inserted after `title` in its draft.

| File | Change |
| --- | --- |
| `lodge/spec/purpose/_area.md` | Rank 1. |
| `lodge/spec/constraints/_area.md` | Rank 2. |
| `lodge/spec/model/_area.md` | Rank 3. |
| `lodge/spec/levels/_area.md` | Rank 4. |
| `lodge/spec/writing/_area.md` | Rank 5. |
| `lodge/spec/reading/_area.md` | Rank 6. |
| `lodge/spec/hook/_area.md` | Rank 7. |
| `lodge/spec/storage/_area.md` | Rank 8. |
| `lodge/spec/structure/_area.md` | Rank 9. |
| `lodge/spec/rollout/_area.md` | Rank 10. |
| `lodge/decisions/d-3d696s-area-ranks-follow-the-first-design.md` | Coordinator process decision, with the required title and work item, a one-sentence statement, reasoning naming the earlier plan's line 73, a numbers handle for that line, and no entry changes. |
| `docs/superpowers/plans/2026-10-31-lodge-viewer/task-11-report.md` | This report. |

Drafts and final dry-run and add outputs remain under `.drafts/task-11/`.
Record files were read only through lodge and written only by the single successful `lodge add`.

## Tests and verification

No tests were added because this task changes records only and names no new tests.
There are therefore no new tests or first failing test outputs.
All commands below completed successfully unless explicitly noted.

| Command or group | Last lines or result |
| --- | --- |
| `cat docs/superpowers/plans/2026-10-31-lodge-viewer/task-11-brief.md`, then `cat CLAUDE.md` | Read the requirements and repository instructions. |
| `uv run --frozen --quiet lodge waiting` | `waiting for the author`, `nothing`; also nothing waiting for an agent. |
| `uv run --frozen --quiet lodge guide` | Exit-code guidance: 0 done, 1 check failed, 2 usage or environment. |
| `uv run --frozen --quiet lodge draft --help` and `lodge add --help` | Draft and add usage, including `--dry-run`. |
| `sed -n '65,80p' docs/superpowers/plans/2026-10-30-lodge-on-itself.md` | Confirmed the area sequence at line 73. |
| `uv run --frozen --quiet lodge draft area:NAME` for all ten names | Generated area Markdown, retained in the drafts. |
| Initial `uv run --frozen --quiet lodge add --dry-run .drafts/task-11/*.md` | `dry run: nothing published`; advisory feedback requested a numbers handle for 73, which was added before the final dry run. |
| Final `uv run --frozen --quiet lodge add --dry-run .drafts/task-11/*.md` | `dry run: nothing published`; no check lines and no shared-rank feedback. |
| Global Constraints' `mkdir`, index copy, and alternate-index `uv run --frozen --quiet lodge add .drafts/task-11/*.md` | `staged d-3d696s`. |
| `uv run lodge spec \| grep '^# '` | Purpose; Constraints; The model; Levels; Writing, feedback, and the check; Reading and the viewer; A hook against writing elsewhere; Storage; Structure; Rollout and open questions, in that order. |
| `uv run lodge check` | `ok`. |
| `uv run ruff format --check` | `508 files already formatted`. |
| `uv run ruff check` | `All checks passed!` |
| `uv run mypy` | `Success: no issues found in 194 source files`. |
| `uv run vulture` | No output, exit 0. |
| `uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py` | `1367 passed in 36.44s`. |
| `uv run lodge check --gate` | `ok`, area-change notes, and finally `note: uncommitted record changes in lodge/; commit them before you push`. |
| `uv run pytest tests/e2e/test_view.py -q -k 'not test_view_serves_the_project_until_interrupted'` | `6 passed, 1 deselected in 0.39s`. |
| `uv run --frozen --quiet lodge show d-4dp4gm --reasoning` | Read the existing order-check decision; it does not need replacement or narrowing for ranks. |
| `uv run --frozen --quiet lodge show d-3d696s --provenance` | Confirmed the process decision, numbers handle, and required work item. |
| `git status --short` | Ten modified area files, the new decision, and the supplied untracked brief before this report was written. |
| Exploratory `rg` and `sed` over source and test definitions | Inspected draft generation and area notes; one `rg` exited 2 because several optional filename globs did not exist, then searches used existing paths. |

The socket-bound files excluded from the main run were `tests/viewer/test_server.py` and `tests/e2e/test_view.py`.
The six socket-free cases in the latter file were run separately, including `test_view_passes_the_port_to_the_viewer`.
Its socket-bound `test_view_serves_the_project_until_interrupted` was deselected.
The coordinator still needs to run `sh scripts/check.sh` outside the sandbox.

## Concerns and uncertainty

Both dry runs and the add reported `order changed` for model, purpose, reading, storage, and writing, although the drafts' order lines were left exactly as supplied by `lodge draft`.
The gate repeated those notes and passed.
No corrective order edits were attempted, and no specification entries were changed.
The exact cause of those notes was not established.
The final dry run also suggested related decisions as advisory feedback; the new decision adds ranks and does not replace or narrow those decisions.
No shared-rank feedback or failed check occurred.
