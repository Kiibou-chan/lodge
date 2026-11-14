# Plan review, practice angle: lodge server core

Plan: `docs/superpowers/plans/2026-11-02-lodge-server-core.md` at `c3320a4`, branch `server-core`.
Angle: can a builder who sees one brief, `CLAUDE.md`, and the repository build each task without guessing; does the plan run well in practice; does it carry out build step 1 without building later steps' work.
Status: done.

## Findings

Probes ran in my own scratch folder: a copy of `probes/` with its installed packages, and `codex sandbox -c sandbox_mode="workspace-write"` (codex-cli 0.165.0) for the sandbox.
Under that sandbox the working folder and `/tmp` are writable, the home folder is read-only, a socket is refused, and `bun test`, `tsc`, dependency-cruiser, Biome, and knip all run; so the plan's sandbox assumptions hold (Global Constraints, plan line 21 and 22).

### P-I1 (Important): `plant` gives the planted tree no `node_modules`, so `yaml` is unresolvable and `core_may_import_yaml_and_noble_hashes` cannot pass

Handle: plan line 336 (`plant`: "a temporary folder holding package.json …, tsconfig.json, and the files"), line 358 (`not-to-unresolvable`), line 368 (`core_may_import_yaml_and_noble_hashes`).
Probe: a tree in `mktemp -d` with `src/core/index.ts` importing `yaml` and `node:fs`, cruised with the plan's two rules, prints `error not-to-unresolvable: src/core/index.ts → yaml`; with a symlink `node_modules` to the installed packages it prints only `core-imports: … → fs`.
Failure: the builder of Task 3 sees the positive test fail and either weakens `not-to-unresolvable` (forbidden by `CLAUDE.md`, "never loosen a rule") or guesses where to plant.
The same holds for `@noble/hashes` and every planted `npm` case (`core_importing_other_npm_package` would report `not-to-unresolvable`, not `core-imports`, unless the package resolves).
Fix: say in `plant` that the tree gets a symlink `node_modules` to `ts/node_modules` (the probe shows it works inside the sandbox: `mkdtempSync` under `/tmp` plus `symlinkSync` printed `ok`), and that the rules are passed with the planted root as `baseDir` or after `process.chdir`, since dependency-cruiser's rule paths are relative to the working folder.

### P-I2 (Important): the rules do not say whether they bind `src` only or also `tests` and `scripts`, and Task 3's own tests need what the rules forbid

Handle: plan line 350 says `front-door` applies "from `src` or `tests`"; lines 352 to 357 (`core-imports` to `network-confinement`) name packages only; line 290 cruises `src tests`; line 563 adds `scripts`; line 574 has `ts/scripts/differential.ts` read files "outside `src`".
Failure: `plant.ts` writes folders, `parity.test.ts` reads `../tests`, and `repository.test.ts` reads `ts/` itself, all through `node:fs`; if the builder writes `file-confinement` with `from: {}` (no path), `repository_has_no_violations` fails on Task 3's own tests, and Task 12's `differential.ts` fails it again.
If the builder scopes it to `^src/` instead, the guess is right but unrecorded, and a later plan may "fix" it the other way.
Fix: one line in Task 3: every rule except `front-door`, `no-circular`, and `not-to-unresolvable` has `from: { path: "^src/" }`; tests and scripts may use `node:fs`, `node:os`, `node:path`, and `Bun`, and `callViolations` walks `src` only (already line 359).

### P-I3 (Important): no positive case for the confined I/O, so a rule written too broadly passes every Task 3 test and blocks Plans 2 to 4

Handle: plan lines 368 and 369 list only refusals for `child_process_outside_git`, `sqlite_outside_store`, `fs_outside_git_store_and_cli`, `http_outside_api`, `spawn_outside_git`, `file_access_outside_git_store_and_cli`, and `sockets_outside_api`; the Python suite has the positive test `test_confined_io_is_allowed_where_ruled` (`tests/test_structure_io.py:191`), which the plan drops.
Failure: `file-confinement` written as "forbid `node:fs` from every package" passes `fs_outside_git_store_and_cli`, and `repository_has_no_violations` passes too, since plan 1 has no `store`, `git`, or `cli` code (the planner names this risk: `planner-report.md:34`).
Plan 2's builder then meets a failing rule on its first `store` file, and `CLAUDE.md` ("Fix a violation in the code; never loosen a rule") leaves it blocked on an author decision.
Fix: add `confined_io_is_allowed_where_ruled` to `imports.test.ts` and `calls.test.ts`: one planted tree with `node:fs` in `git`, `store`, and `cli`, `node:child_process` and `Bun.spawn` in `git`, `bun:sqlite` and `Bun.file` in `store`, `node:http` and `Bun.serve` in `api`, and `clock.now()` in `app`, asserting no violation.

