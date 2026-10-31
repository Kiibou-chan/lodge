# lodge: interacting through the viewer

Status: not approved; written on 2026-10-31 from a brainstorm cut short, under the author's words "Can you just go through this" (2026-10-31 00:47).
Quotes are the author's; everything else is agent text; **[my call]** marks a choice made in writing this document, for her to check.
**[advisor]** marks a choice the advisor changed or added while ruling on the calls (d-7w5aq0, table in `docs/superpowers/plans/2026-10-31-lodge-viewer/advisor-ruling.md`); it is for her to check too.
It adds to the specification in lodge (`lodge spec`) and changes it only where it says so; once built, its content goes into lodge as entries and decisions, and this document is frozen like the first one.

## Intent

Her words (2026-10-30, 09:34 to 09:47, local time, as stamped on each of her messages in the session):

- "And I think would like to have the option to interact with knowledge through the viewer now. Does not need to be editing. But confirming them would be nice." (recorded as d-dyrpc6)
- "Also, what do I do with an entry I have doubts/a question about? A chat on it would be ideal that can then directly interact with it for example."
- "Also, knowledge has a dependency graph, right? Having the entries ordered in some way or arranged would be nice."
- What the arrangement is for: "Easily see and understand dependencies between points. If I see a point that sounds wrong and it rests on another point that's also wrong then that's interesting to know."
- What happens to the points resting on a wrong one: "Retired, corrected, whatever is appropriate".
- Who works that out: "Me, you, both".
- On confirming: "On confirmation, I believe it would not be good if everything I read and confirmed is then marked as mine. It's still very important to know who actually wrote what. Just because I read and confirmed it does not mean that I understand it fully or all of its consequences."
- Editing from the viewer: "Editing from the viewer would also be a goal later" (d-2hcgav).

Today she reaches knowledge in the viewer but acts on it only through a session, where an agent quotes her.
The 82 specification entries lodge holds about itself wait for her confirmation, and she would rather give it in the viewer.

## Goals

1. Confirm from the viewer, in her own words, a single decision or every decision behind an area's entries at once.
2. Raise a doubt or a question on any record from the viewer, and have it answered, and acted on, by an agent, in a thread on that record.
3. Entries that rest on other entries say so, checked, and the viewer shows what an entry rests on, what rests on it, and when something it rests on is in doubt, retired, or changed since.
4. The specification readable in an order that follows those links, areas in their own order.

## Non-goals for now

- Editing records from the viewer (d-2hcgav: later).
- A live chat in the viewer that runs an agent **[my call]**.
  A thread is answered when an agent session next works on the project, which `lodge waiting` and the session's instructions make it do first.
  A live chat needs the viewer to start an agent with tools from a web page, which is a security change of its own; the thread's format is what a live chat would write, so it can come later without changing the records.
- Links between decisions beyond `replaces`, `narrows`, and `confirms`; a decision already rests on what its reasoning cites.
- Writing from the viewer over any network address that is not configured; see Security.

## Must nots

The first design's must-nots hold, and three follow from her words here:

1. Confirming never makes agent text read as hers: the confirmed decision keeps its `decided_by`, and her confirmation is a separate author record in which only the quote and the reasoning are her words, the title and statement being lodge's fixed text **[advisor]**.
2. The viewer never records words she did not type: every author record it writes takes its quote from the form, verbatim.
3. A doubt never changes a record by itself: it marks the record and what rests on it, and the change comes from a decision, as every change does.

## Confirming

On a decision's page, an agent decision not yet confirmed shows a form: a text field, "Your words", and a button, "Confirm".
On an area's page, the same form confirms every current agent decision, not yet confirmed, that created or last changed an entry in the area, listed above the form with their titles and with the entries each changes, in this area or another, so she sees everything she confirms **[advisor: the entries]**.
The form carries the IDs it listed, and the viewer confirms exactly those; when one of them has since been replaced or confirmed, it writes nothing and shows the page again with the new list **[advisor]**.
The field is required, and its text is recorded verbatim.
The form says, beside the field, that the record stays the agent's and that her words are kept as written, so a caveat such as "read, not fully understood" belongs there.

Submitting writes one author decision through the same code path as `lodge add`:

- `decided_by: author`, `confirms` the listed decisions, `scope` `product` when any listed decision is `product` and `process` otherwise (every decision behind an entry is `product` today) **[advisor]**;
- `quote: {text: <her words>, where: "lodge viewer", when: <now, local time to the minute>}`;
- title "Confirms d-xxxxxx" or "Confirms the decisions behind area NAME", statement "The author confirms d-xxxxxx." or the list, and reasoning equal to her words (the rule for author records);
- the generated title and statement are lodge's, not hers, and only the quote and reasoning hold her words **[my call]**.

