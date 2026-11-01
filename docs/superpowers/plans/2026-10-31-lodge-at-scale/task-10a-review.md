# Review of cd92b9c (Task 9c fix round) and 6da6939 (Task 10a: stored states for `show`, `waiting`, `threads`, `thread`; keep on second sight)

Counts: 0 Blocking, 1 Important, 6 Minor.
Space answer: section "The space question" below.

## Method

Own detached worktrees `/var/tmp/lodge-review-t10a/wt` (6da6939) and `/var/tmp/lodge-review-t10a/wt-base` (cd92b9c, for before/after behaviour); `/var/tmp/lodge-build` was only used to add the worktrees.
Scratch stores are copies of `/var/tmp/lodge-bench/s900` and `s9000` (and, for the space check only, `s90000`) with their `.git/lodge` removed, so each has its own index file under the build digest of my worktree; the shared index under the repository's `.git/lodge` was never opened, and the one pytest run used `LODGE_INDEX=off` first, then the nine e2e tests that need the index were rerun without it.
Harness: `/var/tmp/lodge-review-t10a/h/` (`lib.py`, `scen.py`, `walk.py` random walk, `killtest.py`, `pinned.py`, `sz.py`, `space90.py`; `probe.py` wraps `lodge.main` to record `built`, `mark`, `keep` events without changing output).
Every comparison is stdout, stderr, and exit status of the indexed read against `LODGE_INDEX=off` on the same files at the same moment.

## Equality of a stored read with the in-memory read (the main check)

Run, not inferred:

