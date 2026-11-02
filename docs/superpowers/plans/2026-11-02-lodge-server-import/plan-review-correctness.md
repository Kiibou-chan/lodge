# Plan review, correctness angle: plan 4 of build step 1 (the importer, the export, and the design's records)

Reviewed: `docs/superpowers/plans/2026-11-02-lodge-server-import.md` at 6c6322c, with its ledger, `probes.md`, `questions.md`, `planner-brief.md`, and `planner-report.md`.
Authority: the server design (`docs/superpowers/specs/2026-11-02-lodge-server-design.md`) and `lodge spec`; plan 1 for the conventions; plan 2 at 7204ad3 and plan 3 at 3e4c29c for the names consumed.
Probes ran in a scratch worktree under `.claude/worktrees/`, removed afterwards.

Counts: 1 Blocking, 4 Important, 13 Minor.

## Findings

### B-1 · Blocking · the import's two checks pass settings that the state check does not take, and three tests assert failures it cannot give

Handles: plan lines 143, 299, 303, 314 (`failing_store_prepares_nothing`, `mapped_state_is_checked_with_the_project_settings`), and 421 (`failing_store_answers_check_failed`); `git show origin/server-core:ts/src/core/check-state.ts`, line 133, `export function checkState(s: Snapshot): CheckResult`; `src/lodge/core/check_entries.py:73-84` (`_unlisted_sources` runs only over `new_decisions(published, after)`, inside `check_change`).
The plan calls `checkState(load(tree(…)), coreSettings(copy.settings))` and `checkState(load(…), settings)`, but plan 1's `checkState` takes one argument, so `tsc` refuses both calls (TS2554).
The settings matter only to `checkChange`: the unlisted-source check and the length guidance judge new decisions of a change, never a published state.
Run in a scratch repository holding probe 6's store committed on `main`, with `.lodge.toml` emptied and committed: `lodge check` prints `ok` and exits 0, and `lodge check --gate` likewise; with `[length] title_chars = 10` committed, `ok` again.
So lodge 0.2 itself accepts the store whose sources are emptied, and no state check fails on a title length.
Failure: `failing_store_prepares_nothing` and Task 8's `failing_store_answers_check_failed` expect a problem for the imported decision that neither `checkState` nor lodge 0.2 reports, and `mapped_state_is_checked_with_the_project_settings` expects a `"server"` stage from a length setting that no state check reads; the builder either cannot make them pass or makes them pass by checking the import as a change (`checkChange` from an empty state), which would refuse legitimate history (`_links_to_dead`, `src/lodge/core/check_change.py:104-120`, refuses a new decision confirming or narrowing a replaced one, which an old store may hold).
d-ag8p8h's reasoning rests on the misreading: it cites `test_import_from_an_unlisted_source_fails_the_check`, which is about `lodge add --import` of a new draft (`tests/e2e/test_add_import.py:30-34`), not about a published store; d-y42b7b's "a store whose own `.lodge.toml` differs so that the check fails is refused" falls with it.
Task 1's `zero_two_store_checks_clean` (line 143) passes settings to `checkState` as well.
Fix: call `checkState(load(tree(…)))` with no settings in Task 1, in step 1, and in step 4; replace `failing_store_prepares_nothing` and `failing_store_answers_check_failed` with a state problem lodge 0.2 reports on a published store (a decision whose `changes` names an entry that does not exist, check 2, or the stray file already planned), and `mapped_state_is_checked_with_the_project_settings` with a problem only the mapped state has (an agent decision `decided_by: ana` without a quote, imported into a project whose owner is `ana`, which the server reads as a person's decision and refuses under check 3, stage `"server"`); record a decision replacing d-ag8p8h (and narrowing d-y42b7b's settings clause), and decide whether `ZeroTwoCopy.settings`, `zeroTwoCoreTable`, and `moving.read`'s TOML join stay only to refuse a malformed `.lodge.toml` as lodge 0.2 does.

### I-1 · Important · `reads_the_branch_layout` expects `.lodge.toml`'s text at a revision that does not hold it

