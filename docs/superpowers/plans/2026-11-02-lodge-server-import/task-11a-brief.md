# Brief: Task 11a of `docs/superpowers/plans/2026-11-02-lodge-server-import.md`

You build Task 11a of the plan named above, in the worktree `/var/tmp/lodge-import-records`, on branch `server-import-records`.
Read `CLAUDE.md` first, then the plan's header, "Global Constraints", "Calls made", "Names this plan consumes", "Review Focus", and the section "### Task 11a" in full; those are your requirements, with the exact values to use verbatim.
The plan was written for a sandbox: you have full access (d-94tynf) and network, but `Bun.spawnSync` stays the rule for spawning, and the "Coordinator" steps are not yours.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Run `sh scripts/check-ts.sh` last; it must exit 0. The structure checks (`ts/tests/structure/`, run by `bun test`) gate the finished task, not intermediate commits.
Never run `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name. `bun install --frozen-lockfile` in `ts/` is allowed.
Never edit earlier briefs, reports, or reviews in `docs/superpowers/plans/2026-11-02-lodge-server-import/` or in `docs/superpowers/plans/done/`: they are history.
Line handles in the plan drift as tasks land; re-locate them by content.
Biome runs with `--error-on-warnings`; `noTemplateCurlyInString` fires on strings holding a dollar sign and brace, so build those by concatenation. Modules stay at 300 lines or fewer; split before the structure test does.
Public repository: no personal paths, machine names, or secrets in code, tests, docs, or the report; fixtures are synthetic.
User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; code comments state the fact.
Front doors: none (records only); tests may import a package's non-front-door files only where the structure rules allow (see `ts/tests/structure/`).
Commit when the gate is green, with explicit paths: `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, message ending with the trailer `Co-Authored-By: Codex <noreply@openai.com>`; then `git push origin server-import-records`. Never touch `main`.
Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-import/task-11a-report.md`: what you changed per file, each test added or carried with its first failing output (or the mutation it failed against, as a table with a `file:line` column), the commands you ran and their last lines, every deviation from the plan with the reason, anything you were unsure of. Commit the report too.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.

## Notes for this task

This is Task 11a only (the plan's "### Tasks 11a, 11b, and 11c" section: its rules for every part, then "Task 11a"); 11b and 11c are later briefs.
You write records, not code: the plan's Task 11 sentence "Tests never touch a real repository" does not apply, but "Record files are written only through `lodge add`, never by hand" does, and so does the hook's advice if it fires.
Setup: the lane worktree is this repository's own checkout on branch `server-import-records`; run lodge as `uv run --frozen --quiet lodge …` (the Python lodge 0.2 reads `lodge/` here); drafts go under `.drafts/task-11a/` (git-ignored); read `uv run --frozen --quiet lodge guide` first, and `lodge waiting` shows nothing waiting.
Coordinator decisions only (`decided_by: coordinator`), never `decided_by: author` and never narrowing or replacing one of her decisions (the ones with `decided_by: author`, listed in the plan); `lodge show ID --reasoning --provenance` reads a decision; `lodge search` finds related ones.
Every consumed ID exists and was checked: the entries s-a4jfp1, s-v1sb0j, s-165qfh, s-3xka4c, s-07ar34, s-z1zvb4, s-j8tp0n, and the decisions the plan names to narrow (d-zq5sfb, d-jxwj8m, d-cg3nn3, d-a3e8kb; note d-cg3nn3 and s-07ar34 are already narrowed by d-3d4g9j and d-dyrpc6, read those first so the edit and the narrowing agree with them).
`uv run --frozen --quiet lodge spec | grep -c 'changed since'` already prints 2 before you start; read which entries, and take them in the "changed since" pass or name them in the report.
The design is `docs/superpowers/specs/2026-11-02-lodge-server-design.md` (frozen history, read it, never edit it); the plan's line ranges refer to it.
"Export to git" and "Moving from lodge 0.2" entries state what Tasks 2 to 10 built; read `ts/src/git/export.ts`, `ts/src/app/exporting.ts`, `ts/src/app/exporters.ts`, `ts/src/app/importing.ts`, and `ts/src/hook/` for the facts, and the decisions d-pv341r, d-sj6hmf, d-va3j7x, d-sdpcyb, d-hg9qq9, d-83kt6y, d-b61590, d-j5s0h0 for the rulings; every number in a statement needs a `numbers:` handle.
Entries are one paragraph within 150 words, British English, no em-dashes, Oxford comma, one sentence per line, in the present tense, from the design's claims; a claim not built from step 1 says "From build step N", resting on the entry for the build order (d-yng7m8; its entry may not exist yet: check `lodge search "build order"`; if none, say in the report and state the step in the entry without `rests_on`, to be linked in 11c).
Dry-run every add; commit `lodge/` (staged by `lodge add`) with the report; the report section goes to `docs/superpowers/plans/2026-11-02-lodge-server-import/task-11-report.md` (create it; 11b and 11c extend it).
Gate before the commit: `uv run --frozen --quiet lodge check` prints ok, and `sh scripts/check.sh`.
