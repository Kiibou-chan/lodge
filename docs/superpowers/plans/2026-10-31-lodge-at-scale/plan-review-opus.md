# Plan review: lodge at scale, correctness and design

Reviewer angle: correctness and design (Opus).
Plan: `docs/superpowers/plans/2026-10-31-lodge-at-scale.md` at `5bcf812` on `read-speed`.
Probes: `/var/tmp/lodge-review-opus/` (git probes `g1/`, `g2/`; loader fuzz `probe/cfuzz.py`, `probe/cfuzz_guard.py`, `probe/ctab.py`), each run from the worktree with `uv run --frozen --quiet python <probe>`.

## Blocking

### B1. Task 3: libyaml with a fallback on exceptions changes check results

Handle: Task 3, Produces ("on any exception from it calls today's pure-Python path"); `src/lodge/core/yamlio.py:59` (`load_yaml`); brief evidence item 2.
The fallback only covers inputs where the C loader raises.
The C loader also accepts inputs the Python loader rejects, and returns different values for some it both accept.
Verified with `probe/cfuzz.py` (a C loader built exactly as Task 3 describes: empty implicit resolvers, kept constructors, pair joining, duplicate-key refusal): of 200,000 generated headers, 2,516 parse under C and fail under Python, and 90 parse under both with different values.
Realistic case (`probe/ctab.py`): `title: x<TAB>` (a trailing tab from a hand edit) is `{'title': 'x'}` under C and today is `found character '\t' that cannot start any token`, so today the record fails check 1 ("the header is not valid YAML") and with Task 3 it reads and passes.
The same holds for `title:<TAB>value`, `- a<TAB>` in a list, and `title: x<TAB># c`.
Value differences: a BOM after a line break (`\n﻿"d"` is `d` under C and `﻿"d"` under Python); and `key: |#` (a block scalar indicator followed by `#`) parses under C only.
Failure scenario: an agent's hand edit leaves a trailing tab in a header; today `lodge check --gate` fails and names the file, after Task 3 the gate passes, against d-1bww1r.
`test_same_value_as_the_python_loader` would catch this only if its generator happens to emit tabs in plain context; the plan's list (tabs among others) does not make that certain, and the test's "or the C path raised" branch cannot detect the C-accepts case at all unless it also asserts the Python path did not raise.
Fix: accept the C result only for a header that a guard admits, and run the Python path for every other header.
The guard that gave zero differences in three further fuzz runs of about 55,000 admitted headers each (`probe/cfuzz_guard.py`, seeds 4 to 6): no character of `[\t\r\x85﻿  ]`, none of `[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f\ud800-\udfff￾￿]`, and no match of `[|>][-+0-9]*#`.
Stronger and simpler: admit only headers whose every line has the shape lodge's writer produces (`key: "json"`, `- "json"`, indented keys of a nested mapping, `key:` alone), since lodge writes values with `json.dumps` (`yamlio.py:78`); every other header takes the Python path.
Make the test assert both directions: when the C path succeeds, the Python path succeeds with the same value; seed the generator with the cases above.
With the parse cache of Task 9 the Python path runs once per blob, so the cold cost of a narrower guard is paid once.

### B2. Task 8: the checkout identity as written changes the gate's output on a clean or touched checkout

