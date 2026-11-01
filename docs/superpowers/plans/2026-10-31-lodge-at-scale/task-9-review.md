# Review of Task 9 (785ed0f) and the Task 8a fix round (94be161)

Reviewed on `read-speed-build` in a detached worktree at 785ed0f (`/var/tmp/lodge-review-t9/wt`), against `docs/superpowers/plans/2026-10-31-lodge-at-scale.md` Task 9, d-9n3mad, d-q0tb8r, d-e3stjn, d-232gxs, and `task-8a-review.md`.
Status: done. Blocking 1, Important 4, Minor 12.

All probes ran on copies under `/var/tmp/lodge-review-t9/` (s900, s9000, a clone of the repository at 785ed0f, a copy of the s90000 index file), never in `/var/tmp/lodge-build`.
One slip: my first `uv run lodge show ...` calls ran in the worktree, whose git common dir is the main checkout's shared `.git`; they only read the existing `index-72670d6e81c923ab.sqlite` there (its mtime is unchanged, 02:47) and touched its `.lock` file's mtime (03:55).

## Blocking

**B1 · A file whose path is not valid UTF-8 makes every read, `check`, the gate, and `add` crash with a traceback when the index is on.**
Handle: `src/lodge/gitstore/index_db.py:127-132` (`IndexDB.parses` catches only `sqlite3.Error`) and `src/lodge/gitstore/index_parses.py:24` (`db.execute(..., key)` outside the `try`).
Paths come from `decode(raw_path)` and `os.walk`, both `surrogateescape`, so such a path holds lone surrogates; sqlite3 refuses to bind them with `UnicodeEncodeError`, a `ValueError` and not an `sqlite3.Error`.
Reproduced on a copy of s900 with `lodge/decisions/stray-\xff\xfe.md` (bytes) created:
- `LODGE_INDEX=off lodge show s-0j96qz` exits 0 and `lodge check` prints the stray-file problem (exit 1).
- `lodge show s-0j96qz` (index on) exits 1 with `UnicodeEncodeError: 'utf-8' codec can't encode characters in position 22-23: surrogates not allowed` from `find_parses`; `lodge check` likewise, so the stray file the user needs to be told about hides behind a traceback.
- Files with invalid UTF-8 *content* are fine (marshal handles surrogates), so the tests' non-UTF-8 coverage, if any, does not reach this.
`keep_parses` has the same hole in the other direction (`ValueError` is caught, so one such path silently drops the whole batch and the cache never fills for that store).
This breaks s-gy0nsm ("a read with the index ... corrupt prints the same") and d-kj554d ("a read never fails").
Fix: make a lookup and a write per key, and treat a key that cannot be encoded (`UnicodeEncodeError`) as unkeyable (no lookup, no write, parse directly); at the port boundary catch `Exception` (not only `sqlite3.Error`) in `parses`, `keep_parses`, and `epoch`, since the invariant is that the index cannot fail a read; add a test in `test_index_parses.py` with a surrogate path and an e2e test with a non-UTF-8 stray file name, index on and off.

## Important

