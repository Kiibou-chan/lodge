# Review of 2e779c0 (Task 10a fix round) and 5a9aac5 (Task 10c)

Counts: 2 Blocking, 2 Important, 4 Minor.

## Method

Own detached worktree `/var/tmp/lodge-review-t10c/wt` (5a9aac5) with its own `.venv`; `/var/tmp/lodge-build` was used only to add the worktree.
Scratch stores are copies of `/var/tmp/lodge-bench/s900` and `s9000` with `.git/lodge` removed, so each has its own index file; the repository's shared index was never opened and `scripts/check.sh` was not run.
Harness: `/var/tmp/lodge-review-t10c/h/` (`lib.py`, `walk.py` random walk, `blobs.py` bucket-blob stress).
Every comparison is stdout, stderr, and exit status of the indexed run against `LODGE_INDEX=off` on the same files.

## Findings

### Blocking

**B-1 · A stored state answers "no record named X" for a record whose code starts with `d-` or `s-`, where the in-memory read prints the record**

`src/lodge/app/index_lookups.py:44-48` (`resolve`: any lowercased ref starting `d-` or `s-` is treated as an ID and, since the fix round (M-2), an ID missing from its intact bucket raises `NotFound` instead of `Miss`).
`core.resolve` (`src/lodge/core/search.py:24-33`) tries the ID first and then the code, and the code grammar (`src/lodge/core/fields.py:11`, `[A-Za-z0-9][A-Za-z0-9._-]*`) allows `d-fast` or `S-1`; no check forbids it.
Failure scenario, run on a copy of s900: set `code: d-fast` on a decision and commit (`lodge check` says `ok`); `lodge show d-fast` prints the record on the first and second read (in memory, marker, then keep), and from the third read, once the state is stored, prints `lodge: no record named d-fast`; `LODGE_INDEX=off` prints the record.
Before the fix round the miss fell back to memory, so this is new in 2e779c0.
Fix: in `resolve`, when the lowercased ref is not an ID in its bucket, fall through to `self.state.codes.get(wanted)` before raising `NotFound` (ID first, then code, as `core.resolve` does); add `test_outputs_print_as_in_memory` cases for codes `d-x` and `S-1`, and the same for the ambiguity message.

**B-2 · Every read that goes through `snapshot_of` now takes the writer lock and, over the cap, clears the whole index, even when it found every parse in the cache**

`src/lodge/app/state.py:81` (`index.keep_parses(kept, files=..., used=memo, epoch=epoch)` is called unconditionally) with `src/lodge/gitstore/index_db.py:145` (`if not parsed and used is None: return`; `used` is now never `None` there, so the early return for "nothing missed" is gone) and `src/lodge/gitstore/index_space.py:105-110` (`prepare_keep` clears when over the cap and a state was kept or `written >= files`).
Affected commands: `spec`, `check`, `check --gate`, `draft`, `add`, thread writes, and both snapshots of every changed indexed read.
Failure scenario, run on a copy of s9000 (words present, so one state is over the 24.2 MB cap, as the report says it is at every measured size): `show A` three times keeps a state (`meta` epoch 3, kept 1, states 1, facts 2, seen 1); the fourth is a hit and changes nothing; then `lodge spec` with no edit at all leaves epoch 4, kept 0, states 0, facts 0, seen 0.
A trace of `lodge spec` and `lodge check --gate` on a warm s900 shows `keep_parses misses=0 used=1603` followed by `BEGIN IMMEDIATE` / `COMMIT`, once per snapshot.
So the repository's own gate, every `check`, and every `add` discard the kept states, the facts, and the markers when the index is over the cap, and the clear then rewrites the whole parse cache (`used`) in the same transaction (about 144 MB at s90000).
Even under the cap each such read takes the single writer lock for no reason, so a deferred keep or a marker of a concurrent read can lose its `BEGIN IMMEDIATE` to the 200 ms busy timeout and fail silently.
Before 2e779c0 `keep_parses({})` returned at once.
Fix: return early when `parsed` is empty (the hits need no write: a keep or marker writes its own working set, and a clear between the lookup and an empty write loses nothing), and keep `used` and `epoch` for the case with misses; add a test that `spec`/`check` on a warm over-cap index with a kept state starts no write transaction and leaves `epoch`, `states`, and `facts` unchanged (recorded by a connection wrapper, as `test_seen_read_writes_nothing` does).

