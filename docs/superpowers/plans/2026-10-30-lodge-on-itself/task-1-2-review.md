# Review of Tasks 1 and 2: lodge on itself

Range 0b52da3..8d24943 on `lodge-on-itself` (Task 1 a2c7d62, Task 2 8d24943).
Reviewer: one reviewer, three passes in order (correctness, practice, design).
Records read only through lodge: `uv run lodge spec`, `uv run lodge show <ID> --reasoning --provenance` for all 7 Task 1 records, all 24 Task 2 decisions, and the 21 earlier author decisions at level 1, `uv run lodge search` probes, `uv run lodge check` (ok).
No probe worktree was needed; nothing on the branch was edited.

Counts: 0 Blocking, 9 Important, 11 Minor.

State that bounds every fix: the published state is the merge base with `main` (47dcfa7), which holds none of the Task 1 or Task 2 records, so all of them are still unpublished.
`lodge draft` refuses to edit a decision ("a decision is immutable, so change it with a new decision that replaces or narrows it", `uv run lodge --help`), so a wrong decision is fixed either by a new decision that replaces it, or by rebuilding the task's records from 0b52da3 through `lodge add` with corrected drafts (`.drafts/t1`, `.drafts/t2` still exist).
The rebuild touches `lodge/` with git, which the plan's Global Constraints (plan:16) forbid for `git checkout` and `sed`; choosing between the two routes is a coordinator ruling.
An entry is fixed by a new coordinator decision that edits it.

## Pass 1: correctness

### Important

**I1. The live author decisions carry a date a day after she made them, which puts them out of time order.**
Handle: d-9vxkjw (LODGE-8), d-qbfdqt (LODGE-9), d-z8jm5y (LODGE-10), and d-gqyp3n each show `2026-10-30` at level 1, while their quotes say 2026-10-29 22:12, 22:47, 22:46, and 22:12; `src/lodge/core/drafts.py:92-98` sets the date at add unless the draft is imported.
Failure: `uv run lodge search --by author` (newest first) lists LODGE-9 and LODGE-10 above the merge go d-axaz9w (22:49) and the tag go d-fw070q (23:33), both dated 2026-10-29, although the merge go was given after the fix round for LODGE-9 and LODGE-10 (done ledger line 217); the viewer's timeline of decisions (s-dm37qr) shows the same wrong order, and level 1 shows a wrong date (must-not 1, s-q4s548).
This is the defect Review Focus 3 guards against for Task 4, met here in Task 1.
Fix: import the four from the done ledger, which already holds each with its time (line 210 "Remove them completely", lines 211 to 212 LODGE-8, line 214 LODGE-10, line 215 LODGE-9), with `date` from the quote's when, by rebuilding Task 1's records from 0b52da3; or, if the coordinator rules against a rebuild, record a ruling that a live author decision is dated when recorded and its quote's when is the time she decided, so the timeline's order is known to be by recording.

**I2. d-gqyp3n's statement says more than "Remove them completely" settled, and nothing in the record says what "them" was.**
Handle: d-gqyp3n, statement "Personal paths and private details are removed from the repository and from its history."; the question was final review finding D13 (`docs/superpowers/plans/done/2026-10-29-lodge/final-review-design.md:99-102`): personal paths in the spec's Constraints and the brainstorm record's paths, plus whether the brainstorm record belongs in a public repository.
Her two words settled that set; "private details" is the ledger's own later wording (done ledger line 210), and the statement turns a one-off removal into a standing rule over the whole repository and its history, under `decided_by: author`.
Failure: an agent cites d-gqyp3n as her ruling that any "private detail" must be purged from history, for example the author's name in `CLAUDE.md`, which the final review judged the public GitHub identity (`final-review-design.md:106`); LODGE-8 makes every word but the quote agent text, so the overreach is an agent's claim shown as hers.
Fix: state only what D13 asked and what she answered, with the handle in the statement, for example "The personal paths and another project's file paths that final review finding D13 found in the specification and the brainstorm record are removed, from the history as well."; take it in the same rebuild or replacement as I1.

