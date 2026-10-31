# Task 4 review: thread operations, and the store's commit

Reviewed: commit a64c88e on `lodge-viewer`, diff `git diff 9c57b8c a64c88e -- src tests`, in a detached scratch worktree of a64c88e.
Requirements: `task-4-brief.md`, `task-4-report.md`, the design's Confirming section (`docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md`, lines 48 to 73), d-7w5aq0, and d-a3h9f3.

Counts: 0 Blocking, 1 Important, 10 Minor.

## What was run

- `sh scripts/check.sh` in the scratch worktree, outside the sandbox, socket tests included: exit 0, `1217 passed`, ruff, mypy, vulture, and `lodge check --gate` clean.
- `uv run pytest tests/app/test_thread_ops.py tests/gitstore/test_commit.py -q`: `42 passed`.
- Git probes in scratch repositories under the scratchpad with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, git 2.56.0, calling `commit_paths` directly:
  - a failing `pre-commit` hook gives `FAILED`, detail `nope`, `HEAD` unchanged, and both the named file and the other staged file still staged;
  - a failing `commit-msg` hook that prints nothing gives `FAILED` with detail `""`, files still staged;
  - a path not in the index gives `FAILED` with git's `pathspec ... did not match` line;
  - `git commit --only -- 'a*.md'` with `a1.md`, `a2.md`, and `other.txt` staged commits both `a*` files; with `git -C DIR --literal-pathspecs`, or `GIT_LITERAL_PATHSPECS=1`, only the file literally named `c*.md` (or `d*.md`) is committed and `cc.md` (or `dd.md`) stays staged;
  - `git rev-parse --git-path MERGE_HEAD --git-path sequencer --git-path rebase-merge` prints one path per line, per worktree in a linked worktree.
- `open_store(repo, StoreSettings(), FixedClock()).commit(...)` on a checkout project: `ON_BASE` on `main`, `COMMITTED` after `git switch -c work`.
- App probes over `MemoryStore`: three rejections raise `Conflict` with nothing published; a `FAILED` commit result reaches `Written.committed` unchanged; a thread whose `about` names no record makes `Lodge.thread` raise `KeyError: 's-zzzzzz'`.
- The scratch probe files were deleted after each run; nothing in the reviewed tree was edited except this file.

## Correctness: the git layer

Verified against the brief and design lines 65 to 70, with no finding beyond the Minors below:

- Only the named paths are committed and other staged files stay staged (`test_commits_only_the_named_paths`, and the hook probe above).
- No identity of its own and no `--no-verify` (`src/lodge/gitstore/commit.py:35`); `test_commit_takes_the_checkouts_identity` removes the test environment's identity variables first, so it does show the checkout's configured name is used.
- Order of the guards matches the brief (`commit.py:19` to `33`): detached, then base, then the six git paths; the paths come from `--git-path`, so a linked worktree reads its own `MERGE_HEAD`, `rebase-merge`, and `sequencer` (probe above).
- Merge, revert, and cherry-pick are real conflicting operations (`tests/gitstore/test_commit.py:61` to `72`); `REVERT_HEAD` is still there after the revert case, so `--only` did not conclude it (plan ruling 25).
- One retry after `retry_seconds` on `index.lock`, then `LOCKED` (`commit.py:34` to `42`); both lock tests pass, and a lock never touches the index, so the files stay staged.
- `BranchStore.commit` raises the brief's `LodgeError` (`src/lodge/gitstore/branch.py:41`), and `threads.write` never calls it, since branch mode returns `PUBLISHED` (`src/lodge/app/threads.py:95` to `99`).

## Correctness: the thread operations

Verified with no finding beyond those below: `q-` IDs minted against decisions, entries, and threads (`threads.py:60`); `ask` resolves an ID or a code and refuses a thread ID ("no record named"); author messages need a non-blank `where` and default `when` to the clock's minute; agent messages refuse `where` and `when` and stamp seconds; `Author`, `the author`, and an empty role are refused; text loses CR before LF and outer whitespace only (a lone CR and inner blank lines survive, probed); an unstorable `where`, `when`, or `by` is a `LodgeError` naming the field and nothing is published; `reply` and `close` refuse a closed thread, also after a rejected publish re-reads one closed meanwhile; `close` without text, or with text that cleans to empty, appends an empty message by the closer (d-a3h9f3); a failing check returns `CHECK_FAILED` with nothing written; three rejections raise `Conflict`; `threads_waiting` puts author-last open threads under `for_agent`.

### Important

