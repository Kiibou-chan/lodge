---
id: d-bc5jk7
kind: decision
title: "lodge uses Codex by MewTwo's procedure"
scope: process
decided_by: author
date: 2026-11-15T00:41:17+01:00
narrows: [d-94tynf]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
quote: {text: "Oh, and have your session adopt the same procedure as Mewtwo regarding the use of codex.", where: "lodge build session", when: "2026-11-15T00:37:10+01:00"}
numbers:
  - {value: "2", handle: "gloss session on MewTwo, the author's ruling 2026-11-14 11:08"}
  - {value: "0.9", handle: "gloss session on MewTwo, the author's ruling 2026-11-14 11:08"}
  - {value: "95", handle: "gloss task-session-rules.md, CR-301"}
---

Codex runs through gloss's wrapper with its question tool and a meter check before each start (stop above 95 %), at medium effort; it builds, fixes, reviews each task read-only, and rechecks; a Sonnet review covers each checkpoint and the branch's end, noting what Codex missed; a session runs up to 2 independent Codex tasks, pacing about 0.9 % of the weekly meter an hour; briefs follow gloss's Codex brief guide.

## Reasoning

The author asked lodge's build session to adopt MewTwo's procedure for Codex; MewTwo's gloss session sent her rulings of 2026-11-14 behind it: Codex used well and not wastefully (11:08), medium over high effort (11:12), Codex reviews between tasks with Claude at fewer checkpoints and quality kept (11:14 to 11:15), and briefs written for Codex (11:16, gloss `docs/codex-briefs.md` b31ad7896).
lodge's copies live outside the public repository: the wrapper, guard, meter, brief guide, and task-session rules under the build machine's lodge work folder.
It narrows d-94tynf, the way Codex runs, and leaves the author's rule that Claude subagents run on Sonnet or cheaper as it is.
Cost if wrong: a Codex review misses what a Sonnet review per task would catch; the `[CODEX-MISS]` count in the ledger shows it, and on a second branch with one, per-task reviews go back to Sonnet.
