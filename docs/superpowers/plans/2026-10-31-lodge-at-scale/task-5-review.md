# Review of Task 5 (`show REF...`, siblings, citers), commit ea92261, and the Tasks 1 and 2 fix round, commit 8f980c9

Reviewer: lodge reviewer (Opus), task review: correctness, then practice, then design.
Under review: branch `read-speed-build`, `ea92261` (Task 5, builder Codex) and `8f980c9` (Tasks 1 and 2 fix round, builder Codex).
Authority: `lodge spec` (s-3n0ndk as edited by d-y94v0n), d-y94v0n read with `lodge show d-y94v0n --reasoning`, the plan's Task 5 section, and `task-1-2-review.md` for the fix round.
Scratch: `/var/tmp/lodge-review-t5/` with detached worktrees `wt` at `ea92261` and `old` at `bd7e03b`, each with its own `.venv`; probes `cmp.py`, `prop.py`, `cost.py`, `cost2.py`; both worktrees removed at the end.
Nothing was run in `/var/tmp/lodge-build`, and nothing was run on `s90000`.

## Counts

Blocking 0, Important 0, Minor 5.

## Verdict on the dispatch's checks

1. Code grammar: `is_code_token` (`src/lodge/core/codes.py:17-19`) is the plan's `[A-Za-z0-9][A-Za-z0-9._-]*` with `fullmatch`, ASCII only (`ſ-1`, `é1`, `A\n` refused by `test_is_code_token_uses_the_ascii_grammar`).
2. `cites` boundary rule: equal to the plan's property on 200,000 independent random cases over a wider alphabet than the builder's test (upper and lower case, digits, `._-`, space, newline, `,():;/`, `ſ`, the Kelvin sign, `İ`, `é`, `ß`), with codes drawn both as substrings of the text and freshly from the grammar, trailing dots included: `uv run --frozen --quiet python /var/tmp/lodge-review-t5/prop.py 7` in `wt` printed `mismatches 0`.
   The oracle is the plan's rule as a regex over `text.lower()`, independent of `code_tokens`.
3. Case by `str.lower()`: `family` (`codes.py:24-28`), `code_tokens` (`codes.py:36`), and `cites` (`codes.py:48`) all use `lower()`; mutating `code_tokens` to `casefold()` fails two tests.
   Mutating `cites`'s `code.lower()` to `casefold()` passes every test, but that mutant is equivalent: record codes are refused unless ASCII (`src/lodge/core/fields.py:55-59`), and `lower()` equals `casefold()` on ASCII.
4. Per-ref errors: a failing ref prints `----- REF` on stdout, then `sys.stdout.flush()`, then `lodge: <error>` on stderr (`src/lodge/cli/commands.py:111-118`); the single-ref path flushes before raising (`:100-103`).
   Through a pipe (`lodge show CODE-896 nope CODE-9.why nope2 2>&1`, on `s900`) separator and error lines interleave in order.
   Removing the flush fails `test_stdout_flushed_before_each_error`; replacing `max` with the last failure's code fails `test_batch_exit_uses_highest_failure`.
5. One read per batch: `show_many` calls `read_checked` once (`src/lodge/app/reads.py:65-81`); `test_one_read_for_many_refs` counts one `trees()` call for four refs.
6. Repeats and aliases: a ref resolving to an ID already shown is carried as `replace(seen[ident], repeat=True)` and printed as `----- REF is ID, shown above`; on `s900`, `lodge show CODE-9 CODE-896 a CODE-9 nope CODE-9.WHY` printed `----- CODE-9 is d-7k14sj, shown above`, the error in place, the lower- and upper-cased aliases resolved, and exit 2.
7. A single ref's output unchanged apart from the new lines, old build `bd7e03b` against new, same store, comparing stdout, stderr, and exit status (`/var/tmp/lodge-review-t5/cmp.py`): the new stdout must equal the old one, or the old one followed only by `siblings:`, `cited by:`, or `and N more` sections.

   | Store | Refs | Flags | Same | Old plus new sections only | Other |
   |---|---|---|---:|---:|---:|
   | repository's own (`wt`) | 356 IDs | `--reasoning --provenance` | 346 | 10 | 0 |
   | repository's own | 356 IDs | none | 346 | 10 | 0 |
   | repository's own | 11 codes (`LODGE-1` to `LODGE-10`, `SCALE-1`) | none | 1 | 10 | 0 |
   | `s900` | 46 (`CODE-9`, `CODE-896`, `A`, `a`, `CODE-1`, `CODE-9.why`, 40 IDs) | `--reasoning --provenance` | 42 | 4 | 0 |
   | `s900` | the same 46 | none | 42 | 4 | 0 |

   An unknown single ref prints nothing on stdout, `lodge: no record named nope` on stderr, and exits 2 in both builds.