**I1 · Decoding a parse unit costs about 20 microseconds, so the parse cache alone costs about 3.2 s at 160,800 files against the plan's 0.45 s.**
Handle: `src/lodge/core/codec.py:97-118` (`_fits`, called per field with `get_origin` and `get_args`) and `:67-94` (`from_plain`); plan cost table, "after one changed record" row ("parse cache 0.45, assembly 0.2") and d-232gxs's 3 s target.
Measured on a copy of the s90000 index (160,800 units, `gc.disable()` as in the CLI, best of two): `find_parses` over every key 3.23 s = 0.54 s lookups + 0.50 s `marshal.loads` + 2.6 s `from_plain`; a profile of `from_plain` puts `_fits`, `get_origin`, `get_args`, and `isinstance` at about 60 per cent.
Failure scenario: a read after one changed record must decode every unit of the current state (Task 10's stored rows cannot replace that), so 3.2 s of the 3 s budget goes to the cache alone, and Task 11 stops on a missed target the plan expected to meet; the same cost is paid twice when `read_checked` also builds the published snapshot from nearly the same keys (`app/state.py:98-103`, `snapshot_of` called for both trees, each decoding the shared units again).
Fix: build, once per class, a validator closure from the type hints (a tuple of per-field checks with `type(v) is str` and the like, no `get_origin` per value), or validate only tag and arity (rows are content-addressed and written by this build; the digest already isolates builds) and drop the per-field type check; share decoded units between the two `snapshot_of` calls of one read (a dict in the call, or in the adapter for the life of the connection).
Re-measure with the same script before Task 10a relies on the figure.

**I2 · Nothing enforces "`sqlite3`, `marshal`, and no pickle only in `gitstore`" outside `core` and `app`.**
Handle: `tests/structure_imports.py:67-84` (`_outside_edge`: `PURE` packages may import only `CORE_MODULES`; every other package is checked only for spawning, writing, and reading modules) against the plan's Global Constraints ("`marshal` and `sqlite3` only in `gitstore`").
Reproduced: adding `import sqlite3`, `import marshal`, `import pickle`, and `import fcntl` to `cli/commands.py`, `viewer/forms.py`, or `hook/post_tool_use.py` leaves `tests/test_structure.py` at 39 passed.
Failure scenario: a viewer or CLI change opens the index file or unmarshals cached bytes directly, past the adapter's failure handling, and no gate stops it; `pickle` is banned only inside `core` by `test_no_pickle_or_marshal_in_core`.
Fix: in `_outside_edge`, for `pkg != "gitstore"` reject `{"sqlite3", "marshal", "pickle", "shelve", "dbm"}` and reject `pickle` and `shelve` in `gitstore` as well; add a case to `tests/test_structure_io.py`.

**I3 · The trees `add`, `ask`, `reply`, and `close` build carry no keys, so they re-parse every file on each call.**
Handle: `src/lodge/app/writes.py:91-94` (`after_tree = Tree(current.rev, {...}, ...)` with no `blobs`), `src/lodge/app/threads.py:92-96`, and `src/lodge/app/state.py:56` (`keys` come from `tree.blobs`); coordinator ruling in `task-9-report.md` ("every snapshot ... build snapshots with cached parses") and the plan ("app builds every snapshot as assemble of cached parses").
Measured on a copy of s9000: `lodge add --dry-run draft.md` 2.41 s with the index against 3.08 s with `LODGE_INDEX=off`; the difference is only the published and current trees, the after tree parses all 9,000 files again (about 7 s at 160,000).
`test_every_app_snapshot_uses_cache[add]` passes because the published tree's lookup raises `index.lookups`, so it cannot see this.
Fix: give a derived tree the keys of the files it did not change, `blobs = {p: b for p, b in current.blobs.items() if p not in files}` (changed paths have no key and parse directly, as `snapshot_of` already does), in `writes.py` and `threads.py`; strengthen the test to assert `parse_file` is called only for the changed paths.
The remaining uncached `load` in `core/apply.py:243` (only when an entry was retired) cannot use the port; note it in the ledger.

**I4 · The cap and the clear have no production caller, so Task 9 as shipped bounds nothing.**
Handle: `src/lodge/gitstore/index_space.py:92-110` (`used_bytes`, `clear`, `prepare_keep`) and `index_db.py:122-131` (`keep_parses` never checks the cap); the plan's "Growth is bounded by `INDEX_FILE_CAP` (Task 9)".
`meta.kept` is set nowhere in `src`, `prepare_keep` is called only from tests, and vulture is satisfied by those tests.
Failure scenario: every edited blob adds a unit that nothing ever deletes (invariant 1), `add` and the gate write units through `keep_parses` alone, and the first thing that clears is Task 10a's `keep_state`; if that wires `prepare_keep` only inside a state keep, the parse-only writers still never clear.
Also: the constant is `MIN_FILE_CAP` plus an inline `max(...)`, not the plan's named `INDEX_FILE_CAP`, which Task 12's report and the cost table cite.
Fix: either record in the ledger that Task 10a must call `prepare_keep` from `keep_parses` too (and make `kept` mean "a state kept", as written), or call it now with the tree's file count; name the constant as the plan does; add a test that a parse-only writer over the cap clears once.

## Minor

**M1 · `prune` aborts entirely on one orphan `.sqlite` without a lock file.**
Handle: `index_space.py:56-62` (the `sorted(..., key=lambda p: ...stat())` raises `FileNotFoundError` for the orphan, caught by the outer `except OSError`).
Reproduced: five builds plus `index-ffffffffffffffff.sqlite` with no `.lock`: no old build is deleted and the orphan stays forever.
The plan says "any failure skips it" (that build).
Fix: compute the age per path with `try`, treat a missing lock as oldest, and delete the orphan only when `exclusive` on a freshly created lock succeeds; lock files themselves accumulate (one empty file per lodge build ever run, never deleted, as the plan says); say so in the README's reclaim note.

**M2 · Corruption found after opening is never repaired.**
Handle: `index_db.py:108-132`; `_connect` reads only `meta`, so a file with a bad page in `parses` opens, every `parses` call raises `SQLITE_CORRUPT`, returns `{}` (dropping the keys found before the error), and every `keep_parses` fails.
Reproduced on s900 (random bytes written into 5 pages from offset 200,000): output identical, but `PRAGMA integrity_check` still reports `malformed` after reads; every read stays fully cold, and at s90000 that is about 17 s per read until someone deletes the folder.
The plan says "after opening, such an error is a miss", so this is as specified; the cost is permanent.
Fix: on `SQLITE_CORRUPT` or `SQLITE_NOTADB` after opening, remember it in the object and let the next `open_index` rebuild (a marker file beside the lock, removed with the rebuild), or run `PRAGMA quick_check` on a cheap schedule; at minimum keep the partial hits.

**M3 · The digest names `yaml.__with_libyaml__` but not libyaml's version.**
Handle: `index_db.py:25-31`; the brief and the plan both name libyaml.
A PyYAML built against the system libyaml (dynamic link) changes parse behaviour when the system library is upgraded, with the same `yaml.__version__`; `yaml._yaml.get_version_string()` exists (here `0.2.5`).
Fix: add it to the digest when `yaml.__with_libyaml__`; add a case to `test_digest_names_python_yaml_libyaml_sqlite`.

**M4 · `project_index` runs a second identical `git rev-parse --git-common-dir`.**
Handle: `index_db.py:46-48` against `gitstore/setup.py:78-79` (`_common_dir`), both called in `_make_lodge` (`main.py:51-56`).
One more subprocess per command (about 3 ms), against the plan's git budget.
Fix: `open_store` and `project_index` share one `common_dir` value (a front-door function `common_dir(root)` called once in `main`).

**M5 · `settings_key` encodes `CoreSettings` through `to_plain`, and `project_index` is outside every `try`.**
Handle: `index_db.py:39-40`, `main.py:55`.
A future non-plain field (a float, a `Path`) in `CoreSettings` makes `to_plain` raise `ValueError` in `_make_lodge`, crashing every command with the index on.
The value (`settings_digest`) is stored and read only by one test until Task 10a.
Fix: `repr(settings)` in `settings_key`, or compute it inside `open_index`'s `try`.

**M6 · `read_state` calls `index.epoch()` and discards the result.**
Handle: `app/state.py:73-75`, pinned by `test_second_read_parses_nothing` (`index.epochs == 2`).
The plan's "a build reads `Index.epoch()` once before its first lookup" needs the value kept for the build; as written it costs a read transaction per `read_state` (several per `add`) and Task 10a will have to thread the value through anyway.
Fix: leave the call out until 10a, or return it and keep it in `State`; the test should then assert once per build, not once per `read_state`.

**M7 · `test_locked_at_open_does_not_delete` never locks anything.**
Handle: `tests/gitstore/test_index_failures.py:57-70`; `BEGIN EXCLUSIVE` in WAL mode blocks neither readers nor opening, so the test passes for any implementation (confirmed: with an exclusive hold, 16 commands on s900 ran in 5.7 s with identical output and the file untouched).
Fix: hold a real writer (`BEGIN IMMEDIATE`) and assert `open_index` returns within 1 s, the file is unchanged, and a `keep_parses` is skipped, or drop the test's claim.

**M8 · `clear`'s virtual-table branch is speculative and untested; its comment cites a later task.**
Handle: `index_space.py:78-90` ("FTS appears in Task 10b"), and no test creates a virtual table; a comment naming a task goes stale and is the edit-explaining kind the repository rules forbid.
Fix: delete the branch and the comment until Task 10b adds the FTS table and its test (a one-line `DELETE` loop over tables is enough now), or add a test with an FTS5 table that checks it is empty and re-creatable after a clear.

**M9 · `find_parses` issues one `SELECT` per key.**
Handle: `index_parses.py:23-25`; 0.54 s of the 3.2 s in I1 at 160,800 keys.
Fix: batch with `WHERE (path, blob) IN (VALUES ...)` in chunks of 400, or walk keys in index order; do this after I1.

**M10 · The plan's `INDEX_FILE_CAP` is computed inside `prepare_keep(db, files)` from a `files` argument no caller supplies yet.**
Covered by I4; listed so the signature is settled in the Task 10a brief: the caller has `len(tree.files)`.

**M11 · Task 8a fix round, sibling path not aligned: `identity.committed` still keys a gitlink by the commit ID.**
Handle: `src/lodge/gitstore/identity.py:100` (`blobs[path] = fields[2].decode()` for any non-attachment entry) against the fixed `trees.py:41-45` (`blob_id(b"")` for a non-blob).
Reproduced in a scratch repository with a gitlink `lodge/decisions/submod`: `committed(root, "HEAD").blobs[path]` is `0ef1566e...` (the commit), `read_tree(root, "HEAD").blobs[path]` is `e69de29b...`.
Failure scenario: the 8a review's M3 invariant (`blobs[p] == blob_id(encode(files[p]))`) holds for `read_tree` only; Task 10's listing-keyed lookups for the five indexed reads key the empty text under a commit ID, and `texts` asks git for that object as a blob.
Fix: in `committed`, key a non-`blob` entry with `blob_id(b"")`, with a test beside `test_gitlink_keys_the_empty_text_read`.

**M12 · Dead and duplicated detail in the new adapter.**
`IndexDB.settings_digest` is set and only a test reads it (`index_db.py:103-106`, `test_creates_folder_and_file_named_by_digest`); `# type: ignore[arg-type]` at `index_parses.py:38` hides `to_plain`'s `object` return where a `cast` would say what it is; `IndexDB.__del__` closes the connection, which in the viewer (a `Lodge` per request) is the only thing that releases the shared lock, so an exception that keeps a frame alive keeps the lock; an explicit `close` in `main`'s factory callers, or a context manager, would not rely on refcounting.

## What was checked and held

Correctness, output parity (compared stdout, stderr, and exit status of 16 commands on a copy of s900, 11 on a clone of the repository, `LODGE_INDEX=off` as the reference):
- first read (index missing), second read, third read: identical in both stores.
- read-only index file and folder (`chmod 0444`/`0555`), and read-only folder with no index file: identical, nothing created.
- an open writer on the file (`BEGIN EXCLUSIVE`, which in WAL mode blocks only writers): identical, writes skipped.
- garbage 5,000 bytes, truncated to 300,000 bytes, random pages overwritten mid-file, empty file: identical; the first, second, and fourth are rebuilt (the file is full size again, `integrity_check` ok); the third is not repaired (M2).
- a thread (`lodge ask`) parsed, cached, and read back: `threads`, `waiting`, `check`, `check --gate`, `show` identical with and without the index.
- invalid UTF-8 *content* in a decision and a new decision: identical (B1 is the path, not the content).
- 12 processes reading one empty index at once, then 3 rounds of an edit and 8 concurrent `check --gate` (one with the index off): every output of a round identical, `integrity_check` ok, 1,610 units.
- the gate against a stale parse: with `git update-index --assume-unchanged` on an edited decision whose committed parse was in the index, `check --gate` reports the edit (`kind must be 'decision' or 'spec'`) identically with the index off, on, and warm.
  A parse planted under the key of the bytes actually read (path, blob of the on-disk text) is taken by the gate by design (d-q0tb8r keys by content; the index is trusted for a key-correct unit as `.git/hooks` is); a parse planted under any other key is never read, and the unit tests plant both.

Parse units: `INSERT OR IGNORE` only, `UNIQUE(path, blob)`, no `UPDATE`, and the only `DELETE` is `clear`; `to_plain`/`from_plain` cover every dataclass and enum reachable from `Decision`, `SpecEntry`, `Area`, `Thread`, and `Problem` (introspected: nothing missing); all 1,607 s900 files were stored; a 20,000-case mutation fuzz of stored plain values (wrong tags, arity, types, floats, bytes, huge ints, lone surrogates) produced no exception outside the decoder's `except` list.
No pickle anywhere in `src`; `marshal` only in `gitstore/index_parses.py`; decoded values are rebuilt only through registered classes with a field-type check (I1 is its cost).

Lock protocol, cap, and clear: a writer process clearing and re-keeping 500 rows 150 times (two writers) against three readers for 8 s: 6,606 snapshot reads, every one saw 0 or 500 rows, never a part; `integrity_check` ok, epoch 300, the file size unchanged by clears; `-wal` bounded.
A refused exclusive upgrade closes the lock file and returns `None`; recovery downgrades to shared; pruning counts the current build, keeps four, deletes by age 7 days only under `LOCK_EX | LOCK_NB`, removes `-wal` and `-shm`, and never the lock file; no `fcntl` means no deletion (all by tests, which I read and ran; M1 is the one failure I found).

Digest: 1.8 ms to compute; changes with source bytes and names (test), `sys.version`, `yaml.__version__`, `yaml.__with_libyaml__`, `sqlite3.sqlite_version`, and the schema number (M3 for the libyaml version).
Only `.py` and `.md` files are hashed; the one other file in the package (`viewer/style.css`) cannot change a parse.

Structure: `tests/test_structure.py` 39 passed; `sqlite3` and `marshal` appear only in `gitstore`, `core/codec.py` imports only allowed modules; the confinement is not enforced for `cli`, `viewer`, `hook`, `main` (I2).

Task 8a fix round (94be161) against `task-8a-review.md`: M1 (case IDs) fixed and checked against the samples (`at(0)` same instant, `09:00:00+00:00` same instant in another offset, `LATER` later, `09:30:00+00:00` 30 minutes later); M2 (status line rewritten in place) fixed; M3 fixed in `read_tree` with a gitlink and FIFO test (but see M11 for `identity.committed`); M4 handled by the `blob_id` docstring only, the review's other ask (record it for Task 8b) was not done and Task 8b has since landed, so the SHA-256 key split (committed 64 hex, disk 40 hex, a miss and never a wrong hit) stays undocumented in the plan; M5 (`Tree` docstring) and M6 (`blob_paths`) fixed.
Focused run of the structure and Task 9 test files in my worktree (`uv run --frozen pytest`): 107 passed, 1 skipped (the `secure_delete` half of `test_secure_delete_off_and_wal_bounded`, skipped because this Python's SQLite defaults it to 0, so the clear's WAL bound at a default of 1 is untested here).

Report against the code: the timing tables, the `s90000` clear (0.049 s best of three, 160,800 rows to 0), and the 288 output pairs were not re-run by me; I checked the clear's premises (one transaction, file size and inode kept) with my stress run and the index copy, and the s90000 index file copy holds the 160,800 units the report names.
Cold Task 9 reads are slower than Task 8b by about 2.5 s at s90000 (16.9 s against 14.2 s for `show {code}`), the cost of writing the cache, as the report says.

## Files read

`CLAUDE.md`; `.claude/agents/reviewer.md`; plan header, Global Constraints, Calls made, cost table, Task 9 section, and the Task 10a interface lines; `task-9-report.md`; `task-8a-review.md`; d-9n3mad, d-q0tb8r, d-e3stjn, d-232gxs, s-gy0nsm through `lodge show`; full diffs of 785ed0f and 94be161; `src/lodge/gitstore/index_db.py`, `index_parses.py`, `index_space.py`, `identity.py` (the `committed` function), `trees.py`, `checkout.py` (`disk_tree`, `trees`), `setup.py`, `git.py`, `published.py`; `src/lodge/core/codec.py`, `snapshot.py`; `src/lodge/app/state.py`, `writes.py`, `threads.py`, `reads.py`, `ports.py`; `src/lodge/main.py`; `src/lodge/cli/commands.py` (the `run` function); tests `tests/app/test_parse_cache.py`, `tests/app/fakes.py` (diff), `tests/gitstore/test_index_failures.py`, `test_index_db.py`, `test_index_parses.py`, `index_helpers.py`, `tests/e2e/test_index_off_same_output.py`, `tests/structure_imports.py`, `structure_tables.py`, `structure_calls.py` (head); `scripts/bench_reads.txt`.

## Files not read

`tests/core/test_codec.py` (ran only); `scripts/bench_reads.py` beyond its header; `viewer/server.py` beyond the factory call sites; `gitstore/branch.py` and `listing.py` (branch mode was not exercised: all probes used checkout mode); the viewer was not run, so a `Lodge` per request, its shared lock lifetime, and `__del__` across threads are reasoned, not observed; `s90000` was not read or timed beyond a copy of its index file.
