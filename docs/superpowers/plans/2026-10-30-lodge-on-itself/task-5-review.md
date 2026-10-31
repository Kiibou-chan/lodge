# Task 5 review

Reviewed commit 645a537 against 019e929, in the worktree on `lodge-on-itself`.
Result: 0 Blocking, 1 Important, 8 Minor.

## Files read

Read: `CLAUDE.md`; the brief and report for Task 5; `task-5-codex-final.txt`; the plan's Global Constraints, Calls made, Review Focus, and Tasks 1 to 5; the whole diff of `.claude/`, `.lodge.toml`, `CLAUDE.md`, the progress file, and the design document; `README.md` lines 100 to 162; all 12 new decisions through `uv run --frozen --quiet lodge show ID --reasoning` and, for most, `--provenance`.
Not read: the raw bodies of the 12 record files (by instruction), the other 124 files under `lodge/decisions/`, any source under `src/` and `tests/`.

## What I ran

- `sh scripts/check.sh` in this worktree: exit 0, 1071 passed, `lodge check --gate` ok.
  The builder's 14 failures were its sandbox denying sockets (`PermissionError`), not a defect.
- The four hook probes from the dispatch: advice for a file under `lodge/decisions/` and for the design document; zero bytes for `docs/superpowers/plans/done/2026-10-29-lodge/task-5-brief.md` and `src/lodge/main.py`; all exit 0.
- Extra probes: a `Write` of the frozen done ledger gives advice; an `Edit` of this plan's progress file is silent.
- A detached worktree without `.venv`, probe removed afterwards: the hook gave the same advice for the design document in 1.4 s, exit 0, and created the `.venv`.
  The builder skipped this case; it holds.
- `git grep -n '2026-10-29-lodge-design.md\|Ruling:' -- CLAUDE.md .claude`: one hit, `CLAUDE.md:7`, which calls the document frozen history.
- A scan of the added lines of every non-record file and of all 12 records for personal paths, machine names, em-dashes, and American spellings: nothing found.
  The identity string at `CLAUDE.md:44` is the existing public no-reply address, unchanged apart from line joining.

## Pass 1: correctness

Met:

- `.claude/settings.json:1-15` has the README hook with the required matcher and command.
- `.lodge.toml:7-8` freezes exactly the two files the plan names.
- Twelve `Ruling:` lines exist in the progress file (lines 7, 10, 11, 12, 17, 18, 23, 28, 29, 33, 38, 39); each ends with one `(d-xxxxxx)`, and the ID matches its ruling by statement, which I checked pair by pair.
- Each ID is one live coordinator decision with scope `process` and `work_item: docs/superpowers/plans/2026-10-30-lodge-on-itself.md`.
  `lodge search --by coordinator` lists all 12 once.
- Every statement is the ruling's "what" and every reasoning its "why" followed by "Cost if wrong: …", verbatim from the ledger line.
  The two rulings that quote her (`d-x1aacr`, `d-x4spd2`) keep her words in quotation marks, attributed to "The author" inside the reasoning, never in the statement.
- Figures carry handles (`d-026tsm` has 2%; `d-4e25kk` has 82, 94%, and 95%).
- Titles are at most 100 characters.

### Important

**I1 · The new top line shifts every line handle into the design document by two**

`docs/superpowers/specs/2026-10-29-lodge-design.md:1-2` adds a line and a blank line above `# lodge design`.
Fifteen records cite the document by line, 25 handles in all (for example `d-z57dy1` cites `lodge-design.md:93`, `d-f84m43` cites `:53-58`, `d-fkndvh` cites `:238` and `:241`, `d-92t2m8` cites `:135` to `:138`, `d-18terz` and `d-c08bdw` cite `:122-126`, `d-4032xv` cites `:167`).
I checked five of them: the cited text (for instance the "**Decision** (prefix `d-`)" line, 93 before) is now at 95, and so on.
The document is frozen and the records are not hand-editable, so each handle points two lines early for good, and `lodge check` does not notice.
The design document is the provenance the plan's Calls made says the records point at, so this breaks the handle each argument is meant to carry.
The plan and the brief say "top line", so this is a plan conflict and needs a ruling recorded with `lodge add`.
Fix: move the notice to the end of the file after a blank line, which keeps every existing line number, and record the ruling (what: the notice goes last; why: 25 handles in 15 records cite lines; cost if wrong: a reader sees the freeze notice only at the end).
Putting the text in a single line already present, for example joining it to the Status line (`:3`), also keeps the numbers but changes a cited line.
The second-best fix, if the top line stays: a coordinator decision that states every `lodge-design.md:N` handle written before 2026-10-31 is two lines early, which `lodge show` readers will not find unless they search for it.

## Pass 2: practice

### Minor

**M1 · Statements open with a label from a review file lodge does not hold**