### P-I4 (Important): the structure rows of the parity table have two contradictory statuses

Handle: plan lines 218 to 225 mark `tests/structure_*.py`, `tests/test_structure.py`, and `tests/test_structure_io.py` "Plan 1, Task 3, changed" with the glob `ts/tests/structure/*.test.ts`; line 365 says "every plan 1 row starts `planned`, and each task flips its rows to `ported`"; line 372 checks `ported_files_exist` and `ported_files_keep_every_python_test_name`; line 556 requires that no plan 1 row stays `planned`.
Failure: if the builder flips the seven structure rows to `ported`, `ported_files_exist` meets a glob that is not a file, and `ported_files_keep_every_python_test_name` fails on 25 Python names with no TypeScript title (`submodule_through_front_door`, `from_lodge_import_package`, `import_inside_function`, `source_that_is_not_utf8_names_the_file`, and others, `grep -n "def test_" tests/test_structure*.py`).
If it marks them `changed`, line 365 and line 556 read as broken, and the schema at line 365 says a `changed` row has no `plan`, while these name plan 1 and Task 3.
Fix: state that the seven rows are `changed` with `plan: 1`, `task: [3]`, the four test files listed by name instead of a glob, and `why` the design line; and that `ported_files_*` apply to `ported` rows only.

### P-I5 (Important): knip does not check what `index.ts` exports, so the dead-code rule the plan states is not enforced at the front door

Handle: plan line 40 ("every export of a module is read by another module or by a test in the task that adds it"); line 304 (`ts/knip.json` with `entry` and `project` only); d-4psbdv (knip "in place of Vulture").
Probe: a scratch project with the plan's `knip.json`, `#core` in `package.json`'s `imports`, and `src/core/index.ts` re-exporting an unused function `unusedFn` and an unused interface `Thread`: `knip` exits 0.
`knip --debug` shows why: package.json's targets become entry files, and `isIncludeEntryExports` is false; with `--include-entry-exports` it reports `unusedFn` and `Thread` in both `index.ts` and `model.ts`.
Failure: every name `core` exports through `#core` escapes the dead-code check, which is nearly all of `core` (Tasks 4 to 11 each list a dozen names); Vulture caught the same case in lodge 0.2.
Turning the option on has a cost the plan must settle too: Task 4 exports `Thread`, `Message`, `ThreadState`, `Raises`, and the other model types (line 389) while its tests read none of them, and Task 6's `builders.ts` would export `treeOf`, first read by Task 11's `applying.ts` (`tests/core/applying.py` imports `tree_of`; no Task 6 test does).
Fix: set `"includeEntryExports": true` in `ts/knip.json` (Task 2), and say in Global Constraints that a task exports through `#core` only the names its own tests or modules read, the rest of a ported module's names following in the task whose tests read them, and a test helper likewise; or keep the option off and say in d-4psbdv that the front door is not checked.

### P-I6 (Important): `ValueError` is one class with subclasses in Python, and the plan makes every exception extend `Error`

Handle: plan line 33 ("an exception becomes a class extending `Error` with the Python name"); line 30 (`pytest.raises(E, match=…)` becomes `toThrow` with the class); line 431 (only `writeRecord` and `writeArea` get "an `Error` named `ValueError`").
Source: `src/lodge/core/yamlio.py:19` (`YamlError(ValueError)`), `src/lodge/core/settings.py:7` (`SettingsError(ValueError)`), `src/lodge/core/search.py:32` (`AmbiguousRef(LookupError)`); 17 `pytest.raises(ValueError…)` in `tests/core` (`grep -n "pytest.raises(ValueError" tests/core/*.py`), raised by `mint_id`, `confirmation_draft`, `write_record`, `write_thread`, and `apply_drafts`, in Tasks 4, 5, 6, 7, and 11.
Failure: each task's builder invents its own `ValueError` (five classes of one name), or `toThrow(Error)` stands in for `toThrow(ValueError)`, which is weaker than the Python assertion (Review Focus 1); and Plan 2's `app`, which turns a `ValueError` from writing into a `LodgeError`, cannot catch one class.
Fix: Task 4 adds `ts/src/core/errors.ts` with `ValueError` and `LookupError` extending `Error`, `YamlError` and `SettingsError` extending `ValueError`, exported through `#core`, and Global Constraints says an exception keeps its Python base class.

