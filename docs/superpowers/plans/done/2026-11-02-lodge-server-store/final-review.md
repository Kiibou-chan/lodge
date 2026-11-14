# Final whole-branch review of plan 2 (`server-store`, HEAD 8f01151)

Reviewer: Sonnet 5.5. Incremental notes; the verdict line closes the file.

## Probes run

- Differential probe, `MemoryStore` against `SqliteStore` through `Lodge` (agent, ada, bo actors): holds, approvals by the wrong person, double approval, declines with and without reasons, approval after decline, relayed ask, reply, and close, approval of a reply after its thread closed, own and foreign thread messages, confirm, check, spec, timeline.
  The two logs are identical once hold numbers are renumbered (`MemoryStore` counts its own `rev`, `SqliteStore` the event `seq`; the numbers appear only in the `nothing is held under number N` text).
  After the run `rebuild` leaves `heads`, `files`, `members`, and `held` row for row as they were.

## Gate and structure (run in a scratch worktree at HEAD 8f01151)

`sh scripts/check.sh` exits 0.
ruff format and ruff pass, mypy strict reports no issues in 195 files, pytest passes 1399 tests, and `lodge check --gate` is ok.
On the TypeScript side biome, tsc, dependency-cruiser (197 modules, no violations), knip, `bun test` (1289 pass, 2 todo, 0 fail), and `differential.sh` (0 differences) pass.
The largest file in `ts/src/app` and `ts/src/store` is `ts/src/app/writes.ts` at 254 lines, so every module is under 300.
Against plan 1's end (4f5d5fb) the only dependency change is `kysely` 0.29.7 in `ts/package.json`, plus the `#app` and `#store` import aliases.
`src/`, `tests/`, `pyproject.toml`, and `uv.lock` are unchanged since 4f5d5fb.

## Interfaces for plans 3 and 4

`ts/src/app/ports.ts`, `results.ts`, `errors.ts`, `time.ts`, `held.ts`, `lodge.ts`, and `ts/src/store/index.ts` match the plan's Interfaces text name for name: `Now`, `Clock`, `IdSource`, `PublishOutcome`, `CommitOutcome`, `Committed`, `Gate`, `Store` (with `hold`, `held`, `decline`, `attachmentTexts`, `approves`), `Actor`, `person`, `agent`, `actorText`, `Role`, `Projects`, `HeldAdd`, `HeldMessage`, `Held`, `Approved`, the `LodgeError` family, `coreSettings`, `stampOf`, `minuteOf`, the `Lodge` methods, `openDatabase`, `LodgeDatabase`, `Tables`, `SqliteStore`, `SqliteProjects`, and `rebuild`.
One deviation is recorded as M-1 below.

## Findings

### Important

**I-1 · The check of a thread write can be deleted without a test failing** (`ts/src/app/threads.ts:166-167`)

Mutation: replace `if (!check.ok)` at line 167 with `if (false)`.
`bun test` still passes (mutation run: 0 failing).
Scenario: a later change makes `ask`, `reply`, or `close` produce a tree that fails `checkChange` (for example a thread file that the new check rejects), and nothing notices that the thread write publishes it anyway.
The Goal says every write is checked against its landing state, and no test holds the thread path to it.
In Python `test_run_thread_outcomes` only mocks `ask`, and in TypeScript the matching test is `test.todo` for plan 3.
Verified by running: a staged `MemoryStore` whose `files` lacks the decision files while `published` still holds them makes `ask` and `add` return `CHECK_FAILED` with no publish, so the test is writable against the existing fakes.
Fix: add one test over the fake store in `ts/tests/app/` that drives `ask` (and one for `reply`) to a `CHECK_FAILED` and asserts that nothing was published.

**I-2 · The baseline of `checkChange` can be swapped from the published tree to the current one without a test failing** (`ts/src/app/writes.ts:124`, `ts/src/app/threads.ts:166`)

Mutation: `load(state.published)` changed to `load(state.current)` at both lines; both survive (0 failing).
Scenario: `published` and `current` differ whenever the store is a git store with an unpublished local state, which is what plan 3 builds on.
Checking an edit against `current` lets an immutable-field change or a rewrite of a published decision pass when only the local copy still holds the old text.
The immutability check is the guard on "every write is checked against its landing state", and the app layer has no test that gives it two different trees.
Fix: the same staged-drift fixture as I-1 serves; assert that an `add` rewriting a published decision is refused when `current` already holds the rewrite.

**I-3 · A second project in the same database is invisible to the store tests** (`ts/src/store/read-tree.ts:30-34` and `:20-24`, `ts/src/store/projects.ts:46-58`, `ts/src/store/sqlite-store.ts:65-72`)

