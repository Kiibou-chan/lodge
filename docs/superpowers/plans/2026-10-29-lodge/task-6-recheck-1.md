# Task 6 recheck 1: fix round 1 (90e9af4)

Scope: the fix diff 30f919b..90e9af4 against task-6-review.md and the Task 6 `Ruling:` lines (progress:84-92).
Scratch copies: `scratchpad/probes-t6/fix1` (`git archive 90e9af4`, own `uv sync --offline`) and `scratchpad/probes-t6/old` (`git archive 30f919b`).

## Runs

- `sh scripts/check.sh` in `fix1`: exit 0, 579 passed.
- The fixed test files copied into `old`, run with `PYTHONPATH=old/src` (checked: `lodge.__file__` resolves to `old/src`): 23 failed, 53 passed. Every new test fails on 30f919b: `test_render_spec_marks_flagged_failing_and_imported_entries`, `test_search_without_words_returns_exact_match_only`, `test_search_ties_larger_id_first`, `test_search_ignores_function_words`, `test_related_ignores_function_words_and_numbers`, `test_search_area_matches_decisions_changing_its_entries`, `test_duplicate_id_marks_kept_record_failing`, and the six in `test_views_trust.py`. The other failures are changed expectations and signatures.
- The builder reports 21 failures before the code; the 2 extra here are signature changes (`render_spec`, `level2`) in tests the builder may have counted once per file. No effect on the verdict.
- Probes rerun: `probe-fix1.py` and `probe2-fix1.py` (the review's probes with the new `failing` arguments), outputs in `probe-fix1-out.txt` and `probe2-fix1-out.txt`; regression probe `probe3.py`, output `probe3-out.txt`.

## Test diff

No assertion was weakened.
Changed expectations follow the rulings: `[2]` to `[2, 2]` for a duplicate ID (test_check_state), the duplicate test now asserts both paths and both messages, `awaiting the author on <id>` for touched records, `changes (edit)`, the quote line in `test_format_level1_exact_text`, and `no decision` for a bare entry.
`ids(area="storage")` gains `d-aaaaaa` by M5.

## Findings

- B1: answered, views.py:73 and views.py:126-130. Probe P6 prints `quote: "Keep it." (a session, 2026-10-28 10:00)` after the statement; an entry takes it only when its newest changing decision is the author's (P7, and absent in P3 under an agent change).
- I1: answered, render.py:35-38. Probe P3 renders `## Store (s-aaaaaa · awaiting the author on d-cccccc)`, and P3b `## Store (s-aaaaaa · fails check)`. Every level-1 flag goes in the heading, as the dispatch states, wider than the ruling's three; retired entries are still not rendered, so `retired by` never shows there.
- I2: answered, views.py:90-94 and views.py:188-189. Probe P5: the level-2 head reads `· author · ... · fails check` and the entry reads `· decision fails check`.
- I3: answered, snapshot.py:87. Probe P1: the kept `d-aaaaaa` reads `· fails check`, and the dropped file is still an unrecorded problem.
- I4: no change, by ruling (progress:90; moved to Tasks 10 and 11). Probes P2 and P2b unchanged. Since B1, P2 also prints her quote under the agent's rewritten entry text, so the hidden-decision case now reads more convincingly as hers. The ruling's warning lines carry the whole answer: Task 10 and Task 11's briefs should place `unrecorded_problems` above the level-1 output, as the ruling says, and test that order.
- I5: answered, search.py:53-61. Probe P4: `42` finds only `d-ffffff`; `%`, `--`, and `2026` (in no title or statement) return `[]`; the empty query lists by filters.
- I6: answered, views.py:173-177. Probe P7: `· its decision replaced by d-mmmmmm`.
- Search-words ruling: answered, words.py (letters or digits, function words dropped) and search.py:68 (`related` drops pure-digit words). probe2: `related` no longer pairs "The cache is small." with "The queue is long."; `search("the is")` returns `[]`.
- M1: answered, views.py:178-181. A record both flagged and touched shows the bare text only (probe3: `d-cccccc` reads `narrowed by d-dddddd · awaiting the author`). Its `narrowed by` names the touching decision, so nothing is hidden. Not a finding.
- M2: answered, search.py:77; probe2 ties read `['d-bbbbbb', 'd-aaaaaa']`, matching `derive`.
- M3: answered, views.py:107.
- M4: answered, views.py:153; probe P8 reads `s-dddddd · current · no decision · storage`.
- M5: answered, search.py:95 and `_areas`.

## Regressions looked for

- Task 4's duplicate-ID change to `load`: `check_change` compares problems by path, check, and message, so a published duplicate now gives two notes, and a new one fails the gate on both paths; the ruling (progress:88) accepts this. Full suite green, including `test_check_change.py`.
- Search ranking on ordinary queries (probe3): `cache eviction` ranks the title match first, `10 minutes` finds the statement holding both, `queue` finds only its decision, and case does not matter. `not cached` finds nothing because there is no stemming, which was already true before the fix.
- Exact `format_level1` text: the header, title, and statement are unchanged, and the quote is added after a blank line only when present. `test_format_level1_exact_text` pins both forms.
- Module sizes: views.py 204 lines, test_views.py 237, all under 300.

## Verdict

0 Blocking, 0 Important, 0 Minor introduced by the fix.
All twelve findings are answered, and I4 is moved by ruling.
Recheck clean.
