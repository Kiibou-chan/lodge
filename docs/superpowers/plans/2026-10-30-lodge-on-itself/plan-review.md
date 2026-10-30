# Plan review: lodge on itself

Plan: `docs/superpowers/plans/2026-10-30-lodge-on-itself.md` at 5a85651, branch `lodge-on-itself`.
Reviewer: one reviewer, two angles in order, correctness against the spec and `CLAUDE.md`, then practice and design.
Probes ran lodge 0.1.0 from this checkout, read-only here, and any write in a detached scratch worktree of HEAD under `.claude/worktrees/plan-probe`, removed afterwards.
The old-history bundle was fetched into scratch refs `refs/probe/*`; the fetch also created `refs/tags/v0.1.0.dev0` by tag auto-following (see I8); all three refs were deleted at once.

## Findings

Counts at the end.

### Pass 1: correctness against the spec and CLAUDE.md

**B1 · Task 3's `scope: build` is refused by lodge 0.1.0**
Handle: plan:71 (`scope: build`); `src/lodge/core/model.py:7-9` (`Scope` holds only `product` and `process`); spec:97.
Scenario, run in the scratch worktree: a ruling draft with `scope: build` and `lodge add --import --dry-run` exits 2 with `scope must be one of 'product', 'process', not 'build'`, so no ruling of Task 3 can be added.
Fix: `scope: process`, with `work_item: docs/superpowers/plans/done/2026-10-29-lodge.md` (spec:103, "for process scope, the work item it rules on"); with that change the same draft passes, and all 61 generated drafts passed one `--import --dry-run` and a real add in the scratch worktree with `lodge check --gate` ok.

**I1 · Task 2's areas leave out the spec's Constraints section, and some of its lines are stale**
Handle: plan:61 lists nine areas, none for "Constraints" (spec:67-81); spec:73-74 and spec:81 say the install from a public tag and the authorisation by a spawning prompt are not yet checked, which done ledger:221 (Task 14) settled.
Scenario: the builder follows the area list, the coverage table reports "Constraints left out", and Task 4 then points `CLAUDE.md` at `lodge spec` and freezes the document, so "files in git are the only source of truth", "public from the first commit", and the install route are in no live authority; or the builder files them under `purpose` verbatim, and `lodge spec` states as open what Task 14 answered (must-not 1, spec:57).
Fix: add a `constraints` area between `purpose` and `model`; for spec:73-74 and spec:81, write the entry as it holds after Task 14 (done ledger:221) and say so in that area decision's reasoning with the ledger line as handle.

**I2 · The spec's reasons are lost: entries carry no reasoning and the area decisions only name the section**
Handle: plan:64 (reasoning "naming the spec section and Rollout 2"); spec:89 ("It has no reasoning of its own; its reasoning is the decisions that changed it"); reasons that live only in the document, for example spec:111 (why a replaced file does not move), spec:120 (why only one link direction is stored), spec:185 (why the readable spec is not committed), spec:188 (why the guide is not copied), spec:215 (why settings are outside the data); Goal 1, spec:26 ("reasoning one explicit step away").
Scenario: after Task 4 freezes the document, `lodge show <entry> --reasoning` for "the reverse link is never stored" lists one decision whose reasoning says the model part moved from the design document; the why is reachable only in a file the hook now tells agents not to use, so the next agent re-argues a settled call, which is the cost the spec exists to cut (spec:16).
Fix: each area decision's reasoning carries, per entry or group of entries, the spec's own reason for it where the spec gives one (agent text, as those reasons were agent text, LODGE-8), within the 1,000-word guidance; where an area's reasons overflow that, split the area into one decision per **[my call]** group, each creating its entries.

