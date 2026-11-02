# Plan 1: recheck of the final fix wave

Branch `server-core`, fix wave 782bb67..4f5d5fb (part A 1b511c2, part B bd0320e, lockfile 4f5d5fb), rechecked in a detached scratch worktree at 4f5d5fb with `ts/node_modules` linked from the branch's worktree.

## Gate and differential

`sh scripts/check.sh` at 4f5d5fb: exit 0; ruff and mypy clean, Python 1,399 passed, Biome 116 files, dependency-cruiser 125 modules and 410 dependencies, `bun test` 924 pass, 0 fail, 63 files.
The gate now ends with `sh scripts/differential.sh`: "354 records, 10 areas, 0 threads, 0 problems, 113 queries, 364 rewritten files", "0 differences", then `differential.integration.ts` 1 pass, 0 fail, 7 `expect()` calls.
This repository holds no thread, so the thread comparison runs only on the made-up store of the integration test.

## Findings of the final review

Each mutation below was applied alone in the scratch worktree, run against the named suite, and reverted; every one of them turned the suite red, and none of the 30 survived.

### F-1 and d-4vhjtt · Resolved

`ts/tests/structure/calls.ts:173-176`: `open` and `openSync`, resolved through a renamed `fs` import, are a write only with a flag argument that is not a string literal or holds `w`, `a`, or `+`.
Tests: `file_import_resolution` (`openSync(p)` in `cli`, `io.open(data)`) and `write_ports_and_read_opens_are_allowed` (`io.open(data)` in `api`, `openSync(p, "r")` in `cli`), `ts/tests/structure/calls.test.ts:219-264`; refusals `open("p", "w")`, `openSync("p", flags)`, `openSync("p", "a")`, `openSync("p", "r+")` kept at `:158-163`.
Mutation `!!flags &&` restored to the old reading (no flag is a write): `file_import_resolution "io.open(data)"`, `"openSync(p)"`, and `write_ports_and_read_opens_are_allowed "src/api/a.ts"` fail.
Mutation `/[wa+]/u` to `/[wa]/u`: `file_writing_outside_git "cli" "openSync(\"p\", \"r+\")"` fails.
The other half of F-1's failure paragraph (`rename`, `link`, `rm`, `mkdir`, and the rest of `writes` matched on any receiver) is unchanged and was not part of F-1's Fix or of d-4vhjtt; no port of plans 2 to 4 has a method of those names (searched in the three plans), so it costs nothing now.

### F-2 · Resolved

`calls.ts:30-37` adds `self`, `global`, `window`, `setImmediate`, `clearImmediate`, `prompt`, `alert`, and `confirm` to `banned`; `calls.ts:91` reports a meta-property in `core` and `app`.
Test: `new_purity_globals` for `core` and `app`, with `{ self: 1, global: 2, prompt: 3 }` allowed (`calls.test.ts:233-255`).
Mutation `"self"` removed from `banned`, and mutation of the meta-property line removed: `new_purity_globals "core"` and `"app"` fail for each.
The meta-property check also refuses `new.target`, with the wrong message (N-3 below).

### F-3 and d-svv7gv · Resolved

`ts/bunfig.toml` holds `[install]` `minimumReleaseAge = 1209600`; `git diff 782bb67..4f5d5fb -- ts/bun.lock` changes exactly four entries (8 lines), `unbash` 6.0.3 to 6.0.0, `@types/node` 26.6.6 to 26.6.5, `tslib` 2.9.1 to 2.8.1, `@napi-rs/wasm-runtime` 1.2.6 to 1.2.5, the last with its own peer ranges; no other line moves.
Publication times read from `https://registry.npmjs.org/<name>` (four requests, one a second): `unbash` 6.0.0 2026-10-16T10:00Z, `@types/node` 26.6.5 2026-10-09T18:46Z, `tslib` 2.8.1 2024-10-31T22:42Z, `@napi-rs/wasm-runtime` 1.2.5 2026-10-05T08:43Z; the lock commit is 2026-11-02T19:59Z, so the cut is 2026-10-19T19:59Z and all four are older.
The installed `ts/node_modules` holds `unbash` 6.0.0 and `@types/node` 26.6.5, so the gate ran on the new versions; `tslib` and the wasm runtime are not installed on this platform.
Two gaps in the record, not the code, are N-4 below.