### P-I7 (Important): Python's `repr` appears in 15 core messages, and nothing in `text.ts` gives it

Handle: plan line 491 ("Every check message is Python's, character for character"), line 430 ("with the same messages"), line 406 (the duplicate key "in single quotes, as `'title'`"); `grep -n '!r}\|repr(' src/lodge/core/*.py` prints 15 sites in `apply.py`, `fields.py`, `fileformat.py`, `yamlio.py`, and `drafts.py`.
Failure: Python's `repr` of a string picks double quotes when the text holds `'` and no `"`, and escapes every character `str.isprintable` refuses (`'\x85'`, `' '`, `'\x01'`); a builder writing `'${text}'` gets `'it's'` where Python prints `"it's"`, and the message for `unreadable character` differs for every control character.
Five tasks meet it (4, 5, 7, 11, and the YAML layer), so each builder writes its own.
Fix: add `pyRepr(s: string): string` to `text.ts` in Task 4, with `py_repr_matches_python` cases for a plain word, a text with `'`, one with both quotes, `\x01`, `\x85`, ` `, and an astral character; and say in Global Constraints that `{x!r}` becomes `pyRepr(x)`.

### P-I8 (Important): the regular-expression rules miss `^` and `$` under `re.MULTILINE`, which JavaScript's `m` flag reads differently

Handle: plan lines 35 and 36 (the regex rules); `src/lodge/core/threads.py:25` and `:26` (`_ESCAPE`, `_UNESCAPE`, both `re.MULTILINE`), `src/lodge/core/render.py:11` (`_HEADING_LINE`, `re.MULTILINE` with `$`).
Probe: on `"x ## Message 3\ny\r## Message 4\nz"`, Python's `re.sub(r"^\\*## Message [0-9]+$", …, flags=re.M)` changes nothing, and JavaScript's `/^\\*## Message [0-9]+$/gmu` escapes both lines, since its `m` flag treats `\r`, U+2028, and U+2029 as line ends and Python's treats only `\n`.
Failure: `writeThread` and `renderSpec` write text that differs from lodge 0.2's for a message or statement holding a lone CR or U+2028, against line 512 ("byte for byte") and d-smx3xf ("exactly as lodge 0.2 writes it"); the carried tests do not hold such a text, and the differential run reads a store with no threads (`ls lodge/threads` is empty).
Fix: add to Global Constraints: under `re.MULTILINE`, `^` becomes `(?<=^|\n)` and `$` becomes `(?=\n|$)` without the `m` flag, and Python's `.` without `re.DOTALL` becomes `[^\n]`; add U+2028 and a lone CR to Review Focus 2.

### P-I9 (Important): four tasks are two to three times the largest Codex run so far

Handle: Python lines to port, module plus tests (`wc -l src/lodge/core/*.py tests/core/*.py`): Task 5, 682 plus 877; Task 7, 463 plus 780; Task 8, 494 plus 1,189 (nine test files); Task 9, 557 plus 825.
The largest task commit of the viewer build was 1,122 inserted lines including its report (`git log --shortstat` on `68c4572`), and that build's practice review split two tasks for size (`docs/superpowers/plans/done/2026-10-31-lodge-viewer-progress.md:2`, "Tasks 6 and 9 split").
TypeScript with braces and types at Biome's width of 100 runs longer than the Python, so Task 8 is likely past 2,500 lines, and four of its Python test files are already near the 300-line limit (`test_check_state.py` 227, `test_check_compare.py` 190), which adds the splitting work of line 39 on top.
Failure: a run that stops part-way through leaves a half-ported task the coordinator cannot gate, and a review that must compare 1,700 Python lines with their port at once misses weakened assertions, the plan's own first Review Focus.
A split by module does not work for Task 8: `tests/core/checks.py` imports `check_change`, and eight test files import `checks`, `test_check_state.py` among them (`grep -l "from checks import" tests/core/*.py`).
Fix: split by test file instead, and say how test-first reads then.
Task 8a ports the six modules with `checks.ts`, `check-state`, `check-links`, and `check-current`; Task 8b carries `check-change`, `check-compare`, `check-immutable`, `check-retired`, and `check-threads`, whose tests run against code already ported, so the plan says each is seen failing against a named mutation of the code it covers, as the viewer's fix rounds did (`docs/superpowers/plans/done/2026-10-31-lodge-viewer-progress.md:22`).
Task 5 likewise: `drafts.py` and `test_drafts.py` (311 Python lines, importing only `parse_draft` and `record_from_draft`) move to a Task 5b or to the head of Task 6.
Keep Tasks 7 and 9 whole only if the coordinator records in the ledger that it accepts their size.


