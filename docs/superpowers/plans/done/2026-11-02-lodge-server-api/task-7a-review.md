# Plan 3, Task 7a: review

Range `03383f6..e40f55a` (one commit), plus `task-7a-report.md`.
Passes in order: correctness, practice, design.
This is a checkpoint review: Task 7a changes the `#cli` front door that Tasks 7b and 8 and plan 4 consume.

## Verdict

0 Blocking, 1 Important, 8 Minor.
The Important finding is marked [CODEX-MISS]; Codex's two Important findings are not repeated.

## Verification statement

- Gate run on a detached scratch copy at e40f55a: `sh scripts/check-ts.sh` is green (1741 pass, 0 fail, 4768 expects, 147 files).
- Biome reports 16 infos about literal-key access.
  The same pattern is in `src/api` and `settings.ts`, so it is not new and not a finding.
- Mutations and probes ran on the scratch copy only; the branch was not edited.
- Not exercised: `LODGE_E2E_BINARY` socket and binary mode.

## Correctness

### Important

**I1 [CODEX-MISS]. No test pins that `init` sends the settings' `core` table.**
Handle: `ts/src/cli/commands.ts:77`, `await call("project-create", { settings: settings.core });`.
The plan says `init` sends `project-create` with the settings' `core` table.
Mutation: replacing the argument with `{ settings: {} }` leaves all 250 targeted tests green (`bun test tests/e2e tests/cli tests/app/thread-fix-paths.test.ts tests/parity.test.ts`).
Failure scenario: `[length]` or `[import]` values in `.lodge.toml` are silently dropped, and the project is created with defaults.
The report's mutation M15 covers only the printed `init` line.
Probe: a test that writes `[length]\ntitle_chars = 40`, spies on the request body, and expects `{project: "work", settings: {length: {title_chars: 40}}}` passes on the original and fails on the mutant.
Fix: add a case to `ts/tests/cli/client.test.ts` that asserts the `project-create` body from a non-default `.lodge.toml`.

### Minor

**M1. Mutation survivors in the targeted suite.**
These are untested behaviours, all low risk.
- `ts/src/cli/threads.ts:27`: replacing `raises: command.raises` with a constant `"doubt"` survives.
  7a asserts the `thread` field for reply and close, not `raises` for ask.
  Task 7b's thread tests may cover it; if not, add one.
- `ts/src/cli/client.ts:24`: dropping the `.replace(/[\r\n]+/gu, " ")` on the `cannot reach` message survives, because the test message has no newline.
  Fix: use a multi-line error message in the test.
- `ts/src/cli/output.ts:101`: the `"none recorded"` fallback survives (Codex noted this too).
- `importing: command.importing` hard-coded to false survives in 7a; 7b's `add-import` covers it.
- Dropping `resolve(io.cwd, name)` in the draft read survives.
  The tests pass absolute draft paths, and the only relative-path test uses a nonexistent file whose error text is restored by the name-restoring code.
  Fix: one test with a relative draft path and a non-default `io.cwd`.

**M2. `client()` throws an uncaught `TypeError` instead of a one-sentence `CliError` on a malformed answer.**
Handle: `ts/src/cli/client.ts:37-44`.
`run` rethrows anything that is not a `CliError`, so the user sees a stack trace.
Scenarios, each needing a malformed server answer (low likelihood):
- A response with a `Lodge-Version` header and a JSON body of `null` gives `TypeError: null is not an object (evaluating 'answer.result')`.
- A 200 with no `result` makes `id` print `undefined\n`.
- A `check-failed` answer without `result` gives a `TypeError` in the `check` case's `[result, read]` destructuring in `commands.ts`.
- A malformed `search` result crashes on `read.freshness`.
Fix: after `response.json()`, require an object, and for a 200 or `check-failed` require a `result` key; otherwise throw `CliError(`${url} answered something other than JSON`)` or a similar sentence.

**M3. A token with an embedded newline makes `new Request` throw an uncaught `TypeError`.**
Handle: `ts/src/cli/client.ts:12`, outside the `try` that starts at line 21.
Probe: `LODGE_TOKEN="ab\ncd"` gives `TypeError: Header '14' has invalid value`.
A trailing newline (`"abc\n"`) and a non-ASCII token were both accepted.
Fix: build the request inside a guard that turns the failure into a `CliError` naming `LODGE_TOKEN`.