**I3. An entry and a decision say the author named one measure the most important; she said "very important".**
Handle: s-ph9z0t ("the author named this the most important measure"), d-5mhgpp reasoning ("the one the author weighted most"), `task-2-report.md:191`; against spec:38 and spec:198 ("4 is very important", "the one she named as very important"), her decision d-9k0dfe ("the very important one"), and d-s6mq0f's own reasoning ("very important").
Failure: a reader comparing measures, or the pilot weighting them, takes "most important" from s-ph9z0t as her ranking; three records now disagree on what she said, at level 1 in one of them.
Fix: s-ph9z0t edited by a new decision to "the author called this measure very important (d-9k0dfe)"; d-5mhgpp's reasoning replaced or rebuilt with the same wording.

**I4. Decision reasoning paraphrases her words as what she said, sometimes stronger than she said it, and never cites the author decision that holds the quote.**
Handle, by decision:
- d-cg3nn3: "Kotlin, which the author prefers" (spec:280: "I personally always like kotlin, but maybe that's too much for this for now"); "the author does not think she can install additional MCP servers"; "The author doubts that hard character limits would serve writers well".
- d-zq5sfb: "the author likes Kotlin, but judged it too much for now" (her "maybe").
- d-18terz: "She sized the reasoning at a few hundred words, up to a thousand or more at most" (her "A few hundred to maybe thousand(s) at most"; "a thousand or more at most" contradicts itself); "Her rule for provenance was" (spec:128 marks it "agreed", a proposal she accepted, not her rule).
- d-f84m43: "The author named the tool showing wrong information as the clearest must-not" (her "would definitely be one").
- d-5mhgpp: "The author's framing was", "her ruling was that the tooling takes their place".
- d-92t2m8: "the author doubts that hard limits would serve writers well, and guardrails alone usually already help" (her words, unquoted).
None of the 24 reasonings names an author decision by ID (checked: no `d-` ID in any reasoning), although her words are on record in d-7v4crf, d-rkcb17, d-c6n1ng, d-pf8xm9, d-n30kqr, d-vzvfg2, d-9k0dfe, d-vxfdz7, and the LODGE-coded decisions.
Failure: an agent arguing for a Kotlin server later cites d-cg3nn3, "which the author prefers", as her preference; the reader of the decision cannot reach her actual words from it, so the paraphrase is the only version in the read path, which is what LODGE-8 (d-9vxkjw) and must-not 1 rule out.
Fix: where a reason is her view, the reasoning names the author decision holding it ("the author's decision d-7v4crf") and states the agent's reading as the agent's, without verbs that grade her ("prefers", "judged", "clearest", "weighted most"); take it in the rebuild, or by replacing the six decisions.

**I5. Entries restate her quotes in agent text, which the plan forbids, and one turns her quote into a claim the spec does not make.**
Handle: plan:33 ("No entry restates an author quote"); s-rger6n ("Hard character limits may not serve the writer well, and guardrails alone usually already help", her quote in d-c6n1ng with "it" changed), s-bzatqh ("Provenance has to be accessible from the repository, because cloud transcripts are not always available", d-pf8xm9), s-7ah5n7 ("has to be evaluated first on the past and then in a pilot", "in whatever way makes sense", spec:46-47), s-a4jfp1 ("easily accessible", d-7v4crf), and s-rx9d11 ("and any other knowledge kept in files in the project", d-vzvfg2).
The spec's goal 4 (spec:29) is "Replace the first user's decision, ruling, and hand-kept specification files"; the "any other knowledge" part is only in her quote, and the non-goals (spec:46) put other kinds of knowledge out of scope for now.
Failure: s-rx9d11 says lodge replaces any other knowledge kept in files, and s-7ah5n7 in the same area says other kinds of knowledge are out of scope for now; a reader of `lodge spec` meets two current entries that contradict each other, and an agent following s-rx9d11 moves a project's to-do file into lodge.
In the other four, her hedges ("may not", "usually already help") read as the coordinator's, so text that is hers shows as an agent's, the reverse of I4.
Fix: one new decision editing the five entries: s-rx9d11 to the spec's goal 4 wording (decision, ruling, and hand-kept specification files, not sitting beside them), and the other four to the claim without her phrasing (s-rger6n: "Length limits are soft guidance, not hard limits."; s-bzatqh's third sentence: "Provenance is kept in the repository, not in transcripts."), each with the author decision ID in the new decision's reasoning.