The checks run as for any `lodge add`, and a failure shows on the page with nothing written.
After a write the viewer answers with a redirect to the page the form was on, so reloading the page does not send the form again **[advisor]**.
In checkout mode the viewer then commits the new or changed record files alone, by explicit path, and does not push **[my call]**: a staged file in a working tree an agent is using could be swept into an unrelated commit or lost; the next push by a session carries it.
The commit leaves any other staged file staged, as `git commit --only` does, and takes the checkout's own git identity, since she made the write **[advisor]**.
A viewer write in checkout mode therefore reaches a session in another worktree, or a cloud session, only once the branch is pushed or merged.
This holds for every viewer write: confirmations, new threads, replies, and closing a thread, each its own commit, with a message naming what it is ("Author confirmation from the viewer: d-xxxxxx", "Thread q-xxxxxx: author reply").
The viewer does not commit on the base branch (`[store] base`, default `main`), on a detached HEAD, or while a merge, rebase, or cherry-pick is in progress **[advisor: the last]**: there it writes and stages, and the page says the write is staged and not committed **[my call]**, since `main` takes only merges.
If git's index is locked by another process, the viewer retries once after a second, then leaves the files staged and says so.
Committing is a new operation of the store port in `gitstore`, the only package that touches git.
In branch mode `add` already commits and pushes, and thread writes do the same.
At level 1 a confirmed decision shows "confirmed by the author" with the confirming decision's ID, beside its own `decided_by`, which never changes.

## Doubts and questions

A **thread** is a new record kind (prefix `q-`), stored under `lodge/threads/` **[my call]**.
Its header names the record it is about (`about`, the ID of one decision or entry **[advisor: not a thread]**), its kind (`doubt` or `question`), and its state (`open` or `closed`); its body is a list of messages, each with who wrote it (`author`, or the agent role), when, and the text.
Messages are only ever appended; a message is never edited **[my call]**, so a thread is a record of what was said.
Check 5 extends to threads: a thread whose published messages, `about`, or kind have changed fails it, and its state may only go from `open` to `closed` **[advisor]**.
An author message's text is her words, verbatim, as typed in the viewer or quoted by a session.

In the viewer every record's page has "Raise a doubt" and "Ask a question", each a text field; the page shows the record's threads below it, newest last, with a reply field while a thread is open and a "Close" button.
On the command line: `lodge threads` lists open threads, `lodge thread q-xxxxxx` shows one, `lodge ask REF --kind doubt|question --by ROLE FILE` opens one, `lodge reply q-xxxxxx --by ROLE FILE` appends a message, and `lodge close q-xxxxxx --by ROLE` closes it **[my call]**: her "Me, you, both" makes agents raise doubts too, a reviewer's say.
Closing appends a message by whoever closes the thread, with an empty text when none is given, which reads show as "closed by BY", so a closed thread shows who closed it and when, and "Closed." is never recorded as anyone's words (d-a3h9f3) **[advisor]**.
A message by `author` written from the command line needs `--where` and `--when`, as an author record's quote has both, and records them **[advisor: `--when`]**; the viewer records `where: "lodge viewer"` and the time of the write **[my call]**.
An agent writes `--by author` only with her words verbatim from where it names, as for author decisions.
`lodge waiting` gains a first group, waiting for an agent: the open threads whose last message is the author's.
The flagged decisions and the open threads whose last message is an agent's follow as waiting for the author, and the viewer's list shows both groups **[advisor]**.
Search and the timeline cover decisions and entries, as now; threads are read with `lodge threads`, `lodge thread`, and on their record's page **[advisor]**.

An open doubt shows at level 1 on its record, as "in doubt", in every read, and on every entry that rests on that record, directly or further down, as "rests on s-xxxxxx, in doubt".
A doubt on a decision also marks the entries that decision created or last changed, and what rests on them, as "changed by d-xxxxxx, in doubt" **[my call]**: she reads on the specification, so a doubt on a decision must show there.
A question shows as "question open", and nothing rests on a question.

Acting on a thread is a decision, as every change is: an agent that answers a doubt by retiring or correcting the record, or what rests on it, writes a decision whose reasoning names the thread, appends a message saying what it did and naming the decision, and closes the thread only if the author's last message asked for that or she closes it herself **[my call]**.
Who works out what is appropriate is open by her words, "Me, you, both"; the thread is where that happens.
An agent change made from a thread on an author record raises the review flag as any other.

An open thread never fails the gate; a thread whose header cannot be read fails check 1, one whose `about` does not resolve fails check 2, and one whose published messages changed fails check 5 **[advisor: checks 1 and 5]**.

## Rests on