Mutations that survive (0 failing each):
- `read-tree.ts`: drop `.where("project", "=", project)` on the `files` query.
- `read-tree.ts`: drop the same filter on the `members` query.
- `projects.ts`: drop the project filter in `members()`.
- `sqlite-store.ts`: drop the project filter, the lower bound, or the upper bound in `attachmentTexts()`.
Scenario: with two projects in one database, project `a`'s tree would contain project `b`'s files, members, and attachment texts, so `a`'s check reads `b`'s decisions and an owner of `b` counts as an owner of `a`.
The held tests do create a second project (`tests/store/held.test.ts:147`), which is why the held filters are killed; no test does it for files, members, or attachments.
Fix: one store test that creates `storage` and `other`, publishes a file, a decision, and an attachment to `other`, and asserts that `trees()`, `members("storage")`, and `attachmentTexts()` of `storage` show none of it.

**I-4 · A user name and a machine path sit in tracked transcripts** (`docs/superpowers/plans/2026-11-02-lodge-server-store/task-12a-fix-1-codex.log:882`, and `pamac-build-user/...` at `task-11-fix-1-codex.log:141,144`, `task-12a-fix-1-codex.log:141,144`, `task-12b-fix-1-codex.log:950,953`, `task-12c-fix-1-codex.log:811,814`)

CLAUDE.md's hard rule is "Public repository: no personal paths, machine names, secrets … in code, tests, or docs".
`git grep <user>` finds exactly these lines, one of them a `/home/<user>/.bun/bin/bun` path.
Scenario: the branch merges to a public `main` with a login name and a build directory name in history and in the tree.
Fix: scrub those seven lines (replace the user name with `<user>`) before the merge, or untrack the `*-codex.log` files; the untracked `task-14-minors-codex*` files need the same check before they are added.
`ts/src`, `ts/tests`, `ts/*.json`, and `lodge/` hold no personal path.

### Minor

- **M-1** `ts/src/app/threads.ts:76-81`: `MessageOptions` carries `close?: boolean`, so the public `Lodge.ask` and `Lodge.reply` accept an option the plan's `{where, when, commit}` does not list.
  Harmless: `ask(..., "", {close: true})` is refused with "message text must not be empty".
  Fix: keep `close` in an internal options type, and pass it only from `Lodge.close`.
- **M-2** `ts/src/app/held.ts:9` and `lodge.ts`: `Lodge.held()` returns every person's holds with their full drafts to any actor (parked M-6).
  Scenario: plan 3 hands the result to a viewer for person `bo` and shows `ada`'s drafts.
  Fix: plan 3 filters by actor, or `held()` takes the actor; record the choice in the plan 3 brief.
- **M-3** A retried `add` holds twice, so one person can approve two identical decisions (parked M-7).
  Fix: a hold keyed on the draft text, or a note in plan 3 that the viewer collapses duplicates.
- **M-4** The hold-time decision id is provisional: approval re-mints it (`d-111111` becomes `d-222222` in the probe), as `task-12b-brief.md:204` says.
  Scenario: plan 3 prints the hold-time id as final and the person looks for it.
  Fix: one line in the plan 3 brief, and a test that approving returns the new id.
- **M-5** `ts/src/store/sqlite-store.ts:99`: the `path.includes("\\")` refusal survives removal (0 failing); `lodge/a\b` is the case no test has, and `src/lodge/gitstore/plumbing.py:21` refuses it.
  Fix: add `lodge/a\\b` to the refusals test.
- **M-6** `ts/src/store/sqlite-store.ts:~60`: a `null` or non-numeric `base.rev` is not refused by name; the test at `tests/store/sqlite-store.test.ts:55` passes anyway because `Number(...)` gives NaN and the update matches nothing.
  The mutation to `false` survives, so the explicit guard is untested; fix by deleting the guard or by asserting its message.
- **M-7** Survivors with no behaviour behind them in the tests: `held()` order (`ts/src/store/sqlite-store.ts`, `.orderBy("seq", "asc")` to `desc`), `SqliteProjects.members` sorting, `touchHead` keeping `rev` (`read-tree.ts`), `events.ts` approved-hold project scoping (redundant while `seq` is global), `schema.ts:88` `.immediate()` against `.deferred()` (needs two processes opening a new database), and `storeFor` passing the actor text (`projects.ts:90`).
  Scenario for the last: every event written through `storeFor(project, actor)` is attributed to the wrong actor without a test failing.
  Fix: one assertion each; the actor one matters most.
- **M-8** `ts/src/core/derive-flags.ts` (`undone`, the `!confirmed.has(target)` term) and `check-state.ts:100` (`strip` before the `author` test) survive removal.
  Both are ported from Python (`derive.py:177-183`) and the Python tests do not kill them either; either an equivalent term or a missing fixture.
  Fix: find the distinguishing fixture or drop the term in both ports.