8. Caps and left-out counts: `reads.py:59-61` take ten of each and count the rest; `test_siblings_and_citers_capped_at_ten` checks 12 siblings and 11 citers giving 10, 10, and `(2, 1)`, the order after `## Provenance`, and the exact closing sentence.
9. The spec edit: s-3n0ndk's third sentence now says `show` takes several refs, printed from one read with each record once, and names a coded record's siblings and citers; the first two sentences are as at `bd7e03b`.
10. Gate in the review worktree: `UV_FROZEN=true sh scripts/check.sh` green, 1,580 passed and 1 skipped, `lodge check --gate` ok.
11. Fix round: I1 is fixed and its test can fail (below); M1, M2, M4, M5, and M6 are fixed or closed; M3 is reported as out of scope.

## Tasks 1 and 2 fix round against `task-1-2-review.md`

| Finding | Outcome | Evidence |
|---|---|---|
| I1 | Fixed | `core.change_facts` (`src/lodge/core/check_change.py:32-50`) is the one constructor, keyed by `sort_key`; `app/state.py`, `app/reads.py`, and `probes/shapes.py` call it; `test_gate_prints_already_published_note` patches `sort_key` and asserts the note; `test_check_change_with_facts_equals_old_oracle` compares with a copy of the pre-Task-2 `check_change` (`tests/core/linear_change_oracle.py`). |
| M1 | Fixed | `State.published_state` reused when `base.published is state.published` (`reads.py:113`); `test_gate_reuses_published_facts` counts two loads, two derives, two state checks. |
| M2 | Fixed, one gap (Minor 4) | SIGTERM handler, `--timeout` through `subprocess.run`, the clean-store check in every mode; `tests/test_bench_cleanup.py`. |
| M3 | Reported, not fixed | Progress ledger line 63; the stated reason covers only half (Minor 5). |
| M4 | Fixed | Every third decision of the first shape is an author's; `datetime.UTC`. |
| M5 | Fixed | The test moved to `tests/app/test_change_facts.py`, the `sys.path` insertion gone. |
| M6 | Closed | Progress ledger line 62. |

The I1 test fails under each of three breaks of the constructor or its use, made in the scratch worktree and reverted:

| Break | Result |
|---|---|
| `change_facts` keys by the hand-spelled `(p.path, p.check, p.message)` instead of `sort_key` | `test_gate_prints_already_published_note` fails (`check 7: s-aaaaaa: is not listed ...` printed as a problem) |
| `change_facts` returns an empty published-problem set | that test and `test_check_change_with_facts_equals_old_oracle` fail |
| the gate in `reads.check` bypasses `change_facts` with a hand-built `ChangeFacts` | `test_gate_prints_already_published_note` fails |

## Findings

### M1 · Minor · Every show of a coded record tokenises every record's title and statement, once per ref, and the viewer pays it for nothing

