# Task 5a review: record files

Commit 1d57ad1 against 1430bab (`git diff 1430bab 1d57ad1 -- ts/`), reviewed from `task-5a-brief.md` and the plan's Review Focus items 1, 2, 4, and 7.
Probes ran in a detached scratch worktree at 1d57ad1 (`.claude/worktrees/review-5a`, removed afterwards), with the Python of this branch run through `uv run --frozen --quiet --project /var/tmp/lodge-server-core python`, whose `src/` the uncommitted Task 4 fix does not touch.

Counts: 0 Blocking, 2 Important, 8 Minor.

## What the differential runs showed

A probe pair (`py_side.py` and `ts_side.ts`, the same JSON cases into `parse_record`, `parse_area`, `write_record`, `write_area`, `new_record_path`, `slug`, and `content_hash`, outputs compared as JSON) gave these results.

- Every file under `lodge/` (218 decisions, 126 specification entries, 10 areas, read as bytes with `surrogateescape`): `parseRecord` and `parseArea` give the same record or problem as Python in all 354 cases, and `contentHash` the same hash in all 354.
- Each of those 354 parsed records written back: `writeRecord`, `writeArea`, and `newRecordPath` agree with Python byte for byte in all 698 cases (Review Focus 7).
- 733 edge cases: U+001C, U+0085, U+FEFF, U+2028, U+3000, U+00A0, U+200B, U+FFFE, U+FFFF, U+0000, DEL, a tab, a lone CR, CRLF, an astral character, and lone surrogates, each in a title, a statement, a reasoning, a quote, an area intro, and before or after a `## Reasoning` line; 20 stamps and 9 bare days with and without `imported_from` (`+00:60`, `+23:60`, `+24:00`, `T24:00:00`, year 0000, 2023-02-29, a leap second, a full-width digit); ranks from 0 to 10^21; unknown keys in text order with quoted names; 14 slugs (U+0130, the Kelvin sign, a ligature, cuts at 59, 60, and 61 characters).
  The only differences in Task 5a's own code are C-1, C-2, and C-3 below; the rest are messages and readings of `loadYaml` already ruled or being fixed under Task 4 (d-p48gr1, d-fbhdvf, and `task-4-review.md` C-4: `unreadable character 28` against `'\x1c'`, U+0085, U+2028, or a trailing tab ending a plain scalar, and the `yaml` package's pretty messages), which this review does not count.
- The edge outputs of TypeScript are identical under `TZ=Pacific/Kiritimati`, `America/St_Johns`, and `Etc/GMT+12` (`cmp`), and every stamp and day case agrees with Python (Review Focus 4).
- The carried tests pass at 1d57ad1 (`cd ts && bun test tests/core`: 180 pass, 0 fail).

## Correctness

### C-1 · Important · a rank above 2^53 is silently changed or refused

Handle: `ts/src/core/fields.ts:146-152` (`readRank` returns `Number(value)`), `ts/src/core/fileformat.ts:44`, and Task 4's `Area.rank: number | null` in `ts/src/core/model.ts`.
Python's `read_rank` returns an `int` of any size (`src/lodge/core/fields.py:150-154`).
Run (the edge probe): an area draft with `rank: 12345678901234567890` parses as rank 12345678901234567000, and `writeArea` writes `rank: 12345678901234567000`, which reads back as the same rounded number, so the read-back check passes and the file holds a number nobody wrote; Python writes `rank: 12345678901234567890`.
`rank: 9007199254740993` becomes `9007199254740992`, and `rank: 1000000000000000000000` makes `writeArea` throw `the area would not read back: rank must be a non-negative whole number without leading zeroes`, since `${1e21}` is `1e+21`, where Python writes it.
Two ranks that differ only past 2^53 compare equal in TypeScript, so Task 7's area order can differ from Python's.
Reach: no record reaches it (the 10 areas here hold ranks 1 to 10), only a draft with a rank of 16 or more digits, which `lodge add` accepts in lodge 0.2.
The finding is Important because the result is a silent change of a stored value (s-q4s548) and the brief cannot settle it: Task 4 fixed the type, and the builder asks for a ruling.
Fix: a coordinator ruling; the cheap form is that `readRank` refuses a value above `Number.MAX_SAFE_INTEGER` with the same message and the key `rank`, listed as a difference, with a test of `rank: 9007199254740992` refused and `rank: 9007199254740991` read; the exact form is `bigint`, which the JSON API of d-sry12f cannot serialise without a converter.

### C-2 · Minor · a read-back message names nested values as `[object Object]`

Handle: `ts/src/core/fileformat.ts:96-102` (`valueRepr`) and `:130`.
Python prints the dataclass repr (`src/lodge/core/fileformat.py:112`).
Run (edge probe): a decision whose change entry is `"s-4kq1zm "` gives in Python `the record would not read back unchanged: changes reads back as (Change(entry='s-4kq1zm', action=<Action.EDIT: 'edit'>),)` and in TypeScript `… changes reads back as ([object Object],)`.
The same holds for `quote`, `numbers`, and `imported_from`, whose objects reach `String(value)`.
Reach: only a record built in code rather than parsed from a draft, since a parsed entry has already passed `read_id`; no carried test pins the message.
Fix: give `valueRepr` the four dataclass reprs (`Change(entry=…, action=<Action.EDIT: 'edit'>)`, `Quote(text=…, where=…, when=…)`, `NumberHandle(value=…, handle=…)`, `Imported(file=…, heading=…)`), chosen by field set, with one test on the changes case above.