- **M-9** `MemoryStore` does not enforce the path, surrogate, attachment-overwrite, and decision-rewrite refusals that `SqliteStore.publish` does, so the app tests over the fake cannot see those refusals; the store tests cover them.
  `MemoryStore` also counts one `rev` per publish where `SqliteStore` counts one `seq` per event, so the numbers in `nothing is held under number N` differ between the two (the only difference the differential probe found).
- **M-10** `MIGRATIONS[0]` was edited in place for d-gxbbnf (`message` is a `blob`), so a database created before 8c75e13 has the old column under the same `user_version`.
  Nothing is shipped, so no database exists; recorded so that the first release does not forget it.
  Migration 1 to 2 is covered at `tests/store/database.test.ts:174`.
- **M-11** The people-call structure rule is syntactic and misses aliased imports, `core["writeThread"](x)`, and `writeThread(x, undefined)` (`tests/structure/calls.ts:172-178`); the limit is documented in Task 14.
- **M-12** Em-dashes occur in the tracked `*-codex.log` and `*-codex-final.txt` builder transcripts (and in the untracked `task-14-minors-codex*` files); they are not authored prose, and no em-dash is in the plan, ledger, reviews, `lodge/`, `ts/src`, or `ts/tests`.
  `docs/research/2026-11-02-server-cloud-sessions.md:310` names a probe session id; fine for a public repo, but it is a session identifier.
- **M-13** The codec speed measurement stays unmeasured (parked), and `publish` trusts the caller's base (parked Task 7b D-1); neither blocks plans 3 and 4.

## Differential and rebuild

Run through `Lodge`, the two stores answer alike over about 36 steps (see "Probes run").
Rebuilding the derived tables from events alone gives rows identical to the live ones for `heads`, `files`, `members`, and `held`.
A message hold changes no thread's waiting, as the fix-round ruling says; a reply approved after its thread closed raises `q-... is closed` and the hold stays open in both stores.

## Goal requirements against mutation

| Requirement | Mutations tried | Killed | Survived |
| --- | --- | --- | --- |
| `decided_by` is a person or a role | role word, strip, casefold, quote needed, imported skip, quote where, confirms by a non-person, immutability | 7 | 1 (`strip`, M-8) |
| A person's decision waits | awaits filters (new, people, self, one at a time), hold made, hold for any actor, `approves` null, name and kind checks | all | none |
| The review flag clears on confirm only by that person | `confirmedBy`, `cleared` (person, confirms, replaces, order), `flagged` (people skip, cleared skip, undone, personOnly, touches, follows), per-person loop, `counts`, `awaiting` | 20 | 1 (`undone` term, M-8) |
| Confirm only by that person | owner only, agent refused, stale length, `decided_by` author | all 4 | none |
| Every write is checked against its landing state | check ignored, REJECTED retried, retry limit, dry-run order, check of an `add` | all | thread check (I-1), baseline (I-2) |

Batches run: app (32 mutations), store and projects (62), core flags and checks (29); each mutation applied in a scratch worktree, `bun test` run, and the file reverted.

## Verified and not verified

Verified by running: the gate, the differential probe, the rebuild comparison, all mutation results above, the staged-drift probe for I-1 and I-2 (deleted afterwards), and the `git grep` results for I-4 and M-12.
Not verified: the Python side beyond the gate (no mutation on `src/lodge`), `reads.ts` and `write-attachments.ts` behaviour beyond the tests that pass, a git-backed `Store` (plan 3), and concurrent writers across two processes.

## Files

Read: `ts/src/app/*.ts` except `reads.ts` and `write-attachments.ts`; `ts/src/store/*.ts`; `ts/src/core/derive-flags.ts`, `people.ts`, `derive.ts` (lines 100-140), `check-state.ts` (lines 90-122), `check-change.ts` in part; `ts/tests/app/{fakes,support,held-support,held-messages-support}.ts`; `ts/tests/store/{support,seed}.ts`; `database.test.ts`, `held.test.ts`, `sqlite-store.test.ts`, and `concurrent.test.ts` in part; `held-approve.test.ts`; the plan (lines 1-215 and 686-697); the ledger; `task-14-minors-report.md`; `lodge spec`; `lodge search --by author`; `src/lodge/core/derive.py` (lines 165-245); `src/lodge/gitstore/plumbing.py` (lines 10-30).
Not read: the per-task brief, report, and review files (grepped only), `reads.ts`, `write-attachments.ts`, most of `ts/tests`, the rest of `ts/src/core`, `ts/tests/structure/*` rule sources, and `docs/research` apart from line 310.

Verdict: 0 Blocking, 4 Important, 13 Minor
