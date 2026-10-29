# Task 12 review: the hook

Commit bc73e71 (base 0844da8), worktree `build-0.1`, reviewed read-only.

## Verdicts

Spec compliance: yes.
The hook fires after `Edit`, `Write`, and `MultiEdit` on a record file or a frozen file, names the file and the lodge operation, never blocks, and in branch mode applies only the frozen globs (spec, "A hook against writing elsewhere"; brief, Interfaces).
The carried rulings hold: `main` calls `parse_hook_settings` for every command but the hook route, an argv starting with `hook` skips parsing and exits 0, the text names `lodge add --dry-run` before `lodge add`, and `README.md` gained only the hook section.

Task quality: not approved, 1 Important.

Counts: 0 Blocking, 1 Important, 5 Minor.

## What I ran

- `git archive bc73e71` into a scratch folder; probes ran the real `lodge.main.main(["hook", "post-tool-use"])` as a subprocess with `PYTHONPATH` on the scratch `src`, in repositories under a temporary directory with `GIT_CONFIG_GLOBAL` an empty file and `GIT_CONFIG_NOSYSTEM=1`.
- Script: `scratchpad/probe12/probe.py` (beside this file); 46 cases, every one exit 0 with empty stderr.
- `pytest tests/hook tests/e2e/test_hook_feedback_after_hand_edits.py tests/test_structure.py`: 77 passed.
- The README's JSON block through `json.loads`: parses, `hooks.PostToolUse[0]` is `{"matcher": "Edit|Write|MultiEdit", "hooks": [{"type": "command", "command": "lodge hook post-tool-use"}]}`, the shape Claude Code's settings take.

## Focus 1: never breaks a session

Verified silent with exit 0 for: empty stdin, `{not json`, `[1,2]`, `null`, invalid UTF-8 bytes, 100,000 nested `[` (RecursionError, swallowed), missing `tool_input`, `tool_input` a string, `file_path` an integer, a NUL byte in the path, `Read` and `Bash` tool calls, a path outside the repository, a path under the home directory, cwd outside any repository, a malformed `.lodge.toml`, `.lodge.toml` with bad UTF-8, `.lodge.toml` unreadable (mode 0), an unknown `[hook]` key, `lodge hook`, `lodge hook other`, `lodge hook post-tool-use extra`.
Git's stderr is captured by `gitstore.git.run_bytes`, so nothing leaks.
When it speaks, stdout is exactly one JSON object and a newline.
Only `lodge hook --help` prints usage on stdout, which no settings file would configure.
Repository without `.lodge.toml`: checkout-mode defaults apply, so record edits get feedback and frozen globs are empty; that is correct, since `lodge init` writes no `.lodge.toml` (`src/lodge/gitstore/setup.py:40-55`).

## Focus 3: path matching

Fires (correct): absolute record path, relative `lodge/decisions/d.md`, a record reached through a symlinked checkout, `lodge/attachmentsX/x.md` (not the attachments folder), frozen `docs/choices.md`, `docs/**/verd?cts.md` against `docs/a/b/verdicts.md` and `docs/verdicts.md`, cwd in a subfolder, branch mode for frozen files.
Silent (correct): `lodge/attachments/d-abc123/x.txt`, `lodge-notes/x.md`, `src/lodge/x.py`, `lodge.md`, `docs/choices.md.bak`, `x/docs/choices.md`, branch mode for a record path.
`Path.is_relative_to` compares whole components, so similarly named folders cannot match.

## Findings

### I1 (Important): "Undo the hand edit with git" can discard work that is not the agent's

Handle: `src/lodge/hook/post_tool_use.py:19` and `:24`.
The natural reading for an agent is `git checkout -- FILE` or `git restore FILE`, both of which reset the whole file to the index, not the one edit.
Scenario, frozen file: the author has uncommitted, unstaged edits in `docs/choices.md` (say, the note marking it frozen, or any uncommitted change); an agent edits a line, gets the advice, runs `git checkout -- docs/choices.md`, and the author's uncommitted changes are gone with no copy anywhere.
Scenario, record file in checkout mode: `lodge add` writes and stages but never commits (plan, "Calls made", Checkout mode), so an agent that reaches for `git checkout HEAD -- FILE`, `git restore --source=HEAD --staged --worktree FILE`, or `git stash` also throws away records published by an earlier `lodge add` in the same uncommitted change; after a `Write` that created a new file, "undo with git" invites `git clean`.
The undo itself is needed: checkout mode reads the working tree as current (`src/lodge/gitstore/checkout.py:1`, `:31`), so a hand edit left in place becomes the base of the next `lodge draft` and travels with the next `lodge add`.
Fix: make the agent reverse only its own change, and forbid the whole-file git commands, for example:
"Reverse your own edit now: put back exactly the text you replaced, with the same tool. Do not run `git checkout`, `git restore`, `git stash`, or `git clean` on this file, since they also discard changes that are not yours. If you cannot restore it exactly, tell the author."
Add a unit test that the text names no git command that rewrites the file (for example asserts `"git checkout"` and `"git restore"` appear only after "Do not").

