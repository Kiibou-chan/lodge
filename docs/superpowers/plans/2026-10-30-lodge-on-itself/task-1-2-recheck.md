# Recheck of fix round 1 for Tasks 1 and 2: lodge on itself

Range 892171f..54916ae on `lodge-on-itself` (fix 54916ae, ledger 2603f9e).
Rechecker: one pass, read-only; records read through lodge (`uv run lodge show REF --reasoning --provenance`, `lodge spec`, `lodge search`), the diff with `git diff 892171f..54916ae -- lodge/`, the spec read for markers.
No probe worktree was needed.
Gate: `sh scripts/check.sh` exit 0 (1071 passed, `ok`).

Counts: findings of the review 19 closed, 1 partly closed (M9); new findings 0 Blocking, 1 Important, 5 Minor.

## Review findings

- **I1 closed.** `uv run lodge search --by author` lists d-fw070q, d-axaz9w, d-qbfdqt (22:47), d-z8jm5y (22:46), then the rest, all dated 2026-10-29; the four show `imported from: ...-progress.md, line N` with N = 211, 215, 214, 210, which are the ledger lines that hold them (`sed -n 205,222p` of the done ledger: 210 "Remove them completely", 211 the LODGE-8 ruling, 214 LODGE-10, 215 LODGE-9).
- **I2 closed.** d-gqyp3n names finding D13 and its set (`final-review-design.md:99-102`); "from the history as well" is backed by done ledger line 210 (history squashed and recreated on her "Remove them completely").
- **I3 closed.** s-ph9z0t and d-5mhgpp say "very important (d-9k0dfe)"; d-9k0dfe's quote is "4 is very important".
- **I4 closed as written, with a defect in the pointers it added: see N1.** The grading verbs ("prefers", "judged", "clearest", "weighted most") are gone from all six decisions (grep of the coordinator decisions for `prefer|likes|judged|doubt|clearest|weighted|wanted|framing`: none); the contradictory "a thousand or more" is gone.
- **I5 closed.** s-rx9d11 is the spec's goal 4; s-rger6n, s-bzatqh, s-a4jfp1, s-07ar34, s-7ah5n7 no longer restate her quotes (a five-word overlap scan of every coordinator record against all author quotes finds only "and design principles are applied" in s-dffw9n, unchanged by this round).
- **I6 closed.** s-m83kjq: "is meant to let ... the pilot measures it (s-3ht96p)".
- **I7 closed.** s-hfjr1m ends "A failing check still refuses the add (s-edgt71)"; d-1x1mgv title and statement say advice without refusing.
- **I8 closed.** s-zv83s7 title names the published state and the one about to be published.
- **I9 closed.** Titles "Check 1:" to "Check 7:" match spec:157-164 and s-j70a0k's order; `lodge search "check 5"` now ranks s-ms14fq first; s-edgt71 names checks 4, 5, and 6.
- **M1, M2 closed.** d-9vxkjw and d-qbfdqt statements as the review proposed.
- **M3 closed.** s-7ah5n7 lost the second-project clause, s-j5ttw1 the read-only sentence, s-582qav points at s-dm37qr.
- **M4 closed.** A script over all 24 area decisions and all entries finds no line holding two sentences in a statement or entry, and no dash.
- **M5 closed.** The quoted inferences are gone from d-4032xv, d-c08bdw, d-z57dy1, d-zq5sfb, d-1x1mgv, d-5mhgpp.
- **M6 closed** with one over-claim, N2.
- **M7 closed.** (LODGE-4) is on s-9n7han and s-fk3yzy; d-jj72ps and d-zq5sfb cite d-y8p15p.
- **M8 closed.** `numbers` handles on d-5mhgpp (spec:18) and d-fkndvh (spec:238); both lines hold the phrases.
- **M9 partly closed.** s-dm37qr, s-x84e3h, s-edgt71, s-zv83s7, s-7m3smc are fixed; d-jj72ps's statement still reads "with the user's authorisation in the spawning prompt" (`lodge show d-jj72ps`, line 2 of the statement), where the review named the same phrase.
  Failure: "the user" reads as the first user in a record whose subject is the first user; done ledger line 221 says the author's authorisation.
  Fix: a statement of "the author's authorisation" (the decision is unpublished, so an in-place edit is allowed as in this round).
- **M10, M11 closed.** Titles of d-5mhgpp, d-cg3nn3, d-f84m43, d-zh00c5 state content (all under 100 characters); the report holds no `s-layout` or draft slug (`grep` finds only the M11 row itself).

## New findings

### Important

**N1. Pointers added by the fix lead to author records that do not hold the words they are cited for.**
Handles:
- d-5mhgpp reasoning: "The author's words on short, searchable decisions with the full reasoning as a further step are in d-n30kqr, and on tooling that constrains how knowledge is worked with in d-c6n1ng".
  d-n30kqr's quote is "A few hundred to maybe thousand(s) at most" (the size of the reasoning); d-c6n1ng's quote is on hard character limits and guardrails.
  The words in question are spec:21-22 ("decisions need to be searchable and short ...", "having actual tooling for this ..."), which no author record holds (`uv run lodge search "searchable" --by author`: no matches; the report says so itself, task-2-report.md "Left out", fourth bullet).
