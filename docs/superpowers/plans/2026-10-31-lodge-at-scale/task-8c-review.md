# Review of Task 8c (47a363a)

Status: complete.
Method: committed code read in `/var/tmp/lodge-review-t8c/wt` (detached at 47a363a); every probe ran there, in `/var/tmp/lodge-review-t8c/scratch`, or on copies of `/var/tmp/lodge-bench/s900`; `LODGE_INDEX=off` throughout, the shared index never written.
`s90000` was read in place by `identities()` alone (git plumbing only, `GIT_OPTIONAL_LOCKS=0`).

## Verdict

Blocking 0, Important 2, Minor 6.
The identity agrees with the exact tree in every probe (staged, unstaged, untracked, deleted, renamed, mode-only, flags, attributes, links, FIFOs, sockets, gitlinks, a rewritten branch), the reader never followed a link or blocked, and the bare `autocrlf` key, the lazy listings, and the one-function R11 switch all hold.
The two Important findings are a recursion crash of the new walk on deep folder trees (A1) and an R11-B readiness claim in the report that does not reproduce (B1).

## Correctness (pass 1)

### A1 Important: `disk.walk` recurses once per folder level, so a 1,100-deep tree crashes every exact read with `RecursionError`
`src/lodge/gitstore/disk.py:63` (`visit`) and `:86` (the recursive call); the chain opened by `DiskWalk.parent` (`:30-52`) holds one descriptor per level as well.
The reader it replaced, `os.walk` in `disk_tree`, is iterative and listed such a tree; git accepts it (path length about 2,200 bytes, under `PATH_MAX`).
Probe (`/var/tmp/lodge-review-t8c/scratch/deep.py`, built with descriptor-relative `mkdir`): depth 900 reads fine and agrees; depth 1,100 raises `RecursionError` at `disk.py:86` after 1,000 frames; `os.walk` on the same folder finds the file, and `git add -A lodge` stages it.
Failure scenario: a branch (or an agent) that holds a folder 1,000 or more levels deep under `lodge/` makes the gate, `add`, `check`, and the fast identity die with a traceback, since `main.py:129` catches `LodgeError` only; the old reader gave a tree.
With a soft limit of 1,024 descriptors the next failure would be `EMFILE` at the same depth, which `visit` turns silently into "unlistable" and hides the files below.
Fix: an explicit stack in `walk` instead of recursion, with a depth cap (a few hundred levels) past which a folder is recorded in `unlistable` rather than entered, so descriptors and frames stay bounded; add a test at depth 1,100 that the walk returns and agrees on both sides of the cap.

### Checked and found correct (probes run, each against `disk_tree` or `read_tree`)
- Differential fuzz, `scratch/probes/test_probe_review.py`: 69 seeds of 60 operations each (30 operation kinds: edit, create, delete, untracked, chmod, file link, folder link swap, FIFO, `mv`, `git mv`, attachments and attachment links, gitlinks with absent, empty, and populated folders, `add -N`, `reset --hard`, `stash -u`, `rm --cached`, assume-unchanged, skip-worktree, root, nested, and `info/attributes` files with `text eol`, `ident`, `filter`, `-text`, `working-tree-encoding`, `autocrlf` in every spelling including the bare key, empty folders, non-UTF-8 content, odd names with newlines and tabs, file replaced by folder, stage, unstage, commit).
  After every step a reused store object and a fresh one both agree with `trees()` (blobs, attachments, `texts`), and the ident-to-exact-tree map never collides: 0 failures.
  A first run hung in my own helper opening a FIFO for writing (`wait_for_partner`); the helper was fixed, not lodge.
- `scratch/s900probe.py`: 25 random operations on a copy of `s900` (1,608 files, folder link swaps included): agrees, no ident collision.
- Links and special files: `scratch/race.py` flipped `lodge/decisions` between a real folder and a link to a folder of `OUTSIDE` files, and a record between a file and a FIFO, from a second thread for 20 s: 54,332 `disk.tree` reads, 0 leaks of outside bytes, no hang.
  Sockets, mode-0 files, a folder of mode 0o444 (listable, not searchable), a folder of mode 0o111, a folder link to a file, a dangling folder link under attachments, hard links, `..name` and `.x/` entries, and a non-UTF-8 file name all agree (`scratch/probes/test_probe2_review.py`).
- The `git add` race: the deterministic tests (`test_staged_between_diff_calls_is_seen`, `test_index_changing_every_time_falls_back_to_exact`) pass, and the key is taken before the first start and after the last end (`identity.py:91`, the check after the group, and again after the overlay).
  A real concurrent writer (edit, `git add`, 1,862 calls) showed no hidden edit under R11-B and none under R11-A; the same stress on Task 8b's code also showed none (985 calls), so it cannot prove the window closed; the deterministic tests and the code are the evidence.
