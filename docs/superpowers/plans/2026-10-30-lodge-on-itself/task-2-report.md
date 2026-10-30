# Task 2 report: the specification in lodge

Status: done. Records added through `lodge add`, one add per area, drafts under `.drafts/t2/` (git-ignored).

Counts: 10 areas, 82 entries, 24 decisions (all `decided_by: coordinator`, `scope: product`, each listing its entries with `create`).

## Decisions and entries added

### Area `purpose`: Purpose

- Decision d-5mhgpp: lodge's intent, goals, and success measures
  - s-kcvh60: lodge is a knowledge tool for agent-built software
  - s-m83kjq: Decisions and entries are short, searchable, and layered
  - s-xx4pk4: Agents write knowledge in one defined way
  - s-rx9d11: lodge replaces the first user's decision, ruling, and specification files
  - s-3ht96p: Cost and speed measures for the pilot
  - s-ph9z0t: Correctness and use measures for the pilot
- Decision d-cg3nn3: lodge's non-goals for now: no server, no MCP server, limited scope, soft limits, read-only viewer
  - s-07ar34: No server and no MCP server for now
  - s-7ah5n7: Kinds of knowledge and projects outside the scope
  - s-rger6n: Length limits are soft guidance, not hard limits
  - s-582qav: The viewer does not edit
- Decision d-f84m43: lodge's three must-nots and how the design answers each
  - s-q4s548: lodge must not show wrong information
  - s-pncjp8: An agent must not quietly rewrite the author's decision
  - s-4ykcm0: lodge must not become a costly third copy

### Area `constraints`: Constraints

- Decision d-jj72ps: lodge runs as a command-line tool installed from a public tag in each session
  - s-az7rg4: lodge is a command-line tool for cloud sessions
  - s-9n7han: Every session installs lodge from a tag of its public repository
  - s-qkcp0s: A cloud session can install lodge from the public tag
  - s-7m3smc: Auto mode needs the install authorised
- Decision d-zq5sfb: lodge is public, Python, file-based, and follows the author's prose rules
  - s-fk3yzy: lodge is public from the first commit
  - s-a4jfp1: lodge is written in Python
  - s-j8tp0n: Files in git are the only source of truth
  - s-t9z0at: Record prose follows the author's writing rules

### Area `model`: The model

- Decision d-6cyjdh: A specification entry says what holds now and has no reasoning of its own
  - s-a67fqm: A specification entry says what holds now
  - s-q10vh5: An entry is current or retired, derived from decisions
- Decision d-z57dy1: A decision records a change, with fields for who, what, and the evidence
  - s-s3z6ea: A decision records a change, with a scope
  - s-aq3a5k: A decision names who decided, when, and the work item
  - s-0yzshh: A decision lists the entries it changes and the decisions it supersedes
  - s-f859z1: A decision carries number handles, attachments, and an import source
  - s-fmwe04: A decision is current or replaced, derived from later decisions
- Decision d-zerbz9: IDs are minted without coordination, and links are stored one way
  - s-fdzcr2: IDs are minted without coordination, and records may carry a code
  - s-8f6scf: Links are stored one way and shown both ways

### Area `levels`: Levels

- Decision d-18terz: Knowledge is read at three levels, and provenance is exact only where it must be
  - s-wcv4en: Knowledge is read at three levels
  - s-bzatqh: Provenance is exact only where it must be
- Decision d-92t2m8: Length guidance is soft, per level, and tuned in the pilot
  - s-fehz74: Length guidance per level

### Area `writing`: Writing, feedback, and the check

- Decision d-1x1mgv: Writes go through lodge, and feedback advises without refusing
  - s-8m99ba: Writes go through lodge, and a decision brings its entries
  - s-bjhnwg: Agents draft records as Markdown with a header
  - s-hfjr1m: Write feedback advises and does not refuse
  - s-aagqv8: A decision that changes nothing is asked about related decisions
- Decision d-3epcjd: The check has seven checks and gates publication
  - s-j70a0k: The check gates publication with seven checks
  - s-qzk2yb: Check 1: a header that cannot be read fails
  - s-g2jwha: Check 2: an unresolved or shared ID fails
  - s-yhppm5: Check 3: an author decision without a quote fails
  - s-kvwrqw: Check 4: an entry change without a decision fails
  - s-ms14fq: Check 5: changing an existing decision fails
  - s-aw5a1j: Check 6: a new link to a superseded record fails
  - s-s27z33: Check 7: an entry out of its area's order fails
