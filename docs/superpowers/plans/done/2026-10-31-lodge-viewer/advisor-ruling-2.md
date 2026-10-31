# Advisor ruling on three plan-review findings

Recorded in lodge as d-a3h9f3 (`uv run lodge show d-a3h9f3 --reasoning`).
The findings are I13, I14, and the s-7ah5n7 part of I11 in `plan-review-correctness.md`, which sent them to the author.
The advisor rules on them in her absence; every ruling is agent text, for her to check.
Plan lines are those of `docs/superpowers/plans/2026-10-31-lodge-viewer.md` at 4f07618; "design N" is a line of `docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md`.
None goes to the author: each follows from her recorded words, and a wrong call costs a local change, not a rebuild.

## I13: a thread closed without text

Ruling: a close without text appends a closing message with an empty text, by the closer, for every role; reads head that message "closed by BY" and show no text under it; no read and no file shows "Closed." as the text of a message.

Why:
- The "Closed." default was the advisor's own addition (design 85, marked **[advisor]** in d-7w5aq0), so it yields to her decisions, not the other way round.
- LODGE-8 (d-9vxkjw, author): "Nothing is my text except than quotes"; a `by: author` message reading "Closed." is text in her name she never gave.
- Design must-not 2 (design 45) and design 81: the viewer never records words she did not type, and an author message's text is her words verbatim.
- What design 85 wanted, who closed the thread and when, survives: the closing message keeps `by`, `when`, and for the author `where`.
- s-q4s548 (lodge must not show wrong information): once the last message of a closed thread is read as the close, a thread closed by hand without a new message would credit the close to whoever wrote last, so check 5 must refuse that.
- Cost if wrong: the thread file format before any thread is published (`lodge/threads/` does not exist yet), plus one heading in two reads.

Plan changes:
- Line 32: drop "Closed." from the list of verbatim strings.
- Line 179: `appended(thread, message, close=True)` accepts a message with an empty text; with `close=False` it raises `ValueError` on an empty text.
- Line 212, check 1: "an empty message text" becomes "an empty message text, except on the last message of a closed thread".
- Line 214, check 5: add `{q}: a thread was closed without a closing message` when the published thread is open, the thread in `after` is closed, and it has no message the published one lacks.
- Line 273: "the text ... must not be empty (`the message is empty`)" holds for `ask` and `reply`; `close` takes the given text, cleaned the same way, or an empty text when none is given or the cleaned text is empty, appends it by the closer, and sets `closed`.
- Line 279 (Task 4 tests): `test_close_appends_closed_by_the_closer` asserts the closing message's `text == ""` and its `by`; add `test_close_without_text_passes_the_check`.
- Task 3 tests (line 221): add `test_empty_text_only_on_the_closing_message` (an empty text on an earlier message, or on the last message of an open thread, fails check 1) and `test_closing_without_a_message_fails_check_5`; `test_thread_round_trips` includes a closed thread whose closing message has no text.
- Line 304, `thread_text`: the last message of a closed thread gets the line `closed by BY · when` (with ` · where` when set) in place of `by · when`, and its text only when non-empty.
- Line 311: `thread` ends with the line `closed by coordinator · …`, and the output holds no "Closed.".
- Line 407, viewer: the closing message of a closed thread is headed "Closed by BY" with its `when` and `where`, and no paragraph when its text is empty; the close form's text area stays optional.
- Line 415 or 416: add a page test that a thread closed from the viewer with the field empty shows "Closed by author" and its file holds no message text.
- Task 9, Doubts and questions decision: the entry on closing states this rule, not design 85's "with the text 'Closed.' when none is given", and its reasoning names this ruling.

## I14: the dependency view indents an entry under one it does not rest on

Ruling: the derived order is depth first; each placed entry is followed at once by the entries it makes ready, siblings in the area's written order, so every indented entry sits under an entry it rests on.

Why:
- Her words on what the arrangement is for (design 15): "Easily see and understand dependencies between points."; an indent that reads as "c rests on b" when it does not defeats that, and s-q4s548 rules it out.
- Both pulling rules are agent calls: the tie rule is marked **[my call]** (design 118), and the indent rule (design 120) is agent text by the design's status line (design 4); neither is her word.
- The design's two visible promises both survive: every entry after what it rests on (design 118), and each entry indented under an entry it rests on (design 120); only "ties kept in the area's own order" becomes "siblings and roots in the area's own order".
- The reviewer's interim fix, a "rests on" line under a wrong indent, leaves the indent misleading and makes the line the only true signal.
- An entry with two same-area targets can be indented under only one, so the others need a line, else the view hides a dependency the entry page shows (design 122).
- Cost if wrong: one function in `core` and one test file, and a different but valid order in `lodge spec`.

