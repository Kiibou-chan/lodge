# lodge on itself: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task by task.

**Goal:** lodge holds its own specification, decisions, and build rulings, and agents working on lodge read them through lodge.

**Architecture:** no code changes; every record goes in through `lodge add` in checkout mode on branch `lodge-on-itself`.
The design document is frozen once its content is in lodge, and the hook warns on hand edits.

**Tech stack:** lodge 0.1.0 from this checkout (`uv run lodge …`), git.

**Spec:** `docs/superpowers/specs/2026-10-29-lodge-design.md` at 47dcfa7; Rollout 2: "lodge's own decisions go into lodge as soon as it can hold them, starting with this brainstorm's; until then they live in this document"; her decision "Replace, not sit beside: 'they would be replaced by the tooling'".

## Global Constraints

- Record files are written only through `lodge add`; never by hand, never with `git checkout` or `sed` on `lodge/`.
- Drafts are written under `.drafts/` at the worktree root (git-ignored, added to `.gitignore` in Task 1), never under `lodge/`.
- `lodge add --dry-run` before every `lodge add`; a `check` line stops the task.
- Author decisions: `decided_by: author`, `quote.text` her words verbatim, reasoning equal to the quote text and nothing else (the done ledger, line 211).
- Agent decisions: `decided_by: coordinator`; their text is agent text and never presented as hers.
- Public repository: no personal paths, machine names, or another project's records or figures; the first user is named only as "the first user".
- British English, no em-dashes, Oxford comma, one sentence per line in Markdown, including record bodies.
- `sh scripts/check.sh` green after every task (it ends with `lodge check --gate`).
- Commit with explicit paths, identity and trailer as in `CLAUDE.md`, push the branch after each commit.

## Calls made

- The design document is frozen, not deleted: it is the provenance the author decisions' `where` names, and the hook's `frozen` glob makes a hand edit visible; one line at its top says the specification now lives in lodge.
- Spec entries are agent text created by one agent decision per area, so check 4 is satisfied and each area's creation reads on its own; no entry restates an author quote.
- Build rulings go in as imported agent decisions: `imported_from: {file: docs/superpowers/plans/done/2026-10-29-lodge-progress.md, heading: "line <n>"}`, the ledger added to `[import] sources`, the date the author date of the commit that added the line, taken from the old-history bundle (`.git/lodge-old-history-2026-10-29.bundle` in the main checkout) when the line predates the squash, else from the current history.
  Imported, because the ruling was made at that date in that file; an import shows `imported` at level 1, which is true.
- LODGE-3 ("private on GitHub") still reads as current, since LODGE-4 does not list it in `replaces`; an agent decision replacing LODGE-3, citing LODGE-4, fixes the read and raises the review flag for her to confirm, since only she may settle it.
- LODGE-8 is her ruling of 2026-10-29 22:12, "Nothing is my text except than quotes, everything else was written by an agent.", which settled the question asked as LODGE-8.
  Her "Remove them completely" (2026-10-29 22:12) goes in as an author decision without a code: the public repository holds no private information.

## Review Focus

1. An entry that says more than the spec, or contradicts a later ruling the spec absorbed (LODGE-9, LODGE-10): `lodge spec` read against the spec section by section.
2. A ruling whose statement drops its "cost if wrong", or turns an agent's call into something that reads as hers.
3. A date taken from the squashed history (22:4x on 2026-10-29 for nearly every line) instead of the bundle, which orders rulings wrongly against the author decisions.
4. A hook that fires on every edit, or never: run it on a hand edit of a record, of the frozen document, and of an ordinary source file.
5. `CLAUDE.md` still pointing agents at the design document for rulings.

---

### Task 1: Her decisions and the LODGE-3 replacement

**Files:** `.gitignore` (add `.drafts/`), records via `lodge add`.

