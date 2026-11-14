# Task 6 review

Branch `server-store-a`, build commit fada0f3 on b5545e3.
Reviewed in a scratch worktree of fada0f3 (removed), with `ts/node_modules` symlinked from the lane worktree.

## Ran

- `sh scripts/check-ts.sh` in the scratch worktree: exit 0, Biome, `tsc`, dependency-cruiser, knip, and `1176 pass`, `2 todo`, `0 fail`.
- 24 mutations of `ts/src/app/confirm.ts` against `bun test tests/app/confirm.test.ts` (one at a time, reverted): 20 killed, 4 survived (findings 1 to 4).
- Killed: no `cleanText`; no CRLF refusal; scope always process, always product; single-id `confirmableIds` test dropped; length check dropped; commit flag ignored; staged test ignored; commit message and paths changed; empty-words check dropped; `ValueError` not wrapped; area `notFound` dropped; entries not deduplicated; unknown entries kept; `StaleList` changed to `Conflict`; stale message shortened; the area not passed to `confirmationDraft`; area precedence removed; area order reversed.
- Two mutations of `lodge.ts`: `behindArea` pinned to `"storage"` is killed; `commit = true` as the default survives (finding 3).
- Front door: printed the 23 Python names and the 38 exports of `#app`; the test is not vacuous.
- Probes (scratch tests, deleted): `confirm([])`, `confirm(["d-zzzzzz"])`, and duplicate ids over two decisions all throw `StaleList` with the right message; an unknown area throws `NotFound`.

## Correctness

Every one of the 19 Python test functions is ported, 21 cases with the two parametrised tests.
Each assertion is kept: error class and message both asserted through `raises` (`ts/tests/app/support.ts:36`, which awaits `toThrow(Class)` and then `toThrow(pattern)`), `store.publishes` and `store.commits` emptiness kept, `quote?.text` and `reasoning` compared to the CRLF-normalised words, and the two ids' order in `confirms`.
No test is weakened or deferred.
`confirmDecisions` matches `confirm.py` line by line: clean, CRLF refusal, empty refusal, one read, expected ids, staleness, scope, draft with `ValueError` wrapped, `add` with defaults, commit only when `STAGED` and requested.
`behindArea` matches, including the not-found rule and the entry dedup.
The set-equality test of Python (`set(ids) != set(expected)`) becomes a length test plus a subset test; the two are equal while `coreBehindArea` returns distinct ids.

## Findings

1. Minor. `ts/src/app/confirm.ts:55`, survivor: dropping `!expected.length ||` passes every test.
   Scenario: `confirm([], "Read.")` on a store with nothing confirmable would then reach `confirmationDraft([])` and fail with `LodgeError("your words hold a character lodge cannot store")` (confirmed by running it) instead of `StaleList`, a wrong class and message for the viewer's 409.
   The Python tests have the same gap, so the port asserts no less.
   Fix: one test, `confirm([], "Read.")` and `confirm(["d-zzzzzz"], "Read.")` rejecting with `StaleList` and the stale message, `publishes` empty.
2. Minor. `ts/src/app/confirm.ts:55`, survivor: dropping `expected.some((id) => !given.has(id))` passes every test.
   Scenario: `confirm([A, A], …, { area })` where the area is behind on A and B has two ids in the list, equal in length to the expected two, so it would confirm A and B from a list that named only A.
   Fix: a test with two decisions behind the area and ids `[A, A]` (probed: current code answers `StaleList`).
3. Minor. `ts/src/app/lodge.ts:101`, survivor: changing the default `commit = false` to `true` passes every test.
   Scenario: `second_identical_confirmation_is_stale` and `second_area_confirmation_is_stale` use a staged store with the default and never assert `store.commits`, and `confirm_one_decision` uses an unstaged store, so a default that commits staged writes is invisible.
   Fix: in `second_identical_confirmation_is_stale`, assert `store.commits` equals `[]` after the first confirmation.
4. Minor. `ts/src/app/confirm.ts:16`, survivor: replacing the "no entry in the area" half of the not-found test with `true` passes.
   Scenario: an area with entries but no area file would answer `NotFound` after a regression, and no test pins that `behindArea` accepts it.
   Also `[[VIEWER, draft]]` (`confirm.ts:69`) is unpinned: a different source name for the draft passes every test.
   Both gaps are Python's; park them for a round touching the file.
5. Minor. `ts/tests/app/front-door.test.ts:25-31`: the `m[1] === m[1]?.toUpperCase()` branch never runs (no all-capitals name in `__all__`), and `name ?? ""` and the `?.` chains on `names` only satisfy the types.
   Fix: write `snake.replace(...)` over a `string` obtained once, dropping the dead branch.
   The `extras` set also names six later-task exports that nothing checks exist, as the brief allows.
6. Minor. `ts/src/app/confirm.ts:11-17`: `behindIds` and `behindArea` read `s.decisions.get(id)?.changes` where Python indexes and would raise `KeyError`; an id from `coreBehindArea` is always a decision, so the `?.` hides a broken invariant as an empty entry list.
   Fix: none needed now; note it.

## Practice

Modules are 73, 108, 209, and 62 lines, well under 300.
Fixtures are the made-up `storage` area; no personal paths, no em-dashes, in the six files (grep run).
The `confirmDecisions` rename is justified by the structure guard on the global `confirm` (`ts/tests/structure/calls.ts:37`) and kept off the public `Lodge.confirm`.
The comment states the fact (callers serialise, retries and commit included).
The report is accurate: 19 functions, 21 cases, mutation table for the two front-door tests, and test-first failure for the rest; the `index.ts` Modify of the brief was a no-op and the report says so.
The commit carries the Codex trailer, the explicit paths, and the author identity the brief names.

## Design

`confirm.ts` imports only `#core` and siblings; `lodge.ts` takes it as `* as confirmations`, as `reads`, `threads`, and `writes` are taken.
The parity row flips with `"task": ["6"]` and every `tests/app/` row is now `ported`, `changed`, or plan 3's.
No plan rule goes unenforced here apart from the "callers serialise" rule, which no TypeScript test can enforce until plan 3's API holds the lock.

Verdict: 0 Blocking, 0 Important, 6 Minor
