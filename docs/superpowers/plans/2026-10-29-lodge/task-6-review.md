# Task 6 review: search, references, level views, readable specification

Commit 7a51397 (base c11448c), reviewed read-only.
Probes ran in a scratch copy (`git archive 7a51397`) at `scratchpad/probes-t6/src`, with its own `uv sync --offline` environment.
`sh scripts/check.sh` in the scratch copy: green, 566 passed.
Probe scripts: `scratchpad/probes-t6/probe.py` (must-not 1, through real file loading with `load(Tree(...))`, `check_state`, `failing_ids`), `scratchpad/probes-t6/probe2.py` (ties, `related`, codes); outputs beside them as `probe-out.txt` and `probe2-out.txt`.

## Verdicts

Spec compliance: no.
Gaps: the quote is not at level 1 (spec:174), and several level-1, level-2, and rendered views read more settled than `Derived` and the check say (must-not 1, spec:57 and spec:63).
Task quality: not approved (1 Blocking, 6 Important, 5 Minor).

## Pass 1: correctness

### B1 (Blocking): her quote is not at level 1, which the spec gives as the safeguard for LODGE-2

Handle: spec:174 says "the required quote, with where and when, shows at level 1, so a wrong attribution is visible to her"; `Level1` (views.py:19-33) has no quote, and `format_level1` (views.py:122-123, 142-147) prints none.
Probe P6: an author decision reads `d-aaaaaa · current · author · 2026-10-28 · product`, then title and statement; the quote appears only in `format_level3`.
Failure: an agent writes `decided_by: author` with an invented quote; every default read and every search result shows "author" and nothing she could recognise as not hers, so LODGE-2's "trust the label" loses the one check the spec pairs it with.
The plan's interface (plan:283-286) and the brief omit the field, so the builder followed the brief; the plan contradicts the spec here, and the spec governs (`CLAUDE.md`: "the plan argues from it, never over it").
Fix: `Level1` gains `quote: Quote | None`; `format_level1` prints, after the statement, `quote: "<text>" (<where>, <when>)` when present; for an entry, the quote of its newest changing decision when that decision is the author's.
This changes the plan's interface, not the spec, so a coordinator ruling suffices; Tasks 8, 10, and 11 consume `Level1` and should get it before they are built.

### I1 (Important): the rendered specification shows flagged, failing, and imported entries as settled text

