# Task 1 review: area rank, `rests_on`, and the derived order

Commit a3b7ebd (diff 852ba18..a3b7ebd), reviewed in a scratch detached worktree of a3b7ebd.
Counts: 0 Blocking, 2 Important, 9 Minor.

## Verdict

Every requirement of the brief is implemented with its stated values, and the gate I ran is green on the commit (`uv run pytest tests --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py`, ruff format and check, mypy, vulture).
`lodge spec` prints byte-identical output before and after (compared on 852ba18 and a3b7ebd, stdout only, 488 lines).
Two of the brief's named tests do not test what they claim (I1, I2); the code is right in both places.

## Important

**I1. Nothing tests the depth-first nesting of `derived_order`, and breadth-first passes every test.**
`tests/core/test_order.py:37-47` (the only tests with a dependant) place at most one dependant at depth 1.
The brief's rule "each followed in the same way before the next is sought" (ruling d-a3h9f3; `order.py:46-54`) is never exercised.
Verified by mutation: replacing the `while child := next(...)` loop by "collect all children, then visit each" (breadth-first) leaves `tests/core/test_order.py` and `tests/core/test_render.py` at 19 passed.
Run on the real code, written a, b, c, d with b and c resting on a and d on b gives `a, b, d, c` (d at depth 2 under b); the mutant gives `a, b, c, d`.
Fix: add `test_dependants_follow_depth_first` to `tests/core/test_order.py` with exactly that fixture, asserting ids `(A, B, D, C)` and the `(depth, under)` pairs `(0, None), (1, A), (2, B), (1, A)`.
Add a diamond (b and c rest on a, d on b and c: d at depth 2 under c) to pin `under` as the last-placed target at depth above 1.

**I2. `test_retired_target_does_not_hold_an_entry_back` passes without the retired-target filter.**
`tests/core/test_order.py:62-71` has one live entry, A, resting on the retired B.
Without the filter at `order.py:36` (`if t in ordered`), A is never "ready" but the cycle fallback (`order.py:57`, `remaining[0]`) places it at depth 0 anyway, so the assertion `== (A,)` holds.
Verified: replacing the filter by `s.entries[i].rests_on` leaves `test_order.py` fully green; only `test_cross_area_target_is_across_not_also` in `test_render.py` fails, for another reason.
Fix: add a live entry C that A does not rest on, written order `(A, C)`, and assert the result is `(A, C)` with A at depth 0 and `under is None`.
Without the filter A is not ready, C is, and the order becomes `(C, A)`, so the test then fails as it should.

## Minor

**M1. The `also` filter on retired same-area targets is untested.**
`render.py:69-71` (`d.status.get(t) == "current"`); deleting that line leaves 576 tests green.
Fix: in `tests/core/test_render.py` add a case where c rests on a live a and a retired b: `p.also == ()` and `p.under == a`.

**M2. `across` lists a retired cross-area target, while `also` drops a retired same-area one (`render.py:73-75`).**
A target retired after the link was made is shown as `rests on s-x (other)` in `lodge spec`, and nothing tests either way.
The brief says "each target that is an entry of another area", so the code follows it; the inconsistency is the brief's.
Fix: decide, and pin it with a test; if retired targets are to be dropped, add `and d.status.get(t) == "current"` at `render.py:75`.

**M3. `derived_order` recurses once per level, so a chain of about a thousand entries raises `RecursionError`.**
Run: 2000 entries each resting on the previous one gives `RecursionError` from `order.py:54`.
The brief says it "never raises on a cycle", which holds; a real area has tens of entries, so this is unlikely to bite.
Fix, if wanted: an explicit stack instead of `visit` recursion, or a one-line comment that depth is bounded by the area size.

**M4. Duplicate IDs in `rests_on` are accepted (`headers.py:104`).**
Run: `rests_on: [s-bbbbbb, s-bbbbbb]` parses to `('s-bbbbbb', 's-bbbbbb')`.
By reading (not run), `rests_on: [a, a, b]` gives `Placed.also == (a, a)`, which Task 7 would show as two links.
Fix: Task 2 should refuse or collapse duplicates with the other `rests_on` checks, or `_area` should use `dict.fromkeys` over the targets.

**M5. Docstrings are stale or missing where the rule is non-obvious.**
`render.py:25` still says `SpecArea` holds "its current entries in order"; it now holds `entries` (written) and `placed` (derived).
`Placed` (`render.py:13`), `Placement`, `area_names`, `written_order`, and `derived_order` (`order.py:15-34`) have no docstring, although the surrounding public functions (`spec_view`, `render_spec`) do; the depth-first and cycle rules live only in the plan.
Fix: one-sentence docstrings stating the fact, for example for `derived_order`: "Entries after what they rest on, depth first; a cycle falls back to the written order."

**M6. `render_spec`'s generator shadows its own parameter (`render.py:54`).**
`for target, area in p.across` rebinds `area`, the function's `area` argument, inside the expression; correct but confusing.
Fix: `for target, other in p.across` and `({other})`.

**M7. `visit` carries a redundant alias (`order.py:40-41`).**
`def visit(i, trigger=None)` then `under = trigger`.
Fix: name the parameter `under`.

**M8. `level1` runs twice per entry (`render.py:61` and `render.py:76`).**
`entries` and `placed` each call `level1(s, d, i, failing)`, and `level1` derives per call.
Fix: build `shown = {i: level1(...) for i in written_order(...)}` once and reuse it for both tuples.

