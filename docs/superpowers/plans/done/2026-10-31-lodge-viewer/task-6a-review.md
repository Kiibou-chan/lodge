# Task 6a review

Reviewer: Opus-class reviewer, first review of commit 978fdfd (`git diff 2bafed4 978fdfd -- src tests`).
Verdict: 0 Blocking, 3 Important, 7 Minor.

## Method

I ran everything in a scratch detached worktree of 978fdfd, since removed.
The builder's gate ran green there: ruff format, ruff, mypy, vulture, and `pytest -q` without the two socket files (1249 passed).
I probed `Lodge.confirm` with 23 awkward word strings and one simulated rival write, and I mutated the code nine ways to see which tests notice.
The probe test file is not kept, and no tracked file was edited.

Files read: the brief, the report, the plan's Review Focus 1 and 2 and rulings 22 to 23, the design's Confirming section and must-nots, `src/lodge/core/{confirmation,drafts,document,headers,derive,views,yamlio,threads,check_state}.py`, `src/lodge/app/{confirm,writes,threads,results,reads,lodge,errors,state}.py`, `tests/app/{test_confirm,fakes,support}.py`, `tests/core/{test_confirmation,builders}.py`.
Files not read: the gitstore implementation (`CheckoutStore.commit`, `publish`), the viewer package, Task 6b's code (only its brief), and the e2e and socket tests.

## Correctness

Holds, each checked by running it:

- `decided_by: author` and `confirms` are exactly the listed decisions, in date order, from `expected` and not from the submitted `ids` (`src/lodge/app/confirm.py:65-66`; mutating this to `ids` fails a test).
- The title and statement are lodge's fixed text; her words reach only `quote.text` and the reasoning, and the draft is written once (`src/lodge/core/confirmation.py:49-56`).
- The scope rule follows the design (`confirm.py:58-62`), though no test pins "any" (I1).
- The stale list is refused before anything is written, including a repeat against staged files, and an unknown area is `NotFound`.
- Review Focus 2: 22 of 23 probe strings kept `quote.text == reasoning == clean_text(words)`, among them a line `## Reasoning` (alone and with trailing spaces), a line `---`, `<script>`, a colon, `#`, quotes, backslashes, tabs, a lone CR, a 20,000-character text, an astral emoji, and a BOM.
  `U+2028`, `U+0085`, `U+000C`, `U+007F`, a lone surrogate, and NUL were refused with the one sentence and nothing published.
- `Written.check` carries a failed check, and no commit is made unless the outcome is `STAGED`.

### Important

**I1. Four required behaviours have no test that fails without them.**
I mutated the code and ran `tests/core/test_confirmation.py tests/app/test_confirm.py`; each of these still passed all 20 tests.

- Scope "any": `any(...)` replaced by `all(...)` at `src/lodge/app/confirm.py:61`.
  `test_scope_product_when_any_listed_is_product` (`tests/app/test_confirm.py:54`) lists two product decisions, and the process test lists one, so `all` and `any` agree on both.
  Scenario: an area with one product and one process decision would be recorded as `process` and nothing would notice.
  Fix: make `OTHER` process-scope in that test (`replace(OTHER, scope=Scope.PROCESS)`) and assert `PRODUCT`.
