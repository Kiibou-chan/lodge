# Plan recheck: lodge at scale, fix round 1, correctness and design

Rechecker angle: correctness and design (Opus), against `plan-review-opus.md`.
Plan at `dea8dcb` on `read-speed`; the fix round is `git diff 7aaef43 dea8dcb`, mapped in `plan-fix-1.md`.
Decisions read through `lodge show --reasoning`: d-q051s2, d-q0tb8r, d-rs76ks, d-rvf532, d-ty4dks, d-vmpspc, d-ytf272, d-7e8zhd, d-ana6c0, d-c5a1y4, d-dqpf59, d-dxqxsn, d-emtwbs, d-faakge, d-her016, d-me8vm3, d-26e6zj (saved in `/var/tmp/lodge-recheck-opus/decisions.txt`).
Probes in `/var/tmp/lodge-recheck-opus/` (`probe/guard.py` is Task 3's guard read literally from plan lines 171 to 177; `probe/gfuzz.py SEED N` compares the two loaders on admitted headers; `probe/cases.py` the single cases below; `g3/` a git probe), each run from the worktree with `uv run --frozen --quiet python <probe>`.
Line numbers below are of `docs/superpowers/plans/2026-10-31-lodge-at-scale.md` at `dea8dcb`.

## Status of the earlier findings

### Blocking

- B1, libyaml fallback changes check results: **fixed**, lines 171 to 179, d-q051s2.
  Verified: the guard as worded, run over 360,000 generated headers built from the writer's shapes with mutations (`probe/gfuzz.py`, seeds 1 to 4), admitted 299,543; on none of them did the C loader succeed where the Python loader failed, and on none did both succeed with different values.
  Every C failure on an admitted header falls back (line 178), so the value or error is today's.
  The fix's test wording is new trouble, see N1.
- B2, the checkout identity changes the gate's output: **fixed**, lines 25, 349, 375 to 376, d-q0tb8r, d-ana6c0, d-7e8zhd.
  The gate and `add` keep exact trees (`committed_gate` untouched), and the fast identity is `base` when the overlay is empty, with touched and reverted paths dropped by hash (tests at line 384).

### Important

- I1, global and system attributes: **fixed**, lines 33, 378, 386, d-dqpf59.
  A residual gap in the attribute list is N5 (Minor).
- I2, paths git trusts its index for: **fixed**, lines 375, 377, 385, d-c5a1y4; Task 8a's `disk_tree` hashes what it read (line 348, `test_disk_tree_ignores_assume_unchanged`).
- I3, published check results from a stored state: **fixed**, lines 465 to 467 (`StateFacts` keyed by ident alone), 541 to 547, d-dxqxsn.
  A retention ambiguity is N6 (Minor).
- I4, indexed results cannot equal in-memory results field for field: **fixed**, line 489, d-rs76ks; equality is on printed text, `Read.statuses` empty, viewer-only fields at defaults, the viewer off the read model (lines 448, 499).
- I5, candidates miss records the ranking accepts: **fixed**, lines 270 to 272, 286, 296, 522, d-emtwbs.
  Checked against `src/lodge/core/words.py:5` and `:91`: `Query.tokens` and `core.words` share the `[^\W_]+` tokenizer, so a phrase's non-function words are a sound candidate filter, and a code such as `A-1` keeps the word `1`.
  A residual wording gap is N8 (Minor).
- I6, one shared index thrashes between builds: **fixed**, line 421, d-rvf532, d-faakge (one file per digest of source bytes, Python, PyYAML, libyaml, SQLite, schema).
- I7, a shell-quoted argument is not a phrase: **fixed**, lines 268, 290 to 291, 298, 314, 317, d-ty4dks, d-emtwbs.
- I8, Tasks 8 and 10 are each two tasks: **fixed**, Tasks 8a, 8b, 10a, 10b, 10c, d-vmpspc.
  Task 8a took a different cut from the one suggested (exact trees gain blob IDs and `trees()` stays, d-7e8zhd), which is simpler and keeps the exact oracle.

### Minor

- M1: **fixed**, lines 471, 488, 496.
  Checked against `src/lodge/core/check_change.py:71`: `_dates` compares `datetime.fromisoformat(d.date) > now`, so a half-open interval from the latest new date not after the build to the earliest after it holds every result constant.
- M2: **fixed**, lines 238, 247.
- M3: **fixed**, lines 237, 245.
- M4: **fixed**, line 411.
- M5: **fixed**, line 202.
- M6: **fixed as proposed**, lines 422, 437; the proposal itself left a residue, N7 (Minor).
- M7: **fixed**, lines 562, 568.
- M8: **fixed**, line 290.

## New findings

### N1. Important. Task 3: the fuzz test's "both succeed with equal values or both fail" cannot hold for admitted headers

Handle: line 184 (`test_admitted_headers_parse_the_same`: "for every admitted header both loaders succeed with equal values or both fail", the generator including "surrogate pairs"); line 178 (any C exception falls back).
Verified with `probe/cases.py`: `title: "\ud83d\ude00"` (a JSON surrogate-pair escape, which the guard admits by its `\uXXXX` rule) fails under libyaml with `ScannerError` and parses under the Python loader to the emoji; `order: [a:, b]` (PLAIN admits a trailing `:`) fails under C and parses under Python to `[{'a': ''}, 'b']`.
`probe/gfuzz.py` found such C-fails, Python-succeeds headers in about 5 per cent of admitted headers (2,580 of 49,827 at seed 1).
`load_yaml` is still right on them, because the C exception falls back; only the test's first clause is wrong, and it is stronger than the review's B1 asked for (one direction).
Failure scenario: the builder's test fails on the first surrogate-pair escape; to pass it the builder either narrows the guard ad hoc or rewrites the assertion, and the plan's one oracle for Task 3 is changed without review.
Fix: assert one direction, "for every admitted header on which the C loader succeeds, the Python loader succeeds with an equal value", plus the existing "for every header `load_yaml` equals today's loader in value or in `YamlError` message and line"; optionally narrow the guard so `\uD800` to `\uDFFF` escapes and a PLAIN ending in `:` are not admitted, which the writer never produces (it writes `json.dumps(..., ensure_ascii=False)`, `src/lodge/core/yamlio.py:82`), and keep `test_c_loader_used_for_admitted_headers` honest.

### N2. Important. Task 8b: the property "idents agree exactly when exact trees are equal" is false for the plan's own identity

Handle: line 387 (`test_random_edits_agree`: "two states agree in ident exactly when their exact trees are equal", with `commit` among the operations); line 376 (the identity: `base` when the overlay is empty, else `sha1(base + overlay)`); line 384 (`test_attachment_bytes_changed_keeps_the_ident`); d-ana6c0 ("an attachment counts by presence only").
The identity is canonical only for the empty overlay.
An unstaged edit gives `sha1(base0 + "lodge/x.md\0<b>")`; committing it gives the new tree ID `base1`; the exact tree is the same in both, the idents differ.
Likewise an attachment whose bytes change and are committed changes `base` while the exact tree (attachments by presence) is unchanged.
Only one direction holds: equal idents imply equal exact trees, which is what every consumer needs (Task 4's shortcut at line 487, the state key at line 470, the facts key at line 465), since an unequal ident for an equal tree costs a rebuild, never a wrong read.
Failure scenario: the first seeded sequence holding an edit then a commit fails the test; the builder either weakens the property test that Review Focus 2 rests on, or makes the identity canonical at a cost the plan did not budget (a `git mktree` of the applied overlay on every read).
Fix: state the property as "equal idents imply equal exact trees", and keep the named canonical cases as separate assertions (clean, touched, staged then reverted on disk: ident equals `base`; line 384's first three tests).

### N3. Important. Task 10b: a cached parse whose words rows were dropped is never a search candidate again

Handle: line 509 ("words rows dropped with the last state that uses them"); line 517 (`keep_words`); line 429 (a snapshot is built from cached parses "plus `parse_file` of the misses, and keeps the misses"); line 522 (candidates are the keys the FTS table returns); parse rows have no eviction anywhere in Tasks 9 to 11.
Words rows are evicted with states, parse rows are not, and the plan does not say that building a state writes words for every key of its rows that lacks them.
If `keep_words` follows the parse misses, as "keeps the misses" invites, a key whose parse is cached but whose words were dropped never returns to the FTS table.
Failure scenario: record `r` at blob `b1` is in state S1; an edit to `b2` and four further states evict S1 and with it the words of `(r, b1)`; the edit is reverted on disk (or the branch moves back), so the new state holds `(r, b1)`, a parse-cache hit; `lodge search <a word of r>` lists `r` with `LODGE_INDEX=off` and omits it through the index.
The read's "less than the state promised" fallback (line 486) cannot see this, since an FTS miss is a valid answer.
The property test at line 529 lists no revert and runs 60 steps, so it reaches this only by chance.
Fix: make the words rows part of the parse cache's lifecycle (written with every parse, dropped only with it), or have `keep_state` write words for every key of its rows that has none, in the same transaction; add `test_revert_after_eviction_is_found` (edit, `KEPT_STATES + 1` further states, revert, search), and add revert to line 529's operations.

### N4. Important. Task 10a: `show` of a coded record needs its citers, which no 10a lookup provides

Handle: lines 226 to 227 and 241 (Task 5: `show` prints up to ten citers and a count of the rest, `citers` scanning every record's title and statement); line 486 (an indexed `show` answers through "one bucket per ID, the parse rows of the records printed"); line 473 (`StoredState.codes` gives the family only); line 496 (`test_outputs_print_as_in_memory` includes `show` of codes); the word candidates arrive only in Task 10b (line 518).
Citers are not among the records printed in full, and finding them needs every record's text or a word index; 10a has neither.
Failure scenario: the builder of 10a either reads `all_rows` and every parse's text for each coded `show` (the 0.3 s target for `show {code}`, the first line of `scripts/bench_reads.txt`, goes) or invents a fallback the plan does not name; either way 10a's interface is incomplete for the read it owns.
Fix: add `citing: Mapping[str, tuple[str, ...]]` (lower-cased code to citer IDs, newest first by `(date, ID)`) to `StoredState`, computed when a state is built (one pass over each record's tokens against the set of codes, linear), and use it in both `show` and Task 10b's code queries in place of the "every word of the code" candidates; or say that 10a's `show` of a record with a code runs in memory until 10b, and name the test that proves it.

### N5. Minor. Task 8b: the deprecated `crlf` attribute converts, and the plan's `check-attr` does not ask for it

Handle: line 378 (`git check-attr --stdin -z text eol filter ident working-tree-encoding`); d-dqpf59; d-atsx8n ("never a wrong one").
Verified in `/var/tmp/lodge-recheck-opus/g3` with git 2.56: `lodge/*.md crlf` in `.git/info/attributes` and `core.eol=crlf` check out `lodge/a.md` with CRLF; `check-attr` reports `text`, `eol`, `filter`, `ident`, and `working-tree-encoding` all `unspecified` and `crlf: set`; `git diff-files` names nothing.
Failure scenario: the path is read from git as LF while `disk_tree` reads CRLF; an indexed `show` prints what the gate does not see, against line 26.
Fix: add `crlf` to the attributes asked for (git still honours it as the old spelling of `text` and `eol`), and add a case to `test_text_attribute_on_one_pattern`.

### N6. Minor. Task 10a: "facts kept for the idents of kept states only" may drop the published facts 10c needs

Handle: line 491 ("facts kept for the idents of kept states only"); line 543 (10c stores the published snapshot's facts); line 470 (a kept state's key is a hash of two idents).
A kept state has a current and a published ident; if "the idents of kept states" is read as their current idents, the published state's facts (in checkout mode the merge base, rarely any state's current) are evicted in the transaction that writes them, and 10c never hits.
The result is still correct (absent facts are computed, line 547), so the cost is the optimisation, silently.
Fix: say "the current and published idents of kept states", and add to `test_absent_facts_are_computed_and_kept` that the published facts survive the `keep_state` that wrote them.

### N7. Minor. Task 9: `synchronous=NORMAL` in `DELETE` journal mode still risks a torn database on power loss

Handle: line 422 (journal mode `DELETE`, `synchronous=NORMAL`); line 437 (the gate trusts a parse row keyed by hashed bytes).
SQLite documents `NORMAL` as corruption-safe in WAL mode only; in rollback-journal mode a power failure at the wrong moment can still corrupt the file.
The review's M6 proposed `NORMAL` without that distinction, so the fix inherits the gap.
The parse key guards against a wrong key, not against a damaged page that still decodes to a valid parse under the right key.
Fix: `synchronous=FULL` for write transactions; a seen read writes nothing (line 497), so the extra sync falls only on reads that already parse and build, and it costs one `fsync` per transaction.

### N8. Minor. Task 6: a words query whose words are all function words is not defined

Handle: line 286 ("for words: records holding every word, by score"); line 272 (`needs_memory` covers a phrase or a code token with empty words, not a multi-word plain query); today's behaviour at `src/lodge/core/search.py:73` (only records with a score above 0 rank, so `search "of the"` finds the exact ID or code only).
For `lodge search "of the"` (two words, not a code token, not `--phrase`) every record "holds every word" of the empty set, so a literal reading lists all records in memory, while the index's candidates (keys holding any query word) are empty.
`test_rank_over_candidates_equals_rank_over_all` would catch the disagreement only if its generator emits such a query.
Fix: say that steps 3 and 4 apply only when `words` is non-empty, as today, and add `of the` (unquoted) to the property test's seeds and to `test_search_prints_as_in_memory`.

### N9. Minor. Task 9: pruning other builds' files should take their journals with them

Handle: line 421 (other builds' files deleted on opening).
A file deleted beside a hot `-journal` (a writer killed mid-transaction) leaves the journal; when that build next creates its file under the same name, SQLite rolls the stale journal into the new file.
Failure scenario: the rebuilt file is corrupt, which d-her016 detects and rebuilds again; a cost, not a wrong read, unless the rolled-back pages decode.
Fix: delete `index-<digest>.sqlite-journal` with its file, and skip a file whose journal exists and is locked.

## Checked and sound in the revised tasks

- Task 3's guard admits every line shape the writers produce: `_decision_header`, `_spec_header`, `_imported_line`, and `write_area` (`src/lodge/core/fileformat.py:57`, `:123`, `:129`, `:164`), and `write_thread`'s header and message blocks (`src/lodge/core/threads.py:106`); `rank` is a non-negative whole number (`src/lodge/core/fields.py:147`), so it matches PLAIN.
- Task 8a's parse key is sound for both kinds of tree: a parse depends on the path and the text, the text is a function of the bytes, and a committed blob's object ID is `blob_id` of its bytes; a link hashes its target bytes as git stores them.
- Task 10a's two-ident key suffices: `read_checked` compares exactly two trees and calls `check_change` without `current` (`src/lodge/app/state.py:66`), and no read but `check_change` reads the clock (`grep clock src/lodge/app`: `confirm.py`, `threads.py`, and `writes.py` are writes; `reads.py:85` is the gate).
- Task 10c's facts keyed by ident alone: `check_state` and `derive` take the snapshot only, and equal idents imply equal snapshots (N2's one direction).
- Task 6's `needs_memory`: a plain function word such as `the` is also a code token, so it takes the memory path too; with N8 settled, every query kind has a sound candidate set.

## Files read

Read: the plan at `dea8dcb` in full, `plan-fix-1.md`, my `plan-review-opus.md`, the seventeen decisions listed above, `src/lodge/core/yamlio.py`, `core/fileformat.py` (writers), `core/threads.py` (`write_thread`), `core/fields.py` (to line 30, `read_rank`), `core/words.py` (tokenizer), `core/search.py`, `core/check_change.py` (`_dates`), `app/state.py`, `app/reads.py` (to line 110), `app/results.py` (to line 60), `app/threads.py` (lines 40 to 80), `gitstore/checkout.py` (`freshness`, `gate`, `publish`).
Not read: the ledger's diff, `plan-review-codex.md`, `plan-recheck-codex.md` (by instruction), `probes/*.py`, `gitstore/trees.py`, `gitstore/published.py`, the viewer.
Not run: any timing (the other rechecker's angle); the N3 and N4 scenarios are argued from the plan's text, since the code they concern does not exist yet.

## Counts

Earlier findings: Blocking 2 of 2 fixed; Important 8 of 8 fixed; Minor 8 of 8 fixed (M6 as proposed, with the residue N7).
New findings: Blocking 0, Important 4, Minor 5.
Most important: N3, Task 10b drops a parse's words rows with the last state that uses it but never drops the parse, so after an edit, four more states, and a revert, a search through the index omits a record that the in-memory search lists.