Handle: `src/lodge/core/codes.py:51-67` (`citers` runs `cites`, so `code_tokens`, over every decision and entry), called per ref from `src/lodge/app/reads.py:47-48`; `Lodge.show` now goes through the same `_shown` (`reads.py:39-41`), and its only production caller is the viewer's record page (`src/lodge/viewer/server.py:188`), whose `pages.record_page` reads neither `siblings` nor `citers` (`grep -rn "siblings\|citers" src/lodge/viewer` is empty).
Measured in process after one `read_checked` (`/var/tmp/lodge-review-t5/cost.py`, new build): `citers` takes 0.021 s at `s900` (1,585 records) and 0.212 s at `s9000` (15,895 records), linear, so about 2.1 s per coded ref at `s90000` (extrapolated, not run there); `read_checked` itself is 1.39 s at `s9000`.
Failure scenario: `lodge show` of five coded refs at 160,000 files spends about 10 s in citation scans on top of one 17 s read, and each viewer record page at that size spends about 2 s computing lines it never shows; the report's benchmark has no single-ref `show {code}` row against Task 4's build, so the added cost is not visible there.
A substring pre-filter, `code.lower() in text.lower()` before `cites`, sound because a whole-token citation is a substring of the lower-cased text, takes the scan to 0.004 s at `s9000` for a code that occurs nowhere (`cost2.py`); it does not help a code like `A` that occurs everywhere.
Fix: filter by substring before tokenising in `citers` (or tokenise each record once per batch and look each code up in a map), and let the viewer's `show` skip the context (a parameter, or `show` without it and `show_many` with it); add a `show {code}` row against the previous build to the report.
Task 10a's stored citers serve seen states later; the in-memory path stays for cold reads.

### M2 · Minor · The code grammar is written twice

Handle: `src/lodge/core/codes.py:11` and `src/lodge/core/fields.py:11`, the same `re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")`.
Failure scenario: the grammar changes in `fields.py` (what a record may hold) and not in `codes.py`; Task 6 then uses `is_code_token` to decide whether a query is a code, and a valid code of the new form is searched as words, the problem d-y94v0n's reasoning names.
Fix: one pattern, in `fields.py` (lower in the import order: `codes` already imports `derive`, `model`, and `snapshot`), imported by `codes.py`.

### M3 · Minor · `code_tokens`'s docstring states a wider rule than the code

Handle: `src/lodge/core/codes.py:34`, "the prefixes before punctuation or terminal dots".
Failure scenario: a reader takes `X-1-a` to yield the token `x-1` (a prefix before punctuation), when only a prefix ending before a `.` that is last in the run or followed by `.`, `-`, or `_` is added (`codes.py:38-41`), which is the plan's rule.
Fix: "Each maximal run of `[a-z0-9._-]` in the lower-cased text, and each prefix of a run that ends before a dot not followed by a letter or digit."

### M4 · Minor · A benchmark timeout ends the whole replay and loses every row measured

Handle: `scripts/bench_reads.py:38-43` raises `subprocess.TimeoutExpired` out of `measure`, and `main` (`:114-117`) prints the table only after every build finished; `tests/test_bench_cleanup.py:37` expects the raise.
Failure scenario: an `--against` replay at `s90000` where one old-build command passes `--timeout` prints a traceback and no table, so the commands that finished are lost, the case Task 4's report met ("s90000, interrupted comparison").
The cleanup the review asked for does run (the `finally` and `TemporaryDirectory` exit), so this is a gap in usefulness, not in safety.
Fix: catch `TimeoutExpired` per sample in `run` and record it as a row (`timeout`, no characters, `Identical` false), so the replay continues.

### M5 · Minor · The reason given for leaving M3 covers only one of its two scans

