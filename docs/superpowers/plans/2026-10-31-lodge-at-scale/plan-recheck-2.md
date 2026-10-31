# Plan recheck 2: lodge at scale, fix round 2

Rechecker angle: the fix round's findings, the index's invariants (d-6hb3yd, d-aej8rs) against every task that writes, evicts, or reads the index, and new problems.
Plan at `e483122` on `read-speed` (fix round 2 is `git diff 8d039d0 3006308`; `e483122` adds d-hxmdkz for broad searches and moves no line numbers).
Line numbers are of `docs/superpowers/plans/2026-10-31-lodge-at-scale.md` at `e483122`.
Decisions read through `lodge show --reasoning` are saved in `/var/tmp/lodge-recheck2/decisions.txt`; probes are in `/var/tmp/lodge-recheck2/`.

Status: complete.

## Status of the rechecks' findings

### Correctness and design recheck (`plan-recheck-opus.md`)

| Finding | Status | Plan lines | Note |
|---|---|---|---|
| N1, the fuzz test's two-way clause | Fixed | 179, 185, 192 | Verified: the guard as now worded (PLAIN not ending in `:`, no `\uD800` to `\uDFFF` escapes), run through the earlier recheck's generator at seeds 1 to 3 (180,000 headers, 95,905 admitted), gave 0 headers where C succeeds and Python fails, 0 value differences, and 0 where C fails and Python succeeds (`/var/tmp/lodge-recheck2/gfuzz.txt`); the plan's one-way assertion holds, and so does the stronger one. |
| N2, idents agree exactly when trees agree | Fixed | 51, 385, 393, 397 | The property and the "agrees" preamble are one-way; the canonical cases stay as named tests (394). |
| N3, evicted words never come back | Fixed in the contract, with a residual | 28, 30, 543, 550, 552 | A parse unit brought back as a parse-cache miss now brings its words; one brought back as a hit in the transaction that evicts its last other referrer is V1. |
| N4, no citer lookup in Task 10a | Fixed | 489, 498, 506, 508, 517 | A family root that is no record's code has no citer row; V5. |
| N5, the `crlf` attribute | Fixed | 52, 387, 396 | |
| N6, published facts evicted | Fixed in the wording | 30, 512, 570 | Whether the new state's own published ident counts at its eviction is V1. |
| N7, `synchronous=NORMAL` | Fixed | 58, 432 | |
| N8, function-word queries | Fixed | 295, 296, 305 | |
| N9, pruning and journals | Fixed | 433, 447 | |

### Feasibility and performance recheck (`plan-recheck-codex.md`)

| Finding | Status | Plan lines | Note |
|---|---|---|---|
| F1, identity depends on representation | Fixed | 51, 385, 394, 507, 517 | Narrowed to the one-way contract (d-c0q20c), with the build's shortcut comparing listings and the three named cases tested. |
| F3, attributes only in git's index | Fixed | 52, 386, 387, 396 | `ls-files ... -- lodge .gitattributes` names the root file and every one under `lodge/`, the only ancestors a record path has. |
| F5, the viewer still recurses | Fixed | 126, 153, 158 | |
| F6, broad searches | Fixed by the coordinator's ruling | 5, 67, 76, 604 | d-hxmdkz (`e483122`): their own stop at 1.0 s warm. |
| R1, states searchable before their words | Fixed in the contract, with a residual | 28, 29, 538 to 543, 551 | `keep_words` is gone; the residual is V1. |
| R2, no bounded path for citers | Fixed | 114, 115, 498, 508, 517, 523 | |
| R3, `git var` with two variables | Fixed | 52, 387, 396 | |
| R4, a file replaced by a folder | Fixed | 384, 394, 397 | |
| R5, empty skeleton bodies | Fixed | 21 | |

## New findings

### V1. Important. Task 10a: the eviction in `keep_state` may drop a parse unit, or facts, that only the evicted state and the state being kept reference

