# Task 12 recheck 1: fix round 1 (6d8a183)

Scope: the diff 397dfb3..6d8a183 against task-12-review.md I1 and M1 to M5 and the Task 12 rulings in the ledger.

Counts: 0 Blocking, 0 Important, 2 Minor (new). Verdict: clean.

## What I ran

- `git archive 6d8a183` into a fresh scratch folder, `UV_OFFLINE=1 sh scripts/check.sh`: ruff format, ruff, mypy, vulture green, 998 passed.
- The 6d8a183 versions of `tests/hook/test_post_tool_use.py` and `tests/e2e/test_hook_feedback_after_hand_edits.py`, copied onto a `git archive 397dfb3` copy: 7 failed, 38 passed.
  Failing as they should: `test_record_advice_reverses_the_edit_without_git`, `test_frozen_advice_names_the_guide`, `test_context_is_asked_about_the_edited_file`, `test_relative_path_is_read_from_the_payload_working_folder`, `test_hook_finds_the_repository_of_the_edited_file_not_of_the_session`, `test_hook_stays_silent_where_lodge_is_not_initialised`, and `test_run_writes_one_json_line_for_a_record_edit` (signature change).
  `test_hook_finds_the_repository_for_a_file_that_does_not_exist_yet` passes on 397dfb3 too; it guards the new `_existing_folder` loop rather than proving a bug, which is fine.
- The review's probe against the real `main` hook route, repositories under a temporary folder with `GIT_CONFIG_GLOBAL` empty and `GIT_CONFIG_NOSYSTEM=1`, now with the test repository initialised (empty `lodge/decisions` and `lodge/spec`) and 7 new cases: 49 cases, every one exit 0 with empty stderr, stdout one JSON object or nothing.
  New cases: relative path with payload `cwd` in a nested worktree (fires), a file in a not yet existing deep folder (fires), `lodge/` at mode 0 (silent), a self-referencing symlink (silent), an uninitialised repository with a `lodge/` Python package (silent), uninitialised checkout mode with a frozen glob (silent, as the README says), uninitialised branch mode with a frozen glob (fires).
  The sibling-worktree case that was silent in the review now fires with the session in the main checkout.
- Script: `scratchpad/probe12/probe2.py`.

## Findings

- I1: answered, `src/lodge/hook/post_tool_use.py:14-19`, used at `:24` and `:30`; the test pins every git command after "Do not run" and no "undo".
- M1: answered, `src/lodge/main.py:63-75` (`_existing_folder`, `_hook_context(edited)`) and `post_tool_use.py:93-105` (`_edited_path` reads the payload's `cwd`).
- M2: answered, `src/lodge/gitstore/setup.py:63-67`, `main.py:74`.
  `holds_records` cannot raise into the hook: it is reached only through `context(edited)` inside `run`'s `try` (`post_tool_use.py:79-87`), and `lodge/` at mode 0 gave exit 0, silent.
  It has no other caller (`git grep holds_records`).
- M3: answered, with N2 below.
- M4: answered, `post_tool_use.py:28-29`.
- M5: settled by ruling (resolving the edited path counts as reading the hook's input); no code change, none needed.

## New problems

### N1 (Minor): a relative path without a payload `cwd` is read from two different places

Handle: `post_tool_use.py:79` passes `Path(relative)` to `context`, which `_existing_folder` resolves against the process's cwd, while `respond` at `:55` joins it to the repository root.
Scenario: process cwd `docs/`, `file_path` `choices.md`, no `cwd` key: the repository is found from `docs/`, but the frozen check sees `choices.md` at the root, not `docs/choices.md`.
Claude Code always sends an absolute `file_path` and a `cwd`, and the old code had the same root join, so this is not a regression.
Fix: in `run`, when the payload has no `cwd`, join a relative path to `Path.cwd()` (from `main`) and pass that absolute path to both `context` and `respond`; or park it.

### N2 (Minor): the README's glob line still calls the syntax `fnmatch`

Handle: `README.md:31`, "(`fnmatch` syntax, except that `*` does not cross a `/` and `[...]` is literal)".
`fnmatch` has no `**` and its `?` matches `/`, so the parenthetical is wrong in two more places and contradicts the ruling's "the syntax lodge implements".
Fix: delete the parenthetical; the sentence before it already states the rules.

## Files

Read: `rechecker.md`, the review package diff, the ledger's Task 12 lines, `scripts/check.sh`, line handles above in the 6d8a183 copy.
Not read: anything outside the diff beyond those handles.
