# Task 5 brief: the hook, the frozen files, and the instructions

You build Task 5 of the plan `docs/superpowers/plans/2026-10-30-lodge-on-itself.md` in this worktree, on branch `lodge-on-itself`.
Read first, in this order: `CLAUDE.md`, the plan's Global Constraints (lines 14 to 26), "Calls made" (lines 28 to 46), and Task 5 (lines 94 to 103).
Those are your requirements, with the exact values to use verbatim.
Then read `README.md` ("Writing", "The hook", "Settings") and run `uv run --frozen --quiet lodge guide`.

## Settled since the plan was written

- Task 3 (her confirmation) is deferred: the author will confirm through the viewer once it can.
  So lodge becomes the authority now, and the instructions must not claim that the entries are confirmed by her.
  Say instead that the entries are agent text written from the design document she approved, and that her own decisions are those with `decided_by: author` (`lodge search --by author`).
- The progress file `docs/superpowers/plans/2026-10-30-lodge-on-itself-progress.md` holds this plan's rulings as lines starting `Ruling:`.
  Each goes into lodge as one live coordinator decision: `decided_by: coordinator`, `scope: process`, `work_item: docs/superpowers/plans/2026-10-30-lodge-on-itself.md`; title its subject (at most 100 characters), statement the "what", reasoning the "why" then "Cost if wrong: …", verbatim where possible.
  Then append ` (d-xxxxxx)` to the end of each such ledger line, with the ID `lodge add` printed.
  Rulings that quote the author keep her words in quotation marks inside the reasoning, attributed, and never as the statement; these are coordinator decisions, not hers.
- The design document's new top line goes in before the frozen glob is added (the hook only advises, but keep the order).
- `CLAUDE.md` line 3 and 4 name the design document as the authority and the spec's "Her decisions" as the place for her rulings; rewrite them per Task 5.
  The build process paragraph's "`Ruling: <what>; why: <why>; cost if wrong: <cost>.` in the ledger" becomes: the ruling is recorded with `lodge add` (scope `process`, `work_item` the plan) and the ledger line gives its ID.
  Make the same change wherever `.claude/agents/*.md` says it.
- Keep every edited Markdown file to the repository's rules: British English, no em-dashes, Oxford comma, one sentence per line.

## How you work

- Drafts go under `.drafts/` (git-ignored), never under `lodge/`; `lodge add --dry-run` before every `lodge add`; never edit a file under `lodge/` by hand.
- Answer "looks related, does it replace or narrow" feedback from the ruling's own text; if unsure, it is neither.
- Do not commit and do not push: the coordinator does both.
- Verify per Task 5's Verify line: pipe synthetic `PostToolUse` JSON (`{"tool_name":"Edit","tool_input":{"file_path":"<absolute path>"},"cwd":"<worktree>"}`) into `uv run --frozen --quiet lodge hook post-tool-use` for a record file, the design document, a brief in `docs/superpowers/plans/done/2026-10-29-lodge/`, and `src/lodge/main.py`, and record what each printed; skip the "worktree without `.venv`" case and say so.
  Then `git grep -n '2026-10-29-lodge-design.md\|Ruling:' -- CLAUDE.md .claude` and `sh scripts/check.sh`.

## Report

Write `docs/superpowers/plans/2026-10-30-lodge-on-itself/task-5-report.md`: what you changed per file, each ruling line with its new decision ID, the four hook outputs verbatim, the grep output with a note on each remaining hit, the gate's last lines, and anything you were unsure of.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the gate, and your concerns.