Handle: line 30 (invariant 3: eviction removes "the parse units no kept state references"); line 29 (invariant 2: the state's row last in the transaction); lines 500 to 504 (`keep_state(..., parses)` writes "the parse units its rows reference that are missing", and the eviction, "and last the state's row"); line 442 (a build takes cached parses and parses only the misses); line 518 (`test_eviction_drops_only_what_the_state_owns`: survival through another *kept* state only); line 552 (the property test's revert is random in time).
The plan does not say whether the state being kept counts as a kept state when its own transaction evicts, nor when "missing" is decided.
Two readings that every named test admits break invariant 2:
1. Single process. S0 holds record `r` at blob `b1`; S1 to S3 hold `r` at `b2`; the edit is reverted, so the build of S4 finds `(r, b1)` as a parse-cache hit and passes only its misses to `keep_state`. Inside the transaction the eviction of S0 computes "referenced by a kept state" over the states that have their row, and S4's row is written last, so `(r, b1)` and its words row go. S4 is published naming a parse unit that does not exist.
2. Two processes. Process A builds S' and finds `(r, b1)` as a hit; process B keeps another state, whose eviction drops `(r, b1)` because S' is not yet kept; A then calls `keep_state` with the misses it found before B's commit.
In both, `lodge search <a word only r's b1 text holds>` omits `r`: the FTS words row is gone, so `r` is never a candidate, and invariant 5 cannot see it, since a search has no promise to check a missing candidate against (line 544); `show r` falls back, so only search is wrong.
The same ordering decides N6: the facts of S4's published ident are dropped in the transaction that wrote them when only S0 named it (line 570's test may run its `keep_state` with no eviction).
None of the fault-injection tests reaches either case: `test_keep_state_interrupted_at_each_statement` interrupts, `test_eviction_drops_only_what_the_state_owns` shares units between existing states, and the property test (line 552) reverts to a random earlier step, so it hits the evicted state's step only by chance.
Not run: no index code exists; this is the plan's text against itself.
Fix: say that `keep_state` takes every parse unit of the state (the snapshot holds them all), and that inside its write transaction it first evicts, counting the state being kept as kept, then writes each referenced parse unit that is absent at that moment, then the rows, answers, citers, facts, and last the state's row.
Add to `test_index_states.py` `test_revert_to_the_evicted_states_contents` (the sequence of reading 1, then a search for a word only `b1` holds lists `r`, and the facts of S4's published ident survive), and to `test_index_concurrency.py` `test_unit_evicted_between_build_and_keep` (reading 2 with two connections: after A's `keep_state`, every key of its rows has its parse and words rows).

### V2. Important. Tasks 10a and 10b: invariant 3 names what eviction drops but not how it finds it, and the obvious ways cost 0.5 to 0.8 s on the changed-record read, which the cost table does not hold

