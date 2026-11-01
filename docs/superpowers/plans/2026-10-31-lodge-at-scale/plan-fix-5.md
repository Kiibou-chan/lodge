# Plan fix round 5

Recheck: `plan-recheck-4.md` (W1, W3, and W4 Important; W2 and W5 to W10 Minor).
SCALE-1 is answered: the author chose A, about 305 MB at 160,000 files with four states (d-j51qmy).
The three Important findings were taken as the recheck names them, and the Minors where cheap; one part of W6 is parked.
The calls are d-a8gkrh (the cap formula), narrowed by d-cqr414 (every write checks the cap) and d-j51qmy (1,900 bytes per file), with d-3ck8km for WAL settings and d-bzp30x (the lock's order, the refused upgrade, and builds' ages; narrows d-e3stjn).

| Finding | Change in the plan | Decision |
|---|---|---|
| W1, no interface yields the epoch | `Index.epoch()` in Task 9, read once before a build's first lookup; `keep_state` reads `meta.epoch` inside its write transaction and compares; `test_clear_between_the_parses_and_facts_lookups` | d-c6cegr |
| W2, the clear could empty `meta` | Every table but `meta`; the epoch starts at 1 and is raised in the clear's transaction; `test_two_clears_in_a_row_raise_the_epoch` | d-c6cegr |
| W3, the cap was twice the author's figure | `INDEX_FILE_CAP = max(16 MiB, INDEX_BYTES_PER_FILE × files)`, about 305 MB at 160,000 files; every write checks the cap and clears when over it provided a state was kept since the last clear or the units inserted since the last clear number at least the tree's file count; Task 12 reports the file's size against d-j51qmy | d-j51qmy, d-a8gkrh, d-cqr414 |
| W4, secure delete writes the whole file through the WAL | `secure_delete=OFF` and `journal_size_limit=16777216` on every connection; `test_secure_delete_off` keeps only the SQLite-default capability skip; `test_clear_wal_bounded` runs on every build and checks a non-empty WAL at most 16 MiB before truncation | d-a8gkrh |
| W5, a refused upgrade drops the shared lock | The corrupt rule applies in `open_index` only; a refused upgrade closes the lock file and returns `None`; `test_refused_upgrade_returns_none_and_holds_no_lock` | d-bzp30x |
| W6, facts make clears periodic | Taken in part: Task 10c Step 4 records the facts bytes per changed read, and Task 12 the clears in 100 consecutive changed reads | none needed |
| W7, the lock's order and the lockless cases | `LOCK_SH` before connecting, released after closing; an existing lock file opened read-only; without `fcntl` a corrupt file turns the index off; one test each | d-bzp30x |
| W8, a build that only reads looks old, and the folder is unbounded | A build's age is its lock file's modification time, touched on opening; builds beyond the four most recently touched go too, under the same lock | d-bzp30x |
| W9, leftovers of the sweep | The invariants' decisions named; `index_db.py` no longer lists pruning; Task 10b gives `keep_state`'s full signature; the words clauses of Task 10a's cross-process tests moved to Task 10b; the cost row says only the clearing read pays | none needed |
| W10, personal paths | Removed from `brief.md`, `review-brief.md`, and `plan-recheck-3.md` | none needed |

## Parked

- W6, the eviction of facts rows no remaining state names: it changes facts from immutable to state-owned, so it waits for Task 10c's and Task 12's measurements of how often clears come.
