# Review of Task 4 fix round (a68be3c) and Task 8a (9f933eb)

Reviewed on `read-speed-build` in a detached worktree at 9f933eb; the old build for parity is c388306 (`git archive`, run through the worktree's venv with `PYTHONPATH`).
Status: done. Blocking 0, Important 0, Minor 6.

## Findings

Blocking 0, Important 0, Minor 6.

### Minor

**M1 · Task 4 fix round: three of the 48 case IDs name the wrong thing.**
Handle: `tests/core/test_identical_change.py:~139-143` (the `earlier-day`, `earlier-time`, and `replacement-same-time` IDs) against `snapshots()` (`:75-92`).
OLD's date is `at(0)` = `2026-10-28T10:00+01:00` (`tests/core/checks.py:38`).
The first verb sample's date `at(0)` is that same instant, not an earlier day; `"2026-10-28T09:00:00+00:00"` is that same instant in another offset, not an earlier time; `"2026-10-28T09:30:00+00:00"` is `at(30)`, 30 minutes after OLD, not "same time" (checked with `datetime.fromisoformat`).
Failure scenario: a failure prints `replaces-earlier-day` and the reader looks for a day-earlier date that is not there.
Fix: name them for what they are (`-same-instant`, `-same-instant-other-offset`, `-later`; `replacement-later-other-offset`).
Related: the IDs are a second list kept parallel to `snapshots()`; a sample inserted mid-list keeps the right count and mislabels every case after it, which is the failure the Task 4 review's M2 fix (`pytest.param(..., id=)` pairs) avoided.

**M2 · Task 4 report: the stale status stays on top.**
Handle: `docs/superpowers/plans/2026-10-31-lodge-at-scale/task-4-report.md:3` still reads "Status: NEEDS_CONTEXT" and `:340-342` the stop; the fix round appends a section saying "This supersedes the NEEDS_CONTEXT above".
Failure scenario: a reader who stops at the header treats Task 4 as stopped.
Fix: change the status line in place (the repository's rewrite-in-place rule for overturned findings), keep the history below.

**M3 · `read_tree` stores a commit ID as a "blob" for a gitlink, breaking the invariant `blobs[p] == blob_id(encode(files[p]))`.**
Handle: `src/lodge/gitstore/trees.py:38-43`: `object_ids[path]` takes `ls-tree`'s ID for every non-attachment entry, and `files[path]` is `""` for a non-blob (`other`).
Reproduced: a committed gitlink `lodge/decisions/submod` gives `blobs == '1111...'` (the commit) with text `""`; `disk_tree` never holds that path, and `blob_id(b"")` is `e69de29...`.
Failure scenario: Task 8b/9 treat `Tree.blobs` as the parse-cache key and compare it with the overlay's hashes; a submodule entry under `lodge/` keys the parse of `""` under a commit ID, and `disk_tree`'s test asserts the invariant on the disk side only (`tests/gitstore/test_tree_blobs.py:50-51`), the committed side asserts `== index_blobs` and `set(blobs) == set(files)` only.
Fix: either `object_ids[path] = blob_id(b"")` for non-blob entries (what the text says), or leave it and state in the `Tree.blobs` docstring that a non-blob entry carries the object's own ID; add a gitlink case to `test_read_tree_blobs_are_git_object_ids`.

**M4 · `blob_id` is SHA-1 only; a SHA-256 repository gives two key families in one session.**
Handle: `src/lodge/core/listing.py:11` against `src/lodge/gitstore/trees.py:38` (`ls-tree` IDs).
Reproduced in `git init --object-format=sha256`: `read_tree(...).blobs` holds a 64-hex ID, `disk_tree(...).blobs` a 40-hex one for the same bytes.
Failure scenario: Task 8b's "an entry whose hash equals `base`'s blob is dropped" never fires and Task 9's cache never hits across committed and working states; reads stay correct, only slower, and nothing consumes `blobs` yet.
Fix: record it in the plan for 8b (read `git rev-parse --show-object-format` once and either require sha1 or hash with the repository's algorithm), and say in `blob_id`'s docstring that it is git's SHA-1 key.

**M5 · `Tree.blobs` is undocumented and empty on three derived trees.**
Handle: `src/lodge/core/snapshot.py:29-37` (docstring says nothing about `blobs`); `src/lodge/app/writes.py:92`, `src/lodge/app/threads.py:85`, `src/lodge/core/apply.py:243` build `Tree(...)` with changed files and no `blobs`.
Failure scenario: a Task 9 consumer reads `after_tree.blobs`, finds `{}`, and parses nothing from cache or, worse, treats the empty mapping as "no files".
Fix: one docstring sentence ("`blobs` keys every file but attachments by git blob ID of the bytes read; an empty mapping means the tree was built without keys"), and `disk_tree`'s docstring (`checkout.py:88-93`) names the keys.

**M6 · Naming in `read_tree`.**
Handle: `src/lodge/gitstore/trees.py:25-26,46`: the local `blobs` holds only blob entries, and the mapping handed to `Tree.blobs` is `object_ids`.
Failure scenario: a later edit "fixes" `Tree(rev, files, ..., object_ids)` to pass `blobs`, which drops gitlink keys and silently changes the key set.
Fix: rename the local `blobs` to `blob_paths` (or `fetched`).

## Correctness: what was checked

### Blob IDs equal git's

`/var/tmp/lodge-review-t8a/h/blobs.py` builds a scratch repository with, under `lodge/`: CRLF, LF, empty, non-UTF-8 (including a CESU surrogate sequence and a stray `\xf0(`), BOM, NUL, lone CR, a 300 kB random file, a non-ASCII file name, an executable file, `.gitkeep`, a symlink to a file, to a folder, dangling, with a non-UTF-8 target, a 3000-character target, a nested folder, a gitlink, and two attachments (one a symlink).
Results at 9f933eb:
- `read_tree(HEAD).blobs` equals `git ls-files -s` for every non-attachment path (True).
- `disk_tree().blobs` equals `read_tree().blobs` on every shared path, symlinks and CRLF included (no differences); the only path in the tree and not on disk is the gitlink, the only path on disk and not in the tree is none.
- every `disk_tree` key equals `git hash-object --no-filters --stdin` of the bytes the text re-encodes to, and the re-encoded bytes equal the file's bytes (`read_bytes`) or the link target (`os.fsencode(os.readlink)`), checked on every path.
- `encode(decode(b)) == b` for 20,000 random byte strings of 0 to 11 bytes.
- attachments stay listed and out of `blobs` on both sides.
Not matching git by design: with `core.autocrlf=true` or `text eol=crlf`, git's index blob is the normalised content while `disk_tree` keys the bytes on disk (d-q0tb8r); this is the overlay's concern in Task 8b.
Unreadable files and FIFOs read as `""` and key `e69de29`, as the plan says.

### The snapshot from per-file parses equals `load` in every field

`/var/tmp/lodge-review-t8a/h/fuzz_load.py` runs the old `load` (c388306) and the new one on the same generated trees and compares `repr(Snapshot)` (so dictionary order, problem order, wording, and exceptions count) with `PYTHONHASHSEED=0`.
The corpus is s900 plus the repository's own records plus six real threads and a duplicate thread; each case picks 0-59 files and applies 0-5 of: truncate, CRLF, empty, damaged `---`, lone surrogates, invalid YAML prefix, unbalanced quote, NUL, BOM, duplicate under another record path (decisions, spec, threads), misplace (decision into spec and entry into decisions), stray extras (`lodge/notes.txt`, `lodge/spec/x/y/z.md`, `lodge/attachments`, `.gitkeep` in odd folders, `README.md`, bare `lodge`), rename away from `.md`, a file used as a folder, deletions, shuffled insertion order, and random explicit attachment sets.
Result: identical digests, old against new, for 12 seeds in two rounds (seeds 1, 2, 11 to 13, 16, 21 to 24; 400 or 1,500 cases each, about 17,000 cases and more than 30,000 problems); no case raised.
The one structural difference is parse order (insertion order against sorted order), which only matters if a parser raises, and none did in these inputs.

### Task 4 fix round (a68be3c) against the review's Minors

M1 fixed (`state.py` docstring and `check_change.py` docstring state the rule, d-zyqzkg), M3 fixed (`same_listing` in `core/snapshot.py:40-42`, used by `read_checked` at `state.py` and `committed_gate` at `published.py:41`, four tests pinning revision-independence, contents, paths, attachments; it is exported through core's front door).
M2 fixed in form but see M1 above for the labels.
No behaviour change in `committed_gate` or `read_checked`.

### Gate

`UV_FROZEN=true sh scripts/check.sh` in my worktree at 9f933eb: ruff, mypy strict, vulture, 1631 passed, 1 skipped in 57.9 s, `lodge check --gate` ok, exit 0 (confirms the report's gate line).

### Equivalence of reads, c388306 against 9f933eb

Harness `/var/tmp/lodge-review-t8a/h/compare.py` runs both builds per command in the same directory and compares exit status, standard output, and standard error (a `fetched N s ago` stamp normalised); each scenario starts from `git reset --hard` and `git clean`.
Commands (25, plus `guide`, `guide --read`, and `--version` on the clean store): `show` of a code, of an entry with `--reasoning --provenance`, of a decision, of four refs, of `CODE.why --reasoning`, of a missing ref, and with no ref; `search` of one word (`--brief` and not), a quoted phrase, a code, `--phrase`, two queries, `--by author`, no query, and a word with no hit; `waiting`; `threads`; `thread q-aaaaaa`; `spec`, `spec --area`, `spec --area nope`; `check`; `check --gate`.
Scenarios (34): clean; stray files (shallow and deep); `.gitkeep` in a stray folder; a file outside `lodge/`; attachments (bytes and empty); a duplicate decision, a duplicate entry (same and other area); an entry in `decisions/` and a decision in `spec/`; invalid YAML, an unclosed header, an empty record, a non-UTF-8 record; CRLF rewrites of an entry and a decision; truncated and emptied records; deleted entry and decision; a symlink to a record, a dangling link, a FIFO; a record turned into a folder; a duplicate and an invalid `_area.md`; an invalid thread file and a nested thread path; a staged edit; a committed edit; a committed duplicate.
- Repository's own store (clone at 9f933eb, checkout mode): 34 scenarios x 25 commands, 850 of 850 identical.
- `s900` (scratch copy): 34 x 25; 33 scenarios identical on the first pass.
  The one reported difference (`committed-dup`, `check`) came from my own `git reset` in that directory while the run was under way; rerun on a fresh copy, `committed-dup`, `committed-edit`, `stray`, and `dup-entry`: 100 of 100 identical.
  So 33 x 25 plus 4 x 25 identical, none different.
- `s9000` (scratch copy of `/var/tmp/lodge-bench/s9000`): clean, 19 of 19 (a trimmed list: no `spec`, `guide`, error, `--by author`, or `thread` commands, for time); 14 scenarios (stray, duplicate decision and entry, misplaced both ways, invalid YAML, non-UTF-8, CRLF edit, truncated entry, deleted decision, attachment, symlink record, record as folder, staged edit, committed duplicate) x 5 commands (`show --reasoning --provenance`, `search berth --brief`, `waiting`, `check`, `check --gate`), 75 of 75 identical.
- Spot check that the scenarios are not vacuous: on `s900` a stray file plus a copied decision gives problems for the duplicate ID, the stray path, and check 1 and 2 in both builds' output.
- Not run: anything on `s90000`; no timing comparison (the builder's table is theirs; I measured none).

## Mutation checks on the new tests (scratch copy, reverted)

- `assemble` iterating `parsed` unsorted: `test_assemble_equals_load[duplicate-id]` fails.
- `disk_tree` hashing `encode` with `errors="replace"` instead of `surrogateescape`: `test_disk_tree_blobs_hash_the_bytes_read` fails.
- Not caught, by design of the tests: a gitlink or SHA-256 repository (M3, M4).

## Practice and design

Practice: `load` is a six-line composition of `parse_file` and `assemble`; no duplicated dispatch beyond the attachment prefix test in both (`snapshot.py:60`, `:85`), which is the price of `assemble` taking a cache's mapping; comments state facts; the tests are new files under 300 lines with independently built expected snapshots.
`Listing` is unused until Task 8b, as the plan says, and `test_blob_id_matches_git` builds a `Listing` only to compare a dict, which tests the dataclass's constructor rather than `blob_id`; harmless, but the `Listing` lines could go until 8b uses it.
Design: the new leaf `core/listing.py` imports nothing from lodge; `disk_tree` change is +4 -2 lines as the plan allows; no port changes; `assemble` dispatches on the parsed value's type, so a cache that hands back a `Decision` for a path under `lodge/spec/` is reported as misplaced exactly as `load` reports it, and a cache that hands back a stale type for a path cannot make a record vanish silently (checked in the fuzz by the misplace operation).
The plan's rule "no read path changes" holds: no file outside `core/snapshot.py`, `core/listing.py`, `core/__init__.py`, `gitstore/trees.py`, `gitstore/checkout.py`, and tests changed.

## Files read

`CLAUDE.md`; reviewer standing rules; plan Task 8a, 8b, 9 interface sections; `task-8a-report.md`; `task-4-report.md` (fix-round section and header); `task-4-review.md`; d-q0tb8r and d-xc4nz9 through `lodge show --reasoning`; full diffs of a68be3c and 9f933eb; `src/lodge/core/snapshot.py`, `core/listing.py`, `gitstore/trees.py`, `gitstore/checkout.py` (the `disk_tree` region); `tests/core/test_listing.py`, `tests/core/test_same_listing.py`, `tests/core/test_identical_change.py`, `tests/gitstore/test_tree_blobs.py`; `tests/core/checks.py` and `builders.py` for the dates.

## Files not read

`lodge spec` as a whole; the rest of `gitstore/checkout.py` and `branch.py`; `app/` beyond the `Tree(` call sites; the plan's other tasks beyond the interface lines above; `scripts/bench_reads.py` beyond its header; the builder's timing table was not reproduced.
