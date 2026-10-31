# Advisor ruling on the viewer interaction design

Recorded in lodge as d-7w5aq0 (`uv run lodge show d-7w5aq0 --reasoning`).
The design is `docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md`; changes there are marked **[advisor]**.
Every row is agent text, for the author to check.

## The design's calls

| Call (section) | Ruling | Handle |
| --- | --- | --- |
| No live chat that runs an agent (Non-goals) | Keep | `src/lodge/viewer/server.py` POLICY forbids scripts; d-14vk9b; the thread format is what a chat would write, so nothing is rebuilt later |
| A confirmation's scope is that of the first listed decision (Confirming) | Change: `product` when any listed decision is, else `process` | the first-listed rule depends on list order; all 25 entry-changing decisions are `product` today (`lodge/decisions/`) |
| Generated title and statement are lodge's, only quote and reasoning hers (Confirming) | Keep; must-not 1 reworded to match | LODGE-8 (d-9vxkjw); must-not 1 had said the record holds only her words |
| Commit by explicit path, no push, in checkout mode (Confirming) | Keep; other staged files stay staged, checkout's identity | `src/lodge/gitstore/checkout.py` `CheckoutStore.publish` only stages |
| No commit on the base branch or a detached HEAD (Confirming) | Keep; also not during a merge, rebase, or cherry-pick | `CLAUDE.md`, Git: `main` takes only merges; git refuses a partial commit during a merge |
| Threads are a record kind `q-` under `lodge/threads/` (Doubts and questions) | Keep; `about` names a decision or an entry | `src/lodge/core/model.py` `Record` |
| Messages only appended (Doubts and questions) | Keep; check 5 extends to threads | s-ms14fq: decisions are immutable by the same check |
| `ask`, `reply`, `close` for any role (Doubts and questions) | Keep; closing appends a message from the closer | her "Me, you, both" (Intent) |
| Author message from the command line needs `--where` (Doubts and questions) | Change: `--where` and `--when` | Check 3 (s-yhppm5) asks both of an author quote; without `--when` the time recorded is the time typed in |
| The viewer records `where: "lodge viewer"` (Doubts and questions) | Keep | must-not 2 of the design |
| A doubt on a decision marks the entries it changed (Doubts and questions) | Keep | s-q4s548; builder check, question 2 |
| An agent closes a thread only on her ask (Doubts and questions) | Keep | must-not 3 of the design |
| `rests_on` on entries only (Rests on) | Keep | her words in Intent are about points resting on points; decisions link through `changes` (s-0yzshh) |
| The `link` action, no flag, not a last change (Rests on) | Keep; the failing check is check 4 | builder check, question 6; `src/lodge/core/check_entries.py` |
| A cycle of `rests_on` fails a new check 8 (Rests on) | Keep | a cycle has no reading order; s-j70a0k to be amended |
| "Rests on s-x, changed since" at level 1 (Rests on) | Keep; an `edit` with unchanged text clears it | `src/lodge/core/check_entries.py` `check_entries` lists an edit only when the text changed |
| Two areas sharing a rank fail check 7 (Arrangement) | Change: ordered by name, with feedback from `lodge add` | d-c6n1ng: feedback, not refusal, where nothing is wrong |
| Derived order within an area (Arrangement) | Keep; the viewer opens on it, as `lodge spec` prints | `src/lodge/core/render.py` `spec_view` |
| Token on every write, foreign `Origin` refused (Security) | Keep; compared in constant time | `src/lodge/viewer/server.py` `do_POST` |
| `--allow-host` matches the whole `Host` (Security) | Keep | `src/lodge/viewer/server.py` `_answer` |
| A write without `Origin` refused (Security) | Keep | browsers send `Origin` on every `POST` |

## Gaps a build would trip on

| Gap (section) | Ruling | Handle |
| --- | --- | --- |
| "The viewer never edits an existing record file", while replies and closing append to one (Security) | Change: never edits a decision, entry, or area file; appends to threads only | the design's own Doubts and questions section |
| The area form shows titles only (Confirming) | Change: lists the entries each decision changes, in any area | LODGE-6 (d-8nkamy): what she confirms counts as hers for the review flag |
| The area form could confirm a decision added after she loaded the page (Confirming) | Change: the form carries its IDs; a stale list writes nothing | s-q4s548 |
| A reload re-sends the form and writes a second author record (Confirming) | Change: redirect after every write | `src/lodge/viewer/server.py` has no write path yet |
| `lodge waiting` was the author's list and now agents read it too (Doubts and questions) | Change: two groups, waiting for an agent and waiting for the author | s-0s9m2d; `lodge --help` describes `waiting` as for the author |
| Whether search and the timeline return threads (Doubts and questions) | Change: they do not; threads have their own commands and pages | `src/lodge/core/model.py` `Record` |
| Which checks a thread can fail (Doubts and questions) | Change: checks 1, 2, and 5 | s-qzk2yb, s-g2jwha, s-ms14fq |
| "17 name another record today" (Process consequences) | Change: 4 name another entry by ID | count of entry bodies under `lodge/spec/` naming an `s-` ID; 17 included IDs of decisions and LODGE codes |
| Entries the design contradicts (Process consequences) | Change: listed, s-j5ttw1 among them | `uv run lodge show s-j5ttw1`: "There is no confirmation step" |

## Questions left to the author

None: every call either follows from her words and recorded decisions or is a local rule a later decision can change without a rebuild.
