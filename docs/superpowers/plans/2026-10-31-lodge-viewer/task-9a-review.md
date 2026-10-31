# Task 9a review

Commit e498dbe, read in a detached worktree at that commit (removed after).
The coordinator's working tree already carried uncommitted Task 8 fix work, so every command below ran on the commit itself.
Counts: 0 Blocking, 1 Important, 4 Minor.

## Checks as asked

1. Author decisions d-9dqycj, d-g7xvwm, d-s64jyh, d-1bnqj5, d-cvtrj6, d-rnjh2s:
   - each quote text occurs verbatim between quotation marks in design lines 13 to 18 (scripted `grep -F` against the design, 6 of 6);
   - `when` equals the brief's value for each, `where` is "lodge build session", `decided_by` is `author`, `scope` is `product`;
   - reasoning equals the quote text and nothing else, in all six (`lodge show --reasoning --provenance`);
   - none repeats d-dyrpc6 (line 12) or d-2hcgav (line 19), and none replaces or narrows an author decision.
2. Coordinator decisions d-3d4g9j and d-s69cq4 and their 22 entries say what the design says: I1 below is the one place a record claims more than the design supports.
   Each design claim from lines 26 to 73 has an entry (s-648y95 to s-j9jc4y), none over 150 words, and areas follow the brief's topic rule.
   Nothing reads as hers except the quotes: the entries say "her words" or "the author's words" only of the quote and reasoning.
   The old entries that still contradict the new ones (s-dm37qr, s-582qav, s-nzhyh3 read-only; s-wcv4en level 1; s-0yzshh actions; s-edgt71 "seven") are all on the brief's 9b and 9c lists, so none is a 9a finding.
3. Prose: no em-dash, no American spelling, no line holding two sentences, no missing Oxford comma in any added file (the one `--only` hit is a git flag).
4. In the detached worktree: `lodge check` prints `ok`; `lodge waiting` prints `nothing` for both groups; `lodge spec | grep -c 'changed since'` prints 0, as the report says.

## Important

### I1. d-s69cq4 narrows d-mzkt6e though no statement of d-mzkt6e is made false, and the mark lands on three unrelated entries

- Records: d-s69cq4 (`narrows: d-mzkt6e`), d-mzkt6e, s-0s9m2d, s-dfejrb, s-j5ttw1.
- The brief limits narrowing to "the coordinator decisions whose statements it makes false".
  d-mzkt6e's statement (the review flag is derived, shown at level 1, cleared by an author decision) stays true, and d-s69cq4's own reasoning says so ("not in its review-flag rule").
- What changed is only a sentence in s-j5ttw1, and the edit of s-j5ttw1 already records that.
- Handle: `lodge spec` now prints `The review flag is derived and clears on confirmation (s-0s9m2d · its decision narrowed by d-s69cq4)` and the same mark on s-dfejrb.
  A reader of the specification is told the review-flag rule was narrowed by the Confirming decision, which is the opposite of what the reasoning says and of LODGE-6 (d-8nkamy).
- Failure scenario: she reads the specification to confirm, sees the review-flag entries marked narrowed by a confirmation decision, and doubts whether confirming still clears the flag.
- Fix: a published decision cannot be edited, so the mark can only be accepted or removed by a decision with `replaces: [d-s69cq4]`, which is disproportionate.
  Recommended: a ruling in the ledger accepting it, with the cost named (three headings carry a "narrowed" mark whose real scope is one sentence of s-j5ttw1), and no narrowing of a decision whose statement stays true in 9b and 9c.

## Minor

### m1. s-bdkjte was edited to defeat a grep, and the edit sits in the Confirming decision

- Records: s-bdkjte, d-3d4g9j (created it), d-s69cq4 (edited it).
- d-s69cq4's reasoning gives the reason: "avoiding a bare warning phrase in ordinary prose".
  The phrase "changed since" is also the read's own mark (design line 111), so the 9b entries that describe that mark will contain it again, and the brief's literal `grep -c 'changed since'` will stop meaning "no warning".
- The edit also makes a Confirming decision the last change of a Goals entry, with no design line of the Confirming section behind it.
- Fix: in 9b and 9c, count warnings with an anchored pattern, for example `grep -c 'rests on s-[a-z0-9]*, changed since)'` on headings, `lodge spec | grep -c ', changed since)'`, and say so in the brief.
  The new wording itself is accurate to design line 111 and can stay.

### m2. d-3d4g9j's reasoning calls the implementation "approved"

- Record: d-3d4g9j, reasoning line 1 ("The approved implementation now provides ...").
- The design still says "Status: not approved" (line 3), and no record or ledger line shows her approving it.
- A coordinator record saying "approved" can read as her sign-off.
- Fix: nothing can be edited; write "built" in later reasoning, and do not carry the word into 9b and 9c.

### m3. d-3d4g9j and the s-hfjr1m reaffirmation do not say the old mark was a tie artefact

- Records: d-3d4g9j (`edit` s-hfjr1m), `task-8-review.md` I1.
- The reasoning says "the change to s-edgt71 does not alter the distinction between advisory feedback and a failing check".
  Task 8's review shows the mark came from two decisions with the same timestamp, ordered by random ID, so no change to s-edgt71 happened after s-hfjr1m was written.
- The result is right (option (b) of that finding) but the stated reason is not the true one.
- Fix: none to the record; if the coordinator's tie-break fix lands, 9b's reasoning should not repeat "changed" for this pair.

### m4. Some statements of the author decisions harden "would be nice" and carry context that is not in the quote

- Records: d-9dqycj ("is raised and answered on that entry", from "A chat on it would be ideal"), d-g7xvwm ("are ordered or arranged", from "would be nice"), d-1bnqj5 and d-cvtrj6 (the subject, a point resting on a wrong one, comes from the question before the quote, which the quote does not contain).
- The wording is the brief's, so this is not the builder's fault; under LODGE-8 (d-9vxkjw) only the quote is hers, and the statement is agent text under her label.
- Failure scenario: a later reader takes "are ordered or arranged" as a requirement she set, where she said it would be nice.
- Fix: none now; at the author's check, offer her the choice to soften d-9dqycj and d-g7xvwm by a decision of hers.

## Read and not read

Read through lodge: all 36 records of the commit (`lodge show` with `--reasoning` and `--provenance` for the decisions), d-dyrpc6, d-2hcgav, d-9vxkjw, d-8nkamy, d-cg3nn3, d-mzkt6e, d-7w5aq0, and the entries they link; `lodge spec`, `lodge search --by author`, `lodge check`, `lodge waiting`.
Read as files: the brief, the report, the Codex final text, the design lines 1 to 141, `task-8-review.md`, the commit's `git show` of `s-j5ttw1` and the `_area.md` files.
Source greps (only to test "what holds now"): confirmation, thread, and commit code in `src/lodge/{core,app,gitstore,viewer}`; I did not run the test suite, and I did not check the viewer's pages in a browser.
Not read: the plan outside the lines cited, the advisor ruling file, the records of Tasks 1 to 8 beyond those named.