**I3 · No entry is protected by the review flag, and Task 4 makes those entries the authority before the author has seen them**
Handle: plan:29 and plan:64 (every entry created by an agent decision); plan:84 (`CLAUDE.md` "Authority" points at `lodge spec`); spec:171 (an agent decision is flagged only when it touches an author decision, or an entry whose last change was an author decision); spec:294 (LODGE-6, a confirmed decision counts as hers); `CLAUDE.md:4` ("the plan argues from it, never over it").
Scenario: after the plan, an agent edits the entry stating check 5's immutable reasoning (LODGE-10) or the one stating that `decided_by: author` is trusted (LODGE-2); the entry's last change is a coordinator decision, so no flag is raised, `lodge waiting` stays empty, and the next plan argues from the changed entry while LODGE-10 still reads current (must-not 2, spec:58).
Meanwhile 40 to 70 agent paraphrases replace the document she approved ("Approved", 14:26, spec:3) as the binding authority without her reading them.
Fix: after Task 2, put the nine area decisions to the author for an author decision with `confirms` (her words quoted), which by LODGE-6 makes every later agent change to those entries flagged; Task 4's authority switch waits for that confirmation, and the ledger records it as waiting.
Smaller alternative if she declines: let the LODGE-9 and LODGE-10 author decisions, which this plan adds fresh, list the entries they settle in `changes` (Task 1 then runs after Task 2's areas exist), so at least those two are protected.

**I4 · Rulings that later events overturned are imported as current decisions**
Handle: plan:71-72 (one current decision per line, statement verbatim); done ledger:188 ("the pushed history keeps them", false since the rewrite at ledger:210); ledger:187 ("the spec and the brainstorm are her text", contradicted by LODGE-8); ledger:211 (paraphrases her ruling instead of naming LODGE-8, which Task 1 adds); ledger:77 (no why, no cost, "the builder's points 4 to 6" unreadable outside the ledger).
Scenario, run in the scratch worktree: after the import, `lodge show` on the line-188 record prints `current · coordinator · imported` and "the pushed history keeps them"; an agent reading it believes the old paths are still in the public history (must-not 1, spec:57), and lodge holds a current coordinator decision saying the spec is her text beside her LODGE-8 saying it is not.
The dry run of all 61 also gave 58 "looks related, does it replace or narrow" lines, which the plan does not say how to answer.
Fix: before drafting, the task report classifies each ruling as standing, overturned (by which later ruling, LODGE-9, LODGE-10, or the rewrite at ledger:210), or closed process; overturned ones get a live coordinator decision that replaces the import (statement: what holds now, reasoning: the later event with its ledger line), and the plan states that a "looks related" line is answered from that classification, not ad hoc.

**I5 · Freezing `docs/superpowers/plans/done/**` makes the hook say something false and fire on CLAUDE.md's own close-out step**
Handle: plan:82; `src/lodge/hook/post_tool_use.py:35-36` (frozen text: "lodge holds its content now, so do not edit it ... Otherwise reverse your own edit now"); `CLAUDE.md:7-8` (after a plan's last task, `git mv` into `done/` and fix links).
Scenario, run in the scratch worktree with the plan's globs: an `Edit` of `docs/superpowers/plans/done/2026-10-29-lodge/task-1-brief.md` prints the frozen text, though lodge holds none of the briefs, reports, or reviews (must-not 1); and when this plan closes, its own ledger and folder move into `done/` and each link fix is answered with "reverse your own edit now".
Fix: freeze only what lodge now holds: the design document and `docs/superpowers/plans/done/2026-10-29-lodge-progress.md` (the ledger whose rulings Task 3 imports); leave the rest of `done/` unfrozen.

**I6 · The agent definitions still name the design document as the binding authority**
Handle: plan:79 (Task 4's files: `CLAUDE.md` only); `.claude/agents/builder.md:9`, `.claude/agents/planner.md:9`, `.claude/agents/reviewer.md:9`, `.claude/agents/integrator.md:9` (each: the spec file is the binding authority); Review Focus 5 (plan:42) checks `CLAUDE.md` only.
Scenario: after a later decision edits an entry, a builder dispatched with `builder.md` reads the frozen document as binding and builds the old behaviour; the hook does not fire, because reading is not editing.
Fix: add the four agent files to Task 4: the binding authority is `lodge spec` with `lodge show`/`search` for decisions, the design document is frozen history; extend Review Focus 5 to `git grep 2026-10-29-lodge-design.md -- .claude CLAUDE.md`.

**I7 · New rulings keep going into ledgers, so the old way sits beside lodge from the next plan on**
Handle: `CLAUDE.md:44-45` and `.claude/agents/integrator.md:12`, `.claude/agents/planner.md:13` (a ruling is a `Ruling:` line in the ledger); spec:29 (Goal 4, "not sit beside them"); spec:38 (success measure 4, "no decision written anywhere else", "very important"); spec:225 (Rollout 2); this plan's own ledger already holds one (`2026-10-30-lodge-on-itself-progress.md:7`).
Scenario: Task 3 imports 61 rulings, and the next fix round writes its ruling as a ledger line again, so lodge's ruling record is incomplete from the first plan after this one and the success measure the author called very important fails on lodge itself.
Fix: Task 4 changes the ruling instruction in `CLAUDE.md` and the two agent files to "record the ruling with `lodge add` (scope `process`, `work_item` the plan), and put its ID in the ledger line"; this plan's own ruling at progress:7 goes in the same way.

**I8 · The plan gives no safe procedure for reading the old-history bundle, and the obvious one pulls old-history refs into this repository**
Handle: plan:30 ("taken from the old-history bundle"); done ledger:210 (the author had the history removed: "Remove them completely").
Scenario, which happened in this review: `git fetch <bundle> refs/heads/build-0.1:refs/probe/old-build` also auto-followed the bundle's tag and created `refs/tags/v0.1.0.dev0` at old commit b975932, whose tree holds files with personal paths (`git grep -l /home/ b975932` lists two); a later `git push --tags`, or any tool that pushes tags, would publish part of the history she had removed.
This reviewer deleted that tag and the probe refs straight away; the unreachable objects stay in the local object store until garbage collection.
Fix: Task 3 reads the bundle only through a separate clone outside the repository (`git clone --bare <bundle> <scratch dir>`, then `git -C <scratch dir> log`/`blame`), never a fetch into this repository, and its report says so.

**I9 · The "Remove them completely" record states more than she decided**
Handle: plan:34 and plan:53 (statement: "the public repository holds no private information"); done ledger:209-210 (her words answered D13, personal paths in the spec and the brainstorm on `main`, and led to the history rewrite); done ledger:177 (LODGE-8 arose because "four of her records state things she did not say").
Scenario: `lodge show` prints `author` beside a general rule about all private information that she never stated, which is the failure LODGE-8 was asked about, repeated in the record that comes with it.
Fix: the statement says what her answer settled, for example "Personal paths and private details are removed from the repository and from its history", and the general public-repository rule stays with LODGE-4 (d-y8p15p) and `CLAUDE.md`.

### Pass 2: practice and design

**M1 · The count of 61 misses one ruling**
Handle: plan:71 (`grep -c 'Ruling:'` = 61); done ledger:34 (`Task 1: Ruling (builder's, adopted):`, the `datetime` attribute ban, still in force in `tests/structure_rules.py`).
Scenario: Task 3's verify counts 61 and passes, and the one ruling written with the parenthesis stays only in the ledger.
Fix: select with `grep -nE 'Ruling( \(|:)'` (62 lines) and verify 62, or name line 34 as left out with a reason.

**M2 · "The commit that added the line" is ambiguous, and Review Focus 3's reason is backwards**
Handle: plan:30, plan:40, plan:73.
Run: ledger lines 1 to 209 are identical in the bundle's `build-0.1` and in the current file apart from two path lines (1 and 6), so line numbers carry over; `git blame` and the first commit containing each line's exact text agree for 55 of the 60 pre-squash rulings, and differ for lines 100, 124, 127, 169, and 187, which were rewritten after first being written; line 187's last edit is the redaction commit 2baa98c (22:20:16), so a blame-based date dates it at the redaction.
Dating from the bundle is otherwise sound: check 1 only refuses an import dated after now (`src/lodge/core/check_change.py:71-75`), and the 61 bundle-dated drafts passed the gate in the scratch worktree.
Review Focus 3 says squashed dates would misorder rulings against her decisions, but her 21 records are dated at their re-add, 22:16:38 to 22:17:05, so bundle dates (14:58 to 20:30) put every ruling before all of them, and squashed dates (22:22:19) after; neither orders them by when she decided.
Several rulings share one commit second (seven at 30f919b), and ties order by ID, which one add assigns ascending in draft order (done ledger:95).
Fix: define the date as the author date of the first commit whose ledger holds the ruling's text up to "; why:" (`git log --reverse` over the separate clone of I8), list the five rewritten lines with both dates in the report, add all rulings in one `lodge add --import` in ledger order, and correct Review Focus 3 to the timeline effect only.

**M3 · Task 1 names the wrong record for LODGE-4, and LODGE-3 already shows it is narrowed**
Handle: plan:54 (`d-dd17rs`); `lodge show LODGE-4` gives d-y8p15p, whose header has `narrows: [d-7m3rc1]`; d-dd17rs is "lodge has its own repository"; `lodge show LODGE-3` already prints `narrowed by d-y8p15p`, which plan:32 does not mention.
Scenario: the builder cites d-dd17rs in the replacement's reasoning; the record then points at the wrong decision for good, since decisions are immutable.
Fix: name d-y8p15p; the replacement's statement can say that LODGE-3's "private" no longer holds, since LODGE-4 already says the repository is public (run in the scratch worktree: the replacement is added, `lodge waiting` lists it, LODGE-3 shows `replaced`, gate ok).

**M4 · LODGE-9 and LODGE-10 take "where" from a spec section that gives none**
Handle: plan:52; spec:296-297 give the quote and time only.
Scenario: the builder invents a `where`, or copies "lodge brainstorm" from the older records, though these answers came in the build session.
Fix: `where: "lodge build session"`, as plan:51 gives for LODGE-8, and name where each verbatim quote was copied from (the ledger at done ledger:214-215 paraphrases; the spec at spec:296-297 holds the quote text); for LODGE-8, plan:33 is the only place its text appears in the repository, so name its source too.

**M5 · Task 3 says nothing about the number feedback or `work_item`**
Handle: plan:71-74; the scratch dry run of 61 drafts gave 48 number lines ("the text holds the numbers 20, 9 without a numbers handle"); spec:103 and spec:105.
Scenario: one builder adds 61 decisions ignoring 48 feedback lines, another invents handles; either way the result differs by builder.
Fix: state the rule: a number that is a task, item, or line label is not a figure and gets no handle; a figure (such as "20 of 20 rounds", ledger:134) gets the review file and item as its handle (`docs/superpowers/plans/done/2026-10-29-lodge/task-9-review.md, I1`); each ruling carries `work_item` as in B1's fix.

**M6 · Handles inside rulings point at line numbers that have since moved**
Handle: done ledger:86 cites "spec:174" for the quote at level 1 as LODGE-2's safeguard; in the current spec that sentence is at spec:178, and spec:174 is about where the flag shows.
Scenario: a reader of the imported ruling opens spec:174 and finds a different claim.
Fix: one line in each affected decision's reasoning, or once in the task report, that `spec:N` and `plan:N` inside a ruling refer to the files at the ruling's date, recoverable only through the author's bundle; or rewrite the handle to the current line where the claim still stands.

**M7 · The Open section has no live home once the document is frozen**
Handle: plan:62; spec:300-304 (licence, ID-prefix clash, length values).
Scenario: the licence question, the author's to settle before others use lodge, is recorded only in a frozen file agents are told not to edit.
Fix: one entry per open question in `rollout` (for example "No licence is chosen yet; the author chooses it before others are invited"), created by that area's decision.

**M8 · The "looks related" feedback fires on decisions that change entries, against spec:151**
Handle: spec:151 (feedback for a decision that "changes nothing, replaces nothing, and narrows nothing"); `src/lodge/core/feedback.py:144-158` checks only replaces and narrows.
Run: a scratch area decision creating two entries got "it replaces and narrows nothing, but these current decisions look related: d-txv0mv ..., d-n30kqr ...", both author decisions.
Scenario: each of Task 2's nine area decisions asks whether it replaces or narrows one of her decisions; a builder answering yes adds `narrows` on her decision, which raises a flag on a pure move.
Fix: the plan says the answer for the area decisions is no, and the ledger records the mismatch as a dogfooding finding for the next code plan (no code change here).

**M9 · The author's other decisions in the ledger are not imported**
Handle: done ledger:4 ("Approved, build"), ledger:217 (merge go), ledger:220 (tag go, "Yes you may"); spec:225 (Rollout 2, lodge's own decisions).
Scenario: lodge holds the coordinator's ruling that the tag waits for her go (ledger:174) but not her go itself.
Fix: import them as author decisions with `imported_from` and her quoted words, or state in Calls made why only `Ruling:` lines are imported.

**M10 · `uv run` in the hook builds a virtual environment on the first edit of a fresh worktree**
Handle: plan:81; in the scratch worktree the first `uv run lodge …` printed "Creating virtual environment" and built the package before answering.
Scenario: the first `Edit` in a new worktree or cloud session waits on a build; offline, `uv` may fail and the hook stays silent for the session.
Fix: `uv run --frozen --quiet lodge hook post-tool-use`, and Task 4's verify runs it once in a worktree without `.venv`.

## Files read

Read: `.claude/agents/reviewer.md`; `CLAUDE.md`; the plan and its progress ledger; the spec; `docs/superpowers/plans/done/2026-10-29-lodge-progress.md`; all 21 files in `lodge/decisions/`; `.lodge.toml`; `.gitignore`; `README.md` (hook and settings sections); `src/lodge/core/check_change.py`, `check_entries.py`, `model.py` (scope), `feedback.py` (related and numbers); `src/lodge/hook/post_tool_use.py`; grep of `.claude/agents/*.md` for authority and rulings; the bundle's ledger history (blame and per-commit text).
Not read: the done plan `docs/superpowers/plans/done/2026-10-29-lodge.md`, the review and report files in `done/2026-10-29-lodge/`, the rest of `src/lodge/` and `tests/`; the session transcript holding her verbatim LODGE-8 words, which is not in the repository.

## Counts

1 Blocking, 9 Important, 10 Minor.
