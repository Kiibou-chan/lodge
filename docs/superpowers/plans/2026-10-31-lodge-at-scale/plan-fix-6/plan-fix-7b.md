# Plan fix 7b: the exact changed read

Replaces plan fix 7, which the review of 6b and 7 rejected (`review-codex-67.md`, F1 to F10).
Coordinator's rulings applied: no delta state of any kind (DELTA-7 dropped: no rows, citers, or failing IDs derived from an earlier kept state); the full `check_change` runs, as today; only optimisations exact by construction; the changed read never rebuilds every stored row and citer before it prints; the 3 s target stays (no TGT-7), and Task 12 records the measured miss and its floor.
Earlier rulings kept: RAW-1 rejected, no stat cache, LAZY-1 not taken, the gate and `add` exact, conversions reported apart, brief ruling 1.
STALE-1 is still with the author; nothing below depends on its answer except the identity's own row.

## Answer

- The exact changed read at 160,800 files measures 4.713 s as a sum of stages run in one process (table below), when the published state's facts are kept (Task 10c); 6.249 s when they are not; its floor, the stages that run in full whatever is kept, is 3.214 s.
  So the 3 s target is missed, and Task 12 records the miss.
- Keeping a whole state is not measured: a partial proxy of it (views of every record, their buckets, a stand-in citer pass, one partial transaction) took 8.764 s at 160,800 files, one call per part, and the review's reruns 8.923 s and 9.358 s; Task 10a measures the complete keep.
  Chosen: a state is kept only the second time a read sees it, and that read keeps it after its output is written and flushed; the first read only writes a marker.
- The seen read is unchanged from plan fix 6b: 0.273 s measured there (0.243 s in the review's rerun) for everything but the app path and printing; one bucket's JSON decode adds 0.2 ms; it is reached from the third read of an unchanged state.
- Decision needed: SECOND-1 (the keep rule, below).

## Setup

Build 094e9ce in a detached worktree `/var/tmp/lodge-plan-fix7/wt`, installed non-editable into `/var/tmp/lodge-plan-fix7/venv` (CPython 3.13.5, SQLite 3.47.1, PyYAML 6.0.3 with libyaml, git 2.56.0).
Store: a fresh copy of `/var/tmp/lodge-bench/s90000` at `/var/tmp/lodge-plan-fix7/s90000`, `.git/lodge` removed, warmed by two `lodge waiting` (16,523 ms and 8,954 ms; index file 145,293,312 bytes, 160,800 parse rows; `measure-7b/warm7b.txt`), then one line appended to `lodge/spec/area-000/s-01z2c4-berth-scheduling-rationale.md`, so current and published differ in one path and that path's parse is a miss.
Run: `cd /var/tmp/lodge-plan-fix7/s90000; GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_ATTR_NOSYSTEM=1 /var/tmp/lodge-plan-fix7/venv/bin/python measure-7b/phases7b.py`, one call at a time, gc disabled, best of three unless a row says one call; output `measure-7b/phases7b.txt`.
The admitted scan (`scan7c.py`, `scan7c.txt`) ran on a second fresh copy made the same way (`warm7c.txt`: 16,724 ms and 8,868 ms).
The copy and worktree are removed afterwards; a rerun rebuilds the copy as above.

## The exact changed read, stage by stage

Fixed stages from plan fix 6b (`measure-6b/proto_stages.txt`): start, imports, and parser 0.166 s; the fast identity after Tasks 8c and 11 about 0.1 s under STALE-1's A (R11-B); the current mapping 0.14 s; 0.406 s together (the review's rerun gives 0.388 s for the same terms, `scratch/67/fixed_stages.txt`).
Under STALE-1's B (R11-A) the identity reads every file, about 3.1 s (`measure-6b/hash_all.txt`), and every row below moves up by that.

