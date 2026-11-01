# Review of Task 8c's fix round (2df7794) and Task 10b (12099d1)

Status: complete.
Method: committed code read in `/var/tmp/lodge-review-t10b/wt` (detached at 12099d1); every probe ran there or on copies under `/var/tmp/lodge-review-t10b/scratch/` (copies of `/var/tmp/lodge-bench/s900` and `s9000`, their `.git/lodge` deleted first); the shared index was never written, and the builder's worktree was never touched.

## Verdict

Blocking 0, Important 2, Minor 6.
Indexed search printed exactly what in-memory search prints in every probe: 0 mismatches in about 2,300 compared runs (list below), with the index's words table checked row by row against `core.parse_words` after clears.
The two Important findings are performance and write-amplification faults that follow from how the cached search raises `Miss` (I1, I2); neither changes any printed text.
B1 of the Task 8c review was fixed in the tests' fixtures only; the R11-B branch is unchanged apart from M2, and that is consistent with R11-B's sentence (see B1 below).

## Task 8c fix round (2df7794)

### B1 (the Task 8c review's Important): fixed in the fixtures, not the branch; right under the sentence, with one coverage cost
What the commit does: `candidates()` (`identity.py:76`) is the one switch; `stat_current` (`:105`) is the R11-B body and gained only M2's `ls-files` failure handling (`:155`).
The property test (`test_identity_property.py:46-52`) now rewrites any CRLF working file to LF before the conversion source is removed, and the FIFO test (`test_identity_links.py:148`) edits its target first.
Probe: a copy of the tree with `candidates` returning `identity.stat_current(rev, trunk)` (`/var/tmp/lodge-review-t10b/r11b`).
- The property test plus the FIFO test passed 20 of 20 fresh runs (`scratch/r11b-prop20.log`, 12.1 to 14.8 s each), where the review had 4 failures in 8 runs on the old test.
- The whole of `tests/gitstore` there (with the four skipped R11-B cases unskipped): 353 passed, 6 failed, and the six are exactly the R11-A-only tests: `test_removed_attributes_agree` (4), `test_every_file_read_without_a_conversion_source`, and `test_r11a_does_not_compute_git_candidates`.
  The four `test_removed_attributes_follow_the_index` cases pass, CRLF included.
- Two of three mutants of `stat_current` (drop the `diff-index`/`diff-files` paths, drop `flagged.paths`) fail the property test in 0.45 s and 0.61 s; the third (drop non-blob kinds, a gitlink matter) survives it, which is as before: gitlinks have their own tests.
Is that right under R11-B's written sentence: yes for the code, because the sentence promises that the printed text never differs for line ends ("which lodge's parser normalises"), while the old property test asserted equal blob IDs, which the sentence does not promise for a staged CRLF file whose attribute source is gone.
The branch was therefore right and the assertion too strict; the builder's route was to remove the history instead of weakening the assertion.
Cost: nothing at property level now exercises "CRLF staged, source removed" under either rule; under R11-B the sentence's line-end claim rests on the one dedicated test, which is skipped in production, and under R11-A the same history rests on `test_removed_attributes_agree[text eol=crlf]`.
The report lists "the plan's R11-B switch is one function" but names no list of the tests STALE-1's answer A must flip; there are six (above), and the sixth (`test_identity_fix_round.py:13`) is the builder's own.

### M1 to M6 of the Task 8c review: all closed
- A1: `disk.py:33-100` walks with an explicit stack and reopens the ancestor chain with two transient descriptors; `test_disk_depth.py` (1,100 levels, soft limit 128 descriptors) passes.
  The reopen costs O(depth) per folder switch, so a 1,100-deep chain costs about 600,000 opens; it finishes, and ordinary trees (depth 4) switch rarely.
- M3: R11-A now makes no git calls beyond the exact walk (`test_r11a_does_not_compute_git_candidates`, passes).
- The rest checked by the suite (67 targeted tests passed, `ruff`, `mypy` 283 files, `vulture`, structure test: all green).

## Task 10b (12099d1)