**I6. A purpose entry states a goal that the pilot is to measure as if it already held.**
Handle: s-m83kjq, "A local web viewer lets the author find a decision quicker than by asking a session."; spec:28 lists it as goal 3, and spec:39 as a success measure still to be measured, as s-3ht96p does ("Finding a decision in the viewer is quicker than asking a session").
Failure: must-not 1, "a short entry reading more settled than it is" (spec:57): a reader of s-m83kjq alone takes the measure as met, while s-3ht96p says it is judged after the pilot.
The other goal entries (s-xx4pk4, s-rx9d11) describe the design and are true as statements of it; this one is an outcome.
Fix: a new decision editing s-m83kjq to "A local web viewer is meant to let the author find a decision quicker than by asking a session; the pilot measures it (s-3ht96p)." or removing the sentence, since s-3ht96p and s-dm37qr hold it.

**I7. A decision says writes are never refused, which LODGE-9 and s-edgt71 contradict.**
Handle: d-1x1mgv title "Writes go through lodge and get feedback, never a refusal" and statement "with feedback at write time and never a refusal"; s-hfjr1m's title "Write feedback is advice, never a refusal"; against s-edgt71 ("Only `lodge check --gate` and `lodge add` refuse (LODGE-9)") and spec:168.
The spec's own line 148 says feedback is never a refusal, which is true of the feedback; d-1x1mgv's title makes it a claim about writes, which LODGE-9's sentence on `lodge add` contradicts (Review Focus 1).
Failure: an agent reads d-1x1mgv at level 1 in a search, writes a draft that links to a replaced decision expecting feedback, and `lodge add` refuses it.
Fix: s-hfjr1m edited to add "A failing check still refuses the add (s-edgt71)."; d-1x1mgv rebuilt or replaced with the title "Writes go through lodge, and feedback advises without refusing".

**I8. An entry's title gives the wrong definition of the change the checks compare.**
Handle: s-zv83s7, title "The same change is the gap between two published states"; its own statement, s-edgt71, d-4032xv's title, and spec:166 say the gap is between the last published state and the state about to be published, which is not published.
Failure: `lodge search` and the viewer show the title first; a reader of the title takes both states as published and runs `lodge check --gate` after pushing rather than before, which is the gate's whole point (spec:167).
Fix: a new decision editing the title to "The same change is the gap between the published state and the one about to be published".

**I9. The seven check entries lose the spec's numbers, which the code and her LODGE-9 use.**
Handle: s-qzk2yb, s-g2jwha, s-yhppm5, s-kvwrqw, s-ms14fq, s-aw5a1j, s-s27z33 carry no number; spec:157-164 numbers them; `src/lodge/core/check_change.py:40` prints "check {n}"; d-qbfdqt says "checks 4 to 6".
Failure: `uv run lodge search "check 5"` ranks s-yhppm5 (the author-quote check, number 3) first and s-ms14fq (number 5) fourth of 18; an agent reading a `lodge check` message "already published, check 5: …" lands on the wrong check, and LODGE-9's "checks 4 to 6" cannot be resolved without counting the list in s-j70a0k.
A check number is a label, so it needs no `numbers` handle (plan:24).
Fix: a new decision editing the seven titles to begin with the number, for example "Check 5: changing an existing decision fails".

### Minor

**M1. LODGE-8's statement limits her text to quotes "in lodge".**
Handle: d-9vxkjw, "Only the author's quotes in lodge are her text, and every other text in the repository is an agent's."; her words have no "in lodge".
Failure: read literally, her verbatim quotes in the frozen design document (spec:5, "Quotes are the author's") and in the done ledger become agent text.
Fix: "Only the author's quotes are her text; everything else in the repository was written by an agent.", in the I1 rebuild.

