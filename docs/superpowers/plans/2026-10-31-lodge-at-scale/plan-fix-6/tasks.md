# Plan fix 6: task texts to paste into the plan

Order after this fix: Task 9 (being built), Task 8c, Task 10a, Task 10b, Task 10c, Task 11, Task 11b, Task 12.
Each block below replaces the plan's text of that name, or is inserted where its heading says.
Measurements behind every number: `plan-fix-6.md` in this folder.

## Insert into "Calls made", after item 21

22. RAW-1 (proposed, for the coordinator): the fast identity of the five indexed reads takes the working tree's raw blob IDs from a private git index that lodge keeps per worktree, checked by git's stat comparison with every conversion turned off; lodge writes an entry only for a file whose `lstat` is equal before and after the write and at least 2 s old; without that file the identity runs as Task 8c leaves it; the gate and `add` never use it (Task 11b).
23. LAZY-1 (proposed, for the author, since it loosens a structure rule): a module may import inside a function only the pairs listed in `LAZY_IMPORTS` of `tests/structure_tables.py`, each an import the module may already make at its top, with the start-up time it saves (Task 8c, Part B).
24. STOP-2 (proposed, narrows d-26e6zj): the stop on missed targets applies after Task 11b.
25. FOLD-1 (proposed, narrows d-8kq2nk): a folder row holds the folder's difference from the base tree, the names on disk the base lacks and the base's names absent from disk, keyed by the base tree's ID, so a hit never takes the base's names (Task 11).

## Replace the "Expected cost" table's rows "a point read" and "after one changed record"

| Read | Today | After Tasks 2 to 4 | After Task 11b |
|---|---|---|---|
| a point read (`show`, `waiting`), seen state | as before | as before | about 0.20 s with LAZY-1, about 0.23 s without, under any `core.autocrlf`: start-up 0.13 or 0.17 (measured floor of a command that reads no store, less 0.034 for LAZY-1), git 0.045 (`diff-files` and `diff-index --cached --raw` against the raw index, `rev-parse`, `merge-base`, started together), folder rows 0.006, the index's lock, digest, and lookups 0.005, printing not yet measured; without Task 11b (Task 8c and Task 11 alone) about 0.24 s, or 0.27 s without LAZY-1, and about 0.6 s under `core.autocrlf=input` |
| after one changed record (checkout, uncommitted) | as before | as before | about 3 s as before, with two corrections: the identity is 0.05 s (any `core.autocrlf`), and the current listing's mapping is 0.14 s (`ls-tree` 0.058 plus parsing 0.080), not 0.06; Task 12 measures it |
| first read in a clone | as before | as before | about 13 s: as before, plus 1.2 s to build the raw index (`update-index --add --info-only` of 160,800 paths, 1.15 s) |

## Insert after Task 9: Task 8c

### Task 8c: The fast identity without needless work

Built after Task 9 and before Task 10a; it changes no output and no port.

