# Task 3 fix round 1 report

Fixed C1, PR1, PR2, and PR3 on `server-store-a`.
D1 remains assigned to Task 4, as the fix instructions require.
The explicit commit and push instructions in this fix request take precedence over the earlier brief's contradictory builder restriction.

## Changes

- `ts/tests/app/support.ts`: added `raises(promise, errorClass, pattern)`, awaiting both the class and message assertions on the same promise.
- `ts/tests/app/writes.test.ts`: all carried message-matching refusals now use `raises`, including the four missing class checks identified by C1.
- `ts/tests/app/writes-attach.test.ts`: all carried message-matching refusals now use `raises`, including the five missing class checks identified by C1 and all six invalid-name cases.
- `ts/src/app/ports.ts`: corrected the `gate` comment to describe the states the gate compares and the origin of `current` (PR1).
- `ts/src/app/writes.ts`: gave `required` a description argument, distinguishing a missing minted ID, written ID, applied decision, and applied record (PR2's proposed generic-helper option).
- `ts/src/app/lodge.ts`: declared `Lodge.add`'s return type as `Promise<Added>` (PR3).
- `ts/tests/app/errors.test.ts`: removed both optional chains after the guard excludes `undefined` (PR3).

## Test-first evidence

The strengthened assertions were written before the production clean-ups.
They passed against the existing implementation, then each specified mutation was applied separately, tested, and reverted in a `finally` block before the next run.
Each mutation changed only the indicated `throw new LodgeError` to `throw new Error`, preserving its message.
The line numbers below are the review's original handles.

Command for each run: `cd ts && bun test tests/app/writes.test.ts tests/app/writes-attach.test.ts`.

| Original site in `ts/src/app/writes.ts` | First failing test or group | Result | Exit |
|---|---|---|---|
| 143, attachment count | `attachment_needs_exactly_one_new_decision` | 23 pass, 1 fail | 1 |
| 146, plain file name | `attachment_names_are_plain_file_names`, all six cases | 18 pass, 6 fail | 1 |
| 156, listed attachment names | `decision_must_list_exactly_the_attached_names` | 23 pass, 1 fail | 1 |
| 174, empty drafts | `add_refuses_unreadable_or_unusable_drafts` | 23 pass, 1 fail | 1 |
| 206, exhausted ID draws | `mint_gives_up_after_ten_draws` | 23 pass, 1 fail | 1 |

The clean focused run before mutations ended with `24 pass`, `0 fail`, and `77 expect() calls`.
After mutations, redundant standalone class assertions were removed from the two cases now using the helper.
No new behavioural tests were needed for the comment, explicit return type, narrowed property access, or invariant-message clarification.
No carried tests were omitted or weakened, and no TypeScript parity exceptions were introduced.

## Commands and verification

- `uv run --frozen --quiet lodge waiting`: nothing waiting for an agent or the author.
- `cd ts && bunx --no-install biome check --write src/app/ports.ts src/app/lodge.ts src/app/writes.ts tests/app/errors.test.ts tests/app/support.ts tests/app/writes.test.ts tests/app/writes-attach.test.ts`: `Checked 7 files`, `Fixed 3 files`.
- The first full gate caught the helper's overly broad `typeof Error` annotation: `TS2345`, because `ErrorConstructor` also requires a callable signature that `LodgeError` does not have.
- The helper now accepts a constructor signature, `new (message: string) => Error`.
- Final `sh scripts/check-ts.sh`: exit 0; Biome clean, TypeScript clean, no dependency violations across 140 modules and 467 dependencies, knip clean, `967 pass`, `0 fail`, and `2419 expect() calls` across 68 files.

Earlier briefs, reports, reviews, and unrelated untracked logs were left untouched.
No outstanding concerns within this fix round's scope.