- Decision d-4032xv: The checks compare the last published state with the state about to be published
  - s-zv83s7: The same change is the gap between the published state and the one about to be published
  - s-edgt71: Reads run every check; only the gate and add refuse
- Decision d-mzkt6e: An agent change to what the author decided raises a derived review flag
  - s-01k42c: An agent change to the author's text raises a review flag
  - s-0s9m2d: The review flag is derived and clears on confirmation
  - s-dfejrb: A flagged agent decision takes effect at once
  - s-j5ttw1: lodge trusts the author label and shows its quote

### Area `reading`: Reading and the viewer

- Decision d-c08bdw: Reads return Level 1 first, and the specification is rendered on demand
  - s-3n0ndk: Search and show give Level 1 first
  - s-v022r0: The readable specification is rendered on demand
  - s-wz17sv: Reads state how fresh their data is
  - s-7f10zc: Agents learn the rules from a guide lodge prints
- Decision d-x42f0x: The viewer is a local, read-only web page on the same parser as the command line
  - s-dm37qr: The viewer is local and read-only
  - s-gg9chm: The viewer cannot disagree with the gate

### Area `hook`: A hook against writing elsewhere

- Decision d-s6mq0f: lodge ships a hook that gives feedback on hand edits
  - s-4nq741: A hook warns against writing elsewhere
  - s-h12s8w: The hook gives feedback and does not block

### Area `storage`: Storage

- Decision d-a3e8kb: Records are Markdown files in git, with settings outside the data
  - s-z1zvb4: Records are Markdown files in git behind one interface
  - s-evv024: Where record files live in a project
  - s-r1eh11: Settings live in .lodge.toml, outside the data
- Decision d-knqtc2: The git adapter reads a checkout or a branch, and the first user's records live on a branch
  - s-6bc10p: The git adapter reads a checkout or a branch
  - s-hjf8cc: The first user keeps records on a branch that never merges
  - s-sgprxs: A specification change names the work branch in work_item

### Area `structure`: Structure

- Decision d-fkndvh: lodge is built in layers with one dependency direction
  - s-dffw9n: Design principles are enforced from the first commit
  - s-t9zd7a: core is pure
  - s-q23m04: app holds the operations and their ports
  - s-nzhyh3: Adapters and the composition root
  - s-ctywm6: Imports run one way, through front doors
- Decision d-jxwj8m: Tests and tools enforce the structure from the first commit
  - s-165qfh: A structure test enforces the import and size rules
  - s-3xka4c: Static analysis is strict and pinned
  - s-20ev8v: Development is test-first, with end-to-end tests per command
  - s-v1sb0j: The environment is reproducible with uv
- Decision d-n7whwk: Plans are reviewed before building, and each task gets two maintainability views
  - s-e55e3t: Plans are reviewed, and each task gets a maintainability review

### Area `rollout`: Rollout and open questions

- Decision d-bz7bav: lodge is rolled out in five steps, evaluated on the first user's past before a pilot
  - s-5gmxyx: The rollout runs in five steps
  - s-awc4kb: Evaluation happens on the first user's past in a scratch copy
  - s-x84e3h: The build provides only what the importer needs
  - s-t7qz74: Measurement uses existing transcripts and cost logs
- Decision d-zh00c5: Open questions: the licence, a second project, and the length guidance values
  - s-38w757: Open: the licence
  - s-hh97bm: Open: whether a second project adopts lodge
  - s-yrz8fz: Open: the length guidance values

`lodge spec` renders the areas in alphabetical order (`src/lodge/core/render.py:27`, `names = sorted(...)`), not in the plan's order; entries within an area follow the area's `order`.

## Coverage: spec section to entries and decisions

