# Plan fix round 1 report: lodge server core

Status: done; committed and pushed (see the end).

## Read
- Both reviews, the plan, the ledger, `planner-brief.md`, `planner-report.md`, `probes.md`.
- Source checks: `tests/structure_tables.py`, the confinement lines of `tests/structure_imports.py` and `tests/structure_calls.py`, `check_state.py:95-128`, `search.py:79`, `fields.py:11-14` and `:150-163`, the imports of every core module of Tasks 5 to 9, `tests/core/checks.py`, and the imports of every carried test of Tasks 5 to 9; the design's "Build order" and "The model".

## Probes (items 15 to 20 of `probes.md`, sources in `probes/fix1/`)
- `test.each` wrapping, `casefold` and `isdigit`, `lower`, `pyRepr`, offsets, and the gate's tools under `bun --bun`; each cited at its finding in `plan-fix-1.md`.

## Rulings recorded (scope process, work item the plan; dry run first, each "looks related" answered no unless set)
- d-bkc7md the YAML layer (replaces d-458jhp); d-s2rdn2 knip and the front doors (narrows d-4psbdv); d-x6f9za where the structure rules bind and each adapter's permissions; d-mfayy5 the task splits; d-jtxwg3 the sign-in page in plan 3; d-xph4ac Bun runs the gate's tools too (replaces d-03xx0a); d-0qmd10 the differential run with the writers (replaces d-g3mbmc).

## Plan edits
- Plan rewritten section by section: Global Constraints, Calls made (19 items), Review Focus (7 items), plan 3's paragraph, the passkeys bullet, the parity rows of the split tasks and the structure rows, Tasks 1 to 4, Tasks 5a to 9b (from 5, 7, 8, and 9), Task 10's Consumes, Tasks 11 and 12.
- `plan-fix-1.md` maps every finding (20 correctness, 20 practice) to its lines; every Important and every Minor is fixed, none declined.
- Ledger: the replaced rulings' lines point to the new IDs; fix round line and three new ruling lines.
- `planner-brief.md`: "the plan's worktree" in place of its folder.
- Gate: `sh scripts/check.sh` green (1399 passed, `lodge check --gate` ok) with the seven records staged.

## Open
- `plan-review-practice.md:103` still quotes the worktree's local folder, as the review's handle; reviews were left as written.
- Plan 3 must still choose how the command refuses `title_chars = 80.0`, since `Bun.TOML.parse` cannot tell it from `80` (plan, plan 3's paragraph).
