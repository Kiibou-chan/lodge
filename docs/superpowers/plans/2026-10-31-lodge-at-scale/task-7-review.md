# Review of the Task 5 fix round (e01a221) and Task 7 (c388306, `lodge guide --read`)

Reviewer: lodge reviewer (Opus), correctness, then practice, then design.
Branch `read-speed-build`; authority: plan Task 7, d-32cvvz (read with `lodge show d-32cvvz --reasoning`), `review-t5.md` for the fix round.
Scratch: `/var/tmp/lodge-review-t7/` (`wt` at c388306, `old` at ea92261, `s900` a copy of the bench store, `cmp.py`, `oldlodge`); worktrees removed at the end.
Nothing was run in `/var/tmp/lodge-build`.

## Counts

Blocking 0, Important 0, Minor 7.

## Verdict on the dispatch's checks

1. Length and content: `src/lodge/cli/guide-read.md` is 25 lines (`wc -l`; the heading and its blank line included), so the limit holds with no room left.
   It holds none of `lodge add`, `lodge draft`, `decided_by`, `lodge ask`, `lodge reply`, `lodge close`, and no em-dash; the one duty that touches writing is Minor 4.
2. Every example runs as written (placeholders substituted) on a copy of `s900` with `lodge` from c388306, exit 0 and empty stderr:
   `waiting`; `search "berth crane" --brief` (first result `s-1xyzjd`, title "Yard yard berth crane berth seal", holds both words); `search --phrase "berth crane" --brief` (first result the same, phrase in order); `search CODE-9 --brief` (`d-7k14sj CODE-9`, `d-16tfh2 CODE-9.why`, then `s-hk7wxn`, the one record `show CODE-9` lists under `cited by:`); `search berth crane --brief` (two `query:` headers, 676 matches for `berth`); `show d-7k14sj s-1xyzjd d-16tfh2`; `show CODE-9.why --reasoning`; `show d-7k14sj --provenance`; `spec`; `threads`.
   The guide's own backticked lines are extracted by `grep -o` in `/var/tmp/lodge-review-t7/examples.txt`: ten, all run.
   Mutations of the guide in my worktree: `--phrases` and `--reason` each fail `test_guide_read_examples_run` and the shortness test (the exact-line check does the work; argparse prefix matching would let `--reason` run).
3. Each sentence about behaviour against the code:

   | Sentence | Handle | Result |
   |---|---|---|
   | "Quotes only group words into one query, with records holding all the words first" | `ranking.py:61-68` (`query.words <= held`, by score), `parser.py` `queries nargs="*"` | true; the first block is every record holding all non-function words |
   | "--phrase matches them as a contiguous run in order" | `ranking.py:76-77` (`_contains` over `[^\W_]+` runs of title or statement) | true of the first group; see Minor 1 |
   | "word1 word2 makes two queries" | `output.py:35-40` prints one `query: W · N matches` header per query | true (s900 output has both) |
   | "A code search puts the family and citers first, with dotted descendants belonging to the family" | `ranking.py:46-51`, `codes.py:22-30` (`code.` prefix at any depth) | true (s900: `CODE-9`, `CODE-9.why`, then the citer) |
   | show "lists siblings and citers for a coded record" | `output.py:51-61` | true, capped at ten with an `and N more` line the guide omits (acceptable) |
   | `--reasoning` adds "the why, or an entry's changing decisions" | `show s-1xyzjd --reasoning` on s900 lists `d-jy0cny`, `d-gkhvf3` after `## Reasoning` | true |
   | `--provenance` adds "quote, numbers, work item, attachments, and links both ways" | `views.py:150-161` | true (also `imported from:`, unlisted) |
   | "Unmarked brief records are current" | `output.py:31`, `:47-50` (the status word is dropped only under the default filter) | true; under `--status` the word prints, and the lines under `siblings:` and `cited by:` print `current` |
   | "replaced decisions have successors, retired entries no longer hold, author confirmation is a separate flag" | `views.py:189-205` (`replaced by`, `retired by`, `confirmed by the author`) | true |
   | "awaiting the author" | `views.py:201-204`, `derive.py:_flagged` | the sentence is the full guide's, word for word; it omits the imported-decision case that `_flagged` also flags (unchanged wording, not a regression) |
   | "in doubt", "question open", "narrowed by" | `doubts.py:27-33`, `:63`, `views.py:192-193` | true; `in doubt` also appears as `changed by X, in doubt` and `rests on X, in doubt`, as the guide says ("or its dependencies") |
   | "fails check", `problem:` | `views.py:213-217`, `output.py:25` (`problem: path:line: message`) | true |
   | `lodge threads` / the thread command | `threads.py:52-54` (`threads`, `thread REF`) | true; see Minor 5 |