- Random walk on s900 (two seeds, 80 steps, 233 reads) and s9000 (30 steps, 93 reads): each step is one of edit a record, break a record file, delete a record file, revert an earlier change, force a clear (the adapter's own `clear()` in a write transaction, as another process would), `git commit -a` (published ident changes), or just reads; after each step 1 to 5 reads of random commands from a set of 46 (`show` of 24 random decision and entry IDs with and without `--reasoning --provenance`, 8 codes, `A`, mixed-case duplicates, unknown ID, unknown code, several refs with a repeat and an unknown one, `waiting`, `threads`, `thread` of three threads, `thread` of an unknown thread, `show` of a thread ID).
  Result: 0 mismatches in stdout, stderr, or exit status.
  The probe (second s900 walk and the s9000 walk, 209 reads) shows the commands were really served three ways: 91 reads answered from a stored state (no snapshot built), 50 first sightings (marker only), 41 second sightings that kept, and 9 reads that built and never kept (a single unknown ref raises before the keep, see M-2); the rest of the 209 lost their probe lines to a log file my own parallel scripts shared.
  The walk includes states that are kept, evicted past four, cleared, and re-entered by revert.
- Validity interval on the real CLI (s900 copy, an uncommitted decision with no changes dated 25 s ahead): while the date is ahead it prints `fails check`, three reads of all four commands equal the oracle and the later ones are stored hits; after the date the oracle prints no `fails check`, the first read rebuilds and re-keeps (events `built keep`), the later ones hit, all equal.
- Pinned inputs (`pinned.py`): second sighting with the keep delayed 4 s (probe), the printed record's file edited meanwhile; the kept state is the old one: after reverting the file the read answers from the store (no `built`) and equals the oracle of the old content, and the edited content then builds, keeps, and hits, all equal.
- Two processes: three rounds of two concurrent first sightings, six concurrent mixed commands racing to keep one state, three more reads; 33 outputs, 0 mismatches; the index ends with exactly one complete state per key; a held write lock (`BEGIN IMMEDIATE` in another connection) during a second sighting: output and status equal the oracle, the keep fails silently after the 200 ms busy timeout, the state is absent, and the next read keeps it.
- Crash during the keep: `SIGKILL` / `SIGTERM` at random delays 0 to 2 s into the second sighting (10 trials, s9000): output equal in all, no partial state (every kept state has 1,024 buckets, 5 answers, 2,786 citer rows, no orphan rows), next two reads equal the oracle; `SIGKILL` held inside the keep's write transaction (probe sleep in `_remove`, killed after 6.5 s): WAL empty after, state absent, marker present, next read keeps and the one after hits.
  `SIGTERM` during the keep gives exit 143 after complete output: `main._exit_on_signals` turns it into `SystemExit`, which the keep boundary rightly does not catch (plan text), but note the command had already succeeded (M-5).
- Output failure: reader gone at flush, with Python's default `SIGPIPE` ignored and with `SIG_DFL` set by the parent (Python resets it): exit 120 after a traceback, no state, marker unchanged, the next two reads equal the oracle and keep then hit; `| head -c 5` (reader alive at the write) exits 0 and keeps.
- A seen read writes nothing: three hit reads leave the sqlite file's md5, size, and mtime unchanged and create no `-wal`.
- Markers: 150 consecutive single-sighting states leave 64 markers (the newest, `at` 87 to 150); a clear deletes them (walk, `seen` 0 after clears).
- Failed keep: `LODGE_INDEX` unchanged, write lock held, killed, read-only paths: output and exit status never differed (see above).
- Full suite on 6da6939: `pytest tests` 2,076 passed, 6 skipped (the run with `LODGE_INDEX=off` set showed 9 failures that are tests needing the index; rerun without it, 9 passed).
  I did not run `scripts/check.sh` because its `lodge check --gate` would open the build repository's shared index.

Verdict on equality: no defect found; the keep is complete or absent, a stored state answers only for its own key, and a failed keep changes neither output nor status.
The two behaviour changes found are in the command's flushes (M-1) and the exit status when the keep is cut by a termination signal (M-5).

## Task 9c fix round (cd92b9c)

M1 (cross-paired test): `tests/gitstore/test_index_parses.py` `scan_index` now gives each unit its own blob name, `test_scan_requires_the_requested_pair` inserts `(path of unit 2, blob of unit 3)` and a requested `(path 4, blob 5)`; asserts the result and that only requested rows are decoded (`len(decoded) == len(expected)`).
Run against the path-only mutant by the builder (report: red, 1 failed); I read the test and it fails for path-only, blob-only, and cross-product mutants by construction.
M2 (`index_parses.py:32-34`): scan only when `len(keys) >= 1000` and `len(keys) * 4 >= max(rowid)`; `max(rowid)` is one b-tree probe inside the caller's read transaction; a gap-ridden table prefers per-key, the safe side; `test_small_fraction_of_a_large_table_uses_per_key` asserts 1,001 statements.
After a clear the rowids restart (`DELETE FROM`, no `AUTOINCREMENT`), so the bound does not drift.
M3 (`index_parses.py:44-46`): `except sqlite3.Error: pass` around the cursor loop keeps the hits already decoded; `test_scan_keeps_hits_before_sql_error` fails 700 of 1,500 as expected; `assert not db.in_transaction` holds.
M4, M5: the plan line and ledger say `sha1(repr(settings).encode()).hexdigest()`; the redundant monkeypatch, the explanatory comment, and the 140 pasted lines are gone.
Findings on cd92b9c: none.


## Findings

### Important

**I-1 · Each state stores its own copy of every bucket, so at 160,801 files one state fits under the cap, not four; with Task 10b's words none fits**

`src/lodge/gitstore/index_schema.py:21-24` (`buckets(key, name, value, PRIMARY KEY(key,name))`), `src/lodge/gitstore/index_states.py` `keep_state` (`for name, raw in encoded.items(): INSERT INTO buckets`, all 1,024 for every kept state), `src/lodge/gitstore/index_space.py:96-100` (cap `1,500 bytes x files`), plan Interfaces "Buckets (d-c4w7xy) ... 1,024 per state" and invariant 2 ("a state owns only its own rows").
The plan does not say buckets are content-addressed or shared; it says each state owns its buckets, and the SCALE-1 sum rests on "four stored states of about 24 MB each (an estimate of 150 bytes of derived facts per record)" (`questions.md`).
Measured (section below): a state is 59.6 MB at 160,801 files, the parse cache alone 144 MB (plan: 86 MB), the second state differing by one record repeats 1,023 of 1,024 byte-identical buckets and adds 59,592,704 bytes (+29.3 per cent).
Failure scenario at s90000 (the builder's own ten cycles, which I reproduced in miniature on s9000): edit, read, read, read: the second state is kept at 263 MB, over the 241 MB cap by 22 MB; the next writer of any kind (a first sighting's marker, `add`, a parse-only keep) clears the whole index, parse cache and kept states included; five clears in ten cycles, every clearing cycle's second read ends in 24.4 to 24.8 s against 15.2 s (M-3 is part of that), and the states that make a revert or a commit cheap (the reason for four) are gone.
When Task 10b adds the word table (52.8 MB in `probes/fts.py`), parse cache plus words are 197 MB and one state makes 257 MB: no state ever survives the next write.
`KEPT_STATES = 4` is therefore a constant the build cannot reach at production size, and no test says so: `test_first_sightings_alone_stay_under_the_cap` and the cap tests run at the 16 MiB floor, where a state is a few hundred kilobytes.
Fix, in this order of cost:
(a) the coordinator takes it to the author as a failed premise of SCALE-1 (d-4pbeax) before Task 10b is built: her 240 MB assumed 86 + 52.8 + 4 x 24; the measured parts are 144 + 52.8 + 4 x 60 = 437 MB without sharing, or, with the layout below, 144 + 52.8 + 60 + 3 x 8 = 281 MB, still over 240 MB;
(b) content-address the buckets: `blobs(h BLOB PRIMARY KEY, value) WITHOUT ROWID` with `h` a 12-byte sha1 prefix, `state_buckets(key, name, h) WITHOUT ROWID`, `keep_state` does `INSERT OR IGNORE` into `blobs` and one pointer row per name, eviction deletes the pointers and then `DELETE FROM blobs WHERE h NOT IN (SELECT h FROM state_buckets)`; `rows()` reads through one join;
(c) the other per-state tables repeat the 40-character key in every row and again in the autoindex: `citers` is 3.65 MB per state at s90000 for 122 KB of values (about 55,000 rows), `facts` 3.33 MB per ident (never evicted until a clear), the `states` row 1.21 MB; storing a state's citers in one value, or sharing facts by content, brings an extra state to about 0.2 MB;
(d) add a bench assertion that N states of the s9000 store (16,124 files, cap 24.2 MB) fit under `INDEX_BYTES_PER_FILE x files` (today 2 states are 27.8 MB, the cap 24.2 MB).

### Minor

**M-1 · `show`, `waiting`, `threads`, `thread` exit 1 with a traceback when stdout (or, for `show`, stderr) is closed, where cd92b9c exited 0**

`src/lodge/cli/commands.py:68-72` (`sys.stdout.flush(); sys.stderr.flush()` in `Show`), `:89-91` (`Waiting`), `:95-97` (`Threads`, `ThreadCommand`).
Scenario: `lodge show d-00gyfz >&-` or `lodge show d-00gyfz 2>&-`: `sys.stdout`/`sys.stderr` is `None`, `.flush()` raises `AttributeError`; run on both worktrees: cd92b9c exit 0, 6da6939 exit 1 with a traceback, with or without the index (`LODGE_INDEX=off` too, because the flush is unconditional).
`show` with stderr closed fails even when it prints nothing to stderr.
The plan's "closed" test (`tests/app/test_indexed_keep.py` `test_output_failure_keeps_nothing[closed]`) closes a `StringIO`, which raises `ValueError`; it never closes the descriptor.
A broken pipe now prints a full traceback from `main` rather than "Exception ignored", same exit 120.
Fix: flush through a helper that skips `None` and returns whether the flush succeeded (`False` skips the keep, an `OSError` on a real closed pipe still ends the command as today), and add a subprocess test with `>&-` and `2>&-`.

**M-2 · An unknown ID or code rebuilds the whole state every time and never keeps**

`src/lodge/app/index_lookups.py:209-219` (`resolve` raises `Miss` for an ID not in its bucket and for a code not in `codes`), `src/lodge/app/indexed.py:97` (falls through to `_built`), `src/lodge/cli/commands.py:62` (a single unknown ref raises before `after_output`).
Scenario: a typo `show d-zzzzzz`, `show nosuchcode`, `thread q-nonexx` with a kept state present costs a full read (9.7 s at s90000 in the report's first-read column) on every attempt; the probe showed 9 of 209 reads in my walk doing this.
The stored state can prove the absence: all 1,024 buckets exist (empty ones included, `promised` checks it), `codes` is complete, and the `NotFound` text needs only `state.read.unrecorded`, which `StoredState` keeps.
Fix: answer `not_found` from the store when the bucket (or `codes`) is present and lacks the name, with the text of `app/state.py:164-170`; add the cases to `test_outputs_print_as_in_memory`.

**M-3 · A clear in a marker or parse-only write keeps none of the parse units the read already holds, so the next read is cold**

`src/lodge/app/indexed.py:101` (`mark_seen(key, {k: state.parses[k] for k in misses}, ...)`), `src/lodge/gitstore/index_states.py` `mark_seen`, `src/lodge/gitstore/index_db.py` `keep_parses`; contrast `keep_state`, which re-reads `meta.epoch` after `prepare_keep` and writes every unit when it moved.
Scenario, run on a copy of s9000 with two kept states over the 24.2 MB cap: edit, first read; `prepare_keep` clears inside `mark_seen`, which then inserts only the one missed unit: index after the read holds 1 parse unit and no state (`meta.epoch 1 to 2`, `parses 1`); the second read reparses all 16,124 files and takes 2.40 s against 1.41 s for an ordinary second read (+70 per cent; at s90000 +9.6 s, the 24.8 s above).
The plan wants "a read that writes a whole working set after a clear" not to be cleared away (Interfaces, the cap paragraph); this read holds the whole working set in `state.parses` and drops it.
Fix: pass every unit the read used and its epoch to `mark_seen` and `keep_parses` and write all of them when `meta.epoch` differs, as `keep_state` does; test: a marker write that clears leaves every unit of its tree in the index.
Becomes rare once I-1 is fixed.

**M-4 · The cap's name and the cap's reach into tests**

`src/lodge/gitstore/index_space.py:98` (`INDEX_FILE_CAP` is a local variable, recomputed in each call; nothing else can name it), tests use `MIN_FILE_CAP + 700000` as "cap plus one working set" (`tests/gitstore/test_index_states.py:138,155`).
Scenario: Task 10b, 10c, and 12 need the cap to size tests and to report states per cap; each will copy the formula.
Fix: a function `index_file_cap(files: int) -> int` beside `INDEX_BYTES_PER_FILE`, used by `prepare_keep` and the tests.

**M-5 · A termination signal during the keep turns a successful read into exit 128 + signal**

`src/lodge/main.py:100-112` (`SIGTERM` and `SIGHUP` become `SystemExit`), `src/lodge/app/indexed.py:123` (the boundary rightly lets `SystemExit` through).
Scenario: `timeout 10 lodge show X` on s90000: the output is complete at 9.8 s, the keep runs 5 s more, `timeout` ends it with exit 124 and the caller sees a failure of a read that succeeded; run in miniature on s9000: `SIGTERM` 0 to 2 s into the keep gave exit 143 with the full, equal output (`killtest.py` trials 1, 5, 7), the index intact.
The plan accepts `SystemExit` passing; the cost is that every second read at scale is a 5 s window where a supervisor's kill changes the status.
Fix (optional): in the deferred keep, on `SystemExit` rethrow after the output but return the status the command computed, or document the window in `lodge guide`; no code change is needed for correctness.

**M-6 · Dead branch with the wrong handling, and a second snapshot assembler**

`src/lodge/app/indexed.py:41-43` (`if path not in texts: raise Miss`): `gitstore/listing.py:_texts` returns every requested path or raises `LodgeError`, so the branch cannot run; if it ever did, `Miss` leaves `_run` uncaught (the `try` covers only the stored lookups) and the command dies with a traceback.
`_built` (`indexed.py:29-71`) re-implements `snapshot_of`, `read_state`, and `read_checked` (`app/state.py:49-130`); the differential walk found no difference, but `snapshot_of` filters `if path in tree.files` and writes through `keep_parses` while `_built` does neither, so a later change to one is invisible to the other except through the differential tests.
Fix: delete the dead branch; leave a test that fails when the two assemblers print differently on the 500-record store (it exists: `test_outputs_print_as_in_memory`; the fix is only to name this coupling in `indexed.py`'s docstring).

## The space question

Question: are buckets content-addressed and shared between consecutive states as the plan says, or does each state store its own copy?
Answer: each state stores its own copy; the plan does not say they are shared (it says "a state owns only its own rows", Interfaces "Buckets" and invariant 2), and `buckets` is keyed by `(state key, name)`.
Measured on copies of `s9000` (16,124 files, `space` scripts `sz.py`; used bytes = (pages - free pages) x page size):

| | s9000 (16,124 files) | s90000 (160,801 files, `space90.py`) |
|---|---:|---:|
| parse cache only (first read) | not read separately | 144,044,032 |
| after the first state is kept | 21,090,304 | 203,591,680 |
| after the second state, one record differing | 27,779,072 | 263,184,384 |
| the second state's cost | 6,684,672 (31.7 per cent) | 59,592,704 (29.3 per cent) |
| buckets byte-identical between the two states | 1,022 of 1,024 | 1,023 of 1,024 |
| bucket values per state (JSON bytes) | 5,041,088 | 50,440,542 |

Of the second state's cost at s90000: buckets 51.3 MB of pages, citers 3.6 MB (rows repeat the 40-character key, plus their autoindex), facts 3.3 MB, the state row 1.2 MB.
The plan's estimate was 24 MB a state; the measured cost is 59.6 MB, 2.5 times as much, and the parse cache 144 MB against 86 MB.
Under the 241.2 MB cap one state fits (203.6 MB), the second takes it to 263.2 MB, and the next write clears; this reproduces the report (five clears in ten cycles) and also holds at s9000, where the cap is 24.2 MB and two states are 27.8 MB.

What a shared layout costs per extra state, prototyped by moving the measured index's buckets into `blobs(h) + state_buckets(key, name, h)` (`WITHOUT ROWID`, 12-byte sha1 prefix) and vacuuming:
- s9000: the two states together 22.585 MB instead of 27.517 MB; a third, fourth, and fifth state differing in two buckets each add 37, 29, and 41 KB.
- s90000: the two states together 210.25 MB instead of 260.61 MB (50.36 MB saved); the third, fourth, and fifth add 118,784, 126,976, and 118,784 bytes, that is the 1,024 pointer rows plus two changed buckets, against 50.4 MB.
- What remains per extra state with only the buckets shared: citers 3.65 MB, facts 3.33 MB per new ident, the state row 1.21 MB, about 8.2 MB in all; sharing or packing those as well brings an extra state to about 0.2 MB.
Four states then cost 144 + 60 + 3 x 8 = 228 MB (without words) rather than 144 + 4 x 60 = 384 MB; with Task 10b's words, 281 MB against a 241 MB cap: the cap constant needs the author in either case (I-1 (a)).
A fix costs: one schema change (schema number rises), about 30 lines in `keep_state`, `rows`, `all_rows`, and the eviction, a hash of 1,024 values already encoded (the 1.5 s bucket encoding in the report stays), and a smaller `keep_state` transaction (only changed buckets are inserted); the per-state `Row` building (1.05 s) and citers (2.37 s) stay.

## Passes

Correctness: above (equality, the keep's atomicity, keys, epochs, markers, signals); the plan's test list is complete (all 34 named tests exist) and the suite passes; no Blocking or Important finding on behaviour, one Important on the space the plan promised.
Practice: M-4 and M-6; comments state facts (the one in `indexed.py:51` does); the `ContextManager` suppression is explained in the report; modules stay under 300 lines.
Design: I-1 (a plan assumption against the code, and a plan rule, "four states", no test enforces), M-2 and M-3 (the cache can prove more than it does), the `Lodge` object carrying a one-slot pending keep (`app/lodge.py:37-42`) is fine for a CLI and would need a queue if a caller made two reads before `after_output`; `show` of one ref goes through `show_many` in `Lodge.show` and returns a `Shown` without `threads`, `confirmable`, `rests_on`, `supports` (viewer-only fields, the viewer passes `read_model=False`), correct today, and a trap for a caller that reads those fields from `Lodge.show`.

## Files read and not read

Read: `.claude/agents/reviewer.md`, `CLAUDE.md`, the plan's Task 10a section and Task 9c, the ledger (parts), `questions.md`, `task-10a-report.md`, `task-9c-review.md`, decisions d-n65rhr, d-e3stjn, d-q0tb8r, d-4j98ph, d-c4w7xy, d-4pbeax; the diffs of cd92b9c and 6da6939 for `src/`; in full `app/indexed.py`, `app/index_lookups.py`, `app/read_model.py`, `app/index_types.py`, `gitstore/index_states.py`, `index_schema.py`, `index_transactions.py`, `index_space.py`, `cli/commands.py` (1-140), `main.py` (tail), `gitstore/listing.py`; parts of `app/state.py`, `app/reads.py`, `app/lodge.py`, `gitstore/index_db.py`, `gitstore/identity.py`, `core/search.py`, `core/codes.py`, `core/views.py`, `cli/threads.py`; tests `app/test_read_model.py`, `app/indexed_support.py`, `app/test_indexed_keep.py`, and the names of every test in the plan's list.
Not read: the bodies of `tests/app/test_indexed_reads.py`, `tests/gitstore/test_index_states.py`, `test_index_concurrency.py`, `test_index_keep_processes.py`, `test_indexed_cli_contract.py`, `tests/app/fake_index.py`; `gitstore/index_parses.py` beyond the diff; the viewer; Task 8c identity code beyond `listing.py` and the head of `identity.py`.
Not done: the report's own s90000 replay timings were not re-run (only the space sequence was); `scripts/check.sh` (its gate step opens the shared index); the SIGPIPE-at-default-disposition case as a signal (Python resets it at startup, so the process cannot be made to die of signal 13; the closed pipe gives exit 120 with no keep).
