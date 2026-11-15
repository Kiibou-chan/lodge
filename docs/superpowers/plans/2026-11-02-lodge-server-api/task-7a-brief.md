Read `CLAUDE.md` in this worktree first, then the plan header, "Global Constraints", "Exports read in a later task", "Calls made", "Order and lanes", and "### Task 7a" in full in `docs/superpowers/plans/2026-11-02-lodge-server-api.md` (your requirements, with every printed line and exact value to use verbatim), and the "Parity" section for the rows of this task.

Outcome: `lodge` runs every command except `server` against the server over `io.fetch`, printing lodge 0.2's lines, with the carried end-to-end tests passing in process against `testServer()`, and the guide, `Io`, `run`, `fromWire`, `Call`, and `runThread` exported through `#cli` as the plan's Interfaces give them.

Scope: the files of the plan's Task 7a "Files" list, and nothing else; `ts/src/api` is read only (a defect there goes to the ask tool); `ts/src/main.ts` and Task 8 are out of scope.
The sandbox rule holds: no test in the gate opens a socket (the `LODGE_E2E_BINARY` mode is S1's).
Modules stay at 300 lines or fewer; Biome runs with `--error-on-warnings`; `bun install --frozen-lockfile` is allowed, never `bun add`; never edit earlier briefs, reports, or reviews.

Evidence, beyond the plan:
- `reply` and `close` send `thread: command.ref` (the grammar's field, `ts/src/cli/grammar-threads.ts`).
- `orphaned_thread_outputs` keeps its `MemoryStore`: `const store = project(); wired(store)`, as `ts/tests/app/thread-fix-paths.test.ts` has it today; the two `test.todo`s there become tests (d-rp74dr).
- Lane C starts from `server-api` with Tasks 2, 3, 5, and 6 merged: `parse` (`grammar.ts`), `readSettings`, `serverOf`, `tokenOf`, `readDraft`, `readExact` (`#cli`), `handler`, `toWire`, `issueSetupCode`, and the `SoftAuthenticator` of `ts/tests/api` are there to use; `ts/tests/api/world.ts` shows how `lodgeFor` and the handler are wired.
- Python sources: `src/lodge/cli/{commands,output,thread_output,threads}.py`, `src/lodge/cli/guide.md`, `tests/e2e/*.py` named in the plan.

Test-first: write the plan's Step 1 tests (the carried files, `client.test.ts`, `wire.test.ts`, the `dropped` parity tests) and the helpers `server.ts`, `project.ts`, `support.ts`; run `cd ts && bun test tests/e2e tests/cli tests/parity.test.ts` and see the new tests fail before the code.
Every ported function of `output.py`, `thread_output.py`, `commands.py`, and `threads.py` is pinned by a carried test or seen failing against a mutation the report names, then reverted (d-zthdm7).

Done when `sh scripts/check-ts.sh` exits 0, your `parity.json` rows are written, and it is green again; write `docs/superpowers/plans/2026-11-02-lodge-server-api/task-7a-report.md` as Step 4 says (each test that approves a held add, every substitution of d-bwb1tt and change of d-4qv0xb by test, every output that differs from lodge 0.2 with its reason, the map of ported functions to tests, and each mutation run); commit with explicit paths as `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, and push `server-api-c`; do not run the Coordinator step.
Unsettled design goes to the ask tool.