### Important

**I-1 · No test pins the one input the stored facts feed to the check: the published statuses**

`src/lodge/app/read_model.py:90-103` (`change_facts_of`), `tests/app/test_published_facts.py:80-102` (`test_published_facts_equal_full`).
The four cases (duplicate code, hand-edited, out-of-order, cycle) differ only in problems, and published problems cannot change a read (see I-2); published statuses decide check 4 and check 6 (`core/check_change.py` `check_entries` and `_links_to_dead`).
Failure scenario, run: replacing the line `{ident: allowed[status] ...}` by `dict(state.derived.status)` (the current state's statuses passed as the published ones) leaves all 14 tests of `test_published_facts.py` green.
I also confirmed the path matters with the CLI: a committed decision replaces D1, the working tree deletes the replacement and adds a decision narrowing D1 and nothing else; with correct facts the indexed `show` equals `LODGE_INDEX=off` (check 6 fires from the published status), with the published status row set to all `current` it differs.
Fix: add that case (published `replaced` or `retired` against current `current`, plus a new decision narrowing, confirming, or editing it) to `test_published_facts_equal_full`, so that swapped or stale statuses fail.

**I-2 · Facts written for a dirty working-tree ident can never be read again, and the stored `problems` never change a read; together they are most of the 3.33 MB per changed read**

`src/lodge/app/read_model.py:106-115` (`build_facts` stores `facts[current]` for every build and the published facts with `problems`), `src/lodge/gitstore/identity.py:200-203` (`_overlay`: a dirty ident is `sha1(base.ident + overlay)`), `src/lodge/gitstore/identity.py:63-71` (a published ident is a git tree ID), `src/lodge/app/indexed.py:72` (the only lookup, by `published.ident`).
A facts row is read only through `published.ident`, which is a tree ID; a dirty current ident is a different hash of a different input, so it never equals a published ident (a clean checkout's ident is the tree ID and does match, so only overlay idents are dead).
The report's table (3,329,571 value bytes per changed read "even when statuses are unchanged") is therefore mostly rows nobody will read, and 0.144 s of marker time at s90000 builds and encodes the dead one.
Second, `ChangeFacts.published_problems` only splits `after_problems` into problems and notes, and `finish_checked` (`app/state.py:129-166`) re-adds every standing problem and drops the notes, so the result is the same for any value: with every stored problem list emptied, reads equalled the oracle (run on s900, `waiting`, `show`).
So `check_state` on the published snapshot (0.448 s at s90000 on a miss) is not needed by any read either; only the gate needs it, and it computes its own.
Fix: store the current ident's facts only when the build's current ident is a committed tree (no overlay), or not at all, and store only the status map; skip the published `check_state` on the indexed path (pass an empty `published_problems`) and say in the plan that the gate keeps the full computation.
Cost if not fixed: with the cap unresolved (DISK-1), every changed read adds 3.3 MB that no read will use, at s90000 about 8 per cent of the cap each.

### Minor

**M-1 · A damaged shared bucket blob is never repaired, and every state sharing it falls back to memory until a clear**

`src/lodge/gitstore/index_states.py:218` (`INSERT OR IGNORE INTO bucket_blobs`).
Scenario, run: set one blob's value to `{garbage`, re-keep the same state and keep another one: `state()` still returns both states (the count join only counts rows), `rows()` returns `None` for both, and the blob stays damaged.
Before the fix round a re-keep replaced the buckets whole.
Reads stay correct (memory fallback), but the stored states are useless and look intact.
Fix: when `INSERT OR IGNORE` reports `rowcount == 0`, compare `length(value)` with the new blob's length and replace on a difference (cheap, no read of the 50 MB), or delete a blob that fails to decode.

**M-2 · `StoredState.threads` has a default of `()`, which turns an old or hand-made row into "no thread named X"**

`src/lodge/app/index_types.py:43`.
A state row without the field decodes with no threads and `indexed.py` `thread` then answers not-found from the store for a thread that exists.
The schema bump covers real files; the default is a wrong answer where a missing field would be a decode error and a memory fallback.
Fix: no default (the plan's interface has none).

**M-3 · No test says the gate, `add`, and `check` take nothing from the facts (d-q0tb8r)**

`tests/app/test_published_facts.py` has no such case; the rule holds today only because `_built` is reached from `_run` alone (`grep '\.facts(' src` finds one call, `app/indexed.py:72`).
I poisoned every facts row (all statuses retired, no problems) and `check`, `check --gate`, and `spec` still equalled the oracle, so the code is right; a later change wiring `index.facts` into `read_checked` would pass the suite.
Fix: one test with a poisoned `MemoryIndex.fact_values` and a gate, `add`, and `check` that compare with an empty index.

**M-4 · `Checked.derived` is now optional, which lets a half-built published state reach code that expects it**

`src/lodge/app/state.py:39`, `src/lodge/app/read_model.py:113` (`assert before.derived is not None`), `src/lodge/app/reads.py:154` (`before=cached.derived`, which would silently recompute for `None`).
Today the `None` form exists only inside indexed reads, which never reach `reads.check`, so there is no failing input.
Fix: a separate type for the facts-backed published state, or a one-line comment on `Checked` saying which constructor may leave `derived` empty.

## Answers to the brief

**Shared bucket blobs deleted only when unreferenced, same transaction.**
`index_states.py:213-226`: eviction and the re-keep's `_remove` run first, the new pointers and `INSERT OR IGNORE` blobs follow, then one `DELETE ... WHERE hash NOT IN (SELECT hash FROM buckets)`, all inside the `BEGIN IMMEDIATE` of `keep_state`, with `prepare_keep`'s clear before them.
I tried to make a kept state point to a missing or wrong blob with `h/blobs.py`: two connections, 8 seeds of 40 random operations (keeps of 0 to 12 rows with random statuses over 8 keys, re-keeps of the same key with other rows, clears, evictions past four, and a reader inside `reading()` whose snapshot another connection keeps over): after every step no pointer lacked a blob, no blob lacked a pointer, every blob's key equalled the sha1 of its value, every kept state's `all_rows` equalled what was kept, and the reader's snapshot never changed.
`state()` counts pointers joined to blobs, so a missing blob makes a state incomplete rather than partial.
Parallel processes: 14 rounds of 14 concurrent reads on a copy of s900 (each round a new state): 0 mismatches against the oracle, no orphan or missing blob.
The only way found to a wrong blob is tampering with the file (M-1).

**Published facts keyed so they cannot apply to another published state.**
The key is `published.ident`, a git tree ID of `<published>:lodge/` (or the empty tree), and `derive` and `check_state` take neither settings nor the clock (`core/derive.py`, `core/check_state.py`), so the facts depend on the tree alone; settings and `now` enter only in `check_change`, which still runs in full.
Another build has another index file (`build_digest` hashes every `.py` and `.md` of the package and the library versions).
A rewritten branch or a moved base gives another tree ID (branch mode with three forced pushes and two resets: 0 mismatches).
`h/walk.py` compared the stored facts of the current and published idents with a fresh `derive` and `check_state` on the oracle's trees after each step: 90 pairs on s900, all `ok`.
I found no way to apply a facts row to another state.

**Every read prints as the in-memory read.**
Random walk with edit, break a file, delete a file, revert, duplicate codes, settings change (`[length] title_chars`), commit, amend, branch and feature commits, fast-forward of main, moving main back one commit, forced clear, and 1 to 4 reads of about 20 commands per step (`show` of IDs with and without `--reasoning --provenance`, codes, `A`, unknown ID and code, mixed refs, `waiting`, `threads`, unknown thread, `check`, `check --gate`, `spec`, two searches), each 1 to 3 times: s900, three seeds, about 1,000 reads; s9000, 173 reads; branch mode with forced pushes, about 400 reads; 14 rounds of concurrent reads.
0 mismatches in stdout, stderr, or exit status, except the two defects above, which the walk did not generate (B-1 needs a code like `d-fast`, B-2 shows in the index, not the output).
About a minute of the walks ran while I had a mutation in the worktree (for I-1); it changed only the facts-backed path and moved the index to another build file, and no mismatch appeared.

**The gate takes nothing from the facts (d-q0tb8r).**
`index.facts` is called once (`app/indexed.py:72`), from `_built`, which only `_run` reaches; `reads.check`, `writes`, and `threads.write` use `read_checked`/`snapshot_of` with `w.checked` unset.
Poisoned facts did not change `check --gate`, `check`, or `spec`.
The gate still reads the parse cache, as d-q0tb8r allows, keyed by the bytes read.

**Space figures.**
Report: one state 251,326,464 bytes at s90000 against the 241,201,500 cap (a state with the word table is already over; no state fits), +8.39 MB per extra state, 59.6 MB before sharing.
Consistent with the 10a review's split of the second state (citers 3.65 MB, facts 3.33 MB per ident, state row 1.21 MB: 8.19 MB) and with my run on s9000 (facts value 0.33 MB per row at 16,124 files, 1,024 distinct blobs for one state).
With four states the shared layout needs about 251 + 3 x 8.4 = 276 MB, still 14 per cent over the cap, so `KEPT_STATES = 4` remains unreachable at s90000 until the author rules on DISK-1, and the 10-cycle clears the report lists are expected.
Which clears are caused by the cap and which by B-2 cannot be told from the report's walk, because it ran `check`-free; with B-2 fixed the count of clears in a mixed session will be lower.

**Can the per-ident facts (3.33 MB each, even with unchanged statuses) be shared without risk?**
Yes, with less risk than the buckets.
Facts are immutable and never evicted, so a content-addressed table (`fact_blobs(hash, value)`, `facts(ident, hash)`, `INSERT OR IGNORE` of the blob) needs no reference count and no collection, only the clear that already empties every table; an extra ident whose statuses did not change then costs a pointer row.
Verify the hash on read (3.3 MB of sha1 is a few milliseconds) to avoid M-1's permanent damage, and keep the completeness check in `indexed.py:73-75`.
Better first, I-2: do not write the dead current-ident facts, and drop `problems`, which leaves one status map per published ident, written once.
Partial sharing of the status map between neighbouring idents (a status changes for a handful of records per commit) would need a delta format and is not worth it.

## Passes

Correctness: above; the plan's Task 10c tests exist and pass (14 cases; `uv run pytest tests/app/test_published_facts.py`: 14 passed), but see I-1.
Practice: comments state facts; `_flushed` and `index_file_cap` are small and used; vulture and size rules are green per the report (not rerun).
Design: the facts keying matches the plan's "keyed by the published ident"; the plan's "every build stores the current snapshot's own facts" is the rule I-2 argues against, so that one is for the coordinator.

## Files read and not read

Read: `.claude/agents/reviewer.md`, `CLAUDE.md`, the plan's Task 10a (amended parts), 10c, `task-10a-review.md`, `task-10c-report.md` (implementation, gate, phases, replay, result), d-n65rhr, d-q0tb8r, d-e3stjn; the diffs of 2e779c0 and 5a9aac5 for `src/`; in full `gitstore/index_states.py`, `index_schema.py`, `index_space.py`, `index_transactions.py`, `app/state.py`, `app/read_model.py`, `app/index_lookups.py` (lines 1-175), `app/indexed.py`, `core/check_change.py`, `gitstore/identity.py`, `gitstore/listing.py`, `tests/app/test_published_facts.py`; parts of `gitstore/index_db.py`, `cli/commands.py` diff, `app/reads.py`, `app/threads.py`.
Not read: the bodies of `tests/gitstore/test_index_shared_buckets.py` beyond line 80, `test_index_closed_streams.py`, `tests/app/fake_index.py` beyond `facts`, the viewer, `index_parses.py`, `index_words.py`.
Not done: `scripts/check.sh` and the full pytest suite (they open the build repository's index or take minutes); the s90000 timings were not re-run (only the report's figures are cited); no signal or kill tests (the 10a review did them and the keep code is unchanged).