**Files:**
- Modify: `src/lodge/gitstore/git.py` (`run_many`), `src/lodge/gitstore/identity.py` (the git calls started together under one key of git's index file; `committed` memoised per store object by commit ID; no base mapping copied on a clean state), `src/lodge/gitstore/listing.py` (`identities()` takes both tree IDs from `rev-parse`; `listings()` builds the mappings on first use), `src/lodge/gitstore/flags.py` (the byte scan), `src/lodge/gitstore/attributes.py` (the key on the sources alone; one `config --list -z` and one `var -l`)
- Part B, only once LAZY-1 is recorded: `src/lodge/main.py` (the viewer and `secrets` imported where used), `src/lodge/cli/parser.py` (`importlib.metadata` imported in the `--version` action), `src/lodge/cli/commands.py` (`importlib.resources` imported where used), `src/lodge/gitstore/plumbing.py` (`tempfile` imported where used), `tests/structure_tables.py` (`LAZY_IMPORTS`), `tests/structure_imports.py` (a listed pair is not "import inside a function")
- Test: `tests/gitstore/test_identity_lazy.py` (new), `tests/gitstore/test_git_many.py` (new), `tests/gitstore/test_flag_scan.py` (new); Part B: `tests/test_startup_imports.py` (new) and one case in `tests/test_structure.py`

**Interfaces:**
- Consumes: Task 8b's `CheckoutIdentity`, `CheckoutListing`, `BranchListing`, `Flags`, `Conversions`, and the tests of `tests/gitstore/test_identity*.py`, `test_flags.py`, `test_attributes.py`, and `test_listing_modes.py` as the oracle, unchanged.
- Produces:
  ```python
  # gitstore/git.py
  def run_many(calls: Sequence[Sequence[str]], cwd: Path) -> list[subprocess.CompletedProcess[bytes]]
      # starts every call before waiting for any; results in the order of `calls`;
      # request_exit waits until all have returned; a missing git raises GitMissing as attempt does
  # gitstore/flags.py
  def scan(raw: bytes) -> Flagged     # equals Task 8b's decode loop on every input
  def config_values(raw: bytes) -> Mapping[str, str | None]   # `config --list -z`; a key without a value is None (git's true)
  # gitstore/identity.py
  class Committed:                    # per store object; at most the two most recent commits
      def tree_id(self, rev: str | None) -> str          # `rev-parse rev:lodge`, EMPTY_TREE when absent or not a tree
      def listing(self, rev: str | None) -> Listing      # `ls-tree` once per commit ID
  ```
- Lazy listings (the review's P1 item 1): `identities()` resolves `HEAD` and the published commit as today and takes both idents without an `ls-tree` of the published commit; `listings()` builds a mapping only when called, from `Committed.listing`, so a published commit equal to `HEAD` costs no second `ls-tree`; until Task 11 the walk still needs the base's names, so the current commit's mapping is still built in `identities()`.
- One snapshot of git's index (found by this plan fix, `identity.py:36-50`, probe `race.py` in `plan-fix-6.md`): `diff-index --cached`, `diff-files`, `ls-files -t -v`, `config --list -z`, and `var -l` start together through `run_many`; the stat of git's index file (inode, size, `mtime_ns`, `ctime_ns`) is taken before they start and after all have ended; when the two differ, the group runs again, at most twice, and then the identity is taken from `disk_tree`'s exact tree, so a `git add` between two calls can never hide an edit; the flags and conversion caches keep their own before-and-after keys (d-n6tqzq).
- Conversions keyed on their sources (the review's P1 item 3): the key is the configuration values, the `git var` values, every source file's stat and bytes, the index-only attributes files, and the index stat, without the path set; the path set is built, and `check-attr` run, only on a miss; nested `.gitattributes` files come from the names the walk already collects (`entry.name == ".gitattributes"`) and from `scan`'s attributes entries, never from an `rsplit` of every path.
- Flags (the review's P1 item 4): `scan` counts the entries and the `H` entries of the raw output and finds `.gitattributes\0`; only when the counts differ does it run Task 8b's loop; it returns what the loop returns.
- Merged configuration calls (the review's P1 item 5): one `config --list -z` gives `core.autocrlf` and `core.attributesFile` in git's spellings, a key with no value counting as true (the Task 8b review's A2); one `var -l` gives `GIT_ATTR_GLOBAL` and `GIT_ATTR_SYSTEM`, a variable it omits being asked with `git var NAME` as today; a failing call converts every path, as today.
- Part B, start-up (LAZY-1): `lodge.viewer`, `secrets`, `importlib.metadata`, `importlib.resources`, and `tempfile` are imported inside the functions that use them; `yaml` stays at the top, since Task 9's build digest imports it on every indexed read; measured saving about 0.034 s of the 0.166 s floor.
- Untouched: the gate, `add`, `trees()`, and branch mode's tip resolution.

- [ ] **Step 0:** skeleton.
- [ ] **Step 1: Write the failing tests:** `test_identity_lazy.py`: `test_identities_run_no_ls_tree_for_published` (a patched runner counts `ls-tree` calls: clean store with published equal to `HEAD`, one; then `listings()`, still one; published behind `HEAD`, `identities()` one and `listings()` two); `test_lazy_listings_equal_eager` (clean, an unstaged edit, an untracked file, a staged deletion, published behind `HEAD`, branch mode: the listings and idents equal Task 8b's, computed by the eager path kept in the test); `test_staged_between_diff_calls_is_seen` (the runner patched to run `git add` of an edited record after the first of the group returns: the listing agrees with `disk_tree`; this test fails on Task 8b's code, as `race.py` showed); `test_index_changing_every_time_falls_back_to_exact` (the runner touches git's index file after every group: the result equals `disk_tree`'s and three groups ran); `test_conversion_key_takes_no_paths` (a second identity on one store object makes no `check-attr` call and never builds the path set, checked by passing a path source that raises); `test_nested_attributes_found_without_a_path_scan` (`lodge/decisions/.gitattributes` with `*.md text eol=crlf`, once on disk only and once in git's index only: agrees).
  `test_git_many.py`: `test_results_in_call_order`; `test_all_started_before_any_awaited` (a patched `Popen` records starts and waits); `test_request_exit_waits_for_every_call`; `test_missing_git_raises_git_missing`.
  `test_flag_scan.py`: `test_scan_equals_the_loop` (500 seeded buffers in `ls-files -t -v -z` form with every tag git prints, lower-case tags, root and nested `.gitattributes`, and paths that are not UTF-8); `test_config_values_spellings` (a key with no value is None, `autocrlf=` is the empty string, `input`, `true`, `yes`, `on`, `1`, `false`, `no`, `off`, `0`, values holding newlines).
  Part B: `test_startup_imports.py`: `test_import_main_loads_no_lazy_module` (a subprocess runs `import lodge.main` and prints `sys.modules`: none of `lodge.viewer`, `http.server`, `secrets`, `importlib.metadata`, `tempfile`); `test_version_still_prints`; `tests/test_structure.py`: a listed pair inside a function passes, an unlisted one fails with "import inside a function".
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement; the Task 8b tests named under Consumes pass unchanged.
- [ ] **Step 4:** gate; at `s90000` with the isolated configuration, `identities()` on a new store object, clean and with one edit, best of three, with each stage's share (Task 8b's script); expected about 0.35 s against 0.785 s (`ls-tree` and parsing of `HEAD` 0.14, the walk 0.08 to 0.10, the git group 0.06, the flag scan 0.015, sets 0.03); the same under `core.autocrlf=input`, recorded and expected unchanged at about 3.1 s (Task 11b removes it); `python -c "import lodge.main"` and `lodge guide --read`, best of nine: about 0.142 s and 0.173 s today, expected about 0.108 s and 0.139 s with Part B; above 0.45 s for the identity, the report gives the stage table and the ledger names it.
- [ ] **Step 5:** commit, push.

## Replace Task 11

### Task 11: Untracked files through folder signatures

**Files:**
- Create: `src/lodge/gitstore/folders.py`
- Modify: `src/lodge/gitstore/identity.py` (the walk replaced when an index is writable or holds rows; the base's names taken only when a folder is listed), `src/lodge/gitstore/index_db.py` (a `folders` table), `src/lodge/main.py` (the store is handed the index at construction)
- Records: FOLD-1, through `lodge add` (scope `process`, `work_item` the plan, narrowing d-8kq2nk)
- Test: `tests/gitstore/test_folders.py` (new)

**Interfaces:**
- Consumes: Task 8b's identity and its names-only walk; Task 8c's `Committed` and `run_many`; Task 9's `open_index`, settings, and failure modes.
- Produces: a table `folders(path, ino, mtime_ns, ctime_ns, listed_at_ns, base, added, removed)`, `added` being `marshal` of the folder's entries the base lacks, each with its kind (a file where the base has a folder, or a folder where it has a file, counts as lacking), and `removed` `marshal` of the base's names in that folder absent from disk; for each folder lodge takes `stat`, then `os.scandir`, then the listing time, in that order (the correctness review's M7); a folder whose `stat` matches its row, whose row's `ctime_ns` is at least 2 s before its `listed_at_ns`, and whose `base` equals the current base tree ID keeps its recorded `added` and `removed`, and its subfolders are taken from the rows below it; any other folder is listed again, compared with the base's names in it, its subfolders followed, and its row rewritten when the index is writable (d-8kq2nk); all rows of one identity are written in one `BEGIN IMMEDIATE` transaction, replacing earlier rows in place, since each row carries its own key and no state depends on it; a folder whose row is missing or undecodable is listed (invariants 5 and 6).
- No base names on a hit (the Task 8b review's P1 item 2): the files on disk the base lacks are the union of the rows' `added`, and the attachments the disk lacks are the union of `removed` under `lodge/attachments/`; the base's names, from `Committed.listing` of the current commit, are taken only when at least one folder is listed again, so a seen read of an unchanged checkout runs no `ls-tree` and builds no 160,800-path set; `identities()` then builds no mapping at all, and `listings()` builds the current one on first use.
- Without a usable index the walk of Task 8b runs, with the base's names, so the output is the same.

- [ ] **Step 1: Write the failing tests** (`tmp_path`, each comparing with Task 8b's walk): `test_unchanged_folders_are_not_listed` (patched `os.scandir` not called on a second identity); `test_seen_identity_takes_no_base_names` (on a second identity a patched runner sees no `ls-tree`, and `Committed.listing` is not called); `test_new_file_in_a_listed_folder`; `test_new_subfolder_with_a_file`; `test_deleted_untracked_file`; `test_rename_within_a_folder`; `test_deleted_attachment_is_absent` (a committed attachment removed from disk: absent from the listing on the second identity, with no `ls-tree`); `test_change_in_the_same_second_as_the_listing` (a row listed within 2 s of the folder's ctime is not trusted); `test_mtime_set_back_still_detected` (`os.utime` to the old mtime after adding a file: ctime differs); `test_base_change_relists` (a commit that adds a file: every folder listed again against the new base, the listing agrees); `test_read_only_index_falls_back_to_the_walk`; `test_interrupted_folder_write_lists_again` (a failure injected after each SQL statement of the folder write: the next identity agrees with the walk).
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement; FOLD-1 through `lodge add`.
- [ ] **Step 4:** gate; the replay at 160,000 files, `seen`, recorded with the identity's share, and `identities()` on a new store object timed as in Task 8c (expected about 0.08 s isolated: the git group 0.06, the flag scan 0.015, the folder rows 0.006); the tests run once with `--basetemp` on a FUSE-mounted disk where one is at hand, the result recorded, and if any fails there the signature cache is disabled on that file system kind (detected by `os.statvfs` and `/proc/mounts`) with the walk used instead.
- [ ] **Step 5:** commit, push.

## Insert after Task 11: Task 11b

### Task 11b: Raw blob IDs through a private git index

**Files:**
- Create: `src/lodge/gitstore/raw_index.py` (the private index: its path, the conditions for using it, the build, the refresh, and the two calls)
- Modify: `src/lodge/gitstore/identity.py` (the overlay from the raw index when it is usable), `README.md` (the raw index beside the index, safe to delete)
- Records: RAW-1 and STOP-2, through `lodge add`, once the coordinator has ruled
- Test: `tests/gitstore/test_raw_index.py` (new), `tests/gitstore/test_raw_index_races.py` (new), `tests/gitstore/test_raw_index_property.py` (new)

**Interfaces:**
- Consumes: Task 8b's `read_disk`, `blob_id`, and `disk_tree` as the oracle; Task 8c's `run_many`, `Committed`, and the one-snapshot key; Task 9's writability and failure rules; Task 11's folder rows.
- Produces:
  ```python
  # gitstore/raw_index.py
  RAW_OVERRIDES: tuple[str, ...]   # -c core.autocrlf=false -c core.attributesFile=/dev/null -c core.ignoreStat=false
                                   # -c core.fsmonitor=false -c core.checkStat=default -c core.trustctime=true
                                   # -c core.symlinks=true -c core.splitIndex=false -c core.untrackedCache=false
                                   # --attr-source=<the empty tree>; and GIT_ATTR_NOSYSTEM=1, GIT_INDEX_FILE=<path> in the environment
  class RawIndex:
      def usable(self) -> bool
      def changes(self, head: str) -> tuple[frozenset[str], dict[str, str | None]] | None
          # (paths diff-files names, path -> raw blob or None for each entry diff-index --cached --raw HEAD reports);
          # None when the raw index's stat moved during the calls twice, or a call failed
      def refresh(self, read: Mapping[str, tuple[os.stat_result, bytes | None]], started_ns: int) -> None
  ```
- Where and when: `<git dir>/lodge/raw.index`, per worktree (`git rev-parse --absolute-git-dir`, taken in the same call as `HEAD`); used in checkout mode when the folder is writable or the file exists, `git --attr-source` is accepted (git 2.40 or later; a refusal is remembered for the store object), and `$GIT_COMMON_DIR/info/attributes` is absent or empty, since `--attr-source` does not cover that file (probe in `plan-fix-6.md`); otherwise the identity runs as Task 8c and Task 11 leave it, with the same output.
- What it holds: one entry per file under `lodge/` outside `lodge/attachments/`, with the stat git took and the blob of the raw bytes, since every conversion is off; it never holds an assume-unchanged or skip-worktree flag, so git's own index, its flags, and the conversion check are not consulted on this path.
- The identity on this path: `diff-files --no-renames -z --name-only` and `diff-index --cached --no-renames -z --raw <HEAD>`, both with `RAW_OVERRIDES` and the pathspec `lodge ':!lodge/attachments'`, start together with `rev-parse` and `merge-base` (`run_many`); the raw index's stat is taken before and after, and when it moved the two run again one after the other, `diff-files` first; the paths to read are those `diff-files` names, those `diff-index` reports as deleted, and the folder rows' added files the raw index lacks; each is read with `read_disk` and hashed by lodge; every other entry `diff-index` reports takes the blob it gives; the overlay is then built and dropped against the base exactly as in Task 8b, attachments from the folder rows, so the ident is the one Task 8b defines.
- The refresh (the racy rule): lodge takes `started_ns = time.time_ns()`, then an `lstat` of each path it read; it passes to `update-index --add --remove --info-only -z --stdin` only the regular files and links whose `mtime_ns` and `ctime_ns` are both at least 2 s before `started_ns`, and the paths now absent; after the call it takes a second `lstat` of each, and removes with `--force-remove` every path whose two `lstat` results differ; a path not passed (too young, or neither a file nor a link) is read again by the next read, as git re-reads a racily clean entry; the refresh runs only when the folder is writable, and a held `raw.index.lock` skips it; a lock older than 10 minutes is deleted first, since git holds it only during one call.
- Why a recorded blob is never stale (the proof the task's tests exercise): assume, as git does and d-8kq2nk already does for git's own index, (F1) any change to a file's bytes gives it a new inode or sets its ctime and mtime from the file-system clock at the change, (F2) that clock is never more than 1 s behind a `time.time_ns()` read earlier, and (F3) `diff-files` with `core.checkStat=default` and `core.trustctime=true` names an entry whose inode, size, mtime, or ctime differ, at least in whole seconds.
  An entry for path P is kept only when the first `lstat` L0 equals the second L1 and L0's mtime and ctime are at most `started_ns` minus 2 s.
  Git's own `lstat` and read of P fall between L0 and L1; had the bytes changed in that span, F1 and F2 would give L1 a new inode or a ctime of at least `started_ns` minus 1 s, unequal to L0's; so git read the bytes P had at L0, recorded L0's stat, and, with conversions off, recorded `blob_id` of those bytes.
  A later change gives, by F1 and F2, a new inode or a ctime at least `started_ns` minus 1 s, which is at least 1 s after L0's ctime, so it differs in whole seconds, and by F3 `diff-files` names P.
  So when `diff-files` does not name P, P's bytes are the ones whose blob the entry holds; and since the entry's mtime is older than the raw index's own write, git never treats it as racily clean, so its content check, the one place a conversion could enter, never runs.
- Building it: the first read in a worktree, or a raw index that git cannot read (deleted and rebuilt), passes every file the identity found, under the same racy rule, in one `update-index` call (1.15 s at 160,800 files, measured); that read is a cold read (d-e3stjn).
- The gate, `add`, `trees()`, branch mode, and the viewer never use the raw index (d-q0tb8r, d-7e8zhd); it holds no flags and no conversion results (d-n6tqzq); a seen read whose `diff-files` names nothing writes nothing.

- [ ] **Step 0:** skeleton.
- [ ] **Step 1: Write the failing tests:** `test_raw_index.py` (each comparing with `disk_tree`, in `tmp_path`): `test_seen_identity_reads_no_file` (a second identity on a new store object: patched `read_disk` never called, and no `ls-files`, `config`, `var`, or `check-attr` call); `test_autocrlf_spellings_read_no_file` (`core.autocrlf` `true`, `input`, and the bare key, in the repository's configuration, CRLF files on disk: agrees, and the second identity reads no file); `test_crlf_rewrite_is_seen` (a record rewritten with CRLF line ends under `core.autocrlf=input`, `git status` clean: the listing holds the CRLF bytes' blob); `test_worktree_and_global_attributes_do_not_convert` (a root `.gitattributes` with a clean and smudge filter, and `$XDG_CONFIG_HOME/git/attributes` with `*.md text eol=crlf`: the raw index's blobs equal `blob_id` of the disk bytes); `test_info_attributes_turns_it_off` (an `info/attributes` file: the raw index is not used, a patched `RawIndex.changes` is not called, and the listing agrees); `test_old_git_turns_it_off` (the runner patched to exit 129 for `--attr-source`: not used, agrees); `test_read_only_git_dir_turns_it_off` (skipped as root); `test_assume_unchanged_and_skip_worktree_agree` (as Task 8b's flag tests, on this path); `test_symbolic_link_and_fifo_agree`; `test_attachments_never_hashed` (a patched `read_disk` is never called for an attachment, and the raw index holds no attachment); `test_corrupt_raw_index_is_rebuilt` (garbage bytes: the read agrees, and the next identity reads no file); `test_held_lock_skips_the_refresh` (output the same, the file unchanged); `test_stale_lock_is_removed`; `test_seen_read_writes_nothing` (after `git status`, the raw index's bytes and stat are unchanged).
  `test_raw_index_races.py` (the racy rule, with a patched clock and runner): `test_young_file_is_not_recorded` (a file written 1 s before `started_ns`: not passed, and read again by the next identity); `test_change_between_lstat_and_call` (the runner rewrites the file, same size, before `update-index` runs: the entry is removed, and the next identity agrees); `test_change_during_the_call` (the rewrite after `update-index` returns and before the second `lstat`: removed, agrees); `test_same_size_rewrite_with_mtime_restored` (after a recorded entry, a same-size rewrite and `os.utime` back to the old mtime: `diff-files` names it, agrees); `test_replaced_by_rename` (an editor's write to a temporary file renamed over the record: new inode, agrees); `test_two_processes_refresh` (one holds the lock: the other skips, both print the same); `test_raw_index_moved_between_the_two_calls` (another refresh commits between `diff-files` and `diff-index`: the pair runs again, agrees).
  `test_raw_index_property.py`: `test_random_edits_agree_on_the_raw_path` (Task 8b's 200 seeded sequences, with the root `.gitattributes` removed at the start of each sequence (the Task 8b review's A6), plus `core.autocrlf=input` set in half of them, CRLF rewrites, and a clock patched forward 3 s after each operation so entries are recorded: after each sequence the listing agrees with `disk_tree`, and two states with equal idents have equal exact trees).
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement; RAW-1 and STOP-2 through `lodge add` after the coordinator's ruling.
- [ ] **Step 4:** gate; at `s90000`, on a copy whose `.git` is writable, `identities()` on a new store object, clean and with one edit, best of three, under the isolated configuration and under a `GIT_CONFIG_GLOBAL` file holding `core.autocrlf=input`: expected about 0.05 s in both, against 0.785 s and 3.148 s at 83ef70b; the raw index's build time and size recorded; the tests of this task run once with `--basetemp` on a FUSE-mounted disk where one is at hand, as Task 11's do, and if any fails there the raw index is turned off on that file system kind with Task 11's detection.
- [ ] **Step 5:** commit, push.

## Replace Task 12

### Task 12: The recorded table, and the stop on the targets

**Files:**
- Create: `docs/superpowers/plans/2026-10-31-lodge-at-scale/timings.md`
- Modify: `scripts/bench_reads.py` (a `--mode chained` that runs `changed`'s distinct edits without restoring the saved index between runs, and prints the index's epoch before and after, for the clears per hundred changed reads; Task 1's `changed` restores the copy each run; a `--git-config FILE` that runs every command with `GIT_CONFIG_GLOBAL=FILE`, `GIT_CONFIG_NOSYSTEM=1`, and `GIT_ATTR_NOSYSTEM=1`, and a `--startup` that times `python -c pass`, `python -c "import lodge.main"`, and `lodge guide --read` with the build's Python, best of nine), `README.md` (one paragraph: the index and the raw index, where they live, one index file per build, cleared in place past its cap, that `rm -r` of either folder is safe at any time and reclaims all its space, `LODGE_INDEX=off`)

**Interfaces:**
- Consumes: every task.
- Produces: `timings.md`, for `s900`, `s9000`, and `s90000` on native disk, per line of `scripts/bench_reads.txt`: the base build of Task 1, this branch `cold`, `seen`, and `changed`, `check --gate` included, cold reads in their own column and under no stop (d-e3stjn), with Task 9's time of one clear beside them, with the output and exit-status comparison against the base build (identical, or the lines Tasks 5 to 7 changed on purpose, named); each search's candidate count, with searches over 5,000 candidates in a table of their own (d-me8vm3); the index file's size per store against d-4pbeax's figure, and the raw index's size; at `s90000`, the clears in a `--mode chained` run of 100 consecutive changed reads; the machine's Python, SQLite, git, and disk kind; where a FUSE-mounted copy of `s90000` is at hand, the same `show {code}` `seen` on it, one line, without its path.
  Two rows of their own at `s90000`:
  - The start-up floor (`--startup`): measured at 83ef70b as 18.0 ms, 142.3 ms, and 172.6 ms; expected about 18 ms, 0.108 s, and 0.139 s with LAZY-1, else about 18 ms, 0.142 s, and 0.173 s; every `seen` read is at least this floor, and the row says how much of the 0.3 s it leaves.
  - `core.autocrlf=input` (`--git-config` with a file holding `[core] autocrlf = input`), `seen` and `changed` for `show {code}`, `waiting`, and `search berth --brief`: at 83ef70b the identity alone takes 3.148 s, so without Task 11b every such read is above both stops; expected with Task 11b within 0.01 s of the same lines under the isolated configuration.
- [ ] **Step 1:** run the replay, the startup row, and the autocrlf row; write `timings.md`.
- [ ] **Step 2:** the stop (d-26e6zj as narrowed by STOP-2, d-232gxs, d-hxmdkz): if at 160,000 files, under either configuration, `show`, `waiting`, `threads`, `thread`, or a search with at most 5,000 candidates is above 0.3 s `seen`, a search with more than 5,000 candidates is above 1.0 s `seen`, or a read is above 3 s `changed`, `timings.md` gives the phase table, with the start-up floor as its first phase, and the ledger records that the server question goes to the coordinator; broad searches are reported apart with their candidate counts, whatever they are.
- [ ] **Step 3:** gate, commit, push.

## Amend the Global Constraints

Replace the bullet beginning "The gate and `add` (and every command but the five indexed reads) read exact trees" with:

- The gate and `add` (and every command but the five indexed reads) read exact trees: every working-tree file read and hashed by lodge, committed trees by git's object IDs; they never take derived state, flags, tree claims, or raw blob IDs from the index or the raw index (Task 11b), and use only the index's parse cache, keyed by those hashes (d-q0tb8r, d-7e8zhd).

## Amend Task 10a

In Task 10a's Consumes, after "Task 8b's `identities`, `listings`, `texts`", add "as Task 8c leaves them (`listings()` builds mappings on first use, so a stored-state hit calls `identities()` only)".
