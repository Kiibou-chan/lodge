# Task 13 review: dogfooding and the public README

Commit fe01a67 against BASE c8d6d93, worktree `build-0.1`.
Passes: correctness, then practice, then design.

## Verdicts

Spec compliance: yes, with gaps.
All 21 items of "Her decisions, as she made them" (spec 276 to 296) have a record, codes LODGE-1 to LODGE-7 on the right seven, every quote verbatim with the right `where` and `when`, no tag created.
Gaps: four author-labelled records state things the spec and brainstorm do not hold (I1).

Task quality: not approved.
0 Blocking, 3 Important, 4 Minor.
I1 needs a fix round before merge; I2 and I3 are lodge defects the dogfood surfaced, Important for 0.1, and can go to the final fix wave if the integrator prefers.

## Verification run

Scratch copy from `git archive fe01a67`, git in the scratchpad only, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`.

- `uv run lodge check --gate`: `ok`.
- `uv run lodge waiting`: `nothing waits for the author`.
- `lodge show d-7m3rc1` prints `narrowed by d-y8p15p` at level 1, so LODGE-3's "private" is not shown bare.
- `lodge show d-y8p15p`, `lodge show d-n30kqr --reasoning`: render as expected.
- `lodge search "" --status any | grep -c '^d-'`: `20` of 21 records.
- README's `.lodge.toml` block copied verbatim as the settings: `lodge check` says `ok`; a hook event for `docs/verdicts.md` then returns the frozen-file advice.
- `lodge view --help`: `--port PORT default 8787`, as the README says.
- Editing an unpublished record: `lodge draft d-n30kqr`, changed, `lodge add --dry-run` and `lodge add` both refuse with `check 5: d-n30kqr: statement of a published decision was changed`, even with `main` holding no records.
- Not run: `sh scripts/check.sh` and pytest (the report says green, 998 passed).

## Quotes, item by item

Every `quote.text` checked against spec 276 to 296, spec 3, spec 237, and the brainstorm.
None is a paraphrase; punctuation and her spellings ("developement", "thousand(s)") are kept.
Times: LODGE-1 and LODGE-2 14:14, LODGE-3 14:15, LODGE-4 14:21, LODGE-5 14:52, LODGE-6 17:17, LODGE-7 17:19, engineering 14:05 (spec 237); the rest `2026-10-29`, as the brief says.
`where` is `lodge brainstorm` on all 18, and the spec path on the three fallbacks.

The three "Approved" fallbacks: the word and time are real (spec 3: `approved by the author, 2026-10-29 14:26 ("Approved")`).
- Own repository (d-dd17rs) and dogfooding (d-y19d7r): neither the spec (277, 288) nor the brainstorm ("Own project, own repository", "Dogfooding (author's idea)") holds her words, so the fallback is right.
- Local viewer (d-gcz871): the brainstorm does hold her words on the need this record's reasoning restates (M2), so the fallback was avoidable.

LODGE-4 (d-y8p15p) quotes the 14:21 sentence, whose "eventually" reads weaker than the statement's "public from the first commit"; the deciding "A" at 14:22 is in the reasoning (line 20).
That is what the brief and spec 293 give, so no finding.

Scopes: all right.
`process` on LODGE-3, LODGE-4, LODGE-5, Python, dogfooding, and engineering principles; `product` on the rest.
d-dd17rs mixes the two (own repository is process, data in the project is product); `product` is defensible.

## Important

### I1. Four author-labelled records state what the author did not say

Handles:
- `lodge/decisions/d-n30kqr-knowledge-is-read-at-three-levels.md:12`: "within a few hundred to maybe a thousand words"; her words, quoted four lines above at :8 and at spec 284, are "maybe thousand(s) at most".
  The level-1 statement narrows her bound by up to an order of magnitude.
- `lodge/decisions/d-yfkgx3-the-tool-is-named-lodge.md:16`: the masons' lodge etymology is in no spec or brainstorm line (`git grep -i mason` finds only `README.md:7`); spec 276 gives her reason as "lodge sounds fun", four words, and the brief caps reasoning at the spec's own words.
- `lodge/decisions/d-vxfdz7-engineering-principles-are-enforced-from-the.md:15`: "The first project to use lodge needed weeks of cleanup" is false; the first user has not used lodge (the brainstorm's agreed order is build, evaluate, pilot, then replace), and her words, quoted in the same record, say "2 weeks" and name the first user.
  Line 11 also says strict typing and test-first are "enforced by tests", which the brainstorm lists as principles beside the tested rules, not as tested.
- `lodge/decisions/d-dd17rs-lodge-has-its-own-repository-and.md:16`: "lets the tool change without moving the data" has no source; spec 77 to 79 give only the facts.

Failure scenario: an advisor runs `lodge show d-n30kqr` to rule on a 1,500-word reasoning, reads the author's bound as about a thousand, and rules against her actual "thousand(s)".
lodge trusts `decided_by: author` (LODGE-2) and nothing flags the record, so these are must-not 1 failures in the store meant to show lodge working.

Fix: records are immutable once committed on the branch (verified above), so a `lodge draft` edit is refused.
The branch is unmerged, `main` holds no records, and nothing links to these four IDs (`grep -rl` over `lodge/decisions` finds only the records themselves).
Ledger ruling for the integrator: in the fix commit, `git rm` the four record files (and d-gcz871 and d-7v4crf for M2 and M3) and re-add corrected drafts through `lodge add --dry-run` then `lodge add`, so the files are still written only by `lodge add`.
Corrected text: d-n30kqr "within a few hundred to maybe thousands of words at most"; d-yfkgx3 reasoning "The author chose it because it sounds fun." only; d-vxfdz7 reasoning "the first user needed two weeks of cleanup after flat folders, import cycles, and no component boundaries; here enforcement comes first." and statement "applied from the first commit, with allowed imports, no import cycles, a module size limit, and no unused code enforced by tests"; d-dd17rs reasoning cut to the first clause.
Cost if the ruling is instead "replace by new decisions": six replaced records on day one of the dogfood, which is upkeep must-not 3 warns about.

### I2. Search stops at 20 without saying so, in the command line and the viewer

Handle: `src/lodge/core/search.py:46` (`limit: int = 20`), called with the default from `src/lodge/app/reads.py:32`, which serves both `cli/commands.py:56` and `viewer/server.py:126`.
Verified: `lodge search "" --status any` prints 20 of 21 records and no note, while `lodge search --help` says "empty lists all".
Failure scenario: in a project with hundreds of decisions, an agent or the author lists all current process decisions, sees 20, and concludes that no decision covers a topic held by the 21st; the viewer's search page, the author's main way in (spec success measure "quicker to find in the viewer"), does the same.
Important for 0.1: yes, it is must-not 1 on the read path and the fix is small.
Fix: `core.search` returns the IDs and the total that matched; `Listed` carries the count; the command line ends with "20 of N shown; narrow the query" when cut, and the viewer shows the same line; an empty query lists all, as the help says.
Test first: 21 decisions, `search ""` lists 21; a query matching 25 prints the "of 25" line.

### I3. "Looks related" fires on one shared title word

Handle: `src/lodge/core/search.py:14-15` with `related` at :63-71: `_TITLE_WEIGHT = 3` against `_RELATED_SCORE = 2`, so one word shared with a candidate's title clears the bar.
Verified: a test draft titled "Records name the project they belong to" was told it looks related to d-49rmkb, d-vzvfg2, and d-dd17rs, through "records" and "project" alone; the builder saw the same on every add, mostly through "lodge".
Failure scenario: in the first user nearly every title carries "renderer" or "core", so every add gets three false suggestions; agents learn to skip the line, and the one real "this replaces d-…" is ignored, which defeats spec 151 and the success measure "every change names what it changes".
Important for 0.1: yes, the pilot measures exactly this behaviour; it is a small pure-core change.
Fix: in `related`, ignore words that occur in more than a third of current decisions (document frequency from the snapshot, still pure), and require at least two distinct shared words.
Test first: five decisions all titled with "lodge", a draft sharing only "lodge" gets no related note; a draft sharing two content words with one of them gets that one.

## Minor

### M1. `--dry-run` names an ID the real add will not use

Handle: `src/lodge/app/writes.py:83-84` mints IDs per attempt, and feedback quotes them.
Verified: the dry run above printed `d-rq3x0r: it replaces and narrows nothing, but …`; the report's "prints no ID for the draft" is inaccurate, it prints one in feedback.
Failure scenario: an agent copies `d-rq3x0r` from the dry run into a second draft's `narrows`, and the real add mints another ID, so the check refuses the second draft as linking to nothing.
Not Important for 0.1: the refusal is loud, and adding first then reading the ID (as the builder did for LODGE-4) works.
Fix: in a dry run, name a new decision in feedback by its draft file ("dr.md: it replaces …"), and add one guide line that a decision's ID exists only after `lodge add`.

### M2. The viewer record falls back to "Approved" though her words exist

Handle: `lodge/decisions/d-gcz871-the-author-browses-lodge-through-a.md:8`; its reasoning at :16 restates the brainstorm's "Browsing need" line.
Fix, with I1's re-add: quote "Not being reliant on a session to have quick access to project knowledge and rulings/decisions (what's the difference anyways?) would be nice.", `where: "lodge brainstorm"`, `when: "2026-10-29"`.

### M3. The Python record drops her hedge

Handle: `lodge/decisions/d-7v4crf-lodge-is-written-in-python.md:16`: "judged it too much"; her words (spec 280) are "maybe that's too much for this for now".
Fix, with I1's re-add: "thought it maybe too much for this for now".

### M4. README names no tag

Handle: `README.md:31` installs `@<tag>`, and no tag exists yet.
Fix: when `v0.1.0` is tagged after the merge, write `@v0.1.0` and say that later releases are the repository's tags.

## README against the brief

Covers what lodge is, install from a tag, `lodge init`, reading, the write path with `--dry-run` before `lodge add`, `--attach` once per file, UTF-8 text, one new decision, the viewer, the hook snippet in project settings with the frozen-glob rules stated without `fnmatch` (`*` and `?` within a folder, `**` across, brackets literal), and every `.lodge.toml` key with its default.
Text rules: British English, no em-dashes, Oxford commas, one sentence per line, "the author" throughout, no "her" or "she" (grep over the diff's added lines).
No personal paths or machine names in the commit's added lines; the only account name is the prescribed GitHub URL.

## Files read

`.claude/agents/reviewer.md`, `CLAUDE.md` (dispatch context), the task 13 brief and report, the review package diff (all record files, README, version and check.sh hunks), `docs/brainstorm-brainstorm-2026-10-29.md`, spec lines 3, 27 to 79, 101 to 178, 219, 237, 274 to 311, `src/lodge/core/search.py`, `src/lodge/core/words.py`, `src/lodge/app/writes.py` 40 to 130, `src/lodge/app/reads.py` 30 to 36, `src/lodge/core/settings.py` (keys), `src/lodge/viewer/pages.py` 13 to 28, and greps of `viewer/server.py`, `cli/commands.py`, `cli/parser.py`, `hook/post_tool_use.py`.

Not read: the rest of the spec, the ledger, the other `src` modules, the tests (only the three version hunks), and `uv.lock` beyond its hunk.
