# Plan fix 6: making the warm-read and changed-read targets reachable

Status: complete.
Build measured: 83ef70b, installed from a detached worktree into `/var/tmp/lodge-plan-fix6/venv`; store `/var/tmp/lodge-bench/s90000` (160,800 listed files), used read-only (the raw-index trials wrote their index file to the scratch folder through `GIT_INDEX_FILE`).
Inputs: the plan's Global Constraints and Tasks 8b to 12, `task-8b-report.md`, `brief.md`, `/var/tmp/lodge-build-briefs/review-t8b.md` (P1, P2), and d-hxmdkz, d-dqpf59, d-q0tb8r, d-232gxs, d-e3stjn, d-8kq2nk, d-n6tqzq, d-26e6zj, d-7e8zhd through `lodge show --reasoning`.
The new and replacement task texts are in `tasks.md`.

## Verdict

- 0.3 s `seen` at 160,000 files is reachable under any `core.autocrlf`, but only with a per-file stat cache that git checks in C (Task 11b, RAW-1): estimated about 0.20 s with LAZY-1 and 0.23 s without, every part measured except printing.
- With the stat cache in lodge's own SQLite file, as the review sketched it, 0.3 s is not reachable under `core.autocrlf=input`: `lstat` of 160,800 files in Python costs at least 0.280 s (mtime only, best case; 0.359 to 0.389 s for full stat results), the whole hit 0.406 s, on top of a start-up floor of 0.13 to 0.17 s; threads made it slower (0.414 s with 8).
  Under the isolated configuration Tasks 8c and 11 alone reach about 0.24 s (0.27 s without LAZY-1), a 0.03 to 0.06 s margin.