4. The full guide points at `--read`: `src/lodge/cli/guide.md:7` ("agents that only read can use `lodge guide --read`"), still 60 lines; `test_full_guide_points_at_read` passes.
   README line 79 names the command; the wheel built by the builder holds `guide-read.md` (`/var/tmp/lodge-bench/venv-task7/lib/python3.13/site-packages/lodge/cli/guide-read.md`).
5. The citers prefilter leaves output unchanged.
   `cmp.py` runs `show` of many refs in one call with the ea92261 code (`/var/tmp/lodge-review-t7/oldlodge`, `PYTHONPATH=old/src`) and with c388306 on the same files, comparing exit status, stdout, and stderr:

   | Store | Refs | Flags | Result |
   |---|---|---|---|
   | `s900` | 280 codes plus `A`, `a`, `CODE-1`, `nope` | none | identical, exit 2 both (`nope`) |
   | `s900` | the same | `--reasoning --provenance` | identical |
   | `s900` | 1,585 IDs | none, and with both flags | identical |
   | repository's own store (`wt`, 358 IDs, 11 codes) | codes plus `A`, `a`, `CODE-1`, `nope`; all IDs | none, and with both flags | identical |

   The filter is sound: a whole-token citation lies inside the title or the statement (the newline joining them is not a run character), and `str.lower()` acts per character on ASCII runs.
   A fuzz over 400,000 random title, statement, and code triples (alphabet with `ſ`, `İ`, Kelvin, sigma, dots, dashes, newlines): `cites(f"{t}\n{s}", code)` true and the substring test false never happened (15,513 true cases).
6. Gate subset in `wt`: `uv run --frozen pytest tests/e2e/test_guide_read.py tests/e2e/test_guide.py tests/core/test_codes.py tests/app/test_show_many.py tests/test_bench_cleanup.py tests/test_structure.py -q` gives 72 passed; `lodge check --gate` prints `ok`.

## Task 5 fix round against `review-t5.md`

| Finding | Outcome | Evidence |
|---|---|---|
| M1 | Fixed | `codes.py:56-62` filters by `wanted in title.lower() or wanted in statement.lower()` before `cites`; `reads.py:56-58` makes `show` skip siblings and citers (`context=False`), `show_many` keeps them. Mutations: `context=True` fails `test_viewer_show_does_not_compute_unused_code_context` and `test_siblings_and_citers_capped_at_ten`; dropping the prefilter fails `test_citers_tokenise_only_records_containing_the_lower_cased_code`. The report's `show {code}` row at `s9000` is 1.744 s before, 1.510 s after, output equal; the before build is b4cd90e, so Task 5's own cost against Task 4 is still not shown (Minor 7). |
| M2 | Fixed | `CODE_PATTERN` once in `fields.py:11`, imported at `codes.py:8`; `codes.py` and `fields.py:57` use it. |
| M3 | Fixed | `codes.py:34-36` now says "Each maximal run of [a-z0-9._-] in the lower-cased text, and each prefix of a run that ends before a dot not followed by a letter or digit", which is the condition at `:42-45`. |
| M4 | Fixed | `bench_reads.py:38-46` returns `(timeout, None, None)`; every mode keeps going, including the warm-up and `changed` restore (`git checkout -- lodge` stays in the `finally`); `identical` is false when any sample timed out (`:130-133`); `test_timeout_keeps_measured_rows_and_continues[cold|seen|changed]` and `test_timeout_keeps_successful_samples_in_the_same_row`. |
| M5 | Fixed | the ledger (`...-progress.md:63`) and the report name both halves of M3, and defer `written_order` to the next round touching `order.py` or `render.py`. |