**M9. Stray blank line after `def` in the new tests.**
`tests/core/test_order.py` (lines 9, 15, 20, 28, 35, 42, 50, 57, 63), `tests/core/test_area_feedback.py:6,22,28`, and `tests/app/test_writes.py:174` have an empty line between the signature and the first statement; no other test in these files does.
Fix: delete those lines (`uv run ruff format` keeps them, so remove by hand).

## Design notes (no code change needed in Task 1)

D1. **Commit trailer.** a3b7ebd ends `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; the brief's Global Constraints say the message ends `Co-Authored-By: Claude <noreply@anthropic.com>`.
The coordinator wrote it, so this is a process note only; later commits should match the brief or the brief should say otherwise.

D2. **`rank` is documented nowhere the plan reaches.**
`src/lodge/cli/guide.md:43` lists an area draft's keys as `kind`, `name`, `title`, and `order`; Task 2 adds `rests_on` sentences to the guide (plan line 169) and Task 11 asks for `rank: N` lines (plan line 584), but no task adds `rank` to the guide or README (plan line 571 mentions `spec` by rank only).
An agent writing an area draft will not learn the key.
Fix: add "and optionally `rank`, a whole number; areas with a rank come first, in rank order, ties by name" to the guide sentence in Task 2's `guide.md` list, or to Task 10.

D3. **Interfaces match the plan's Interfaces block.**
`Area.rank`, `SpecEntry.rests_on`, `read_rank`, `Placement`, `area_names`, `written_order`, `derived_order`, `Placed`, `SpecArea.placed`, and `area_feedback` all have the signatures and field order the plan states, and all are exported from `lodge.core`.
`SpecArea.entries` stays in written order for Task 7's "As written" view, and `placed` is derived order for "By dependency".
The design (line 120) says "under the first entry it rests on"; the plan's ruling 8 and the brief say the last-placed target, and the implementation follows the ruling (verified by `test_under_is_the_target_placed_last`, which fails when `under` is the first target).

## Correctness pass, requirement by requirement

- `Area.rank`, `SpecEntry.rests_on` last fields with defaults: `model.py:72,81`. Met.
- `read_rank`: `fields.py:147-151`. Probed: `2`, `"2"`, `2 # c`, `2\n`, and 40 digits read; `""`, `-1`, `1.5`, `true`, `two`, `01`, `+2`, an Arabic-Indic digit, and a bare empty value are refused with key `rank` at line 4. Met.
- Header keys: `SPEC_KEYS` gains `rests_on` read with prefix `s`; `AREA_KEYS` gains `rank`; a decision ID in `rests_on` is refused with "not a specification entry id". Met.
- Writing: `rests_on` after `title` and before `imported_from`; `rank` after `title` and before `order`; no keys written when absent, byte for byte (`test_area_without_rank_writes_as_before`, which passes before the change by design). Met.
- `area_names`, `written_order`: ranked first by `(rank, name)`, then unranked and folder-only areas by name; `written_order` equals the removed `render._area` order. Met.
- `derived_order`: matches the brief's rule on the probes I ran: dependants nest depth first, a diamond puts the dependant under the later target, a self-link and a cycle fall back without raising, a dependant of a cycle written first is placed at depth 0 (the brief's "first unplaced one"). Met.
- `spec_view`, `render_spec`: areas by `area_names`, `placed` in derived order, `also` in `rests_on` order, `across` pairs, one `rests on s-xxxxxx (area)` line after the statement. Met.
- `area_feedback` message text, `a`, `a and b`, `a, b, and c` joins, only for written area paths; wired in `writes.py:99` (one line, within the 4-line allowance). Met; the `files.keys()` argument is the changed files only, so an unchanged area file gives no note.
- `_area_notes` compares `rank`; `spec` help line verbatim. Met.
- Mutations that the tests do catch: dropping rank from `area_names`, `under` as the first target, ignoring `written_paths`, dropping `rank` from `_area_notes`, dropping the `writes.py` wiring, and not writing `rank`.

## Practice pass

- Structure rules green (`tests/test_structure.py` runs in the full pytest); `order.py` is 59 lines, `render.py` 88, `feedback.py` 198, `writes.py` 214 (+1), `parser.py` 223 (+4, the help line), no test file over 300.
- No em-dashes, no personal paths in the commit (report, brief, and final note checked); the report's `.drafts/` mentions name git-ignored scratch files and no machine.
- Test-first evidence in the report is credible: the first failures are listed per test, and the report says which one passed beforehand and why.
- Vulture is clean: `Placed.depth`, `under`, `also`, and `across` are read by `test_render.py` and `render_spec`.

## Files read

`CLAUDE.md`, `task-1-brief.md`, `task-1-report.md`, `task-1-codex-final.txt`, the plan's Task 1 and Interfaces blocks and rulings 8, 10, 31, and 32, the design lines 104 to 122, the full `git diff 852ba18 a3b7ebd`, and in the scratch worktree `src/lodge/core/{order,render,headers,drafts,feedback}.py`, `src/lodge/app/writes.py`, `tests/core/builders.py`, `src/lodge/cli/guide.md` (grep).
Not read: the other spec file `docs/superpowers/specs/2026-10-29-lodge-design.md` beyond what CLAUDE.md quotes, `yamlio.py` (its scalar behaviour was probed instead), the viewer package, the socket-bound tests (`tests/viewer/test_server.py`, `tests/e2e/test_view.py`, not run here), and `scripts/check.sh` (not run; I ran its parts individually).
