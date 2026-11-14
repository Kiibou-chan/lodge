# Task 11 review (commit 0e20687)

Angles in order: correctness, practice, design.
Scratch worktree `/var/tmp/lodge-review-11` at 0e20687, `ts/node_modules` symlinked from the main worktree; removed afterwards.

## Evidence run

- `sh scripts/check-ts.sh` in the scratch worktree: exit 0, 1234 pass, 2 todo, 0 fail (Biome, tsc, dependency-cruiser, knip, bun test).
- `grep -rn "writeThread\|isAuthor\|parseThread" ts/src` outside core: the only call is `ts/src/app/threads.ts:123`, `writeThread(thread, s.people)`; no call of `isAuthor` or `parseThread` exists outside core.
- The new rule fails a real one-argument call: with `writeThread(thread)` at `ts/src/app/threads.ts:123`, `bun test tests/structure` fails `repository_has_no_violations` with `src/app/threads.ts:123: writeThread requires explicit people` (reverted).
- Planted probes through `callViolations`: `writeThread(...args)`, `writeThread?.(x)`, `obj.isAuthor(d)` and `new Foo().isAuthor(x)` are reported; the cases in Minor 1 are not.
- Mutations: deleting `people: current.people` from `ts/src/app/writes.ts:94` gives 2 failures in `tests/app` and `tests/store`; deleting it from `ts/src/app/threads.ts:132` gives 2 failures.
- Probe over the SQLite store: `wired(store).confirm([...], "x")` throws `Forbidden: only an owner of the project confirms`, and `wired(store).ask(..., "author", ...)` throws `name a person of the project exactly, or use your own role` (see Important 1).

## Correctness

No Blocking findings.
Every Task 11 requirement of the brief is in the code: `Forbidden` (exit code 2) at `errors.ts:10`, the fifth `Lodge` argument at `lodge.ts:22`, the owner query at `read-tree.ts:41-52`, the people-based words in `threads.ts:49-70`, the impersonation refusal at `threads.ts:95`, `waitingIn` at `threads.ts:196-197`, and `confirm` at `confirm.ts:53-54` and `:65`.
Both after-states carry `people` and the two mutations above are seen by the suite.
Dependencies, `parity.json`, and `knip.json` are untouched; files are at most 264 lines in the touched set (`ts/tests/structure/calls.ts` 250); no em-dash and British English in the new text.
The three Task 6 survivors each have a test with a mutation in the report; Task 9's three minors concern files this commit does not touch (`checked-writes.test.ts`, `parity.test.ts`, `seed.ts`), so parking them again is justified.

## Important

1. `ts/tests/store/support.ts:14` creates the project with owner `ada`, while `ts/tests/app/support.ts:32` makes every `wired(store)` act as `person("author")`.
   The plan's Task 11 text says every `Lodge` of the store tests "acts as `person("author")`, the owner of their project", which does not hold: over the SQLite store `author` is not among the people, so `confirm` is `Forbidden` and a message `by: "author"` is refused (both probed above).
   No store test exercises either today, so the suite is green, but the first later task that confirms or relays a person's message through `wired(store)` over SQLite (Tasks 12 and after, plan 3's server tests) fails for a reason that is a test setup error, not a defect.
   Fix: create the store tests' project with owner `author` and move the `ada` expectations of `ts/tests/store/people.test.ts` to a project made there, or give `setup()` a `lodge` acting as the owner; one of the two, so that the plan's sentence is true.

## Minor

1. `ts/tests/structure/calls.ts:172-178` is syntactic and misses `import { writeThread as wt } from "#core"; wt(x)`, `core["writeThread"](x)`, and `const f = writeThread; f(x)`; it also accepts `writeThread(x, undefined)`.
   No call in `src` does any of these, and d-wz7fc2's cost clause accepts a narrow rule; fix if wanted: resolve the callee through `imported(expr)`-style alias tracking, or note the limit in a comment.
2. `ts/src/app/threads.ts:95` throws `Forbidden` before the reference is resolved and before the closed-thread refusal (`:117`), so a person writing as another to an unknown or closed thread gets `Forbidden` rather than `NotFound` or `is closed`.
   The brief says "after lodge 0.2's refusals", and Task 12c's mutation list (plan line 662) places the hold after the `where` and closed-thread refusals; place the check beside the closed-thread refusal so 12c replaces it in one spot.
3. `ts/src/app/threads.ts:196-197` filters `openIn(state).items` twice with `?? ""` standing in for a message-less thread; a single pass with one `people.has(...)` per thread avoids the empty-string sentinel.
4. `ts/tests/app/people.test.ts:31` asserts `new Forbidden("").exitCode` inside `an_agent_cannot_confirm`; it tests the class, not the operation, and belongs in an errors test or can go.
5. `ts/src/app/confirm.ts:53` reads the whole state before the `agent` refusal, which needs no state; the agent check can sit with the words checks above it.

Files read: the brief, the report, plan Task 11 and Global Constraints, d-wz7fc2 and d-vwsnz5, `git show 0e20687` in full for `ts/src`, `ts/tests/structure`, `ts/tests/app/{people,confirm,fakes,support}`, `ts/tests/store/{people,support}`, plus `ts/src/app/{state,threads}.ts` and `ts/tests/structure/calls.ts` whole.
Not read: the other test files of `tests/app` and `tests/store` beyond greps, `ts/src/core` beyond signatures, Task 12 and later briefs.

Verdict: 0 Blocking, 1 Important, 5 Minor
