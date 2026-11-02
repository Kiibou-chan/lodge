# Task 5a recheck 1

Fix commit bfc8c5c against cb94f31 (`git diff cb94f31 bfc8c5c`), checked in a detached scratch worktree at bfc8c5c, removed afterwards.
The gate commands rerun there: `biome check --error-on-warnings .` clean, `tsc --noEmit` clean, `bun test` 429 pass, 0 fail.

Counts: 14 closed, 0 open, 0 new Blocking, 0 new Important.

## Findings

- D-1: closed. Five mutants applied one at a time to `bun test tests/core`, each reverted. `hasReasoningHeading` `trimEnd` fails `feff_after_reasoning_heading_round_trips`. `splitReasoning` `trimEnd` fails the same test. `trimBlock` `.trimEnd()` fails `trailing_feff_round_trips`. `trimBlock` `.trim()` fails `opening_feff_line_round_trips`. `readStr` `.trim()` fails `python_whitespace_title_is_empty`. Tests at `ts/tests/core/fileformat-edges.test.ts:5-20`. The unmutated tree gives 252 pass, 0 fail.
- C-1: closed. `ts/src/core/fields.ts:151-155` adds `Number.isSafeInteger`. Ranks run through `parseArea`: 9007199254740991 and 0 read; 9007199254740992, 12345678901234567890, 1000000000000000000000, and 007 are problems naming `rank` at line 4. Tests at `fileformat-edges.test.ts:21-39`.
- C-2: closed. `fileformat.ts:106-116` gives the four dataclass reprs; test `nested_change_read_back_repr` (`fileformat-edges.test.ts:40`) pins the Python message.
- C-3: closed. No code change, as ruled (d-0q54zn); the ledger line 54 and the report's differences list name both surrogate cases and the `bad_utf8_is_problem_1` reach.
- C-4: closed. `fileformat.test.ts:174-193` feeds Python's seven escape forms.
- P-1: closed. `ID_KIND`, `CODE` in `fields.ts:6-11`; `SLUG_WORDS`, `SLUG_CHARS`, `PLAIN` in `fileformat.ts:68-70`.
- P-2: closed. Comments at `document.ts:43`, `:83`, `fields.ts:62`, `:124`, `fileformat.ts:29`.
- P-3: closed. `refused` helper (`fileformat-write.test.ts:4`), the `.map` gone, `bytesToHex` used.
- D-2: closed. `ts/src/core/read-back-fields.ts` holds the lists and `ts/tests/core/read-back-fields.test.ts` compares them to `Object.keys` of each model. It reads the source through the TypeScript parser, so it stays behind the front door.
- D-3: closed. Ledger line 16 names the `requireField` alias.

## Parked items

- Task 3, table literals: closed. `ts/tests/structure/table.test.ts` pins `PACKAGES` and `CORE_NPM`.
- Task 4 N-1: closed. The report lists `bad_code_is_problem_1` among the tests that cannot hold, citing d-p48gr1.

## Ruling d-f18pz7

Closed. `ts/package.json` runs `biome check --error-on-warnings .`; `git diff cb94f31 bfc8c5c -- ts/biome.json` is empty; no `biome-ignore` in `ts/src` or `ts/tests`. The `!` assertions became narrowing (`document.ts:12`, `:46`), a `mapString` helper (`headers.ts:154-158`), and optional access (`fields.ts:41`), and the biome run is clean with zero warnings.

## New problems

None Blocking or Important.
Minor, no action: `fields.ts:41` prints `U+undefined` if the code point were ever absent, which `unreadableChar` cannot return; `mapString` in `headers.ts` throws a message no test reaches, for a state `readMap` already excludes.