### Printed output: identical in every probe
Harness: `scratch/harness.py` (in-process `lodge.main.main`, `LODGE_INDEX=off` against the index, stdout, stderr, and exit status compared), queries from `scratch/qgen.py`.
The harness counted calls of `IndexDB.candidates` and of `reads.search_many`, so each comparison says whether it ran cached or in memory.
- `s900` copy, 700 seeded queries (`run-a.log`): words (1 to 3), quoted multi-word arguments, `--phrase` over real runs, over random pairs, and with function words, codes (upper and lower case, dotted families, roots no record holds, `A`, `NO-ONE`, `CODE-9.`), IDs in both cases, absent words and IDs, empty queries, function words alone (bare and quoted), numerics, several queries per call, every filter, `--limit` 1 to 1000, `--brief`, and a unicode list: 0 mismatches, 638 cached, 62 in memory.
- `s9000` copy, 150 queries (`run-9000.log`): 0 mismatches, 131 cached.
- Special characters and FTS syntax in the query (`AND`, `NEAR(berth crane)`, `"berth"`, `berth*`, `^berth`, `title:berth`, `{title}: berth`, `berth -crane`, a quoted SQL fragment, fullwidth and superscript forms, 3,000 distinct words in one call and in one argument, a 2,000-word phrase): 0 mismatches; the large calls went through the cached path or fell back cleanly.
- Unicode records added to a copy (`café`, `Müller`, `Größe`, `straße`, `École`, `港口`, `İstanbul`, `ǅ`, `ﬁsh`, a combining `é`, `Ⅻ`, `①`): each found in the cached path with the same lines as memory.
  Invalid UTF-8 in a record makes it a problem rather than a record, so no lone surrogate reaches `insert_words` (the `except UnicodeEncodeError: continue` at `index_parses.py:73` could otherwise leave a parse row without its words row; it cannot today).
- Edit sequences (`scratch/run2.py`, three runs of 60, 60, and 50 steps, 336, 356, and 297 compared queries): a step is one of add a word, change a title, delete a record, create a unicode record, rename, revert to earlier contents, stage, commit, touch only; after each, 2 to 8 queries (the first three are the state's first, second, and third sighting; the edit's new words always among them): 0 mismatches.
- Clears: `TINYCAP=1` makes every keep over the cap clear the index; one single-process run (50 steps; the epoch reached 72) and three concurrent processes on one store (150 queries each, epoch 100): 0 mismatches.
  After each run `scratch/chk_index.py` compared every `parses` row with its `words` row: counts equal, no parse without words, no words without parse, and every row's title and statement text equal to `core.parse_words` of the parse.