- d-f84m43 reasoning "The three must-nots are the author's decision d-9k0dfe", and d-mzkt6e and d-s6mq0f citing d-9k0dfe for the must-not: d-9k0dfe's quote is "4 is very important", which settles the measure; her must-not words (spec:55, "The tool showing wrong information would definitely be one. But yes, all of the above would not be great.") are in no author record, and d-9k0dfe's statement ("lodge must not show wrong information, let an agent quietly rewrite ...") says more than its quote settled (a Task 1 record, now relied on by three decisions).
- d-cg3nn3 reasoning "the author's remarks on languages are in d-7v4crf": d-7v4crf's quote is "easily accessible (so python might make sense?)"; her Kotlin remark (spec:280) is in no author record.
- d-18terz "her words are in d-n30kqr" for the three levels: the quote is only the size.

Failure: this round's I4 fix exists so that a reader reaches her actual words from a decision; an agent following d-5mhgpp to d-n30kqr or d-f84m43 to d-9k0dfe finds a quote that does not say it, and either concludes the claim is hers on the pointer's word or that the pointer is wrong.
LODGE-8 (d-9vxkjw) makes any text but a quote the agent's, so the pointers present an agent's attribution as hers.
Fix: either add the missing author records through `lodge add --import` from their source (the brainstorm lines at spec:21-22, 55, 280 are the evidence; the author decides whether they are decisions), or reword each pointer to the spec line (`docs/superpowers/specs/2026-10-29-lodge-design.md:21-22`, `:55`, `:280`) and drop "author's decision" for those; and narrow d-9k0dfe's role to the measure its quote settles.

### Minor

**N2. d-4032xv says the spec marks the choice of published state as the specification author's call; it does not.**
Handle: d-4032xv reasoning "'The same change' as the difference between two states, and the choice of published state, are the specification author's calls, marked in the design document"; spec:166 marks "The same change" **[my call]**, spec:167 (the published state) carries no marker.
Failure: SPEC-1 reads the claim as the list of what she must check and misses that the published-state definition was not flagged to her.
Fix: "'The same change' ... is the specification author's call, marked in the design document; the definition of the published state in the next line is not marked."

**N3. s-qkcp0s mixes a dated past with timeless present.**
Handle: `lodge show s-qkcp0s`: "On 2026-10-29 a cloud session image had Python 3.13 and uv, api.github.com and pypi.org answer, and git traffic goes through a session proxy ...".
Failure: the first verb is dated and the next two read as standing facts again, so the dating (the point of the M9 fix) covers only the first clause.
Fix: "On 2026-10-29 a cloud session image had Python 3.13 and uv, api.github.com and pypi.org answered, and git traffic went through ...".

**N4. Decisions refer to others by position, which an ID-ordered reader cannot resolve.**
Handles: d-18terz "the next decision's guidance" (it means d-92t2m8), d-1x1mgv "as the next decisions describe", d-cg3nn3 "(see the rollout area)".
Failure: `lodge show` of one record has no "next"; a reader cannot find the target.
Fix: cite d-92t2m8, d-4032xv and d-qbfdqt, and s-hh97bm, by ID.

**N5. The report's "Left out" section still says the quotes are paraphrased in reasoning.**
Handle: `task-2-report.md`, "Left out, with reasons", fourth bullet ("paraphrased in reasoning where a reason depends on them"), against the Fix round 1 section, which says reasons cite her decisions by ID instead.
Failure: a later reader of the report takes the stale line as the method.
Fix: rewrite that bullet in place to "cited by decision ID, not restated" (no appended note).

**N6. s-7ah5n7 no longer carries the spec's "evaluated first" claim, and no entry does.**
Handle: spec:46-47 (other kinds of knowledge "would have to be evaluated (first on the past and then in a pilot)"; the to-do list integrated "later"); after the fix only d-cg3nn3's reasoning holds them (`grep -rn -i "evaluated" lodge/spec`: only the rollout step).
Failure: `lodge spec` shows "out of scope for now" with no condition for leaving scope; the review asked for the phrasing to be dropped, not the claim.
Fix: s-7ah5n7 states "Other kinds of knowledge are evaluated first on the past and then in a pilot before they come into scope."

## Checked and clean

- Public repository: the fix diff holds no `/home/`, `~/`, user name, or machine name.
- Dashes: none in any record; Oxford commas and British spelling in the added text.
- Decisions are not contradicted: s-hfjr1m and d-1x1mgv agree with s-edgt71 and LODGE-9 (`d-qbfdqt`); s-edgt71 and s-zv83s7 agree with spec:166-168; s-7m3smc and s-qkcp0s agree with done ledger line 221 and Task 14; no entry says a failing check does not refuse the add.
- Author records: 28, each reasoning equal to its quote (the four imports show the quote as the reasoning); no statement of the four re-dated records says more than its quote and ledger line (d-gqyp3n reads the D13 set, and its title says so).
- Markers named in the added reasoning (M6) match the spec at spec:89-90, 111, 116, 119, 171, 185, 188, 206, 215-216, except N2.
- `uv run lodge check` ok inside the gate; `lodge spec` shows no `awaiting`, `fails check`, or `problem:`.