| Stage | Exact, as 7b builds it | Today | Handle (`phases7b.txt`) |
|---|---|---|---|
| Fixed stages | 0.406 s | 0.406 s after Tasks 8c and 11 | 6b |
| Parse lookup | 1.089 s: one rowid-ordered scan inside the read transaction, each row matched on its whole `(path, blob)`, decoded on its own, and admitted by today's type check, an error or a refused value a miss for that key alone (Task 9c) | 1.435 s, per-key `SELECT` (1.428 s in `phases7b.txt`) | `scan7c.txt`: its result equals today's lookup on all 160,800 keys |
| The one missed parse | under a millisecond | the same | |
| `assemble` | 0.146 s | 0.146 s | |
| `derive`, current | 0.996 s, full | the same | |
| `check_state`, current | 0.577 s, full | the same | |
| Published snapshot | 0.476 s, `snapshot_of` with the read's parses as its memo, as `read_checked` does; equal listings take Task 4's shortcut instead | the same | |
| Published `derive` and `check_state` | 0.028 s when Task 10c's facts for the published ident are kept; 1.564 s (1.001 plus 0.563) when not | 1.564 s | |
| `change_facts`, `check_change` | 0.918 s, full | the same | |
| `failing_ids`, `unrecorded_problems` | 0.065 s (0.027 plus 0.038) | the same | |
| The answer printed (`waiting`'s decisions and threads) | 0.012 s | the same | |
| Sum | 4.713 s with the published facts kept; 6.249 s without | 6.588 s with the per-key lookup and no kept facts | |
| Floor: fixed, lookup, `assemble`, `derive`, `check_state` | 3.214 s | | |

The sum is a sum of stages measured in one process on one state, not a timed command; Task 12 times the command.
The lookup row comes from `scan7c.txt` (the admission check of the review of 7b, B1, added; 1.056 s without it in `phases7b.txt`), the other rows from `phases7b.txt`.
It leaves out writing the output, and the parse-unit insert for the missed file, both under a few milliseconds here.
The review's rerun of the same stages on 094e9ce agrees within 3 % for every stage it repeated (`check_change` 0.895 s there) (`review-codex-67.md`, timing table).

## What a whole keep costs, and when to keep

A partial proxy of keeping a state, at 160,800 files, one call per part (`phases7b.txt`); it is an estimate of the order of the cost, not of the keep Task 10a builds:

| Part | Time |
|---|---|
| Rows: `level1`, `level3`, and `changed_by` of every record | 0.855 s |
| `to_plain` and `json.dumps` into 1,024 buckets (71,061,698 bytes) | 2.190 s |
| `code_tokens` of every record's title and statement | 2.238 s |
| Citer rows: every token's records, newest first (1,200 tokens; 27,583 codes) | 3.015 s |
| The citer rows of the state's codes as JSON | 0.020 s |
| The state's facts as JSON | 0.030 s |
| One write transaction of buckets, citer rows, and facts | 0.416 s |
| Sum of the proxy | 8.764 s (the review's reruns: 8.923 s and 9.358 s) |

What the proxy is not (the review of 7b, B4): it encodes `Level1`, `Level3`, and `changed_by` of each record, texts included, where Task 10a's `Row` holds only derived fields with the file key and areas (50,440,556 bytes in 1,024 buckets on the review's rerun, against the proxy's 71,061,698); its citer pass sorts date strings and has neither family exclusion nor family-root rows; its transaction writes no answers, state row, missed parses, full-text rows, or eviction, and runs no cap check.
So the proxy gives no keep time, no state size, and no count of states under the cap; Task 10a's Step 4 measures all three with the complete keep.

The two keeps ruling 3 allows, for a state read k times before it changes, writing C for the read (4.713 s), K for the complete keep (not measured; the partial proxy alone took 8.764 s), and s for a seen read (about 0.27 s):

| Rule | The first read prints after | Its process ends after | Total over k reads |
|---|---|---|---|
| Keep after the output is written and flushed, on the first read | C | C + K | C + K + (k - 1) s |
| Keep only the second time a state is seen, after that read's output is flushed | C | C, plus a marker write | C for k = 1; 2C + K + (k - 2) s for k at least 2 |

A process that ends late is a read that ends late for its caller: a shell, a script, or an agent waits for the exit, not for the flush.
Under the first rule every changed read ends after C + K; under the second, only the second read of a state does, and a state read once, the usual case after each edit, never pays K.
The second rule costs one more full read (C) for a state read at least twice, and saves K for every state read once; with K unmeasured, no break-even share is claimed, and no measurement of how often a state is read once exists.
The choice rests on the ending times: the second rule ends every first read at C, and the worst single read is C + K under both.
Chosen: the second rule (SECOND-1); the second read keeps only after its output is flushed, as ruling 3 requires.
The first read writes the marker and, when it computed them, the published facts and its parse units, in one short transaction: the marker's own write measured under 0.05 ms (`phases7b.txt`).

## Correctness of the keep

- A seen read stays exact: it answers only from a state whose row exists, and a state row is written last in the transaction that holds every row it promises (invariants 1 to 3, unchanged); markers never answer anything.
- A failed or interrupted keep leaves no partial state: the keep is one `BEGIN IMMEDIATE` transaction, so a failure rolls it back and a killed process leaves the WAL without its commit; the epoch rule (d-c6cegr) still decides which units the keep inserts.
- The keep runs only after the output was written and flushed without error; any exception in it is swallowed, nothing is printed for it, and the exit status is the read's own.
- A marker is the full stored-state key (current ident, published ident, settings digest), inside the build's own index file; markers are bounded (the 64 newest, the oldest deleted in the transaction that adds one) and go with every clear; a marker whose state is later evicted only makes the next read keep it again; it never supplies data.
- The cap stays armed without a kept state (the review of 7b, B2): Task 9's clear needed "at least one state kept since the last clear", which a run of first sightings never meets, so parse units and facts could grow without bound (the review's probe: 30,056,448 used bytes against a 16 MiB cap, no clear); every writer now clears over the cap once the units inserted since the last clear reach the tree's file count or a state was kept, which bounds the file at the cap plus one working set.
- The keep is deferred, not merely late (the review of 7b, B5): the read returns a closure over its pinned inputs, and the whole construction of rows, buckets, answers, citers, and facts, their encoding, and the SQL run inside it, after the output's explicit flush, within one boundary that leaves the exit status alone; an edit made meanwhile only gives the next read another key.
- Published facts are content-keyed and immutable like parse units, so writing them on a first read is not state derived from an earlier keep; ruling 2's ban is on rows, citers, and failing IDs.

## The rejected parts of plan fix 7

- Joined decoding (F1): dropped; each row is decoded on its own and admitted by today's check, at 1.089 s against the joined form's 1.027 s (plan fix 7, on 8df3b2e).
- The diff-scoped `check_change` (F3, F5): dropped; the full one runs, 0.918 s.
- Delta rows, buckets, and citers (F2, F4, F6, F8, F9): dropped with DELTA-7.
- The published snapshot from the current one: dropped except where Task 4's identical-listing shortcut already gives it.
- TGT-7 (F7): dropped; the target stays 3 s.

## Decision needed

- SECOND-1 (scope `process`, for the coordinator; the keep rule ruling 3 asked me to choose; amends Task 10a's "otherwise the state is built in memory ..., kept, and the read answers from memory"): "A read keeps a state in the index only the second time it finds that state not kept: the first such read answers in memory and writes the state's key as a marker, with any published facts and parse units it computed; a later read that finds the marker answers in memory, writes and flushes its output, and only then keeps the state in one transaction, whose failure changes neither the output nor the exit status; no read keeps a state before its output is flushed."
  Handles: `phases7b.txt` and `scan7c.txt` (C 4.713 s, the partial keep proxy 8.764 s, the marker under 0.05 ms); cost if wrong: a state read exactly twice costs one full read more than keeping it on the first read.
- No other decision: the target stays 3 s (ruling 4), STALE-1 stays with the author, and Task 9c's scan is exact by construction and by its test.

## The review of 7b, applied

`review-codex-7b.md`: 6b accepted; 7b accepted with fixes, each applied here and in `tasks-7b.md`.
- B1 (the scan dropped today's admission check): restored in both paths, with the four refused values and a non-parse dataclass in the tests; measured 1.089 s.
- B2 (first sightings alone never arm the cap): every writer clears over the cap once a working set has been inserted since the last clear, or a state was kept; tested from an empty index and after a clear.
- B3 (the scan's snapshot test): the snapshot is established by a first read before the other connection clears.
- B4 (the keep figure rested on a partial proxy): 8.764 s is labelled a partial proxy; the state size, the states under the cap, and the break-even share are withdrawn; Task 10a measures the complete keep.
- B5 (deferred construction and every keep failure): the keep is a closure over pinned inputs, run after the flush, with construction, encoding, and SQL inside one boundary; failures injected at each stage and output failures of four kinds.
- B6 (inherited tests expected a hit on the second read): moved to the third read, or a preseeded state.