- Date order: the sort key replaced by `lambda i: i` at `src/lodge/core/confirmation.py:30`.
  In `test_behind_area_lists_creators_and_last_changers_oldest_first` (`tests/core/test_confirmation.py:28`) the IDs and dates rise together, so the test named "oldest first" cannot tell dates from IDs (design line 51; the brief's `(datetime.fromisoformat(date), id)`).
  Fix: give the older decision the larger ID (`d-cccccc` at `at(0)`, `d-aaaaaa` at `at(2)`) and expect `("d-cccccc", "d-aaaaaa")`; add a same-date pair to pin the ID tie-break.
- Commit gating on the outcome: `and commit` or the `STAGED` test deleted at `src/lodge/app/confirm.py:72`.
  `test_commit_after_staged` only runs the one combination that commits (`tests/app/test_confirm.py:115`).
  Scenarios: `commit=True` on a branch-mode store (outcome `PUBLISHED`) must call no `commit`, since `add` already published; `commit=False` on a staged store must leave the file staged.
  Fix: two tests asserting `store.commits == []` for those two cases.
- A failed check: no test makes `writes.add` return `CHECK_FAILED` through `confirm`, though the design says "a failure shows on the page with nothing written" and Task 6b's `test_failed_check_answers_400_and_writes_nothing` depends on `Written.check` and `outcome`.
  Fix: one test with a newest decision dated more than three seconds ahead of the clock (so check 1 refuses), asserting `outcome is CHECK_FAILED`, `not result.check.ok`, `store.publishes == []`, and `store.commits == []` with `commit=True` on a staged store.

**I2. Review Focus 2 names a line `## Reasoning`, and no 6a test carries one.**
The behaviour is right (probed), so this is a missing pin: `test_words_with_specials_kept_verbatim` (`tests/app/test_confirm.py:98`) holds quotes, a backslash, `#`, brackets, a tab, and a lone CR only.
Scenario: a later change to `split_reasoning` or to the draft layout (`src/lodge/core/confirmation.py:55`) could cut her words at her own heading, and the reasoning would no longer equal the quote.
Fix: add to that string a line `## Reasoning` and a line `---`, with another text after each.

**I3. The stale-list check is not atomic with the publish, and `confirm` does not say so.**
Probe: with `store.reject_next(...)` landing a second author confirmation of the same decision after the check, `writes.add` retries from a fresh read (`src/lodge/app/writes.py:46-56`) without asking again, and the store ended with two author decisions confirming `d-aaaaaa`.
Review Focus 1 says the second confirmation writes nothing "even when both arrive at once"; 6a alone cannot promise that, and the ledger (line 16) rests it on Task 6b's one module-level lock.
That lock serialises one viewer process; a second `lodge view` on the same checkout, or her own CLI write, can still interleave, and the result is a duplicate confirmation (harmless to the record, noise in the history).
Fix: put one sentence on `confirm` (`src/lodge/app/confirm.py:37`) that the list is checked once, before the publish, and that the caller serialises confirmations; keep Task 6b's concurrent test (`test_two_concurrent_confirmations_write_once`) as the real guard.
I do not ask for a recheck inside `writes.add`, which is at 214 of 300 lines; I rate this Important only because the focus names it and the guarantee lives in a later task.

## Minor

**M1. `clean_text` leaves a CR before an LF for `\r\r\n`, so the quote and the reasoning differ.**
`src/lodge/app/confirm.py:44` calls `clean_text` (`src/lodge/core/threads.py:143`), a single `replace("\r\n", "\n")`, and `"a\r\r\nb"` becomes `"a\r\nb"`.
The quote keeps `"a\r\nb"`, the file reader's `normalise_newlines` turns the reasoning into `"a\nb"` (probed), which breaks "reasoning equal to her words" (design line 60) and "a CR before each LF" is not gone.
A browser textarea never sends `\r\r\n`, so only a hand-made request reaches it.
Fix: in `confirm`, after cleaning, refuse a text that still holds `"\r\n"` with the existing "your words hold a character lodge cannot store" sentence, or loop `clean_text` until stable (a Task 3 change, so the author of that task should agree); add the string to the specials test.

**M2. `tests/app/test_confirm.py:72` tests the wrong stale shape.**
`test_stale_area_list_writes_nothing` submits an extra decision that is not in the store at all (`OTHER`), not "one of them has since been replaced or confirmed" (design line 52) or "a decision has joined the list".
Fix: submit `[AGENT, OTHER]` with both in the store, then confirm `OTHER` (or add a third decision) and assert the stale refusal.
Also missing: the area path for a repeated submission (the second area confirmation finds an empty list), duplicate IDs (`[A, A]` passes with the length check deleted, which then writes a correct confirmation, so that line is strictness only), and the two-item "and" form (`" and ".join` replaced by `", ".join` passes).

**M3. The ordering expression repeats `derive.order_key`.**
`src/lodge/core/confirmation.py:30` builds `(datetime.fromisoformat(s.decisions[i].date), i)`; `src/lodge/core/derive.py:101` already defines `order_key(d)` with the same value, and the module already imports from `lodge.core.derive`.
Fix: `sorted(found, key=lambda i: order_key(s.decisions[i]))`, which also drops the `datetime` import.

**M4. The minute format is written twice.**
`src/lodge/app/confirm.py:66` and `src/lodge/app/threads.py:35` both spell `"%Y-%m-%d %H:%M"`; the viewer's two kinds of author record must agree on it (brief: "the clock's minute").
Fix: one constant or helper in `core` (for example `MINUTE_FORMAT`) used by both.

**M5. The nested conditional in `confirm` is hard to read.**
`src/lodge/app/confirm.py:48-56` is a three-level conditional expression followed by a four-part refusal.
Fix: extract `_expected(state, ids, area) -> tuple[str, ...]`, and rename `_behind` (`confirm.py:13`) to `_behind_ids`, since `behind_area` in the same module returns `Behind` rows.

**M6. `behind_area` and `confirmation_draft` carry no docstring for their rule.**
`src/lodge/core/confirmation.py:22` selects on "created, or `changed_by[0]`", and `:33` takes `area=None` to mean "one decision" (with several IDs and no area the title silently names the first).
Fix: a one-line docstring on each, and `confirmation_draft` raising `ValueError` for `area is None and len(confirms) != 1`.

**M7. The report's "first failing run" is a collection error.**
The report says each test "had the import failure above on the first run"; both files stopped at collection, so no test was seen failing on its own assertion, and I1 shows several would not have.
Process note for the next brief: ask for the first run to import-stub the new names, or to run each test against a body that returns a wrong value, so that the assertion is what fails.

## Design

What 6b and 7 consume is what the plan says, with these notes:

- `StaleList` is a `Conflict`, itself a `LodgeError`: 6b must catch `StaleList` before the generic `LodgeError` branch, or the stale redirect becomes a 400.
- `Written.about` is `None` for a confirmation (`src/lodge/app/confirm.py:76`); 6b's redirect must come from the form's own page, not from `about`.
- A confirmation with no IDs, or several IDs and no area, raises `StaleList` with the "list changed" sentence (`confirm.py:57`); 6b's early validation (an `id` field that is a `d-` ID) keeps a malformed form from showing that message, but a form with zero `id` fields needs its own 400 there.
- `behind_area` takes `changed_by[0]` whatever its status (`src/lodge/core/confirmation.py:28`); `changed_by` includes replaced decisions (`derive.py:50`), so an entry whose newest changer was replaced by a decision that does not list the entry has no "last changer" in the list, only its creator.
  This follows the plan's wording and is rare; Task 7 or the author should know it before the 82 entries are confirmed.
- Core purity, front doors, and the 300-line rule hold (`confirm.py` 76 lines, `confirmation.py` 56, `lodge.py` 119, `test_confirm.py` 148); no existing test assertion changed.