### C-3 · Minor · the hash difference is narrower in reach and wider in kind than the report says

Handle: `ts/src/core/fileformat.ts:71-76`, `ts/tests/core/fileformat.test.ts:213-217`, and the report's "TypeScript differences and concerns".
Judgement on the builder's concern: Python calls `content_hash` only on a stored file's text (`src/lodge/core/apply.py:202`, `src/lodge/app/reads.py:122`), decoded by `src/lodge/gitstore/trees.py:16` with `surrogateescape`, so its lone surrogates are always U+DC80 to U+DCFF, one per undecodable byte.
In TypeScript no text decoded with `TextDecoder` holds a lone surrogate, and no TypeScript writer stores one (`writeRecord` reads its text back through `splitDocument`, which refuses them), so no input of this plan reaches the difference; it becomes reachable only when a later task decodes stored bytes, which no task of this plan names.
The report lists only the DC80 to DCFF case; the probe also shows that for U+D800 to U+DC7F and U+DD00 to U+DFFF Python raises `UnicodeEncodeError` (`'utf-8' codec can't encode character '\ud800' … surrogates not allowed`) where TypeScript returns the hash of U+FFFD.
The same decoding question decides `bad_utf8_is_problem_1`: lodge 0.2 reports a file with an undecodable byte as problem 1 only because the store decodes with `surrogateescape`; with `TextDecoder`'s default replacement the TypeScript reader would see U+FFFD and parse the file as valid, while the carried test still passes on its synthetic `\udcff`.
Fix: list both cases in the report; add a ledger line for the task that first decodes stored bytes in TypeScript (the importer of plan 4, or the store) to decode as `surrogateescape` does (each byte b of an invalid sequence to U+DC00 + b) and to have `contentHash` encode U+DC80 to U+DCFF back to the byte, which makes the hash equal Python's and keeps problem 1.

### C-4 · Minor · `control_character_is_problem_1` feeds the loader other escapes than Python

Handle: `ts/tests/core/fileformat.test.ts:173-181`; Python `tests/core/test_fileformat.py:155`.
Python escapes with `unicode_escape`, so the header holds `"a\x01b"`, `"a\x7fb"`, `"a\x85b"`, `"a\tb"`, and `"a\nb"`; the TypeScript test writes every case as `\uNNNN`, so YAML's `\x`, `\t`, and `\n` escapes are never read by the carried test (Review Focus 1: the title matches while the input differs).
The behaviour agrees on Python's exact inputs (run: all seven give `title holds U+…, which a header cannot carry` at line 4 in both), so only the test is weaker.
Fix: write the seven escaped forms as Python gives them (`["\\x01", "\\x7f", "\\x85", "\\u2028", "\\ufffe", "\\t", "\\n"]`, with the character beside each for the title), or a helper that escapes as `unicode_escape` does.

## Practice

### P-1 · Minor · module constants of Python inlined or rebuilt per call

Handle: `ts/src/core/fields.ts:87-91` builds the `kinds` map on every `readId` call where Python has the module constant `ID_KIND` (`fields.py:15`); the pattern `[A-Za-z0-9][A-Za-z0-9._-]*` is written out at `fields.ts:44` and `fileformat.ts:145` where Python names it `_CODE` and `_PLAIN`; `slug` uses the bare numbers 6 and 60 (`fileformat.ts:66-69`) for `_SLUG_WORDS` and `_SLUG_CHARS`.
Scenario: a later edit to the code pattern in one file leaves the writer's plain-name test and the reader's check disagreeing, and `decided_by` values start being quoted or refused differently.
Fix: module constants named as in Python (`ID_KIND`, `CODE`, `PLAIN`, `SLUG_WORDS`, `SLUG_CHARS`), unexported.

### P-2 · Minor · facts in Python's docstrings are dropped

Handle: `ts/src/core/document.ts:42-46` (`trim_block`: "indentation stays"), `:81-86` (`key_line`: "for a dotted key its first part", and the `+ 2` for the fence line), `ts/src/core/fields.ts:57-77` (`read_map`: the `multiline` key may hold line breaks and tabs), `:121` (`read_date`: a bare day only for an imported record), and `ts/src/core/fileformat.ts:27` (`write_record`: a record that would not read back is a `ValueError`).
Scenario: a reader of `keyLine` takes `index + 2` for an off-by-one and "fixes" it, and `unknown_key_named` (line 8) catches it only after the edit.
Fix: one comment per function whose rule the code does not show, stating the fact as the docstring does; the self-explanatory ones stay bare.

### P-3 · Minor · test and helper duplication