Handle: line 30 and line 512 (eviction drops "the parse units no kept state references", and, line 30, the gate's and `add`'s unreferenced units at the next eviction); line 470 (a `Row` carries its `key`, inside buckets that are `marshal` blobs, line 512); line 543 (the FTS table `(key, title, statement)`, one row per parse unit, dropped with it); line 77 (the changed read at about 3 s, its writing 0.2 s; the feasibility recheck already sums the estimates to 3.31 s); line 581 (the 3 s stop).
Every changed read keeps a new state and, once four are kept, evicts one, so this cost falls on every changed read in steady use.
Finding the units no kept state references needs either the keys of every kept state or a reference structure; the plan specifies neither.
Measured with `/var/tmp/lodge-recheck2/evict_cost.py 160000` (synthetic 2,900-byte parse values, as 476 MB over 160,000 in `plan-report.md`; four kept states; Python 3.14.7, SQLite 3.53.4, native ext4; a probe of the mechanisms, not a timing of lodge, and not the plan's like-for-like interpreter):
- decoding every bucket of four kept states to their keys: 0.311 s;
- the alternative, a references table: writing the new state's 160,000 references 0.424 s, then dropping the oldest state's references and every parse unit with none left 0.370 s;
- checking which of the new state's 160,000 keys are absent (V1's fix needs it inside the transaction): 0.228 s.
The words rows add a second cost: `/var/tmp/lodge-recheck2/fts_delete.py` deletes from a 160,000-row FTS5 table at 0.235 s for ten rows by an unindexed `key` (each a full scan) against 0.002 s by rowid; an eviction drops one unit per record that differs between the evicted state and the kept ones, so hundreds after a pull or a branch switch touching hundreds of records.
Failure scenario: Task 10a's builder writes the plainest correct eviction, the changed read lands near 4 s, and the stop of Task 12 fires on a cost that a different mechanism avoids, after Task 11.
Fix: specify the mechanism and budget it.
One that holds invariant 3 cheaply: the candidates for dropping are the evicted state's keys (decode its own 1,024 buckets, about a quarter of the 0.311 s) that the new state's rows do not name (already in memory), each checked against the remaining kept states' rows for that record's ID (one bucket per state per candidate); the units no state ever referenced (the gate's, `add`'s, a published snapshot's) carry a flag and are swept when their count passes a bound, not at every eviction; each words row shares its parse row's rowid, so it is deleted by rowid.
Add the eviction to line 77's changed-read phases and to Task 10a's Step 4 phase times.

### V3. Important. Task 10a: no test can tell a `reading()` that holds a read transaction from one that does not, and Python's `sqlite3` by default does not

Handle: line 32 (invariant 5: a reader takes a state "only inside one read transaction"); line 493 (`reading()`); line 519 (`test_eviction_between_lookups_cannot_split_a_read`: "the writer waits or the reader falls back"; `test_reader_during_a_concurrent_keep_state`); line 506 (a stored state whose interval misses `now` is rebuilt and kept under the same key); line 432 (journal mode `DELETE`).
Python's `sqlite3` in its default mode opens a transaction only before a data-changing statement, so a `reading()` written as `with conn:` around `SELECT`s runs each lookup in its own autocommit read.
Verified with `/var/tmp/lodge-recheck2/read_txn.py`: on a default connection, after the state row and one bucket are read (`in_transaction` False), another connection commits a re-keep of the same key, and the reader's next bucket comes from the new build; with `isolation_level=None` and an explicit `BEGIN`, the writer gets `database is locked` and the reader's second bucket is from the build it started with.
The named tests pass either way: an eviction between lookups leaves buckets missing, which the reader detects and falls back on, and a reader "between two statements" of another connection's `keep_state` sees none of its uncommitted writes under rollback-journal isolation whatever `reading()` does.
The case only a real transaction protects is a re-keep of the same key with different content, which line 506 makes routine: a state built at `now1` (a new decision dated in the future fails check 1, line 517) is rebuilt under the same key once the clock passes that date.
Failure scenario: reader R at a time inside the old interval reads the state row and the bucket of one record; process W, whose clock has passed the decision's date, re-keeps the key; R reads a second record's bucket from W's build and prints one record as failing check 1 and another as not, a combination neither in-memory read prints.
Fix: say that the index's connection uses `isolation_level=None`, that `reading()` issues `BEGIN` and ends with `COMMIT` or `ROLLBACK` in a `finally` (so no SHARED lock outlives it, including through the in-memory fallback), and that every write uses `BEGIN IMMEDIATE`; add `test_rekeep_between_lookups_waits_for_the_reader` (inside `reading()`, after one lookup, another connection re-keeps the same key with other rows: its commit fails busy or waits until `reading()` ends, and the reader's output equals the in-memory read at its own `now`) and assert `in_transaction` inside `reading()`.
Say also what `keep_state` does with a key that exists (replace it whole in its transaction, and whether it then counts as the newest state for first in, first out), which the plan leaves open.

### V4. Minor. Tasks 8b and 9: the flag and conversion caches do not say to take their key before reading their inputs