| Spec section (lines) | Entries holding it | Decisions carrying its reasons |
|---|---|---|
| Intent (8-22) | s-kcvh60 (8-12) | d-5mhgpp |
| Goals (24-39) | s-m83kjq (24-28); s-xx4pk4 (24-27); s-rx9d11 (24-30); s-3ht96p (32-39); s-ph9z0t (32-39) | d-5mhgpp |
| Non-goals for now (41-51) | s-07ar34 (41-44); s-7ah5n7 (41-51); s-rger6n (41-49); s-582qav (41-50) | d-cg3nn3 |
| Must nots (53-65) | s-q4s548 (53-63); s-pncjp8 (53-64); s-4ykcm0 (53-65) | d-f84m43 |
| Constraints (67-81) | s-az7rg4 (69); s-9n7han (70-71); s-qkcp0s (72-74); s-7m3smc (81); s-fk3yzy (75); s-a4jfp1 (76); s-j8tp0n (77-79); s-t9z0at (80) | d-jj72ps; d-zq5sfb |
| The model (83-120) | s-a67fqm (83-89); s-q10vh5 (90-91); s-s3z6ea (93-98, 114); s-aq3a5k (98-99, 103-104, 108); s-0yzshh (100-102); s-f859z1 (105-107); s-fmwe04 (110-113); s-fdzcr2 (116-117); s-8f6scf (119-120) | d-6cyjdh; d-z57dy1; d-zerbz9 |
| Levels (122-140) | s-wcv4en (122-126); s-bzatqh (128-129); s-fehz74 (131-138) | d-18terz; d-92t2m8 |
| Writing, and feedback on writes, and the check (142-178) | s-8m99ba (144-145); s-bjhnwg (146); s-hfjr1m (148-153); s-aagqv8 (151); s-j70a0k (155); s-qzk2yb (158); s-g2jwha (159); s-yhppm5 (160); s-kvwrqw (161); s-ms14fq (162); s-aw5a1j (163); s-s27z33 (164); s-zv83s7 (166-167); s-edgt71 (168-169); s-01k42c (171-172); s-0s9m2d (173-175); s-dfejrb (176-177); s-j5ttw1 (178) | d-1x1mgv; d-3epcjd; d-4032xv; d-mzkt6e |
| Reading (180-188) | s-3n0ndk (182-183); s-v022r0 (184-185); s-wz17sv (186); s-7f10zc (188) | d-c08bdw |
| The viewer (190-194) | s-dm37qr (192-193); s-gg9chm (194) | d-x42f0x |
| A hook against writing elsewhere (196-201) | s-4nq741 (196-199); s-h12s8w (200-201) | d-s6mq0f |
| Storage (203-220) | s-z1zvb4 (205, 216); s-evv024 (206-213); s-r1eh11 (215); s-6bc10p (218); s-hjf8cc (219); s-sgprxs (220) | d-a3e8kb; d-knqtc2 |
| Rollout (222-233) | s-5gmxyx (222-233); s-awc4kb (226-228); s-x84e3h (229-230); s-t7qz74 (231) | d-bz7bav |
| Structure (235-272) | s-dffw9n (235-239); s-t9zd7a (241-244, 257); s-q23m04 (245-246); s-nzhyh3 (247-252, 292); s-ctywm6 (241, 255-256); s-165qfh (261); s-3xka4c (262-264); s-20ev8v (266-267); s-v1sb0j (269-270); s-e55e3t (272) | d-fkndvh; d-jxwj8m; d-n7whwk |
| Her decisions, as she made them (274-298) | none: her quotes stay author decisions (Task 1 and earlier records, LODGE-1 to LODGE-10 and the rest); their gist is restated in the entries above where it settles a design point | the area decisions cite her rulings by code (LODGE-1, 2, 5, 6, 7, 9, 10) in their reasoning |
| Open (300-304) | s-38w757 (302); s-hh97bm (303); s-yrz8fz (304) | d-zh00c5 |

