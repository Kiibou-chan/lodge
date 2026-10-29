# Task 13 recheck 1: fix round bf7ef0b

Diff 4a89ea6..bf7ef0b, scoped to I2, I3, and M1 of the Task 13 review; I1, M2, M3, and M4 are not in this round.
Scratch copy from `git archive bf7ef0b`, git only in the scratchpad with `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1`, removed when done.

Counts: 0 Blocking, 1 Important, 2 Minor.

## Verification run

- `sh scripts/check.sh`: green, 1005 passed, gate `ok`.
- `lodge search "" --status any` on lodge's own 21 records ends with `20 of 21 shown; narrow the query or give --limit 21`.
- New tests run against the 4a89ea6 source: `tests/core/test_search.py` fails at import (`search_counted`), and `test_search_says_how_many_more_matched_beyond_the_limit`, `test_search_page_says_when_it_stops_at_the_limit`, and `test_search_limit_says_what_it_left_out` fail.
- `test_search_limit_must_be_a_positive_whole_number` passes against the 4a89ea6 source (see m2).
- `src/lodge/core/search.py` with `_COMMON_FROM = 10**9` (the common-word filter off): all 17 tests in `tests/core/test_search.py` pass (see R1).
- `_shared` forced to `True` (the two-word rule off): `test_related_needs_two_shared_words_not_one` fails, as it should.

## Findings

I2, search names what it left out: answered.
`src/lodge/core/search.py:61` (`search_counted`), `src/lodge/app/reads.py:31-33` (`Listed.more`), `src/lodge/cli/output.py:23`, `src/lodge/viewer/pages.py:17`, `--limit` in `src/lodge/cli/parser.py`.
Tests in core, app, viewer, and e2e fail without the fix.
User-facing text follows the rules: "20 of 21 shown; narrow the query or give --limit 21", "2 of 4 shown; narrow the query.", and the README line, one sentence each, British English, no em-dashes.

I3, related needs two shared uncommon words: answered in code, only half guarded by tests (R1).
`src/lodge/core/search.py:80` drops the common words, `:86` requires two shared words, `:91-100` counts words in more than a third of current decisions, from five decisions on.

M1, report wording: answered (`task-13-report.md`, the `--dry-run` bullet now says the dry run names an ID in its feedback lines).

## New problems

### R1 (Important). No test fails without the common-word filter

Handle: `tests/core/test_search.py:167` (`test_related_ignores_a_word_most_decisions_carry`), against `src/lodge/core/search.py:80` and `:91-100`.
In that test the draft shares only "lodge" with each common decision, so the two-word rule at `:86` already rejects them; with the filter switched off, all 17 tests pass.
The report claims this test covers the filter.
Failure scenario: a later change drops or breaks `_common_words`, every test stays green, and in the first user a draft sharing "renderer" with most decisions again gets three false "looks related" lines, the noise I3 was about.
Fix: in that test give the five common decisions and the draft two shared common words (for example titles `Lodge {name}` and statements `Records held.`, a draft `Lodge zeta` with statement `Records held there.`), assert `related(...) == []`, and confirm it fails with `_COMMON_FROM` set out of reach; keep the twin, sharing two uncommon words, as the positive case.

### m1 (Minor). `lodge search --help` still says an empty query lists all

Handle: `src/lodge/cli/parser.py:147`: "words, an ID, or a code; empty lists all, newest first".
It lists 20 by default, as the README now says, so the help contradicts both the README and the behaviour.
Fix: "words, an ID, or a code; empty lists every record the filters allow, newest first, up to --limit".

### m2 (Minor). The `--limit` validation test passes without the validator

Handle: `tests/e2e/test_search_limit.py:14-18` asserts only exit code 2 and `--limit` in stderr, which argparse's "unrecognized arguments: --limit 0" also satisfies on the old source.
Fix: assert `"is not a positive whole number" in result.err`.

## Files read

`.claude/agents/rechecker.md`, the review package `review-4a89ea6..bf7ef0b.diff` in full, and the lines of `src/lodge/core/search.py`, `src/lodge/cli/parser.py`, `src/lodge/cli/output.py`, and `src/lodge/viewer/pages.py` at bf7ef0b named above.
Not read: files outside the diff.