### P-I10 (Important): the differential run leaves out the writer, which is the part the later plans need byte for byte

Handle: plan lines 569 to 573 (the four keys: `spec`, `problems`, `levels`, `search`); d-smx3xf ("an event … holds the record's path and its whole file text, exactly as lodge 0.2 writes it"); design line 284 (the export "reads like a lodge 0.2 store").
Failure: Plan 2 stores the text `writeRecord` gives, and Plan 4 exports it; a difference in key order, quoting, or the end of the text (for instance `quoted` choosing `JSON.stringify`'s escapes where `json.dumps(…, ensure_ascii=False)` differs, plan line 407) changes every exported file, and nothing in Task 12 would show it, since the carried tests compare written text for a handful of made-up records only (`tests/core/test_fileformat.py:71`, `tests/core/test_thread_files.py:65`).
The store has 192 decisions and 137 files under `lodge/spec/` (`ls lodge/decisions | wc -l`, `find lodge/spec -type f | wc -l`), far more shapes of header than the fixtures.
Fix: add a fifth key, `rewrite`: for every record and area file, whether `write_record(parse_record(path, text))` (or `write_area`) equals the file's text, and the TypeScript side computes the same; any file where the two writers differ is a difference.
Add to Review Focus: "`writeRecord`, `writeArea`, and `writeThread` give lodge 0.2's text byte for byte".

### P-I11 (Important, design fit): build step 1 owns passkeys for one person, and no plan builds a page to use them

Handle: design line 304 ("passkeys come in step 1 … since the server is reachable beyond one machine from the first Funnel"); plan lines 99 to 102 (a setup code, registration, sign-in, a session cookie, and "a token for agents is issued by the signed-in person"); line 82 (Plan 3 ends "when the carried command tests pass against the server and the compiled binary runs them"); the interface is build step 3 (design line 298).
Failure: a passkey is created and used only through `navigator.credentials` in a page served from the relying party's origin, and step 1 serves no page; so after Plan 3 the person cannot register or sign in, cannot issue the first agent token, and the `lodge` command cannot reach the server outside the tests.
The same holds for SRV-2's `approve` (plan line 94): after Plan 2 a person's decision drafted by a session is not current until that person approves it (design line 75), and in step 1 the person has no client to approve with, so every such draft waits until step 3.
Fix: in "Settled for the later plans", give Plan 3 a minimal page served by `api` (register with the setup code, sign in, issue and revoke an agent token, and approve a drafted decision), tested through the handler with the software authenticator; or rule that until step 3 the person acts through `lodge-server` on the server's own machine, and say so in d-yayhct.

## Minor

### P-M1: the committed brief names the worktree's local folder

Handle: `docs/superpowers/plans/2026-11-02-lodge-server-core/planner-brief.md:3` ("in the worktree `/var/tmp/lodge-server-core`"); the planner raised it and repeats the folder (`planner-report.md:37`); `git grep -n "/var/tmp"` finds no other committed file.
Failure: a local machine path in a public repository, against `CLAUDE.md` ("no personal paths, machine names"); it names no person, so the harm is small.
Fix: "in a worktree of its own on branch `server-core`".

### P-M2: Task 12's expected counts do not match the store, and the store has no threads

Handle: plan line 581 ("about 175 decisions, 155 files under `lodge/spec/`, the threads"); at `c3320a4`, `ls lodge/decisions | wc -l` prints 192 (200 after Task 1), `find lodge/spec -type f | wc -l` prints 137 (10 areas), and `ls lodge/threads` is empty.
Failure: a builder told to expect about 175 decisions spends a round on a count that is right; and thread parsing, `newestLast`, and thread problems get no differential coverage at all.
Fix: give the counts as the script prints them without an expected figure, and say that threads are covered by the carried tests only, or add a made-up thread store for the run.

### P-M3: Node runs the gate's tools wherever it is installed

Handle: d-03xx0a ("Node is not used"); plan line 290 (`bun run check` calling `tsc`, `depcruise`, and `knip`, whose bins start with `#!/usr/bin/env node`).
Probe: a bin with a `node` shebang run through `bun run` prints `node` with Node on the path and `bun` without it.
Failure: none today, since both work, but a tool that breaks under one runtime breaks the gate on some machines only.
Fix: `bun --bun run check`, or say in d-03xx0a that the gate's tools run under Node where it is installed.

### P-M4: the software authenticator Plan 3 is told to reuse does not pass strict `tsc`

Handle: plan line 101 ("the software authenticator of `probes/tests/passkey.test.ts`"); the plan's `tsconfig.json` includes `tests` (line 302).
Probe: `tsc --noEmit -p .` in the probe folder prints `tests/passkey.test.ts(37,244): error TS2345: Argument of type 'Uint8Array<ArrayBufferLike>' is not assignable to parameter of type 'Uint8Array<ArrayBuffer>'`.
Fix: note it in "Settled for the later plans" so Plan 3's builder expects a type fix, not a broken probe.

### P-M5: the YAML nesting rule differs from Python in its line and its depth

Handle: plan line 406 and d-458jhp ("nesting deeper than 100 … each a `YamlError` with its line"); `src/lodge/core/yamlio.py:61` and `:62` raise `YamlError("the header is nested too deeply")` with no line, on Python's `RecursionError`, not at depth 100.
Failure: the builder must choose between the ruling (a line) and parity (none); `test_deep_nesting_is_an_error_not_a_crash` may assert either.
Fix: say that the nesting error carries no line, as Python's, and that the depth of 100 is a chosen bound listed as a known difference.

### P-M6: `Bun.TOML.parse` reads `5.0` as the whole number 5, which `tomllib` keeps as a float that lodge 0.2 refuses

Handle: plan line 574 (Task 12 parses `.lodge.toml` with `Bun.TOML.parse`); `src/lodge/core/settings.py:53` refuses a non-`int`.
Probe: `Bun.TOML.parse("[length]\ntitle_chars = 5.0")` gives `{"length":{"title_chars":5}}` and `Number.isInteger` true; `tomllib.loads` gives `5.0`.
Failure: none in Task 12 (this repository's `.lodge.toml` has no `[length]`), but Plan 3's command would accept a setting lodge 0.2 refuses.
Fix: a line in the Plan 3 paragraph; `test_settings.py`'s `tomllib.loads` calls become `Bun.TOML.parse` in Task 4, which the plan does not say either.

### P-M7: Task 1's `where` assumes the coordinator is the session she answered in

Handle: plan line 252 (`where: <the session's name as the coordinator's session shows it>`); the existing author decisions name a session (`lodge show d-3tq6cx --provenance`: "lodge build session").
Failure: a fresh coordinator session cannot know the name and either guesses or writes its own, which then misstates where she said it.
Fix: give the name in the plan, or say that a coordinator which did not hold the conversation asks the author before Task 1.

### P-M8: d-k5swcq sets the whole import table, which `CLAUDE.md` gives to the author

Handle: `CLAUDE.md`, "Structure checks": "Raising a limit or adding an allowed edge is the author's call, recorded as a decision"; d-k5swcq is a planner ruling; `tests/structure_tables.py:5` to `:13` has `gitstore`, `cli`, `viewer`, and `hook`, where the plan has `store`, `git`, `api`, `cli`, and `hook`.
Failure: none if the table only renames lodge 0.2's edges, but the ruling does not say so, and `store` gains file access (plan line 356) that no Python package but `gitstore` and `cli` had.
Fix: say in d-k5swcq's reasoning that each adapter keeps 0.2's edges (`app` and `core`) and which 0.2 package each replaces; or put `store`'s file access to the author.

### P-M9: Review Focus has nothing on the gate itself

Handle: plan lines 67 to 71; Task 3 builds the rules every later plan relies on.
Failure: a rule that passes its refusal tests while refusing too much or too little (P-I3) or a parity check that a glob slips through (P-I4) is not on any reviewer's list.
Fix: a sixth item: "Each structure rule has a refusal and an allowed case, and `parity.test.ts` fails when a ported file loses one Python name".

## Design fit and the cut

The plan carries out the first part of build step 1 (design line 296) and builds nothing a later step owns: `core` only, at parity, with `view` and the viewer tests marked for step 3 (plan lines 200 and 228 to 238), and no runner, MCP server, tasks, or workflow.
The structure table names the packages of step 1 only (`store`, `git`, `api`, `cli`, `hook`, `main`); later steps add theirs, which is an author decision under `CLAUDE.md`, so the table will be reopened at step 3 (the interface) and step 4 (the runner).
The cut into four plans (d-26dx04) is sound in size: Plan 2 ports `src/lodge/app` (1,052 lines, tests 1,481) with four model changes, Plan 3 ports `src/lodge/cli` (627) and the end-to-end tests (1,714) behind the API, and Plan 4 replaces `gitstore` (1,090, tests 1,794) with the importer and the export.
Each plan ends in tested software; only Plan 1's end is a library with a differential run rather than a program, which the brief allows.
What step 1 owns and no plan builds is the person's way in (P-I11).
Task 1 records her answers before any code (d-j3z85y), which matches how the viewer build recorded her quotes (viewer ledger, Task 9a).

## Checked and found sound

- The sandbox: the working folder and `/tmp` writable, home read-only, sockets refused, and the whole TypeScript gate running inside it (probe above), so no task needs a socket, the network, or git's index; Task 2 and Task 1, which do, are the coordinator's.
- The gate's speed: `tsc` 2.6 s, dependency-cruiser 0.4 s, knip 0.3 s, and Biome under 0.1 s on the probe folder; dependency-cruiser's `cruise` runs in process under Bun.
- The `test.todo`s of Tasks 6, 7, and 8: an import scan of `tests/core` finds exactly the five tests the plan names as calling a later task's module (`test_duplicate_id_marks_kept_record_failing`, `test_thread_id_is_not_number_feedback`, `test_confirmed_decision_shows_confirmation_and_keeps_decided_by`, `test_flag_order`, `test_thread_problems_are_visible_in_reads`).
- The parity table: 126 rows, equal to `git ls-files tests | wc -l` and to the files under `tests/` without `__pycache__`.
- `test.each(…)("name %p", …)` and `test.todo` run under `bun test` 1.3.14 as the plan uses them.
- The Python tests import `core` through its front door only, so `#core` is enough for every carried test.

## Files read and not read

Read: `CLAUDE.md`; the plan; its ledger; `planner-brief.md`, `probes.md`, and `planner-report.md`; the server design; the architecture options (lines 1 to 8 and 40 to 66); the viewer plan (lines 1 to 60), its ledger, and `builder-check.md` (head); the 17 rulings through `lodge show`; `src/lodge/core/yamlio.py`, `settings.py` (whole), `fields.py` (118 to 163), and `derive.py` (90 to 110), with greps across `src/lodge/core`; `tests/structure_tables.py`, `tests/structure_rules.py`, `tests/test_structure_io.py` (185 to 206), and `tests/core/test_settings.py` (1 to 30), with greps across `tests/core`; the probe sources' `package.json`, `tsconfig.json`, `.dependency-cruiser.cjs`, and `knip.json`; `scripts/check.sh`, `.gitignore`, `.lodge.toml`, `pyproject.toml` (paths), and `.claude/settings.json`.
Not read: the needs document and the research notes; the viewer build's briefs, reports, and reviews beyond greps; the other core modules in full; `src/lodge/app`, `cli`, `gitstore`, `viewer`, and `hook`, and their tests (sized with `wc` only); the probe sources `passkey.test.ts` and `db.ts` (run, not read); and the sibling review `plan-review-correctness.md`, left unread to keep this one independent.

## Counts

Blocking 0, Important 11, Minor 9.
