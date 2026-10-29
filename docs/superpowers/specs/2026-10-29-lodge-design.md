# lodge design

Status: approved by the author, 2026-10-29 14:26 ("Approved"); her questions LODGE-1 to LODGE-4 answered.
Source: the lodge brainstorm (her words verbatim, the evidence, the prior art).
Quotes are the author's; "agreed" marks a proposal she accepted; **[my call]** marks a choice made in writing this document, for her to check.
The next step is the implementation plan, `docs/superpowers/plans/2026-10-29-lodge.md`.

## Intent

lodge is a knowledge tool for software development done by agents with a human in the loop.
Agents use it to record and read a project's decisions and specification in one defined way; the author browses the same knowledge without a session.
First user: gloss.

Why now (brainstorm, "How it started"):

- Advisor rulings took the largest share of the first user's fresh Claude tokens, more than all review.
- A ruling run is long and costly because the advisor rebuilds the case with `git show`, `sed`, and `grep` over long dated logs; cost tracks the number of calls, not the prompt length.
- The logs grow without bound: entries of tens of thousands of characters, few entries that say what they replace, and history leaking into the specification.
- The author reaches decisions and rulings only through a session.

Her framing: "decisions need to be searchable and short and reasoning on them also needs to be shortened. Full reasoning on it would only be available if needed at all as a third step."
And: "having actual tooling for this that can work on this effectively but also constrain how it can be worked with and what can be done with it would be wise."

## Goals

1. Short, searchable decisions and specification entries, with reasoning one explicit step away and provenance a further step.
2. One defined way for agents to write knowledge, with feedback at the moment of writing (length, missing "replaces", a competing current decision), as her hook on auto-loaded files does.
3. A local web viewer in which she finds a decision quicker than by asking a session.
4. Replace the first user's decision, ruling, and hand-kept specification files, not sit beside them: "they would be replaced by the tooling, just like any other possible knowledge that's kept in files in the project whatever they may be."
5. Built so that it does not need the cleanup the first user needed (see Structure).

Success after the pilot (agreed), each measured:

