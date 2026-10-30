# lodge

Knowledge tool for agent-built software: decisions and specification entries, levelled reads, a check.
Authority: `lodge spec`; the plan argues from it, never over it.
Read decisions and her rulings with `lodge show` and `lodge search`; her own decisions have `decided_by: author` (`lodge search --by author`).
The entries are agent text written from the design document she approved, awaiting her confirmation through the viewer.
The design document (`docs/superpowers/specs/2026-10-29-lodge-design.md`) is frozen history.
Read through lodge, never by opening record files; run `uv run --frozen --quiet lodge guide` for the writing rules.
Drafts go under `.drafts/`, and `lodge add --dry-run` precedes every `lodge add`.
Open plans in `docs/superpowers/plans/`, each with `-progress.md` (the ledger) and a folder of briefs, reports, and reviews.
Plan's last task merged → same branch `git mv`s plan, progress, folder to `docs/superpowers/plans/done/`, links fixed (`git grep 'plans/<file>'` = 0 outside `done/`).

## Commands

`sh scripts/check.sh` (the whole gate: ruff format, ruff, mypy strict, vulture, pytest, and once lodge holds records `lodge check --gate`) · `uv run pytest <files> -q` · `uv run lodge …`.
Code: `src/lodge/{core,app,gitstore,cli,viewer,hook}` behind front doors (`__init__.py`), wired in `src/lodge/main.py`; tests in `tests/`, `tests/structure_rules.py` the import and size rules.

## Structure checks

`tests/test_structure.py` runs in every pytest: allowed imports, front doors, no cycles, modules ≤ 300 lines, core purity, I/O confinement (LODGE-5).
There is no baseline: lodge starts clean.
Fix a violation in the code; never loosen a rule to pass.
Raising a limit or adding an allowed edge is the author's call, recorded as a decision.
In `core` and `app`, take the time and randomness through the ports; never read the clock or `secrets`.

## Hard rules

- Test-first; see each new test fail before its code; all existing tests keep passing.
- Public repository: no personal paths, machine names, secrets, or another project's records in code, tests, or docs; fixtures synthetic (a made-up project), never her words or another project's records.
- Tests never touch a real repository: git only in `tmp_path` with `GIT_CONFIG_GLOBAL` empty, `GIT_CONFIG_NOSYSTEM=1`, `git init -b main`; no network.
- Record files are written only through `lodge add`, never by hand, here too.
- User-facing text and Markdown: British English, no em-dashes, Oxford comma, one sentence per line.

## Build process (adapted from an existing project)

Plan → plan review (two angles) → one fix round → rechecks until 0 Blocking, 0 Important → preflight scan in the ledger (each task's Produces against the next tasks' Consumes) → build.
Agents in `.claude/agents/`: `builder` (Sonnet, one task from its brief), `reviewer` (Opus, first reviews), `rechecker` (fix diffs), `integrator` (merges, rulings), `planner` (plans, fix rounds).
Tasks run in order on one build branch in its own worktree; each task: brief, build, report, review (correctness, then practice, then design), fix round if needed, ledger line.
Minors are parked in the ledger and taken by the next round touching those files.
Final whole-branch review, fix wave, recheck.
A finding that conflicts with the plan is recorded with `lodge add` (scope `process`, `work_item` the plan), with a handle per argument and the cost if wrong in its reasoning.
The ledger line gives the decision's ID; a ruling that changes what the spec says goes to the author.

## Git

Branch per work item; `main` takes only merges, and code reaches `main` only on the author's go.
`git -c user.name="Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit` with explicit paths, trailer `Co-Authored-By: Claude <noreply@anthropic.com>`; push the branch to `origin` (GitHub) after each commit; never push `main` from a builder, reviewer, or rechecker.