A specification entry may list `rests_on: [s-xxxxxx, ...]`: the entries it would not hold without **[my call: entries only, not decisions]**.
`rests_on` is part of the entry, so adding or changing it is a change to the entry, made with a decision like any other.
A decision that changes only an entry's `rests_on` lists it with a new action, `link`; check 4 fails on a `link` change that alters anything else in the entry **[my call; advisor: check 4]**.
A `link` change raises no review flag and does not count as the entry's last change for "changed since", so adding links to existing entries neither floods `lodge waiting` nor clears the warning the links exist for.
The check fails on a `rests_on` ID that does not resolve or names a non-entry (check 2), and on an entry in a cycle of `rests_on` links (a new check 8) **[my call]**, since a cycle has no point to start from.
Check 6 extends to `rests_on`: an entry edited in this change may not newly rest on a retired entry.
Feedback, never a refusal: an entry whose statement names another entry's ID without listing it in `rests_on` is asked whether it rests on it.

Reads derive the reverse ("supports"), and show at level 1, on an entry, any entry it rests on that is in doubt, retired, or changed after the entry's own last change ("rests on s-xxxxxx, changed since") **[my call]**.
An entry that still holds after what it rests on changed is said to hold by a decision that lists it with `edit`, its text unchanged, and says why in its reasoning; that is its new last change, and check 4 already allows it **[advisor]**.
Level 3 lists `rests_on` and its reverse, "supports", both ways.

## Arrangement

`lodge spec` and the viewer's specification show areas in their own order (fixing the alphabetical order of today): each area's `_area.md` gains an optional whole-number `rank`, areas with a rank come first in rank order, the rest after them alphabetically, and two areas sharing a rank are ordered by name, with feedback from `lodge add` on the shared rank **[advisor]**, and within an area the entries in an order that puts every entry after those it rests on in the same area, ties kept in the area's own order **[my call]**.
The area's stored `order` stays the check's reference (check 7), and the derived order is a reading order only.
The viewer's specification page offers "As written" (the area's order) and "By dependency" (the derived order, with each entry indented under the first entry it rests on in the area, and cross-area links as lines "rests on s-xxxxxx (area)").
It opens on "By dependency", the order `lodge spec` prints **[advisor]**.
An entry page shows a small tree: what it rests on, down to the roots, and what rests on it, one level.

## Security

Writing makes the viewer a target it was not when read-only.

- Every write is a `POST` carrying a token minted when the viewer starts and embedded in its pages; a request without it, or with a foreign `Origin`, is refused **[my call]**, the token compared in constant time **[advisor]**.
- The host check stays: `127.0.0.1:PORT` and `localhost:PORT`, plus each value given with `lodge view --allow-host HOST` (repeatable), compared with the whole `Host` header, so a reverse proxy on another port is given as `name:port` **[my call]**; no machine name appears in code or committed settings.
- A write's `Origin` must be `http://` or `https://` followed by an allowed host; a write without `Origin` is refused, since browsers send it on every `POST` **[my call]**.
- Writes are limited to the threads and author records described here; the viewer never edits an existing decision, entry, or area file, and changes a thread file only by appending a message or closing it **[advisor]**.
- Anyone who can reach the viewer can write as the author; that is the trust LODGE-2 already gives `decided_by: author`, and is why only names she configures are allowed.

## Process consequences

All of the following are tasks of the plan that builds this design, after the code they need:

- Agents read open threads first: the guide (`lodge guide`) and the project instructions say to run `lodge waiting` at the start of a session and answer what waits.
- The 82 existing entries get `rests_on` in one coordinator decision per area, proposed from their text (4 name another entry by its ID today: s-dm37qr, s-hfjr1m, s-m83kjq, and s-582qav **[advisor]**), each listed in the task report for her to check in the viewer.
- This design goes into lodge as entries and decisions, and the entries and decisions that say the viewer is read-only are retired, edited, or narrowed to match.
  Found so far **[advisor]**: s-dm37qr, s-582qav, and s-nzhyh3 (read-only); s-j5ttw1 ("There is no confirmation step", which meant the author label and now reads against confirming); s-a67fqm and s-evv024 (two record kinds, and where files live); s-0yzshh (the actions of `changes`); s-01k42c (the review flag, now without `link`); s-j70a0k and s-edgt71 (seven checks); and s-0s9m2d (the list of what waits).
- Task 3 of the plan that put lodge into lodge (her confirmation) is done by her in the viewer once this is built.

## Left to the builder

The page layout and styling, within the existing viewer's look; the thread file's exact Markdown shape; the new modules' placement within the package rules in `tests/structure_rules.py`; how the derived order breaks ties beyond the rule above.

Its content now lives in lodge (`lodge spec`, `lodge show`); this document is frozen.