**I1. A thread whose `about` names no record crashes `Lodge.thread` with a `KeyError`.**
Handle: `src/lodge/app/threads.py:122`, which calls `core.level1(..., thread.about, ...)`; `level1` indexes `s.entries[record_id]` (`src/lodge/core/views.py:69`).
Scenario: a thread file is hand-edited, or arrives in a merge without its record, so its `about` is `s-zzzzzz`; `parse_thread` accepts any `d-` or `s-` ID (`src/lodge/core/threads.py:41`), so the thread loads and check 2 fails it, exactly the state design line 100 names.
`Lodge.thread("q-111111")` then raises `KeyError: 's-zzzzzz'` (probed over `MemoryStore`); neither `src/lodge/main.py:112` nor `cli/commands.py` catches it, so Task 5's `lodge thread` prints a traceback, against the global constraint "no traceback reaches the user" and the first spec's must-not 1 answer that a record failing the check is shown as failing (`docs/superpowers/specs/2026-10-29-lodge-design.md:63`).
The same state leaves `ThreadList.titles` and `ThreadsWaiting.titles` without a key for that thread (`threads.py:108`), so Task 5's `thread_head(t, title)` fed with `titles[t.about]` fails the same way.
Fix: make `ThreadShown.about` `Level1 | None`, None when `thread.about` is in neither `decisions` nor `entries`, and tell Task 5 and Task 7 to read `titles.get(about)` and show the thread as failing check 2; or, if the interface must stay, raise `LodgeError(f"{thread.id} is about {thread.about}, which lodge does not hold; lodge check names the problem")` in `show`.
The first changes a Produces line of the plan, so it needs a coordinator ruling; add `test_thread_about_a_missing_record_reads` to `tests/app/test_thread_ops.py` (225 lines, room for it).

## Practice

### Minor

**M1. A failure that prints nothing gives an empty `detail`.**
Handle: `src/lodge/gitstore/commit.py:39`.
Scenario: a `commit-msg` hook exits 1 silently (probed: detail `""`); Task 6b's notice says "the terminal running lodge view says why", and the terminal then gets an empty line.
Fix: `first_line(done.stderr, done.stdout) or f"git commit exited with status {done.returncode}"`, as `run_bytes` falls back (`src/lodge/gitstore/git.py:70`).

