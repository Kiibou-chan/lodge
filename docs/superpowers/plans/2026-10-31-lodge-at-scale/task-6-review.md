# Review of Task 6 (commit 61d2629, branch read-speed-build)

Reviewer worktree: /var/tmp/lodge-review-t6/wt (detached at 61d2629); the old build is `git archive ea92261` in /var/tmp/lodge-review-t6/old with its own environment.
Read against d-e8pdqe, d-ty4dks, d-emtwbs, d-n9w4by (narrowed by d-aej8rs), d-p60ka9, d-3g6ard, d-fqymzm, d-y94v0n, the plan's Global Constraints, Task 6, and Task 10b, and the coordinator's M3 ruling in brief-t6.md.
Nothing was run in /var/tmp/lodge-build; the old build was never run on s90000.

Counts: 0 Blocking, 1 Important, 9 Minor.

## Correctness pass: what was checked and holds

- Ranking order (src/lodge/core/ranking.py:39-77): exact ID (lower-cased), then for a code token with a non-empty family the family in `family` order and the citers in `citers` order, else the record whose code equals the query; then, only with words, the full group (every word, or the phrase's contiguous run) by score, then the partial group by score; ties newest first by `(date, ID)` through the stable sort over `newest`.
  Filters apply to family and citers (`i in kept`).
- `rank` over candidates equals `rank` over all records.
  Argument: phrase tokens and words come from the same `[^\W_]+` over `text.lower()`, and words are tokens minus function words, so a phrase run in a record means the record holds every query word; every other ranked record is the exact ID, a family member, a citer, or holds a query word.
  The only escape is `rank`'s code-equality branch for a query that is not a code token, which needs a record whose code breaks the grammar; `read_code` refuses such a code at parse (src/lodge/core/fields.py:57), so no real store has one.
  My own seeded probe (scratch test, deleted): 120 entries in three areas, 240 decisions, about 10 % replaced, codes with absent family roots (`Q.1`, `Q.2`), mixed case, dotted citations, underscores, non-ASCII (`Straße`, `İsland`, ligatures, title-case digraphs), upper-case IDs, padded codes, one to three word queries, 30 % phrases, seven filter sets including area, status replaced, scope, and decided-by; candidates as Task 10b defines them (family only for a code token, citers only with a family).
  2,863 queries not needing memory, `rank(subset) == rank(all) == search_counted`, all passed.
- `needs_memory` (ranking.py:26-27) is the plan's rule: no words, and a phrase or a code token after stripping.
- Phrases: contiguous whole-word runs with function words kept, within title or statement separately (ranking.py:98-101); `test_phrase_keeps_function_words` and my CLI runs agree.
- One read per batch: `search_many` calls `read_checked` once (src/lodge/app/reads.py:40); `test_one_read_for_many_queries` counts one `trees()` call.
- Each record printed once, with `· also ... above`, and `--limit` per query excluding earlier records (reads.py:44-52, output.py:29-41); checked on the repository store with `lodge search search --phrase "brief lines" --brief --limit 3`: the second query names d-e8pdqe and s-3n0ndk above and shows 3 of 14 fresh records.
- Brief lines drop ` · current` only when `filters.status == "current"` (commands.py:66, output.py:45-50); `--status any` prints the status and no notice (`lodge search ITEM-1 --brief --status any`, and `test_brief_with_status_any_prints_status`).
- Edited existing expectations: exactly the three in tests/e2e/test_search_brief.py the report lists (the notice line, the omitted status, the line count); each follows from d-p60ka9 as made product behaviour by d-e8pdqe.
  tests/core/test_search.py is unchanged.
- Single-query differential against ea92261 on the repository store: 15 queries by 6 filter sets, 90 runs; 4 differ, all `S-3N0NDK`, where s-dm37qr (holding both `s` and `3n0ndk`) moves to the all-words group, as d-e8pdqe intends.
- Whole-spec output byte-identical against ea92261, exit 0 both: repository store (43,500 bytes), s900 (156,730), s9000 (1,584,257); `spec --area` identical on s9000 for area-000 and area-007.
  By reading, the local snapshot in render.py:72-85 is equivalent because `written_order` and `derived_order` (src/lodge/core/order.py:31-73) only touch current entries of the named area.
- Gate in my worktree: `sh scripts/check.sh` exit 0, 1,600 passed, 1 skipped, `lodge check --gate` ok.

## Findings

### Important

**I1 · A phrase search hides records holding every word out of order** (src/lodge/core/ranking.py:66-76; encoded by tests/core/test_ranking.py:84-90 and tests/e2e/test_search_many.py:41-42).
Failure: on the repository store `lodge search --phrase "lines brief" --brief --limit 50` lists 11 records, each holding one of the two words, and omits d-p60ka9 and d-e8pdqe, which hold both; `lodge search "lines brief" --brief` ranks those two first.
So the nearest near matches vanish while farther ones show, which defeats the plan's own purpose clause for step 4 ("so its words still find near matches below the exact ones"); the builder followed the plan's literal "at least one word but not all".
Fix: for a phrase, a record holding every word without the run joins the second group (by score, so it heads it), that is the partial condition becomes `query.words & held` when `query.phrase`; update the two tests; the candidate property is unaffected, since such records hold query words.
This conflicts with the plan's wording, so it needs a recorded process decision (scope process, work_item the plan) before the fix.

### Minor

**M1 · Every query rebuilds every candidate** (src/lodge/core/search.py:51-62, called per query from src/lodge/app/reads.py:44-45).
Failure: each query recomputes `level1`, two word sets, and areas for every record; on s9000 `search berth --brief` takes 1.72 s and `search berth tide crane cargo --brief` 2.39 s (my runs, three each, wall clock), about 0.22 s per extra query; the report's s90000 rows show 17.4 s for one query against 20.2 s for two.
The in-memory path stays after Task 10b for `needs_memory` queries, no FTS5, and cold reads.
Fix: build the candidate list once per read in `search_many` and pass it to `rank` for each query.

**M2 · Words after an option fail to parse** (src/lodge/cli/parser.py:161-166).
Failure: `lodge search brief --brief lines` exits 2 with `unrecognized arguments: lines`, because argparse closes an `nargs="*"` positional at the first option; several positional queries now invite exactly that order.
Fix: collect leftovers with `parse_known_args` for the search subcommand (or intermix its arguments) and append them to the queries; one e2e test.

**M3 · Help text does not describe the new behaviour** (parser.py:164-166).
Failure: `lodge search --help` shows `--phrase WORDS` with no help, and `queries` says nothing of each argument being its own query, a quoted argument being all its words, or `--limit` applying per query.
Fix: help strings for both, in the existing register.

**M4 · "1 matches"** (src/lodge/cli/output.py:35; encoded by tests/e2e/test_search_many.py:14).
Failure: `query: ITEM-1 · 1 matches` is ungrammatical user-facing text.
Fix: `match` for one; update the test.

**M5 · Two copies of the filter, date, and score rules** (ranking.py:80-97 against search.py:102-125, the latter kept for `related`).
Failure: a filter added to one `_passes` and not the other makes `related` and `search` disagree silently.
Fix: let `related` use ranking's helpers over `Candidate`s and delete search.py's copies (and `_newest_first`'s area branch, which `related` never reaches with `kind="decision"` only).

**M6 · The phrase tokeniser restates the words pattern** (ranking.py:23 and 100 against src/lodge/core/words.py:5).
Failure: the candidate property for Task 10b rests on phrase tokens and words sharing one pattern; an edit of `_WORDS` alone would let a phrase match a record holding none of the query words, which the index would not offer.
Fix: a `tokens(text)` in words.py used by `words`, `parse_query`, and `_contains`.

**M7 · The status is removed by string surgery** (output.py:45-50).
Failure: `.replace(" · current", "", 1)` is right only while the status is the first part after the ID and code in `_head` (src/lodge/core/views.py:177); a reordered header would cut the wrong text or none.
Fix: format the brief line from `head_parts` without the status, or give `format_brief` a status switch.

**M8 · The per-area snapshot is built positionally** (src/lodge/core/render.py:73-81).
Failure: a field added to `Snapshot` before `threads` would be filled from the wrong argument where types happen to agree.
Fix: `dataclasses.replace(s, entries={...})`.

**M9 · The candidate property test cannot exercise filters** (tests/core/test_ranking.py:136-176).
Failure: its snapshot holds decisions only, all current, every family with its root, so `Filters(kind="spec")` is empty on both sides and area, replaced status, and absent family roots never occur; Task 10b reuses the property.
Fix: add entries in several areas, replaced decisions, an area filter, a family without its root, and upper-case IDs (my probe above passed with these).

## Files read

CLAUDE.md; .claude/agents/reviewer.md (lodge); brief-t6.md; task-6-report.md; the plan's header, Global Constraints, Calls made, Review Focus, Tasks 5, 6, and 10b; d-e8pdqe, d-ty4dks, d-emtwbs, d-n9w4by, d-aej8rs, d-p60ka9, d-3g6ard, d-fqymzm, d-y94v0n, and s-3n0ndk through lodge; the whole diff of 61d2629 in src/ and scripts/; src/lodge/core/ranking.py, filters.py, codes.py, words.py, order.py, the changed parts of render.py and search.py, search.py at ea92261, views.py (`level1`, `format_brief`, `_head`), fields.py (`read_code`), snapshot.py (`Snapshot`); src/lodge/app/reads.py (`search_many`, `_views`); src/lodge/cli/output.py, parser.py, commands.py (changed parts); src/lodge/cli/guide.md lines 13-14; tests/core/test_ranking.py, tests/core/test_render_grouping.py, tests/app/test_search_many.py, tests/e2e/test_search_many.py, the diff of tests/e2e/test_search_brief.py, tests/core/builders.py.

## Files not read

tests/core/test_search.py (unchanged by the commit); the rest of render.py, views.py, and reads.py; app/state.py and `read_checked`; the viewer; scripts/bench_reads.py; the plan-review and fix files; earlier task reports; the raw logs under /var/tmp/lodge-bench.
