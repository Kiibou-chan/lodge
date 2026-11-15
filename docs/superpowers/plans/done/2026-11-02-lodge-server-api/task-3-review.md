# Task 3 review (settings, file readers, errors)

Reviewed commit 920b23f on top of 42a852a, lane B (`server-api-b`).
Verdict: PASS. 0 Blocking, 0 Important, 9 Minor.
Method: gate run in a scratch detached worktree (`sh scripts/check-ts.sh`: 1368 pass, 2 todo, 0 fail, knip and dependency-cruiser clean); 24 hand mutations of `ts/src/cli/settings.ts` and `ts/src/cli/files.ts` run against `bun test tests/cli`; edge probes through the front door; a trial merge with lane A (`c7185d4`).

## Pass 1: correctness

- The exported names and signatures match the plan's Task 3 "Produces" block one for one: `CliError(message, exitCode: 1 | 2 = 2)`, `ServerPlace`, `ProjectSettings`, `NO_SERVER` (text identical), `repositoryRoot`, `readSettings`, `serverOf`, `tokenOf`, `readDraft`, `readExact` (`ts/src/cli/index.ts:1-11`).
- `title_chars = 80.0` is refused with `.lodge.toml: length.title_chars must be a positive whole number`.
  `integersAsBigInt` is at `ts/src/cli/settings.ts:96`; dropping it fails 6 tests (mutation M1), and the four forms of the plan's `whole_number_float_is_refused` (`settings.test.ts:45-52`) pin it.
  The float-to-`null` branch (`settings.ts:35`) is pinned too (M2: 4 failures).
  `inf`, `nan`, dates, `99999999999999999999`, `0x50`, `+80`, `1_000` behave as the plan says (probe and tests).
- Messages match lodge 0.2 where the plan keeps them: `{cwd} is not inside a git repository` (`src/lodge/gitstore/setup.py:24`, pinned by `tests/e2e/test_outside_repository_one_sentence_exit_2.py:16`), `not UTF-8 text` (`src/lodge/cli/files.py`, `tests/e2e/test_add_attach.py:75`), the unknown-name sentences (`src/lodge/core/settings.py:30-35`).
- Report's concern on filesystem error descriptions: judged not a defect.
  Lodge 0.2's tests pin only `startswith("lodge: <missing>: cannot be read")` and one line (`tests/e2e/test_add_attach.py:95`); no test pins the system's wording, and the plan says the report only "compares" it.
  Probe against Python: ENOENT, EISDIR, EACCES, EPERM, ENOTDIR agree word for word.
  Two differ (ELOOP: Bun "Too many symbolic links encountered" against glibc "Too many levels of symbolic links"; ENAMETOOLONG: "Name too long" against "File name too long"); both are unreachable in a test and need no action.
- Every probed malformed file gives one `.lodge.toml: ` line (`[length\n`, duplicate key, newline in a key name, a directory as `.lodge.toml`).
- Test-first: the report's file:line handles match the test titles (checked against `grep -n '^test'`).
- Mutation survivors are in the Minor list below; none hides a plan requirement.

### Minor findings

1. Minor: a byte order mark in `.lodge.toml` is accepted, lodge 0.2 refuses it.
   Handle: `ts/src/cli/files.ts:25` (`ignoreBOM: true`) reached by `settings.ts:92`; `python3 -c "import tomllib; tomllib.loads('﻿[length]\ntitle_chars=5')"` gives `Invalid statement (at line 1, column 1)`, while `readSettings` of the same text returns `title_chars` 5.
   Scenario: a file saved with a BOM on another platform passes on the server command and fails in lodge 0.2; harmless, but it departs from the plan's "as lodge 0.2 reads it" and no test says which is meant.
   Fix: either refuse a leading U+FEFF in `readSettings` with a one-line sentence, or add a test naming the leniency.