**M2. LODGE-9's statement drops what "A" was chosen over.**
Handle: d-qbfdqt; spec:296 ends "chosen over keeping them at the gate only"; the quote is "A", and the reasoning may hold only the quote (plan:20), so the statement is the only place the rejected option can go.
Failure: a reader of d-qbfdqt cannot tell what the author rejected; d-4032xv's reasoning carries it, but that is a coordinator record.
Fix: append the clause in the I1 rebuild.

**M3. One claim sits in several entries, so a later change leaves a stale copy.**
Handle: whether a second project adopts lodge is open in both s-7ah5n7 and s-hh97bm; the viewer is read-only in s-582qav, s-dm37qr, and s-j5ttw1; soft length guidance in s-rger6n, s-fehz74, and s-yrz8fz; "same parser and check as the gate" in s-q4s548 and s-gg9chm.
Failure: a decision that settles the second-project question retires s-hh97bm and leaves s-7ah5n7 saying it "stays open"; the plan's "one entry per claim" (plan:75) and must-not 3 (s-4ykcm0) both say a claim lives once.
Fix: in the I5 edit decision, drop the last clause of s-7ah5n7 and the read-only sentence of s-j5ttw1; s-582qav may keep its reason and point at s-dm37qr.

**M4. Decision statements hold two sentences on one line.**
Handle: `lodge show` prints the statement of d-5mhgpp, d-f84m43, d-jj72ps, d-6cyjdh, d-z57dy1, d-zerbz9, d-18terz, d-1x1mgv, d-3epcjd, d-4032xv, d-mzkt6e, d-s6mq0f, d-a3e8kb, d-knqtc2, d-fkndvh, d-jxwj8m, d-n7whwk, d-bz7bav, and d-zh00c5 as two sentences on one line, where the earlier d-9k0dfe and d-pf8xm9 print one sentence per line; plan:23 applies the rule to record bodies.
Failure: line-based diffs and the one-sentence rule fail on these records, and the next agent copies the form.
Fix: take it in any rebuild; otherwise leave it and note it in the ledger, since replacing 19 decisions for line breaks costs more than it saves.

**M5. Some reasons in decision reasoning are the coordinator's, presented among the spec's.**
Handle: d-4032xv ("because those are the states a reader can rely on"), d-1x1mgv ("because the baseline shows few entries say what they replace"; "lets the writer act on it before publishing"), d-c08bdw ("Level 1 first keeps reads cheap"; "so the reader can judge whether it is current"), d-z57dy1 ("so that it costs nothing to ordinary reads"), d-zq5sfb ("so there is nothing to keep in step"); none is in the spec, and plan:32 asks for the spec's own reasons; `task-2-report.md:168` says the reasons are the spec's.
Failure: a later reader takes an agent's inference as the design's stated reason.
Fix: mark each as the coordinator's reading in a rebuild, or drop it.

**M6. The spec author's calls are marked in some decisions and not in others.**
Handle: spec:5 marks **[my call]** choices "for her to check"; d-cg3nn3, d-1x1mgv, d-92t2m8, d-s6mq0f, d-jxwj8m, and d-bz7bav name "the specification author's call", while d-zerbz9 (identifiers, spec:116; one-way links, spec:119), d-6cyjdh (newest first and the file not moving, spec:89-90), d-mzkt6e (the review flag, spec:171), d-4032xv (the same change, spec:166), d-c08bdw (rendered on demand, the guide, spec:185, 188), and d-a3e8kb (layout, Markdown with YAML, settings location, spec:206, 215-216) do not; `task-2-report.md:188` says the marker is carried "where it matters".
Failure: under SPEC-1 the author cannot tell from the records which entries she agreed in the brainstorm and which she approved only as part of the document.
Fix: name the call in each rebuilt decision, or list the unmarked ones in the SPEC-1 question.