Handle: Task 8, "Identity, checkout mode" (`ident` = sha1 over `base` and the sorted overlay) and "the gate's 'committed against working tree' note stays, decided by comparing the `HEAD` tree's ident with the current ident"; `src/lodge/gitstore/published.py:37` (`committed_gate`), which today compares file mappings.
Two gaps, each verified with git 2.56 in `/var/tmp/lodge-review-opus/g1`.
First, `git diff-files` names a file whose stat changed but whose content did not: after `touch lodge/a.md`, `git diff-files --name-only -- lodge` prints `lodge/a.md`.
The overlay then holds `lodge/a.md` with the same blob as `base`, and the ident differs from the clean one, which contradicts the plan's own `test_touched_but_unchanged_keeps_the_ident`.
The same happens for `test_staged_edit_then_reverted_on_disk`: `diff-index --cached` names the path, the disk bytes equal `HEAD`'s blob.
Second, the ident of an empty overlay is a sha1 over `base`, not `base` itself, while the published ident and "the `HEAD` tree's ident" are not defined by that formula; read literally, a clean checkout's current ident never equals the published or the `HEAD` ident.
Failure scenario: on a clean checkout (or after an editor rewrites a record with the same bytes), `lodge check --gate` prints `uncommitted record changes in lodge/; commit them before you push` and labels every problem `committed and working tree:`, where today it prints neither; Task 4's shortcut never fires in checkout mode, so the identical-state speed-up is lost silently.
Fix: drop an overlay entry whose blob equals `base`'s blob at that path (and a deletion of a path `base` lacks); define `ident` as `base`'s tree ID when the overlay is empty, else sha1 over `base` and the sorted overlay; define the published and `HEAD` idents as their tree IDs.
Tests: a clean checkout's ident equals the published ident and the `HEAD` tree ID; a touched file and a staged-then-reverted file give the clean ident; an e2e gate on a touched clean checkout prints no `UNCOMMITTED` note (compare with the output before Task 8).

## Important

### I1. d-atsx8n misses the global and system attributes files

Handle: Task 8, "d-atsx8n's check" (`git config --get-regexp '^core\.(autocrlf|attributesfile)$'`, `$GIT_COMMON_DIR/info/attributes`, `.gitattributes` in the root or under `lodge/`); d-atsx8n's "Cost if wrong: a slower read ..., never a wrong one".
Git reads `$XDG_CONFIG_HOME/git/attributes` (default `~/.config/git/attributes`) when `core.attributesfile` is unset, and `/etc/gitattributes` unless `GIT_ATTR_NOSYSTEM`.
Verified in `/var/tmp/lodge-review-opus/g2`: with `*.md text eol=crlf` in `$HOME/.config/git/attributes` and no config, the checked-out `lodge/a.md` holds CRLF, the config query prints nothing, no `info/attributes` exists, `git diff-files` names nothing, and `git check-attr` reports `eol: crlf`.
So the plan's check says "no path converts" and the listing gives the blob's LF text while today's `disk_tree` reads CRLF.
Failure scenario: Task 8's `publish` compares blob IDs; the disk bytes' blob (CRLF) never equals the listing's (LF), so every `lodge add` that edits such a record is REJECTED, where today it publishes; and `committed_gate` today sees the CRLF working tree differ from `HEAD` and prints the uncommitted note, which the new identity does not.
The same gap: `core.autocrlf` written as a git boolean (`yes`, `on`, `1`) is not "true" to a string comparison (`git -c core.autocrlf=yes config --get-regexp` prints `core.autocrlf yes`).
Also, tests run with `GIT_CONFIG_GLOBAL` empty but `HOME` unchanged, so a developer's own attributes file reaches the tests.
Fix: take the files from `git var GIT_ATTR_GLOBAL GIT_ATTR_SYSTEM` (present in git 2.56 here; `/etc/gitattributes` and the XDG path), treat any that exists as "may convert"; read `core.autocrlf` with git's boolean spellings; set `HOME` and `XDG_CONFIG_HOME` to `tmp_path` in the gitstore and e2e helpers; add `test_global_attributes_file_reads_from_disk`.

### I2. Paths git trusts its index for are read from git, not from disk

Handle: Task 8, the overlay built from `git diff-index --cached` and `git diff-files`; `src/lodge/gitstore/checkout.py:90` (`disk_tree` reads every file on disk).
Verified in `/var/tmp/lodge-review-opus/g1`: after `git update-index --assume-unchanged lodge/b.md` and an edit, `git diff-files` does not name `lodge/b.md`; the same after `--skip-worktree`.
`core.ignoreStat` sets the assume-unchanged bit on every new index entry; a sparse checkout sets skip-worktree on paths that are not on disk at all.
Failure scenario: a sparse checkout excluding part of `lodge/` reads records that are not on disk, where today they are missing and `_missing` fails the gate; an assume-unchanged record edited on disk reads as its committed text; both change a read's output and the gate's result without a product decision.
Fix: find the flagged paths with `git ls-files -v -t -- lodge` (entries in lower case or marked `S`), read them from disk like d-atsx8n's paths, and cache the result in the index keyed by `.git/index`'s stat so the warm read does not pay for it; or record the narrower behaviour as a product decision with a spec edit.
Add `test_assume_unchanged_reads_from_disk` and `test_skip_worktree_missing_file`.

