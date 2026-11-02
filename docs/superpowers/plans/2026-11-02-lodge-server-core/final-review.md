# Plan 1: final whole-branch review

Branch `server-core` at 1e80e61, range 5966465..1e80e61, reviewed in a scratch worktree at the same commit.

## Counts

0 Blocking, 3 Important (F-1 to F-3), 3 Minor (F-4 to F-6); none repeats a parked finding.
The two rulings for the fix wave, d-d0vca9 and d-svv7gv, are worked out under their own heading below, with F-1, F-3, and F-4 feeding them.

## Gate and differential

`sh scripts/check.sh` at 1e80e61 in the scratch worktree: exit 0; Python 1,399 passed; the TypeScript gate green, Biome 106 files, dependency-cruiser 115 modules and 372 dependencies, knip clean, `bun test` 853 pass, 0 fail, 2,164 `expect()` calls across 57 files.
`sh scripts/differential.sh`: "353 records, 10 areas, 0 threads, 0 problems, 113 queries, 363 rewritten files", "0 differences", exit 0.
The ledger's Task 12 line reads 350 records and 360 rewritten files; the three more are the records added since (d-d0vca9, d-snrhjs, and the d-4zg8q3 replacement), not a change in the comparison.

## Findings

### Blocking

None.

### Important

#### F-1 · Important · the call rule calls any `open(…)` without a write flag a file write, so plan 3's `serverCommand` fails the gate