- The fallback is exact: `identities()`, `listings()`, and `texts()` all come from one `disk.tree` (`identity.py:152-158`); its ident uses NUL between attachment names.
- Bare `core.autocrlf`: `git config --list -z` prints the key without a newline (verified for the file form and for `-c core.autocrlf`); `attributes.py` treats `None` as true, the empty string as false; the 8b review's A2 is closed.
- Lazy listings: one `ls-tree` for `HEAD` and `published` when equal, a second only in `listings()` when they differ (`test_identities_run_no_ls_tree_for_published`); `Committed` keeps two commits, evicts the older, and rebuilds on demand; branch mode keeps `rewritten` before `accept` as `BranchStore.trees` does and gives a gitlink the key `blob_id(b"")`.
- The R11 rule is in one function: `identity.py:76` `read_paths`.
  Switched in a scratch copy (`scratch/r11b`, `return changed`): the four skipped `test_removed_attributes_follow_the_index` cases pass when unskipped; `test_removed_attributes_agree` (4) and `test_every_file_read_without_a_conversion_source` fail, as they must; see B1 for the rest.
- Parser: `parse(["guide", "--read"])` best of nine, 50 parses each, 13.97 ms before (Task 8b's parser) and 2.34 ms after (minus 11.6 ms); help and error texts compared by the new tests.
- Gate: `ruff format`, `ruff`, `mypy` (257 files), `vulture` green; `pytest` 1,971 passed, 7 failed, 6 skipped when I exported `LODGE_INDEX=off` for the whole run (the seven are `test_index_lifetime.py` and `test_index_off_same_output.py`, which need the variable unset); those two files pass (13 passed) with it unset; `lodge check --gate` prints `ok`.
  The builder's 1,978 passed, 6 skipped is consistent.

### Time: `identities()` on `s90000`, new build, once
2.079 s on a new store object in a fresh process, R11-A as shipped, isolated configuration, 160,800 files (`scratch/time90k.py`; imports excluded).
The report's best of three is 1.989 s, so they agree; the plan's R11-A estimate was about 3.1 s.

## Important

### B1 Important: the R11-B readiness claims in the report do not reproduce, and two tests besides the named ones assume R11-A
The brief: "the other branch is a change of that one function and its tests"; the report says the corrected property test "passes with R11-B selected in a scratch package" and that the four review mutants each fail it.
Scratch copy with `read_paths` returning `changed` (`/var/tmp/lodge-review-t8c/scratch/r11b`):
- `tests/gitstore/test_identity_property.py::test_random_edits_agree` fails on the unmutated R11-B code in 4 of 8 consecutive runs (9.2 to 9.7 s) and passes in the other 4 (12.8 s): `AssertionError` on `lodge/decisions/record-29.md`, the fast blob is the index's LF text and the disk holds CRLF.
  The cause is the A6 fix itself (`test_identity_property.py`, the added `.gitattributes` unlink) with the `crlf` and `stage` operations: a CRLF file staged under `*.md text eol=crlf`, then the source removed, is exactly R11-B's stated exception, and whether git re-hashes it depends on whether the run crossed a second boundary (racy-git).
  So the four mutants "failing" (0.3 to 1.9 s in my runs, `scratch/mut.sh`) is confounded by a baseline that fails half the time; the report's `r11b-property 0 1 passed` was one lucky run.
- `test_regular_file_swapped_for_fifo_before_open` fails under R11-B (exit code 1): it swaps a clean file that only R11-A opens, so under R11-B the swap happens inside the exact reader after the fast listing took the base blob.
Failure scenario: the author answers STALE-1 with R11-B, the builder changes `read_paths`, unskips four tests, and finds a property test that fails at random and an F10 test that fails every time, neither named in the plan as changing.
Fix: say in the report and ledger that the property test and the F10 test need an R11-B version (the property test's `crlf` operation must not leave a staged CRLF file without its source, or compare parsed text, as the ruling says line ends are normalised; the F10 test must edit the file first); better, write both now with a module flag or two parametrised cases so the switch is a one-line change; re-run the four mutants against a baseline that passes 20 of 20.

## Minor

### M1 Minor: code only tests run
`flags.py:39-47` (`Flags.read` and its pair of keys) is called only by `tests/gitstore/test_flags.py` and `test_attributes.py`; the group uses `scan(results[2].stdout)` (`identity.py:122`), so the tests of "cached flags keyed by the index stat" test a path no read executes.
Likewise `attributes.py:36` `configuration()` with `:126` `config or ...` and `:61-67` (`attributes is None`) run only from tests, and `DiskWalk.root` and `DiskWalk.unlistable` (`disk.py:18`, `:21`, written at `:70` and `:80`) are never read; `checkout.py:21` `disk_tree = tree` exists for the tests and `trees()`.
Failure scenario: a later change to the group's flag handling passes every flag test, since they exercise the other copy.
Fix: delete `Flags.read`, the fallback branches, and the unread fields; point the flag tests at `CheckoutIdentity.current`.

### M2 Minor: a failing `ls-files` is read as "no flags"
`identity.py:122` ignores `results[2].returncode`, where Task 8b's `Flags.read` used `run_bytes` and raised.
Under R11-B an assume-unchanged or skip-worktree edit is then missed unless `diff-files` also fails (it usually does on the same corrupt index, which sets all base paths changed, `identity.py:138-140`).
Fix: when `results[2].returncode` is non-zero, treat every base path as changed, as the two diff calls do.

### M3 Minor: R11-A computes the whole candidate machinery and throws the result away
Under `read_paths` returning `base | present | changed`, `changed` is a subset of what is already read; the five git calls of the group, `scan`, `Conversions.paths` (0.049 s under `autocrlf=input`), the set differences, and the three-attempt loop with its exact fallback all run for nothing (the report's R11-A "other" stage is 0.12 s against 0.06 s for R11-B, the group 0.057 s, serial git 0.064 s).
A busy index (an editor running `git status`) drives three groups and then the fallback, whose ident has another form (`sha1` of every path against the tree ID for a clean checkout), so equal trees get unequal idents and Task 10a stores a miss.
Fix: move the group and `changed` into the function STALE-1 switches (`candidates()` returning `None` under R11-A, which then reads everything and never takes the fallback), so the switch stays one function and R11-A pays neither the calls nor the flapping.

### M4 Minor: the root is opened with `O_NOFOLLOW`
`disk.py:61` (`os.open(root, _FOLDER)`) raises on a root path whose last component is a link (verified: `OSError: Not a directory`); the old `os.walk` followed it.
Unreachable today because `repo_root` is git's resolved top level (`setup.py:20`), but `disk.tree` and `walk` take any `Path`.
Fix: open the root without `O_NOFOLLOW`; only `lodge` and below must not follow links.

### M5 Minor: a test needs `/proc`
`tests/gitstore/test_identity_links.py:95` reads `/proc/self/fd/N`, so `test_folder_swapped_for_link_during_the_walk` fails off Linux.
Fix: skip it without `/proc`, or recognise the folder by the order of calls (the first `scandir` of a descriptor).

### M6 Minor: `_COMMANDS` is a hand copy no test ties to the parser
`parser.py:13-31` and the test's `COMMANDS` (`tests/test_parser_named.py:14-32`) list the names twice by hand; a new command missing from `_COMMANDS` silently takes the 14 ms full parser, and one removed from the parser but left in the set gives an empty "choose from" error.
Fix: a test comparing both lists with the choices of the full parser's subparsers action.

## Practice and design (passes 2 and 3)

- Comments state facts (`disk.py:129`, `identity.py:77`); British English, no em-dashes, one sentence per line in the report, ledger, and tests (checked by search over the diff).
- Sizes: `identity.py` 188, `disk.py` 161, `attributes.py` 162 lines; the structure test and the gate pass; `checkout.py` lost 37 lines net (the plan says none added; three were).
- One reader for disk: `disk.tree` serves the gate, `add`, the fallback, and the overlay; the 8b review's B1 for the disk side is closed, the `ls-tree` side still has two parsers (`trees.py:75`, `identity.py:Committed.listing`) that now agree on kinds and the gitlink key.
- Plan rules no test enforces: "descriptors bounded by depth" (A1); "the stat of git's index file after the last call ends" (tested only by the patched runner, adequate).
- Existing tests edited: exactly the two the report lists (`test_attributes.py`, `test_identity_property.py`); verified by `git show --stat`.
- The report's R11-B identity timings (0.442 s clean, 0.448 s edited) sit 0.10 s above the plan's 0.34 s estimate and just under the 0.45 s reporting threshold after a first diagnostic of 0.485 s; the ledger names both, which is honest, and Task 12 should read them as the R11-B figure.

## Files read
Report, plan (Global Constraints, Review Focus, Tasks 8b, 8c), progress-ledger diff, brief, `task-8b-review.md`, `plan-fix-6/review-codex-67.md` (R3, R11, R13, F10 sections), reviewer rules, `CLAUDE.md`; `src/lodge/gitstore/{disk,identity,flags,attributes,listing,git,checkout,published,trees,accepted}.py`, `branch.py` (`trees`), `cli/parser.py` (whole), `main.py` (root and error handling); tests `test_identity_lazy.py`, `test_identity_links.py`, `test_parser_named.py`, `test_identity_property.py`, `test_identity.py` (head), `conftest.py`, `repos.py`.

## Files not read
`test_identity_gitlinks.py`, `test_git_many.py`, `test_flag_scan.py`, `test_flags.py`, `test_attributes.py` line by line (run green; mutants only in the builder's report); `tests/gitstore/test_listing_modes.py`; the builder's `task-8c-*` scripts and logs under `/var/tmp/lodge-bench`; the viewer.

## Probes and logs
`/var/tmp/lodge-review-t8c/scratch/`: `probes/test_probe_review.py` (fuzz), `probes/test_probe2_review.py` (links, sockets, permissions, depth), `probes/test_probe_race_review.py`, `deep.py`, `race.py`, `s900probe.py`, `time90k.py`, `mut.sh`, `r11b/` (scratch package with `read_paths` switched), `fuzz*.log`, `check.log`, `prop-r11b-FAIL.log`.
