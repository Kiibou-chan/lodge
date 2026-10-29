### Task 9: The git store

**Files:**
- Create: `src/lodge/gitstore/git.py` (one `run(args, cwd, env=None, input=None) -> str` wrapper), `src/lodge/gitstore/trees.py` (reading trees with `ls-tree` and `cat-file --batch`), `src/lodge/gitstore/checkout.py`, `src/lodge/gitstore/branch.py`, `src/lodge/gitstore/setup.py` (settings, init, lock)
- Test: `tests/gitstore/repos.py` (`bare_remote`, `clone(remote, name)`, `worktree(clone, name)`), `tests/gitstore/test_checkout.py`, `tests/gitstore/test_branch.py`, `tests/gitstore/test_setup.py`

**Interfaces:**
- Consumes: `lodge.app` ports and errors, `lodge.core` (`Tree`, `CoreSettings`, `parse_core_settings`).
- Produces (exported from `lodge.gitstore`):
  ```python
  @dataclass(frozen=True) class StoreSettings: mode: Literal["checkout", "branch"] = "checkout"
      branch: str = "lodge"; remote: str = "origin"; base: str = "main"
      max_staleness_seconds: int = 60; commit_trailer: str | None = None
  @dataclass(frozen=True) class ProjectSettings: core: CoreSettings; store: StoreSettings; raw: Mapping[str, object]
  class NotARepository(LodgeError); class NotInitialised(LodgeError); class GitMissing(LodgeError)
  def repo_root(cwd: Path) -> Path
  def load_settings(root: Path) -> ProjectSettings      # reads .lodge.toml; absent means defaults; known sections
                                                        # length, import, store, hook; TOML and settings errors
                                                        # become LodgeError; [hook] keys are validated by
                                                        # hook.parse_hook_settings, which main calls
                                                        # for every command except the hook route itself
  def open_store(root: Path, settings: StoreSettings, clock: Clock) -> Store
  def init_store(root: Path, settings: StoreSettings) -> str
  def data_root(root: Path, settings: StoreSettings) -> Path | None   # None in branch mode
  ```
- Every `git` call: `-C <path>`, `check=True`, `capture_output=True`, `stdin=DEVNULL` unless `input` is given; a failure becomes `LodgeError` with git's first stderr line; a missing `git` binary becomes `GitMissing`.
- Trees read every file under `lodge/` except `lodge/attachments/**`, which they list without reading, so `load` reports stray files; in checkout mode that is every file on disk there, tracked or not; files are decoded as strict UTF-8 and one that fails becomes a problem 1 naming its path, not a crash.
- Checkout mode: `trees()` gives the working tree (rev `None`) and the tree at `merge-base HEAD <ref>`, `<ref>` the first of `<remote>/<base>` and `<base>` that exists, or the empty tree when neither does or `HEAD` is unborn; `freshness()` is `None`; `publish` takes the lock, checks that every path it writes still has the text it had in `base` (or is still absent), writes, `git add`s, returns `STAGED`, or `REJECTED` on a mismatch.
- Branch mode: `trees()` returns the tree at `refs/remotes/<remote>/<branch>` twice, fetching first (under the lock, so concurrent viewer requests never fetch at once) with `git fetch <remote> +refs/heads/<branch>:refs/remotes/<remote>/<branch>` when lodge's own stamp file (`<git common dir>/lodge-fetched`, holding the time from `clock`) is older than `max_staleness_seconds` or the store is marked stale; a failed fetch keeps the cached ref and `freshness()` says `fetch failed; data as of <time>`, otherwise `<branch>@<short rev>, fetched <n> s ago`. `publish`: under the lock, if the ref is not at `base.rev` return `REJECTED`; else build the commit with `GIT_INDEX_FILE` set to a temporary file (`read-tree base.rev`, `hash-object -w --stdin`, `update-index --add --cacheinfo`, `write-tree`, `commit-tree -p base.rev`, trailer appended to the message when set), push `<commit>:refs/heads/<branch>` without force; on success `update-ref` the remote-tracking ref and return `PUBLISHED`; on a non-fast-forward rejection mark the store stale and return `REJECTED`.
- Lock: `<git common dir>/lodge.lock` created with `os.open(..., O_CREAT | O_EXCL)`, removed in `finally`; a second process waits up to `lock_wait_seconds` (a keyword parameter of `open_store`, default 30), polling every 100 ms, then reports the lock's path; a lock older than ten minutes is reported as stale with its path rather than broken.
- `init_store`: checkout mode creates `lodge/decisions/.gitkeep` and `lodge/spec/.gitkeep`; branch mode builds a parentless commit holding the same with plumbing and pushes it to `refs/heads/<branch>`; both refuse when already initialised. Reading before init raises `NotInitialised`.

- [ ] **Step 1: Write failing tests** with real git: `test_settings_absent_defaults`, `test_settings_malformed_toml_is_lodge_error`, `test_settings_unknown_section_named`, `test_checkout_publish_stages_not_commits`, `test_checkout_published_is_merge_base_with_remote_base`, `test_checkout_published_empty_without_base`, `test_checkout_publish_rejects_changed_file`, `test_branch_init_pushes_orphan`, `test_branch_publish_commits_on_base_and_pushes`, `test_branch_fetch_only_when_stale`, `test_unrelated_fetch_does_not_refresh_stamp`, `test_branch_fetch_failure_serves_cache_and_says_so`, `test_branch_moved_ref_rejected`, `test_branch_rejected_push_marks_stale`, `test_attachments_listed`, `test_not_a_repository`, `test_not_initialised`, `test_lock_waits_then_reports_path` (with `lock_wait_seconds=0.2`), `test_stray_and_non_utf8_files_reported`, `test_checkout_unborn_head_published_empty`.
- [ ] **Step 2: Run**; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Write the concurrency tests** (Review Focus 1), each asserting that both decisions are on the remote branch and that `check_state` of the remote tip is clean: `test_two_clones_add_at_once` (two clones, both read the same tip, both add, the second retries) and `test_two_worktrees_of_one_clone_add_interleaved`, where a wrapper over B's store runs A's whole `add` between B's `trees()` and B's `publish`. Also `test_stale_tree_publish_rejected_ref_unchanged` at store level: two stores over two worktrees of one clone both read, A publishes, B publishes its stale tree and gets `REJECTED` with the ref left at A's commit. Run; expected: PASS.
- [ ] **Step 5: Run** `sh scripts/check.sh`; expected: green.
- [ ] **Step 6: Commit and push.**


## Carried from earlier tasks (ledger rulings, binding)

- Attachments live at `lodge/attachments/<decision id>/<name>`, and check 2 resolves a listed name there (Task 5 M3): the tree lists each attachment file at that full path, unread.
- A file that cannot be read becomes a problem through `load`, never an exception: every read already surfaces it (Task 6 I4, Task 8 I1).
- `add` reads `trees()` once per attempt and may retry up to three times on `REJECTED` (Task 8); the store never retries on its own.