Reasons carried, by decision (the spec's own reasons; where a reason depends on her words, the reasoning cites her decision by ID instead of paraphrasing her):
- d-5mhgpp: Why now (spec:14-19), her framing (21-22), replace-not-sit-beside (29), the success baselines (34-39), the measure the author called very important, cited as d-9k0dfe (38, 198).
- d-cg3nn3: server and Kotlin (43), no MCP (44), kinds of knowledge (46), to-do (47), hard limits (49), viewer read-only as the spec author's call (50), second project (51).
- d-f84m43: spec:55-65, the three answers.
- d-jj72ps: spec:70-74 and spec:81 as settled by the cloud check, done ledger line 221.
- d-zq5sfb: spec:75-80 with LODGE-4 (spec:293).
- d-6cyjdh, d-z57dy1, d-zerbz9: spec:83-120, including why no stored status (spec:111) and why links are stored one way (spec:119-120).
- d-18terz, d-92t2m8: spec:125-129 and spec:131-140 (for scale, spec:140).
- d-1x1mgv, d-3epcjd, d-4032xv, d-mzkt6e: spec:142-178 with LODGE-2, 6, 7, 9, 10.
- d-c08bdw, d-x42f0x: spec:180-194.
- d-s6mq0f: spec:196-201.
- d-a3e8kb, d-knqtc2: spec:203-220 with LODGE-1.
- d-fkndvh, d-jxwj8m, d-n7whwk: spec:235-272 with LODGE-5.
- d-bz7bav, d-zh00c5: spec:222-233 and spec:300-304.

## Left out, with reasons

- "Left to the builder" (spec:306-313): not entries, per the plan.
- The status and provenance header (spec:3-6) and the implementation plan pointer: document metadata, not claims about lodge.
- The author's quotes (spec:21-22, 29, 49, 55, 237, and the whole of 274-298): not copied into entries or decisions; paraphrased in reasoning where a reason depends on them. Her rulings stay as the author decisions of Task 1 and earlier.
- The "**[my call]**" and "agreed" markers (spec:5): the entries state what holds; whose call it was is carried by the decisions' reasoning where it matters (agent call named as such).
- The Task 14 statements (spec:73-74, 81): entries state what holds after Task 14 (done ledger line 221): the clone through the proxy works, so the fallbacks are not needed; a spawning-prompt authorisation is enough; a `CLAUDE.md` line and a settings allow rule are untested.
- The directory layout block (spec:208-213) and the package tree (spec:243-253): restated in prose in s-evv024 and in the package entries rather than as code blocks, since entries are one paragraph.
- The success-measure item label "4 is very important" (spec:38): stated as the author calling this measure very important, citing d-9k0dfe, without her words.

## Dry-run feedback answered

- "Looks related, does it replace or narrow" fired on the area decisions (for example the purpose decisions against the existing author decision on the three must-nots and six success measures, and the structure decision against LODGE-6's decision). Answer for every one: no. Each area decision is a pure move of the document's content into entries; none replaces or narrows anything (plan, Calls made). No `replaces` or `narrows` was added. The same mismatch with spec:151 (feedback fires on decisions that change entries) is already in the ledger as a finding for the next code plan.
- "The text holds the number 1 without a numbers handle": fired on decisions whose text says "Level 1" or cites LODGE-9 or LODGE-10; these are labels (a level, a record code), not figures, so no handle.
- "The text holds the number 2011 / 2017": the years of the two cited works (Nygard, Martin) in d-z57dy1 and d-fkndvh; a figure of the citation, handled with the spec line carrying the citation (spec:93, spec:241).
- Figures given handles (`numbers`): Python 3.13 (spec:72), the four length figures 100 characters, 80 words, 150 words, 1,000 words (spec:135 to 138), 300 lines (spec:261), Python 3.12 (spec:269), each with the spec line in `docs/superpowers/specs/2026-10-29-lodge-design.md`.

## Verification

- `uv run lodge spec` renders all ten areas, no `awaiting`, `fails check`, or `problem:` flags in any heading.
- `uv run lodge check`: ok.
- Every entry at most 150 words, every decision statement at most 80 words and three sentences, every reasoning under 1,000 words, by script before adding.

## Fix round 1

Method: none of these records was published (published state 47dcfa7), so each was edited in place through `lodge draft` into `.drafts/fix1/`, `lodge add --dry-run`, then `lodge add` (no record file touched by hand, no reset, checkout, or force-push).
The four Task 1 decisions went in with `--import`; lodge accepted turning live records into imports, so I1 closes without a replacing record.
Dry runs gave no feedback or `check` lines.
Verification: `uv run lodge check` ok; `lodge spec` has no `awaiting`, `fails check`, or `problem:` flag and no leftover placeholder; the author-record script (reasoning equals quote) gives 28 author records, 0 differ; `sh scripts/check.sh` exits 0 (1071 passed, `ok`).

| Finding | What changed | Records |
|---|---|---|
| I1 | The four live author decisions are imports: dated from her quoted times on 2026-10-29 (22:12, 22:47, 22:46, 22:12, +01:00), `imported_from` the done ledger at lines 211, 215, 214, and 210. `lodge search --by author` now lists them in time order after the merge go. | d-9vxkjw, d-qbfdqt, d-z8jm5y, d-gqyp3n |
| I2 | d-gqyp3n names what "them" was (the personal paths and another project's file paths that final review finding D13 found in the specification and the brainstorm record, from the history as well) and no longer states a standing rule; its title says the same. | d-gqyp3n |
| I3 | "Most important" became "very important", citing d-9k0dfe, in the entry and in d-5mhgpp's reasoning. | s-ph9z0t, d-5mhgpp |
| I4 | Reasoning no longer paraphrases her; each reason that depends on her words cites her decision by ID (d-n30kqr, d-c6n1ng, d-vzvfg2, d-vxfdz7, d-9k0dfe, d-rkcb17, d-14vk9b, d-7v4crf, d-pf8xm9, d-gcz871, LODGE-n decisions), and the grading verbs are gone. | d-cg3nn3, d-zq5sfb, d-18terz, d-f84m43, d-5mhgpp, d-92t2m8, plus citations in d-jj72ps, d-s6mq0f, d-x42f0x, d-knqtc2, d-fkndvh, d-mzkt6e |
| I5 | Entries no longer restate her quotes: goal 4 back to the spec's wording (no "any other knowledge"), the soft-limits, provenance, and Python entries cut to the claim, the non-goals scope entry and the MCP sentence cut to the spec's own claim. | s-rx9d11, s-rger6n, s-bzatqh, s-a4jfp1, s-7ah5n7, s-07ar34 |
| I6 | The viewer goal is stated as meant, with the pilot measuring it (s-3ht96p). | s-m83kjq |
| I7 | A failing check still refuses the add; the entry title and the decision title and statement say feedback advises without refusing. | s-hfjr1m, d-1x1mgv |
| I8 | Title says the gap is between the published state and the one about to be published. | s-zv83s7 |
| I9 | The seven check entries begin with "Check 1:" to "Check 7:"; s-edgt71 names checks 4, 5, and 6. | s-qzk2yb, s-g2jwha, s-yhppm5, s-kvwrqw, s-ms14fq, s-aw5a1j, s-s27z33, s-edgt71 |
| M1 | LODGE-8's statement no longer limits her text to quotes "in lodge". | d-9vxkjw |
| M2 | LODGE-9's statement says what she chose "A" over. | d-qbfdqt |
| M3 | Dropped the second-project clause from s-7ah5n7, the read-only sentence from s-j5ttw1, and made s-582qav point at s-dm37qr. | s-7ah5n7, s-j5ttw1, s-582qav |
| M4 | All 24 decision statements are one sentence per line. | all 24 area decisions |
| M5 | Dropped the coordinator's inferences that the spec does not give ("a reader can rely on", "keeps reads cheap", "judge whether it is current", "costs nothing to ordinary reads", "nothing to keep in step", "lets the writer act", "the baseline shows"). | d-4032xv, d-c08bdw, d-z57dy1, d-zq5sfb, d-1x1mgv, d-5mhgpp |
| M6 | The specification author's calls are named in the reasoning wherever the spec marks them. | d-zerbz9, d-6cyjdh, d-z57dy1, d-mzkt6e, d-4032xv, d-c08bdw, d-a3e8kb |
| M7 | (LODGE-4) added to the install and public entries; reasoning cites d-y8p15p. | s-9n7han, s-fk3yzy, d-jj72ps, d-zq5sfb |
| M8 | `numbers` handles for "tens of thousands of characters" (spec:18) and "over a hundred files" (spec:238). | d-5mhgpp, d-fkndvh |
| M9 | Referents named: filters of the search entry, the first build 0.1.0, the published state and the one about to be published, "in the first user" for the gate before each push, the image observation dated 2026-10-29, and "the author" for the authorisation. | s-dm37qr, s-x84e3h, s-edgt71, s-zv83s7, s-qkcp0s, s-7m3smc |
| M10 | Four titles state the content, not the bookkeeping. | d-5mhgpp, d-cg3nn3, d-f84m43, d-zh00c5 |
| M11 | The report names decisions by ID and s-layout became s-evv024. | this report |

Not fixed: none.
Note: file names of edited decisions keep their old slugs; the title in the header is the new one.
