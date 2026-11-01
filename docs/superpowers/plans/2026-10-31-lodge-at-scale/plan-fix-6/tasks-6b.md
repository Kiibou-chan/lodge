# Plan fix 6b: task texts to paste into the plan

These replace `tasks.md` of plan fix 6, which is withdrawn whole (Task 11b, RAW-1, LAZY-1, and STOP-2 are gone).
Order: Task 9 (being built), Task 8c, Task 10a, Task 10b, Task 10c, Task 11, Task 12.
Measurements behind every number: `plan-fix-6b.md`, and `plan-fix-6.md` where it is cited.

## Insert into "Calls made", after item 21

22. R11-A or R11-B (proposed, for the coordinator; one of them): whether the fast identity reads every file on every read (exact; R11-A), or, with no conversion source present, takes stat-clean files at git's index blob as `git status` does (R11-B); Task 8c carries the one ruled.
23. CONV-1 (proposed, records the coordinator's ruling 4, narrows d-232gxs): where a conversion source is present the identity reads every file it may convert (d-dqpf59); that configuration is reported beside the targets, not under them; the stop (d-26e6zj) applies to the configuration without conversions.
24. FOLD-1 (proposed, narrows d-8kq2nk): a folder row holds the folder's difference from the base tree, keyed by the base tree's ID and taken with `lstat`, so a hit takes none of the base's names and never follows a link (Task 11).

## Replace the "Expected cost" table's rows "a point read" and "after one changed record"

| Read | Today | After Tasks 2 to 4 | After Task 11 |
|---|---|---|---|
| a point read (`show`, `waiting`), seen state, no conversion source | as before | as before | about 0.26 s plus the app path and printing, with R11-B: one process measured at 0.273 s best and 0.278 s median doing everything but the app path and printing (Python 0.019, imports 0.123, parser 0.017, the git group 0.066 to 0.072, published tree and flag scan 0.018, folder rows 0.0075, digest and index hit 0.0067), less 0.012 for the parser of the named command; with R11-A about 3.4 s (every file read, 3.148 s) |
| a point read, seen state, `core.autocrlf=input` | as before | as before | about 3.4 s: every file read (identity 3.148 s at 83ef70b) plus the rest; reported beside the targets (CONV-1) |
| after one changed record (checkout, uncommitted), no conversion source | as before | as before | about 3 s as before, with the identity at about 0.1 s and the current listing's mapping at 0.14 s (`ls-tree` 0.058 plus parsing 0.080), not 0.06; Task 12 measures it |

## Insert after Task 9: Task 8c

### Task 8c: The fast identity without needless work, and the Task 8b review's identity findings

Built after Task 9 and before Task 10a; it changes no port, and no output except where the Task 8b review found the fast listing disagreeing with the exact tree.

**Files:**
- Create: `src/lodge/gitstore/disk.py` (the one disk reader: folders and files opened relative to their parent's descriptor, never through a link)
- Modify: `src/lodge/gitstore/git.py` (`run_many`), `src/lodge/gitstore/identity.py` (the git group under one key of git's index file; `Committed` memoised per store object by commit ID, keeping entry kinds; the overlay through `disk.py`), `src/lodge/gitstore/listing.py` (`identities()` takes both tree IDs from `rev-parse`; `listings()` builds mappings on first use; `texts()` reads blobs only), `src/lodge/gitstore/flags.py` (`scan`, `config_values`), `src/lodge/gitstore/attributes.py` (the key on the sources alone; one `config --list -z` and one `var -l`), `src/lodge/gitstore/checkout.py` (`disk_tree` calls `disk.py`; lines removed, none added), `src/lodge/cli/parser.py` (the parser for the named command), `tests/gitstore/test_identity_property.py` (the review's A6: one line)
- Test: `tests/gitstore/test_identity_lazy.py` (new), `tests/gitstore/test_identity_links.py` (new), `tests/gitstore/test_identity_gitlinks.py` (new), `tests/gitstore/test_git_many.py` (new), `tests/gitstore/test_flag_scan.py` (new), `tests/test_parser_named.py` (new)

**Interfaces:**
- Consumes: Task 8b's `CheckoutIdentity`, `CheckoutListing`, `BranchListing`, `Flags`, `Conversions`, and its tests as the oracle where they agree with the exact readers; `disk_tree` and `read_tree` as the exact readers.
- Produces:
  ```python
  # gitstore/git.py
  def run_many(calls: Sequence[Sequence[str]], cwd: Path) -> list[subprocess.CompletedProcess[bytes]]
      # starts every call before waiting for any; results in the order of `calls`;
      # request_exit waits until all have returned; a missing git raises GitMissing as attempt does
  # gitstore/disk.py
  def walk(root: Path) -> DiskWalk          # names with kinds, the real folders reached, the folders that could not be listed
  def read_at(walked: DiskWalk, path: str, *, attachment: bool = False) -> bytes | None
      # None (deleted) unless every folder on the path is a real folder the walk reached; never follows a link;
      # a link's target bytes, an empty file for anything not regular, as disk_tree reads them
  # gitstore/flags.py
  def scan(raw: bytes) -> Flagged         # equals Task 8b's decode loop on every input
  def config_values(raw: bytes) -> Mapping[str, str | None]   # `config --list -z`; a key with no value is None, git's true
  # gitstore/identity.py
  class Committed:                        # per store object; at most the two most recent commits
      def tree_id(self, rev: str | None) -> str            # `rev-parse rev:lodge`, EMPTY_TREE when absent or not a tree
      def listing(self, rev: str | None) -> CommittedListing   # `ls-tree` once per commit ID, each entry with its kind
  ```
- Lazy listings (the review's P1 item 1): `identities()` resolves `HEAD` and the published commit as today and takes both idents without an `ls-tree` of the published commit; `listings()` builds a mapping only when called, from `Committed.listing`, so a published commit equal to `HEAD` costs no second `ls-tree`; until Task 11 the walk still needs the base's names, so `HEAD`'s mapping is still built in `identities()`.
- One snapshot of git's index (plan fix 6, `measure/race.py`; the review confirmed it): `diff-index --cached`, `diff-files`, `ls-files -t -v`, `config --list -z`, `var -l`, and the `rev-parse` and `merge-base` calls start together through `run_many`, with commit IDs pinned; the stat of git's index file (inode, size, `mtime_ns`, `ctime_ns`) is taken before the first starts and after the last ends; when they differ, the whole group and every result that depends on it (flags, conversions) are discarded and run again, at most twice, and then the identity, `listings()`, and `texts()` all take one exact tree from `disk_tree`, so a `git add` between two calls never hides an edit.
- Conversions keyed on their sources (P1 item 3): the key is the configuration values, the `git var` values, every source file's stat and bytes, the index-only attributes files, and the index stat, without the path set; the path set is built, and `check-attr` run, only on a miss; nested `.gitattributes` come from the walk's names and from `scan`'s attributes entries, never from an `rsplit` of every path; where a source converts, the paths it may convert are read from disk (d-dqpf59, CONV-1).
- Flags (P1 item 4): `scan` counts the entries and the `H` entries and finds `.gitattributes\0`; only when the counts differ does it run Task 8b's loop.
- Merged configuration calls (P1 item 5): one `config --list -z` gives `core.autocrlf` and `core.attributesFile` in git's spellings, a key with no value counting as true (review A2); one `var -l` gives `GIT_ATTR_GLOBAL` and `GIT_ATTR_SYSTEM`, a variable it omits being asked with `git var NAME` as today; a failing call converts every path.
- Links (review A1 and R3): `disk_tree` and the overlay read through `disk.py` only; a folder is entered with `O_NOFOLLOW | O_DIRECTORY` relative to its parent's descriptor and a file opened with `O_NOFOLLOW` relative to its folder's (a link read with `readlink` relative to it); an overlay path, attachment or not, whose folders are not all real folders the walk reached is deleted, never read; a folder swapped for a link after its parent was listed is read as the link it now is; a folder that cannot be listed hides its base files as `disk_tree` does (review A3); `disk_tree`'s result changes only in that swap.
- Gitlinks (review A4 and R13): `Committed.listing` keeps each entry's kind; in checkout mode a base entry that is not a blob always joins the overlay, so the disk decides, as `disk_tree` does; in branch mode such an entry keeps `read_tree`'s representation, and `texts()` gives it empty text without asking `cat-file`.
- The parser: `parse` builds a parser holding only the subcommand that `argv[0]` names, with all its arguments; `--help`, `-h`, `--version`, no command, and a name that is not a command take the full parser; every help and error text is unchanged (14.4 ms against 1.9 ms, `measure-6b/parser_partial.txt`).
- R11, as ruled: with R11-A, `identities()` reads every file through `disk.py` in every configuration, as d-dqpf59 does for conversions; with R11-B, it takes stat-clean files at git's index blob when no conversion source is present, and a test records the ruled divergence (below).
- Untouched: the gate, `add`, `trees()` but for `disk.py`, and branch mode's tip resolution.

- [ ] **Step 0:** skeleton.
- [ ] **Step 1: Write the failing tests** ("agrees" means equal to the exact reader's tree, `disk_tree` in checkout mode, `read_tree` in branch mode):
  `test_identity_lazy.py`: `test_identities_run_no_ls_tree_for_published` (a patched runner counts `ls-tree` calls: clean store with published equal to `HEAD`, one; then `listings()`, still one; published behind `HEAD`, `identities()` one and `listings()` two); `test_lazy_listings_agree` (clean, an unstaged edit, an untracked file, a staged deletion, published behind `HEAD`, branch mode); `test_staged_between_diff_calls_is_seen` (the runner runs `git add` of an edited record after the first call of the group returns: agrees; fails on Task 8b's code); `test_index_changing_every_time_falls_back_to_exact` (the runner touches git's index file after every group: the identity, `listings()`, and `texts()` all agree with one `disk_tree`, and three groups ran); `test_conversion_key_takes_no_paths` (a second identity on one store object makes no `check-attr` call and never builds the path set, checked by a path source that raises); `test_nested_attributes_found_without_a_path_scan` (`lodge/decisions/.gitattributes` with `*.md text eol=crlf`, once on disk only and once in git's index only: agrees); `test_bare_autocrlf_key_converts` (review A2: a `[core]` section with a bare `autocrlf` line, a CRLF checkout of one record, `git status` clean: agrees); with R11-B, `test_removed_attributes_follow_the_index` (the review's `removed_attrs.py` steps with an `ident` attribute: the read prints git's index text, recorded as R11-B's case), or with R11-A, `test_removed_attributes_agree` (the same steps, and the CRLF variant: agrees).
  `test_identity_links.py`: the three review A1 probes, `test_folder_replaced_by_symlink_to_copy`, `test_folder_replaced_by_symlink_to_other_content`, and `test_attachments_folder_symlink`; `test_folder_link_to_outside_is_never_read` (a link to a folder outside the repository holding `old.md`: no outside bytes in the listing or `texts()`); `test_link_inside_an_attachment_path`; `test_folder_swapped_for_link_during_the_walk` (a patched `os.scandir` swaps a listed folder for a link before it is entered: both readers give the link, never the files behind it); `test_unlistable_folder_agrees` (review A3, skipped as root).
  `test_identity_gitlinks.py` (review A4 and R13, each in checkout and branch mode against the exact readers): `test_empty_submodule_folder`; `test_populated_submodule`; `test_submodule_commit_absent_from_the_object_database` (branch mode: `texts()` gives the empty text `read_tree` gives, and no `cat-file` request for it).
  `test_git_many.py`: `test_results_in_call_order`; `test_all_started_before_any_awaited` (a patched `Popen` records starts and waits); `test_request_exit_waits_for_every_call`; `test_missing_git_raises_git_missing`.
  `test_flag_scan.py`: `test_scan_equals_the_loop` (500 seeded buffers in `ls-files -t -v -z` form with every tag git prints, lower-case tags, root and nested `.gitattributes`, and paths that are not UTF-8); `test_config_values_spellings` (a bare key is None, `autocrlf=` the empty string, `input`, `true`, `yes`, `on`, `1`, `false`, `no`, `off`, `0`, values holding newlines).
  `test_parser_named.py`: `test_help_texts_unchanged` (`lodge --help` and `lodge <command> --help` for every command, byte for byte against the full parser); `test_errors_unchanged` (an unknown command, a missing argument, and a bad option for each command, standard error and exit status against the full parser); `test_named_parser_builds_one_subcommand`.
  `test_identity_property.py`: the review's A6, `(repo / ".gitattributes").unlink(missing_ok=True)` at the top of each sequence; the review's four mutants (no diff calls, no flagged paths, no untracked paths, no conversions) each fail it, run once and recorded in the report.
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement; the Task 8b tests pass unchanged except where they encoded a disagreement with the exact readers, each such edit listed in the report.
- [ ] **Step 4:** gate; at `s90000`, isolated configuration, `identities()` on a new store object, clean and with one edit, best of three, with each stage's share: expected about 0.34 s against 0.785 s with R11-B, about 3.1 s with R11-A; the same under `core.autocrlf=input`, expected about 3.1 s (CONV-1); `lodge guide --read` and `python -c "import lodge.main"`, best of nine: about 0.16 s and 0.145 s, the first about 0.012 s below today; above 0.45 s for the R11-B identity, the report gives the stage table and the ledger names it.
- [ ] **Step 5:** commit, push.

## Replace Task 11

### Task 11: Untracked files through folder signatures

**Files:**
- Create: `src/lodge/gitstore/folders.py`
- Modify: `src/lodge/gitstore/identity.py` (the walk replaced when an index is writable or holds rows; the base's names taken only when a folder is listed), `src/lodge/gitstore/index_db.py` (a `folders` table), `src/lodge/main.py` (the store is handed the index at construction)
- Records: FOLD-1, through `lodge add` (scope `process`, `work_item` the plan, narrowing d-8kq2nk)
- Test: `tests/gitstore/test_folders.py` (new)

**Interfaces:**
- Consumes: Task 8c's `disk.py`, `Committed`, and `run_many`; Task 9's `open_index`, settings, and failure modes.
- Produces: a table `folders(path, ino, mtime_ns, ctime_ns, listed_at_ns, base, added, removed)`, `added` being `marshal` of the folder's entries the base lacks, each with its kind (a file where the base has a folder, or a folder where it has a file, counts as lacking), and `removed` `marshal` of the base's names in that folder absent from disk; for each folder lodge takes `lstat`, then lists it through `disk.py`, then takes the listing time, in that order (the correctness review's M7); a folder whose `lstat` shows a real folder matching its row, whose row's `ctime_ns` is at least 2 s before its `listed_at_ns`, and whose `base` equals the current base tree ID keeps its recorded `added` and `removed`, and its subfolders are taken from the rows below it; a folder that is now a link or a file is listed again from its parent, and every row below it is dropped; any other folder is listed again, compared with the base's names in it, its subfolders followed, and its row rewritten when the index is writable (d-8kq2nk); all rows of one identity are written in one `BEGIN IMMEDIATE` transaction, replacing earlier rows in place, since each row carries its own key and no state depends on it; a folder whose row is missing or undecodable is listed (invariants 5 and 6).
- No base names on a hit (the Task 8b review's P1 item 2): the files on disk the base lacks are the union of the rows' `added`, and the attachments the disk lacks are the union of `removed` under `lodge/attachments/`; the reachable real folders are the rows' folders; the base's names, from `Committed.listing` of the current commit, are taken only when at least one folder is listed again, so a seen read of an unchanged checkout runs no `ls-tree` and builds no 160,800-path set; `identities()` then builds no mapping, and `listings()` builds the current one on first use.
- Without a usable index the walk of Task 8c runs, with the base's names, so the output is the same.

- [ ] **Step 1: Write the failing tests** (`tmp_path`, each agreeing with `disk_tree`): `test_unchanged_folders_are_not_listed` (patched listing not called on a second identity); `test_seen_identity_takes_no_base_names` (on a second identity a patched runner sees no `ls-tree`, and `Committed.listing` is not called); `test_new_file_in_a_listed_folder`; `test_new_subfolder_with_a_file`; `test_deleted_untracked_file`; `test_rename_within_a_folder`; `test_deleted_attachment_is_absent` (a committed attachment removed from disk: absent on the second identity, with no `ls-tree`); `test_folder_replaced_by_link_drops_its_rows` (the three Task 8c link probes, each on a second identity after rows were written); `test_change_in_the_same_second_as_the_listing` (a row listed within 2 s of the folder's ctime is not trusted); `test_mtime_set_back_still_detected` (`os.utime` to the old mtime after adding a file: ctime differs); `test_base_change_relists` (a commit that adds a file: every folder listed again against the new base); `test_read_only_index_falls_back_to_the_walk`; `test_interrupted_folder_write_lists_again` (a failure injected after each SQL statement of the folder write: the next identity agrees).
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement; FOLD-1 through `lodge add`.
- [ ] **Step 4:** gate; the replay at 160,000 files, `seen`, recorded with the identity's share, and `identities()` on a new store object timed as in Task 8c (with R11-B expected about 0.1 s isolated: the git group 0.07, published tree and flag scan 0.018, folder rows 0.0075); the tests run once with `--basetemp` on a FUSE-mounted disk where one is at hand, the result recorded, and if any fails there the signature cache is disabled on that file system kind (detected by `os.statvfs` and `/proc/mounts`) with the walk used instead.
- [ ] **Step 5:** commit, push.

## Replace Task 12

### Task 12: The recorded table, and the stop on the targets

**Files:**
- Create: `docs/superpowers/plans/2026-10-31-lodge-at-scale/timings.md`
- Modify: `scripts/bench_reads.py` (a `--mode chained` that runs `changed`'s distinct edits without restoring the saved index between runs, and prints the index's epoch before and after, for the clears per hundred changed reads; Task 1's `changed` restores the copy each run; a `--git-config FILE` that runs every command with `GIT_CONFIG_GLOBAL=FILE`, `GIT_CONFIG_NOSYSTEM=1`, and `GIT_ATTR_NOSYSTEM=1`; and a `--startup` that times `python -c pass`, `python -c "import lodge.main"`, and `lodge guide --read` with the build's Python, best of nine), `README.md` (one paragraph: the index, where it lives, one file per build, cleared in place past its cap, that `rm -r` of the folder is safe at any time and reclaims all its space, `LODGE_INDEX=off`)

**Interfaces:**
- Consumes: every task.
- Produces: `timings.md`, for `s900`, `s9000`, and `s90000` on native disk, per line of `scripts/bench_reads.txt`, under `--git-config /dev/null` (no conversion source): the base build of Task 1, this branch `cold`, `seen`, and `changed`, `check --gate` included, cold reads in their own column and under no stop (d-e3stjn), with Task 9's time of one clear beside them, with the output and exit-status comparison against the base build (identical, or the lines Tasks 5 to 7 and Task 8c's link and gitlink fixes changed on purpose, named); each search's candidate count, with searches over 5,000 candidates in a table of their own (d-me8vm3); the index file's size per store against d-4pbeax's figure; at `s90000`, the clears in a `--mode chained` run of 100 consecutive changed reads; the machine's Python, SQLite, git, and disk kind; where a FUSE-mounted copy of `s90000` is at hand, the same `show {code}` `seen` on it, one line, without its path.
  Two rows of their own at `s90000`:
  - The start-up floor (`--startup`): measured at 83ef70b as 18.0 to 19.8 ms, 142.3 to 149.7 ms, and 158.6 to 172.6 ms; expected about the same, the last about 0.012 s lower (Task 8c's parser); every `seen` read is at least this floor, and the row says how much of the 0.3 s it leaves.
  - The conversion row (CONV-1; `--git-config` with a file holding `[core] autocrlf = input`), `seen` and `changed` for `show {code}`, `waiting`, and `search berth --brief`: the identity reads every file (3.148 s at 83ef70b), so these reads are expected at about 3.4 s `seen`; reported beside the targets, never under the stop.
- [ ] **Step 1:** run the replay, the start-up row, and the conversion row; write `timings.md`.
- [ ] **Step 2:** the stop (d-26e6zj, d-232gxs as narrowed by CONV-1, d-hxmdkz): if at 160,000 files without a conversion source `show`, `waiting`, `threads`, `thread`, or a search with at most 5,000 candidates is above 0.3 s `seen`, a search with more than 5,000 candidates is above 1.0 s `seen`, or a read is above 3 s `changed`, `timings.md` gives the phase table, with the start-up floor as its first phase, and the ledger records that the server question goes to the coordinator; broad searches and the conversion row are reported apart, whatever they are.
- [ ] **Step 3:** gate, commit, push.

## Amend Task 10a

In Task 10a's Consumes, after "Task 8b's `identities`, `listings`, `texts`", add "as Task 8c leaves them (`listings()` builds mappings on first use, so a stored-state hit calls `identities()` only)".

## No change

The Global Constraints keep their text: with Task 11b gone, the gate and `add` already take nothing but parses from the index (d-q0tb8r, d-7e8zhd).