Handle: render.py:20-33 (`_area_blocks`, `_entry_block`) prints `## <title> (<id>)` and the statement, with no flag.
Probe P3: an agent decision edits an entry whose previous change was hers; `level1` reads `· coordinator · ... · awaiting the author`, while `render_spec` prints `## Store (s-aaaaaa)` and the agent's text with no mark.
Probe P3b: an entry failing check 7 (missing from its area's order) is in `failing_ids` and renders the same plain block.
Failure: she reads the specification in the viewer (`/spec`) or through `lodge spec` and takes an agent's unreviewed rewrite of her entry as the settled specification, the case must-not 1 names.
The format is the plan's (plan:307), so this needs a ruling.
Fix: `render_spec` takes `failing` like `level1`, and an entry carrying any of `awaiting the author`, `imported`, or `fails check` renders as `## <title> (<id> · <flags>)`; the viewer's `spec_page` already renders headings, so no Task 11 change beyond passing `failing`.

### I2 (Important): a failing decision does not mark the views that borrow from it

Handle: views.py:91 builds the level-2 heads with `frozenset()`, so they never say `fails check`; views.py:68-69 and 79-80 give an entry the `decided_by` and `date` of its newest changing decision without looking at whether that decision fails.
Probe P5: an author decision without a quote (check 3) creates an entry; `failing_ids` = `{d-hhhhhh}`; the entry's level 2 prints `d-hhhhhh · current · author · 2026-10-28 · product` with no `fails check`, and the entry's level 1 reads `· author ·` with no flag.
Failure: the entry reads as hers, on the strength of a decision the check says lacks the quote that makes it hers.
The builder raised the level-2 half (report, call 9); it is a must-not 1 gap, not a stylistic choice (spec:63, "a record failing the check is shown as failing").
Fix: `level2(s, d, record_id, failing)` passes `failing` to the heads; an entry whose newest changing decision is in `failing` carries the flag `decision fails check` after `fails check` in the order.
Both are signature or order changes to the plan's interface, so a ruling.

### I3 (Important): a duplicate ID hides a file and leaves the kept record unmarked

Handle: snapshot.py:84-86 files the check-2 problem under the second path only; views.py:48-51 maps problems to records by path, so the kept record is not failing.
Probe P1: two files carry `d-aaaaaa` with different statements; `failing_ids` = `[]`, and level 1 shows `A holds.` with no flag; the other file appears only as an unrecorded problem.
Failure: which file is "the" record depends on sort order of paths; a reader sees one of two contradictory statements as plainly current.
Fix: `failing_ids` also marks a record whose path a problem of check 2 names in its message (the message holds both paths), or Task 4's `load` emits the duplicate problem against both paths; add `test_duplicate_id_marks_kept_record_failing`.

### I4 (Important): an unparsable decision file silently removes its links, so what it touched reads settled

Handle: views.py:54-57 reports the file as unrecorded, and nothing else; `derive` never sees the decision, so statuses, `changed_by`, and flags are computed without it.
Probe P2: her decision creates an entry, an agent decision edits it; with the agent file parsing, the entry reads `· coordinator · ... · awaiting the author`; with one YAML character broken in the agent file, the same entry text reads `· author ·` with no flag.
Probe P2b: an agent decision replacing hers fails to parse; hers reads `current`, unflagged.
Failure: the entry shows the agent's text attributed to her, which is wrong information, not missing information; the plan's answer (plan, Task 8: `Read.unrecorded`, one `problem:` line per read, a banner count in the viewer) sits apart from the record and does not correct its level-1 line.
This is the "record a failing file hides" case; the fix needs a decision on behaviour, so a ruling.
Options: (a) every level-1 view carries `unreadable decisions: <n>` while any `lodge/decisions/` file is unrecorded, cheap and honest, noisy only while the store is broken; (b) `load` keeps the record IDs found by pattern in an unparsable file's text, and `level1` flags those IDs `touched by an unreadable file`, precise but a Task 4 change.
Recommendation: (a) now, since a broken decision file fails the gate and should be rare and short-lived.

### I5 (Important): a query with no letters returns every record as if it matched

Handle: search.py:55-56 lists everything when `_words(query)` is empty, which is true for `42`, `2026`, `%`, and `--`, not only for the empty query.
Probe P4: `search(s, d, "42", Filters())` returns both decisions, the one whose statement holds `42` and the one that does not, newest first.
Failure: an agent looking for the decision behind a results number gets a list of every record presented as hits.
The ledger's search ruling (digits become words) fixes `42` and `2026` but not `%` or a query made only of function words, which would then list everything, against the ruling's own stated cost ("falls back to the exact ID or code match").
Fix: list by filters alone only when `query.strip()` is empty; otherwise a query without searchable words returns only the exact ID or code match; add `test_search_without_words_returns_exact_match_only`.

### I6 (Important): an entry whose newest changing decision is replaced or narrowed reads settled

Handle: views.py:68-69 takes who and date from `changed_by[0]` without its status; `_flags` (views.py:150-169) looks only at the entry's own links.
Probe P7: `d-kkkkkk` edits `s-cccccc`, `d-mmmmmm` replaces `d-kkkkkk` without touching the entry; the entry reads `s-cccccc · current · author · 2026-10-28 · storage`, no mention that its basis is replaced.
Failure: the entry states what a superseded decision decided, and level 1 gives no hint; must-not 1 names "a short entry reading more settled than it is".
Fix: an entry whose `changed_by[0]` is replaced or narrowed carries `basis replaced by <ids>` or `basis narrowed by <ids>` after `retired by` in the order; alternatively, or as well, a Task 7 feedback rule on a decision that replaces one with `changes` but changes none of those entries.
The spec is silent on this case, so a ruling.

### Minor

- M1: `awaiting the author` on a touched record does not name the decision that waits (views.py:161-162); an entry reads `· awaiting the author` and its level 3 lists `changed by` with statuses but not flags (probe P9). Fix: `awaiting the author on <ids>` from `touched_by_flagged` for touched records, the bare text for the flagged decision itself. The spec (spec:171) is met either way.
- M2: search ties put the smaller ID first (search.py:49-54, stable sort on `_when` with `reverse=True` over ascending IDs; probe2: `['d-aaaaaa', 'd-bbbbbb']` at equal dates), against the ledger's rule "newest-first order with ties by larger ID" (progress:61) that `derive` follows. Fix: sort by `(_when(v), v.id)` with `reverse=True`.
- M3: `level3` drops the action of `changes` (views.py:103), so a retire and an edit read alike except through the target's status. Fix: relations `changes (create|edit|retire)` in the existing string slot.
- M4: an entry with no changing decision and no import shows no who at all (views.py:79, `_head` drops `None`; probe P8: `s-dddddd · current · storage`); spec:63 says every level-1 view carries who decided. Fix: `no decision` in the who slot; the state only arises before the gate, so Minor.
- M5: `Filters.area` excludes every decision (search.py:100), so the viewer's area filter never shows the decisions behind an area's entries. The builder's reading is defensible (spec:178 does not define a decision's area); a decision could match an area when an entry in its `changes` is in it.