**M7. LODGE-4 is not cited where the spec cites it, while the other codes are.**
Handle: spec:70 and spec:75 cite LODGE-4; s-9n7han, s-fk3yzy, d-jj72ps, and d-zq5sfb name neither LODGE-4 nor d-y8p15p, although d-zq5sfb's reasoning describes that decision; s-q10vh5 (LODGE-7), s-hjf8cc (LODGE-1), s-nzhyh3 (LODGE-5) keep theirs; `task-2-report.md:173` says d-zq5sfb carries LODGE-4.
Failure: `lodge search LODGE-4` finds d-y8p15p but no entry or decision built on it.
Fix: add "(LODGE-4)" in the I5 edit decision to s-9n7han and s-fk3yzy.

**M8. Figures written in words carry no handle.**
Handle: s-dffw9n and d-fkndvh ("over a hundred files"), d-5mhgpp ("tens of thousands of characters"); spec:238 and spec:18 hold them; the feedback only catches digits.
Failure: a figure about the first user stands unhandled, contrary to plan:24.
Fix: add `numbers` with the spec line in any rebuilt decision.

**M9. Some entries do not read alone, or state a dated observation as timeless.**
Handle: s-dm37qr ("the filters above"), s-x84e3h ("This build", which reads as whatever build is current), s-edgt71 ("the two states"), s-zv83s7 ("there the gate runs before every push to `lodge`", which reads as the work-branch case, copied from spec:167); s-qkcp0s ("A cloud session image has Python 3.13") states a 2026-10-29 observation as a standing fact; d-jj72ps and s-7m3smc say "the user", which reads as "the first user", for the author (done ledger line 221 says "the author's authorisation").
Failure: a reader of one entry through `lodge show` cannot resolve the reference or reads it wrongly.
Fix: in the I5 edit decision, name the referent ("the filters of s-3n0ndk", "lodge 0.1.0", "the published state and the state about to be published", "in the first user, the gate runs before every push to `lodge`", "on 2026-10-29 the image had").

**M10. Some decision titles describe the bookkeeping, others the design.**
Handle: d-5mhgpp, d-cg3nn3, d-f84m43, and d-zh00c5 end in "are specification entries", "is recorded as specification entries", "are entries", or "are recorded as entries"; the other 20 state the design ("Records are Markdown files in git…").
Failure: a search on a design word ranks the meta titles lower, and the four read as decisions about lodge's records, not about lodge.
Fix: in any rebuild, state the content, for example "lodge's intent, goals, and success measures".

**M11. The report's handles do not resolve.**
Handle: `task-2-report.md:190` names "s-layout", which does not exist (the entry is s-evv024); `task-2-report.md:168-181` names decisions by draft slugs ("purpose-goals", "storage-files") instead of IDs.
Failure: a reviewer checking the reasons-to-decisions map must guess which ID each slug became.
Fix: replace the slugs with the IDs from `task-2-report.md:11-143`.

### Checked and clean

- Coverage: every spec section from line 8 to line 304 was read against `lodge spec`; apart from the findings above, each claim is in an entry or, for reasons, in a decision's reasoning, and the report's table matches (spot-checked every row; the "Her decisions" and "Left to the builder" omissions follow plan:74).
- Task 14: s-qkcp0s and s-7m3smc state what holds after done ledger line 221, and d-jj72ps's reasoning cites that line, as plan:34 asks.
- LODGE-9 and LODGE-10: s-edgt71 and s-ms14fq state them; no entry keeps the pre-LODGE-9 "checks 4 to 6 only at the gate".
- Task 1: 28 author records, each with reasoning equal to its quote (all seven new ones read; the 21 earlier ones at level 1); imports carry `imported` and `imported from: … line N`; `.lodge.toml` `[import] sources` names the done ledger; d-3tq6cx, d-axaz9w, and d-fw070q say no more than their quotes and ledger lines 4, 217, and 220 settle.
- Public repository: `git diff 0b52da3..8d24943 -- lodge` holds no `/home/`, `~/`, user or machine name, or project name of the first user; `Kiibou-chan` appears only in the install URL, which the final review judged the public identity (`final-review-design.md:106`).
- `uv run lodge check`: ok; `lodge spec` shows no `awaiting`, `fails check`, or `problem:`.

