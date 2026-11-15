# Task 2, recheck of fix round 1

Scope: `git diff a4808db 059868b` (commit `059868b`), run in a scratch worktree at that commit, removed afterwards.
Reference: lodge 0.2 `_parser().parse_args` from the repository environment, Python 3.13.5, `COLUMNS=80`.

## Differential

120000 random argv (twelve shards of 10000) over every command, built from words, each command's options (full, abbreviated, `=` forms), `--`, `-h`, `-1`, `-.5`, `-`, unknown options, lengths 0 to 5, plus the full length-0-to-3 space for the sampled commands.
Exit code, stdout, and stderr compared byte for byte for exits; the positional and option values compared for successes.
Normalised away: the `choose from` list (view and hook, d-sry12f) and the top-level help body for the same reason.
Result: 0 differences.
The same harness on `a4808db` shows 705 differences in one 10000-case shard, so it detects the old bugs.
Cases with the token `--=` were excluded: both versions give `ignored explicit argument ''` where argparse gives `ambiguous option`; this is older than the fix (checked on `a4808db`) and outside it.
The thread message rule (`--where` without `--by author`) lives after `parse_args` in Python and was not compared.

## I-1: resolved

`ts/src/cli/args.ts:74-90` (`consumeWords`) hands the positional run to the positionals when an option arrives and keeps the cursor (`positionalIndex`), so a run closed by an option cannot be extended.
`add a t --dry-run x` and `add d-aaaaaa --s a builder` match; pinned at `ts/tests/cli/argparse-fix-cases.json:3,12,21,30`, with eight other commands at `:39` to `:102`.
Mutation (drop the call before options): 6 failures.
Mutation (leftover error disabled) fails the other commands' cases.

## M-1: resolved

`args.ts:94-103` keeps `--` in the leftovers when no positional is left to take it, as Python 3.13.5 does.
Pinned at `argparse-fix-cases.json:111,120,129`; mutations "always drop" (2 failures) and "only when no positionals" (1 failure) both fail.

## M-2: resolved for the option value; one same-kind gap at the top level

`id x --help` is an invalid-choice error (`argparse-fix-cases.json:138`; mutation without the early consumption fails it).
`--limit -.5` is no longer an option (`args.ts:54`, the regular expression `^-(?:\d+|\d*\.\d+)$`; `:147`; the old expression fails 1 test).
See N-1 for the same rule before the command.

## M-3: resolved

`--version=1` and `--help=x` (`argparse-fix-cases.json:156,165`): disabling the explicit-argument rejection gives 2 failures.
`--ver` (`:174`): exact-only version matching gives 1 failure.
`--` before the command (`argparse-fix.test.ts:12`): removing the branch, and removing `index++`, each give 1 failure.
One neighbouring mutation survives: matching `--help` abbreviations exactly (`grammar.ts:77`, `"--help".startsWith(key)` to `=== key`) fails no test, so `--he` is unpinned (Minor, N-2).

## Dead code: resolved

`Declaration.summary` and its fifteen initialisers are gone (`grep -rn summary ts/src` is empty); the unreachable `default` in `grammar.ts` is gone, replaced by the typed narrowing at `grammar.ts:88-89`.
Gate `sh scripts/check-ts.sh` in the scratch worktree: Biome, types, dependency rules, Knip, 1378 pass, 0 fail.

## Hygiene

No personal path, machine name, or em-dash in the added lines; fixtures synthetic; all modules at most 225 lines; no structure rule or dependency touched; the report names its test per finding as asked and corrects "differences: 0" with the five missed shapes.
Untracked `task-2-codex-final.txt` and `task-2-fix-1-codex-final.txt` remain unstaged.

## New findings

Blocking 0, Important 0, Minor 2.

### N-1 (Minor): `-.5` before the command still takes the old negative-number rule

Handle: `ts/src/cli/grammar.ts:75` keeps `/^-\d+(?:\.\d+)?$/u`, while `args.ts:54` was widened.
`lodge -.5` gives lodge 0.2 `argument COMMAND: invalid choice: '-.5'`; the branch gives `the following arguments are required: COMMAND`.
`lodge -.5 show d` gives `unrecognized arguments: -.5` in the branch against the invalid-choice error.
Harm: only the message of a nonsense invocation.
Fix: share one `looksNegativeNumber` between the two files and pin `-.5` in `argparse-fix-cases.json`.

### N-2 (Minor): `--he` (help abbreviation at top level) is pinned by no test

Handle: `ts/src/cli/grammar.ts:77`; mutation above survives.
Fix: one case `["--he"]` expecting the top help.