## Findings

### M1 · Minor · `--phrase` is described without the tail of some-word matches that follows its matches

Handle: `src/lodge/cli/guide-read.md:11` ("--phrase matches them as a contiguous run in order"); behaviour `src/lodge/core/ranking.py:61-71`.
Failure scenario: on `s900`, `search --phrase "berth crane" --brief --limit 1000` prints 812 records, five of which hold the phrase (`s-1xyzjd`, `s-577pwa`, `d-9e1955`, `d-wh5rx6`, `d-4kath8`); the sixth line, `s-70e1xn`, "Mooring mooring manifest tally crane mooring", holds only `crane`.
An agent that reads the guide as "matches" takes the first twenty lines as phrase matches and cites records that do not hold the phrase.
Fix: say it in the same line, for instance "--phrase lists records holding them as a run in order first, then records holding some of the words".
The line has to stay one line or another goes, since the file is at 25.

### M2 · Minor · Observed in Task 6, outside this diff: a phrase search drops records holding every word out of order while it lists records holding one

Handle: `src/lodge/core/ranking.py:68-71`: `partial` takes `query.words & held and not query.words <= held`, so a record holding all the words but not as a run is neither `full` nor `partial` for a phrase.
Failure scenario: on `s900`, `search "berth crane"` lists `s-94grgp` ("Invoice crane forklift pilot weighbridge berth") and `d-fd4ryp` among its first results; `search --phrase "berth crane" --limit 1000` holds neither (`grep -c` of both IDs in `/var/tmp/lodge-review-t7/phr.txt` is 0), while it holds 800 records with one of the words.
The plan's rule 4 says "at least one word but not all" literally, so the code follows the plan; its stated purpose ("near matches below the exact ones") is not served.
Fix: for a phrase, `partial` takes any record with at least one word that is not `full`; or record the plan's wording as intended in d-e8pdqe's successor.
For the whole-branch review; no change to Task 7.

### M3 · Minor · `show CODE.why --reasoning` is an example without its convention

Handle: `src/lodge/cli/guide-read.md:15`; the sentence at `:12` explains dotted descendants but not `.why`.
Failure scenario: in this repository's own store no record is coded `X.why` (`lodge show LODGE-1.why --reasoning` prints `lodge: no record named LODGE-1.why`, exit 2), so an agent that copies the shape on a project without the convention gets an error and may read it as a missing record.
Fix: one clause, "(`CODE.why` where a project codes the reasoning that way)", or use `lodge show CODE --reasoning` as the example; if the cap forbids both, merge lines 12 and 15.

### M4 · Minor · The reading guide tells a read-only agent to answer what waits

Handle: `src/lodge/cli/guide-read.md:5` ("answer what waits for an agent first"), taken from the full guide's Reading section where `ask`, `reply`, and a decision follow in Writing.
Failure scenario: an agent given only this guide finds a waiting thread, has no command or rule for answering, and either invents one (a `lodge reply` without `--by`) or drops the instruction.
Fix: "and tell the coordinator what waits for an agent; `lodge guide` has the rules for answering", or "read what waits for an agent first".

### M5 · Minor · Two reading details the full guide has are missing, and the thread command has no invocation

Handle: `guide-read.md:21` says "the thread command reads one by its ID" with no `lodge thread ID`; the full guide's third Reading paragraph on a rewritten lodge branch (`guide.md:19`) has no counterpart.
Failure scenario: an agent guesses `lodge threads ID` (accepted silently as a list, no read of the thread); a branch-mode freshness line about a rewritten branch appears with no word on who acts.
Fix: write `lodge thread ID` in the line (its example would need a seeded thread in `test_guide_read_examples_run`, or stay out of backticks as now), and add a clause on the freshness line if a line can be freed.