Handles: plan lines 179 (`readStore` "reads `.lodge.toml` at the commit in the same batch, null when there is none"), 185 (`zeroTwoRepository("branch")` puts `lodge/` on an orphan branch `lodge` holding only `lodge/`, `.lodge.toml` on `main`, and `rev` the commit holding `lodge/`), and 189 (both layout tests expect "`.lodge.toml`'s text in `settings`").
In the branch layout the commit `rev` names holds no `.lodge.toml`, so `readStore` as specified answers `settings: null`, and the test as specified fails; lodge 0.2 reads a branch-mode store's settings from the checkout of the base branch, never from the store's branch (`src/lodge/gitstore/settings.py:33-36` reads `root / ".lodge.toml"`).
Failure: the Task 2 builder meets a test that contradicts its interface and either reads `.lodge.toml` from another revision it was not told to name (`main`, guessed) or weakens the test.
Fix: `reads_the_branch_layout` expects `settings` null; if the import must also refuse a malformed `.lodge.toml` in the branch layout (B-1's last clause), give `import` and `readStore` a second revision for the settings, defaulting to `rev`.

### I-2 · Important · IMP-1 and probe 7 describe option A's and option B's effects on lodge 0.2 inaccurately

Handles: `questions.md:9`, `:12`, and `:16`; `probes.md:35`.
Re-run in a scratch repository with probe 6's store committed, then each `decided_by: author` and the thread's `by: author` replaced by `ana` and committed (probe 7), with stdout and stderr apart:
- `lodge spec` does not print the same text, against `probes.md:35` and the A option's "renders the same `lodge spec`": its standard output gains `problem: lodge/threads/q-j2dsgk.md:20: when must be ISO 8601 with seconds and an offset`, and the entry's heading loses its mark, `## Transcripts are kept (s-cjhfb7 · question open)` becoming `## Transcripts are kept (s-cjhfb7)`.
- `lodge waiting` loses the open question: before, `waiting for an agent` lists `q-j2dsgk · open · question · about s-cjhfb7 · 2 messages · last by author`; after, `nothing`.
- `lodge show d-q59cdf` loses ` · confirmed by the author (d-t46j05)`, as `questions.md:9` says (confirmed).
- `lodge check --gate` on the committed mapped store (probe 3's store, no thread) prints `ok` and `note: already published, check 3: … confirms is for author decisions, but decided_by is ana`, exit 0, against the recommendation's "a project's own `lodge check --gate` on its exported copy fails from the first confirmation" (`questions.md:16`); plain `lodge check` exits 1, as the question says.
- Under B, "the export is then a lodge 0.2 store byte for byte, which `lodge check` passes" (`questions.md:12`) holds only when the export is read through a `.lodge.toml` the export never writes (I-3): a checkout of probe 6's `lodge/` alone on a branch `lodge` prints `check 4: d-40q44p: imported from docs/choices.md, which is not listed in [import] sources` and `the published state cannot be found: origin/main and main were tried…`, exit 1.
Failure: the author rules IMP-1 on a description that understates A's cost for any project with a thread (its specification view and waiting list change, not only its check) and overstates B's (lodge 0.2 reads B's export cleanly only with a settings file beside it), and cites a gate failure that does not happen.
Fix: rewrite `probes.md:35` with the outputs above, and IMP-1's A to say that a thread holding the person's message also drops its mark from `lodge spec` and its question from `lodge waiting`, and that `--gate` notes rather than fails; B to say that `lodge check` passes when the export is read through a `.lodge.toml` in branch mode naming the export's branch and listing the store's `[import]` sources; the recommendation to argue from plain `lodge check` rather than `--gate`.

### I-3 · Important · the export reads like a lodge 0.2 store only beside a `.lodge.toml` it never writes, and Task 10's script does not say which

Handles: design line 284 ("the export reads like a lodge 0.2 store"); plan lines 215 to 217 and d-pv341r (the export branch holds nothing outside `lodge/`, so never `.lodge.toml`); line 473 (`scripts/round-trip.sh` runs `lodge spec` and `lodge check` "in a checkout … of the export", no settings named).
lodge's own store holds 69 imported decisions (`git grep -l '^imported_from' -- lodge/decisions | wc -l` prints 69 at 6c6322c), and its `.lodge.toml` lists their source; the export copies none of that.
Run: probe 6's `lodge/` committed alone on a branch `lodge` and checked out gives `check 4: d-40q44p: imported from docs/choices.md, which is not listed in [import] sources` and `the published state cannot be found`, exit 1 (I-2); the same branch pushed to a bare repository and read from a clone whose `main` holds `[store] mode = "branch"`, `branch = "lodge"`, and the store's `[import]` sources prints `ok` for `lodge check` and `lodge check --gate`, and `lodge spec` renders.
Failure: the coordinator's run on lodge's own records (d-2jk0mw) reports 69 check 4 problems and a missing published state that are artefacts of how the copy was read, not of the export, and the report cannot tell the expected effects of IMP-1 (line 474) from these; a reader of a real export in a separate repository meets the same.
Fix: Task 10's script reads the export through a repository whose `main` holds the clone's `.lodge.toml` with `[store]` set to `mode = "branch"` and `branch` the export's branch (its `[import]` and `[length]` kept), and says so; the plan (and Task 11a's entry for "Export to git") states that the export is read as a branch-mode lodge 0.2 store through such a settings file, which a person writes once in the target repository.

### I-4 · Important · plan 3's two new `Projects` methods break Tasks 5 and 6 at the merge of plan 3, so Task 9's gate fails beside Task 8

Handles: plan 3 at 3e4c29c, Task 4 ("`Projects` gains, beside plan 2's four methods: `create(…, settings?)`, `settings(project)`, `names()`", none optional); plan lines 94 and 95 (Tasks 8 and 9 both start once plan 3 is merged, side by side), 355 (`exportingProjects(...): Projects`, Task 6), 315 (Task 5's "fake `Projects` giving one store per project"), and 399 (only Task 8 modifies `exporting.ts` to forward `settings` and `names`).
When plan 3 merges into `server-import` after Tasks 5 and 6, `exportingProjects`' object and Task 5's fake `Projects` lack the two required methods, so `tsc` fails with TS2739 until Task 8 lands; Task 9 branches from that merge and its builder's gate (`sh scripts/check-ts.sh`, plan line 457) is red for code outside its task, and Task 5's test fake is in no task's Modify list.
Fix: the coordinator's merge of plan 3 (Task 1's merge points, line 140) adds the forwarding of `settings` and `names` to `exportingProjects` and the two methods to Task 5's fake, with `sh scripts/check.sh` green before Tasks 8 and 9 branch; or Task 6 forwards every method it does not change generically (a `Proxy` over the inner `Projects` whose `get` replaces only `storeFor`), so that a method a later plan adds passes through without an edit; a spread of a `SqliteProjects` instance would not copy its prototype's methods.

### M-1 · Minor · Task 9's `initialise()` makes the store's folders but does not stage them, as `lodge init` does

Handles: plan line 451 (`initialise()` "making `lodge/decisions/.gitkeep` and `lodge/spec/.gitkeep`"); `src/lodge/gitstore/setup.py:47-56` (`init_store` ends with `run(["add", "--", *KEPT], root)`); `tests/e2e/test_hook_feedback_after_hand_edits.py:34-37` (`project.git("commit", "-m", "Store")` right after `init`, then `git worktree add` of a sibling).
Failure: with the files unstaged, `git commit -m Store` has nothing to commit and exits 1, and the sibling work tree holds no `lodge/`, so `hook_finds_the_repository_of_the_edited_file_not_of_the_session` fails or is rewritten.
Fix: `initialise()` writes both files and runs `git add -- lodge/decisions/.gitkeep lodge/spec/.gitkeep`, as `init_store` does.

### M-2 · Minor · Task 4's test-local `resolve` over `realpathSync` throws on the files the carried tests name, which do not exist

Handles: plan line 261; `tests/hook/test_post_tool_use.py:98-104` (`test_symlinked_checkout_still_matches`: the link must be followed for `link/lodge/decisions/d-abc123-slug.md`, a file that does not exist) and nearly every other test there (edited paths under an empty `tmp_path`).
`realpathSync` of a missing path throws `ENOENT`, so a resolve "over `realpathSync` and `path.resolve`" either throws, which `respond` does not catch, or skips the link.
Fix: the brief says the test-local `resolve` resolves the longest existing prefix with `realpathSync` and appends the rest, as Task 2's `resolvePath` does (line 181), or Task 4's tests import `resolvePath` from `#git` once Task 2 has merged.

### M-3 · Minor · three decodings of stored or read bytes are left unnamed under d-0q54zn

Handles: plan line 385 (Task 7's `target(project)` reads an event body written as UTF-8 JSON; no decoder named); line 446 (`hookContextFor` reads `.lodge.toml`; no strictness named); line 404 (`zeroTwoCoreTable(text)` takes `readStore`'s `decodeUtf8` text).
Failure: a target body read with `TextDecoder` turns an escaped byte in a repository path (a JSON `\udcff` in the request) into U+FFFD, so the export writes to another path; a `.lodge.toml` that is not UTF-8 makes lodge 0.2's hook silent (`src/lodge/gitstore/settings.py:41-45` raises `cannot be read`, which `run` swallows) but would give advice in TypeScript if read lossily; and a store whose `.lodge.toml` is not UTF-8 is refused by lodge 0.2 but parses with lone surrogates in TypeScript.
Fix: Task 7 decodes the body with `decodeUtf8`; Task 9 reads `.lodge.toml` strictly, as plan 3's `readSettings` does, any failure giving null; Task 8's `zeroTwoCoreTable` refuses a text holding U+DC80 to U+DCFF with `.lodge.toml: cannot be read: not UTF-8`.

### M-4 · Minor · `writes_within_a_minute_share_one_commit` cannot be staged with plan 2's `FixedClock`

Handles: plan line 369; plan 2 at 7204ad3, Task 2 (`FixedClock`'s `sleep` "adds `seconds * 1000` to `start`" and resolves at once).
A run ends as soon as no write is pending, and the run's own sleep resolves in the same tick, so writes "10, 20, and 30 seconds later before the run ends" cannot arrive during the sleep; and the test can move the clock only by calling `sleep` itself, which also lands in `slept`.
Fix: the test uses a clock whose `sleep` records its seconds and resolves when the test releases it, or the test is restated as three writes issued together 10 seconds after the commit: one `sleep(50)` and one more `write`.

### M-5 · Minor · `moved_remote_branch_answers_moved` needs a way to land a push between the export's fetch and its push

Handles: plan line 224.
`exportStore` runs `ls-remote`, `fetch`, and `push` in one call, so a test cannot interleave a second clone's push without a hook point.
Fix: name the mechanism in the brief, a `pre-push` hook in the work repository that pushes a commit to the remote from the second clone (it runs after the fetch and before the remote is updated), so the export's push is refused as not a fast-forward; this mechanism was not run here.

### M-6 · Minor · "at most one commit a minute" does not hold across a restart

Handles: plan lines 352 and 361 to 363 (`start` exports each project with a target at once; the last commit's time lives in `Exporters`' memory); design line 285.
Failure: writes in the last seconds before a server stops are committed again at once by `start`, less than a minute after the commit before the stop.
Fix: `Exporters` takes the last commit's time from the branch tip (Task 3 answers the tip's committer time with `unchanged` and `committed`), or the plan and Task 11a's entry state the exception.

### M-7 · Minor · a symbolic link under `lodge/` reads as the path it names and comes back as a regular file

Handles: plan line 189 (`symbolic_link_reads_as_its_target`, "reads as its target's text"); `src/lodge/gitstore/trees.py:37-42` (a blob of mode 120000 is read as its content, the path the link names); plan line 218 (the export writes every file with `update-index` and no mode named).
Failure: "its target's text" invites reading the file the link points to, and the export writes the link back with mode 100644, so the round trip changes the file's mode.
Fix: name the test `symbolic_link_reads_as_the_path_it_names`, and either write mode 120000 back for a path read from a link or state the change in Task 10's expectations.

### M-8 · Minor · Review Focus 1's chain has no end-to-end test

Handles: plan line 104 ("a record file with an undecodable byte is problem 1 and refuses the import, an attachment that is not UTF-8 comes back byte for byte"); Task 5's tests (line 314) hold no undecodable record; Task 10's round trip (line 470) uses the made-up store, whose attachment is UTF-8.
Each link is tested alone (Task 2's two reads, plan 1's `bad_utf8_is_problem_1`, plan 2's `file_bytes_survive_exactly`, Task 3's `escaped_bytes_are_written_as_bytes`), but no test shows the import refusing such a record or the attachment's bytes crossing import, store, and export.
Fix: Task 5 adds `undecodable_record_refuses_the_import` (a decision holding U+DCFF: problem 1, stage `"lodge 0.2"`), and Task 10's round trip adds an attachment holding `\xff\xfe` to one layout and compares bytes.

### M-9 · Minor · the ledger keeps three replaced rulings as current "Ruling:" lines

Handles: `docs/superpowers/plans/2026-11-02-lodge-server-import-progress.md:9`, `:10`, and `:12` (d-bh93bn, d-m31e0d, d-srfxj8, each replaced by a line further down).
Failure: a coordinator writing a brief from line 9 tells the builder to keep thread messages unmapped, against d-83kt6y.
Fix: rewrite lines 9, 10, and 12 in place with the current decisions, and drop the "replacing" clauses of lines 16 to 18.

### M-10 · Minor · d-j5s0h0's reasoning cites plan 3 at a commit whose claim no longer holds

Handles: d-j5s0h0's reasoning ("plan 3 builds its accounts' reads from the events without a derived table (plan 3 at f2dcc72, Task 4)"); plan 3 at 3e4c29c, Task 4 ("The derived tables … `setup`, `setup_codes`, `passkeys`, `sessions`, `tokens`, and `project_settings`").
The conclusion stands on its other argument (a target changes rarely and is read once per export), so nothing in the plan changes.
Fix: note it in the ledger line for d-j5s0h0; no new record is needed unless the target later wants a table.

### M-11 · Minor · Task 9 changes `readSettings` but not plan 3's test that it leaves `[hook]` alone

Handles: plan line 449 (`readSettings` checks `[hook]`); plan 3 at 3e4c29c, Task 3 (`hook_is_left_alone` in `ts/tests/cli/settings.test.ts`); plan line 433 (Modify lists `ts/src/cli/settings.ts`, not its test).
Failure: if `hook_is_left_alone` writes a `[hook]` table lodge 0.2 would refuse, it fails once Task 9 lands, in a file the task may not edit.
Fix: list `ts/tests/cli/settings.test.ts` under Task 9's Modify, its `hook_is_left_alone` renamed to what it now asserts.

### M-12 · Minor · a bad export target is accepted and then fails every minute

Handles: plan line 416 (`export-target` stores any `repository`, `branch`, and `remote`); line 215 (`exportStore` refuses a bad branch name with `_name`'s message, which begins `.lodge.toml: store.branch`, `src/lodge/gitstore/settings.py:78-83`); line 362 (a throw is logged and retried a minute later).
Failure: a typo in the branch name or the repository path is answered `{"target": …}` and then logs `the export of <project> failed` every minute, with a message naming `.lodge.toml`, which the person never wrote.
Fix: `export-target` checks the branch name with the same rule and its own message (`export-target: branch must be …`) before storing; `Moving` gains a check of the repository's existence from `main` if that is wanted.

### M-13 · Minor · IMP-1's B understates its change to Task 6

Handles: `questions.md:19` ("B changes one function of Task 6 (`exportFiles` writes `author` for the owner)"); plan line 347 (`exportFiles(current, attachmentTexts)` has no owner and no writer).
Under B, `exportFiles` needs the project's owner (from `Projects`, through `ExportPorts`) and must parse and rewrite each decision and thread through the writers, refusing as Task 5 does, so `ExportPorts` and `Exporters` change too.
Fix: say so in IMP-1, so that the author weighs the real cost.

## Checked and holding

- Every name of the table "Names this plan consumes from plans 2 and 3" exists at 7204ad3 and 3e4c29c with the signature the plan gives: `Clock` with `sleep`, `Store` with `attachmentTexts` and Task 12's methods, `Projects` (plan 3's `create(…, settings?)`, `settings`, `names`), `Role`, `actorText`, `stampOf`, `coreSettings(table)`, `Forbidden`, `decodeUtf8` and `encodeUtf8` through `#core`, `Tree.people` and the two thread functions with `people`, `appendEvents(tx, project, actor, at, events)`, `FixedClock` with `slept`, `MemoryStore` with `publishes` and `people`, `ApiOptions` (`projects`, `lodgeFor`), `lodgesOver`, `Accounts.setup()`, `Io`, `run`, `parse`, `readSettings`, `CliError`, `ServerIo.open`, and the help tests; plan 2's file is unchanged between 7204ad3 and `origin/server-store`'s be72406, and both plans' reviews are now in (plan 3's at 1b4ba97), so their fix rounds may still move names.
- The importer keeps IDs, dates, codes, and `imported_from` (Task 5's `ids_dates_codes_and_imported_from_are_kept`, Task 10's byte comparison); the owner mapping has its tests; "one owner" narrows design line 78's "first owner" with its reason in d-y42b7b (plan 2's `members` is in code-point order, so "first" has no meaning there, and step 1 has one person, design line 304).
- The export: one way, a bare or separate repository and a project's own 0.2 branch as targets, no work tree, no force, no commit when unchanged, at most one commit a minute within one server run (M-6 for restarts); every published write reaches it through the wrapped store, the import included.
- The hook: the moved advice for records, threads, and frozen files, in both modes, never `git checkout`; silent on every failure; the carried tests by name (M-1 and M-2 for two mechanics).
- The design's records and the freeze: Tasks 11a to 11c edit the seven entries plan 1 names and narrow only coordinator decisions (`lodge show` of d-zq5sfb, d-jxwj8m, d-cg3nn3, d-a3e8kb: each `coordinator`), and freeze the document after its last line.
- Probe 3 re-run: `lodge check` exits 1 with `check 3: d-t46j05: confirms is for author decisions, but decided_by is ana` (also for `person:ana` and `ana@example.com`), `lodge spec` and `lodge waiting` unchanged, and `lodge show d-q59cdf` loses ` · confirmed by the author (d-t46j05)`, as `probes.md:12-18` says; the change must be committed, since uncommitted it shows as check 5 problems instead.
- d-0q54zn: `run`, `readStore`, `exportStore`, and the store's blobs decode and encode through plan 2's codec; the three places of M-3 are unnamed.
- d-1skjw1, d-83kt6y, d-ryss91, d-pv341r, d-sj6hmf, d-va3j7x, d-bs5mm8, and d-yng7m8 hold against the design lines they cite; d-ag8p8h and d-y42b7b fall in part (B-1), and d-j5s0h0's reasoning has one stale handle (M-10).