### M1 (Minor): the repository is found from the session's cwd, not from the edited file

Handle: `src/lodge/main.py` `_hook_context` (`repo_root(Path.cwd())`).
Verified: with cwd at the main checkout, an edit of `.claude/worktrees/w/lodge/decisions/d.md` is silent; with cwd in that worktree it fires.
This project's own coordinator works from one worktree and edits files in the sibling worktree `build-0.1`, so the pilot's count of occasions would miss exactly those.
Fix: find the repository from the nearest existing ancestor of the edited file (relative paths joined to the payload's `cwd`), and read that repository's `.lodge.toml`.
It changes `run`'s `context` from `Callable[[], ...]` to one taking the path, which the brief fixes, so it needs a ledger ruling; deferring to 0.2 is defensible.

### M2 (Minor): fires in any repository that has a top-level `lodge/` folder

Handle: `src/lodge/main.py` `_hook_context`, `src/lodge/gitstore/setup.py:58-60`.
A hook placed in user-level settings tells an agent in an unrelated flat-layout Python package called `lodge` that every source file is a record.
Fix: have `_hook_context` return None when the data folder does not exist (`data_folder_exists`, already in `gitstore`), and have the README say project settings, not user settings.

### M3 (Minor): the glob syntax is not documented and differs from shell globs

Handle: `src/lodge/hook/post_tool_use.py:97-118`, `README.md` hook section.
`[abc]` is matched literally and a leading `/` never matches, silently; a user writing `/docs/choices.md` gets no feedback and no error.
Fix: one README line ("`*` and `?` within a folder, `**` across folders, relative to the repository root, no leading slash"), and either reject a leading `/` in `parse_hook_settings` or strip it.

### M4 (Minor): the frozen text says "write a draft" without saying how

Handle: `src/lodge/hook/post_tool_use.py:21-23`.
An agent that has never used lodge gets no route to the draft format.
Fix: add "(`lodge guide` shows the draft format)".

### M5 (Minor): `respond` touches the filesystem through `Path.resolve()`

Handle: `src/lodge/hook/post_tool_use.py:52-53`.
The plan's I/O line says "`hook` reads stdin only" (Global Constraints, LODGE-5); `resolve()` reads no file content but does `lstat` and `readlink`, and no structure rule checks `hook`'s I/O (`tests/structure_rules.py` names no hook rule).
Resolving is what makes symlinked checkouts match, so keep it; record a one-line ruling that path resolution is allowed in `hook`.

## Practice and design notes without findings

- `main._settings` and `_hook_context` both read `raw.get("hook", {})`; the duplication is two lines and keeps the hook route free of the commands' settings errors, so it is right.
- `parse_hook_settings(table: object)` against the brief's `Mapping[str, object]` is a sound widening; `hook = 3` gives one sentence.
- The hand-rolled glob is justified: `PurePath.full_match` needs Python 3.13 and the project requires 3.12.

## Files

Read: `.claude/agents/reviewer.md`, `task-12-brief.md`, `task-12-report.md`, the review package diff (README, `hook/__init__.py`, `hook/post_tool_use.py`, `main.py`, the e2e test), lines 1 to 60 of `tests/hook/test_post_tool_use.py`, the spec's "A hook against writing elsewhere", the plan's Global Constraints, "Calls made in this plan", and Task 12, `cli/parser.py:75-95`, `cli/commands.py:60-85`, `gitstore/setup.py`, `gitstore/git.py:42-66`, `gitstore/settings.py:33-49`.
Not read: the rest of `tests/hook/test_post_tool_use.py`, `gitstore/checkout.py` beyond its docstrings, the spec's Structure section (taken from the plan's restatement), `CLAUDE.md` beyond the dispatch's copy.