`d-04jnwq` ("M3, no LODGE-3 replacement."), `d-0cj3bn` ("M9, her decisions …"), `d-kanyrm` ("I1, d-dhz8an narrows …"), `d-eae44h` ("I2, a ruling is dated …"), and `d-74sttc` (reasoning "N1 was the only Important") name findings of `plan-review.md`, `task-4-review.md`, or `task-1-2-recheck.md` without saying which.
A reader of `lodge show` cannot resolve M3 or I1.
Scenario: `lodge search "I1"` matches several unrelated records, and a later agent cannot tell which review is meant.
Fix: these are verbatim from the ledger, which the brief asked for; the cheapest repair is a replacing decision per record that drops the label or adds the review file as a handle.
It is a Minor, so it can wait for the final wave.

**M2 · Two reasonings are fragments, and `d-74sttc`'s statement omits the tasks**

`d-x4spd2` reasoning is a noun phrase ("The author's words on …, "Use codex …"") with no clause saying why.
`d-74sttc` statement ("The coordinator rechecked fix round 2 itself.") does not say that it is the fix round for Tasks 1 and 2; only its title does.
Fix: as M1.

**M3 · Times without dates in `d-wfxez9` reasoning**

"dated 19:32:58" and "dated 22:43:31" give no day, so the reader cannot compare them with the record dates.
They are verbatim from the ledger line, so this is a ledger wording matter rather than the builder's fault.

**M4 · The rulings are dated 2026-10-31, not the day they were made**

Most of the 12 were made before 2026-10-31 (the ledger names `d-2hcgav` at 2026-10-30 09:34 after several of them), but every record shows 2026-10-31, so the timeline orders them by the day they were added.
The plan asks for live decisions, so this is as specified; the reasoning could have said when each ruling was made.
Fix: none needed now; if it matters, state the ruling date in a replacing record.

**M5 · The report's gate line reads as a failure**

`task-5-report.md` ends its gate section on "14 failed" and exit 1, and `task-5-codex-final.txt` says the same.
The failures are the builder's sandbox (no sockets); in an unrestricted shell the gate passes (1071 passed here).
Fix: the coordinator runs the gate once outside the sandbox before committing further; I did, and it is green at 645a537.

**M6 · The report's account of the git index**

The report says `lodge add` ran against a temporary index under `.drafts/` because the real metadata directory was read-only.
The commit now holds all 12 records and `git status` shows only the two untracked viewer files, so nothing is lost, but the claim "I used alternates" cannot be checked from the commit.
Fix: none; the record is complete and the gate agrees.

## Pass 3: design

The instructions agree.
`CLAUDE.md:3-9` and the five agent files each give the same authority (`lodge spec`), the same way to read decisions and her own (`lodge show`, `lodge search`, `--by author`), the same status of the entries, and the design document as frozen history.
Nothing still sends a ruling to the ledger alone: the planner (`planner.md:17-18`), integrator (`integrator.md:16-17`), and `CLAUDE.md:42-43` all say `lodge add` with scope `process` and `work_item` the plan, and the ledger line gives the ID.
The README's hook and settings sections match `.claude/settings.json` and `.lodge.toml`; the settings use `uv run --frozen --quiet` where the README shows plain `lodge`, as the plan specifies.

### Minor

**M7 · The same four lines sit in six files, and one of them is time-bound**

The block "The binding authority is …; The entries are agent text … awaiting her confirmation through the viewer. …" is repeated at `CLAUDE.md:3-7` and in `builder.md:10-13`, `planner.md:10-13`, `reviewer.md:10-13`, `rechecker.md:10-13`, and `integrator.md:10-13`.
"Awaiting her confirmation" stops being true when Task 3 runs, and nothing but memory reminds anyone to edit six files.
Scenario: Task 3 completes, one agent file keeps saying the entries are unconfirmed, and a reviewer treats confirmed entries as agent text.
Fix: every agent already reads `CLAUDE.md` first, so keep the status sentence there only and let the agent files say "as in `CLAUDE.md`"; or add the six-file edit to Task 3's file list.
Two smaller drifts: `reviewer.md:15` still says "the spec's must-nots" where the other files say `lodge spec` or "the specification", and `CLAUDE.md:44` says "the spec" where `integrator.md:17` says "the specification".
Neither misleads.

**M8 · `CLAUDE.md` does not mention the hook or the second frozen file**

`CLAUDE.md:7` says the design document is frozen but nothing tells an agent that the done ledger is frozen too or that the hook gives the advice.
The hook text itself says what to do, so an agent that edits a frozen file is told; the cost is a wasted edit.
Fix: one line in `CLAUDE.md` Hard rules: the hook advises on record files and on the `frozen` globs of `.lodge.toml`.

Two plan rules still have no check: that every `Ruling:` line in a progress file ends with a decision ID, and that the ID names a live coordinator decision.
I did both by hand (12 of 12).
A later code plan could add a check; that is the author's call.

## Summary

0 Blocking, 1 Important (I1, the shifted line handles), 8 Minor (M1 to M8, of which M3 to M6 need no action).
Hook checks, ledger IDs, decision wording, and the gate all pass.
