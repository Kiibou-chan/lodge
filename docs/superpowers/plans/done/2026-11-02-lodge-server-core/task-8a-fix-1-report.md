# Task 8a, fix round 1 report

Implemented the findings within this lane, without committing, staging, pushing, installing packages, or accessing the network.
The supplied brief was already untracked and is left unchanged.
`ts/src/core/index.ts` is unchanged, and both new exports remain inside the package.

## Findings and evidence

### 8a-D-1: shared check result construction

`check-state.ts` exports `checkResult(problems, notes)`, which computes `ok` as plain data.
`checkState`, `checkChange`, and the two result fixtures in `views.test.ts` use it.
A source search found no other result constructors outside this factory, apart from expected values in assertions.
`check_result_computes_ok_from_problems` asserts the whole failing and clean results, including notes.
Its initial run failed with `SyntaxError: Export named 'checkResult' not found`.
A temporary constructor spreading the original getter-bearing clean `checkState` literal and overriding `problems` and `notes` then failed with this output:

```text
- "ok": false,
+ "ok": true,
(fail) check_result_computes_ok_from_problems
0 pass, 1 fail
```

The changed view tests were also run with their problem inputs temporarily emptied.
`failing_ids_maps_paths` failed with expected two IDs and received `Set {}`, and `unrecorded_problem_for_unparsable_file` failed with expected the broken-file problem and received `[]`.
That run ended `0 pass, 2 fail`.
All mutations were reverted.

### 7a-D-2: shared ordering comparator

`derive.ts` exports `compareOrderKeys`, comparing the instant from `orderKey` through `orderInstant`, then IDs with `byCodePoint`.
Derivation, confirmation ordering, and confirmation clearing use it.
`views.ts` uses the comparator with equal comparison IDs, preserving Python's instant-only changed-since condition.
The existing `same_second_change_does_not_mark_changed_since` test passes.
`orderKey` is now private because its external readers use the comparator instead, as required by the no-unused-exports constraint.
No knip exception was added.

The existing C-1 regression `orders_by_instant_across_offsets_then_by_id` was exercised before the refactor.
Dropping the tie-break failed with expected `d-bbbbbb, d-aaaaaa`, received `d-aaaaaa, d-bbbbbb`.
Comparing date text instead of instants failed with expected `d-dddddd, d-cccccc, d-bbbbbb, d-aaaaaa`, received `d-bbbbbb, d-cccccc, d-aaaaaa, d-dddddd`.
Both runs ended `0 pass, 1 fail`, and both mutations were reverted.

### 7b-P-1: exception inheritance

`confirmation_draft_empty_area_list_keeps_python_index_error` now asserts `toThrow(LookupError)` and the required message directly.
Changing `IndexError` to extend `Error` before the implementation changes produced:

```text
Expected constructor: LookupError
Received constructor: IndexError
Received message: "list index out of range"
0 pass, 1 fail
```

The production inheritance already satisfied the requirement and is preserved.

### 8a-P-1: helper invariant

`oldDecision` now checks `old?.kind` and throws `Error("expected Decision")` before returning, replacing the cast.
The new `old_decision_requires_a_decision` test verifies the helper's result.
Temporarily changing the original unchecked helper to return element zero instead of element two failed with `Expected: "decision"`, `Received: "area"`, and `0 pass, 1 fail`.
An earlier attempt at this mutation was obscured by the not-yet-added constructor export, so it was rerun successfully after that export existed.
The mutation was reverted before adding the guard.

### 8a-D-2: ordering and de-duplication

Added `check-state-order.test.ts` beside the existing near-limit test file, and listed it beside that file in `parity.json`.
`problems_sort_by_path_check_and_message_and_deduplicate_links` asserts the whole problem list, including paths, check numbers, messages, kind, and line.
It combines repeated missing `rests_on` and attachment targets with deliberately shuffled problems.
U+E000 and U+1D518 in paths and messages distinguish code point order from UTF-16 order.
Each mutation below was applied alone and reverted.

| Mutation | Failing output |
| --- | --- |
| Remove the sort | First problem expected decision path/check 1, received entry path/check 3 |
| Drop path comparison | Expected decision-path problem first, received a different-path problem |
| Drop check comparison | Expected check 1, received check 2 |
| Drop message comparison | Expected U+E000 before U+1D518, received the reverse |
| Use UTF-16 relational comparisons | Both Unicode paths and messages reversed |
| Remove `rests_on` set | Received an extra missing-target problem |
| Remove attachment set | Received an extra missing-attachment problem |

Every run ended `0 pass, 1 fail`.
The six structural mutations were rerun against the final Unicode fixture; the UTF-16 mutation was run separately against that fixture.

### Parked Minors

8a-P-2 explicitly assigns deletion of the duplicate cycle test to Task 8c when it carries the link tests.
This lane leaves that test alone.
7b-D-1 assigns minute formatting instructions to plan 2's briefs.
This lane preserves `MINUTE_FORMAT` and does not edit future briefs.
These are the review's prescribed deferrals, rather than unresolved defects in the requested files.