Handle: `docs/superpowers/plans/2026-10-31-lodge-at-scale/task-5-report.md`, Tasks 1 and 2 fix round, "would require `heapq`"; progress ledger line 63, "within the fixed core import rules".
`written_order` scans every entry once per area (`src/lodge/core/order.py:31-36`, called per area at `src/lodge/core/render.py:63`); grouping entries by area once per render needs no import beyond `CORE_MODULES`; only the `derived_order` half plausibly needs a priority queue.
Failure scenario: the coordinator reads the ledger as "M3 needs an import rule change" and the whole-spec render keeps its quadratic-in-areas scan (2.56 s at 905 areas in the earlier review, about 16 s at the bench's size) although half of it is a local fix.
Fix: correct the ledger line to name the two halves, and take the `written_order` grouping in the next round touching `order.py` or `render.py`.

## Correctness pass, Task 5, beyond the dispatch's checks

- `family` takes the code and its dotted descendants at any depth, not `X-10` or `X-1a`; ordered code first, then by lower-cased code and ID (`codes.py:22-30`); dropping the `+ "."` fails two tests.
- `citers` excludes the whole family (breaking it to exclude only the record fails a test), reads title and statement joined by a newline (a non-run character, so no token spans the two), and orders by the level-1 date (an entry's newest changing decision, as `views.level1` takes it) and ID, newest first, undated entries last.
- Breaking `code_tokens` to add a prefix before every dot fails two tests.
- `test_cites_equals_the_boundary_rule` falls back to five fixed codes when a substring fails the grammar, so fewer than 2,000 cases are drawn substrings; the independent run above covers that.
- The spec's "a line naming each ref after the first" says nothing of failures; a failing first ref also prints `----- REF`, as the plan's failure rule requires.
- `ShownMany`, `Shown`'s four fields, and the parser change (four lines, within six) are as the plan states; `cli/parser.py` stays at 236 lines.
- A non-coded record and a coded record with no siblings or citers print no new lines (`output.py:51-61`); 346 of the repository's 356 records print byte for byte as before.

## Practice and design notes, no finding

- `results.py` now imports `LodgeError` so `ShownMany` can carry failures in place; the structure suite accepts the edge inside `app`.
- `Lodge.show` is kept beside `show_many`; after this task the command line uses only `show_many`, and `show` serves the viewer and tests (see Minor 1).
- `/var/tmp/lodge-bench/read-cache-q0hux8ou` (00:38, before the fix round's commit at 01:13) is a leftover of an interrupted pre-fix run; `read-cache-c71fkqfs` (01:32) belongs to a run in progress; neither was touched.

## Files read

`CLAUDE.md`; `.claude/agents/reviewer.md` of the main checkout; d-y94v0n (`lodge show --reasoning`); s-3n0ndk at `ea92261` and `bd7e03b`; the plan's header, Global Constraints, Calls made, and Tasks 4, 5, and the start of 6; `task-5-report.md` (both commits' versions); `task-1-2-review.md`; the progress ledger's fix-round lines; the full diffs of `ea92261` (`src/`, `scripts/`, `tests/`, report) and `8f980c9` (`src/`, `scripts/bench_reads.py`, `probes/shapes.py`, `tests/app/test_change_facts.py`, `tests/core/test_linear_checks.py`, `tests/core/test_linear_derive.py`); `src/lodge/core/codes.py`; `src/lodge/core/views.py` (`level1` to `level3`); `src/lodge/core/search.py` (ordering); `src/lodge/core/check_change.py` (`change_facts`); `src/lodge/core/fields.py` (`read_code`); `src/lodge/core/order.py` (`written_order`); `src/lodge/app/errors.py`; `src/lodge/app/state.py` (`resolve_ref`, `not_found`); `src/lodge/main.py` (`main`); `src/lodge/cli/output.py` (`_lines`); `src/lodge/viewer/pages.py` (`record_page` head); `tests/core/test_codes.py`; `tests/app/test_show_many.py`; `tests/e2e/test_show_many.py`; `tests/test_bench_cleanup.py` (test names and raises); `tests/structure_tables.py` (`CORE_MODULES`); `task-4-report.md` (timing rows).

## Files not read

`lodge spec` beyond s-3n0ndk; the Task 5 brief (`/var/tmp/lodge-build-briefs/brief-t5.md`) and the Codex logs; `tests/core/linear_change_oracle.py` beyond its use (the mutation runs show it differs from the constructor where it matters); `tests/e2e/support.py` and `conftest.py`; `tests/app/support.py` and `fakes.py`; the rest of `src/lodge/viewer/`; `tests/structure_rules.py`; the plan's Tasks 7 to 12; the other plan review and fix files.