- Advisor rulings cheaper and quicker than the baseline measured on the first user (fresh tokens, calls, and minutes per ruling), and "seeing it myself".
- Entries correct on a random sample checked against their sources.
- Every change names what it changes (baseline: few entries in the first user's logs say "replaces").
- Upkeep tokens below the reading tokens saved.
- Agents actually use it: no decision written anywhere else ("4 is very important").
- Quicker to find in the viewer than to ask a session.

## Non-goals for now

- A server. "a serverless prototype seems reasonable for now"; a shared server is the later ideal, so storage sits behind one interface a server can replace (Kotlin is a candidate then).
- An MCP server: "I don't think I can install additional mcp servers in cloud environments".
- The phone.
- Other kinds of project knowledge beyond decisions and specification entries; "What and how that might be useful would have to be evaluated (first on the past and then in a pilot)."
- Her personal to-do list (later, "plausibly integrated there in whatever way makes sense").
- Conversation logs as provenance.
- Hard length limits: "I don't know if hard character limits would serve it well, but guardrails alone usually already help."
- Editing from the viewer **[my call]**: the viewer is read-only, as in the project whose viewer served as the model; her decisions reach lodge through a session, quoted, as they reach the first user's files today.
- Porting a second project onto lodge; whether it later adopts lodge stays open.

## Must nots

Her words: "The tool showing wrong information would definitely be one. But yes, all of the above would not be great."

1. Show wrong information, including a short entry reading more settled than it is.
2. Let an agent quietly rewrite a decision she made.
3. Become a third copy that costs more upkeep than it saves.

How the design answers each:

1. Every level-1 view carries who decided, the status, and any open review flag; reads and viewer use the same parser and check as the gate, so a record failing the check is shown as failing; derived facts (reverse links, review flags, statuses, what replaced what) are computed, never typed by hand.
2. Decisions are never rewritten; an agent decision that touches something she decided is flagged until she confirms it (see Review flag).
3. The old files are frozen after the pilot and retired; the readable spec is generated, not committed; no link is stored in two places; upkeep cost is a success measure.

## Constraints

- Works in cloud sessions: a command-line tool agents run through Bash, plus instructions (settled).
- Every session that needs lodge, cloud children included, installs it from a tag of its public repository, `uv tool install git+https://github.com/Kiibou-chan/lodge@<tag>` (LODGE-4); no credential, setup script, or second attached repository.
  Attaching lodge as a session repository does not reach the child sessions that the first user's coordinator starts, which get one repository each.
  Checked in a cloud session of the first user, 2026-10-29: Python 3.13 and uv are in the image, api.github.com and pypi.org answer, and git traffic goes through a session proxy scoped to the repositories the session holds.
  Not yet checked: whether that proxy lets a session clone a public repository it does not hold; the plan's first task runs the install in a fresh cloud child **[my call]**.
  If it does not, the fallbacks are publishing lodge to PyPI, which is reachable outside the proxy, or the coordinator attaching lodge to each child session.
- Public from the first commit (LODGE-4): no personal paths, names of her machines, or specifics of the first user in code; everything project-specific in the project's `.lodge.toml`; documentation written for a reader who knows neither her nor the first user.
- Python (settled: "easily accessible (so python might make sense?)").
- Files in git are the only source of truth; any index is disposable (agreed).
- The knowledge lives in the repository of the project it is about (settled).
- lodge is its own repository (settled).
- Prose in records follows the author's invariants: British English, no em-dashes, Oxford comma, one sentence per line.
- Installing lodge in a cloud session (`uv tool install git+https://github.com/Kiibou-chan/lodge@<tag>`) works, but auto mode blocks it as code from outside until the user authorises it in that session's chat (Task 2, 2026-10-29); whether instructions held in the repository or a spawning session's prompt can authorise it is tested in the release check.

## The model (agreed with her, detailed here)

Two record kinds: specification entries and decisions.

**Specification entry** (prefix `s-`): what holds now, at level 1, rewritten in place.
It has an area, a title, and a statement.
It has no reasoning of its own; its reasoning is the decisions that changed it, which lodge lists newest first **[my call]**.
Status `current` or `retired`, derived: an entry is retired while a decision that lists it in `changes` as retired is not replaced (LODGE-7); its file stays where it is **[my call]**.
Replacing the retiring decision makes the entry current again, back in its area's order.

**Decision** (prefix `d-`): records a change, close to an architecture decision record (Nygard 2011).
Fields:

- `title` and `statement`: what was decided (level 1).
- `scope`: `product` or `process` (agreed: "one record kind with a scope field"; the first user's decisions and rulings become one kind).
- `decided_by`: `author`, or the agent role that decided (`coordinator`, `advisor`, and so on).
- `date`, local time.
- `changes`: each specification entry it touches, with the action, `create`, `edit`, or `retire`.
- `replaces` and `narrows`: the decisions it supersedes in whole or in part.
- `confirms`: agent decisions the author confirms (author decisions only).
- `work_item`: for process scope, the work item it rules on (a plan path or a request id).
- `quote`: her words with where and when (required when `decided_by: author`).
- `numbers`: each number the statement or reasoning states, with a handle (a record and key, or a runnable command).
- `attachments`: expanded evidence (logs and the like) "where applicable for eval purposes", kept outside the default read path.
- `imported_from`: for a record converted from an existing file, that file and heading (see Rollout).
- Reasoning, as the body under a heading (level 2).

Status `current` or `replaced`, derived: a decision is replaced when a later decision names it in `replaces`.
Nothing in the replaced decision's file changes and the file does not move **[my call]**: a stored status or an archive folder would be a second copy of what the links already say, and would mean editing an immutable record.
Reads and the viewer show current records by default and the rest by filter.
A narrowed decision stays current and shows what narrows it.
A process ruling is a decision with scope `process`; nothing else distinguishes it.

**Identifiers** **[my call]**: a type prefix and six random characters from Crockford's base32 alphabet, minted without coordination between sessions, never reused.
Each record may also carry a human `code` (such as `ITEM-1`), unique and checked, because she and the sessions quote codes; search finds a record by its code.

**Links** go one way in the files, written on the decision; lodge derives and shows the reverse on every read and in the viewer **[my call]**.
The agreed model says "links both ways, checked"; both directions are shown and checked, but only one is stored, so the two copies cannot disagree ("The reverse direction is never stored").

## Levels

1. The decision or specification entry: title, statement, status, who decided, date, scope, and any review flag; what every read returns by default and what she browses.
2. The reasoning: "A few hundred to maybe thousand(s) at most" words, read only when asked for by name.
3. Provenance: her quote, number handles, what it replaces or narrows, the work item, and attachments.

Provenance (agreed): summarised reasoning is enough; exact provenance only for her own words as a quote, numbers as a record or a runnable command, and what a decision replaces or narrows as an ID.
"Provenance has to be accessible, cloud transcripts are not always for example."

Length guidance **[my call]**, soft, in project configuration, to be tuned in the pilot:

| what | guidance | feedback above |
|---|---|---|
| title | one line | 100 characters |
| decision statement | up to three sentences | 80 words |
| specification statement | one paragraph | 150 words |
| reasoning | a few hundred words | 1,000 words |

For scale: the first user's longest records run to hundreds of words, all at one level today.

## Writing, and feedback on writes

Writes go through lodge; an agent never edits record files by hand.
A decision and the specification entries it changes are added together in one operation, so every change to the specification names the decision behind it.
An agent drafts records as Markdown files with a header, and lodge assigns IDs, places the files, and prints feedback.

Feedback, never a refusal at write time (settled):

- a length over guidance, per level;
- a decision that changes nothing, replaces nothing, and narrows nothing while current decisions look related (sharing a specification entry, or ranking high on a search of its title and statement): lodge lists them and asks whether it replaces or narrows any;
- digits in a statement or reasoning without a `numbers` handle **[my call]**;
- an agent decision that will raise a review flag, saying so.

**The check** gates publication (agreed: "a check before merge").
It fails on:

1. a header that does not parse or lacks a required field;
2. an ID that does not resolve, or two records sharing an ID or code;
3. an author decision without a quote, with where and when, unless it is imported;
4. a specification entry created, edited, or retired without a decision in the same change naming it in `changes`, unless it is imported;
5. an existing decision whose statement, quote, `decided_by`, links, or reasoning changed (decisions are immutable; a correction or a shorter reasoning is a new decision that replaces it, LODGE-10);
6. a record added in this change that links to a replaced decision or a retired entry, other than through `replaces`, or `changes` with `retire`; older records keep their links, and reads show each target's status beside them **[my call]**;
7. a specification entry not placed in its area's order.

"The same change" **[my call]** is the difference between two states of the records: the last published state and the state about to be published.
The published state is the remote tip of the shared branch (in the first user, `lodge`), or the merge base with `main` where a project keeps records on its work branches; there the gate runs before every push to `lodge`.
Checks 4, 5, and 6 compare the two states and run only at the gate; reads and the viewer run checks 1, 2, 3, and 7, which need one state.
So `core`'s check takes two snapshots, and the Store port gives the current and the published snapshot, which a server can also give; no history beyond that is needed.

**Review flag** **[my call]**, answering must-not 2: an agent decision is flagged "awaiting the author" when it replaces or narrows an author decision, or changes a specification entry whose last change was an author decision.
A decision she confirmed counts as an author decision here (LODGE-6), so an agent change to text she approved is flagged too.
The flag is derived, never typed, so it cannot be forgotten.
It shows at level 1 on the agent decision, on the decision or entry it touched, and in a viewer list of what waits for her.
It clears when a later author decision names it in `confirms` or `replaces`.
An author decision that replaces an agent decision whose entry edits still stand gets feedback asking whether it edits those entries back (LODGE-7).
The agent decision takes effect at once, as flagged rulings do in the first user today, so work does not stall overnight.
lodge trusts `decided_by: author` as written (LODGE-2, her call): the required quote, with where and when, shows at level 1, so a wrong attribution is visible to her, and the pilot's random sample checks attributions; no confirmation step, and the viewer stays read-only.

## Reading

- Search over titles, statements, and codes, with filters by kind, scope, status, area, and decided-by; results are level-1 lines.
- Show one record at level 1; reasoning and provenance only when asked for by name.
- The readable specification rendered from the entries in area order, with each entry's ID.
  Rendered on demand, not committed **[my call]**: a committed copy is a third copy (must-not 3).
- Every read states how fresh the data is when it comes from a shared branch.

Agents learn the rules from a short guide lodge prints itself; a project's `CLAUDE.md` points at it instead of copying it **[my call]**, so the rules live once, versioned with the tool.

## The viewer

Local, read-only, started from the command line (settled: a web interface, local for now).
It shows search with the filters above, each record at level 1 with reasoning and provenance one click away, links in both directions, the rendered specification, a timeline of decisions, and the list awaiting her.
Built on the same parser and check as the command line, so it cannot disagree with the gate.

## A hook against writing elsewhere

Success measure 4 is the one she named as very important.
lodge ships a hook command for a project's Claude Code settings **[my call]**: after a tool call that edits a record file by hand, or a file lodge has replaced (the first user's decision and ruling logs once frozen), it returns feedback naming the lodge operation to use instead.
Feedback, not a block, consistent with the settled guardrail style.
The pilot counts the occasions it fires.

## Storage

Files in git, one record per file, behind one storage interface (settled), so a server can replace it later.
Layout inside the project's repository **[my call]**:

```
lodge/spec/<area>/_area.md              area title, one-line intro, ordered entry IDs
lodge/spec/<area>/s-xxxxxx-<slug>.md    specification entries, current and retired
lodge/decisions/d-xxxxxx-<slug>.md      decisions, current and replaced
lodge/attachments/<id>/                 expanded evidence, outside the default read path
```

Settings (store mode and branch, length guidance, hook) live in `.lodge.toml` at the root of the working checkout, not in the data, because in branch mode lodge must know where the data is before it can read it **[my call]**.
Record files are Markdown with a YAML header, as in an existing project: the header for programs, the body for people **[my call]**.

The storage adapter reads and writes either the current checkout or a named branch kept in its own worktree, fetched before reads when stale and pushed after writes, retrying on a rejected push.
In the first user, the records live on a `lodge` branch that never merges (LODGE-1, her call); lodge's own data lives on lodge's main.
A specification change therefore does not travel on the work branch that implements it; the decision names that branch in `work_item`, as the first user's "Built: in task 7 on a branch" lines do today.

## Rollout (agreed order)

1. Build lodge, test-first.
2. Dogfood: lodge's own decisions go into lodge as soon as it can hold them, starting with this brainstorm's; until then they live in this document.
3. Evaluate on the first user's past in a scratch copy: convert a sample of decisions, rulings, and spec sections through lodge, replay past advisor rulings with and without it, and measure the success criteria.
   The sample size and replay method go in their own plan once lodge exists **[my call]**, since they set most of the cost.
   That plan also owns the importer and all measurement **[my call]**.
   This build provides only what the importer needs: `imported_from`, explicit past dates (the date is data, so `core` stays clock-free), and the exemptions in checks 3 and 4.
   An imported author decision without a recoverable quote shows "imported, unquoted" at level 1, so it does not read as more settled than it is.
   Measurement is counted from the session transcripts the first user already keeps and its cost logs; lodge itself writes no telemetry.
4. Pilot: new decisions of the first user only in lodge, the old files frozen.
5. Replace the files once the pilot holds.

## Structure

Her requirement (brainstorm, 14:05): "Please from the get go make sure that appropriate software developement and design principles are applied here. I don't want another 2 weeks of cleanup as was needed with gloss."
In the first user, enforcement came last, after many import cycles and flat folders of over a hundred files; here it comes first.
The proposals below were drafted by Claude in the brainstorm and are for her sign-off before any plan.

**Packages**, by responsibility, with one dependency direction (the dependency rule of clean architecture, Martin 2017):

```
lodge/core/        pure: record kinds, parsing and writing the format, levels, the check,
                   write feedback, search ranking, review flags, rendering the specification
lodge/app/         the operations (add, read, search, check, render) and the ports they need:
                   Store (current and published snapshot, write), Clock, IdSource
lodge/gitstore/    the Store on files in git; the only package that touches git or the record files
lodge/cli/         the command line
lodge/viewer/      the read-only web viewer
lodge/hook/        the Claude Code hook command
lodge/main.py      composition root: wires adapters to the app
```

Allowed imports: `app` imports `core`; `gitstore` imports `app` and `core`; `cli`, `viewer`, and `hook` import `app` and `core`; `main.py` imports all; nothing imports `cli`, `viewer`, `hook`, or `gitstore` except `main.py`; adapters never import each other.
Each package has one front door, its `__init__.py`; other packages import only from it.
`core` reads no clock, no randomness, no environment, no disk, and no network: the time and ID entropy come in as parameters (the first user's rule).

**Enforced by tests from the first commit:**

- a structure test, written with the standard library's `ast` **[my call]**: the allowed-imports table above, no import cycles between modules, imports across packages only through front doors, no module over about 300 lines, and no forbidden call in `core` (clock, randomness, `os`, `subprocess`, `open`);
- no unused code: Ruff's unused-import and unused-variable rules, and Vulture over the package with a pinned allow-list **[my call]**;
- strict typing: mypy in strict mode **[my call]**;
- Ruff as linter and formatter with its configuration pinned in `pyproject.toml`.

**Tests**: test-first; `core` tested alone and fast with no temporary files; one end-to-end test per command against a temporary git repository with a bare remote, so pushing and a rejected push are exercised.
pytest **[my call]**.

**Environment**: Python 3.12 or later, `pyproject.toml` and `uv.lock` committed, so a fresh clone in a cloud session reproduces the environment with `uv sync`.
Runtime dependencies kept to PyYAML **[my call]**; the viewer uses the standard library's HTTP server, as an existing project's does.

**Process**: the plan is reviewed before building; at each task's end a maintainability review from two views, practice (duplication, complexity, naming, documentation against behaviour) and design (boundaries, coupling, plan rules no test enforces); multi-agent builds follow the plan, review, and implement rounds of an existing project.

## Her decisions, as she made them

- Name: lodge, "lodge sounds fun".
- Own repository; the data lives in the project it is about.
- Command line through Bash plus instructions, no MCP: "I don't think I can install additional mcp servers in cloud environments".
- Serverless first: "a serverless prototype seems reasonable for now"; a server later ("spending a bit of money on it might be worth it?").
- Python: "easily accessible (so python might make sense?)"; "I personally always like kotlin, but maybe that's too much for this for now".
- A local web viewer; the phone out of scope for now.
- Replace, not sit beside: "they would be replaced by the tooling".
- The specification is "a central part of it"; the spec-entry and decision model, levels, and provenance rules above were agreed.
- Three levels, reasoning "A few hundred to maybe thousand(s) at most" words.
- Provenance: "Provenance has to be accessible, cloud transcripts are not always for example." "And where applicable for eval purposes there can be expanded evidence like logs or anything else attached."
- Guardrails as feedback, a check before merge, her decisions quoted.
- The three must-nots and the six success measures, "4 is very important".
- Dogfooding: lodge keeps its own decisions in lodge.
- LODGE-1, where the data lives in the first user: "A: own branch" (2026-10-29 14:14), a `lodge` branch that never merges, chosen over records on `main` landing with merges.
- LODGE-2, decisions labelled as hers: "A: trust the label" (2026-10-29 14:14), chosen over requiring her confirmation somewhere an agent cannot reach.
- LODGE-3, GitHub: "A: private on GitHub" (2026-10-29 14:15), chosen over keeping it local until the pilot.
- LODGE-5, input and output outside the git store: "A: amend the rule" (2026-10-29 14:52); `gitstore` is the only package that touches git or the record files, while `cli` reads the draft files it is given, `cli` and `viewer` read their own package data, and `hook` reads its input; chosen over routing all of these through `gitstore`.
- LODGE-4, how cloud sessions get lodge: "I would intend this tool to eventually become public" (14:21), then "A" (14:22), public now, chosen over private until a first release with a setup script and token in the meantime; this changes LODGE-3's private to public.
- LODGE-6, an agent changing what she confirmed: "A: Yes, flag it" (2026-10-29 17:17), a confirmed decision counts as hers for the review flag, chosen over flagging only decisions she wrote.
- LODGE-7, replacing an agent's change to her entry: "Seems like A makes (more) sense" (2026-10-29 17:19), a retirement counts only while its decision stands and feedback asks to edit the entry back, chosen over the entry keeping the agent's change.
- LODGE-10, shortening a decision's reasoning: "The latter seems like the better option." (2026-10-29 22:46), reasoning is immutable like the rest of a decision and a shorter reasoning is a new decision that replaces it, chosen over allowing an edit that only removes parts of it.
- Engineering principles enforced from the first commit: "I don't want another 2 weeks of cleanup as was needed with gloss."

## Open

- The licence, hers, before others are invited to use it.
- Whether a second project later adopts lodge; its ID prefixes may clash with lodge's, which matters only then.
- Length guidance values, tuned in the pilot.

## Left to the builder

- Command names, flags, and output formats, within the operations above.
- The search ranking, given the corpus is hundreds of records, not millions.
- How a draft file names the specification entry it edits, and how lodge hands an agent a draft to edit.
- Staleness bound for fetching a shared branch, and the retry policy on a rejected push.
- The viewer's page layout and styling.
- How the hook recognises a hand edit of a record file.