### I3. Task 10: the published state's check results cannot come from a stored state as specified

Handle: Task 10, "Building a state where the published state's rows are stored: `check_change` gets `ChangeFacts` with ... its `check_state` problems from its stored state"; Task 2's `ChangeFacts.published_problems` ("sort keys of `check_state(published)`"); Task 10's `StoredState` (holds `unrecorded` only).
`StoredState` stores the unrecorded problems, not every problem of `check_state`, so the sort keys of problems at record paths are not there.
A stored state is keyed by (current ident, published ident, settings) and its results are `check_state` plus the change problems against its own published state; they equal `check_state(P)` only when that state was read with `P` as both current and published.
In checkout mode on a feature branch the published state (the merge base) is rarely ever the current state of this worktree, so a lookup by key will mostly miss, and a lookup by current ident alone would return results mixed with another comparison.
Failure scenario: a builder fills `published_problems` from the stored flags or the unrecorded list; a problem the published state already has is then reported as new in a read after one changed record (or a new one is dropped as known), and the differential test catches it only if a sample has a published problem at a record path.
Fix: a table keyed by a state's ident alone (it depends on nothing else: `check_state` and `derive` take no settings and no time, `src/lodge/core/check_state.py:26`) holding the statuses and the sort keys of `check_state` problems; write it whenever a snapshot's `derive` and `check_state` run; `ChangeFacts` for the published state reads it by the published ident.
`test_published_facts_from_rows_equal_full` must include a published state with a problem at a record path (a duplicate code, a hand-edited published decision).

### I4. Task 10: indexed results cannot equal in-memory results field for field

Handle: Task 10, `test_outputs_equal_in_memory` ("equal results") and "only the unrecorded problems are stored"; `src/lodge/app/results.py:19` (`Read.statuses`, every status of the state); `src/lodge/app/reads.py:38` (`Shown.changing`, `threads`, `confirmable`, `rests_on`, `supports`).
`Read.statuses` holds every record's status (`src/lodge/app/state.py:56`); an indexed read that fills it reads all 160,000 rows, one that does not differs from the in-memory `Read`.
The `Shown` fields the viewer reads (`src/lodge/viewer/pages.py:30` to `54`, `viewer/spec.py:75`) are not in `Row`, and the command line prints none of them (`src/lodge/cli/output.py:41`).
Failure scenario: the builder either stores all statuses per read (the 0.3 s target goes) or leaves them empty and weakens the test ad hoc; either way the plan does not say which output the equality covers.
Fix: state that an indexed `Shown`, `Listed`, `ThreadList`, `ThreadShown`, and `ThreadsWaiting` carry an empty `Read.statuses` and the viewer-only `Shown` fields at their defaults; compare the printed text of `cli/output.py` and `cli/thread_output.py` in the differential tests, not the dataclasses; add a test that a `Lodge` built with the read model refuses to serve the viewer's factory (`test_viewer_factory_has_no_read_model` exists, keep it).

### I5. The index's search candidates miss records the ranking accepts

