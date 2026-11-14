# Task 2, fix round 1

Read `CLAUDE.md`, then `task-2-brief.md`, `task-2-report.md`, and `task-2-review.md` in this folder (history: do not edit them).
Worktree: this one (lane A, branch `server-api-a`), on top of `c7185d4`.
Test-first: see each new or changed test fail before its fix; all existing tests keep passing; gate `sh scripts/check-ts.sh`.

The reference is lodge 0.2's real argparse (`src/lodge/cli`, run with Python from the repository's environment); a case counts as fixed when the branch's result equals it byte for byte, so pin each case below as a test with lodge 0.2's captured message and exit code.

1. **I-1** (`ts/src/cli/args.ts:120-129`): `add` pools every non-option word into the file list, even after an option.
   `lodge add a t --dry-run x` must exit 2 with `unrecognized arguments: x`, and `add d-aaaaaa --s a builder` must list `--s a builder` as lodge 0.2 does.
   Compare more shapes the same way (words after options for every command with positionals), and put the ones you check into the tests.
2. **M-1**: `--` is dropped from the leftover words when the command has positionals; match lodge 0.2 (Python 3.13.5 is the reference).
3. **M-2**: `id x --help` must give lodge 0.2's invalid-choice error, and `--limit -.5` must not be taken as an option.
4. **M-3**: add tests that kill the surviving mutations in `parse`'s top-level handling of `--version=1`, `--help=x`, `--ver`, and `--` before the command.
5. Delete the unreachable `default` in `ts/src/cli/grammar.ts` (about line 172) and the unread `Declaration.summary`, if both are really unused.

Leave M-4 and the rest of M-5 alone (parked in the ledger).
In the report, correct the claim "differences: 0": say which cases the earlier capture missed.
Do not stage any `*-codex-final.txt`.
Write `task-2-fix-1-report.md` in this folder: per finding, the test that pins it with `file:line`, and the mutation that fails it.
Commit with explicit paths as `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, push `server-api-a`.
Final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, with the commit hash.