Handle: `ts/tests/core/fileformat-write.test.ts:300-399` builds each refused record twice and calls `writeRecord` twice, once for `toThrow(ValueError)` and once for the pattern; `ts/tests/core/samples.ts:57` ends with the no-op `.map((row) => row)`; `ts/src/core/fileformat.ts:73-75` hand-writes the hex that `bytesToHex` of `@noble/hashes/utils.js` (a dependency already, line 357 of that file) gives.
Scenario: a fix to one of the two literals of a refused record leaves the other testing the old record, so the class and the pattern are checked on different inputs.
Fix: one helper, `refused(write: () => unknown, pattern: RegExp)`, that catches once and asserts `instanceof ValueError` and the pattern; drop the `.map`; use `bytesToHex(sha256(…)).slice(0, 12)`.

## Design

### D-1 · Important · the brief's text-edge rules have no test, and the JavaScript spellings survive

Handle: `ts/src/core/document.ts:40`, `:44`, `:45`, `:49`, and `ts/src/core/fields.ts:29`; the brief's line "`document.py`'s `rstrip` (lines 44, 52, and 59) is `rstrip` of `text.ts`, so a line `## Reasoning` followed by U+FEFF does not start the reasoning".
The behaviour is right today (edge probe: 0 differences), but mutation runs in the scratch worktree, each reverted, left `bun test tests/core` at 180 pass, 0 fail for each of: `rstrip(line)` to `line.trimEnd()` in `hasReasoningHeading` and in `splitReasoning`, `rstrip(lines.join("\n"))` to `.trimEnd()` and `strip(lines[0]!)` to `.trim()` in `trimBlock`, and `strip(value)` to `value.trim()` in `readStr`.
Scenario after such an edit: a statement holding a line `## Reasoning\ufeff` is refused by `writeRecord` or split into statement and reasoning where lodge 0.2 keeps it whole, a statement ending in U+FEFF or opening with a line of U+FEFF loses it, and a title of U+001C reports `title holds U+001C` instead of `title must be a non-empty string`.
Task 12's differential runs on this repository's records, none of which holds these characters, so nothing in the plan catches the regression (Review Focus 2).
Fix: four TypeScript tests beside the carried ones: the statements `A\n## Reasoning\ufeff\nB`, `S.\ufeff`, and `\ufeff\nS.` each round-trip through `writeRecord` and `parseRecord` unchanged, and a header `title: "\x1c"` gives a problem naming `non-empty`.
Run: these four tests, written in the scratch worktree, pass at 1d57ad1, and each of the five mutants fails at least one of them (the first kills both heading mutants).

### D-2 · Minor · the read-back check compares a hand-kept field list

Handle: `ts/src/core/fileformat.ts:103-131`.
Python's `back != record` compares every dataclass field (`fileformat.py:52`, `:67`); the TypeScript check compares only the names listed, so a field added to `Decision`, `SpecEntry`, or `Area` and forgotten by both the list and the writer passes the check and is lost on every write.
Fix: keep the list for the message order, and add a test that each list equals `Object.keys` of the corresponding filler's result (`decision`, `specEntry`, `area`) less `kind`, so the list cannot fall behind the model.

### D-3 · Minor · the `require` alias is a convention the next reader must find

Handle: `ts/src/core/headers.ts:17` imports `require as requireField`, because the structure rule against dynamic code treats any call named `require` as one (report, first check run).
Scenario: Task 6's builder ports `threads.py`, which calls `require` (`src/lodge/core/threads.py` imports it), writes `require(header, "id")`, and loses a gate run to the structure test.
Fix: a line in the ledger for Task 6's brief naming the alias; the rule stays as it is.

## Files read

Read: `CLAUDE.md`; `task-5a-brief.md`, `task-5a-report.md`, `task-5a-codex-final.txt`; the plan's Review Focus, Global Constraints, and "Settled for the later plans"; `task-4-review.md` (C-3, C-4) and `task-4-fix-1.md`; decisions d-p48gr1, d-fbhdvf, d-v9mw2d, and d-g1hrmn; `lodge spec` (purpose and constraints); the whole diff (`ts/src/core/fields.ts`, `document.ts`, `headers.ts`, `fileformat.ts`, `index.ts`, `ts/knip.json`, `ts/tests/parity.json`, `ts/tests/core/samples.ts`, `fileformat.test.ts`, `fileformat-write.test.ts`, `fileformat-problems.test.ts`); `src/lodge/core/fields.py`, `document.py`, `headers.py`, `fileformat.py`, `yamlio.py`, and the field lists of `model.py`; `tests/core/samples.py`, `test_fileformat.py`, `test_fileformat_problems.py`; the parts of `ts/src/core/yamlio.ts` and `model.ts` named above; `src/lodge/app/reads.py:110-122`; the import lines of `src/` and `tests/` naming the four modules.

Not read: `probes.md` and `probes/` (the items the brief names were checked by running instead); `ts/src/core/text.ts`, `stamps.ts`, and `ids.ts` beyond their behaviour in the probes; `ts/tests/structure/` beyond a search for `trim` and `.length`; `ts/tests/parity.test.ts` beyond its name check; `src/lodge/core/apply.py` and `drafts.py` beyond the lines cited.