Plan changes:
- Line 45, Call 8: "the derived order places, at the top, the first unplaced entry in the area's written order whose current same-area `rests_on` targets are all placed, or on a cycle the first unplaced one, at depth 0; after placing an entry it places at once, again and again, at its depth plus 1, the first unplaced entry in written order whose targets are now all placed and include it, each followed in the same way before the next is sought; `under` is the target whose placement made the entry ready, so an indented entry always sits under it; why: design 118 and 120 and her words in design 15; cost if wrong: a different but valid reading order."
- Line 101: "`under` is the first ID in the entry's `rests_on` ..." becomes "`under` is the entry placed just before the entry's subtree began, the last of its same-area current targets to be placed, or `None` at depth 0"; `depth` follows Call 8; it never raises on a cycle.
- Line 94, `Placed`: add `also: tuple[str, ...]`, the entry's same-area current targets other than `under`, in `rests_on` order.
- Line 108, tests: keep `test_entry_after_what_it_rests_on` (b, c, a holds under the new rule); `test_under_is_first_same_area_target` becomes `test_under_is_the_target_placed_last` (written a, b, d, with d resting on a and b: order a, b, d, d `under` b at depth 1, `also == (a,)`); add `test_dependant_follows_what_it_rests_on` (the reviewer's case: written a, b, c, with c resting on a: order a, c, b, c at depth 1 under a, b at depth 0); `test_cycle_falls_back_to_written_order` unchanged.
- Line 409: in "By dependency", an entry with a non-empty `also`, or at a depth over 5, carries one line "also rests on" with links to `also`, and to `under` too when the depth is over 5, since `depth-5` no longer shows the parent.
- Line 416: `test_spec_opens_by_dependency` uses the reviewer's case (written a, b, c, c resting on a) and asserts the order a, c, b with c in `depth-1`.
- Task 9, Arrangement decision: the entry states "dependants follow what they rest on, siblings in the area's order", and its reasoning names this ruling.

## The s-7ah5n7 part of I11: threads and "other kinds of project knowledge"

Ruling: a thread is not a kind of project knowledge in s-7ah5n7's sense, so the design does not contradict the entry, but its words invite that reading once s-a67fqm says three record kinds; Task 9 adds one sentence to s-7ah5n7 and does not wait for her.

Why:
- She asked for threads herself, a day after that non-goal was written: "A chat on it would be ideal that can then directly interact with it" (design 13, 2026-10-30; the non-goal is in the first design, 2026-10-29, at `docs/superpowers/specs/2026-10-29-lodge-design.md:46`).
- Her reason for the non-goal is that a new kind's use "would have to be evaluated (first on the past and then in a pilot)" (first design line 46); a thread holds no claim that holds now, and what it settles enters lodge only as a decision (design 46, must-not 3, and design 96), so the decisions and entries stay the only knowledge.
- Search and the timeline leave threads out (design 90, d-7w5aq0), so a thread is never read as knowledge.
- "Conversation logs as provenance" means session transcripts, which d-pf8xm9 (author) keeps out of the repository's read path because they are not always available; a thread lives in the repository, and a decision acting on one names it as a handle, as it names a file.
- The entry's decision d-cg3nn3 is a coordinator's, already narrowed by her d-dyrpc6, so an edit narrows no author decision; editing the entry rather than leaving it keeps two entries from reading against each other (s-q4s548).
- Cost if wrong: she rules threads a kind of knowledge, and the edit is undone by one decision; threads exist because she asked for them, so nothing is rebuilt.

Plan changes:
- Line 458, Doubts and questions: add "s-7ah5n7 (one sentence after its first: a thread, a doubt or question on a decision or entry with its messages, is not such a kind: it holds no claim of its own, and what it settles enters lodge as a decision)", its statement otherwise unchanged.
- Line 456: the Doubts and questions decision's reasoning names this ruling and her line 13 author decision for the s-7ah5n7 edit.
- I11's "Task 9 does not run until she answers or the plan records her ruling" is answered by this ruling: Task 9 runs.
- Line 460, the report: the s-7ah5n7 edit is listed with the sentence added, as every edited entry is.