### M6 · Minor · The prose sentences about behaviour are checked only by presence, and the wheel test does not list the new file

Handle: `tests/e2e/test_guide_read.py:38-56` (the phrases are substring checks), `:58-90` (five of the seven examples are checked for exit 0 only); `tests/test_wheel.py:32` lists only `lodge/cli/guide.md`.
Failure scenario: a later change to ranking or to the flags can falsify "word1 word2 makes two queries" or "family and citers first" with the guide's test green (the Task 6 tests catch the behaviour, not the sentence); a packaging change that drops `guide-read.md` fails only when someone runs `lodge guide --read` from an installed wheel (the report did it once by hand).
Fix: assert two `query:` headers for the unquoted example and `CODE` first with its `.why` sibling second for the code example; add `lodge/cli/guide-read.md` to the wheel test's expected names.

### M7 · Minor · `Lodge.show` now returns empty siblings and citers without saying so; the fix round filed under the Task 7 report

Handle: `src/lodge/app/lodge.py:36-37` and `src/lodge/app/reads.py:56-58` (`show` passes `context=False`); no docstring on either.
Failure scenario: a later caller of `Lodge.show` (Task 10a's indexed reads or a viewer panel) reads `shown.siblings` and gets `()` for a record that has siblings, indistinguishable from none.
Fix: a docstring on `Lodge.show` and `reads.show` ("the record without code context; `show_many` carries siblings and citers"), or a distinct name.
Also: the fix round's account is in `docs/superpowers/plans/2026-10-31-lodge-at-scale/task-7-report.md` (there is no `task-5-fix-report.md`), and its `show {code}` timing compares b4cd90e with the fix, not Task 5 with Task 4; the progress ledger has no Task 7 line yet.
Fix: a line in the ledger naming where the fix round is reported, and, if the coordinator wants Task 5's total cost, one `show {code}` row at `s9000` against the Task 4 build.

## Practice and design notes, no finding

- `Guide(read: bool = False)` and the three parser lines are within the plan's limit of three; `commands.py:87-89` picks the file by name; no new import edge.
- The two guide files share no text beyond the first-paragraph definitions; they will drift, and nothing ties the reading guide's flag list to `views.py:_flags`; `test_guide_read.py` could not catch that (see Minor 6).
- Bare flags in prose (`--phrase`, `--reasoning`, `--provenance`) are not in backticks, unlike the full guide; harmless for the test, which reads the backticked lines only.
- Style: British English, no em-dash, Oxford comma, one sentence per line hold (line 11 is one sentence with semicolons).
- The d-32cvvz record and the edit of s-7f10zc are as the plan says (`lodge show d-32cvvz --provenance`: `changes (edit): s-7f10zc`); `lodge check --gate` is `ok`.

## Files read

`CLAUDE.md`; `.claude/agents/reviewer.md`; `src/lodge/cli/guide-read.md`, `guide.md`, `commands.py`, `parser.py`, `output.py`, `threads.py`; `src/lodge/core/ranking.py`, `codes.py`, `search.py`, `views.py` (flags, level 3), `doubts.py`, `derive.py` (`_flagged`); `src/lodge/app/reads.py`, `lodge.py`; `scripts/bench_reads.py`; the diffs of e01a221 and c388306 (src, tests, scripts, ledger, README, reports); `tests/e2e/test_guide_read.py`; `tests/test_wheel.py` (guide lines); `task-7-report.md` at both commits; `review-t5.md`; the plan's Task 6 and Task 7 sections; d-32cvvz, d-e8pdqe, d-y94v0n, s-7f10zc through `lodge show`.

## Files not read

`tests/test_bench_cleanup.py` beyond its diff; `tests/e2e/test_search_many.py` and `tests/core/test_ranking.py`; the Task 7 brief and Codex logs; `docs/superpowers/plans/2026-10-31-lodge-at-scale-progress.md` beyond the fix-round lines; the viewer beyond the `show` call site; the full gate (`scripts/check.sh`) and the s9000 timings were not re-run.
