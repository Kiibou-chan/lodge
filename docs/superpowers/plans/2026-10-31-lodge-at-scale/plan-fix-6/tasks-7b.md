# Tasks after plan fix 7b

These replace `tasks-7.md` whole; read beside `plan-fix-7b.md` (the measurements) and `tasks-6b.md` (which they amend, not replace).
Order: Task 9 (fix round 2 done at 094e9ce), Task 8c, Task 9c (new), Task 10a, Task 10b, Task 10c, Task 11, Task 12.
No delta state of any kind; `derive`, `check_state`, and `check_change` run in full on every build; Task 10b and Task 11 do not change.

## Task 9c (new): the parse lookup in one scan

Built after Task 8c and before Task 10a; it changes no port and no output.

**Files:**
- Modify: `src/lodge/gitstore/index_parses.py` (`find_parses`)
- Test: `tests/gitstore/test_index_parses.py`

**Interfaces:**
- `find_parses(db, keys)` keeps its signature, its result, and `IndexDB.parses`'s explicit read transaction around it (`BEGIN ... COMMIT`, so a clear committed meanwhile is not seen).
  When `len(keys)` is at least `SCAN_FROM = 1_000`, it reads `SELECT path, blob, value FROM parses ORDER BY rowid` once, keeps each row whose whole `(path, blob)` is in the set of requested keys, and decodes that row's value on its own, `from_plain(json.loads(value), CORE_CLASSES)` with the validators, the row's key and its decoded value carried together; the decoded value is then admitted by today's check, `value is None or isinstance(value, (Area, Decision, Problem, SpecEntry, Thread))`, in both the scan and the per-key path (the review of 7b, B1: `123`, `"text"`, `{}`, `[""]`, and a valid non-parse dataclass decode without raising); a row whose decode or validation raises, or whose value the check refuses, is a miss for its own key alone; a decoded `None` is a hit, as today; duplicate requested keys and rows of other blobs change nothing.
  Below `SCAN_FROM` keys it keeps the per-key `SELECT`.
  No values are joined into one document (the review's F1).
- Measured at 160,800 keys on 094e9ce, with the admission check: 1.089 s against 1.435 s for the per-key lookup, its result equal to the per-key lookup's (`measure-7b/scan7c.txt`).
  The scan reads every row, so its cost grows with the table; the cap (Task 9, d-4pbeax) bounds the table, and Step 4 reports the scan with the table at the cap.

- [ ] **Step 1: Write the failing tests:** `test_scan_equals_per_key` (a table of 2,000 units with older blobs of the same paths, a `None` parse, and a Problem; 1,500 requested keys, 20 of them absent and 5 requested twice: the result equals the per-key result); `test_one_bad_value_is_one_miss`, one case each, every other key found and equal to the per-key result: a truncated value; the review's `null,null` (valid only when joined); the pair `null,"foo` and `bar"` in adjacent rows (valid only when joined, with the right count of elements); a value of valid JSON that fails a validator; each of `123`, `"text"`, `{}`, `[""]`, and a valid `Level1` (decodes, refused by the admission check); `test_scan_reads_once` (a connection wrapper counts one `SELECT` above `SCAN_FROM` keys and one per key below); `test_scan_inside_one_read_transaction` (the read transaction's snapshot is established by a first `SELECT` inside it, then another connection clears and commits, then the scan runs: the result is the one from before the clear; and a clear committed between the `BEGIN` and the first `SELECT` gives misses only, which the read answers from memory; the review of 7b, B3).
  Mutants run once and recorded in the report, each failing a test: values joined into one `json.loads`; rows matched on the path alone; an exception ending the whole scan; the admission check removed from the scan.
- [ ] **Step 2:** run; expected FAIL.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** gate; at `s90000`, the whole state's lookup, best of three, beside 1.435 s, and once more with older units filling the table to the cap.
- [ ] **Step 5:** commit, push.

## Amend Task 10a

After SECOND-1 is recorded.

1. Interfaces, replace "otherwise the state is built in memory from `listings()` and the parse cache, kept, and the read answers from memory." with:
   "otherwise the read answers from memory, built from `listings()` and the parse cache, and keeps by SECOND-1: when the index holds no marker for the state's key (the full stored-state key, in the build's own index file), the read writes one (`seen(key, at)`, the 64 newest kept, the oldest deleted in the transaction that adds one), in one short `BEGIN IMMEDIATE` transaction with the parse units it missed and any facts it computed (Task 10c), and builds no rows, buckets, answers, or citers; when it holds a marker, the read returns its answer together with a deferred keep (below), and the command runs that keep only after its whole output was written and flushed without error."
   The deferred keep (the review of 7b, B5): a closure over the read's checked `State`, its listings, its parses, its `now`, its epoch, and its stored-state key, all pinned when the read answered; it never reads the files, the listings, or git again, so an edit during the output or the keep only leads the next identity to another key; inside it, the whole construction of rows, buckets, answers, citers, and facts, their encoding, and `keep_state` run, in that order, all within one boundary that catches every ordinary exception (not `KeyboardInterrupt` or `SystemExit`), prints nothing, and leaves the command's own exit status, nonzero ones included; it is called from the command's success path after the explicit flush, never from a `finally`, an `atexit` hook, or a release hook, and never after a write or flush that failed.
   `keep_state` keeps its signature; the read model's constructors are called only from inside the deferred keep, never while answering.
