# Task 2, fix round 1 report

Fixed I-1, M-1, and M-2, pinned M-3, and removed the two requested unused parts of M-5.
M-4 and the remaining M-5 work stay parked.
Historical briefs, reports, and reviews are unchanged.

## Changes and reference

`args.ts` consumes each contiguous positional run before processing the next option, retaining the positional cursor across runs.
This closes an `add` file group at an option, preserves excess words in order, and validates positional choices before a subsequent help flag.
The negative-number recogniser now includes `-.5`.
The end-of-options marker survives when it belongs to leftovers, following Python 3.13.5.
`grammar.ts` removes the unreachable default and narrows the command name to the command union, with the existing declaration lookup still rejecting unknown names.
`Declaration.summary` had no readers, so its property and all fifteen initialisers are removed.

The new JSON fixture captures stdout, stderr, and exit codes from the real `src/lodge/cli/parser.py` `_parser().parse_args` under the repository environment, Python 3.13.5, lodge 0.2.0, and `COLUMNS=80`.
All twenty exit cases compare the complete result byte for byte, with the version argument set to `0.2.0`.
The additional `-- show d` case was checked against the same parser's successful namespace and pins the equivalent typed command.
No runtime Python dependency or package was added.

## Test-first and mutation evidence

The first behavioural run of the twenty captures plus the successful marker case had 13 passes and 8 failures before implementation changes.
Failures were four `add` run-boundary cases, two marker cases, invalid positional choice before help, and the negative decimal converter message.
The other cases already matched the reference and were then checked against deliberate mutations.
Each mutation below was applied separately, run against the new test file, and restored.
The test runner is `ts/tests/cli/argparse-fix.test.ts:7`, with the successful command case at line 12.
Fixture line references identify each parameterised test's input and exact expected output.

| Finding | Test with file:line | Mutation caught and result |
|---|---|---|
| I-1 | `ts/tests/cli/argparse-fix-cases.json:3`, `:12`, `:21`, `:30` | Remove consumption before options, pooling positional runs again: 6 failures, including all four `add` cases. |
| I-1, other positional commands | `ts/tests/cli/argparse-fix-cases.json:39`, `:48`, `:57`, `:66`, `:75`, `:84`, `:93`, `:102` | Disable the leftover error: 15 failures, including these cases for id, search, show, draft, thread, ask, reply, and close. |
| M-1 | `ts/tests/cli/argparse-fix-cases.json:111`, `:120`, `:129` | Drop retained markers: 2 failures for show and add; disabling the leftover error also fails the search case. |
| M-2, choice | `ts/tests/cli/argparse-fix-cases.json:138` | Remove consumption before options: invalid choice loses to help, among 6 failures. |
| M-2, number | `ts/tests/cli/argparse-fix-cases.json:147` | Restore the old negative-number regexp: 1 failure. |
| M-3, explicit values | `ts/tests/cli/argparse-fix-cases.json:156`, `:165` | Disable the top-level explicit-value rejection: 2 failures. |
| M-3, abbreviation | `ts/tests/cli/argparse-fix-cases.json:174` | Match version only exactly: 1 failure. |
| M-3, marker | `ts/tests/cli/argparse-fix.test.ts:12` | Disable top-level marker handling: 1 failure. |
| M-5, requested removals | `ts/src/cli/args.ts:13`, `ts/src/cli/grammar.ts:102` | No behavioural test for dead declarations or unreachable code; TypeScript, Knip, and the full gate pass after removal. |

## Correction to the earlier report

The earlier statement `differences: 0` described only its 122 captured cases, not parser parity in general.
That capture missed words following an option inside `add`'s multi-file positional, words following an unknown option after that positional, leftover `--` markers on commands with positionals, invalid positional choices preceding help, and negative fractional option values such as `-.5`.
Its claim that continuing a multi-file positional after an option was required was incorrect.
The current captures exercise those omissions and additional leftover shapes for every command with positionals.
This report corrects those claims without editing the historical report.

## Validation

`uv run --frozen --quiet lodge waiting` reported nothing waiting for an agent or the author.
`uv run --frozen --quiet python` captured twenty reference exits with Python 3.13.5.
`bun test tests/cli` passed 76 tests with 92 assertions after the fixes.
`bunx biome check --write --error-on-warnings src/cli tests/cli` passed.
The first full gate identified the missing exhaustive command narrowing and JSON literal typing; both were corrected.
`sh scripts/check-ts.sh` then passed Biome, TypeScript, dependency checks, Knip, and 1378 tests, with 2 todos, 0 failures, and 3475 assertions.
The final gate was repeated after restoring all mutations.
Tests use synthetic inputs and open no sockets.
No historical document, dependency, structure rule, or final-message scratch file is staged.
No unresolved concern remains within this fix brief's scope.
