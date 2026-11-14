# Task 3 review: the structure rules and the parity table

Range `5966465..471b8ca` (one commit), branch `server-core`.
Reviewer probes and mutations ran in a detached scratch worktree at `471b8ca` (`.claude/worktrees/review-task3`, with `ts/node_modules` hard-linked from the branch's), since the branch worktree already holds uncommitted Task 4 work.
Counts: 1 Blocking, 5 Important, 9 Minor.

## Verified first

- `parity.json` at `471b8ca` matches the plan's `## Parity table` row for row: a script parsing the 126 table rows into `{status, plan, task, ts, why}` and comparing them with the committed file found 0 differences, no extra key, and no duplicate, and the keys equal `git ls-files tests` exactly.
- The gate stays fast: `bun test` in `ts/` runs the 143 tests in 0.65 s wall time, and `bun --bun run check` (Biome, tsc, dependency-cruiser, knip, tests) in 3.1 s.
- `scripts` is bound by the gate today, though not by the gate's `depcruise src tests` line: with a two-file cycle planted in the scratch `ts/scripts/`, `depcruise src tests` reports no violation, while `repository.test.ts` fails with `no-circular: scripts/a.ts -> scripts/b.ts`, since `cruise` (`plant.ts:65-67`) includes `scripts` when it exists; Task 12 adds `scripts` to the `depcruise` line (plan line 728).
- Mutations that the tests kill: dropping the `src` to `tests` rule (`.dependency-cruiser.cjs:4`), the `core` allowed-imports rule (`:5`), the `core` alias rule (`:13`), the `tests`/`scripts` binding of `front-door` (`:12-25`), the `core` type of `app-imports` (`:29`), `sqlite-confinement` (`:31`), `network-confinement` (`:33`), `Date.now` (`calls.ts:84`), the zero-argument `Date` case (`:101`), local time in `app` (`:104`), the `now` rule (`:107`), `missing front door` (`:148`), and the `Sync` variants (`:55`).

## Pass 1: correctness

### B1 (Blocking). A file directly under `src/` escapes every import and purity rule, so `core` can reach the clock through it with the whole gate green

Handle: `ts/tests/structure/calls.ts:141-151` lists only folders under `src`; `ts/.dependency-cruiser.cjs:5-25` forbid targets only inside another package's folder, `src/main.ts`, `tests/`, or `scripts/`.
d-k5swcq says "a relative import never leaves its package", and Python's `package_of` (`tests/structure_tables.py:46-48`) makes a loose `src/lodge/util.py` the unknown package `util`, which `_layout` (`tests/structure_rules.py:47-50`) and `_lodge_edge` (`tests/structure_imports.py:77-78`) both refuse.
Failure scenario, run in the scratch worktree: `ts/src/util.ts` holding `export const t = Date.now() + Math.random(); console.log(process.env);`, `ts/src/core/leak.ts` holding `import { t } from "../util.ts"; export const u = t;`, and `export { u } from "./leak.ts";` appended to `ts/src/core/index.ts`; `bun --bun run check` exits 0 with 143 tests passing.
A Codex builder of Tasks 4 to 11 that puts a shared helper in `src/` beside `main.ts` breaks `core`'s purity, and no check says so.
Fix, verified in the scratch worktree (142 of 142 structure and parity tests still pass): replace the fourteen `front-door` rules at `:12-25` with two group-matching ones,

```js
{name: "front-door", severity: "error", from: {path: "^src/([^/]+)/"}, to: {path: "^src/", pathNot: "^src/$1/", dependencyTypesNot: ["aliased-subpath-import"]}},
{name: "front-door", severity: "error", from: {path: "^(?:tests/|scripts/|src/main\\.ts$)"}, to: {path: "^src/", dependencyTypesNot: ["aliased-subpath-import"]}},
```

which report `front-door: src/core/a.ts -> src/util.ts` and still pass `#core` from `src/main.ts` and `tests/`; and make `layoutViolations` report a `.ts` file directly under `src` other than `main.ts` as `unknown package <name>`, as Python does; with a test for each (`src/core/a.ts` importing `../util.ts`, and a planted `src/util.ts`).

### I1 (Important). Five of the seven `allowed-imports` rules, six of the seven packages' `front-door` rules, and every allowed edge can be deleted or inverted with no test failing

Handle: `ts/.dependency-cruiser.cjs:6-11` and `:14-25`; `ts/tests/structure/imports.test.ts:5-14` plant only a `core` source and a `cli` source; no test asserts that an allowed edge (`app` to `#core`, an adapter to `#app` or `#core`) is clean, since `import_past_front_door` (`:15-23`) asserts only `.some(…front-door…)`.
Review Focus 6 asks for a refusal and an allowed case for each rule.
Mutations, each run against `tests/structure` and `tests/parity.test.ts`, all with 0 failures: deleting the `app`, `store`, `git`, `api`, or `hook` line of `allowed-imports` (`:6`, `:7`, `:8`, `:9`, `:11`); adding `core` to `app`'s forbidden targets at `:6`; adding `app` to `store`'s at `:7`; deleting `app`'s non-index `front-door` rule at `:14`.
Failure scenario: a later edit that forbids `store` importing `#app` passes this task's tests and breaks only when Plan 2 ports `store`.
Fix, prototyped in the scratch worktree as `edges.test.ts` (one planted tree, one cruise, 0.34 s, and it kills all seven mutants above): plant `src/<P>/index.ts` for every package and `src/main.ts`, each importing `#<Q>` for every other package `Q`, and assert that the `allowed-imports` violations equal exactly `{P -> Q : Q not in PACKAGES[P]}` derived from `table.ts`; likewise one tree where every package imports `../<Q>/x.ts` for the `front-door` rules.

### I2 (Important). Nothing pins `no-circular` and `not-to-unresolvable` to `tests` and `scripts`

Handle: `ts/.dependency-cruiser.cjs:26` and `:34` name `^(src|tests|scripts)/`, as the brief requires, but every cycle and unresolvable test plants under `src` (`imports.test.ts:34-45`, `:86-89`).
Mutations narrowing either rule's `from` to `^src/` pass all tests.
Failure scenario: a later "tidy" of the configuration drops `tests|scripts`; a cycle between two test helpers (`tests/core/checks.ts` and `tests/core/builders.ts` are both on the plan) then passes the gate, and Task 12's `scripts/` likewise.
Fix: add a cycle between `tests/a.ts` and `tests/b.ts`, and `import "missing-package"` in `scripts/a.ts`, each asserting its rule.

### I3 (Important). The refusal tests assert "some violation of this rule" where the brief and the Python assert "the one violation named"

Handle: `imports.test.ts:7` and the eighteen like it use `found.some((v) => v.startsWith("<rule>:"))`; `calls.test.ts:158` and `:210` use `.some((v) => v.includes("may not use"))`.
The brief says each test asserts "the one violation named", and Python's `only` (`tests/structure_tree.py:32-33`) asserts exactly one violation containing the fragment (Review Focus 1: `toContain` where Python compares whole values).
Failure scenario, run: changing `calls.ts:77` to report every pure-package global as `core may not use …` passes all 142 tests, so an `app` message naming the wrong package goes unseen; and a refusal tree that also yields a false positive (for example `#core` from `app` flagged) passes `import_past_front_door`.
The calls side also reports duplicates: `Date.now()` in `core` gives `["…core may not use Date.now", "…core may not use Date.now", "…core may not use Date"]`, and `new Date()` in `core` gives `core may not use Date` twice.
Fix: assert whole lists, `expect(found).toEqual(["front-door: src/app/a.ts -> src/core/check.ts"])` and `expect(callViolations(root)).toEqual([`src/${pkg}/a.ts:1: ${pkg} may not use ${name}`])`, after removing the duplicate reports in `calls.ts` (report a `Date.now` or `Math.random` access once, at `:82-86`, and skip the call-level `now` and `Date` checks for a node already reported).

### I4 (Important). `Date(x)` called without `new` reads the clock in `app` and is not reported

Handle: `ts/tests/structure/calls.ts:97-103` exempts a call of `Date` with one argument whether or not it is `new`; JavaScript's `Date(…)` without `new` ignores its arguments and returns the current time as a string.
Run: `export const s = Date("x");` in `src/app/a.ts` gives `callViolations` `[]`.
The brief's wording ("`new Date()` and `Date()` with no argument or with more than one") carries the gap, so this conflicts with the plan and needs a coordinator record (`lodge add`, scope `process`).
Fix: in `core` and `app`, report every call of `Date` without `new`, whatever its arguments, and keep the one-argument exemption for `new Date(x)` only; add `Date("x")` to `core_disallowed_global`'s `app` cases.

### I5 (Important). `cli`, `store`, `api`, and `hook` can write files through `openSync(p, "w")`, `createWriteStream`, `writeSync`, and `Bun.file(p).write(…)`

Handle: `ts/tests/structure/calls.ts:42-56` and `:116`; lodge 0.2 refuses `open(p, "w")` outside `gitstore` (`tests/structure_calls.py:331-371`, `_open_mode`), and d-x6f9za gives `cli` "those of `cli` (reading the drafts it is given)".
Run: `import { openSync, createWriteStream, writeSync } from "node:fs"; const f = openSync("p", "w"); writeSync(f, "x"); createWriteStream("q"); Bun.file("r").write("x");` in `src/cli/a.ts` gives `callViolations` `[]` and no `cruise` violation.
The builder's report lists `test_open_for_writing_outside_gitstore` as not carried "instead" of named writes, so the rule d-x6f9za keeps is lost; the brief's list omits these forms, so this too conflicts with the plan and needs a coordinator record.
Fix: outside `git`, report `createWriteStream`, `write`/`writeSync`/`writev`/`writevSync`, `link`/`linkSync`, and `mkdtemp`/`mkdtempSync` as `file writing outside git`; report `open`/`openSync` (and `fs.promises.open`) whose flags argument is absent from a non-literal or holds `w`, `a`, or `+`, as Python's `WRITE_MODE` does; report a `write`, `writer`, or `delete` call whose receiver is a `Bun.file(…)` call; one refusal case each in `file_writing_outside_git` and `openSync(p, "r")` in `cli` as the allowed case.

### m1 (Minor). `fetch` and `WebSocket` reach the network outside `api` unreported

Handle: `calls.ts:118` names only `Bun.serve`, `Bun.listen`, and `Bun.connect`; `fetch` is banned only in `core` and `app` (`:21`).
Run: `await fetch("http://x");` in `src/cli/a.ts` gives `[]`.
lodge 0.2 had no network rule, so this is a gap in the new rule rather than a lost one.
Fix: report `fetch` and `new WebSocket` outside `api` as `sockets outside api`, unless the coordinator rules that `cli` may call the server.

### m2 (Minor). Object keys and interface members named like a banned global are reported in `core` and `app`

Handle: `calls.ts:74-77` skips only the name of a property access.
Run: `export const o = { process: 1, console: 2 }; export interface I { readonly fetch: string }` in `src/core/a.ts` gives four `core may not use …` lines.
No field in `src/lodge/core` or `src/lodge/app` has such a name today (`grep -nwE 'process|crypto|fetch|performance|console|navigator' src/lodge/{core,app}/*.py` finds only text and the value `"process"`), so nothing fails yet.
Fix: skip an identifier that is the `name` of a property assignment, property signature, property declaration, method, or binding element's property name.

### m3 (Minor). Three layout and size branches have no test

Handle: `calls.ts:147` (`|| pkg === "main"`, so a folder `src/main/` is unknown) and `:128` (`scripts` in `sizeViolations`): deleting either passes every test, run.
`layout.test.ts:160-167` runs `tests/core/a.ts` twice, once in `oversized_module %p` and once in `oversized_test`, where the brief puts `src/core` in the first and `tests/core` in the second.
Fix: `oversized_module` on `src/core/a.ts` only, a `scripts/a.ts` case in `oversized_test` (`test.each`), and `unknown_package` also on `src/main/index.ts`.

## Pass 2: practice

### m4 (Minor). The `test:structure` script in `ts/package.json` serves only the builder

Handle: `ts/package.json:10`; the brief names `ts/package.json` under Modify with "no new dependency" and no change, the gate never runs the script, and the brief's Step 2 command is `cd ts && bun test tests/structure tests/parity.test.ts`.
Failure scenario: none at run time; a second way to run a subset invites drift once `tests/structure` gains a file the script's paths miss.
Fix: remove the line, so that `ts/package.json` is as Task 2 left it.

### m5 (Minor). `.dependency-cruiser.cjs` mixes two styles, runs to about 200 characters a line, and is checked by no formatter

Handle: `ts/.dependency-cruiser.cjs:4` has bare keys, `:5-36` quoted keys; `ts/biome.json`'s `files.includes` has no `*.cjs`, so Biome never sees it, and Task 2's version of the file had Biome's spacing.
Fix: with B1's two `front-door` rules the file shrinks by twelve lines; generate the seven `allowed-imports` rules from one object in the file (`Object.entries({core: [...], ...}).map(...)`) and lay it out as Biome would, or add `*.cjs` to Biome's includes.

### m6 (Minor). Two titles are each defined twice instead of through `test.each`

Handle: `imports.test.ts:46` and `:50` (`core_importing_node_builtin`), `:74` and `:78` (`fs_outside_git_and_cli`).
The plan's porting rule writes a test with several cases as `test.each(cases.map((c) => [c]))("name %p", …)`; two `test` calls with one title make Bun's output ambiguous about which case failed.
Fix: `test.each([["src/core/a.ts", "node:fs"], ["src/core/a.ts", "fs"]])("core_importing_node_builtin %p %p", …)`, and likewise for the other.

### m7 (Minor). The parity row loop is not what `a_ported_file_losing_a_name_fails` exercises

Handle: `parity.test.ts:84-93` inlines the row loop and shadows `p` at `:90`; `:99-103` checks `missingNames` on two literal strings, not "the check on a made-up row" the brief names.
At `471b8ca` no row is `ported` (0 of 126), so the loop body has never run; a wrong path join there first surfaces in Task 4.
Fix: extract `rowMissing(root, pythonPath, row)` into `parity-names.ts`, call it from both tests, and feed the made-up row through it with a planted pair of files.

### m8 (Minor). The builder's report lists fixture strings as test titles

Handle: `task-3-report.md`, section `ts/tests/parity.test.ts`, lists `a`, `c %p`, `no`, and `real %p` as tests with first failures; they are strings inside `parity_names_read_both_languages` and `parity_names_ignore_non_test_calls` (`parity.test.ts:108` and `:115`).
Fix: none to the code; the ledger line need not repeat the count.

## Pass 3: design

### m9 (Minor). `PACKAGES` and `CORE_NPM` are not the source of the rules they name

Handle: `table.ts:1-11`; `layoutViolations` reads only `PACKAGES`'s keys (`calls.ts:147`), and the edges and the two npm names are written a second time, by hand, in `.dependency-cruiser.cjs:5-11` and `:28`.
CLAUDE.md makes adding an allowed edge the author's call, recorded as a decision; after this task such a decision needs two edits that nothing checks against each other.
Fix: I1's table-driven test makes `table.ts` the checked source of the edges; a test that `core` importing each `CORE_NPM` name is clean (as `confinedTree` already does at `imports.test.ts:96-98`) and that a third name is refused does the same for `CORE_NPM`.

Further design checks with no finding: the brief's interfaces match the exports (`plant`, `cruise`, `callViolations`, `sizeViolations`, `layoutViolations`, `pythonTestNames`, `typescriptTestTitles`, `todoTitles`; `missingNames` is an extra export that `parity.test.ts` reads, so knip accepts it); `plant` copies `devDependencies` as well as `dependencies`, which makes `typescript` an `npm-dev` import that `core-imports` (`:28`) refuses, as in `ts/`; the structure rules bind `ts/src` alone for calls and confinement, as d-x6f9za says.

## Files read

Read: `task-3-brief.md`, `task-3-report.md`, `task-3-codex-final.txt`, the whole diff (`ts/.dependency-cruiser.cjs`, `ts/package.json`, `ts/tests/structure/{table,plant,calls}.ts`, `ts/tests/structure/{imports,calls,layout,repository}.test.ts`, `ts/tests/parity-names.ts`, `ts/tests/parity.test.ts`, `ts/tests/parity.json` by script); `ts/biome.json`, `ts/knip.json`, `ts/tsconfig.json`, `scripts/check-ts.sh`; the plan's `## Parity table`, `## Review Focus`, and line 728; `tests/structure_rules.py`, `tests/structure_tables.py`, `tests/structure_tree.py`, `tests/structure_imports.py`, `tests/structure_calls.py`; d-x6f9za, d-k5swcq, and LODGE-5 through `lodge show`.
Not read: the bodies of `tests/test_structure.py` and `tests/test_structure_io.py` beyond `test_unknown_package` and `test_root_imports_nothing` (their 38 names were taken from the builder's report and `grep -c 'def test_'`); the plan's other task sections; the design documents.