Handle: `ts/tests/structure/calls.ts:137-139`, `writingOpen` is true for any callee named `open` or `openSync`, on any receiver, whenever the second argument is missing or not a string literal.
Plan 3 declares `ServerIo.open: (data: string) => Promise<ServerParts>` and has `api`'s `serverCommand` call it (plan 3 at 8f02776, `docs/superpowers/plans/2026-11-02-lodge-server-api.md:424-430` and `:585` on `server-api`; plan 4 builds on it, at a64d512, `docs/superpowers/plans/2026-11-02-lodge-server-import.md:84` and `:466` on `server-import`).
Failure scenario, run in the scratch worktree with `callViolations` on a planted tree: `src/api/a.ts` holding `await io.open('data')` gives `src/api/a.ts:1: file writing outside git`; plan 3's builder meets a red gate on a port call, as plan 3's B-1 did on `process.stdout.write` before d-d0vca9, and either renames the port or loosens the rule.
The same rule refuses a read in `cli`, which d-x6f9za lets read files: `openSync('p')` and `promises.open('p')` (both default to the flag `r` in Node's `fs`) each give `file writing outside git`.
And the `writes` set (`calls.ts:43-62`) matches `link`, `cp`, `rm`, `truncate`, `copyFile`, `appendFile`, `mkdtemp`, and `symlink` on any receiver, where lodge 0.2 matches only its pathlib method names on any receiver and the rest only as `os.<name>` (`tests/structure_calls.py:14-38`, `:171`); `s.rename('x'); s.link('y')` on a port in `app` gives two findings.
Fix: in the fix wave's change for d-d0vca9, give `open` and `openSync` the shape d-d0vca9 gives `write`: reported only as an `fs` function (a name imported from `fs`, `node:fs`, `fs/promises`, or `node:fs/promises`, or a property of such a namespace or of `promises`), and only with a flag argument that is not a string literal or that holds `w`, `a`, or `+`; a missing flag is `r`.
This narrows d-d0vca9's text, so it needs the coordinator's ruling; the cheaper alternative is for plan 3 to rename `ServerIo.open`, which leaves the `cli` read refused.
Tests: `io.open('data')` in `api` and `openSync('p')` in `cli` pass; `openSync('p', 'w')` in `cli` and `open(x)` imported from `node:fs` with flag `"a"` in `api` are refused.

#### F-2 · Important · `import.meta.env`, globals reached through `self` or `global`, and `setImmediate` pass the purity rule in `core` and `app`

Handle: `ts/tests/structure/calls.ts:15-29` (the `banned` set) and `:95` (an identifier is reported only when it is not a property name).
Review Focus 5 asks for "a global the structure test does not name"; the plan's Global Constraints say `core` and `app` use no clock, randomness, process, or timer.
Failure scenario, each run with `callViolations` on a planted tree, each giving no finding: in `core`, `import.meta.env.TZ`, `self.process.env.TZ`, `global.process`, `self.Math.random()`, `self.crypto.getRandomValues(…)`, `setImmediate(…)`, and `prompt('x')`; in `app`, `self.Date.now()`.
Bun 1.3.14 gives `self` and `global` as objects and reads the environment through both `import.meta.env` and `self.process.env` (`FOO=bar bun -e 'console.log(import.meta.env.FOO, self.process.env.FOO)'` prints `bar bar`), so a plan 2 builder reading a setting with `import.meta.env` in `app` passes the gate.
No such use is in `ts/src` today (`grep -rnE 'import\.meta|\bself\b|\bglobal\b|setImmediate' ts/src` finds nothing).
Fix: add `self`, `global`, `window`, `setImmediate`, `clearImmediate`, `prompt`, `alert`, and `confirm` to `banned`, and report an `import.meta` meta-property (`ts.isMetaProperty`) in `core` and `app`; one refusal per name in `calls.test.ts`'s first `test.each`, and `property_names_are_not_globals` gains `{ self: 1 }` as an allowed case.

#### F-3 · Important · four packages locked in `ts/bun.lock` were under two weeks old when Task 2 locked them (d-svv7gv)

Handle: `ts/bun.lock:249` (`unbash@6.0.3`, published 2026-11-01T08:58Z, a dependency of knip), `:131` (`@types/node@26.6.6`, 2026-10-28T18:36Z, of `bun-types`), `:245` (`tslib@2.9.1`, 2026-10-30T20:20Z, of `@emnapi/*` and `@tybys/wasm-util`), and `:45` (`@napi-rs/wasm-runtime@1.2.6`, 2026-10-25T08:00Z, of the wasm32 binding of `oxc-resolver`); the lock was committed at 5966465, 2026-11-02T17:05:45+01:00, so the cut is 2026-10-19T16:05:45Z.
Evidence: the publication time of each of the 121 locked versions, read one request a second from `https://registry.npmjs.org/<name>`'s `time`, 117 older than the cut, these four younger, none unanswered; the two packages `core` imports, `yaml@2.9.1` and `@noble/hashes@2.4.0`, and every package `ts/package.json` names, are older (knip 6.42.0, the youngest named, 2026-10-18T13:44Z).
Failure scenario: d-4psbdv's reason, time for a bad release to be pulled, does not hold for these four; `unbash` runs inside knip in every gate, and `@types/node` types every file; plan 3's `bunfig.toml` setting governs resolution, so a lock line already present is kept by plans 2 to 4 unless re-resolved (not verified on Bun 1.3.14).
Fix: add `ts/bunfig.toml` with `[install]` `minimumReleaseAge = 1209600` now rather than in plan 3, re-resolve the four (remove their entries from `ts/bun.lock`, then `bun install`; Bun 1.3.14 with the setting picked `tslib` 2.8.1 for plan 3, d-svv7gv), confirm `bun install --frozen-lockfile` is clean and the gate green, and list each re-resolved version with its publication date in the ledger line.

### Minor

#### F-4 · Minor · a renamed `fs` import passes the file-writing rule

Handle: `ts/tests/structure/calls.ts:147`, which matches the callee's own text (`writes.has(attr)`), so an import renamed at its specifier is not seen.
Failure scenario, run with `callViolations` on a planted tree: `import { writeFileSync as save } from 'node:fs'; save('p', 'x')` in `src/cli/a.ts` gives no finding, and `import { writeSync as w } from 'node:fs'; w(1, 'x')` likewise; `cli` is the one package besides `git` that may import `fs` (`ts/.dependency-cruiser.cjs`, `file-confinement`), and it writes no file (d-x6f9za).
Fix: the change d-d0vca9 asks for already has to know which names come from `fs`; build that map from the file's import declarations of `fs`, `node:fs`, `fs/promises`, and `node:fs/promises` (local name to `propertyName ?? name`, plus namespace and default imports), and test every name of `writes` against the imported name rather than the local one; add `writeFileSync as save` in `cli` to `file_writing_outside_git`.

#### F-5 · Minor · `isDigit`'s Unicode digit branch is pinned by no test

Handle: `ts/tests/core/text.test.ts:54-57` tries `12`, `²`, and `①`; the first is ASCII and the other two come from `DIGIT_RANGES` (`ts/src/core/text.ts:42-63`), so the `\p{Nd}` test at `text.ts:69` is reached only by ASCII digits.
Failure scenario, run in the scratch worktree: replacing `/\p{Nd}/u` with `/[0-9]/u` at `text.ts:69` leaves all 853 tests green; `related` (`ts/src/core/search.ts:77`) would then keep `٣` as a query word where lodge 0.2 drops it (`'٣'.isdigit()` is `True`).
Fix: add `٣` (U+0663) and `𝟙` (U+1D7D9) to the true cases of `is_digit_like_python`; both are `True` in Python 3.13.5 and `true` in TypeScript today.

#### F-6 · Minor · the plan's rules for patterns and sorting are held by no check

Handle: the Text constraint (`docs/superpowers/plans/2026-11-02-lodge-server-core.md`, Global Constraints, "Text": every pattern has the `u` flag; `\s`, `\w`, `\d`, and `\b` are rewritten; no `m` flag; strings sorted by code point) is enforced neither by `ts/tests/structure/calls.ts` nor by Biome's recommended preset (`ts/biome.json`).
Failure scenario, run in the scratch worktree: a file `src/core/zz-probe.ts` holding `export const R = /a\s+b/;` and `[...xs].sort()` passes `biome check --error-on-warnings`, and `callViolations` has no rule for either, so a plan 2 builder porting `app` (bound by the same Text rule) can write Python's `\s` as JavaScript's, which differs at U+001C to U+001F, U+0085, and U+FEFF (run here over every code point: Python's `str.isspace` holds 29, JavaScript's `/\s/u` 25, and `isPySpace` the same 29 as Python only because `text.ts` spells the class out).
`ts/src/core` complies today: no regular expression without `u` and no `\s`, `\w`, `\d`, or `\b` escape (`grep -nE '\\\\?\\[swdbSWDB]' ts/src/core/*.ts` finds none); the three default sorts are parked as 11-P-2.
Fix: a call rule over `ts/src/core` and `ts/src/app` that reports a regular expression literal or a `new RegExp` whose flags lack `u` or hold `m`, a pattern text holding `\s`, `\w`, `\d`, or `\b`, and a `.sort()` or `.toSorted()` called without a comparator, each with a refusal and an allowed case in `calls.test.ts`.

## What the coordinator's rulings need in the code

### d-d0vca9, the file-writing rule

`ts/tests/structure/calls.ts:43-62`: take `write` and `writev` out of the names `writes` is built from, which also removes `writeSync` and `writevSync`.
`calls.ts:144-148`: report those four only when the callee is a name imported from `fs`, `node:fs`, `fs/promises`, or `node:fs/promises` (resolving a renamed specifier, F-4); the ruling's text, "functions called by name", leaves `fs.writeSync(fd, x)` on a namespace import unreported, and since `cli` may import `fs`, the fix should treat a property of a namespace or default import of those modules as the same function and say so in the ledger.
`bunFileWrite` (`calls.ts:140-143`) already reports `.write`, `.writer`, and `.delete` on a `Bun.file(…)` call, and `Bun.write` stays reported by name (`:147`).
After the change, `const f = Bun.file(p); f.write(x)` in `cli` passes, which the ruling's cost if wrong accepts; reporting those three methods on an identifier whose declaration is initialised with `Bun.file(…)` in the same file closes it for one more condition.
`ts/tests/structure/calls.test.ts:150-153` (`write(x)`, `writeSync(x)`, `writev(x)`, `writevSync(x)` in `cli`, no import) must gain `import { write, writeSync, writev, writevSync } from "node:fs";`, or under the import-resolving fix they pass and the test fails; the `git` case of `confined_calls_are_allowed_where_ruled` (`:198-199`) stays allowed either way.
New cases: refused, `import * as fs from "node:fs"; fs.writeSync(1, x)` in `cli`; allowed, `process.stdout.write("x")` in `cli` and in `src/main.ts`, `process.stderr.write("x")` in `api`, and `port.write(x)` in `app` (each refused today, run with `callViolations`: `src/main.ts:1: file writing outside git`, `src/cli/a.ts:1: …`, `src/app/a.ts:1: …`).
F-1 asks the same shape for `open` and `openSync`, under a ruling of its own.

### d-svv7gv, the release age of every locked package

The check is done here (F-3): 4 of 121 locked versions fail it, all development tooling, none in `core`'s two dependencies.
What the code needs: `ts/bunfig.toml` with `[install]` and `minimumReleaseAge = 1209600`, the four re-resolved in `ts/bun.lock`, and the ledger line listing the new versions and their dates; plan 3's setup task then finds the file present and adds nothing.
The registry reads are one request a second over 120 package names; the script and its output are in the reviewer's scratch folder, not the repository.

## Across the branch

### Review Focus 1 to 7

1. Carried tests: every parametrised Python test of `tests/core` (42, read with Python's `ast`, `HEADER_EDITS`'s 14 counted by importing the module) has as many TypeScript cases under its name as Python has (`bun test tests/core --reporter=junit`, titles counted by prefix); none differs.
2. Text: `isPySpace` and Python's `str.isspace` agree on all 1,112,064 scalar values (29 each), and `splitLines` breaks where Python's `splitlines` breaks (10 each); 14 targeted mutations of `text.ts`, `stamps.ts`, `yamlio.ts`, and `render.ts` (UTF-16 order, U+2028, U+0085, CRLF, `trim`, code-unit length, the repr quote, the sigma, the `m` flag on headings) each turn a test red, except the `isDigit` one (F-5).
3. YAML: a `!!str` tag on a sequence allowed, the keys walked in reverse, and `quoted` without escapes each fail tests (1, 3, and 5 failing tests).
4. Stamps: `+00:60` accepted, `+23:60`, `T24:00:00`, `:60` seconds, and `2026-02-30` refused, nine stamps accepted or refused as Python's `datetime.fromisoformat` does, with equal instants on the five both accept, and the output identical under `TZ=UTC`, `Pacific/Kiritimati`, and `America/St_Johns`; the same-second tie by ID, the offset sign, and the bare day's midnight UTC each fail tests when mutated.
5. Purity: no clock, randomness, or environment reaches `core` today through a default parameter or a module constant (the one computed constant, `NEVER` at `ts/src/core/search.ts:10`, is `orderInstant` of a fixed stamp); the gate's gaps are F-2.
6. The gate: removing one carried name from a ported file fails `ported_files_keep_every_python_test_name`, and removing `isAuthor` from or adding `sortKey` to `ts/src/core/index.ts` fails the matching front-door test; the call rules' gaps and false refusals are F-1, F-2, and F-4, and the unchecked Text rules F-6.
7. Writers: the differential above rewrote 363 files with 0 differences; the thread writer's coverage is parked as 12-D-1.

### Seams between the lanes

The merges that resolved conflicts (632c9eb and 4e20c28 in `ts/knip.json` and `ts/src/core/index.ts`, d625cf3 in `ts/tests/parity.json`) kept both sides; `ts/knip.json`'s `entry` is back to Task 2's two patterns, and knip is clean.
The duplicated helpers across lanes are all parked already: two private `byCodePoint`s (`snapshot.ts:35`, `threads.ts:162`; Task 6 P-1), three structural `equal`s (`check-entries.ts:8`, `check-immutable.ts:10`, `fileformat.ts:90`; 8b-P-1), the problem comparator (8b-P-2), and the three default sorts (11-P-2); `valueRepr` is one module (`value-repr.ts`) used by `apply.ts`, `drafts.ts`, and `fileformat.ts`.
Every `catch` in `ts/src/core` (9) rethrows any other class on its next line.

### The front door and the parity table

`ts/src/core/index.ts` exports every name of `__all__` of `src/lodge/core/__init__.py` in camelCase, the ten constructors d-ca6wbw and d-snrhjs allow, and the names of `errors.ts`, `text.ts`, and `stamps.ts`, and nothing else; `quoted`, `unreadableChar`, `LINE_BREAKS_AND_TABS`, and `FormatError` stay inside.
`ts/tests/parity.json`: 40 `ported` rows of plan 1, every `tests/core` file among them, each TypeScript file present; 7 `changed` rows of plan 1, the structure rules; the 40 `planned` rows name plans 2 to 4; no plan 1 row is `planned`.

### Names plans 2 to 4 consume

Each name the three plans take from plan 1 exists with the signature they give: plan 2 at 0244e79 (`instant`, `isStamp`, `tree`, `load`, `pyRepr`, `parseCoreSettings`, `SettingsError`, `ValueError`, `writeThread(thread)`, `newestLast` ascending, `checkChange(…, now)` with a stamp, `Derived.awaitingAuthor`, `CORE_NPM` in `ts/tests/structure/table.ts`, and `filesOf` and `at` of `ts/tests/core/builders.ts`); plan 3 at 8f02776 (`filters`, `Filters`, `Scope`, `Raises`, `pyRepr`, `parseCoreSettings`, `CoreSettings`, `compareStamps`, `parseDraft(source, text)`, `recordFromDraft(draft, id, date, area)`, `formatLevel1`, `formatLevel3`, `WORD_CLASS`, and the handles `ts/src/core/headers.ts:56,61` and `withId` of `drafts.ts`); plan 4 at a64d512 (`checkChange(published, after, settings, now)`, `checkState`, `load`, `tree`, `parseCoreSettings`, `parseRecord`, `writeRecord`, `parseThread`, `writeThread`, `CoreSettings`, `Problem`, `problem`, `ATTACHMENTS`).
The one seam that fails is not a name but a call rule: plan 3's `ServerIo.open` (F-1).
Plan 3 and plan 4 were committed again during this review (`server-api` 9ac93ac to 8f02776, `server-import` cbedab8 to a64d512); the handles above are from the later commits.

## Files read and not read

Read whole: `CLAUDE.md`; the plan's header, Global Constraints, Calls made, Review Focus, and the later-plan sections (`docs/superpowers/plans/2026-11-02-lodge-server-core.md:1-140`); the ledger; `ts/src/core/index.ts`, `text.ts`, `stamps.ts`; `ts/tests/structure/calls.ts`; `ts/tests/parity.test.ts`, `ts/tests/parity-names.ts`, `ts/tests/core/front-door.test.ts`; `ts/package.json`, `ts/knip.json`, `ts/tsconfig.json`, `ts/biome.json`, `ts/.dependency-cruiser.cjs`; `scripts/check.sh`, `scripts/check-ts.sh`, `scripts/differential.sh`; `src/lodge/core/__init__.py`'s `__all__`; d-d0vca9 and d-svv7gv with their reasoning.
Read in part: `ts/src/core/snapshot.ts:1-30`, `apply.ts:15-25`, `apply-areas.ts:30-72`, `check-change.ts:15-30`, `drafts.ts:28-72`, `fields.ts:115-170`, `fileformat.ts:66-80`, `derive.ts:1-40`, `headers.ts:50-64`, `yamlio.ts:1-160`, `threads.ts` (signatures and patterns); `ts/tests/structure/calls.test.ts` (titles and `:140-217`), `plant.ts:1-40`; `ts/tests/core/fileformat.test.ts:60-80`, `feedback.test.ts:1-30`, `feedback-edit-back.test.ts:1-25`, `views-trust.test.ts:15-50`, `text.test.ts:50-58`, `builders.ts` (exports); `ts/bun.lock` (the young packages and their dependants); `src/lodge/core/fields.py:110-170`, `fileformat.py:84-95`, `yamlio.py:1-60`; `tests/structure_calls.py:1-60` and `:120-190`; `tests/core/test_views_trust.py:1-62`, `test_check_immutable.py:22-52`, `test_fileformat.py:60-90`; the headings of every task review and recheck; plans 2, 3, and 4 where they name `#core`, the call rules, or plan 1's names.
Not read: the other modules of `ts/src/core` beyond the greps above (`check-*.ts`, `confirmation.ts`, `doubts.ts`, `feedback.ts`, `order.ts`, `render.ts`, `search.ts`, `views.ts`, `words.ts`, `document.ts`, `ids.ts`, `model.ts`, `settings.ts`, `value-repr.ts`, `read-back-fields.ts`); the other 43 of the 49 test files of `ts/tests/core` and their Python originals, beyond the case counts and the samples above; `ts/scripts/differential.ts`, `differential.test.ts`, and `scripts/differential_dump.py`; the task briefs and reports; the design document; `probes.md` and `probes/`.