## Files read and not read

Read: the plan, its ledger, `planner-brief.md`, `planner-report.md`, `probes.md`, `questions.md`, and `probes/zero-two-store/` in full; the server design in full; plan 1's Global Constraints, Review Focus, "The rest of build step 1", and "Settled for the later plans"; plan 2 at 7204ad3, "Interfaces for plans 3 and 4" and Tasks 2, 7a, 7b, 10, 11, and 12; plan 3 at 3e4c29c, Calls made, Review Focus, Order and lanes, Names consumed, and Tasks 3 to 6, with greps of Tasks 2, 7a, and 8; plan 3 at f2dcc72, Task 4's events line; `ts/src/core/index.ts`, and greps of `check-state.ts`, `snapshot.ts`, `fileformat.ts`, `threads.ts`, and `parity.json` at `origin/server-core`; `src/lodge/hook/post_tool_use.py`, `src/lodge/main.py:55-86`, `src/lodge/gitstore/trees.py`, `setup.py`, `settings.py` (parts), `plumbing.py:1-26`, `src/lodge/core/check_state.py:110-150`, `check_change.py:1-120`, `check_entries.py` (greps); `tests/hook/test_post_tool_use.py`, `tests/e2e/test_hook_feedback_after_hand_edits.py`, `tests/e2e/test_hook_outside_repository_exit_0_silent.py`, `tests/e2e/test_add_import.py:30-34`, `tests/gitstore/conftest.py`; the eleven rulings and d-0q54zn, d-2jk0mw, d-j3z85y with `--reasoning`; the heads of the seven entries and four decisions Task 11a edits.
Not read: plan 1's tasks and parity table beyond the rows named; plan 2's Tasks 3 to 6, 8, 9, 13, and 14; plan 3's Tasks 1, 2, 7a, 7b, 8, and 9 beyond greps; the probe sources in `probes/` (`decode.ts`, `export-probe.ts`, `fixture.py`, and the rest), so probes 1, 2, 4, 5, 6, and 8 were not re-run; plans 2 and 3's review files; `ts/tests/structure/table.ts`.