2. Minor: `server.url` accepts `https://host:` and `https://host\`.
   Handle: `settings.ts:51` (the regex `[^/\s@?#]+` allows a trailing colon and a backslash); probe returned `url: "https://host:"` and `"https://host\\"`.
   Scenario: the stored URL is later joined with `/api/v1/…` and sent; a backslash is read as a slash by `fetch`, so the request goes somewhere other than the text says.
   Fix: forbid `\` in the host class and require a port to have digits, for instance `^https:\/\/[^/\s@?#\\:]+(:[0-9]+)?\/?$` plus the `http` localhost form.
3. Minor: the URL validator is three layers deep and most of the second and third are unreachable.
   Handle: `settings.ts:51-71`; mutations M4 (drop `parsed.username || parsed.password`), M5 and M5b (drop the `?` and `#` tests), M23 (drop the `https:` protocol test), M24 (drop the `pathname` test) all leave 66/66 passing, because the regex at line 51 and the `http` regex at line 63 already refuse those inputs.
   Scenario: a later edit to the regex silently relies on guards no test reaches; the code is also about 20 lines for one rule.
   Fix: one regex for the accepted shape plus `new URL` to refuse an invalid host; keep the `test.each` as it is.
4. Minor: the date and time branch of `convert` is dead.
   Handle: `settings.ts:35` (`value instanceof TomlDate || value instanceof Date`), and the `Date` exclusion in `table` (`settings.ts:28`); mutation M3 (delete the branch) leaves 66/66 passing, since `parseCoreSettings` (`ts/src/core/settings.ts`, `typeof value !== "number"`, `s is string`) refuses a `Date` as it would `null`.
   Scenario: none today; it is an unpinned branch and the only reason for the `TomlDate` import.
   Fix: drop the branch and the import, or keep it and say in a comment that it is for the plan's wording; the dates test already pins the outcome.
5. Minor: the `descriptions` table in `readExact` is partly redundant and partly untested.
   Handle: `files.ts:11-16`; deleting `ENOENT` leaves 66/66 passing (the fallback capitalisation gives the same words), and `EACCES` and `EPERM` have no test (the report says the account bypasses modes).
   Fix: keep `EISDIR` only (the one Bun words differently); the fallback covers the rest.
6. Minor: unknown top-level names are checked in `Object.entries` order, which puts integer-like keys first.
   Handle: `settings.ts:106`; `a=1\n5=2` gives `unknown key 5`, Python (`tomllib`, insertion order) `unknown key a`.
   Scenario: the plan's "first unknown name in file order" is wrong for a numeric key; unlikely in practice.
   Fix: none needed unless the order matters to someone; say so in the test title, or accept.
7. Minor: the refusal tests match with a substring.
   Handle: `settings.test.ts:25-26` (`toThrow(string)` is a substring match) and `files.test.ts:27-34`.
   Scenario: a message with trailing text, for example a second sentence, passes; the one-line tests (`settings.test.ts:67`, `176`) cover only some paths.
   Fix: compare `(error as Error).message` with `toBe`, as `server_is_needed` already does (`settings.test.ts:93`).
8. Minor: the test-first evidence for the original tests is a missing module, not a behaviour.
   Handle: `task-3-report.md`, "Test-first evidence": rows marked A failed with `Cannot find package '#cli'`, so none was seen failing on its assertion.
   Scenario: CLAUDE.md asks to see each new test fail before its code; a stub that throws would have shown which assertions bite.
   Fix: none for this task (my mutation run shows the tests do bite, apart from the survivors above); next briefs could ask for a stub-first failure.
9. Minor: `repositoryRoot("rel/dir")` stops at `.` and never walks above the working folder.
   Handle: `settings.ts:20-26`, probe: `rel/dir is not inside a git repository`.
   Scenario: only if a caller passes a relative path; Task 5's `run` should pass `process.cwd()` or a `resolve`d path.
   Fix: `resolve(cwd)` first, keeping `cwd` in the message, or state the absolute-path precondition in Task 5's brief.

## Pass 2: practice

- Hard rules: no personal path, machine name, or secret in the diff (`git diff 42a852a 920b23f | grep -E '/home/|/var/tmp|kiibou'` is empty); fixtures are synthetic (`lodge.example.org`, `synthetic-token`); tests use `mkdtempSync` temporaries only, no git, no network, no sockets.
- Biome `--error-on-warnings`, tsc strict, vulture-equivalent knip, dependency-cruiser: all green in the scratch gate.
  `smol-toml` is out of `ignoreDependencies` (`ts/knip.json`) and knip reports nothing unused.
- Size: `settings.ts` 127 lines, `files.ts` 32, `errors.ts` 9; all under 300.
- Structure rules are not loosened: the diff touches no file of `ts/tests/structure/` and not `ts/.dependency-cruiser.cjs`; `cli` reads files through `node:fs` reads only (`file-confinement` allows `cli`).
- No new dependency: `ts/bun.lock` is unchanged and `ts/package.json` gains only the `#cli` import.
- Prose: the report and comments use British English; I found no em-dash or acronym macro.
- Minor, commit trailer: 920b23f ends `Co-Authored-By: Codex <noreply@openai.com>`, where the plan's Global Constraints say `Claude <noreply@anthropic.com>`.
  The brief (`task-3-brief.md`, line 12) told the builder to use Codex, so the builder followed its instructions; the coordinator should decide whether the merge keeps it.
  The same holds for lane A (`c7185d4`).
- Minor, stray file: `docs/superpowers/plans/done/2026-11-02-lodge-server-api/task-3-codex-final.txt` is untracked in lane B (`git status --short`).
  It is the builder's final message, with no sensitive content; do not stage it with explicit-path commits, or delete it.
- Minor, awkward call: `settings.ts:92` passes `"cannot be read: not UTF-8 text"` as the `notUtf8` argument and `settings.ts:94` rewrites the path prefix by `String.replace`; it works and is tested (`settings.test.ts:153`), but a reader has to follow two layers to see the sentence.
  No fix needed.

## Pass 3: design

- Names match the plan's Exports; `index.ts` re-exports exactly the Task 3 names, no extra.
  No export is read only by a later task except through the front door; knip is green without a `knip.json` entry, as the plan's table for Task 3 expects (only `smol-toml` leaves `ignoreDependencies`).
- Lane merge with Task 2 (trial merge of `c7185d4` into this commit in a scratch worktree, not committed):
  - `ts/package.json`: both lanes made the identical `#cli` line, so it merges without conflict.
  - `ts/src/cli/index.ts`: add/add conflict; the resolution is the union of both files' exports.
    Pasting the two sides alone fails Biome's export ordering (one error), so the merger must run `bunx biome check --write src/cli/index.ts`; after that the merged tree passes `sh scripts/check-ts.sh` (1423 pass, 0 fail).
  - No other file overlaps.
- `readSettings` reads the settings in the order: unknown names, `[server]`, then core tables; lodge 0.2 has no `[server]`, so the order of a server error against a core error is unspecified by the plan and is a free choice here.
- Plan rules no test enforces: `[hook]` left unchecked (`settings.ts:107`, pinned by `hook_is_left_alone`), `store` as an unknown section (pinned), the project-name limit of 63 characters (pinned at 64 only; a 63-character name is not in a test, M14 shows the boundary is caught from the refusal side).
  Not enforced: that `tokenOf` is the only reader of `LODGE_TOKEN`, which is a Task 5 concern.

## Files

Read: `/var/tmp/lodge-server-api/CLAUDE.md`; the plan's header, Global Constraints, Exports, Calls made, Review Focus, and Task 3 (`/var/tmp/lodge-server-api/docs/superpowers/plans/done/2026-11-02-lodge-server-api.md`); `task-3-brief.md` (first 80 lines) and `task-3-report.md`; the whole diff `42a852a..920b23f` in `ts/src/cli/*`, `ts/tests/cli/*`, `ts/package.json`, `ts/knip.json`; `ts/src/core/settings.ts`; `src/lodge/gitstore/settings.py`, `src/lodge/cli/files.py`, `src/lodge/core/settings.py`, `src/lodge/gitstore/setup.py:15-40`; `ts/.dependency-cruiser.cjs:80-100`; lane A's `ts/src/cli/index.ts` and `ts/package.json` change; grep hits of lodge 0.2's e2e tests for the sentences.
Not read: `ts/tests/structure/*` in full (only grepped for `cli`), `task-2-brief.md` beyond its lane note, the design document, plan 3's other tasks, the probes folder (probe 1 and 2 behaviour was run, not read), lodge's own `lodge spec` entries (the plan's decisions d-dfkqec and d-1zmfdr were read through the plan text only).
Scratch artefacts: `/tmp/rev3probe/` (probe and mutation scripts); the scratch worktree under lane B's `.claude/worktrees/rev3` is removed.