Handle: line 31 (invariant 4); line 386 (flags keyed by the stat of git's index file); line 388 (conversions keyed by the configuration values, the source files' bytes, and that stat); line 435; line 585 states the order for folder signatures only (stat, then list, the correctness review's M7); line 448 (`test_cached_flags_and_conversions_keyed` checks a different key, not the order).
If the key is taken after `git ls-files` or `check-attr` runs, a git command that rewrites the index, or an edit of a `.gitattributes`, between the two stores the old answer under the new key, and it stays a hit until the next change.
Failure scenario: `git update-index --assume-unchanged lodge/x.md` lands while lodge runs `ls-files`; the cached flags omit `x.md` under the new index stat; a later edit of `x.md` on disk is not in the overlay, and an indexed `show` prints the committed text while the gate reads the disk.
Fix: take the stat, the configuration values, and the source bytes before the git call, take the stat again after it, and keep the result only when the two stats are equal; name "the stat" as inode, size, `mtime_ns`, and `ctime_ns`; add the interleaving to `test_cached_flags_and_conversions_keyed`.

### V5. Minor. Task 10a: a family root that is no record's own code has no citer row, so its searches run in memory, or print wrongly if a missing row is read as empty

Handle: line 488 (`codes`: lower-cased code to IDs); line 508 (citer rows "against the state's codes ... one row per code"); line 230 (a family holds records whose code starts with the query and a dot); lines 232 to 233 (`code_tokens` yields a prefix only before a `.` that no letter or digit follows); line 498 (`citing` returns None for a missing row); line 544.
When `CODE-17.why` exists and no record is coded `CODE-17`, `search CODE-17` has a non-empty family, so ranking step 2 needs the citers of `code-17` (texts holding `CODE-17` alone or before a final dot), but no citer row exists for it.
By line 506 the missing row ends the read in memory, every time; a builder who reads a missing row for a non-code as "no citers" prints a list without them.
The bench store gives every `.why` code its root (line 114), so Step 4's numbers do not show it.
Fix: write a citer row for every family root, that is every code of the state and every prefix of one that ends before a `.`; add the case to `test_show_code_reads_citers_without_texts` or to `test_search_prints_as_in_memory`.

### V6. Minor. Task 9: the flag cache in the index makes a seen read write after any `git status`

Handle: line 57 ("a read of a seen state writes nothing"); line 435 (flag and conversion results kept in the index, each in its own transaction); line 518 (`test_seen_read_writes_nothing` in a still repository).
`git status` replaces git's index file whenever it refreshes an entry; verified at `/var/tmp/lodge-bench/s90000`: after a touched record, `git status` gave `.git/index` a new inode and `mtime` (it also did this to the bench store's index, the only change this recheck made there, beside one record's `mtime`).
So an agent's routine `git status` turns its next seen read into a write transaction with `synchronous=FULL`, which also takes the write lock other processes' `keep_state` waits on.
Uncached, the flags call costs 0.020 s at `s90000` (`git ls-files -t -v -z -- lodge .gitattributes`, best of three, 11.5 MB of output).
Fix: either say that refreshing these caches is the one write a seen read may make, and test it, or keep them in the store object only (the 0.020 s is then in every read, and goes in line 75's git phase, which today omits the flags call).

### V7. Minor. Task 10b: the FTS table's `key` column is not said to be unindexed

Handle: line 543 (FTS5 table `(key, title, statement)`); `probes/fts.py` used `id unindexed`; line 540 (`candidates(words, every)`).
As written, the ascii tokenizer indexes the path and the blob's hex, so a query word such as `lodge`, `decisions`, or `md` matches every row through its key: correct after `rank`, which reads the title and statement word sets, but a broad search for any word that is also a path part, and `every` true for keys that hold a word only in their path.
Fix: `key UNINDEXED`, the rowid shared with the parse row (V2), and `{title statement}:` column filters in the match expression.

### V8. Minor. Task 10b: its Files list misses the callers of the changed `keep_parses`, and the plan's place for "words per parse" would make a cycle

Handle: line 530 (10b modifies `app/read_model.py` for words per parse, and `ports.py` so that `keep_parses` takes words, but not `app/state.py`, which calls `keep_parses` from Task 9, line 408 and 442, nor `tests/app/fakes.py`, whose fake index implements it, line 450); line 460 (`read_model.py` builds rows "from a checked `State`", so it imports `app/state.py`).
If `state.py` takes each parse's words from `read_model.py`, the two import each other, which `tests/test_structure.py` refuses (line 33).
Step 0's skeleton would catch the cycle, but the builder then places the function without the plan.
Fix: put the words of a parse in `core` (beside `core.words`, a pure function of a `Parsed`), and list `app/state.py` and `tests/app/fakes.py` among Task 10b's Modify files.

## The invariants against every task that writes, evicts, or reads the index

The five invariants are the right set: they make every stored value either self-keyed (parses, flags, conversions, folder rows, facts) or reachable only through a marker that one transaction publishes with everything it promises, and they leave a reader nothing to trust that it cannot check, except a search's candidates.
That exception is why invariants 2 and 3 carry search alone: a missing words row cannot be seen by the reader (line 544), so the writer must never publish or keep a state without one, and V1 is where the plan's text still admits it.
Per place:

| Place | Invariants | Upheld as written | Would the named tests catch a violation |
|---|---|---|---|
| Task 9, `keep_parses` | 1 | Yes | Yes (448: interrupted at each statement, concurrent) |
| Task 9, flag and conversion caches | 4 | Key named; order not (V4); a seen read writes (V6) | Key: yes (448); order: no |
| Task 9, pruning | none of the five; d-4n5tr6 | Yes | Yes (447) |
| Task 10a, `keep_state` | 2, 3 | Atomicity yes; the new state's own references at its eviction, and when "missing" is decided, open (V1) | Atomicity yes (519); V1 no |
| Task 10a, eviction | 3 | Contract yes; mechanism and cost unspecified (V2) | Shared-between-kept-states yes (518); new state no (V1) |
| Task 10a, the reader | 5 | Missing or short: yes; same-key re-keep between lookups needs a real transaction the tests do not force (V3) | Missing: yes (517, 519); re-keep: no |
| Task 10b, words | 1, 2 | Yes, given V1 | Interrupted and locked: yes (551); V1 no |
| Task 10b, the reader | 5 | Rows and parses checked; candidates rest on 2 and 3 | Only through the property test, by chance for V1 |
| Task 10c, facts | 2, 3, 4 | Keyed by ident alone, which is enough: `check_state` and `derive` take the snapshot only (`src/lodge/app/state.py:46` to `47`); eviction at the writing transaction is V1 | Partly (570) |
| Task 11, folder rows | 4, 5 | Yes: each row carries its stat and base, a missing or undecodable row is listed | Yes (588) |

Two tests add nothing as worded: `test_reader_during_a_concurrent_keep_state` (line 519) and `test_search_between_another_connections_writes` (line 551) cannot fail under rollback-journal isolation, since another connection's uncommitted writes are invisible; the interrupted-write tests already cover what they aim at, and V3's test covers the reader.
The state key (two idents and the settings digest, line 483) misses nothing a stored state depends on: `read_checked` reads two trees, the settings, and the clock (`src/lodge/app/state.py:59` to `66`), the clock being covered by the validity interval, and the answers read no clock (`src/lodge/app/threads.py:139`).
The overlay's ident and the listing come from the same bytes read once (line 389), so a disk change between `identities()` and `listings()` cannot store a state under the key of other contents.

## Verification and limits

Probes, all under `/var/tmp/lodge-recheck2/`: `probe/guard.py` (Task 3's guard as now worded) with `probe/gfuzz.py` from the earlier recheck, run from the worktree with `uv run --frozen --quiet python`; `evict_cost.py`, `fts_delete.py`, and `read_txn.py` with the system Python 3.14.7 and SQLite 3.53.4 on native ext4, against scratch databases only.
The `s90000` bench store was read; `git status` there refreshed its index file, and one record's `mtime` was touched, with no content change (`git status --short` empty afterwards).
No index code exists yet, so V1 is the plan's text against itself, and V2's numbers time the mechanisms an implementation would use, not lodge.
No `lodge add`, network, commit, or push; this file is the only change in the worktree.
Read: the plan at `e483122`, `plan-fix-2.md`, `plan-recheck-opus.md`, `plan-recheck-codex.md`, the progress ledger, `probes/fts.py`, `plan-report.md` (its timings), the decisions d-6hb3yd, d-aej8rs, d-c0q20c, d-9r24jc, d-4n5tr6, d-gd00c6, d-hxmdkz, d-her016, d-rs76ks, d-dxqxsn, d-faakge, d-ana6c0, d-n9w4by, d-zyqzkg, d-ytf272, and `src/lodge/app/state.py`, `src/lodge/app/reads.py`, `src/lodge/app/results.py`, `src/lodge/app/threads.py` (in part), `src/lodge/core/views.py` (in part), `src/lodge/cli/output.py` (in part).
Not read: `plan-review-*.md` beyond what the rechecks quote, `brief.md`, `lodge spec` in full, the rest of `src`, and the tests.

## Counts

Earlier findings: N1 to N9, F1, F3, F5, F6, and R1 to R5 all fixed (F6 by d-hxmdkz); N3, N6, and R1 keep the residual V1.
New: 0 Blocking, 3 Important (V1, V2, V3), 5 Minor (V4 to V8).
The most important is V1: a parse unit that only the evicted state and the state being kept reference can be dropped in the transaction that keeps it, which silently omits a record from search, the class d-6hb3yd set out to close, and no named test reaches it.
