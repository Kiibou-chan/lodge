# Brief: final fix wave, part A (the structure rules)

You fix findings of plan 1's final review and earlier parked Minors that touch the structure checks, in this repository on its current branch (`server-core`).
Read `CLAUDE.md`, then the plan's Global Constraints in `docs/superpowers/plans/2026-11-02-lodge-server-core.md`, then `final-review.md` in this folder.
Do not commit and do not push; you have no network, so never run `bun install` or `bun add`.
Your gate is `sh scripts/check-ts.sh`; run it last, and it must exit 0.
Read each ruling with `uv run --frozen --quiet lodge show <id> --reasoning`.

## What to fix

- d-d0vca9: in `ts/tests/structure/calls.ts`, outside `git`, report `write`, `writev`, and their `Sync` forms only as functions imported from `fs` (or `node:fs`, `fs/promises`, `node:fs/promises`), called by their name or through the imported namespace, renamed imports included (final review F-4); report `.write`, `.writer`, and `.delete` only on a `Bun.file(…)` call; `process.stdout.write`, `process.stderr.write`, and a method named `write` on any other receiver are allowed. The final review spells out what this needs, including the four `cli` cases at `ts/tests/structure/calls.test.ts:150-153` that must gain an import from `fs`.
- d-4vhjtt: `open` and `openSync` are a file write only when the call has a flag argument that is not a string literal or whose literal holds `w`, `a`, or `+`; without a flag argument the call is a read.
- F-2: the purity rule for `core` and `app` also reports `import.meta.env`, `self.process`, `global.process`, `globalThis.process` (if not already), `self.Math.random`, `self.crypto`, `setImmediate`, and `prompt`.
- 11-D-1 (`task-8b-9a-11-review.md`): a check that a `catch` in `ts/src/core/apply.ts` and `apply-areas.ts` rethrows anything that is not the brief's `ValueError` equivalent, as the finding's Fix says; prefer a test over the two catch sites if a structure rule cannot express it cleanly, and say which you chose.
- Task 3's parked Minor (ledger line 46): a test pinning `PACKAGES` in `ts/tests/structure/table.ts` to d-k5swcq's table, so a wrong edge fails.
- 8afix-D-2 (`task-10-12-8afix-review.md`): enforce that check results are built through `checkResult` (d-qe513h, d-snrhjs), by a structure check or a test, as the finding's Fix says.
- F-6: as `final-review.md` words it, if a check is cheap; otherwise say in the report why not.
- Every rule change gets a refusal case and an allowed case in `ts/tests/structure/calls.test.ts` (Review Focus 6), each seen failing before the change.

Touch only `ts/tests/structure/*`, the tests these findings name, and `ts/knip.json` if needed.

Write your report to `final-fix-a-report.md` in this folder: per finding, what you changed, the test, and its failing output; the commands you ran and their last lines.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.
