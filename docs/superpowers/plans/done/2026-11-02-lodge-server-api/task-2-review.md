# Task 2 review: the command's grammar

Commit `c7185d4` on `server-api-a` over `42a852a`.
Verdict: no Blocking findings; 1 Important, 6 Minor.
Reviewed by Sonnet 5.5 in three passes (correctness, practice, design).

## How it was checked

- `bun test tests/cli` in a scratch detached worktree at `c7185d4`: 55 pass; the full gate (biome with `--error-on-warnings`, `tsc`, depcruise, knip, `bun test`) is green: 1357 pass, 2 todo, 0 fail.
- Differential run against lodge 0.2's real argparse: 4,146 argv generated from a pool of 60 tokens over all fifteen commands, plus 150 random top-level and 80 leading-option argvs, run through lodge 0.2's `parse` (stdout, stderr, exit code captured at `COLUMNS=80`, Python 3.13.5) and through `parse` of the branch.
  Differences are listed in I-1, M-1, and M-2; every other case matched byte for byte, including the `COMMAND` invalid-choice list apart from `view` and `hook` (d-sry12f), the three message rules of `threads.py`, `--limit` conversions, and abbreviations.
- Seven mutations of `args.ts` and `grammar.ts` run against the tests (below).
- A trial merge of `c7185d4` into `server-api` at `3b3eeb0` (which already holds Task 3): `ts/package.json` merges clean; `ts/src/cli/index.ts` conflicts (add/add) and resolves by keeping both export blocks; biome, tsc, depcruise, knip, and `bun test` are green after that (1423 pass).
- Not done: the compiled binary, Python versions other than 3.13.5, and a run of `uv run lodge <name> -h` per command (the differential covers every command's `-h` through the argparse module itself, and no help-body difference appeared).

## Pass 1: correctness

### I-1 (Important): `add` accepts words after an option that lodge 0.2 refuses, and swallows words after an unrecognised option

Handle: `ts/src/cli/args.ts:120` (every non-option word goes into one pool, `words`) and `args.ts:122-129` (the pool is handed to the positionals whatever options sat between).
argparse gives `FILE [FILE ...]` the first contiguous run of words and treats later words as leftovers.
Failure scenarios, each run on both sides:

- `lodge add d-aaaaaa t --dry-run x`: lodge 0.2 exits 2 with `lodge: error: unrecognized arguments: x`; the branch returns `kind: "add"` with `files: [d-aaaaaa, t, x]` (4 of 4146 differential cases; `add builder 0 --import -1 a` likewise).
- `lodge add d-aaaaaa --s a builder` (an unrecognised or ambiguous option followed by words): lodge 0.2 lists `--s a builder`; the branch lists only `--s` (31 of the differential cases, all `add`, since it is the only command whose positional takes more than one word).
  The exit code is still 2, so the harm is the message, and the words the user meant as the option's value are not shown.

The report calls this "as the task requires" (`task-2-report.md`, Deviations); the plan's sentence is "reads options before, between, and after positionals", which argparse honours between separate positionals (`ask d-a --by x f` works in both) but not inside one `+` group.
It is not a listed difference from lodge 0.2 in the sense Task 2 asks for ("the report lists any other difference"), and the report's "differences: 0" holds only for the 122 cases it captured.
Fix: either end a `+` positional's run at the first option, so that later words become leftovers (a change to `args.ts:122-129`, with a test `add a --dry-run b` giving `unrecognized arguments: b`), or keep the leniency and say so in the report and in a `changed` note for the plan's parity table (a carried Python test is not affected, since none passes words after an option, but Task 7a's rows should not rely on the superset by accident).
The first is smaller and keeps byte-for-byte parity, which Global Constraints demand wherever the table marks no change.

## Pass 1 continued: smaller correctness points

### M-1 (Minor): `--` is dropped from the leftover words when the command has positionals

Handle: `ts/src/cli/args.ts:77-81`, which pushes `--` into `extras` only when the command declares no positional.
lodge 0.2 on Python 3.13.5 keeps it: `show a w f -- --gate` gives `unrecognized arguments: w f -- --gate`, the branch `w f --gate` (18 differential cases; `init -- -x` matches and is pinned at `args.test.ts:63`).
argparse's handling of `--` has changed between Python versions, so which side is "right" depends on the interpreter; the plan fixes none.
Fix: pick the Python version lodge 0.2 ships on (`requires-python` in `pyproject.toml`), run the same case there, and either pin a test or list the difference.

### M-2 (Minor): a bad positional choice is reported after `-h` in the branch, before it in lodge 0.2

Handle: `ts/src/cli/args.ts:85-91` answers `-h` while scanning, `args.ts:123-129` checks positional choices afterwards.
`lodge id x --help` gives exit 2 `invalid choice: 'x'` in lodge 0.2 and the help (exit 0) in the branch (8 differential cases, all `id`, the only command with a positional that has choices).
Also `search --limit -.5` (`args.ts:55`): argparse's negative-number rule accepts `-.5`, giving `'-.5' is not a positive whole number`; the branch's `^-\d+(?:\.\d+)?$` makes it an option and says `expected one argument`.
Fix: both are one-line cases; a test or a listed difference.

### Checked and correct

- Usage errors: the command's usage line first, then `lodge <name>: error: …`; leftover words from the top-level parser (`args.ts:139`, `usageError` with the default `TOP_USAGE`), as correctness review M-1 of the plan asks; `thread q-aaaaaa extra` is pinned at `args.test.ts:36`.
- The messages of the plan's list (`required`, `invalid choice` with `pyRepr`, `--limit` sentence, `expected one argument`, `unrecognized arguments`, `ambiguous option`): all reproduced; ambiguous option lists options in declaration order, as argparse does.
- `--by author` rules: sentences equal `threads.py:71-82` and print without a usage line, as `tests/e2e/test_threads.py:91` needs.
- Required-argument order for `ask` (`--kind, --by, FILE`) matches argparse because the action order follows `threads.py`.
- `--version` and `-h` before the command, with abbreviations (`--ver`, `--he`) and `--version=1`: match lodge 0.2.
- `--limit` rejects non-ASCII digits (`args.ts:34`): the narrowing of `parser.py:153` the plan names, and the report lists it.
- The test titles of the plan's step 1 are all present with the plan's inputs; the report's first-failure table handles are correct (checked: `args.test.ts:4` to `:36`, `:44` to `:63`, `grammar.test.ts:71` to `:131`).

### Tests against mutations

Each mutation was applied to a clean checkout of `c7185d4` and `bun test tests/cli` run; `git checkout` restored the file between runs.

| Mutation | File:line | Result |
|---|---|---|
| remove `--help` prefix matching | `ts/src/cli/args.ts:85` | 1 fail (caught) |
| `-5` style words become options | `ts/src/cli/args.ts:55` | 1 fail (caught) |
| drop the sort of leftovers by index | `ts/src/cli/args.ts:137` | 1 fail (caught) |
| drop the `--where` without author check | `ts/src/cli/grammar.ts:157` | 1 fail (caught) |
| drop the top-level explicit-argument error (`--version=1`, `--help=x`) | `ts/src/cli/grammar.ts:80` | 55 pass (survives) |
| ignore `--` before the command | `ts/src/cli/grammar.ts:70` | 55 pass (survives) |
| `--version` only exact, no prefix | `ts/src/cli/grammar.ts:78` | 55 pass (survives) |

### M-3 (Minor): top-level branches of `parse` no test pins

The three surviving mutations above are in `grammar.ts:70-85` and `grammar.ts:78`: `-- show d`, `--version=1`, `--help=x`, `--ver`.
The harness shows them correct today; they have no test, so a refactor can change them unseen.
Fix: three one-line tests in `grammar.test.ts`.

## Pass 2: practice

- CLAUDE.md hard rules: no personal path, machine name, or secret in the diff (grepped `/home`, `kiibou`, `/var/tmp`, em-dashes: none); fixtures are made up (`d-aaaaaa`); no socket, git, or network in the tests; British English and one sentence per line in the report; no em-dash.
- No new dependency (`ts/package.json` diff is the `#cli` line only); no change to `ts/tests/structure/`, `.dependency-cruiser.cjs`, `ts/knip.json`, or `biome.json`; the gate is green; modules are at most 236 lines (limit 300).
- Commit: one commit, message with `Co-Authored-By: Codex`, as the brief says (the plan's Global Constraints name `Claude`; the brief wins for builders).
- Test-first: one commit, so history cannot show red then green; the report's table gives `Cannot find package '#cli'` as the first failure of every initial test, which shows only that the module was missing, not that each assertion fails for its own reason (Minor, M-4).
  The four regression tests have behavioural first failures, which is better evidence.
- Untracked `docs/superpowers/plans/done/2026-11-02-lodge-server-api/task-2-codex-final.txt` in the worktree is a builder's scratch message; it is not committed and should stay out of the merge (M-5, Minor).

### M-4 (Minor): the report's first-failure column

See above; fix: none needed beyond noting it, since the mutation table in this review shows the assertions bite.

### M-5 (Minor): dead and duplicated data in the declarations

- `Declaration.summary` (`ts/src/cli/args.ts:14`) is written for fifteen commands and read nowhere; `TOP_HELP` (`grammar-data.ts:4`) repeats the same sentences as text, as `help` repeats `usage` (`grammar-records.ts:6-7`, one pair per command).
  When plan 4 adds `view` and `hook`, nothing checks that a new summary, usage line, help body, and `TOP_HELP` line agree.
  Fix: drop `summary`, or derive `TOP_HELP`'s command lines from it, and add a test that each `help` begins with its `usage`.
- `grammar.ts:172` (`default:` of the `switch`) is unreachable and its message (`unrecognized arguments: <all argv>`) is wrong if reached; a `never` check or a table keyed by command makes the missing case a compile error.
- `grammar.ts:109, 116-118, 167` cast stringly typed values (`as "d" | "s"`, `as Filters["kind"]`, `as Raises`) and `grammar-records.ts:56` repeats the scope names, where `parser.py` takes them from `Scope`; a change in `#core` leaves `tsc` silent.
  Fix: build the choices from `#core`'s values where they are exported, otherwise add a test that every declared choice is accepted by `filters`.
- `args.ts:64` names the caught value `error`, shadowing the local function `error` of line 53; biome does not mind, a reader does.

## Pass 3: design

- Exports: `ts/src/cli/index.ts` gives `parse`, `Command`, `ThreadCommand`, `Exit`, exactly the plan's Produces; the type of `Command` equals the plan's field for field (`grammar.ts:5-58`).
  `ThreadCommand` is exported through the front door, so knip with `includeEntryExports` (Task 8) will find a reader only when Task 7a's thread output imports it: the plan's practice review I-2 asks for exactly this.
- Files: three modules beyond the plan's (`grammar-data.ts`, `grammar-records.ts`, `grammar-threads.ts`) exist to keep each under 300 lines; the report says so and the structure test accepts them (depcruise: no cycle; `#core` is the only import).
  The static help bodies avoid a second help formatter, a fair trade, with the drift risk of M-5 and with the argparse-version risk of M-1; they are not reproducible in the repo (the differential was throwaway), so no test pins them against lodge 0.2 beyond the draft sentence.
  Minor, and the right place for a fix is Task 7a's carried help tests, not here.
- Lane merge with Task 3: Task 3 is already on `server-api` (`920b23f` in `3b3eeb0`).
  Trial merge: `ts/package.json` auto-merges (both lanes add the identical `#cli` line); `ts/src/cli/index.ts` is an add/add conflict, resolved by keeping both blocks with the `./grammar.ts` line between `./files.ts` and `./settings.ts`; biome, tsc, depcruise, knip, and `bun test` pass after the resolution (1423 pass).
  The coordinator should expect that one conflict and no other.
- Plan assumption against the code: the plan's step list says "`ThreadCommand` of `grammar.ts`" is read by a later task; `Exit`'s `kind: "exit"` shape is relied on by Task 7a's `run` (`parse` result narrowing at `grammar.ts:96`), which the plan does not state; the shape is in the plan's Produces, so no change needed.
- Plan rule no test enforces: "help bodies and wrapped usage lines follow argparse's layout at 80 columns as far as the carried tests and probe 6 check them" has no test in this task for wrapped usage (`search`, `ask`); `grammar.test.ts` checks a prefix only.
  Covered in M-5.

## Files read

`CLAUDE.md`; plan header, Global Constraints, Exports, Calls made, Review Focus, Order and lanes, Task 2 and Task 3; `task-2-brief.md`; `task-2-report.md`; `probes.md` item 6; the whole diff `42a852a..c7185d4` (`args.ts`, `grammar.ts`, `grammar-data.ts`, `grammar-records.ts`, `grammar-threads.ts`, `index.ts`, `package.json`, both test files); lodge 0.2's `src/lodge/cli/parser.py` and `threads.py` (lines 55 to 140), `tests/e2e/test_help_lists_every_command.py`, `tests/e2e/test_search_limit.py`; `scripts/check-ts.sh`.

Not read: `ts/tests/structure/*` (only run), `ts/knip.json` and `biome.json` (unchanged by the diff, confirmed by the diffstat), Task 3's code (only the trial merge and `index.ts`), `plan-review-*` files, other tests of lodge 0.2 beyond the greps for `usage` and `--limit`.
