# lodge on itself: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task by task.

**Goal:** lodge holds its own specification, decisions, and build rulings, and agents working on lodge read them, and record new rulings, through lodge.

**Architecture:** no code changes; every record goes in through `lodge add` in checkout mode on branch `lodge-on-itself`.
The design document and the done ledger are frozen once lodge holds their content, and the hook warns on hand edits.

**Tech stack:** lodge 0.1.0 from this checkout (`uv run lodge …`), git.

**Spec:** `docs/superpowers/specs/2026-10-29-lodge-design.md` at 47dcfa7; Rollout 2: "lodge's own decisions go into lodge as soon as it can hold them, starting with this brainstorm's; until then they live in this document"; her decision "Replace, not sit beside: 'they would be replaced by the tooling'".

## Global Constraints

- Record files are written only through `lodge add`; never by hand, never with `git checkout` or `sed` on `lodge/`.
- Drafts are written under `.drafts/` at the worktree root (git-ignored, added to `.gitignore` in Task 1), never under `lodge/`.
- `lodge add --dry-run` before every `lodge add`; a `check` line stops the task.
- Scopes are `product` or `process` only; a `process` decision carries `work_item`, the plan it rules on.
- Author decisions: `decided_by: author`, `quote.text` her words verbatim, reasoning equal to the quote text and nothing else (the done ledger, line 211); the statement says only what her words settled.
- Agent decisions: `decided_by: coordinator`; their text is agent text and never presented as hers.
- Public repository: no personal paths, machine names, or another project's records or figures; the first user is named only as "the first user".
- British English, no em-dashes, Oxford comma, one sentence per line in Markdown, including record bodies.
- A number in a statement that is a task, item, or line label is not a figure and gets no `numbers` handle; a figure gets the file and item it comes from as its handle.
- `sh scripts/check.sh` green after every task (it ends with `lodge check --gate`).
- Commit with explicit paths, identity and trailer as in `CLAUDE.md`, push the branch after each commit.

## Calls made

- The design document is frozen, not deleted: it is the provenance the author decisions' `where` names, and the hook's `frozen` glob makes a hand edit visible; one line at its top says the specification now lives in lodge.
  Of `done/`, only the ledger whose rulings Task 4 imports is frozen; the briefs, reports, and reviews are not in lodge, and `CLAUDE.md`'s move to `done/` edits links there.
- Spec entries are agent text created by agent decisions, one per area or per group of an area, so check 4 is satisfied; each decision's reasoning carries the spec's own reasons for its entries where the spec gives one, within 1,000 words, so the why survives the freeze.
  No entry restates an author quote.
  Where Task 14 settled what the spec calls unchecked (spec:73-74, spec:81), the entry states what holds after Task 14, and the decision's reasoning cites done ledger line 221.
- Build rulings go in as imported agent decisions: `imported_from: {file: docs/superpowers/plans/done/2026-10-29-lodge-progress.md, heading: "line <n>"}`, the ledger added to `[import] sources`, `scope: process`, `work_item: docs/superpowers/plans/done/2026-10-29-lodge.md`.
  Imported, because the ruling was made at that date in that file; an import shows `imported` at level 1, which is true.
  Each is dated by the author date of the first commit whose ledger holds the ruling's text up to "; why:", read from the old-history bundle through a separate bare clone in the scratch directory (`git clone --bare <bundle> <scratch>/old.git`), never by a fetch into this repository, which would pull in old refs whose trees hold personal paths; lines added after the squash take the current history's date.
  All rulings go in one `lodge add --import`, in ledger order.
- A ruling that a later event overturned is imported as it was, then replaced by a live coordinator decision stating what holds now, with the later event and its ledger line as reasoning.
  The "looks related, does it replace or narrow" feedback is answered from that classification only.
- LODGE-3 needs no new record: LODGE-4 (d-y8p15p) already narrows it, and `lodge show LODGE-3` prints `narrowed by d-y8p15p`.
- LODGE-8 is her ruling of 2026-10-29 22:12, "Nothing is my text except than quotes, everything else was written by an agent.", which settled the question asked as LODGE-8.
  Her "Remove them completely" (22:12) answered D13, personal paths and private details in the repository and its history.
  Her other words in the done ledger that decided something (line 4, "Approved, build"; line 217, the merge go; line 220, the tag go, "Yes you may") are imported as author decisions with those quotes.
- The "looks related" feedback also fires on the area decisions, which change entries; spec:151 limits it to decisions that change, replace, and narrow nothing, so the answer there is no, and the ledger records the mismatch for the next code plan.
- From Task 5 on, a ruling is recorded with `lodge add` (scope `process`, `work_item` the plan), and its ledger line carries the decision's ID; this plan's own earlier rulings go in the same way in Task 5.

## Review Focus

