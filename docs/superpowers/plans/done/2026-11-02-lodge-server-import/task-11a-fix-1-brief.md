# Brief: fix round 1 for Task 11a of `docs/superpowers/plans/2026-11-02-lodge-server-import.md`

Worktree `/var/tmp/lodge-import-records`, branch `server-import-records`; same rules as `task-11a-brief.md` in this folder (records only through `lodge add`, dry run first, drafts under `.drafts/task-11a/`, coordinator decisions only, never an author decision narrowed or replaced).
The Sonnet review is `~/.cache/lodge-work/codex/plan4/sonnet-task11a-review.md`; read it for the probes.
Published decisions are immutable (`lodge guide`): a correction is a new decision with `replaces:` or `narrows:` of the coordinator decision you made in 3601469 (never of an older one unless the finding needs it), editing the entry in the same add; where a finding touches an entry only, a new decision that lists it with `edit` and says why.
Acceptance first: extend your `.drafts` acceptance script so each finding below fails against the current store, then pass after the adds.

1. Important I1: `s-165qfh` no longer states Python's structure rules (the size limit and the forbidden calls `os`, `subprocess`, `open` outside the I/O modules are stated nowhere now). Restate each environment's rules in its own sentence (lodge 0.2 in Python, the server in TypeScript); read the pre-3601469 text with `git show server-import:lodge/spec/<area>/s-165qfh-*.md` and `lodge show` of the earlier decision, and keep what held.
2. Minor M2: `s-20dnpp`'s work-tree rule holds only for a local target, not with a remote (`ts/src/git/export.ts`), and the sentence is ambiguous: state each case.
3. Minor M3: `s-yaz279` says every source file is refused if its writer does not reproduce it, but the code checks only files it would map (`ts/src/app/importing.ts`); it also repeats `s-b6jxhr`. State what the code does, once.
4. Minor M4: `s-3cagcv` has a garbled sentence about attachments. Minor M5: `s-07ar34` ends on a non-sequitur about the viewer. Minor M9: `s-a4jfp1` and `s-07ar34` cite "the server design" as if it were a handle: cite the decision (d-8kasej, d-b1yjpp) or say nothing.
5. Minor M8: two step assignments in `s-d1dd20` are inferences, not the design's Build order: take each step number from the design's Build order section, or drop the step and say in the report which claim the design gives no step.
6. Minor M1: the four decisions carry the same eleven number handles including ones they never use; the new decisions carry only the numbers their statements use, and "one commit a minute" gets a handle (`ts/src/app/exporters.ts`, `EXPORT_INTERVAL_SECONDS`). The old decisions stay as they are; say so in the report.
7. Minor M6: `s-j8tp0n` and `s-z1zvb4` dropped sentences the report does not name: name each dropped sentence and why in the report.
8. Minor M7 (`s-d1dd20`, `s-g8m3qv`, `s-5sgcxx` each carry several claims): split only where it is cheap and no `rests_on` breaks; otherwise park it in the report.

After the adds: `uv run --frozen --quiet lodge check` prints `ok`; `uv run --frozen --quiet lodge spec | grep 'changed since'` accounted for in the report; `sh scripts/check.sh` green.
Commit `lodge/` and the report extension with explicit paths, trailer `Co-Authored-By: Codex <noreply@openai.com>`, push the branch.
Extend `task-11-report.md` with a "Fix round 1" section (each decision, entry changed, finding answered, what was parked) and commit it.
Final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the checks.