- 3 s `changed`: the identity's share falls from 3.148 s (autocrlf) and 0.785 s (isolated) to about 0.05 s under Task 11b; the rest of the changed read is the plan's estimate of about 3 s, unmeasured until Tasks 10a to 10c, with one correction found here (the current listing's mapping is 0.14 s, not 0.06 s); so it is not blocked by the identity any more, and whether it lands under 3 s is Task 12's measurement.
- The start-up floor today is 0.166 s of the 0.3 s (a command that reads no store); LAZY-1 lowers it by about 0.034 s; it is a row of its own in Task 12.

## What changed in the plan, and why

| Item | Change | Measurement it rests on | Decision |
|---|---|---|---|
| P1 item 1, lazy listings and the committed tree by commit | Task 8c: `identities()` takes both idents by `rev-parse`; `listings()` builds mappings on first use; `Committed` memoises `ls-tree` per commit, so published equal to `HEAD` costs nothing | `ls-tree` 58.3 ms plus parsing 80.0 to 82.1 ms per commit; the review's 0.143 s for the redundant published one | none (no port change) |
| Found here: a `git add` between `diff-index` and `diff-files` hides an edit | Task 8c: the five git calls start together under one before-and-after key of git's index file; on a moved key run again twice, then the exact tree | probe `measure/race.py` at 83ef70b: the fast listing kept `HEAD`'s blob and the clean ident while the disk held the edit (`identity.py:36-50`) | none (a correctness fix within d-8kq2nk and d-n6tqzq) |
| P1 item 3, conversions keyed on their sources | Task 8c: the key without the path set; `check-attr` and the path set only on a miss; nested `.gitattributes` from the walk's names and the flag scan | `rsplit` of every path 15.7 ms, run twice per key; the review's 0.142 s stage | none |
| P1 item 4, byte-scanned `ls-files -t -v` | Task 8c: `scan` compares two `bytes.count` results and finds `.gitattributes\0`, falling back to the loop when any entry is flagged | loop 49.2 ms; fast path 15.3 ms; a regex 105.1 to 273.5 ms and per-tag `find` 89.5 ms, both rejected | none |
| P1 item 5, merged configuration calls | Task 8c: one `config --list -z` (a bare key is true, the review's A2) and one `var -l`, started with the diff calls | each call 1.3 to 2.3 ms alone; the group of seven 60.1 ms together against 84.5 ms in turn | none |
| Lazy imports | Task 8c Part B, only with LAZY-1: the viewer, `secrets`, `importlib.metadata`, `importlib.resources`, `tempfile`; `yaml` stays, since Task 9's digest imports it on every indexed read | stubbed imports: 149.2 ms to 125.5 ms (viewer), 112.6 ms (and yaml), 101.9 ms (and the other four); `yaml` alone 12.9 ms of it | LAZY-1 (author: the structure test forbids imports inside functions, `tests/structure_imports.py:38`) |
| P1 item 2, folder rows without the base's names | Task 11 rewritten: rows hold the folder's difference from base (added, with kinds, and removed), so a hit takes no base names and runs no `ls-tree`; the removed names cover attachments, which Task 11b keeps out of the raw index | `ls-tree` plus parsing 0.14 s avoided per seen read; folder-row hit 6.4 ms | FOLD-1 (narrows d-8kq2nk) |
| P2, the per-file stat cache | Task 11b, new: a private git index per worktree, conversions off, written under a stricter racy rule than git's, with the proof in the task text; the gate and `add` never use it | raw-index `diff-files` 39 to 54 ms and `diff-index --raw` 12.5 ms under `core.autocrlf=input`, 44.2 ms with the small calls started together; against 0.406 s for the SQLite stat cache hit and 3.148 s today | RAW-1 (coordinator) |
| Task 12's expectations | The start-up floor and the autocrlf case as rows of their own; `--git-config` and `--startup` in the replay; the stop applies under either configuration and after Task 11b | floor 18.0, 142.3, and 172.6 ms; autocrlf identity 3.148 s | STOP-2 (narrows d-26e6zj) |
| Expected cost table | The seen, changed, and first-read rows rewritten with the measured parts | as above, and the raw index's build 1.15 s | none |

## The stat cache: why a private git index rather than rows in lodge's SQLite file

Both store the review's tuple (git's index entry holds ctime, mtime, device, inode, mode, uid, gid, and size, with the blob ID) and both take only changed files' bytes.
They differ in who runs the 160,800 `lstat` calls: Python costs 0.280 to 0.389 s for them, and no form tried was faster (by full path, relative to an open folder, inside a `scandir` walk at 0.522 s, or in threads); `git diff-files` runs them in C, with its preload threads, in 39 to 54 ms.
The racy rule is lodge's own on top of git's: an entry is written only when lodge's two `lstat` results around the `update-index` call agree and the file's mtime and ctime are at least 2 s old, so git never treats an entry as racily clean and never reaches its content check, the one place a conversion could enter; the proof is in Task 11b's text, and rests on the same three assumptions about the file system and git's stat comparison that d-8kq2nk already accepts for git's own index.
What it costs: a second file in the git folder (about 22 MB at 160,800 files), 1.15 s once per worktree in a cold read, a dependency on `git --attr-source` (git 2.40 or later, else Task 8c's path runs), and no use while `info/attributes` exists, since `--attr-source` does not cover that file (the probe recorded the filtered blob).
What it removes from the seen path: `ls-files`, both configuration calls, `check-attr`, and the attributes sources, since git's own index, its flags, and conversions no longer matter there; Task 8b's flag and conversion code stays as the path for the cases above, and as the tests' second opinion.

## Decisions needed (proposed statements; none recorded, no `lodge add` run)

- RAW-1 (scope `process`, for the coordinator, narrows d-8kq2nk and d-atsx8n for the five indexed reads): "In checkout mode the fast identity takes the working tree's raw blob IDs from a private git index per worktree, `<git dir>/lodge/raw.index`, which git checks by stat with every conversion turned off; lodge records a file in it only when its `lstat` is equal before and after the write and its mtime and ctime are at least 2 s old; without git's `--attr-source`, with an `info/attributes` file, or without a writable git folder, the identity runs from git's own index as before; the gate and `add` never use it."
  Reasoning handles: `diff-files` on the raw index 39 to 54 ms against 0.406 s for a stat cache in SQLite and 3.148 s today under `core.autocrlf=input`; cost if wrong: a stale read if the file system breaks the assumptions git itself relies on.
- LAZY-1 (scope `structure`, for the author, since it loosens a rule of the structure test): "A module may import inside a function only the pairs listed in `LAZY_IMPORTS` of `tests/structure_tables.py`, each an import the module may already make at its top, listed with the start-up time it saves."
  Reasoning handles: about 0.034 s of a 0.166 s floor (stubbed-import measurement); cost if wrong (declined): seen reads land about 0.03 s higher, 0.23 s instead of 0.20 s with Task 11b, 0.27 s instead of 0.24 s without it.
- STOP-2 (scope `process`, narrows d-26e6zj): "The stop on missed targets applies after Task 11b, and at 160,000 files under both the isolated git configuration and `core.autocrlf=input`."
- FOLD-1 (scope `process`, a planner's call, narrows d-8kq2nk): "A folder row holds the folder's difference from the base tree, its names the base lacks with their kinds and the base's names it lacks, keyed by the base tree's ID, so a read whose folders are unchanged takes none of the base's names."
- No product decision is needed: nothing here changes what a command prints or what the gate decides.

## Risks and what is not measured

- Printing and the indexed read's own Python (Tasks 10a to 10b) are not measured; the 0.20 to 0.23 s estimates leave 0.07 to 0.10 s for them.
- The changed read's other phases (parse cache, assembly, `derive`, checks, rows, writing) remain the plan's probe estimates until Task 10c.
- Several start-up timings were taken while a Codex replay ran at `s9000` on one of 16 cores; each is a best of 7 or 9.
- The raw index rests on git's stat comparison exactly as d-8kq2nk's use of git's index does; Task 11b's Step 4 runs its tests on a FUSE-mounted disk where one is at hand and turns it off on that file system kind if any fails.

## Measurements (scripts and raw outputs in `measure/` beside this file)

Build: `/var/tmp/lodge-plan-fix6/venv` (CPython 3.13.5, PyYAML 6.0.3 with libyaml, SQLite 3.47.1, `compileall` done), installed from the worktree at 83ef70b; git 2.56.0.
Every timing is best of 7 or 9 sequential runs; a Codex replay ran at `s9000` on one core during some of them.

Start-up (`scratch/startup.py`, `scratch/blocked_import.py`):
- `python -c pass` 18.0 ms; `python -c "import lodge.main"` 142.3 ms; `lodge --version` 165.7 ms; `lodge guide --read` 172.6 ms.
- `import lodge.main` with stubs for lodge.viewer, yaml, importlib.metadata, secrets, tempfile, importlib.resources, http, email, zipfile: 101.9 to 103.9 ms against 149.2 ms unstubbed under the same harness, so lazy imports save about 46 ms.
- Also stubbing the write path and the check path (core.apply, drafts, app.writes, app.confirm, plumbing, commit, derive, doubts, check_*, snapshot, fileformat, document, fields, yamlio, yamlfast, feedback): 95.6 ms, a further 8 ms.
- `version('lodge')` from importlib.metadata, called by `build_parser` on every command (`cli/parser.py:113`): 78.6 ms with its import against 59.2 ms for the import alone.
- In-process, after `import lodge.main`: the first `version('lodge')` 2.2 ms; `_parser()` 14.1 to 17.2 ms, of which 12.7 ms is creating the 17 subparsers with no arguments, so a partial parser saves little; `main(['guide','--read'])` 17.0 ms.
- `python -c "import lodge.main"` 145.0 ms and `python -c "import lodge.main; lodge.main.main(['guide','--read'])"` 166.2 ms in the same run: the CLI floor today is about 0.166 s, of which 0.018 s is Python, about 0.124 s imports, and about 0.021 s parsing and dispatch.

Identity at 83ef70b (`scratch/identity_now.py`, a new store object each run, clean):
- isolated (`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_ATTR_NOSYSTEM=1`): best 0.785 s of five (0.785 to 0.832);
- the author's own global configuration (`core.autocrlf=input`): best 3.148 s of three.

Git calls, each alone, isolated configuration (`scratch/gitstages.py`, best of 7):
- `rev-parse --verify HEAD^{commit}` 1.8 ms; `rev-parse HEAD^{commit} HEAD:lodge` in one call 1.6 ms; `rev-parse --git-path index --git-path info/attributes` in one call 1.4 ms; `merge-base` 1.5 ms; `config --list -z` 1.6 ms; `var -l` 2.3 ms; `config --get core.autocrlf` 1.3 ms.
- `ls-tree -r -z HEAD -- lodge` 58.3 ms (19.7 MB); `ls-files -t -v -z -- lodge .gitattributes` 22.3 ms (11.5 MB); `diff-index --cached` 12.2 ms; `diff-files` 43.6 ms.
- `diff-index`, `diff-files`, and `ls-files` started together: 59.7 ms wall; with `rev-parse`, `merge-base`, `config --list`, and `var -l` also started together: 60.1 ms; the same seven one after another: 84.5 ms.

Python stages on that output (best of 7 or 9):
- `ls-files` output: the decode loop of `flags.py` 49.2 ms; a compiled regex over the bytes 105.1 to 273.5 ms (slower, rejected); per-tag `bytes.find` 89.5 ms (rejected); the fast path, `count(b"\0")` against `count(b"\0H ")` plus one `find(b".gitattributes\0")`, 15.3 ms (`scratch/scan.py`).
- `ls-tree` output to a path to blob mapping: the split loop of `identity.py` 80.0 to 82.1 ms; one compiled `findall` 124.6 ms (slower, rejected) (`scratch/lstree_parse.py`).
- `rsplit` of every path for `.gitattributes` once 15.7 ms (done twice per key, `attributes.py:82-86`); `dict(base.blobs)` 2.7 ms.

Per-file stat cache in lodge's own SQLite file (`scratch/statcache.py`, `scratch/statthreads.py`):
- `os.lstat` of the 160,800 files: 389.3 ms by full path; 358.6 ms by name relative to an open folder; 279.5 ms reading `st_mtime_ns` only; 2 threads 243.2 ms, 4 threads 441.8 ms, 8 threads 414.1 ms (the GIL serialises them).
- A `scandir` walk with an `lstat` per file 521.7 ms; the names-only walk of `identity.py` 83.4 ms; `lstat` of the 2,252 folders 4.3 ms.
- Loading the rows: one row per file 260.9 ms; one row per folder (`marshal` of name to stat and blob) 89.5 ms; `lstat` and compare against the folder rows 304.2 ms; load plus compare, the whole hit, 405.8 ms.

Private raw git index (`scratch/private_index.py`, and the shell commands in this report's section on it):
- Built with `GIT_INDEX_FILE` in the scratch folder and conversions off (`-c core.autocrlf=false -c core.attributesFile=/dev/null -c core.ignoreStat=false -c core.fsmonitor=false -c core.checkStat=default -c core.trustctime=true -c core.symlinks=true -c core.splitIndex=false -c core.untrackedCache=false --attr-source=<empty tree>`, `GIT_ATTR_NOSYSTEM=1`): `update-index --add --info-only -z --stdin` of the 160,800 paths 1,152 and 1,162 ms; `read-tree HEAD` then `update-index --refresh` 142 plus 1,109 ms.
- Under the author's own global configuration (`core.autocrlf=input`, overridden for these calls): `diff-files` 39 to 54 ms; `diff-index --cached --raw HEAD` 12.5 ms; both started together 40.5 ms; with `rev-parse`, `merge-base`, and `config --list` also started together 44.2 ms; the five one after another 62.9 ms; a refresh of one path in the 160,800-entry file 10 to 11 ms.
- `diff-index --cached HEAD` against the stdin-built raw index named 0 paths: its raw blobs equal `HEAD`'s for all 160,800 files.
- Probe in a scratch repository (`scratch/probe`): with `core.autocrlf=input` in the author's configuration and a CRLF file on disk, the raw index records `c30dea8…`, which `git hash-object --no-filters` gives for the disk bytes, and `diff-index --raw` reports it against `HEAD`'s LF blob without lodge reading the file; a worktree `.gitattributes` with `* filter=up` is ignored under `--attr-source=<empty tree>`; an `info/attributes` with `* filter=up` is not ignored (the recorded blob was the filtered one), so that file must be absent for the raw index to be used.

Index hit on a scratch SQLite file shaped like Tasks 9 and 10a, 166 MB (`scratch/sqlite_hit.py`): `flock`, connect, five pragmas, one read transaction with a state row of 20,000 codes, one bucket of 157 rows, and one parse row 2.6 ms; the build digest over the installed package's 315,994 bytes of `.py` and `.md` 2.2 ms.
Folder rows of Task 11 (`scratch/folder_hit.py`): load 2,252 rows, `lstat` each folder, compare 6.4 ms.
s90000 holds 27,583 records with a code; `lodge/decisions` holds 90,542 files in one folder.

Commands run in a shell rather than a script (at `s90000`, `S=/var/tmp/lodge-plan-fix6/scratch`, `E` the empty tree's ID, `O` the overrides listed above, `GIT_ATTR_NOSYSTEM=1`):
- `GIT_INDEX_FILE=$S/raw.index git $O read-tree HEAD` 142 ms, then `git $O update-index -q --refresh` 1,109 ms; `diff-files` on it five times 39, 43, 48, 48, 45 ms; the real index's `diff-files` under the author's configuration 52, 53, 57 ms.
- `git ls-files -z -- lodge > $S/paths.z`; `GIT_INDEX_FILE=$S/raw2.index git $O update-index --add --info-only -z --stdin < $S/paths.z` 1,162 and 1,152 ms; one path refreshed 10, 11, 11 ms; `diff-files` 54, 51, 46 ms; `diff-index --cached --name-only HEAD` named 0 paths.
- `measure/race.py` in a fresh repository (`git init -b main`, one record committed, then edited on disk, isolated configuration): printed `fast listing blob: a2e56be6ec2c  disk blob: 415d7d0a9611  base ident kept: True`.
- `/var/tmp/lodge-plan-fix6/venv/bin/python measure/identity_now.py 5` with the isolated environment, and `... 3` without it, for the two identity figures.