## Practice

**M4. The test server hard-codes the version.**
Handles: `ts/tests/e2e/server.ts:58` and `ts/tests/cli/client.test.ts:13` write `"0.3.0"`, while `ts/tests/e2e/project.ts` reads `package.json`.
A version bump breaks the in-process e2e on a version mismatch with a message that does not point at the cause.
Fix: one shared constant read from `package.json`.

**M5. `ts/tests/cli/client.test.ts` is 298 lines.**
The 300-line rule covers `src` only, so the gate is green, but there is no headroom for the I1 test.
Fix: put the new `init` body test in its own file, or split `client.test.ts` by concern.

**M6. Hardening the plan does not ask for.**
`fetch` has no timeout and no `redirect: "error"` (`ts/src/cli/client.ts:22`).
A hung server hangs the command; a redirect would resend the bearer token to the redirect target.
Fix: not for 7a; park for the plan's security pass.

## Design

The `#cli` exports match the plan's Interfaces: `Io`, `run`, `fromWire`, `Call`, `runThread`, plus the earlier `CliError`, `readDraft`, `readExact`, `parse`, `Command`, `Exit`, `ThreadCommand`, `NO_SERVER`, `ProjectSettings`, `readSettings`, `repositoryRoot`, `ServerPlace`, `serverOf`, `tokenOf`.
Plan 4's "Names consumed" (`Io`, `run(argv, io)`, `parse`, `Command`, `readSettings`, `CliError`, the `tomlTable` factoring) are all present.
Plan 4 adds an optional `Io.hook` and answers `hook` before settings; the current `run` structure allows that, and `Io` has no `hook` yet, which is correct for this task.
Operation names and body fields match `ts/src/api/operations.ts`: search `{query, filters, limit}`, show `{ref, reasoning, provenance}`, mint `{prefix}`, add `{drafts, attachments, importing, dryRun}`, ask `{ref, raises, by, text, where, when}`, reply and close `{thread, ...}`, project-create `{settings}`.
Check-failed handling is right: 422 with `error.kind` `check-failed` and a result for add, ask, reply, and close; 200 for `check`, with the CLI reading `result.ok`.
Read order is as planned: drafts and attachments before settings, message files after.
`guide.md` matches the plan's replacements against lodge 0.2; parity rows match the plan's table, the wheel row is `planned`, and the three widened checks are in place.

**M7. A plan rule no test enforces.**
This is I1: the `core` table sent by `init` is stated in the plan and pinned by no test.

**M8. `Call` lives in `client.ts` and `runThread` reads the message file itself.**
This is workable and matches the plan.
Task 7b should not add a second file reader for the same job; reuse `readExact`.
No change needed now.

No design Blocking or Important found.

## Test carries against the Python reference

The carries for waiting, spec, check-and-gate, broken-agent, guide, init, id, help, search-limit, before-init, outside-repository, and malformed-settings match the Python assertions apart from the plan-sanctioned substitutions and Codex's two findings.
The clock equivalents (`MinuteClock`, `StuckClock`) in `ts/tests/e2e/server.ts` match `tests/e2e/conftest.py`.

## Files read

- `ts/src/cli/{index,client,wire,threads,thread-output,commands,output,settings,files,errors,grammar,guide.md}.ts`
- `ts/src/api/{operations,http,wire}.ts`
- Python `src/lodge/cli/{commands,output,thread_output,threads}.py` and `tests/e2e/conftest.py`
- `ts/tests/e2e/{project,support,server}.ts`
- e2e tests: spec, waiting, check-and-gate, broken-agent-decision-warns-above-show, guide, help-lists-every-command, init, id, search-limit, search-shows-unparsable-file, show-ambiguous-code-one-line, before-init, outside-repository, malformed-settings
- `ts/tests/cli/{client,wire}.test.ts`, `ts/tests/app/thread-fix-paths.test.ts`, `parity.test.ts`, `parity-names.ts`, the `parity.json` diff
- Plan sections Task 7a, 7b, 8, 9 and the parity table; plan 4's interface text; the task report; the Codex review

## Files not read

- `ts/tests/e2e/search.test.ts`, `ts/tests/e2e/show-levels.test.ts` (beyond Codex's account), `ts/tests/cli/settings.test.ts`
- `grammar*.ts` in depth
- Python `test_search` and `test_show_levels` bodies
