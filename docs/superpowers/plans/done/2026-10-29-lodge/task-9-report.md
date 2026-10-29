# Task 9 report: the git store

Status: DONE_WITH_CONCERNS (concerns are design choices the brief left open, none blocking).

## Built

`src/lodge/gitstore/`: `errors.py` (`NotARepository`, `NotInitialised`, `GitMissing`, the shared not-initialised sentence), `git.py` (`attempt`, `run_bytes`, `run`, `resolve`), `lock.py`, `settings.py` (`StoreSettings`, `ProjectSettings`, `load_settings`), `trees.py` (`ls-tree` plus one `cat-file --batch`, UTF-8 with `surrogateescape`), `plumbing.py` (path guard, temporary-index commit, push), `checkout.py`, `branch.py` (store and `init_branch`), `setup.py` (`repo_root`, `open_store`, `init_store`, `data_root`), `__init__.py` (the front door, exactly the brief's names).
Tests: `tests/gitstore/{conftest,repos,test_setup,test_checkout,test_branch,test_concurrent}.py` and an empty `tests/gitstore/__init__.py`; `vulture_allow.py` gains the autouse fixture.
Largest module 124 lines.

## Test-first

All four test files were written before any code; the first run failed at collection:

```
tests/gitstore/repos.py:12: from lodge.gitstore import StoreSettings, init_store, open_store
E   ImportError: cannot import name 'StoreSettings' from 'lodge.gitstore'
ERROR tests/gitstore/test_branch.py / test_checkout.py / test_concurrent.py / test_setup.py
4 errors in 0.27s
```

After the implementation the first run had one real failure, which showed git's own behaviour: a successful `git push` already moves the remote-tracking ref, so `update-ref <ref> <new> <old>` failed ("is at <new> but expected <old>").
The store now runs `update-ref <ref> <new>` without the old value (idempotent).

## Result

`sh scripts/check.sh` green: 751 passed (63 new in `tests/gitstore`).
The three concurrency tests of Step 4 pass; the two interleaved ones also assert the store saw `[REJECTED, PUBLISHED]`, so the retry path is really driven (clones: push refused as not ahead; worktrees: ref moved, refused before pushing).

## Behaviour worth knowing

- `raw` in `ProjectSettings` is the whole parsed TOML table (the brief says only `Mapping[str, object]`); main passes `raw.get("hook", {})` to `hook.parse_hook_settings`.
- `store.branch`, `remote`, `base` must match `[A-Za-z0-9][A-Za-z0-9._/-]*` without `..`, so a name can never read as a git option.
- Both modes refuse a write outside `lodge/` (`..`, empty, `.git` parts) with a `LodgeError`, before taking the lock.
- Checkout `publish` compares each written path with `base.files.get(path)`; attachments are never in `files`, so a write to an existing attachment file is `REJECTED` (only new attachment files can be created).
- "Marked stale" is an in-process flag set after a rejected push; the stamp file is left alone (so `fetch failed; data as of <time>` keeps the last real fetch time). A second process finds the stamp as it was.
- A failed fetch with no cached ref is `NotInitialised` only for "couldn't find remote ref" (git run with `LC_ALL=C` for that match); any other failure is `LodgeError("cannot fetch <remote>/<branch>: ...")`.
- `init_store` in checkout mode also `git add`s the two `.gitkeep` files (consistent with "stages, never commits"); in branch mode it checks `ls-remote --exit-code --heads` first and treats a push rejection as already initialised. Initialised in checkout mode means `lodge/` exists.
- Fetch and push take the lock; a read that needs no fetch does not. The fetch is checked twice (outside and inside the lock) so a waiting reader does not repeat a fetch another process just made.
- `git push` runs user pre-push hooks (no `--no-verify`); noted, not decided.
- Unreadable files in checkout `trees()` become `""` text, so `load` reports a stray or format problem naming the path; `publish` on an unreadable target raises `LodgeError`.

## Concerns

1. `tests/gitstore/__init__.py` exists because mypy rejects two `conftest.py` named alike without package context; the test modules therefore import `from gitstore.repos import ...` (the only package-style imports among the tests).
2. `vulture_allow.py` imports `tests.gitstore.conftest` for the same reason as the other entries (fixture looks unused to Vulture).
3. Branch mode keeps no in-repo state beyond refs and the two files `lodge.lock` and `lodge-fetched` in the git common directory.

## Fix round 1

Findings B1, I1, I2, M1 to M7 of `task-9-review.md`. Tests were written first; before the fix the new tests failed (9 of 11 in `test_checkout_safety.py`, the FIFO test hung on `open`, 4 of 6 in `test_push_race.py`/`test_branch.py` additions, with the push error `cannot lock ref ... is at X but expected Y` for I1). After: `sh scripts/check.sh` green, 791 passed (81 in `tests/gitstore`), run three times without a failure.

- B1: checkout mode `lstat`s every component of each written path under the lock and refuses a link, or anything that is not a folder on the way and a regular file at the end, with a `LodgeError` naming the path; `lodge` itself as a link, or as a file (M5), is refused in `trees()` and `init_store`; `disk_tree` reads a link as its target text and a FIFO or other special file as empty text (M3), never following either; a linked folder is listed as one entry. Tests assert the outside folder is unchanged in all four review cases.
- I1: `push` takes the parent; after any failed push it runs `ls-remote` for `refs/heads/<branch>` and returns False (so `REJECTED` and the stale mark) when the tip differs from the parent, otherwise raises git's first line. The `[rejected]` text match is gone. `tests/gitstore/test_push_race.py` rigs the remote as the reviewer's `p7` did (a one-shot `pre-receive` hook moves the branch to a commit another clone had published, the branch having been put back first): the store returns `REJECTED`, and `add` over it ends `PUBLISHED` with all three decisions on the remote and `check_state` clean.
- I2: checkout `publish` writes every file to a `.<name>.lodge-tmp` sibling, replaces them, then stages; on any `OSError` or failed `git add` it removes temporaries, restores prior bytes, removes folders it made, and puts the index entries back (a failing `git add` of an ignored path had already staged the others); the error is a `LodgeError` naming the path. The stamp write turns an `OSError` into a `LodgeError`.
- M1: the stamp holds `<tracking ref> <time>`; a stamp for another ref counts as never fetched.
- M2: `remote_tip` runs `ls-remote <remote> refs/heads/<branch>` and compares the printed ref exactly; init uses it.
- M4: a non-blob entry under `lodge/` (a gitlink) gets empty text in `files`, so `load` reports it as stray.
- M6: `KEPT` lives in `trees.py`, used by both modes.
- M7: both modes refuse (`LodgeError`) a write to a path in `base.attachments`; `check_writes(base, writes)` replaces `check_paths`.

Concerns: the FIFO test and the folder-permission test need a non-root user (the latter is skipped as root). `ls-remote` after a failed push is one more remote call, as the ruling accepts.

## Fix round 2

Findings N1, N2, N3 of `task-9-recheck-1.md`. Tests first: before the fix the link-at-the-old-name test, the file-at-the-old-name test, both mode tests, and the lost-report store test failed with the assertions the recheck predicted. After: `sh scripts/check.sh` green, 805 passed (87 in `tests/gitstore`), `tests/gitstore` run three times without a failure.

- N1: each temporary comes from `tempfile.mkstemp(dir=<target folder>, prefix=".<name>.", suffix=".lodge-tmp")` and is written through its descriptor, so an existing name, link or file, is never reused or followed. Tests: a link at the old fixed name (outside file unchanged, link still a link, record not a link) and her regular file at that name (kept).
- N2: `push` returns True when `ls-remote` shows the branch at the pushed commit; only a tip that is neither the parent nor the commit is `False`. Tests use `tests/gitstore/fakessh.py`, a typed copy of the recheck's stand-in for ssh that drops the first receive-pack's report: store level `PUBLISHED` with the tracking ref at the remote tip and one new commit, and one `add` of a decision leaves exactly one decision on the remote.
- N3: the temporary gets the old file's mode with `fchmod` (tests for 0600 and 0755); a new file gets `0666 & ~umask`, read with `os.umask` set and restored at once.

Concerns: the umask read is process-global for a moment, harmless in the single-threaded command line; the viewer never writes. The `_put_back` folder order seen in the recheck is left, as it only leaves an empty folder.
