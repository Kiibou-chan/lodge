# Task 3 recheck 1

Range `b0c6f0c..30557fe`, branch `server-core`.
Probes ran in a detached scratch worktree at `30557fe` (removed since), with `ts/node_modules` linked from the branch's.
Result: 15 of 15 findings closed, 0 open, no new Blocking or Important.
The gate (`bun --bun run check` in `ts/`) passes at `30557fe`: 259 tests.

## Per finding

- B1 closed: a planted `src/util.ts` with `src/core/leak.ts` importing `../util.ts` now gives `front-door: src/core/leak.ts -> src/util.ts` from `depcruise` and a failing `repository_has_no_violations`; the rules are `ts/.dependency-cruiser.cjs:25-40`, the layout rule `ts/tests/structure/calls.ts:187`.
- I1 closed: `ts/tests/structure/edges.test.ts` kills these mutants, each with failures: `app` omitted from the group `front-door` rule (4 fail), `hook` dropped from the package list (1), `app` forbidden from `#core` in the generator (4) and in `table.ts` (3), `api` allowed `cli` (1).
  Removing `app` from `store`'s entry in `table.ts` passes by construction, since the config and the test both read `table.ts`; that table is now the single source, which is what m9 asked for.
- I2 closed: narrowing `no-circular` or `not-to-unresolvable` to `^src/` fails 2 tests each (`.dependency-cruiser.cjs`).
- I3 closed: no `.some(` remains in `tests/structure/*.test.ts`; `Date.now()` and `new Date()` in `core` give one report each; changing `calls.ts:96` to a fixed `core` name fails 13 tests.
- I4 closed: `Date("x")` in `app` gives `app may not use Date`, `Date()` likewise, `new Date(1)` stays clean; `core` refuses all three (ruling d-mfskz3 applied).
- I5 closed: the review's probe now gives four `file writing outside git` reports; also reported are `openSync` with absent, non-literal, or `r+` flags, `fs/promises` `open("p","w")`, `fs.promises.open`, `writevSync`, `linkSync`, `mkdtempSync`, `Bun.file(…).writer()` and `.delete()`, and an aliased `Bun.file` receiver; `openSync("p","r")` is clean.
- m1 closed: `fetch` and `new WebSocket` give `sockets outside api` in `store` and `git`, nothing in `cli`, `hook` (and `api`), per d-s5s2c3.
- m2 closed: `{ process: 1 }` and a renamed destructuring property are not reported, while `process.env` still is (`calls.ts` property-name skip).
- m3 closed: dropping `scripts` from `sizeViolations` (`calls.ts:164`), dropping `src` from it, and dropping `|| pkg === "main"` (`:187`) each fail 1 test.
- m4 closed: `ts/package.json` no longer holds `test:structure`.
- m5 closed: the file has no line over 100 characters and builds its rules from `PACKAGES` and `CORE_NPM` (`.dependency-cruiser.cjs:1-2`).
- m6 closed: `imports.test.ts:50` and `:84` are `test.each`.
- m7 closed: `rowMissing` is exported from `parity-names.ts` and both the row loop (`parity.test.ts:45`) and the made-up row (`:57`) call it.
- m8 closed: `task-3-report.md` no longer lists the four fixture strings.
- m9 closed: see I1; `CORE_NPM` mutations are reported killed by the builder and the `core-imports` rule reads `CORE_NPM` (`.dependency-cruiser.cjs`), which I did not re-run.

## New problems

None Blocking or Important.
`missingNames` is no longer exported, and `rowMissing` throws if a row's `ts` file is absent; Task 4 onward will see that as a failing parity test, which is the intended outcome.