## Pass 2: practice

- Entries: all within 150 words; one sentence per line in the rendered entries; no em-dash or en-dash (`grep` over `lodge spec` and all 24 decisions); British spelling ("licence", "behaviour", "authorise"); Oxford commas present in every list of three or more checked.
- Decisions: statements within 80 words and three sentences, reasoning far under 1,000 words (the longest, d-5mhgpp, about 300); line breaks in statements are M4.
- Number handles: Python 3.13, the four length figures, 300 lines, Python 3.12, 2011, and 2017 each carry the spec line; labels (Level 1, LODGE-n, line 221) carry none, as plan:24 asks; words-only figures are M8.
- Titles: all within 100 characters; the wrong title is I8, the meta titles M10.

## Pass 3: design

**Granularity.**
82 entries in ten areas suits `lodge show` and `lodge search`: the count exceeds the plan's 40 to 70 (plan:75) mainly because the spec's own enumerations became one entry each (seven checks, the must-nots, the packages), which is what a reader looks up alone, for example the check a `lodge check` message names.
Merging them would make search return a paragraph where one sentence answers; the cost of the split is only real where a claim is repeated (M3) or an entry loses its label (I9).
Search noise comes less from the entry count than from the decisions: each statement restates its entries' content (d-x42f0x's statement is s-dm37qr's first two sentences), so `lodge search "viewer read-only"` returns 49 records, entry and decision side by side with near-identical text.
That is not a finding against this task, since the plan set no form for the statements, but a later agent deciding how to word the statement of a decision that moves content should state the move and the entries, not their text.

**Her reading, if she confirms these under SPEC-1.**
The entries in `lodge spec` run to 4,526 words (`wc -w`), against 4,312 for the design document she approved (`wc -w docs/superpowers/specs/2026-10-29-lodge-design.md`); the 24 decisions add 4,814 words, mostly the spec's reasons and paraphrases of her own words (I4).
Confirming through `confirms` on 24 decision IDs invites reading both, about twice the document she already approved.
`lodge spec` renders areas alphabetically (`src/lodge/core/render.py:27`, already in the ledger), so Constraints comes first and Purpose fourth, which is a poor order for a first read.
Proposal for the SPEC-1 revision of Task 3: ask her to read `lodge spec` alone, after the I3 to I9 edits, and confirm the 24 decisions in one author decision; the decisions' reasoning need not be read, since it restates the frozen design document, and I4's fix gives each of her views a pointer to her own record.

**Entries whose last change is a coordinator decision.**
No entry is flagged now, because no entry's last change is an author decision (s-01k42c); until SPEC-1 is answered, an agent can edit any of the 82 without a flag, which is the exposure SPEC-1 already names.
LODGE-6 (d-8nkamy) makes a confirmed decision count as hers, so one confirming author decision closes it for all 82, with no structural change.

## Files read

Read: `CLAUDE.md`; `.claude/agents/reviewer.md`; the plan `docs/superpowers/plans/2026-10-30-lodge-on-itself.md`; its ledger `docs/superpowers/plans/2026-10-30-lodge-on-itself-progress.md` (working-tree version, with the uncommitted Task 2 line); `docs/superpowers/plans/2026-10-30-lodge-on-itself/task-2-report.md`; the spec `docs/superpowers/specs/2026-10-29-lodge-design.md`; done ledger lines 4, 177 to 222 of `docs/superpowers/plans/done/2026-10-29-lodge-progress.md`; `docs/superpowers/plans/done/2026-10-29-lodge/final-review-design.md:95-110`; `src/lodge/core/drafts.py:55-98` (date rule); `src/lodge/core/check_change.py:40`; `.lodge.toml`; the records through lodge as listed at the top.
Not read: `plan-review.md`; the record files directly (by instruction); the rest of `src/` and `tests/`; `scripts/check.sh` was not run (the gate's last step, `lodge check`, was run and is ok).