**M2. Paths are passed as pathspecs, so a glob character widens the commit.**
Handle: `src/lodge/gitstore/commit.py:35`.
Scenario: `Store.commit` is a port taking any paths, and `Added.paths` includes attachment paths (`src/lodge/app/writes.py:113`), whose names are command-line base names (`src/lodge/cli/commands.py:114`); a path `lodge/attachments/d-x/a*.md` would commit every staged `a….md` (probed with `a*.md`).
No caller passes an attachment today (threads and Task 6a's confirmation write fixed names), so this is latent.
Fix: `attempt(["--literal-pathspecs", "commit", "--only", ...], root)`, since `git -C DIR --literal-pathspecs commit` is valid; `env={"GIT_LITERAL_PATHSPECS": "1"}` does the same; both probed to commit only `c*.md` (or `d*.md`) and leave `cc.md` (or `dd.md`) staged.

**M3. Six `git rev-parse` processes per commit where one does.**
Handle: `src/lodge/gitstore/commit.py:24` to `33`.
Fix: one `run(["rev-parse", *(a for n in NAMES for a in ("--git-path", n))], root).splitlines()`, probed to print one path per line, per worktree.

**M4. No test reaches `CheckoutStore.commit` or `BranchStore.commit`.**
Handle: `src/lodge/gitstore/checkout.py:38`, `src/lodge/gitstore/branch.py:41`; `git grep '\.commit('` in `tests` finds only `Interleaved.commit`.
Scenario: a wrong argument in the two-line delegation (the base, or the retry) would pass every test, and Tasks 5 to 7 never commit through a real store (Task 6b's routes run on `staged_world()`).
The probe above shows the wiring is right today.
Fix: in `tests/gitstore/test_commit.py` (129 lines), `test_checkout_store_commits_by_path` through `open_store` (`ON_BASE` on `main`, `COMMITTED` on a work branch), and `test_branch_store_refuses_commit`.

**M5. The retry interval is a literal in two places, and `open_store`'s keyword has no caller.**
Handle: `src/lodge/gitstore/setup.py:33` and `src/lodge/gitstore/checkout.py:29`, both `1.0`; `git grep index_retry_seconds` finds no caller passing it.
Fix: drop the keyword from `open_store` (the brief's Produces names only the `CheckoutStore` parameter), or name the value `INDEX_RETRY_SECONDS` beside `LOCK_WAIT_SECONDS` and use it in both.

**M6. Two docstrings were deleted to meet the eight-line cap, and the new port method has none.**
Handle: `src/lodge/gitstore/checkout.py:41` and `47` lost "The working tree, and the tree at the merge base of `HEAD` with the base branch." and its sibling (report, "removed two redundant method docstrings"); `src/lodge/app/ports.py:46` declares `commit` with no docstring, while `trees`, `freshness`, `gate`, and `publish` each state their contract.
The first fact is not in the `Store` protocol's docstring, so it is lost, not deduplicated.
Fix: restore both (267 lines, under the limit; the cap is the brief's, so the coordinator rules on two lines over it), and give `Store.commit` one: "Commit exactly `paths` with the checkout's identity and hooks, leaving other staged files staged; the outcome says why when it does not commit."
The module docstring of `commit.py:1`, "preserving git's identity, hooks", reads better as "with the checkout's identity and hooks".

**M7. The CR-and-whitespace rule is written twice, and Task 6a needs it a third time.**
Handle: `src/lodge/app/threads.py:25` and `src/lodge/core/threads.py:138`, both `replace("\r\n", "\n").strip()`.
Fix: one core function, for example `clean_text(text: str) -> str` in `core/threads.py`, used by `_message`, `appended`, and Task 6a's `confirm`.

**M8. `threads.write` switches mode on a `None` sentinel and two positional booleans.**
Handle: `src/lodge/app/threads.py:43` to `102` (60 lines, nine parameters, `raises is None` meaning reply or close); `src/lodge/app/lodge.py:99` calls `threads.write(self._w, thread, None, by, text or "", where, when, commit, True)`.
Fix: a builder per operation (`_opened(state, ref, raises, message, now)` and `_appended(state, ref, message, close)`) passed to one publish loop, or at least `close` and `commit` keyword-only; `description` also changes meaning at line 91, which a second name avoids.

**M9. Three tests pass on weaker code than they name.**
Handle and scenario:
- `tests/app/test_thread_ops.py:77`: `match=r"role|author|by"` would accept any refusal mentioning "author", so a reworded message goes unnoticed; match `write author exactly, or use your own role` for the two role spellings and `by needs a non-empty role` for the empty one.
- `tests/app/test_thread_ops.py:179` to `187`: `FixedClock()` has `step=0`, so every `opened` ties and the order comes from the IDs, which count up; sorting by ID alone would pass; use `FixedClock(step=timedelta(minutes=1))` with `CountingIds(first=9, step=-1)` so time and ID disagree.
- `tests/gitstore/test_commit.py:62`: `conflict` starts with `git reset --hard`, which unstages `one.txt` and `other.txt`, so the merge, revert, and cherry-pick tests never show the named file stays staged; stage `one.txt` after the conflict and assert it is in `git diff --cached --name-only` after `perform`.

**M10. The brief's "at most three times, then `Conflict`" has no test.**
Handle: `src/lodge/app/threads.py:54` and `102`; `test_rejected_publish_starts_again` covers one rejection only.
Fix: `test_three_rejections_are_a_conflict` (`store.reject_next({}, {}, {})`, `Conflict`, `store.publishes == []`), probed to pass.

## Design

Every name in the brief's Produces exists with the brief's signature, and each consumer reads what it needs:

- Task 5: `Lodge.ask`, `reply`, `close`, `threads`, `thread`, `threads_waiting`, `Written.ids` and `outcome`, `ThreadList.titles`, `ThreadsWaiting`; the command line passes no `commit`, so the default `False` holds (I1 is the one gap).
- Task 6a: `Store.commit`, `Committed`, and `Added.paths`, filled only on `PUBLISHED` and `STAGED` (`writes.py:113`); a confirmation publishes one new decision file, so `added.paths` is exactly that path.
- Task 6b: `Written.committed` is None unless a commit ran, `CommitOutcome` carries each notice's case, `Written.about` and `ids[0]` give `/r/{about}?done={code}#{q}`; `Committed.detail` feeds stderr (M1).
- Task 7: `Shown.threads` holds the record's threads, closed ones included, newest last (`src/lodge/app/reads.py:48`).

Structure holds: git runs only in `gitstore` (`commit.py` through `gitstore.git`), `app/threads.py` reads the clock and IDs only through the ports, every module is under 300 lines (`checkout.py` 265, `writes.py` 214, `threads.py` 133), and the structure tests pass.
The design's "retries once after a second" (line 70) is the default `1.0`; its list of operations (line 69) is widened to revert and the sequencer by plan ruling 25, which the code follows.

## Files

Read: `CLAUDE.md`; `docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md` (lines 1 to 140); `docs/superpowers/specs/2026-10-29-lodge-design.md` (Must nots and the review flag, lines 53 to 65 and 171 to 194); the plan's Tasks 4 to 6b and its task list (`docs/superpowers/plans/2026-10-31-lodge-viewer.md`, lines 257 to 457, and the ruling lines 61 to 72 by search); `task-4-brief.md`; `task-4-report.md`; d-7w5aq0 and d-a3h9f3 with reasoning; every file in the diff (`src/lodge/app/{__init__,lodge,ports,reads,results,threads,writes}.py`, `src/lodge/gitstore/{branch,checkout,commit,setup}.py`, `tests/app/{fakes,test_thread_ops}.py`, `tests/gitstore/{test_commit,test_concurrent}.py`); `src/lodge/gitstore/git.py`; `src/lodge/app/state.py`; `src/lodge/core/threads.py`; `src/lodge/core/search.py` (`resolve`); `src/lodge/core/views.py` (`level1`); `src/lodge/core/check_change.py` (`check_change`); `tests/gitstore/repos.py` (helpers).
Not read: the rest of the plan (Tasks 1 to 3, 7 to 11 beyond their Consumes lines); `advisor-ruling.md` and `advisor-ruling-2.md`; `src/lodge/gitstore/{published,plumbing,trees,lock,accepted}.py` beyond `published.py`'s use of `base`; `src/lodge/core/check_*.py` other than `check_change.py`; the Task 3 review and `task-4-codex-final.txt`.