- Author decisions, each with `code` where she has one, quote verbatim:
  - LODGE-8: quote "Nothing is my text except than quotes, everything else was written by an agent.", where "lodge build session", when "2026-10-29 22:12"; statement: only her quotes in lodge are her text, every other text in the repository is agent text; scope `process`.
  - LODGE-9 and LODGE-10: quote, where, and when as the spec's "Her decisions" gives them; statements as there; scope `product`.
  - No code: quote "Remove them completely", where "lodge build session", when "2026-10-29 22:12"; statement: the public repository holds no private information; scope `process`.
- Agent decision replacing LODGE-3 (`replaces: [d-7m3rc1]`), statement: the repository is public on GitHub; reasoning cites LODGE-4 (d-dd17rs or whichever record carries `code: LODGE-4`).
- Verify: `uv run lodge show LODGE-8`, `LODGE-9`, `LODGE-10` each print the quote at level 1; `uv run lodge waiting` lists the LODGE-3 replacement; reasoning equals quote over all author records, by script; `sh scripts/check.sh` ok.

### Task 2: The specification in lodge

**Files:** records via `lodge add`.

- Areas, in this order, each with a title and a one-line intro: `purpose` (Intent, Goals, Non-goals, Must nots, success measures), `model` (The model), `levels` (Levels), `writing` (Writing, feedback, the check and its seven checks), `reading` (Reading, The viewer), `hook` (A hook against writing elsewhere), `storage` (Storage, settings), `structure` (Structure), `rollout` (Rollout).
- The spec's "Open" and "Left to the builder" sections and her quotes do not become entries.
- One entry per claim a reader would look up on its own, one paragraph, within 150 words; about 40 to 70 entries in all.
- One agent decision per area, `scope: product`, `changes` listing every entry of the area with `create`, statement "The <area> part of lodge's specification moves from the design document into lodge", reasoning naming the spec section and Rollout 2.
- Verify: `uv run lodge spec` renders every area with no flags; a coverage table in the task report maps each spec section (lines 8 to 273) to the entries holding it and lists anything left out with the reason; `sh scripts/check.sh` ok.

### Task 3: Build rulings as decisions

**Files:** `.lodge.toml` (`[import] sources`), records via `lodge add --import`.

- One imported agent decision per `Ruling:` line of `docs/superpowers/plans/done/2026-10-29-lodge-progress.md` (61 lines by `grep -c 'Ruling:'`), `decided_by: coordinator`, `scope: build`.
- Title: the ruling's subject in at most 100 characters; statement: the "what"; reasoning: the "why", then "Cost if wrong: …", verbatim from the line where possible.
- Date: as in "Calls made"; the task report lists each line number with its date and the commit it came from.
- Drafts are generated by a script kept in `.drafts/`, not committed; the dry run's summary for all 61 is in the report.
- Verify: `uv run lodge search` finds a ruling by a word of its statement; the number of decisions with that `imported_from.file` is 61; `sh scripts/check.sh` ok.

### Task 4: The hook, the frozen files, and CLAUDE.md

**Files:** `.claude/settings.json`, `.lodge.toml` (`[hook] frozen`), `docs/superpowers/specs/2026-10-29-lodge-design.md` (one line at the top, before freezing), `CLAUDE.md`.

- `.claude/settings.json`: the README's `PostToolUse` hook, command `uv run lodge hook post-tool-use`, matcher `Edit|Write|MultiEdit`.
- `frozen = ["docs/superpowers/specs/2026-10-29-lodge-design.md", "docs/superpowers/plans/done/**"]`.
- The design document's top line: the specification and her decisions now live in lodge (`lodge spec`, `lodge show`), and this document is frozen.
- `CLAUDE.md`: "Authority" and "Her rulings" point to `lodge spec`, `lodge show`, and `lodge search`; the design document is named as frozen history.
- Verify: pipe a synthetic `PostToolUse` JSON for an `Edit` of a record file, of the frozen design document, and of `src/lodge/main.py` into `uv run lodge hook post-tool-use`; the first two print feedback, the third prints nothing; `sh scripts/check.sh` ok.