2. Interfaces, add: a clear deletes the `seen` table with the others; eviction leaves markers alone; a marker never answers a read, it only lets the next read keep.
   The cap (the review of 7b, B2), replacing Task 9's condition "and at least one state kept since the last clear": every write transaction (a marker's, a parse-only writer's, and a keep) first compares the used pages with `INDEX_FILE_CAP`, and when over it clears, provided the units inserted since the last clear (parse units and facts, counted in `meta.written`, which the clear resets to 0 and each insert raises by the rows it inserted) number at least the tree's file count, or a state was kept since the last clear; so a read that writes a whole working set after a clear is not cleared away by the next writer, and growth stays within the cap plus one working set whether or not any state is ever kept.
   `meta.kept` keeps its meaning, a complete state kept (Task 9 fix report, I4).
3. Interfaces, add: `keep_state` is called only from the deferred keep above, so no changed read builds or writes any row or citer before it prints (ruling 3).
4. Step 1, `test_indexed_reads.py`, add: `test_first_read_keeps_only_a_marker` (the first `show` of a new state: a connection wrapper sees one write transaction holding the marker and parse units and no bucket, citer, answer, or state row); `test_second_read_keeps_after_its_output` (the second `show`: the whole output is written and flushed, recorded by a stream wrapper, before the first call of any read-model constructor and before the first SQL statement of `keep_state`, both instrumented; the third `show` is a seen read that writes nothing); `test_first_read_builds_no_rows` (the first `show`: the read-model constructors are never called); `test_failed_keep_keeps_output_and_status` (a failure injected in turn into row building, bucket encoding, citer building, answer building, facts encoding, and each SQL statement of `keep_state`, with and without an eviction: the printed output and exit status equal `LODGE_INDEX=off`'s, for a `show` that exits 0 and for a `show` of several refs, one unknown, that exits nonzero, and `state()` finds nothing new); `test_keep_uses_pinned_inputs` (a file edited after the second read answered and before its deferred keep runs: the kept state is the one under the second read's key, equal to a full build of the files before the edit, and the next read builds the edited state); `test_output_failure_keeps_nothing`, one case each, no constructor called and no keep begun: a stream that accepts the writes and raises on the flush; Python's standard output closed; a broken pipe with Python's default handling (the exception); a broken pipe with `SIGPIPE` at its default disposition (the process ends by signal 13, and the next read finds no new state); `test_killed_during_keep_leaves_no_state` (a child process killed with `SIGKILL` inside the keep's transaction, after its buckets: the next read finds no state row and prints as `LODGE_INDEX=off`); `test_marker_bounded_and_cleared` (65 states seen once: 64 markers; a clear removes them).
   `test_index_states.py`: `test_seen_read_writes_nothing` keeps its text; a read that finds a marker but no state is not a seen read; `test_first_sightings_alone_stay_under_the_cap` (from an empty index and again just after a clear, 50 states each seen once with a cap of 16 MiB and parse units filling it: used pages never pass the cap plus one working set, the epoch rises, `meta.kept` stays 0, and a second and third read of the last state keep it and then answer from it).
   Amend Task 10a's own Step 1 (the review of 7b, B6): in `test_seen_state_reads_no_snapshot` and `test_show_code_reads_citers_without_texts`, the patched `assemble` and `code_tokens` are forbidden on the third `show`, after the second's keep was seen to commit, instead of on the second; tests whose subject is not the keep's timing preseed a complete state through `keep_state` directly.
5. Step 4, add: at `s90000`, the first read of a changed state (prints and ends), the second (prints, then ends after its keep), and the third (seen), each timed to its exit, with the complete keep's parts (rows as `Row`, buckets, answers, citers with family exclusion and roots, facts, and `keep_state`'s transaction with its eviction and any clear apart); the kept state's bytes, how many states fit under the cap, and the clears after ten such cycles; plan fix 7b's 8.764 s is a partial proxy, not this.

## Amend Task 10c

1. Produces, keep the text, and add: facts are units like parse units, content-keyed by the published ident and immutable; a read that computed the published facts writes them in its marker transaction (SECOND-1) or its keep, so the published `derive` and `check_state` (1.564 s at `s90000`) run once per published ident, not once per changed read.
2. Produces, add: the published snapshot is `snapshot_of(published, index, parses)` as today, or the current snapshot when Task 4's identical-listing shortcut holds; no other reuse (ruling 2).
3. `check_change` and its helpers do not change.
4. Step 1, add: `test_facts_written_on_the_first_read` (the first read of a changed state with no published facts writes them in its marker transaction; the next read of another changed state with the same published ident runs no published `derive`, by a patched counter).
5. Step 4, add: the changed read's stages as in plan fix 7b's table, with the facts hit and miss apart.

## Amend Task 12

1. The changed row's target is 3 s, without a conversion source; plan fix 7b measures the exact path's stages at 4.713 s with the published facts kept and its floor at 3.214 s, so the row is expected to miss: Step 2's stop applies, and `timings.md` gives the phase table with the floor named.
2. Three changed rows at `s90000`, each timed to the process's exit: the first read of a changed state, the second (its keep after the output, ending after the read plus the complete keep, which Task 10a measures; plan fix 7b's partial proxy alone took 8.764 s), and the third (a seen read); each under the stop as Step 2 states it.