## The builder's points, against the spec

1. `related` met by function words: confirmed (probe2: `related(a)` returns `d-bbbbbb` for "The cache is small." and "The queue is long."); the ledger ruling fixes it.
2. `area` entries only, `scope` decisions only: acceptable reading; M5.
3. Empty query lists everything: right for the empty string, wrong for a letterless one; I5.
4. Digits split words: the plan's literal text, and the ruling overturns it; within the coordinator's authority since the spec leaves "The search ranking" to the builder (spec:301).
5. `awaiting the author` on both: matches spec:171; M1 for naming.
6. `level2` of an entry omits `fails check`: a must-not 1 gap; I2.
7. Level-3 links carry no action: M3; status `unknown` for a missing target is honest, and the decision itself fails check 2, so `fails check` shows at its level 1.

## The ledger ruling on search words (progress:84)

It holds: the spec leaves ranking to the builder (spec:301), and both defects it names are real (probe P4 and probe2).
Two conditions for the fix round.
First, the empty-query listing must key on `query.strip()`, not on the word set, or a query of function words lists every record (I5), contradicting the ruling's stated cost.
Second, `related` should drop pure-digit tokens from its query: with digits as words, two statements carrying the same date (`2026`, `10`) or small numbers reach the threshold of 2 as the function words did; search keeps them, since a number is a fair query.

## Pass 2: practice

No duplication beyond the `_passes` and `level1` reuse, which is the right sharing.
`search` builds a `Level1` for every record per call (search.py:49-53) and `related` again (search.py:67-72); fine at hundreds of records (spec:301), worth a note if Task 11's timeline calls it per request.
Comments and docstrings state facts.
Tests: the brief's 17 plus 6 extras, each asserting exact flags or text; `test_failing_ids_maps_paths` uses synthetic `Problem`s rather than `check_state` output, so it did not catch I3; add one test through `load` and `check_state`.
Module sizes: views.py 183, search.py 102, render.py 33, test_views.py 236, all under 300.

## Pass 3: design

`search` depending on `views.level1` for filtering keeps one definition of status, who, and area; good.
The plan's `level2(s, d, record_id)` and `render_spec(s, d, area)` lack `failing`, which is the root of I1 and I2; the plan's must-not 1 answer (spec:63) is carried by `level1` alone, and every other view that prints a record needs the same input.
Plan rule no test enforces: "flags, in this order" is tested on pairs, not on the full order; a test with a decision both narrowed, awaiting, imported, and failing would pin it.

## Files

Read: `.claude/agents/reviewer.md`; `CLAUDE.md` (dispatch context); task-6 brief and report; progress ledger `Ruling:` lines and lines 78-84; spec lines 1-200 and 270-310; plan lines 15-72, 197-340, and the Task 8 to 11 lines naming level views; at 7a51397: `src/lodge/core/{search,views,render,derive,snapshot,model,check_state,check_areas,__init__}.py`, `tests/core/builders.py` (lines 1-80), `tests/core/test_views.py` (lines 1-140), the test names in `test_search.py` and `test_render.py`.
Not read: the review package diff (I read the same files at the commit), `test_search.py` and `test_render.py` bodies, `test_views.py` after line 140, `fileformat.py`, `drafts.py`, `check_change.py`, spec lines 200-270.