### F-4 · Resolved

`ts/tests/structure/guards.ts:35-71` (`fsImports`) maps named, renamed, namespace, default, and `promises` imports of `fs`, `node:fs`, `fs/promises`, and `node:fs/promises` to the imported name, and `calls.ts:185-187` tests `writes` against it.
Test: `file_import_resolution` (`writeFileSync as save`, `writeSync as w`, `fs.writeSync`, a default import of `fs/promises`, `promises as fs`), `calls.test.ts:220-229`.
Mutation keeping the local name (`names.set(item.name.text, item.name.text)`): the two renamed cases fail.

### F-5 · Resolved

`ts/tests/core/text.test.ts` adds `٣` and `𝟙` to the true cases of `is_digit_like_python`.
Mutation `/\p{Nd}/u` to `/[0-9]/u` at `ts/src/core/text.ts:69`: `is_digit_like_python` fails.

### F-6 · Resolved as worded, with a gap (N-2)

`guards.ts:76-93` (`unsafePattern`) refuses, in `core` only (the coordinator's ruling), a regular expression literal or a literal `RegExp` whose flags lack `u` or hold `m`, or whose pattern holds `\s`, `\w`, `\d`, or `\b`; `calls.ts:163-170` refuses `sort()` and `toSorted()` without a comparator in `core`.
Tests: `portable_patterns` and `explicit_sort_comparator`, `ts/tests/structure/core-rules.test.ts:28-51`.
Mutation dropping the escape test: three `portable_patterns` cases fail; mutation `node.arguments.length === 0` to `false`: both `explicit_sort_comparator` refusals fail.
The upper-case escapes and the flags of a pattern built from a template are not checked (N-2).

### d-d0vca9 · Resolved

`calls.ts:182-191`: `write`, `writev`, and their `Sync` forms are reported only when `fsImports` resolves them, by name or through a namespace (the namespace reading the final review asked for); `.write`, `.writer`, and `.delete` only on a `Bun.file(…)` call (`calls.ts:177-181`); `Bun.write` by name.
The four `cli` cases now import from `node:fs` (`calls.test.ts:150-153`), so the refusal still has a subject.
Tests: `file_import_resolution` (`process.stdout.write`, `process.stderr.write`, `port.write`, `port.writer`, `port.delete`, and an unimported `write(x)` allowed in `cli`) and `write_ports_and_read_opens_are_allowed` (`src/main.ts`, `api`, `app`).
Mutation reporting the four names on any receiver again: `file_import_resolution` (two cases) and `write_ports_and_read_opens_are_allowed "src/main.ts"` fail; mutation dropping namespace resolution: `file_import_resolution "import * as fs from \"node:fs\"; fs.writeSync(1, x)"` fails.

### 11-D-1 · Resolved

`guards.ts:3-33` (`guardedCatch`) requires every `catch` in `core` to open with `if (!(e instanceof C)) throw e;` on its own binding; `calls.ts:92-93`.
Tests: `guard_and_result_construction` (`core-rules.test.ts:5-15`), with the adapters left alone by `core_only_rules_leave_adapters_alone`, per the coordinator's ruling.
Mutation accepting any thrown identifier: the `throw other` case fails; mutation deleting the guard at `ts/src/core/apply.ts:166`: `repository_has_no_violations` fails with `src/core/apply.ts:165: catch must rethrow other errors`.

### 8afix-D-2 · Resolved

`calls.ts:94-106` refuses an object literal with an `ok` key (plain, string, shorthand, or computed string) in `core` outside `src/core/check-state.ts`.
Mutation `"ok"` to `"okk"`: `guard_and_result_construction "const r = { problems, notes, ok: true }"` fails.
It is syntactic, so a spread copy of a check result passes, as the part A report says.

### 8afix-D-1 and d-snrhjs · Resolved

Already answered at 1e80e61; `checkResult` stays on the front door and the fix wave did not touch it.

### Task 3's parked Minor (`PACKAGES`) · Resolved

Already pinned by `package_edges_match_ruling` in `ts/tests/structure/table.test.ts` since bfc8c5c; part A's wrong-edge mutation failed it (`final-fix-a-report.md`); not re-run here.

### 12-D-1 · Resolved

`ts/scripts/differential.ts:75-78` and `scripts/differential_dump.py:70-74` put every thread file through `parseThread` and `writeThread` into `rewrite`; `ts/scripts/differential.integration.ts` builds a made-up store with two threads, open and closed, each with an `author` message carrying `where` and `when`, and asserts 4 rewrites, "2 threads", and "0 differences".
Mutation of `writeThread` writing an author's `when` unquoted (`ts/src/core/threads.ts:120`): `sh scripts/differential.sh` exits 1 with `rewrite["lodge/threads/q-aaaaaa.md"]["0"]` and `q-bbbbbb` differing, "2 differences".
Mutation dropping the TypeScript thread branch: "2 differences", `TypeScript=undefined`; dropping the Python branch: `toHaveLength(4)` fails.
This repository holds no thread, so on real records the thread comparison stays empty until one is opened.

### 12-D-2 · Resolved

The Python-spawning test moved to `ts/scripts/differential.integration.ts`, outside `bun test`'s default pattern; `scripts/differential.sh` runs it, and `scripts/check.sh` now ends with `sh scripts/differential.sh`.
Run: `env -i PATH=<a folder holding only bun> bun test` in `ts/`: 924 pass, 0 fail, 63 files.
`ts/scripts/differential.test.ts` keeps its `Bun.spawnSync` of `differential.ts`, so plan 4's handle to it as the sandbox's spawning example (plan 4 at a64d512, line 24) still holds.

### 10-D-1 · Resolved

`ts/tests/core/feedback-edges.test.ts`, listed in `ts/tests/parity.json` with a `why`.
Six of the review's 21 mutations run here, each failing one test: `isAuthor(decision)` dropped (`edit_back_is_only_author_rejecting_agent`), `START` dropped from `NUMBER` (`number_scan_edges "x3 item-1 4 % 5 5"`), the edited entries unsorted (`edit_back_entries_are_sorted`), `PY_SPACE_CLASS` replaced by `\s` (`number_scan_edges "4\u001C% 5%"`), the specification word limit as `>=` (`spec_at_word_limit_is_clean`), and the revival's own-change set emptied (`own_change_suppresses_edit_back_and_revival`).

### 11-P-1 and the fold of `apply-areas.ts` · Resolved, no behaviour changed by the fold

`git diff -M 782bb67..4f5d5fb` shows `apply-areas.ts` renamed to `ts/src/core/apply-state.ts` at 94 % similarity; the changes are the `byCodePoint` import, `draftedAreas` narrowed to `ReadonlySet<string>`, and the two sorts of 11-P-2; `apply.ts` changes only its import, a type-predicate `filter` giving the same set, and the third sort.
The sorts are the one intended change: default `sort()` and `byCodePoint` disagree only where UTF-16 order and code point order differ (a code point from U+E000 against an astral one), which no ID or area name of the store holds; the differential on this repository's 354 records and the carried apply tests are green.

### 11-P-2 · Resolved

The three sorts use `byCodePoint` (`apply.ts:42`, `apply-state.ts:39-41` and `:72`).
Mutation of `apply-state.ts:72` back to `.sort()`: `repository_has_no_violations` fails on the new `core` sort rule.

### 11-D-2 · Resolved differently, adequately

No `#core` export; `plan-2-writes-handoff.md` names `isStale`'s marker test, and plan 2 at 0e5a042 carries it (`docs/superpowers/plans/2026-11-02-lodge-server-store.md:298` on `server-store`).

### 11-D-3, 8b-D-1, 9a-D-1 · Resolved

New files `apply-edges.test.ts`, `check-change-edges.test.ts`, and `views-edges.test.ts`, each with a parity `why`.
Mutations run here: `checkChange`'s duplicate filter dropped (`ts/src/core/check-change.ts:122`) and its sort removed fail `change_problems_are_sorted_and_duplicate_changes_report_once`; `level3`'s `uniqueChanges` dropped (`ts/src/core/views.ts:88`) fails `agent_quote_is_not_author_evidence`; 11-D-3's two mutations taken from the part B report, not re-run.

### 8b-P-1 and 8b-P-2 · Resolved

One `equal` (`ts/src/core/equal.ts`) for `check-entries.ts`, `check-immutable.ts`, `fileformat.ts`, and now `threads.ts`; one `uniqueChanges` (`ts/src/core/model.ts:16-24`) kept off the front door by an explicit export list; one `compareProblems` (`ts/src/core/check-state.ts:149-153`).
The shared `equal` adds `Object.hasOwn` and `Map` and `Set` comparison to `fileformat.ts`'s copy, which only tightens it; the read-back tests and the differential are green.

### 8afix-P-1 · Resolved

`views.ts:199-200` compares `orderInstant` of the two dates, which is Python's `order_key(latest)[0] > order_key(who)[0]` (`src/lodge/core/views.py:223`); the fixture-only test is gone.
Mutation `>` to `>=`: `same_second_change_does_not_mark_changed_since` fails.

### 8a-P-2 · Resolved

The deleted `check_8_cycles_include_each_member_and_ignore_self_and_missing_links` is covered by `check-links.test.ts:51-90` (`rests_on_itself_fails_check_2` with no check 8, the two- and three-entry cycles).

### 6-C-2 and 6-D-1 · Resolved

Mutation adding `m` to `UNESCAPE` (`threads.ts:23`): `unescape_breaks_lines_at_newline_only` fails.
Mutation removing `where` from `READ_BACK_FIELDS.message`: `read_back_fields_cover_model` fails.

### 6-C-3 · Not resolved in full (Minor, still open)

`ts/src/core/yamlio.ts:95-108` now reports PyYAML's line for the two named patterns, and five cases pin it (`ts/tests/core/yamlio.test.ts:103-116`).
Run, 20 headers through `loadYaml` and lodge 0.2's `load_yaml`: 18 agree, two do not: `"a: b\nc d   \ne: f"` gives 3 in Python and 2 in TypeScript, and `"a: b\r\nc d\r\ne: f"` the same, because `yamlio.ts:107` steps over a `\n` directly after the key's end but not over trailing blanks or a `\r\n`.
A record with CRLF line ends is a case the differential already holds (its integration store), so a hand-edited Windows header still gets the line above.
Fix: step over `/^[ \t]*\r?\n/u` instead of a lone `\n`; run here, all 20 agree and `tests/core` stays green (706 pass); add the two cases to `implicit_mapping_key_error_uses_token_end`.

### 5b-C-1 and 6-C-1 · Resolved differently, adequately

The part B report says it corrected the old task reports; the coordinator reverted those edits (ledger, part B line), so the reviews' mutation tables stand as the evidence, as their Fix says, and the rule for later briefs is carried by `plan-2-writes-handoff.md` and plan 2's Global Constraints (`2026-11-02-lodge-server-store.md:24` on `server-store`).
The two rows of `final-fix-b-report.md` that describe the report edits no longer match the branch; the ledger's part B line says so.

### The other parked Minors · Resolved by the report, not re-run

5b-C-2, 5b-P-1 to 5b-P-4, 5b-D-1, 6-P-1 to 6-P-4, 6-D-2, 8c-P-1, 9a-P-1, 9b-C-1, 9b-C-2, 9b-P-1, and 10-P-1: each change is in the diff where the part B report puts it, and the gate is green; their failing-first outputs are in `final-fix-b-report.md` and were not reproduced here.

## Structure rules against lodge 0.2 and plans 3 and 4

A probe of 40 planted files through `callViolations` (`bun test` of a file in the scratch worktree):
- Refused, as `tests/structure_calls.py` refuses their counterparts (`:14-38`, `:139`, `:171`, `:231-238`): `writeFileSync`, `fs.mkdirSync`, `renameSync`, `unlinkSync`, `rmdirSync`, `symlinkSync`, `linkSync`, `truncateSync`, `rmSync`, `createWriteStream` on a default import, `openSync` with `"w"`, `"wx"`, `"r+"`, a variable, and renamed with `"a"`, `fsp.open(p, "w")`, `fs.promises.writeFile`, a renamed `writeFile` from `node:fs/promises`, `Bun.write`, `Bun.file(p).write`, `.writer()`, `.delete()`, `x.mkdir` and `x.rename` in `api`, `port.open(p, 'w')` in `app`, and the purity, dynamic code, and dynamic import cases.
- Allowed, as plans 3 and 4 need: `process.stdout.write(text)` in `src/main.ts`, `await io.open(data)` in `api`, `await target.write(t, files, m)` in `app`, `readFileSync`, `fs.openSync(p)`, and `promises.open(p)` in `cli`.
- `io.open(data)` in `api` is a read lodge 0.2 refuses by its attribute rule (`tests/structure_calls.py:137-138`); d-4vhjtt and the dispatch accept it, and `api` still cannot import `fs` (`ts/.dependency-cruiser.cjs`, `file-confinement`).

## Names plans 2 to 4 consume from `#core`

`tsc --declaration` of `ts/src/core/index.ts` at 782bb67 and at 4f5d5fb, diffed: `index.d.ts` changes only `export * from "./model.ts"` into a list that names every one of `model.ts`'s 20 exports at 782bb67; the other differences are internal (`apply-areas.d.ts` to `apply-state.d.ts`, `equal.d.ts`, `compareProblems`, `uniqueChanges`, two `READ_BACK_FIELDS` keys), none reachable through `#core`.
No name or signature of the front door changed; `ts/tests/core/builders.ts` widens `snapshotOf`'s `paths` to accept `null`, which keeps every earlier call valid.

## New findings

### N-1 · Minor · the CRLF and trailing-blank YAML lines (6-C-3's remainder)

Handle, scenario, and fix under 6-C-3 above.

### N-2 · Minor · the pattern rule misses the upper-case escapes and a built pattern's flags

Handle: `ts/tests/structure/guards.ts:92`, the test `\\[swdb]`, and `:85`, which returns early for any `RegExp` whose pattern is not a literal, flags included.
Run: `/a\S/u` and ``new RegExp(`a${b}`, "g")`` in `src/core/a.ts` each give no finding.
Scenario: a plan 2 change to `core` writes Python's `\S` as JavaScript's, which differs at the same code points as `\s` (U+001C to U+001F, U+0085, U+FEFF, the final review's F-6 count), or builds a pattern from `PY_SPACE_CLASS` without `u`, and the gate is green.
Fix: test `\\[swdbSWDB]`, and check a literal flags argument whatever the pattern is; one refusal each in `portable_patterns`.

### N-3 · Minor · `new.target` is refused in `core` and `app` as `import.meta`

Handle: `ts/tests/structure/calls.ts:91`, `ts.isMetaProperty(node)` without its keyword.
Run: `new.target` in `src/app/a.ts` gives `src/app/a.ts:1: app may not use import.meta`.
Scenario: a plan 2 error class in `app` sets its prototype through `new.target`, and the builder meets a refusal that names something the file does not hold; nothing in `ts/src` or plans 2 to 4 uses `new.target` today.
Fix: `ts.isMetaProperty(node) && node.keywordToken === ts.SyntaxKind.ImportKeyword`, and `new.target` as an allowed case in `new_purity_globals`.

### N-4 · Minor · F-3's ledger line has no dates and cites a decision this branch does not hold

Handle: `docs/superpowers/plans/2026-11-02-lodge-server-core-progress.md:104` names d-svv7gv and the four versions without their publication dates, which F-3's Fix asked for; `uv run --frozen --quiet lodge show d-svv7gv` on `server-core` answers `no record named d-svv7gv` (the record is on `server-api`, and part B's report met the same).
Scenario: plan 1 merges to `main` before plan 3, and its ledger and `ts/bunfig.toml` rest on a decision `main` does not hold until plan 3 merges.
Fix: add the four dates read above to the ledger line, and note there that d-svv7gv arrives with plan 3, or record the move of the setting to plan 1 as its own coordinator decision on this branch.

## Counts

Findings of the final review and the rulings: F-1 to F-6, d-d0vca9, d-4vhjtt, and d-snrhjs resolved (F-6 with N-2 left).
Parked Minors: all resolved but 6-C-3, open in part (N-1); 5b-C-1, 6-C-1, and 11-D-2 answered differently but adequately.
New: 0 Blocking, 0 Important, 4 Minor (N-1 to N-4).
Mutations run: 30, all killed.