- Fresh processes: 30 runs by `python -m lodge.main` in subprocesses over 6 edited states with 5 sightings each: 0 mismatches.
- Superset property: held structurally (every rank branch other than the exact ID, the family, and the citers needs a query word in the record's title or statement, a phrase's tokens contain its words, and `needs_memory` sends the queries with no words and a code or phrase to memory), and empirically by the runs above.
  Not run: `s90000` (the builder's replay compared 108 samples there, which I did not repeat) and branch mode.

### Fallbacks cannot print a partial result
The cached closure builds every `Listed` into a local tuple and returns it only at the end (`indexed.py:256`); every exit before that is `raise Miss`, caught with all other exceptions in `_run` (`:94`), which discards the partial value and answers the whole request in memory.
Rows the cached path found incomplete (`rows()` returns `{}` on any bucket fault) are covered by the `ids <= rows.keys()` and `extras <= rows.keys()` checks (`:213`), which is also what causes I2.
Faults injected after each SQL statement of `keep_state` and a locked database leave no searchable state (builder's tests pass; I ran them).

### FTS created, cleared, rebuilt: coordinated, checked
`create_words` runs at index creation (`index_schema.py:37`), swallowing only the exact "no such module: fts5" error; `clear` drops `words` before listing the tables and re-creates it before the epoch rises (`index_space.py:90-97`), in the keep's write transaction, so a reader on an older snapshot keeps its words and a reader after the commit sees an empty table with the new epoch.
Every parse unit is inserted through `insert_parses`, and the words row only when `rowcount` says the parse row was new (`index_parses.py:70-72`); `parses.rowid` is an explicit `INTEGER PRIMARY KEY`, so no vacuum can renumber it.
The build digest includes `sqlite3.sqlite_version` and `sys.version`, so a file built without FTS5 is not opened by a build that has it.

## Important

### I1 Important: a search that must run in memory re-keeps the whole stored state, on every read
`indexed.py:178-179` (`needs_memory` raises `Miss`) and every other `raise Miss` in `cached`, with `_run` at `:94-96` and `:104`.
When the state is stored and valid and `cached` raises, `_run` takes the memory path and, because `index.seen(key)` is true, returns `keep`, which the CLI runs after the output (`commands.py:67-69`): `keep_state` rewrites every bucket, answer, citer, and facts row of a state that was already complete.
Probe (`s900` copy, counting `keep_state`): `search A`, `search THE`, `search --phrase "of the"`, and `search d-zzzzzz` each ran once in memory and once through `keep_state`, on every call; `search berth --brief` ran neither.
Failure scenario at scale: `s9000` copy (index 25.8 MB against a 24.2 MB cap): the epoch rose from 3 to 4 on one `search A` (the cap sees an over-size index and a kept state and clears everything, parse units and FTS included), `search berth` before and after left it alone, and `search A` took 2.2, 1.1, and 2.8 s against 1.8 s with `LODGE_INDEX=off` (CPU shared with my other runs, so only the epoch is firm).
A function-word code (`A`, `THE`, `NO-ONE`) is a query an agent can type by accident, and each one wipes the index of a large store.
The same fault exists for `show A` from Task 10a; Task 10b adds the search triggers.
Fix: let the search raise a distinct exception for a decision about the query (`needs_memory`, an unknown exact ID, `candidates` None) that `_run` answers in memory without returning `keep` when the stored state was valid; keep `Miss` for a stored state found incomplete, where a re-keep heals it.
Test: a stored state, a `needs_memory` query, a counting `keep_state` wrapper: zero calls and an unchanged epoch.

### I2 Important: one record that is in `parses` but not in the current state sends every search that hits it to memory, for good
`indexed.py:201` (`ids` from every candidate parse, historical ones included) and `:213` (`not ids <= rows.keys()` raises `Miss`).
Parse units are never deleted except by a clear, so a deleted record, a record only on another branch you visited, or a record in the published tree but not the working tree leaves a parse whose ID has no row; every query holding one of its words then fails the check.
Probe (`s900` copy, three reads to store the state, then one deleted record file): all six following `search berth --brief` calls ran in memory, and calls 2 to 6 each also re-kept the state (I1), unchanged by further reads of the same tree.
In the edit-sequence run with 60 steps and seed 21, 132 of 336 queries ran in memory (function-word and unknown-ID queries included; I did not split the causes).
Failure scenario: after a `git checkout` of another branch and back, or one `rm` of a record file, the search the index was built to speed up costs a full build plus a full re-keep on every call, at `s90000` seconds to tens of seconds each.
The check is wrong, not the data: a candidate whose ID has no row is not in the current snapshot, so memory would not rank it either.
Fix: drop the `ids` condition and the historical IDs with it (rank over the candidates whose ID has a row with an equal key); what `rows()` returning `{}` on a bucket fault must still prove is better said by `rows()` returning `None` on a fault (or the state's promised bucket count) than by guessing from missing IDs.
Test: `test_deleted_record_does_not_send_search_to_memory`, a store, a stored state, a deleted file: `reads.search_many` not called and the output equal.

## Minor

### M1 Minor: the 8c fix round removes a history from the property test instead of weakening its assertion
`test_identity_property.py:46-52`: see B1; compare parsed texts for the staged-CRLF state instead of blob IDs, so both rules keep the history; list the six R11-A-only tests in the report and ledger for STALE-1.

### M2 Minor: an empty or filter-only search parses every record one by one
`indexed.py:224` (`wanted = set(rows)`) and `:229`: for an empty query `rank` returns `newest[:limit]` without reading a word, yet every row's parse is fetched with its own `SELECT` and its words computed for a `Candidate`.
`s9000` copy: `search --kind decision --limit 3 --brief` 1.04 s with the index against 1.58 s without, where `search berth` took 0.75 s; at `s90000` this is 158,000 single-key lookups (not measured).
Fix: for an empty query build the candidates from the rows and `Level1` fields only for the first `limit` after ranking by `(date, id)`, or keep `all_rows` ordering and fetch parses for the shown records alone.

### M3 Minor: an unknown exact ID sends the search to memory
`indexed.py:204-205` adds any `d-`/`s-` shaped query to `extras` and `:214` raises `Miss` when it has no row, so a mistyped or deleted ID costs a full build (and, until I1 is fixed, a re-keep); the plan says "the exact ID if it exists", and the code reads its absence as a miss.
Fix: take the exact ID only if `rows` holds it, and otherwise leave it out, since memory's exact-ID step finds nothing either.

### M4 Minor: the FTS table takes the stored index past the cap at `s9000`
Report: baseline index 25,763,840 bytes against 24,180,000 at `s9000`, 250,286,080 against 241,200,000 at `s90000`; Task 10a's `s90000` parse table alone was at the cap (241,197,056).
With one complete state already over the cap, the next keep of any other state clears the index (the report's 36 "changed (clear, cold)" rows).
The report discloses it and leaves it to Task 12 and d-gvz66f (awaiting the author), so this is a pointer, not a defect of the commit; `detail=none` is not available with the column filters the plan requires, so the cost is the plan's.

### M5 Minor: the plan's differential test cannot see the tokenizer
`test_search_prints_as_in_memory` uses `MemoryIndex.candidates` (`tests/app/fake_index.py:29`), which matches Python word sets, so the 300-query differential never reaches FTS5; only `test_sqlite_code_search_uses_stored_rows` and the end-to-end property (three-word vocabulary, no unicode) do.
My harness found no difference, so this is a coverage gap only.
Fix: run the 300 searches once against a real `IndexDB` on the same 500-record store with a vocabulary that includes non-ASCII and digit words.

### M6 Minor: production holds R11-B code that only tests run
`identity.py:105-170` (`stat_current`) and what only it reaches (`flags.scan` on the candidate group, `Conversions.paths`) run in no production read until STALE-1 is answered; the Task 8c review's M1 named the same smell for the deleted `Flags.read`.
Accepted by the plan (the switch is one function), so noted only: the ledger should say so beside the six tests of B1.
Also `Index.candidates(..., every)` has an `every` parameter that no production caller sets true (the plan's signature).

## Plan rules no test enforces
- "Several queries share one read": `cached` resolves each query's candidates separately and shares only `lookups.loaded`; correct, but no test counts `candidates` calls for a two-query search.
- The report's claim that the search keep runs after the second output flush is tested (`test_search_keeps_only_after_second_output_flush`).

## Files read
Plan (Global Constraints, Tasks 8c and 10b, Review Focus lines named), progress ledger diffs, both reports, `task-8c-review.md`, reviewer rules, `CLAUDE.md`, decisions d-e8pdqe, d-t2dsd3, d-kx50jd (`lodge show --reasoning`); all of `git show 2df7794` and `12099d1` under `src/`; `core/ranking.py`, `core/search.py`, `core/codes.py`, `app/index_lookups.py`, `app/indexed.py`, `app/reads.py` (search), `app/read_model.py` (`build_rows`), `gitstore/index_{db,schema,space,states,parses,words,transactions}.py`, `gitstore/identity.py`, `gitstore/disk.py`; tests `test_identity_lazy.py` (R11 part), `test_identity_property.py` and `test_identity_links.py` (diffs), `identity_rules.py`, `test_identity_fix_round.py`, `fake_index.py`, `test_indexed_search.py` (head), `index_property_support.py` (head).

## Files not read
`test_index_words.py`, `test_index_words_faults.py`, `tests/e2e/test_index_property.py` line by line (run green); `test_disk_depth.py` and `test_flags.py` line by line; the viewer; `gitstore/attributes.py` and `flags.py` beyond the diff; the builder's replay script and `/var/tmp/lodge-bench/task10b` timings (not repeated; `s90000` not run by me).

## Probes and logs
`/var/tmp/lodge-review-t10b/scratch/`: `harness.py`, `qgen.py`, `run1.py` (seeded queries), `run2.py` (edit sequences), `sub.py` (fresh processes), `chk_index.py` (words against parses), logs `run-a.log`, `run-9000.log`, `run2-21.log`, `run2-22.log`, `run2-31.log` (tiny cap), `run-c1.log` to `run-c3.log` (three concurrent processes), `r11b-prop20.log`; `/var/tmp/lodge-review-t10b/r11b` (the R11-B switch and three mutants `r11b-m1` to `r11b-m3`).