## Commands and outcomes

Commands used for inspection included `cat`, `sed`, `rg`, `git diff`, and `git status --short` over the required briefs, reviews, source files, tests, and configuration.
`uv run --frozen --quiet lodge waiting` ended with `waiting for the author` / `nothing`, and also reported nothing waiting for an agent.
`uv run --frozen --quiet lodge show d-qe513h --reasoning` confirmed both shared constructors/comparators and their package-internal scope.
Temporary Python scripts under `/tmp` applied, ran, captured, and reverted each mutation in a `finally` block.
No script was added to the repository.

| Command, from `ts` unless stated | Last lines / outcome |
| --- | --- |
| `bun test tests/core/check-state-order.test.ts` before implementation | `0 pass`, `1 fail`, `1 error`; missing export |
| `bun test tests/core/check-state-order.test.ts -t check_result` with stale getter spread | `0 pass`, `1 fail` |
| `bun test tests/core/check-state-order.test.ts -t problems_sort` for each sort/de-duplication mutation | `0 pass`, `1 fail` per run |
| `bun test tests/core/check-state-order.test.ts -t old_decision` with helper reorder | `0 pass`, `1 fail` |
| `bun test tests/core/confirmation.test.ts -t confirmation_draft_empty` with inheritance mutation | `0 pass`, `1 fail` |
| `bun test tests/core/derive.test.ts -t orders_by_instant` for both ordering mutations | `0 pass`, `1 fail` per run |
| `bun test tests/core/views.test.ts -t "failing_ids_maps_paths\|unrecorded_problem_for_unparsable_file"` with empty problem inputs | `0 pass`, `2 fail` |
| `bunx --no-install biome check --write` on changed TypeScript and JSON files | `Checked 10 files`; fixed formatting in five files |
| `bunx --no-install knip` before making `orderKey` private | `Unused exports (1): orderKey`; exit 1 |
| `bunx --no-install biome check --write tests/core/check-state-order.test.ts tests/core/checks.ts src/core/derive.ts` | `Checked 3 files`; no fixes applied |
| `bun test tests/core/check-state-order.test.ts tests/core/confirmation.test.ts tests/core/views.test.ts tests/core/views-links.test.ts tests/core/derive.test.ts tests/parity.test.ts` | `65 pass`, `0 fail`, `462 expect() calls`, six files |
| `git diff --check`, repository root | No output; exit 0 |

One temporary evidence script initially failed with `NameError: name 'Path' is not defined`; its import was corrected, and the affected evidence runs were repeated.
No TypeScript limitation prevented any requested test.
The cloud runtime skill was read, but no environment-status tool is exposed in this session; no network operation was needed.

Final required gate result follows.

The first gate exited 2 at TypeScript: indexed expected problems had type `Problem | undefined`.
The fixture is now a fixed readonly tuple (`as const`), preserving the same values and assertions.
The final gate was rerun after this type-only correction.

Final `sh scripts/check-ts.sh` exit: 2.

```text
$ biome check --error-on-warnings . && tsc --noEmit -p . && depcruise src tests --config .dependency-cruiser.cjs && knip && bun test
Checked 89 files in 67ms. No fixes applied.

  [31merror[39m front-door: [1mtests/core/views.test.ts[22m → [1msrc/core/check-state.ts[22m
  [31merror[39m front-door: [1mtests/core/check-state-order.test.ts[22m → [1msrc/core/check-state.ts[22m
[31m
x 2 dependency violations (2 errors, 0 warnings). 97 modules, 308 dependencies cruised.
[39m

```

## Blocker: internal constructor versus test import boundary

Status: BLOCKED.
The final gate exits 2 at dependency-cruiser, after Biome and TypeScript pass.
It reports `front-door` for both `tests/core/views.test.ts → src/core/check-state.ts` and `tests/core/check-state-order.test.ts → src/core/check-state.ts`.
The last line is `2 dependency violations (2 errors, 0 warnings). 97 modules, 308 dependencies cruised.`

The mandatory new test must call `checkResult`, and the existing view fixtures must also use that constructor rather than hand-built results.
The constructor must stay package-internal, and the brief expressly forbids editing `ts/src/core/index.ts`.
However, `ts/.dependency-cruiser.cjs` requires every test-to-source import to use the package front door, and `#core` resolves to that unchanged index.
The Global Constraints also forbid relative imports leaving a package and loosening structure rules.
There is no permitted import path for these required constructor calls under the current requirements.
No alias, dynamic import, or subprocess workaround was introduced to evade that boundary.

The narrow resolution needs a coordinator ruling allowing either `checkResult` through the front door or a narrowly scoped internal-test import policy and its configuration changes.
Neither change is authorised by this brief's explicit file and export restrictions.
The implementation and failing boundary diagnostics are left reviewable; no commit or push was made.
The green focused tests above precede this discovery and do not establish a passing full gate.
