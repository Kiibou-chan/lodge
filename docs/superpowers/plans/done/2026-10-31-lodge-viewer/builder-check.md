# Builder check: questions before planning the viewer interaction design

Ranked by how much a wrong guess would cost.

## 1. Where does the order of areas live?

The document says `lodge spec` and the viewer show "areas in the order of the area list (fixing the alphabetical order of today)".
No area list exists.
`src/lodge/core/render.py:27` sorts area names alphabetically, and an area is only a folder with an `_area.md` that holds `title`, `intro`, and the entry `order`.
Goal 4 repeats it ("areas in their own order").
Why it matters: the answer decides the storage format.
It could be a key in `.lodge.toml`, a new field on each `_area.md` (a position), or a new index file.
Each of these changes the parser, `lodge draft area:NAME`, the area checks (check 7, or a new one for a duplicate or missing position), and whether the existing ten areas need a data migration.
It also decides whether a project that sets nothing falls back to alphabetical.

## 2. Does a doubt on a decision reach the entries it changed?

`rests_on` exists on entries only, so "rests on" never leads out of a decision.
"An open doubt shows ... on every entry that rests on that record, directly or further down" therefore only ever fires for a doubt on an entry.
But her flow is mostly confirming decisions, and the doubt form sits on every record's page, decisions included.
The document does not say whether an open doubt on decision `d-x` marks the entries `d-x` created or last changed (and, through them, everything resting on those), or only `d-x` itself.
Why it matters: the first reading adds a second propagation path (`changed_by` then `rests_on`) to the derivation, the level-1 flags, the tree, and the tests.
The second leaves a doubt on a decision invisible on the specification, which is where she reads.

## 3. What does the viewer commit in checkout mode, and on which branch?

The document says the viewer commits a confirmation "by explicit path ... and does not push" in checkout mode.
Open points:

- Do doubts, new threads, replies (an edit to an existing, possibly already committed file), and Close get the same commit, or are they only left in the working tree?
- Which branch takes the commit?
  The viewer runs wherever `lodge view` was started, and `CLAUDE.md` says `main` only takes merges on the author's go.
  A viewer started in a checkout of `main` would commit to it.
  Should it refuse on the base branch or on a detached HEAD, or commit anyway?
- Only `gitstore` may touch git (`tests/structure_tables.py`), and `Store.publish` returns `STAGED` and never commits (`src/lodge/gitstore/checkout.py`).
  The commit therefore needs a new port method or outcome.
  A commit also races an agent's own `git add` and commit in the same tree.

Why it matters: this fixes the `Store` protocol change, the fakes in `tests/app/fakes.py`, the gitstore tests, and whether the first tasks touch the git layer at all.

## 4. Who can open a thread, and can a session write as the author?

The command line has `threads`, `thread`, `reply`, and `close`, but no command that creates a thread.
Only the viewer can raise a doubt or ask a question.
Is that intended, or should an agent (a reviewer, say) be able to raise a doubt on a record from a session?
That would be one more command and one more actor on the same record.

Also, `reply --by ROLE` with ROLE `author` is described as "quoted by a session".
It is not said whether that is allowed.
If it is, does an author message then need a `where`, as the author-record quote does, and does check 3 or any other check apply to it?
If it is not, the CLI can never record her words, and a thread she answers in a session is lost to the format.
Why it matters: it sets the thread file format (whether a message carries `where`), the command set, and the must-not 2 test ("the viewer never records words she did not type").

## 5. What does `--allow-host NAME` match, and what happens to a missing `Origin`?

The existing host check accepts only `127.0.0.1:PORT` and `localhost:PORT` (`src/lodge/viewer/server.py`).
For a reverse proxy the `Host` header carries the proxy's name and usually its own port, or none.
Does NAME match the whole `Host` value, the host part with any port, or must the user write `name:port`?
Is an `Origin` compared against the same allowed set?
And is a POST with no `Origin` header, which some clients send, accepted when the token is right, or refused?
Why it matters: this is the security gate on every write, and the choice decides the matching rule and the refusal tests.

## 6. Does adding `rests_on` raise the review flag, and does it reset "changed since"?

`rests_on` is part of the entry, so adding it is an edit of the entry.
The review flag is raised when an agent decision "changes a specification entry whose last change was an author decision" (spec, Review flag).
The coordinator decisions that add `rests_on` to the 82 entries would flag every entry whose last change was hers or a confirmed decision's.
The same edit also becomes the entry's "own last change", so every "rests on s-x, changed since" mark computed before it disappears.
Should an edit that only touches `rests_on` be exempt from both, or is the ripple intended?
Why it matters: the exemption is a rule in `derive.py` (`_flagged`) and in the "changed since" comparison, with its own tests.
Without it the migration produces a large unrelated flag list in `lodge waiting` and wipes out the warning the feature exists for.

## 7. Is the data work part of this plan?

"Process consequences" asks for one coordinator decision per area adding `rests_on` to the 82 entries, "proposed from their text", each listed in the task report for her to check.
It also says the content of this document goes into lodge as entries and decisions once built, and that the existing first design is changed "only where it says so", which includes its sentence that the viewer stays read-only.
Are the migration of the 82 entries, the recording of this design as entries, and the amendment of the old read-only sentences tasks of this plan, or follow-ups outside it?
Why it matters: proposing 82 sets of dependencies is judgment work that needs its own task and review (and the data lives in unpublished, untracked files in this working tree), and it can only come after the `rests_on` field and checks exist, which fixes the plan's order and its last tasks.