1. An entry that says more than the spec, or contradicts a later ruling the spec absorbed (LODGE-9, LODGE-10, Task 14): `lodge spec` read against the spec section by section.
2. A ruling whose statement drops its "cost if wrong", or turns an agent's call into something that reads as hers.
3. A ruling dated from the squashed history (22:22 on 2026-10-29 for nearly every line) instead of the bundle, which puts the rulings out of their order in time.
4. A hook that fires on every edit, or never: run it on a hand edit of a record, of the frozen document, of a brief in `done/`, and of an ordinary source file.
5. A file that still names the design document as the authority or the ledger as the place for rulings: `git grep -n '2026-10-29-lodge-design.md\|Ruling:' -- CLAUDE.md .claude`.

---

### Task 1: Her decisions

**Files:** `.gitignore` (add `.drafts/`), `.lodge.toml` (`[import] sources`), records via `lodge add`.

- Live author decisions, `where: "lodge build session"`:
  - LODGE-8: quote "Nothing is my text except than quotes, everything else was written by an agent.", when "2026-10-29 22:12"; statement: only her quotes in lodge are her text, and every other text in the repository is an agent's; scope `process`.
  - LODGE-9 and LODGE-10: quote and when as the spec's "Her decisions" (spec:296-297) gives them; statements as there; scope `product`.
  - No code: quote "Remove them completely", when "2026-10-29 22:12"; statement: personal paths and private details are removed from the repository and from its history; scope `process`.
- Imported author decisions from the done ledger, lines 4, 217, and 220, with her quoted words and the line as `heading`, `scope: process`, `work_item` the done plan.
- Verify: `uv run lodge show LODGE-8`, `LODGE-9`, `LODGE-10` each print the quote at level 1; reasoning equals quote over all author records, by script; `sh scripts/check.sh` ok.

### Task 2: The specification in lodge

**Files:** records via `lodge add`.

- Areas, in this order, each with a title and a one-line intro: `purpose` (Intent, Goals, Non-goals, Must nots, success measures), `constraints` (Constraints), `model` (The model), `levels` (Levels), `writing` (Writing, feedback, the check and its seven checks), `reading` (Reading, The viewer), `hook` (A hook against writing elsewhere), `storage` (Storage, settings), `structure` (Structure), `rollout` (Rollout, and one entry per question in "Open").
- "Left to the builder" and her quotes do not become entries.
- One entry per claim a reader would look up on its own, one paragraph, within 150 words; about 40 to 70 entries in all.
- Decisions as in "Calls made", `scope: product`, `changes` listing each entry they create.
- Verify: `uv run lodge spec` renders every area with no flags; a coverage table in the task report maps each spec section (lines 8 to 304) to the entries holding it, and the spec's reasons to the decisions carrying them, and lists anything left out with the reason; `sh scripts/check.sh` ok.

### Task 3: Her confirmation of the specification

Waits on the author's answer to SPEC-1 (protection of the specification entries); the plan is revised to her answer before this task runs.

### Task 4: Build rulings as decisions

**Files:** records via `lodge add --import`, then live replacements.

- Select the rulings with `grep -nE 'Ruling( \(|:)'` over the done ledger: 62 lines.
- The task report first classifies each as standing, overturned (by which later ruling, author decision, or event, with its ledger line), or closed process.
- One imported decision per line as in "Calls made"; title: the ruling's subject in at most 100 characters; statement: the "what"; reasoning: the "why", then "Cost if wrong: …", verbatim from the line where possible, and the line "Line handles such as spec:N refer to the files at this ruling's date."
- Then one live coordinator decision per overturned ruling, replacing it.
- The report lists each line with its date, the commit it came from, and, for the lines rewritten after first being written (100, 124, 127, 169, 187), both candidate dates.
- Verify: 62 decisions with that `imported_from.file`; `uv run lodge show` on the line-188 record prints `replaced`; `uv run lodge search` finds a ruling by a word of its statement; `sh scripts/check.sh` ok.

### Task 5: The hook, the frozen files, and the instructions

**Files:** `.claude/settings.json`, `.lodge.toml` (`[hook] frozen`), the design document (one line at the top, before freezing), `CLAUDE.md`, `.claude/agents/{builder,planner,reviewer,rechecker,integrator}.md`, this plan's ledger, records via `lodge add`.

- `.claude/settings.json`: the README's `PostToolUse` hook, command `uv run --frozen --quiet lodge hook post-tool-use`, matcher `Edit|Write|MultiEdit`.
- `frozen = ["docs/superpowers/specs/2026-10-29-lodge-design.md", "docs/superpowers/plans/done/2026-10-29-lodge-progress.md"]`.
- The design document's top line: the specification and her decisions now live in lodge (`lodge spec`, `lodge show`), and this document is frozen.
- `CLAUDE.md` and the agent files: the authority is `lodge spec`, with `lodge show` and `lodge search` for decisions and her rulings; the design document is frozen history; a ruling is recorded with `lodge add` and its ID goes in the ledger line.
- This plan's ledger rulings go in as live coordinator decisions, and their lines gain the IDs.
- Verify: Review Focus 4 by piping synthetic `PostToolUse` JSON into the hook command, once in a worktree without `.venv`; Review Focus 5's grep shows no stale instruction; `sh scripts/check.sh` ok.
