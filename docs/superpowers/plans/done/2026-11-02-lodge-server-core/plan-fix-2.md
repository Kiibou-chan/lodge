# Plan fix round 2: lodge server core

Answers `plan-recheck-1.md` (0 Blocking, 3 Important, 6 Minor, and the mismatch rows of its preflight) of the plan at `b5c8ad5`.
Line numbers are those of the plan after this round.
New probes are items 21 to 25 of `probes.md`, their sources in `probes/fix2/`.
Rulings made in this round, scope `process`, work item the plan: d-tha8st, d-hshapm (narrows d-s2rdn2), d-bxcave, and d-87kzys.

## New Important findings

| Finding | What changed |
|---|---|
| N1 exports whose first reader is a later task | d-tha8st settles one rule for every task boundary: a module or test helper is ported whole, exporting what another Python file imports from it; a file with an export whose first reader comes in a later task goes into `ts/knip.json`'s `entry` in the task that creates it, and the task that gives its last such name a reader takes it out, both listing `ts/knip.json` under Modify (Global Constraints, lines 44 to 60). The table at lines 49 to 58 gives the eight files, from the import lines of `src/lodge/core/*.py` and `tests/core/*.py`: the split boundaries (`headers.ts` and `document.ts` 5a to 5b, `derive.ts` 7a to 7b, `check-state.ts` 8a to 8b, `checks.ts` 8a to 8c) and the old ones (`yamlio.ts` 4 to 5a with `LINE_BREAKS_AND_TABS`, `document.ts` and `fields.ts` 5a to 6, `builders.ts` 6 to 11 with `treeOf`). Probe 21: knip leaves an `entry` file's exports alone and checks them again once it is out. The recheck's own fix, leaving `export` off until the reader's task, was not taken: `tsc`'s `noUnusedLocals` fails on a name its own file never reads (probe 21, `TS6133`), which holds for `new_decisions`, `read_stamp`, `LINE_BREAKS_AND_TABS`, `tree_of`, and `REMEDY_CHECK_4`, so the earlier task would have to leave part of the module unported. Each task's Modify list and Step 3 now name the entries it adds or removes (Tasks 4, 5a, 5b, 6, 7a, 7b, 8a, 8b, 8c, and 11), Steps 4 check that knip reports no unused export, Task 2's `knip.json` (line 339) says the list grows and shrinks, and Task 11's Step 4 (line 719) checks it is back to Task 2's two patterns. `sortKey` is named in Task 8a (line 591); line 587 says why `checks.ts` keeps all of `checks.py` but `check` and `verdict` and waits in `entry` until 8c. The four Python helper names no other file imports (`drafted`, `next_id`, `base_items`, `key`) are not exported (line 45). |
| N2 `front_door_exports_nothing_else` against Task 4's exports | d-hshapm: line 714 allows, besides the names of `errors.ts`, `text.ts`, and `stamps.ts`, the default-filling function of each `PascalCase` name of `__all__` defined in `model.ts` (`decision`, `specEntry`, `area`, `problem`, and `message`, from the dataclasses with defaults in `src/lodge/core/model.py`); `quoted` and `unreadableChar` leave `#core` (line 430) and are module-internal of `yamlio.ts`, in knip's `entry` until Task 5a reads them (line 454, d-tha8st), since no test imports a name from a submodule of `lodge.core` (`grep -rn "from lodge.core\.[a-z_]* import" tests/core` prints nothing). Line 430 names the five default-filling functions and says the `errors.ts`, `text.ts`, and `stamps.ts` names go through `#core`. |
| N3 `py_repr_matches_python` and U+200B | Line 469: U+200B to `'\u200b'`, written as a backslash and `u200b`, Python's `repr` (probe 22). The plan had held the raw character, as had probe 22's own first draft: the editing tool turns a written `\u200b` into the character, so this round wrote every such escape through `chr(92)` and checked the plan for characters of categories `Cf`, `Cn`, `Co`, `Cs`, `Zl`, and `Zp` (none left). |

## New Minor findings

| Finding | What changed |
|---|---|
| m1 `isDigit`'s 90 extra characters | Line 455: `isDigit` differs from `isdigit` at 90 code points, all `Cn` in Unicode 15.1, the first U+10D40, listed in the report (probe 23); the interface comment (line 441) gives Python's 808. |
| m2 `plant`'s link and dependency types | d-bxcave: the planted `package.json` copies `ts/package.json`'s `dependencies` (line 382), and `cruise` sets `preserveSymlinks: true` (line 383), so `yaml` resolves to `node_modules/yaml/dist/index.js` with type `npm` as in `ts/` (probe 24). |
| m3 `\s` has no helper | d-87kzys: `text.ts` exports `PY_SPACE_CLASS` as `\u{…}` escapes (line 447), tested against `isPySpace` over every code point by `py_space_class_matches_is_py_space` (line 469); line 38 and Task 10 (line 692) use it for `_NUMBER`'s `\s?`. `WORD_CLASS`, which had no reader before Task 10, gets `word_class_matches_python_w` in the same test file, so neither waits in knip's `entry`. |
| m4 raw characters | Lines 462 and 469 write U+D7FF, U+E000, U+FFFD, U+FEFF, U+2028, U+200B, and U+FFFF as `\uXXXX`. |
| m5 Biome's notice | The M-8 row of `plan-fix-1.md` is corrected in place: the notice appears as an info and exits 0; the plan is unchanged. |
| m6 plan 3's page | Line 114: `api` imports the page as text (`with { type: "text" }`), which a compiled binary embeds (probe 25), since `api` may not read files (d-x6f9za). |

## Preflight mismatches

| Row | Answer |
|---|---|
| Task 4 against itself | N3 and m1 above. |
| Task 5a against itself | Its deferred names are listed (line 488) and wait in `entry` (N1). |
| Task 7a against itself | `orderKey` waits in `entry` until 7b (line 552, N1). |
| Task 8a against itself | `newDecisions`, `problemAt`, and `sortKey` wait in `entry` until 8b, and `checks.ts` until 8c (lines 587 and 591, N1). |
| Task 8b against itself | `checks.ts` stays in `entry` for `REMEDY_CHECK_4` (8b's Step 3, N1). |
| Task 11 against itself | N2 above. |
| 5a and 5b | 5b imports the six names 5a exported and takes `headers.ts` out of `entry`; `document.ts` stays until 6 (N1). |
| 7a and 7b | 7b takes `derive.ts` out of `entry`; its Modify list names `ts/knip.json`, not `derive.ts`, since 7a already exported `orderKey` (N1). |
| 8a and 8b | 8b takes `check-state.ts` out of `entry` (N1). |
| 8b and 8c | 8c takes `checks.ts` out of `entry` once `check-compare.test.ts` reads `REMEDY_CHECK_4` (line 636, N1). |
| 4 and 11 | N2 above. |
| Same mechanism at old boundaries (4 and 5a, 5a and 6, 6 and 11) | `yamlio.ts`, `document.ts`, `fields.ts`, and `builders.ts` rows of the table (N1). |

## Not changed

- d-s2rdn2's own text: d-hshapm narrows it with what the test allows besides `__all__`.
- The design and `lodge spec`: no finding asks for a change to either.