Handle: Task 6, ranking step 3 (phrase = "substring of the lower-cased, whitespace-collapsed text") and `test_rank_over_candidates_equals_rank_over_all` ("the property Task 10 relies on"); Task 10, "candidates are the keys matching any query word or phrase word ... and for a code the keys matching every word of the code"; `src/lodge/core/words.py:93` (function words removed).
Three counterexamples to the stated property, each from the definitions:
a phrase that is not on word boundaries (`"ttled poi"` is a substring of `settled point`, its words `ttled` and `poi` are no record's words, so no candidate);
a phrase of function words only (`"of the"` has no words at all, matches by substring in memory, has no candidate in the index);
a code whose words are all function words (`A`, `NO-ONE`, `IT-A`: the grammar of `src/lodge/core/fields.py:11` allows them; `words("NO-ONE")` is empty, so "every word of the code" is an empty FTS query, which errors and per d-kj554d becomes a miss, while `citers` in memory finds every text citing `NO-ONE`).
Failure scenario: `lodge search '"of the"'` lists records from memory (with `LODGE_INDEX=off` or after an edit) and none from a seen state; s-q4s548 forbids that kind of disagreement, and d-eby5pb's "cost if wrong: a slow broad search, not a different one" does not hold.
Fix: define a phrase as a run of whole words (the `[^\W_]+` tokens of the text, function words kept, compared as a token sequence), so a phrase's non-function words are a sound candidate filter; a phrase or code with no non-function word takes `all_rows` (or the in-memory path); make the property test's generator emit partial-word phrases, function-word phrases, and function-word codes.
This is part of Task 6's product decision, so the spec edit says it.

### I6. One shared index thrashes between lodge builds, and its key omits the parser's dependencies

Handle: Task 9, "Location: `<git common dir>/lodge/index.sqlite`" and "Meta table: schema number, the package digest, and the parse format; any mismatch empties every table"; d-f3r5aq.
The git common dir is shared by every worktree of a repository.
This project itself runs two builds against one common dir: the hook and the main checkout's installed `lodge`, and `uv run lodge` in a plan worktree (`CLAUDE.md`, Build process: tasks run in their own worktree); their package digests differ.
Failure scenario: each alternation empties every table and rebuilds; at 160,000 files every read becomes a cold read (about 12 s by the plan's own table), and nothing reports why.
The key also omits what a parse and a stored state depend on besides lodge's files: the Python version (`marshal`'s format, and `str.lower` and `\w` follow the Unicode database, which changes `core.words` and so the FTS rows), PyYAML's version and whether libyaml is present (the parse itself, see B1), and SQLite's version for FTS5.
Fix: namespace by build: one file per digest (`index-<digest>.sqlite`, the two most recently used kept), or a digest column in every table with the eviction per digest; put `sys.version_info`, `yaml.__version__`, `yaml.__with_libyaml__`, and `sqlite3.sqlite_version` into the digest; replace "parse format" by those named inputs.
Add `test_two_builds_keep_their_states` (two digests alternating; the second read of each is warm).

### I7. Task 6 and Task 7: a shell-quoted argument is not a phrase, but the guide shows it as one

Handle: Task 6, `Query.phrases` ("each `"..."` in the text") and "A quoted multi-word argument is one query"; Task 7, the example `lodge search "phrase of words" --brief`.
The shell removes the quotes, so `lodge search "berth crane"` gives the query text `berth crane` with no phrase; a phrase needs `lodge search '"berth crane"'`.
Failure scenario: an agent follows the reading guide, expects contiguous matches, and gets the all-words ranking; the guide teaches the wrong model in the one command it exists to teach.
Fix: decide one of: an argument with spaces and no inner quotes ranks its whole text as a phrase first, then all words, then some (the guide's example then holds); or the guide shows `lodge search '"exact phrase"'` and says that a multi-word argument is all its words.
Either is part of Task 6's product decision; `test_guide_read_examples_run` should assert the phrase example's first result holds the phrase.

### I8. Tasks 8 and 10 are each two tasks

Handle: Task 8 (four new modules, eleven modified modules across `core`, `app`, and `gitstore`, the `Store` port replaced, four new test files plus edits to every existing test using `trees()`); Task 10 (four new modules, five new test files, two property tests, the published-facts optimisation, FTS, eviction, and expiry).
Failure scenario: a review of Task 8 has to judge a port refactor and the riskiest new correctness surface (B2, I1, I2) in one diff; a defect in the identity hides in port-renaming noise, and a fix round reopens both.
Fix: split Task 8 into 8a, the port moves to listings and texts with the checkout identity computed from a full disk read (the ident a hash of every file's blob, as slow as today and obviously sound), proven by the existing tests unchanged in substance; and 8b, the cheap identity (git's differences, the walk, attributes, flagged paths) with the identity tests, each comparing with 8a's full-read identity as the oracle.
Split Task 10 into 10a, rows, answers, expiry, and the four non-search reads; 10b, FTS candidates and indexed search with the candidate property; and 10c, the published facts from stored results (I3), which is only an optimisation of the changed-record read and needs its own proof.
Task 9 is the right size.

## Minor

### M1. Task 10: expiry compared as text, and a clock set back

Handle: Task 10, `StoredState.expires: str | None` and "at or after it the state is rebuilt".
Decision dates carry offsets, so a string comparison with `clock.now()` in another offset is wrong; and a state built at time T that the clock later precedes (an NTP step back) keeps a result in which `_dates` (`src/lodge/core/check_change.py:66`) would now fail a decision.
Fix: store `built` and `expires` as ISO datetimes, compare with `datetime.fromisoformat`, and treat `now < built` as expired; one test each.

### M2. Task 5: errors "in place" are not in place when standard output is a pipe

Handle: Task 5, "a ref that fails prints `----- B` then `lodge: <the error>` on standard error in place".
With standard output piped, Python buffers it by block and standard error by line, so in `lodge show A B C 2>&1` the error lines come first.
Fix: flush standard output before each error line, or print the error under its separator on standard output and a one-line summary on standard error; test with the streams merged.

### M3. Task 5: `cites` casefolds while `core.words` lower-cases

Handle: Task 5, `cites` ("code, casefolded, as a whole token"); `src/lodge/core/words.py:93` (`text.lower()`).
`"ſ-1".casefold()` is `s-1` and the Kelvin sign casefolds to `k`, so `cites` accepts a text whose words (`ſ`, `1`) do not include the code's word `s`; the index's every-word candidate filter then misses a citer that memory finds.
Fix: `cites` compares with `.lower()`; codes are ASCII (`src/lodge/core/fields.py:11`), so nothing else changes.

### M4. Task 10: no registry in `core/codec.py`

Handle: Task 10, Files ("`src/lodge/core/codec.py` (app's result classes registered by `app`, not imported by `core`)"); Task 9, `from_plain(plain, classes)`.
`from_plain` already takes the classes, so a registration hook adds module state to `core` for nothing.
Fix: `app` passes `{**CORE_CLASSES, **APP_CLASSES}`; drop `codec.py` from Task 10's files.

### M5. Task 4: the identical-state test's samples omit the checks the proof argues away

Handle: Task 4, `test_check_change_of_a_state_with_itself_is_empty`; d-zyqzkg.
The proof argues `_dates`, `_unlisted_sources`, and the link-only branch of check 4 away; the listed samples hold none of a future-dated decision (with `now` before its date), an imported record from a source not in `[import] sources`, or an entry whose decision lists `link`.
Fix: add those three snapshots, so a later change to those checks that breaks the proof fails the test.

### M6. Task 9: `synchronous=OFF` and a gate that trusts the parse cache

Handle: Task 9, `synchronous=OFF`; Task 9, "`app` builds every snapshot (reads, the gate, `add`, ...) as `assemble` of cached parses".
SQLite documents that with `synchronous=OFF` an operating-system crash or power loss can corrupt the database; a page that still decodes to a valid but wrong parse would reach the gate, which d-1bww1r keeps exact.
Fix: `synchronous=NORMAL` for the parses table's transactions (writes only, reads unaffected), or let the gate verify a parse row by a checksum stored beside it.

### M7. Task 11: the order of `stat`, listing, and the listing time; the FUSE disk

Handle: Task 11, "whose row's `ctime_ns` is at least 2 s before the time the row was listed"; d-8kq2nk.
The racy rule is sound only if the recorded `stat` is taken before `scandir` and the listing time after both; the plan does not fix the order.
The rule's premise (a folder's ctime changes on every entry added or removed) is tested only in `tmp_path` on native disk, while the author's working trees are on NTFS through FUSE (brief, timings).
Fix: state the order; run the Task 11 tests once on the FUSE disk and record the result in the report, falling back to the walk on a file system where they fail.

### M8. Task 6: `(k already listed)` hides which records

Handle: Task 6, "a record already printed under an earlier query left out and counted in `(k already listed)`".
An agent cannot tell which of a later query's best matches were listed above without re-reading both lists.
Fix: name them on the header line, `query: Q2 · 7 matches · also d-xxxxxx, d-yyyyyy above`; and say whether a left-out record counts toward `--limit`.

## Checked and sound

- Task 4's proof against the code: for equal snapshots `check_entries` (`src/lodge/core/check_entries.py:13`) finds no wanted action and iterates no new decision, `check_immutable` (`check_immutable.py:16`) compares equal values, `_links_to_dead`'s entry half finds no new `rests_on` target, `_missing` finds every ID; `read_checked` re-sorts by the same key `check_state` sorts by (`check_state.py:40`), so the problem order is unchanged; `Tree.rev` is unused by `load` (`snapshot.py:51`), so equal `(files, attachments)` means equal snapshots.
- d-f3r5aq's claim that only `_dates` reads the time: `grep` of `src/lodge/core` finds no other comparison with a clock value.
- Task 2's Tarjan rewrite matches `check_cycles` (`check_cycles.py:9`): today's `others` is the strongly connected component without `i`, and a self-link alone yields nothing.
- The settings a stored state depends on are the core settings only: `.lodge.toml`'s store section decides which states are compared, and those reach the key through the idents (`src/lodge/gitstore/settings.py:14`).
- Symbolic links: a git blob of a link is its target text, as `_read` reads it today (`checkout.py:110`), so a tracked link reads the same from git.
- The package digest from name, size, and mtime: `uv pip install` gives install-time mtimes (checked on a wheel built from this branch, whose entries carry 1980 timestamps), so a reinstall changes the digest.
- Core purity and confinement: the new `core` modules use only `CORE_MODULES` (`hashlib` for `blob_id`), `marshal` and `sqlite3` stay in `gitstore` and `app`, and `gitstore` importing `app` for `Row` and `StoredState` is an allowed edge (`tests/structure_tables.py`).
- Product decisions: Tasks 5, 6, 7, and 9 each record one with a spec edit; Tasks 2 and 4 change no output; Tasks 3 and 8 change output without one (B1, B2, I1, I2), and Task 6's phrase definition needs I5 and I7 in its decision.

## Files read

Read: the plan, its ledger, `brief.md`, `plan-report.md`, `questions.md`, `review-brief.md`; decisions d-zyqzkg, d-f3r5aq, d-8kq2nk, d-atsx8n, d-c400w8, d-eby5pb, d-m0g9tx, d-1bww1r (through `lodge show --reasoning`); `src/lodge/app/state.py`, `app/reads.py`, `app/results.py`, `app/ports.py`, `core/check_change.py`, `core/check_state.py`, `core/check_entries.py`, `core/check_immutable.py`, `core/check_cycles.py`, `core/check_areas.py`, `core/views.py`, `core/search.py`, `core/words.py`, `core/yamlio.py`, `core/snapshot.py` (to line 80), `core/document.py` (to line 42), `core/settings.py`, `core/model.py` (field lists), `gitstore/checkout.py` (to line 120), `gitstore/trees.py`, `gitstore/published.py`, `gitstore/settings.py` (store section), `cli/output.py`, `main.py`, `tests/structure_tables.py`, and the purity rules in `tests/structure_calls.py` by search.
Not read: `probes/*.py` (their numbers taken from `plan-report.md`), `core/derive.py`, `core/fileformat.py`, `core/fields.py` beyond line 11's grammar as the plan cites it, `app/writes.py`, `app/threads.py`, `app/confirm.py`, `gitstore/branch.py`, the viewer beyond the lines cited, `lodge spec` in full, and `plan-review-codex.md` (by instruction).
Not run: a timing of any kind (the other reviewer's angle), the Task 11 premise on the FUSE disk (M7).

## Counts

Blocking 2, Important 8, Minor 8.
1. B1: libyaml with a fallback on exceptions accepts headers today's loader rejects (`title: x<TAB>`), so a check 1 failure disappears; 2,516 of 200,000 fuzzed headers parse under C only.
2. B2: the checkout identity puts stat-dirty and reverted paths in the overlay and never equals a tree ID, so the gate prints the uncommitted note on a clean or touched checkout and Task 4's shortcut never fires.
3. I3 with I5: the index path is not provably equal to memory: the published `check_state` problems are not in `StoredState`, and FTS candidates miss partial-word phrases, function-word phrases, and function-word codes.
