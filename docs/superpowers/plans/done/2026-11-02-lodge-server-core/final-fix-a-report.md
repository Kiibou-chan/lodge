# Final fix A report

DONE_WITH_CONCERNS.
No production files, dependencies, records, commits, or network were changed.

## Findings

- d-d0vca9 and F-4: resolve named, renamed, namespace, default, and `promises` imports from all four fs module names.
  The four descriptor write functions require an fs import; other write names also resolve renamed imports.
  Namespace calls are treated as the same fs function, as the brief requests.
  Direct `Bun.file(...).write`, `.writer`, and `.delete` remain refused.
  The four existing cli descriptor-write fixtures now import from fs.
  `file_import_resolution` covers renamed and namespace calls, stdout, stderr, arbitrary port methods, and unimported write names.
  Before implementation: `(fail) file_import_resolution "import { writeFileSync as save } from \"node:fs\"; save(p, x)"`, likewise renamed `writeSync`, stdout/stderr, and `port.write` cases.
  Explicit main, api, and app allowed cases also cover the final review's receivers.
- d-4vhjtt: missing flags mean read; literal `r` remains allowed, and dynamic, `w`, `a`, and `r+` flags remain refused.
  Renamed fs open imports resolve to their original function name.
  Before implementation: `(fail) file_import_resolution "import { openSync } from \"node:fs\"; openSync(p)"` and `(fail) file_import_resolution "io.open(data)"`.
- F-2: ban self, global, window, immediate timers, and browser prompts, and report import.meta in core and app.
  Tests cover the requested process, randomness, crypto, and environment forms, with property names allowed.
  Before implementation: `(fail) new_purity_globals "core"` and `(fail) new_purity_globals "app"`.
- 11-D-1: chose a structure rule over behavioural tests at the two catch sites.
  Every src catch must begin with a negated instanceof guard against a named class and rethrow the same caught identifier.
  Tests refuse missing guards, missing catch bindings, and throwing a different value; the standard ValueError guard is allowed.
  Before implementation: `(fail) guard_and_result_construction "try {} catch (e) { return e; }"`, with the missing binding and wrong thrown identifier also failing.
- Task 3 parked Minor: `table.test.ts` already contains `package_edges_match_ruling`, pinning every PACKAGES row and CORE_NPM exactly to d-k5swcq.
  Kept that existing test and proved it detects a wrong edge by temporarily adding app to core's imports.
  Output: `(fail) package_edges_match_ruling`, `0 pass`, `1 fail`.
  Restored the table immediately afterwards.
- 8afix-D-2: chose the review's proposed structure rule refusing object literals with an ok key outside src/core/check-state.ts.
  Tests cover plain and computed string keys, allow checkResult calls, and allow the constructor's own literal.
  Before implementation: `(fail) guard_and_result_construction "const r = { problems, notes, ok: true }"`, with the computed-key case also failing.
  This is the review's syntactic check, not type-aware detection of spread copies or aliases.
- F-6: enforce Unicode flags, no multiline flag, and no Python shorthand escapes in regex literals and literal-string RegExp construction in core/app.
  Escaped backslashes are allowed; dynamic patterns are not statically inspected.
  Before implementation: seven `portable_patterns` failures, including `/a/`, `/a/mu`, `/a\\s/u`, and `new RegExp("a")`.
  Default-sort enforcement remains open: three current calls in apply.ts and apply-areas.ts would fail it, and fixing those files is outside this brief's permitted scope.
  A clean check therefore needs those source fixes first; no baseline or exemption was added.

## Test-first evidence and commands

All refusal additions were run against the original rules before their implementation.
Allowed additions which already passed were tested with a temporary mutation that reports every source file, then that mutation was reverted.
Its last run ended `17 pass`, `142 fail`, `185 expect() calls`, including the allowed regexes, correct catch, checkResult calls, constructor literal, and explicit main/api/app receivers.
This mutation checks the allowed assertions' sensitivity; it does not model a particular production regression.

- `uv run --frozen --quiet lodge waiting`: nothing waiting for either agent or author.
- `uv run --frozen --quiet lodge show <id> --reasoning`, for d-d0vca9, d-4vhjtt, d-k5swcq, d-qe513h, and d-snrhjs: all read successfully.
- `cd ts && bun test tests/structure/calls.test.ts`, initial red run: `132 pass`, `13 fail`, `145 expect() calls`.
- Same command, regex red run: `148 pass`, `7 fail`, `181 expect() calls`.
- `cd ts && bun test tests/structure/table.test.ts`, wrong-edge mutation: `0 pass`, `1 fail`.
- `cd ts && bunx --no-install biome check --write tests/structure`: `Checked 10 files in 23ms. Fixed 3 files.`
- `cd ts && bun test tests/structure`: `200 pass`, `0 fail`, `230 expect() calls`, across 6 files.
- Final command: `sh scripts/check-ts.sh`, result recorded below.

Final gate exited 0.
Last lines: `886 pass`, `0 fail`, `2223 expect() calls`, `Ran 886 tests across 57 files. [4.30s]`.
Biome checked 107 files without fixes; dependency-cruiser found no violations across 116 modules and 374 dependencies; tsc and knip passed.
