# Task 9, fix round 1

Fixed I-1, I-2, M-a, M-b, M-c, and M-e on `server-import-hook`.
M-d is intentionally unchanged, as requested: the hook's more permissive treatment of settings is harmless.

## Changes by file

| File | Change |
|---|---|
| `ts/src/cli/grammar-data.ts` | Give the hook its `post-tool-use` choice, argparse usage, positional label, and help spacing; place its help and declaration after `guide` and before the thread commands. |
| `ts/src/cli/hook-context.ts` | Reuse `table` from settings instead of maintaining a duplicate predicate; preserve strict `readExact`. |
| `ts/src/cli/settings.ts` | Export `table` for the hook context's internal import, without adding it to `#cli`. |
| `ts/src/main.ts` | Apply the unavailable-cwd fallback only to `hook`; other client commands retain the original `process.cwd()` failure. |
| `ts/tests/cli/grammar.test.ts` | Correct the full hook help expectation; add exact invalid-event-before-help and command-order checks. |
| `ts/tests/cli/hook-context.test.ts` | Add invalid UTF-8 inside a TOML comment, followed by otherwise valid hook settings. |
| `ts/tests/hook/entrypoint.test.ts` | Exercise a symlinked store from a session subfolder with a relative edited path; preserve non-hook cwd errors. |
| `ts/tests/hook/hand-edits.test.ts` | Reject checkout advice outside the existing reversal warning in both moved-project store modes. |

## Failing tests and mutation evidence

Every mutation below was reverted before verification.
Line handles refer to the finished files.

| Finding | Test | file:line | First failure or mutation |
|---|---|---|---|
| I-1 | `hook_help_and_summary_match_argparse` | `ts/tests/cli/grammar.test.ts:144` | Failed before implementation: received `EVENT` and two spaces after `--help`, expected `{post-tool-use}` and seven spaces. |
| I-1 | `hook_invalid_event_before_help_is_an_error` | `ts/tests/cli/grammar.test.ts:154` | Failed before implementation: received help with code 0, expected invalid choice with code 2. |
| I-2 | `malformed_hook_context_is_null` | `ts/tests/cli/hook-context.test.ts:77` | Replaced `readExact` with `readFileSync(path, "utf8")`; the comment containing byte `ff` returned a context instead of null: `22 pass`, `1 fail`. |
| M-a | `hook_precedes_threads_in_help_and_command_choices` | `ts/tests/cli/grammar.test.ts:162` | Failed before implementation: the choose-from list ended with `close, hook`, rather than putting `hook` before `threads`. |
| M-b | `main_resolves_a_symlinked_store_from_the_session_folder` | `ts/tests/hook/entrypoint.test.ts:54` | Two independent mutations, replacing the resolver with `(path) => path` and passing null for the hook cwd, each produced empty stdout and `JSON Parse error: Unexpected EOF`: `4 pass`, `1 fail` each. |
| M-c | `main_preserves_cwd_errors_for_non_hook_commands` | `ts/tests/hook/entrypoint.test.ts:80` | Failed before implementation: `Expected: not 0`, received exit 0 after making `process.cwd()` throw `working folder unavailable`, modelling the deleted-folder failure. |
| M-e | `hook_gives_the_moved_advice_for_a_project_on_the_server` | `ts/tests/hook/hand-edits.test.ts:100` | Injected `git checkout` into the rendered server value; both modes failed the final assertion after excluding the reversal warning: `11 pass`, `2 fail`. |

The first combined grammar and entrypoint run ended `52 pass`, `4 fail`.
After implementing the declaration, ordering, and cwd changes, the same run ended `56 pass`, `0 fail`.

## Verification

- `uv run --frozen --quiet lodge waiting`: nothing waiting for an agent or the author.
- Directly ran `uv run --frozen --quiet lodge hook -h`, `uv run --frozen --quiet lodge hook x -h`, `uv run --frozen --quiet lodge -h`, and `uv run --frozen --quiet lodge nosuch` to inspect Python's output.
- A temporary Bun comparison script used `Bun.spawnSync` to capture the real Python commands and `bun ts/src/main.ts` separately, with `COLUMNS=80`, and checked stdout bytes, stderr bytes, and exit codes.
- `hook -h`: stdout and stderr byte-identical; exit 0.
- `hook x -h`: stdout and stderr byte-identical; exit 2.
- `-h`: byte-identical after removing only Python's planned `view` help entry; exit 0.
- `nosuch`: byte-identical after removing only `view` from Python's choices; exit 2.
- Focused `bun test tests/cli/grammar.test.ts tests/cli/hook-context.test.ts tests/hook tests/cli/settings.test.ts`: `208 pass`, `0 fail`, `522 expect() calls`, across nine files.
- Targeted `bunx --no-install biome check --write` formatted the changed TypeScript files; exit 0, informational diagnostics only.
- `git diff --check`: exit 0.
- Final gate `sh scripts/check-ts.sh`: exit 0; `2114 pass`, `0 fail`, `7261 expect() calls`, across 189 files.
- The gate included TypeScript, dependency, unused-export, and structure checks; no dependency violations, with 43 informational Biome diagnostics.

## Coordinator ruling and deviations

The requested literal `not.toContain("git checkout")` also failed against the unmutated text because the carried reversal warning says not to run that command.
Asked `coord.ask_coordinator` whether to change moved warning wording or preserve it and exclude the warning from the assertion.
The coordinator ruled: keep the lodge 0.2 warning and existing warning assertions, remove the reversal-warning sentence for the new assertion, and change no text in `texts.ts`.
Implemented that ruling and verified the adjusted assertion against a mutation outside the warning.

The top-level comparisons preserve the existing planned omission of `view`, documented by `d-sry12f` in `ts/tests/parity.json`.
No dependency, Python, historical report, record, or warning-text changes were needed.
No unresolved questions remain.
