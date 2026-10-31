# lodge viewer interaction: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** the author confirms decisions and raises doubts and questions from the viewer, entries say what they rest on, and the specification reads in an order that follows those links.

**Architecture:** `core` gains the `rests_on` field, the `link` action, check 8, the area rank and the derived order, and a third record kind, the thread (`q-`), with its marks at level 1.
`app` gains thread operations, the confirmation, and a commit through a new `Store.commit`, which `gitstore` implements with `git commit --only`.
The command line gains the thread commands; the viewer gains `POST` writes behind a token, an `Origin` check, and the host check, and the pages that use them.
Then the records: `rests_on` for the existing entries, this design into lodge, the documents, and the area ranks.

**Tech stack:** Python 3.12 or later, uv, PyYAML, pytest, mypy (strict), Ruff, Vulture; the standard library's `http.server`, `hmac`, `threading`, `urllib.parse`, `secrets` (in `main.py` only), and `subprocess` (in `gitstore` only).

**Spec:** `lodge spec` (the specification in lodge) and `docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md` (the design) where it adds to or changes it, with the advisor's ruling d-7w5aq0 (`docs/superpowers/plans/2026-10-31-lodge-viewer/advisor-ruling.md`).
The plan argues from them, never over them; where they disagree with this plan, they win and the builder reports it.

## Global Constraints

- Builders are Codex (`codex exec`), one task per brief; a brief holds these constraints and its task, and Codex sees only its brief, `CLAUDE.md`, and the repository.
- The design is `docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md`, and "design line N" in a task is a line of that file; where the design and a task disagree, the design wins and the builder reports it.
- In Codex's sandbox git's index is read-only and sockets are refused (`docs/superpowers/plans/2026-10-30-lodge-on-itself/task-5-report.md`, lines 104 and 125): the builder never stages, commits, or pushes, and never needs a socket-bound test to pass.
- The builder's gate: `uv run ruff format --check && uv run ruff check && uv run mypy && uv run vulture && uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py && uv run lodge check --gate`; the two ignored files need sockets, apart from `tests/e2e/test_view.py::test_view_passes_the_port_to_the_viewer` and the tests a task names with it, which the builder runs with `uv run pytest tests/e2e/test_view.py -q -k NAME`.
- The coordinator's gate after every task: `sh scripts/check.sh` green outside the sandbox, then it stages with explicit paths, commits with `git -c user.name="Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, the message ending `Co-Authored-By: Claude <noreply@anthropic.com>`, and pushes `lodge-viewer` to `origin`; never `main`.
  A socket test that fails there goes back to the builder as a fix round, its output in the brief.
- `lodge add` in the sandbox: once per task, `mkdir -p .drafts/objects && cp "$(git rev-parse --absolute-git-dir)/index" .drafts/index`; then every `lodge add` (dry runs need none of this) runs as `GIT_INDEX_FILE="$PWD/.drafts/index" GIT_OBJECT_DIRECTORY="$PWD/.drafts/objects" GIT_ALTERNATE_OBJECT_DIRECTORIES="$(git rev-parse --path-format=absolute --git-common-dir)/objects" uv run --frozen --quiet lodge add FILE...`.
  When that fails, the builder stops with BLOCKED and the error, leaving the drafts and their dry-run output under `.drafts/`, and the coordinator runs the adds.
  The record files land in the working tree, and the coordinator stages them with `git add lodge/`.
- Test-first: each named test is written and seen failing before its code; every existing test keeps passing, edited only where a task says so.
- Structure (`tests/structure_rules.py`, `tests/structure_tables.py`, run by every pytest): allowed imports as `ALLOWED`; other packages import only from a package's `__init__.py`; no import cycles, within a package too; no module over 300 lines, tests included; `core` imports only `CORE_MODULES`; `subprocess` only in `gitstore`; file reads only in `gitstore` and `cli`, and `viewer` reads only its package data.
- `core` and `app` read no clock and no randomness: the time comes from `Clock`, IDs from `IdSource`; the viewer's token is minted in `src/lodge/main.py`.
- Modules near the limit take no new code: `core/apply.py` (277 lines), `gitstore/checkout.py` (257), `core/derive.py` (227), `core/views.py` (220), `cli/parser.py` (219), `app/writes.py` (213); new code goes in the new modules each task names, and a task that edits one of these adds at most the lines it states.
- Tests near the limit take no new tests: `tests/core/test_feedback.py` (282 lines), `tests/core/test_fileformat.py` (279), `tests/viewer/test_pages.py` (239); new tests go in the new files each task names, marked "(new)".
- `tests/`, `tests/core/`, and `tests/app/` are not packages, so a new test file's basename is unique across the three; two files of one name stop pytest at collection.
- Vulture scans `src` and `tests`; every produced name, field included, is read in the task that adds it, by its source or by one of its tests.
- Tests never touch a real repository: git only in `tmp_path` through the existing helpers (`tests/gitstore/repos.py`, `tests/e2e/conftest.py`), no network; fixtures are a made-up project (the `storage` area, transcripts), never her words or another project's records.
- User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line.
- Record files only through `lodge add`; drafts under `.drafts/` (git-ignored); `lodge add --dry-run` before every `lodge add`; a check line stops the task.
- Exit codes stay 0 done, 1 failed check or conflict, 2 usage or environment; no traceback reaches the user, so a `ValueError` from writing a file becomes a `LodgeError` naming the field.
- Text she types in the viewer, and every message text, loses a CR before each LF and the whitespace around it, nothing else, and must not then be empty, except a closing message's text.
- The viewer writes as `author` with `where` `lodge viewer` and `when` the clock's minute, `%Y-%m-%d %H:%M` (design lines 59 and 86).
- Every string the design fixes is used verbatim: "Your words", "Confirm", "Raise a doubt", "Ask a question", "Close", "lodge viewer", "in doubt", "question open", "As written", "By dependency", "Confirms d-xxxxxx", "Confirms the decisions behind area NAME", "The author confirms d-xxxxxx.", "Author confirmation from the viewer: d-xxxxxx", "Thread q-xxxxxx: author reply".

## Calls made

Each is the planner's ruling, for the author to check; a handle follows each argument.
Every task repeats what it needs of them, so no brief needs this section.

1. Ruling: a thread file keeps its header (`id`, `kind: thread`, `about`, `raises`, `state`, `opened`) and its messages in the body, each under a line `## Message <n>`, numbered from 1, then a block of `by`, `when`, and for the author `where`, a blank line, and the text; a text line reading `## Message <digits>` behind any number of backslashes gets one more backslash on write and loses one on read; why: the design puts the messages in the body (design line 78) and leaves the shape to the builder (line 146), and the escape keeps any text exact; cost if wrong: a format change, free before the first thread is published.
2. Ruling: the header key for doubt or question is `raises`; why: `kind` names the record kind in every record file (`src/lodge/core/headers.py`, `_expect_kind`); cost if wrong: a rename before the first thread.
3. Ruling: `opened`, the time lodge wrote the first message (ISO 8601 with seconds and offset), orders threads newest last; why: the design shows threads newest last (line 83), and an author message's `when` is free text, as a quote's is (`src/lodge/core/headers.py:133`, `_quote`), so it cannot be sorted; cost if wrong: one header key.
4. Ruling: a message's `when` is the author's time as given (`--when`, or the viewer's minute) for her messages and lodge's clock (ISO with seconds) for an agent's; why: design line 86 and line 59; cost if wrong: one rule in `app/threads.py`.
5. Ruling: a decision whose change on an entry is `link` is left out of `changed_by` and listed in a new `linked_by`; why: an entry's level 1 takes who decided from `changed_by[0]` (`src/lodge/core/views.py:69`), so a coordinator's links on her entry would read as the coordinator's (must-not 1 of the design), and design line 107 says a `link` is not the entry's last change; cost if wrong: an entry's level 2 does not list link decisions, which level 3 does.
6. Ruling: "rests on s-x, retired" and "rests on s-x, changed since" look one link deep, and "rests on s-x, in doubt" looks down every link; why: design line 92 says "directly or further down" for doubts only, and line 113 clears "changed since" per direct link; cost if wrong: a change two links down shows only on the entry between.
7. Ruling: the reverse of `rests_on` is called "supports" in level 3 and the viewer; why: design line 112 names it "supports", and "supported by" (line 114) would label the reverse wrongly; cost if wrong: one label.
8. Ruling (d-a3h9f3, the advisor's, on correctness I14): the derived order places, at the top, the first unplaced entry in the area's written order whose current same-area `rests_on` targets are all placed, or on a cycle the first unplaced one, at depth 0; after placing an entry it places at once, again and again, at its depth plus 1, the first unplaced entry in written order whose targets are now all placed and include it, each followed in the same way before the next is sought; `under` is the target whose placement made the entry ready, so an indented entry always sits under one it rests on; why: design lines 118 and 120, and her words in design line 15, "Easily see and understand dependencies between points."; cost if wrong: a different but valid reading order.
9. Ruling: `lodge spec` prints the derived order, and after each entry one line `rests on s-xxxxxx (area)` per target in another area; why: design line 121, "the order `lodge spec` prints", and line 120 for the cross-area lines; cost if wrong: two lines of output per cross-area link.
10. Ruling: no new area; the design's entries go into `purpose`, `model`, `writing`, `reading`, and `storage` by topic, and the ranks follow the first design's section order, as the plan that put lodge into lodge laid the areas out (`docs/superpowers/plans/2026-10-30-lodge-on-itself.md:73`); why: the brief names "the ten existing areas"; cost if wrong: one area draft.
11. Ruling: an area's page is the existing `/spec?area=NAME`; why: the viewer has no other area route (`src/lodge/viewer/server.py`, `_page`); cost if wrong: one route.
12. Ruling: the viewer's writes are `POST /confirm`, `POST /threads`, `POST /threads/<q>/reply`, and `POST /threads/<q>/close`, with the fields of Task 6b's table; a write answers `303 See Other` to the page the form was on with `done=<code>`, a fixed code whose text the page shows; a stale list answers `303` with `done=stale`; a failed check or a refused input answers 400 with the reason and nothing written; why: design lines 52, 63, and 64, and no text she typed ever goes into a URL; cost if wrong: one more round trip to read the reason.
13. Ruling: her words lose a CR before each LF and the whitespace around them, and nothing else; why: browsers send a text area's line ends as CRLF, and `write_record` refuses a reasoning that does not read back unchanged (`src/lodge/core/fileformat.py:41`), while parsing trims a body's ends (`src/lodge/core/document.py:47`); cost if wrong: a trailing space she typed is not kept.
14. Ruling: `Store.commit` runs only for viewer writes after a publish returned `STAGED`; command-line thread writes stage like `add`; `BranchStore.commit` raises, since its `publish` already commits; why: design line 68 names viewer writes, and line 72 says branch mode commits on publish; cost if wrong: an agent's thread write sits staged until its own commit, as an `add` does today.
15. Ruling: the commit runs the checkout's own hooks (no `--no-verify`), and any other git failure leaves the files staged with the notice "git could not commit"; why: the commit takes the checkout's own identity (design line 66), and its hooks are the checkout's rules as much; cost if wrong: a slow hook delays the redirect.
16. Ruling: a confirmation's commit message names the new author decision ("Author confirmation from the viewer: d-new"), and thread commits read "Thread q-x: doubt raised by author", "Thread q-x: question asked by author", "Thread q-x: author reply", and "Thread q-x: closed by author", with the writer's role in place of `author` from the command line in branch mode; why: design line 68 gives the forms, and the commit adds that record; cost if wrong: commit messages.
17. Ruling: a `POST` body is at most 65,536 bytes of `application/x-www-form-urlencoded`; why: no form carries more than one message, and the reasoning guidance is 1,000 words (`lodge show s-fehz74`); cost if wrong: a very long message is refused with 413.
18. Ruling: `Lodge.waiting()` keeps its result, and a new `Lodge.threads_waiting()` gives the two thread groups; why: every caller of `waiting()` stays green between tasks (`src/lodge/cli/commands.py`, `src/lodge/viewer/server.py`); cost if wrong: two calls where one would do.
19. Ruling: the six quotes of the design's Intent not yet recorded (lines 13 to 18; lines 12 and 19 are d-dyrpc6 and d-2hcgav) become six author decisions with `where: "lodge build session"` and each its own minute on 2026-10-30: line 18 at 09:37, lines 13 and 14 at 09:41, line 15 at 09:43, line 16 at 09:46, line 17 at 09:47; why: the coordinator read the minutes from the session (fix round 1), the design gives only a range (design line 10), and check 3 needs a `when` (`src/lodge/core/check_state.py:111`); cost if wrong: an author decision is immutable, so a wrong minute needs her replacement.
20. Ruling: a role that contains "author" without being `author` is refused for thread messages by the app, as check 3 refuses it for decisions (`src/lodge/core/check_state.py:111`); why: must-not 2 of the design; cost if wrong: one refusal message.
21. Ruling: records tasks run `lodge add` with a temporary index (Global Constraints), and when that fails the coordinator runs the adds from the builder's drafts; why: the index is read-only in the sandbox (`task-5-report.md:125-127`); cost if wrong: the coordinator does one task's adds.
22. Ruling: fourteen tasks under eleven numbers: Tasks 6 and 9 are split into 6a and 6b, and 9a, 9b, and 9c, the numbers kept so the reviews' handles hold; why: the confirmation and the write gate are two reviews, the second the security one, and the design's records are too much judgement for one review (`plan-review-practice.md`, I6 and I7); cost if wrong: more coordinator rounds.
23. Ruling: one lock in `viewer/writes.py` serialises the viewer's writes; why: the server answers in threads (`src/lodge/viewer/server.py:21`), and a checkout publish rejects only a changed path (`src/lodge/gitstore/checkout.py:48-63`), so two confirmations sent at once would both write (`plan-review-correctness.md`, I2); cost if wrong: writes wait on each other, at the pace of one person.
24. Ruling: a doubt sent twice opens two threads; why: nothing makes the second one stale, and a duplicate thread is visible and closable (correctness I2, its thread part, declined); cost if wrong: one thread to close by hand.
25. Ruling: the viewer does not commit during a revert or a sequencer run either, beside the design's merge, rebase, and cherry-pick (design line 69); why: `git commit --only` during a conflicted revert concludes it (correctness I3, run on git 2.56.0); cost if wrong: a write staged during a revert.
26. Ruling: Tasks 3, 4, and 8 stay whole; why: their parts share one data type each and fewer review questions than Tasks 6 and 9, and fourteen tasks already pass the brief's ten (practice I8 and I9, declined); Task 8 gains a baseline of `lodge waiting`; cost if wrong: a rejected task is redone whole.
27. Ruling: check 3 does not extend to thread messages; why: design line 100 gives a thread checks 1, 2, and 5 only, the app refuses such a role (Call 20), and the hook advises against a hand edit (Task 5) (correctness M8, declined); cost if wrong: a hand-written `by: The Author` message passes the gate.
28. Ruling: `lodge draft q-…` needs no new refusal; why: `resolve` looks only at decisions and entries (`src/lodge/core/search.py:36-45`), so it already exits 2 with "no record named q-…" (practice M5, declined); cost if wrong: a message that does not name the thread commands.
29. Ruling: these calls stay in the plan, not the ledger; why: they are the planner's rulings on the plan, and since every task repeats what it uses, no brief carries them (practice M1, declined); cost if wrong: plan length.
30. Ruling: Task 11 stays apart from Task 10; why: one is records, the other prose (practice M10, declined); cost if wrong: one more coordinator round.
31. Ruling (d-a3h9f3, the advisor's, on correctness I13): a close without text appends a closing message with an empty text, by the closer, for every role, and reads head it "closed by BY"; no read and no file shows "Closed." as a message's text; why: the "Closed." default was the advisor's addition (design line 85), and a `by: author` message reading "Closed." is text in her name she never gave (LODGE-8, d-9vxkjw; design lines 45 and 81); cost if wrong: the thread file format before any thread is published.
32. Ruling (d-a3h9f3, the advisor's, on the s-7ah5n7 part of correctness I11): a thread is not a kind of project knowledge in s-7ah5n7's sense, and Task 9b adds one sentence saying so to that entry without waiting for the author; why: she asked for threads herself (design line 13), a thread holds no claim of its own, and what it settles enters lodge as a decision; cost if wrong: one decision undoes the edit.

## Review Focus

1. A form sent twice, by a double click or a reload: the second confirmation finds the list stale and writes nothing, even when both arrive at once, and a reload after the redirect sends nothing (tests in Tasks 6a and 6b).
2. Her words holding what YAML, Markdown, or HTML would mangle (a colon, quotes, `#`, `<script>`, a line `## Reasoning`, CRLF, a character a header cannot carry such as U+0000): recorded verbatim apart from the CR rule, or refused with one sentence and status 400, never a 500 (tests in Tasks 3, 6a, and 6b).
3. A viewer started by the author on `main`, on a detached HEAD, or during a rebase or revert: the write is staged, not committed, and the page says why (tests in Tasks 4 and 6b).
4. One add that makes a cycle across two drafts, or newly rests an entry on one it retires in the same add: check 8 or check 6 refuses with a sentence naming the entries (test in Task 2).
5. A malformed write: no `Content-Length`, a negative one, a body over the limit, a body that is not UTF-8, a bad percent escape, two `token` fields, a non-ASCII token, a `kind` that is neither doubt nor question: a 4xx answer, nothing written, and the server keeps serving (tests in Task 6b).

---

### Task 1: Area rank, the `rests_on` field, and the derived order

**Files:**
- Modify: `src/lodge/core/model.py`, `src/lodge/core/fields.py`, `src/lodge/core/headers.py`, `src/lodge/core/fileformat.py`, `src/lodge/core/render.py`, `src/lodge/core/feedback.py`, `src/lodge/core/check_change.py` (`_area_notes`), `src/lodge/core/__init__.py`, `src/lodge/app/writes.py` (at most 4 lines), `src/lodge/cli/parser.py` (the `spec` help line)
- Create: `src/lodge/core/order.py`
- Test: `tests/core/test_order.py` (new), `tests/core/test_fileformat_links.py` (new), `tests/core/test_area_feedback.py` (new), `tests/core/test_render.py`, `tests/core/test_check_change.py`, `tests/app/test_writes.py`

**Interfaces:**
- Consumes: `Snapshot`, `Derived`, `level1`, `Feedback` as they are.
- Produces:
  ```python
  # model.py, each the last field
  Area.rank: int | None = None
  SpecEntry.rests_on: tuple[str, ...] = ()
  # fields.py
  def read_rank(value: object) -> int    # a str matching 0|[1-9][0-9]*, as int; else FormatError key "rank"
  # order.py
  @dataclass(frozen=True) class Placement: id: str; depth: int; under: str | None
  def area_names(s: Snapshot) -> tuple[str, ...]      # ranked by (rank, name), then unranked by name
  def written_order(s: Snapshot, d: Derived, area: str) -> tuple[str, ...]
  def derived_order(s: Snapshot, d: Derived, area: str) -> tuple[Placement, ...]
  # render.py
  @dataclass(frozen=True) class Placed:
      entry: Level1; depth: int; under: str | None
      also: tuple[str, ...]                    # same-area current targets other than under, in rests_on order
      across: tuple[tuple[str, str], ...]      # (target, its area)
  SpecArea(name, title, intro, entries: tuple[Level1, ...], placed: tuple[Placed, ...])
  # feedback.py
  def area_feedback(after: Snapshot, written_paths: Collection[str]) -> list[Feedback]
  ```
- The YAML loader gives every scalar as text (`src/lodge/core/yamlio.py:28-31`), so `rank: 2` and `rank: "2"` both read as 2, and `-1`, `1.5`, `true`, `two`, `01`, and an empty string are refused.
- Values: `SPEC_KEYS` gains `rests_on` (entry IDs, read with the `s` prefix), `AREA_KEYS` gains `rank`; `_spec_header` writes `rests_on: [s-a, s-b]` after `title` when non-empty; `write_area` writes `rank: N` after `title` when set; a file without them reads and writes as today.
- `written_order` is today's `render._area` order: the area's `order` filtered to current entries, then the other current entries of the folder by ID.
- `derived_order` is depth first (d-a3h9f3): at the top it places the first unplaced entry in the written order whose current same-area `rests_on` targets are all placed, or on a cycle the first unplaced one, at depth 0, `under` None.
  After placing an entry it places at once, again and again, at that entry's depth plus 1 and `under` it, the first unplaced entry in written order whose same-area current targets are now all placed and include it, each followed in the same way before the next is sought; then the top-level search goes on.
  So `under` is the last of an entry's same-area current targets to be placed, every indented entry sits under one it rests on, and siblings and roots keep the written order; it never raises on a cycle.
- `spec_view` lists areas in `area_names` order and fills `placed` in derived order, `also` holding the entry's same-area current targets other than `under`, in `rests_on` order, `across` holding each `rests_on` target that is an entry of another area, with that area; `render_spec` prints each area's entries in derived order, each followed, after its statement, by one line `rests on s-xxxxxx (area)` per `across` pair.
- `area_feedback`: for each area whose `_area.md` path is in `written_paths` and whose rank another area of `after` shares, `Feedback(f"area:{name}", f"rank {rank} is shared with area {others}; areas that share a rank are ordered by name")`, `others` joined as "a", "a and b", or "a, b, and c"; `app/writes.py` `_attempt` appends it to the add's feedback with `files.keys()` as `written_paths`.
- `_area_notes` adds `rank` to the fields it compares: `area storage: rank changed`.
- The `spec` help reads "print the readable specification: areas by rank, entries after what they rest on".
- `Placed.depth`, `Placed.under`, and `Placed.also` are read by `test_render.py` until Task 7 shows them.

- [ ] **Step 1: Write the failing tests.**
  - `test_order.py`: `test_ranked_areas_first_then_by_name` (ranks b=2, a=1, z and c unranked: `area_names(s) == ("a", "b", "c", "z")`); `test_shared_rank_ordered_by_name` (`("w", "x")` for w=1, x=1); `test_folder_without_area_file_sorts_with_unranked`; `test_entry_after_what_it_rests_on` (order a, b, c with a resting on c: ids `("s-b…", "s-c…", "s-a…")`); `test_no_links_keeps_written_order`; `test_under_is_the_target_placed_last` (written a, b, d, with d resting on a and b: order a, b, d; d `under` b at depth 1, `also == (a,)`); `test_dependant_follows_what_it_rests_on` (written a, b, c, with c resting on a: order a, c, b; c at depth 1 under a, b at depth 0); `test_cycle_falls_back_to_written_order` (a and b rest on each other: order a, b, no exception); `test_retired_target_does_not_hold_an_entry_back`.
  - `test_fileformat_links.py`: `test_rests_on_round_trips`; `test_rank_round_trips`; `test_rank_reads_quoted_and_plain_alike` (`rank: 2` and `rank: "2"` both 2); `test_rank_must_be_a_whole_number` (`-1`, `1.5`, `true`, `two`, `01`, and `""` each a problem with key `rank`); `test_rests_on_holds_entry_ids_only` (`[d-3m8qk2]` is problem 1); `test_area_without_rank_writes_as_before` (the existing text, byte for byte).
  - `test_render.py`: `test_render_spec_follows_rank_then_derived_order`; `test_render_spec_lists_cross_area_targets` (a line `rests on s-xxxxxx (other)` after the statement); `test_spec_view_places_with_depth_under_and_also`; `test_cross_area_target_is_across_not_also` (c rests on x in another area and on a: `under == a`, `also == ()`, `across == (("s-x…", "other"),)`).
  - `test_area_feedback.py`: `test_shared_rank_feedback` (exact message above); `test_unshared_rank_no_feedback`; `test_unwritten_area_no_feedback`.
  - `test_check_change.py`: `test_area_rank_change_is_note` (`"area storage: rank changed" in result.notes`).
  - `tests/app/test_writes.py`: `test_add_area_sharing_a_rank_gives_feedback` (`Feedback("area:storage", …)` in `added.feedback`, outcome not `CHECK_FAILED`).
- [ ] **Step 2: Run** `uv run pytest tests/core/test_order.py tests/core/test_fileformat_links.py tests/core/test_area_feedback.py tests/core/test_render.py tests/core/test_check_change.py tests/app/test_writes.py -q`; expected: the new tests FAIL.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the builder's gate; expected: green, and `uv run lodge spec` prints this repository's areas alphabetically and each area's entries in the same order as before (no area has a rank and no entry `rests_on` yet).
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, then commit the files above and push.

### Task 2: The `link` action, the checks on `rests_on`, check 8, and what reads derive

**Files:**
- Modify: `src/lodge/core/model.py`, `src/lodge/core/derive.py` (at most 15 lines), `src/lodge/core/check_state.py`, `src/lodge/core/check_entries.py`, `src/lodge/core/check_change.py` (`_links_to_dead`), `src/lodge/core/views.py` (at most 30 lines), `src/lodge/core/feedback.py`, `src/lodge/core/__init__.py`, `src/lodge/cli/guide.md`
- Create: `src/lodge/core/check_cycles.py`
- Test: `tests/core/test_check_links.py` (new), `tests/core/test_derive_links.py` (new), `tests/core/test_views_links.py` (new), `tests/core/test_feedback_links.py` (new), `tests/app/test_writes.py`, `tests/e2e/test_guide.py`

**Interfaces:**
- Consumes: Task 1's `SpecEntry.rests_on`.
- Produces:
  ```python
  Action.LINK = "link"
  Derived.linked_by: Links      # entry -> decisions whose change on it is link, newest first
  Derived.supports: Links       # entry -> entries listing it in rests_on, by ID; known entries only
  def check_cycles(s: Snapshot) -> Iterator[Problem]     # check 8, run by check_state
  ```
- `derive`: an entry counts in a decision's `touches` (so in `changed_by`, the review flag, and revivals) only when that decision has a change on it other than `link`; a `link` change is listed in `linked_by` instead, so it never becomes who decided an entry, never raises a flag, and is never an entry's last change (design line 107).
- Check 4 (`check_entries`): an entry whose only difference from its published self is `rests_on` needs a new decision listing it with `edit` or `link`, else `edited, but no new decision in this change lists it with action edit or link; list it in the decision's changes`; a new decision listing `link` for an entry that differs in anything else is `{d}: lists link for {entry}, which changes more than rests_on; list it with action edit`, and for an entry not yet published `{d}: lists link for {entry}, which is new; list it with action create`.
- Check 2 (`_unresolved`): per entry, `{e}: rests_on itself`, and `{e}: rests_on {t}, which does not exist`.
- Check 8: an entry is in a cycle when it reaches itself through one or more `rests_on` links; one problem per member, at its path: `{e}: is in a cycle of rests_on links with {others}`, `others` the other members of its cycle, sorted, joined with ", ".
- Check 6: an entry of `after` that is new or whose `rests_on` changed, for each target not in its published `rests_on` that is retired in `after`: `{e}: rests on {t}, which is retired`.
- Level 1, on an entry, after the "awaiting the author" flags and before "imported": per target of its own `rests_on` (one link deep), `rests on {t}, retired` when retired, else `rests on {t}, changed since` when the target's newest `changed_by` decision orders after the entry's own, by `(datetime.fromisoformat(date), id)`; nothing when either has no change or the target does not resolve.
- Level 3 of an entry, after `changed by`: `("rests on", t, status)` per own target, `("supports", x, status)` per `supports`, `("linked by", d, status)` per `linked_by`.
- Feedback on a written entry, per entry ID its statement names (`\bs-[0-9a-hjkmnp-tv-z]{6}\b`, first appearance order) that exists, is not itself, and is not in `rests_on`: `the statement names {t}, but rests_on does not list it; does {e} rest on {t}? If so, add it to rests_on`.
- `guide.md` gains under Writing: "An entry lists the entries it would not hold without in `rests_on: [s-…]`; a decision that changes only `rests_on` lists the entry with action `link`." and "When an entry still holds after an entry it rests on changed, say so with a decision that lists it with `edit`, its text unchanged, and why in the reasoning."

- [ ] **Step 1: Write the failing tests.**
  - `test_check_links.py`: `test_link_changing_rests_on_only_passes`; `test_rests_on_change_without_decision_fails_check_4` (message above); `test_edit_may_change_rests_on`; `test_link_changing_the_statement_fails_check_4`; `test_link_for_a_new_entry_fails_check_4`; `test_unknown_rests_on_fails_check_2` (`which does not exist`); `test_rests_on_itself_fails_check_2`; `test_two_entry_cycle_fails_check_8_on_both` (two problems, check 8, `s-a: is in a cycle of rests_on links with s-b` and the reverse); `test_three_entry_cycle_names_the_other_two`; `test_new_rest_on_retired_entry_fails_check_6`; `test_kept_rest_on_retired_entry_passes_check_6`.
  - `tests/app/test_writes.py` (Review Focus 4): `test_cycle_made_in_one_add_is_refused` (two entry drafts resting on each other, one decision linking both: outcome `CHECK_FAILED`, a check 8 problem per entry, `store.publishes == []`); `test_rest_on_entry_retired_in_the_same_add_is_refused` (check 6).
  - `test_derive_links.py`: `test_link_is_not_a_change` (`changed_by` lacks the link decision, `linked_by` has it); `test_link_raises_no_flag` (author created the entry, an agent links it: not in `awaiting_author`); `test_supports_is_the_reverse_of_rests_on`.
  - `test_views_links.py`: `test_rests_on_retired_mark`; `test_rests_on_changed_since_mark`; `test_edit_with_unchanged_text_clears_changed_since`; `test_link_after_the_change_keeps_changed_since`; `test_entry_level1_keeps_the_author_after_a_link` (`decided_by == "author"`); `test_level3_lists_rests_on_supports_and_linked_by`.
  - `test_feedback_links.py`: `test_statement_naming_an_unlisted_entry_asks`; `test_listed_named_entry_no_feedback`; `test_own_id_no_feedback`.
  - `tests/e2e/test_guide.py`: `test_guide_names_rests_on_and_link` (`"rests_on" in out and "action `link`" in out`).
- [ ] **Step 2: Run** `uv run pytest tests/core tests/app/test_writes.py tests/e2e/test_guide.py -q`; expected: the new tests FAIL.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the builder's gate; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 3: Threads in core

**Files:**
- Modify: `src/lodge/core/model.py`, `src/lodge/core/ids.py`, `src/lodge/core/fields.py` (`read_stamp`; `ID_KIND` gains `"q": "thread"`), `src/lodge/core/snapshot.py`, `src/lodge/core/derive.py` (at most 6 lines), `src/lodge/core/check_state.py`, `src/lodge/core/check_change.py` (`_missing`), `src/lodge/core/check_immutable.py`, `src/lodge/core/views.py` (at most 12 lines), `src/lodge/core/feedback.py` (its `_ID` takes `q`), `src/lodge/core/__init__.py`, `tests/core/builders.py` (`thread(**kw)`, `message(**kw)`; `files_of` and `snapshot_of` take threads)
- Create: `src/lodge/core/threads.py`, `src/lodge/core/doubts.py`
- Test: `tests/core/test_thread_files.py` (new), `tests/core/test_check_threads.py` (new), `tests/core/test_doubts.py` (new)

**Interfaces:**
- Consumes: Task 2's `Derived.changed_by` without links, `rests_on`.
- Produces:
  ```python
  class Raises(StrEnum): DOUBT = "doubt"; QUESTION = "question"
  class ThreadState(StrEnum): OPEN = "open"; CLOSED = "closed"
  @dataclass(frozen=True) class Message: by: str; when: str; text: str; where: str | None = None
  @dataclass(frozen=True) class Thread:
      id: str; about: str; raises: Raises; state: ThreadState; opened: str; messages: tuple[Message, ...]
  def mint_id(prefix: Literal["d", "s", "q"], entropy: bytes) -> str   # is_id accepts q- too
  def read_stamp(value: object, key: str) -> str      # ISO 8601 with seconds and offset, as read_date
  THREADS = "lodge/threads/"
  def thread_path(thread_id: str) -> str              # f"lodge/threads/{thread_id}.md"
  def parse_thread(path: str, text: str) -> Thread | Problem
  def write_thread(thread: Thread) -> str             # ValueError when it would not read back unchanged
  def appended(thread: Thread, message: Message, close: bool = False) -> Thread
      # ValueError if the thread is closed, or if the text is empty and close is False
  def newest_last(threads: Iterable[Thread]) -> tuple[Thread, ...]   # by (datetime of opened, id)
  Snapshot.threads: Mapping[str, Thread] = field(default_factory=dict)  # paths hold thread paths too
  def doubt_marks(s: Snapshot, changed_by: Links) -> dict[str, tuple[str, ...]]
  Derived.doubts: Mapping[str, tuple[str, ...]]
  ```
- File shape: the header holds the record; the messages are the body, as design line 78 asks; `opened` is the time lodge wrote the first message, so threads sort newest last although an author's `when` is free text:
  ```
  ---
  id: q-4kq1zm
  kind: thread
  about: s-0abcde
  raises: doubt
  state: open
  opened: 2026-10-29T09:30:00+01:00
  ---

  ## Message 1

  by: author
  when: "2026-10-29 09:30"
  where: "lodge viewer"

  Is this still true?

  ## Message 2

  by: coordinator
  when: 2026-10-29T10:00:00+01:00

  It is; see d-3m8qk2.
  ```
- Writing: `opened` and an agent's `when` are written plain, as a decision's `date` is; `by` plain when it matches `[A-Za-z0-9][A-Za-z0-9._-]*`, else with `yamlio.quoted`; an author's `when` and `where` with `yamlio.quoted`; the text through `trim_block`.
- Reading: a line exactly `## Message <n>` starts message `n`; the lines up to the first blank line are its YAML block; the rest up to the next heading is its text.
- The escape: on write, a text line matching `^\\*## Message [0-9]+$` gets one more leading backslash; on read, a line matching `^\\+## Message [0-9]+$` loses one; so every text reads back exactly.
- Check 1 (a parse problem, with the key where one applies): unknown header or message key; a malformed `id` (`q-BAD`); `about` not a `d-` or `s-` ID (`about must name a decision or a specification entry`); `raises` or `state` outside its values; `opened` not a stamp; no message (`a thread needs at least one message`); a message heading out of sequence (`messages are numbered 1, 2, 3, in order`); text before `## Message 1`; a message without `by` or `when`; an author message without `where` (`an author message needs where`); an empty message text, except on the last message of a closed thread (its closing message, d-a3h9f3); the file name not starting with the ID; a file in a folder under `lodge/threads/` (stray).
- Check 2: `{q}: about {t}, which does not exist`; a duplicate thread ID as for records; a published thread missing from `after` (`_missing`).
- Check 5 (`check_immutable`), comparing a published thread with its `after` self: `{q}: about of a published thread was changed`; `{q}: raises of a published thread was changed`; `{q}: opened of a published thread was changed`; `{q}: a published message was changed or removed; messages are only appended`; `{q}: a closed thread was opened again`; `{q}: a message was added after the thread was closed`; `{q}: a thread was closed without a closing message` when the published thread is open, the one in `after` is closed, and it has no message the published one lacks.
- An open thread fails no check.
- `doubt_marks`, per record: `in doubt` when an open doubt is about it; `question open` when an open question is; on an entry, `changed by {d}, in doubt` per doubted decision that lists it with `create` or is its `changed_by[0]`, by ID; on an entry, `rests on {y}, in doubt` per entry `y` reached through one or more `rests_on` links (cycle-safe) that is itself in doubt or changed by a doubted decision, by ID; questions never propagate.
- Level 1 flags, after the "awaiting the author" flags and before Task 2's rests-on flags: `confirmed by the author ({ids})` on a decision in `d.confirmed_by`, the confirming IDs joined with ", ", then the `d.doubts` marks in the order above.

- [ ] **Step 1: Write the failing tests.**
  - `test_thread_files.py`: `test_thread_round_trips` (multi-line text, an agent and an author message, and a closed thread whose closing message has no text); `test_empty_text_only_on_the_closing_message` (an empty text on an earlier message, or on the last message of an open thread, is problem 1); `test_written_shape_matches_the_example` (the example above, byte for byte); `test_text_line_like_a_heading_round_trips` (texts `## Message 2` and `\## Message 2` read back exact); `test_yaml_and_markdown_specials_round_trip` (Review Focus 2: `a: "b" # c`, `<script>`, `## Reasoning`); `test_author_message_needs_where`; `test_malformed_id_is_problem_1` (`id: q-BAD`, no exception); `test_about_must_name_a_decision_or_entry` (`q-…` is problem 1); `test_thread_needs_a_message`; `test_messages_numbered_in_order`; `test_body_text_before_first_message_refused`; `test_appended_refuses_a_closed_thread`; `test_newest_last_by_opened_then_id`; `test_load_reads_threads_and_their_paths`; `test_nested_file_under_threads_is_stray`.
  - `test_check_threads.py`: `test_open_thread_passes_every_check`; `test_unresolved_about_fails_check_2`; `test_duplicate_thread_id_fails_check_2`; `test_file_name_must_start_with_the_id`; `test_appending_a_message_passes`; `test_closing_passes`; `test_editing_a_published_message_fails_check_5`; `test_removing_a_message_fails_check_5`; `test_changing_about_fails_check_5`; `test_changing_raises_fails_check_5`; `test_reopening_fails_check_5`; `test_message_after_closing_fails_check_5`; `test_closing_without_a_message_fails_check_5`; `test_missing_published_thread_fails_check_2`.
  - `test_doubts.py`: `test_open_doubt_marks_its_record`; `test_closed_doubt_marks_nothing`; `test_question_open_mark_and_no_propagation`; `test_doubt_reaches_entries_resting_on_it_further_down` (c rests on b rests on a, doubt on a: `"rests on s-a…, in doubt"` on b and c); `test_doubt_on_decision_marks_entries_it_created_and_last_changed`; `test_doubt_on_decision_reaches_what_rests_on_its_entries`; `test_cycle_of_rests_on_does_not_hang`; `test_confirmed_decision_shows_confirmation_and_keeps_decided_by` (`"confirmed by the author (d-bbbbbb)" in flags`, `decided_by == "coordinator"`); `test_flag_order` (one entry with `awaiting the author on …`, `in doubt`, `rests on …, retired`, `imported`, in that order).
- [ ] **Step 2: Run** `uv run pytest tests/core -q`; expected: the new tests FAIL.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the builder's gate; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 4: Thread operations, and the store's commit

**Files:**
- Modify: `src/lodge/app/ports.py`, `src/lodge/app/results.py`, `src/lodge/app/lodge.py`, `src/lodge/app/reads.py` (`show` fills `threads`), `src/lodge/app/writes.py` (`_mint` renamed `mint_unused`; `Added.paths` filled), `src/lodge/app/__init__.py`, `src/lodge/gitstore/checkout.py` (at most 8 lines), `src/lodge/gitstore/branch.py`, `src/lodge/gitstore/setup.py`, `tests/app/fakes.py`, `tests/gitstore/test_concurrent.py` (`Interleaved.commit` delegates to `inner.commit`)
- Create: `src/lodge/app/threads.py`, `src/lodge/gitstore/commit.py`
- Test: `tests/app/test_thread_ops.py` (new), `tests/gitstore/test_commit.py` (new)

**Interfaces:**
- Consumes: Task 3's `Thread`, `Message`, `Raises`, `thread_path`, `write_thread`, `appended`, `clean_text`, `newest_last`, `Snapshot.threads`.
- Produces:
  ```python
  # ports.py
  class CommitOutcome(StrEnum):
      COMMITTED = "committed"; ON_BASE = "on the base branch"; DETACHED = "on a detached HEAD"
      IN_PROGRESS = "during a merge, rebase, cherry-pick, or revert"
      LOCKED = "git's index is locked by another process"; FAILED = "git could not commit"
  @dataclass(frozen=True) class Committed: outcome: CommitOutcome; detail: str = ""
  Store.commit(self, paths: Sequence[str], message: str) -> Committed
  # results.py
  @dataclass(frozen=True) class Written:
      ids: tuple[str, ...]; outcome: AddOutcome; check: CheckResult
      committed: Committed | None = None; about: str | None = None
  @dataclass(frozen=True) class ThreadList: items: tuple[Thread, ...]; titles: Mapping[str, str]; read: Read
  @dataclass(frozen=True) class ThreadShown: thread: Thread; about: Level1; read: Read
  @dataclass(frozen=True) class ThreadsWaiting:
      for_agent: tuple[Thread, ...]; for_author: tuple[Thread, ...]; titles: Mapping[str, str]; read: Read
  Added.paths: tuple[str, ...] = ()          # the files written, set when published or staged
  Shown.threads: tuple[Thread, ...] = ()     # the record's threads, newest last
  # lodge.py
  def ask(self, ref: str, raises: Raises, by: str, text: str, where: str | None = None,
          when: str | None = None, commit: bool = False) -> Written
  def reply(self, thread: str, by: str, text: str, where: str | None = None,
            when: str | None = None, commit: bool = False) -> Written
  def close(self, thread: str, by: str, text: str | None = None, where: str | None = None,
            when: str | None = None, commit: bool = False) -> Written
  def threads(self) -> ThreadList                  # open threads, newest last
  def thread(self, ref: str) -> ThreadShown        # a thread ID in any case; NotFound "no thread named X"
  def threads_waiting(self) -> ThreadsWaiting      # open; last message by author -> for_agent, else for_author
  # writes.py
  def mint_unused(ids: IdSource, prefix: Literal["d", "s", "q"], taken: Collection[str]) -> str
  # gitstore/commit.py
  def commit_paths(root: Path, base: str, paths: Sequence[str], message: str,
                   retry_seconds: float, sleep: Callable[[float], None] = time.sleep) -> Committed
  CheckoutStore(root, settings, common_dir, lock_wait_seconds, index_retry_seconds: float = 1.0)
  ```
- `titles` maps each thread's `about` ID to that record's title; `Written.about` is the thread's `about` for a thread write and None otherwise.
- Rules in `app/threads.py`, each refusal a `LodgeError` naming the fault:
  - the text follows the Global Constraints' CR rule and, for `ask` and `reply`, must not be empty (`the message is empty`);
  - `by` must be non-empty, and a `by` other than `author` holding "author" in any case is refused (`write author exactly, or use your own role`);
  - an author message needs `where` (`a message by author needs where, the place of the author's words`) and takes `when` from the clock's minute (`%Y-%m-%d %H:%M`) when none is given;
  - an agent message takes `when` from the clock (`isoformat(timespec="seconds")`) and may not carry `where` or `when` (`where and when are for messages by author`);
  - a `where`, `when`, or text that a header cannot carry (`write_thread` raises `ValueError`) is refused naming the field;
  - `ask` resolves `ref` with `resolve_ref` (an ID or a code), mints a `q-` ID with `mint_unused`, and stamps `opened` from the clock;
  - `reply` and `close` refuse a closed thread (`{q} is closed`); `close` takes the given text, cleaned the same way, or an empty text when none is given or the cleaned text is empty, appends it by the closer as the closing message, and sets `closed` (d-a3h9f3).
- Each write reads the state, builds the thread file, and runs `core.check_change(load(published), after, settings, now, snapshot)`; a failing check returns `Written(…, AddOutcome.CHECK_FAILED, check)` and writes nothing.
  Otherwise it calls `store.publish(current, {path: text}, message)`, starting again on `REJECTED`, at most three times, then `Conflict`; on `STAGED` with `commit=True` it calls `store.commit((path,), message)`; the command line never passes `commit=True`.
- Commit and publish messages, `ROLE` being `by`: `Thread {q}: doubt raised by ROLE`, `Thread {q}: question asked by ROLE`, `Thread {q}: ROLE reply`, `Thread {q}: closed by ROLE`.
- `commit_paths`, in order: `git symbolic-ref --quiet --short HEAD` failing is `DETACHED`; the branch equal to `base` is `ON_BASE`; any of `git rev-parse --git-path` `MERGE_HEAD`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`, `rebase-merge`, `rebase-apply`, or `sequencer` existing is `IN_PROGRESS`; then `git commit --only --quiet -m MESSAGE -- PATHS`, with no identity of its own and no `--no-verify`, so the checkout's identity and hooks apply; stderr naming `index.lock` sleeps `retry_seconds` and tries once more, then `LOCKED`; any other failure is `FAILED` with git's first line as `detail`.
- `BranchStore.commit` raises `LodgeError("branch mode commits when it publishes")`; `MemoryStore` gains `commits: list[tuple[tuple[str, ...], str]]` and `commit_result: Committed`, default `Committed(CommitOutcome.COMMITTED)`.

- [ ] **Step 1: Write the failing tests.**
  - `test_thread_ops.py`: `test_ask_writes_a_thread_file` (one publish at `lodge/threads/q-111111.md`, read back: `about == "s-aaaaaa"`, `raises is Raises.DOUBT`, open, one message by `coordinator` at `START.isoformat(timespec="seconds")`, `written.about == "s-aaaaaa"`); `test_ask_resolves_a_code`; `test_ask_on_an_unknown_ref_is_not_found`; `test_author_message_needs_where`; `test_author_when_defaults_to_the_minute` (`"2026-10-29 09:30"`); `test_agent_message_may_not_carry_where`; `test_role_like_author_refused` (`"Author"`, `"the author"`); `test_empty_text_refused`; `test_text_loses_cr_and_outer_whitespace_only`; `test_unstorable_where_refused` (`"a\x01"`: `LodgeError`, nothing published); `test_reply_appends`; `test_reply_to_closed_thread_refused`; `test_close_appends_closed_by_the_closer` (the closing message's `text == ""`, its `by` the closer); `test_close_without_text_passes_the_check`; `test_close_with_text`; `test_rejected_publish_starts_again`; `test_commit_after_staged_when_asked` (author, `where="a session"`: `store.commits == [(("lodge/threads/q-111111.md",), "Thread q-111111: doubt raised by author")]`, `written.committed.detail == ""`); `test_no_commit_unless_asked`; `test_no_commit_when_published`; `test_threads_lists_open_newest_last` (`titles["s-aaaaaa"] == "Transcripts are kept"`, `read.freshness` set); `test_thread_shows_one_thread` (`shown.read.freshness` set); `test_threads_waiting_groups` (and its `titles` and `read`); `test_show_carries_the_records_threads`; `test_added_paths_lists_the_files_written`; `test_search_and_timeline_leave_threads_out`.
  - `test_commit.py` (a work branch in a `tmp_path` repository): `test_commits_only_the_named_paths` (another staged file stays staged: `git diff --cached --name-only` lists it alone); `test_commit_takes_the_checkouts_identity` (author is the repository's configured name); `test_no_commit_on_the_base_branch` (`ON_BASE`, the file still staged, `HEAD` unchanged); `test_no_commit_on_a_detached_head`; `test_no_commit_during_a_merge` (a real conflicting merge); `test_no_commit_during_a_revert` (a real conflicting revert; `REVERT_HEAD` still there after); `test_no_commit_during_a_rebase` (a `rebase-merge` folder at its git path); `test_no_commit_during_a_cherry_pick`; `test_locked_index_retries_once_then_locked` (`index.lock` present, `sleep` recorded once); `test_lock_gone_on_retry_commits` (the `sleep` given removes the lock); `test_other_failure_is_failed_with_gits_line`.
- [ ] **Step 2: Run** `uv run pytest tests/app/test_thread_ops.py tests/gitstore/test_commit.py -q`; expected: FAIL.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the builder's gate; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 5: Thread commands, `waiting` in two groups, and the guide

**Files:**
- Modify: `src/lodge/cli/parser.py` (at most 12 lines: the import, the `Command` union, one call, the `waiting` help), `src/lodge/cli/commands.py` (`_read` moves out), `src/lodge/cli/output.py`, `src/lodge/cli/guide.md`, `src/lodge/hook/post_tool_use.py`, `tests/hook/test_post_tool_use.py`
- Create: `src/lodge/cli/threads.py` (the five commands' dataclasses, `add_thread_commands`, `run_thread`), `src/lodge/cli/thread_output.py`, `src/lodge/cli/files.py` (`read_file`, moved from `commands._read`, imported by `commands.py` and `threads.py`, so no import cycle)
- Test: `tests/e2e/test_threads.py` (new), `tests/e2e/test_waiting.py`, `tests/e2e/test_help_lists_every_command.py`, `tests/e2e/test_guide.py`

**Interfaces:**
- Consumes: Task 4's `Lodge.ask`, `reply`, `close`, `threads`, `thread`, `threads_waiting`, `Written`, `ThreadList.titles`, `ThreadsWaiting`.
- Produces: the commands `threads`, `thread REF`, `ask REF --kind {doubt,question} --by ROLE [--where W] [--when T] FILE`, `reply REF --by ROLE [--where W] [--when T] FILE`, `close REF --by ROLE [--where W] [--when T] [FILE]`; and
  ```python
  def read_file(name: str, not_utf8: str, exact: bool) -> str   # cli/files.py, as commands._read was
  def thread_head(t: Thread, title: str) -> str
  def thread_text(shown: ThreadShown) -> str
  def waiting_text(listed: Listed, waiting: ThreadsWaiting) -> str
  ```
- The command line refuses, exit 2: `--by author` without both `--where` and `--when` (`a message by author needs --where and --when, the place and time of the author's words`); `--where` or `--when` with another role (`--where and --when are for messages by author`).
- The message file is read with `read_file`, as drafts are; the command line never asks for a commit.
- Help lines: `threads` "list the open threads: doubts and questions on records"; `thread` "show one thread with its messages"; `ask` "open a thread on a record: a doubt or a question"; `reply` "add a message to an open thread"; `close` "close a thread, with a closing message"; `waiting` "list what waits: for an agent, then for the author".
- `thread_head`: `q-111111 · open · doubt · about s-aaaaaa · 2 messages · last by coordinator`, then the title line; `thread_text`: the head, a blank line, then per message a line `by · when` (with ` · where` when set), the text, and a blank line between messages; the last message of a closed thread gets the line `closed by BY · when` (with ` · where` when set) in place of `by · when`, and its text only when non-empty (d-a3h9f3).
- `waiting_text`: the read lines, then `waiting for an agent`, the heads or `nothing`, a blank line, `waiting for the author`, the level-1 blocks then the heads, or `nothing`.
- A write prints `published q-…` or `staged q-…`, or the check lines and `not published: the check failed` with exit 1; `threads` with none prints `no open threads`.
- The hook: a hand edit under `lodge/threads/` gets `THREAD_TEXT`, "{path} is a lodge thread file, and lodge owns it: do not edit it by hand. Add a message with `lodge reply Q --by ROLE FILE`, or close it with `lodge close Q --by ROLE`. " followed by `REVERSE`, in place of `RECORD_TEXT`, whose `lodge draft` refuses threads; test `test_thread_file_edit_names_reply_and_close`.
- `guide.md` gains under Reading: "Run `lodge waiting` at the start of a session, and answer what waits for an agent first." and "`lodge threads` lists the open doubts and questions, and `lodge thread Q` shows one."; under Writing: "`lodge ask REF --kind doubt|question --by ROLE FILE`, `lodge reply Q --by ROLE FILE`, and `lodge close Q --by ROLE [FILE]` write threads.", "Answer a doubt by acting with a decision whose reasoning names the thread, then reply naming the decision; close a thread only when the author asked for it.", and "Write `--by author` only with the author's words verbatim, with `--where` and `--when`."

- [ ] **Step 1: Write the failing tests.**
  - `test_threads.py`: `test_ask_reply_close_round_trip` (`ask` prints `staged q-…`; `threads` lists it; `reply`; `thread` shows both messages in order; `close` then `threads` prints `no open threads`; `thread` ends with the line `closed by coordinator · …`, and its output holds no "Closed."); `test_author_message_needs_where_and_when_exit_2`; `test_where_with_an_agent_role_exit_2`; `test_ask_on_unknown_ref_exit_2`; `test_thread_files_are_staged_not_committed` (`git diff --cached --name-only` lists `lodge/threads/q-…`, `HEAD` unchanged).
  - `test_waiting.py`: the existing test reads its decision block under `waiting for the author`; `test_waiting_groups_threads` (an author-last thread under `waiting for an agent`, an agent-last one under `waiting for the author`).
  - `test_help_lists_every_command.py`: the five new names.
  - `test_guide.py`: `test_guide_says_waiting_first`.
- [ ] **Step 2: Run** `uv run pytest tests/e2e/test_threads.py tests/e2e/test_waiting.py tests/e2e/test_help_lists_every_command.py tests/e2e/test_guide.py tests/hook/test_post_tool_use.py -q`; expected: FAIL.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the builder's gate; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 6a: The confirmation in core and app

**Files:**
- Modify: `src/lodge/app/errors.py` (`StaleList`), `src/lodge/app/results.py` (`Behind`, `Shown.confirmable`), `src/lodge/app/lodge.py`, `src/lodge/app/reads.py` (`show` fills `confirmable`), `src/lodge/app/__init__.py`, `src/lodge/core/__init__.py`
- Create: `src/lodge/core/confirmation.py`, `src/lodge/app/confirm.py`
- Test: `tests/core/test_confirmation.py` (new), `tests/app/test_confirm.py` (new)

**Interfaces:**
- Consumes: Task 4's `Written`, `Committed`, `Added.paths`, `Store.commit`; Task 3's level-1 confirmation mark.
- Produces:
  ```python
  # core/confirmation.py
  VIEWER = "lodge viewer"
  def confirmable_ids(s: Snapshot, d: Derived) -> frozenset[str]   # agent, current, not in confirmed_by
  def behind_area(s: Snapshot, d: Derived, area: str) -> tuple[str, ...]
  def confirmation_draft(confirms: Sequence[str], scope: Scope, words: str, when: str,
                         area: str | None) -> str                   # ValueError on a character a header cannot carry
  # app
  class StaleList(Conflict)
  @dataclass(frozen=True) class Behind: decision: Level1; entries: tuple[tuple[str, str], ...]  # (entry, area)
  Shown.confirmable: bool = False
  Lodge.confirm(self, ids: Sequence[str], words: str, area: str | None = None, commit: bool = False) -> Written
  Lodge.behind_area(self, name: str) -> tuple[Behind, ...]         # NotFound for an unknown area
  ```
- `behind_area`: the confirmable decisions that list an entry of the area's folder, current or retired, with `create`, or are its `changed_by[0]`, ordered by `(datetime.fromisoformat(date), id)` (design line 51); `Behind.entries` lists every entry the decision's `changes` names that exists, once, in order, with its area.
- `confirmation_draft` (design lines 56 to 61): `kind: decision`, title `Confirms {id}` or `Confirms the decisions behind area {area}`, `scope`, `decided_by: author`, `confirms: [ids]`, `quote: {text: words, where: "lodge viewer", when: when}` with `yamlio.quoted`; body `The author confirms {listed}.` (`d-a`, `d-a and d-b`, or `d-a, d-b, and d-c`), then `## Reasoning`, then the words.
- `confirm`: the words follow the Global Constraints' CR rule, empty refused (`your words are required; nothing was written`); the expected list is `behind_area` for an area, else `(ids[0],)` when exactly one ID was given and it is confirmable; any other set of IDs raises `StaleList("the list changed since the page was loaded; nothing was written")`.
  Scope is `product` when any listed decision is, else `process`; `when` is the clock's minute; a `ValueError` from the draft is a `LodgeError` (`your words hold a character lodge cannot store`).
  The draft goes through `writes.add(w, [(VIEWER, draft)], False, False)`, so it writes only one new decision file; on `STAGED` with `commit=True`, `store.commit(added.paths, f"Author confirmation from the viewer: {added.ids[0]}")`.

- [ ] **Step 1: Write the failing tests.**
  - `test_confirmation.py`: `test_confirmable_ids_skip_author_confirmed_and_replaced`; `test_behind_area_lists_creators_and_last_changers_oldest_first`; `test_behind_area_includes_the_retirer_of_a_retired_entry`; `test_confirmation_draft_single` (parsed with `parse_draft` and `record_from_draft`: title `Confirms d-aaaaaa`, statement `The author confirms d-aaaaaa.`, `reasoning == words`, `quote.where == "lodge viewer"`); `test_confirmation_draft_area_lists_with_the_oxford_comma`.
  - `test_confirm.py`: `test_confirm_one_decision` (one author decision published, `confirms` the agent decision, `quote.when == "2026-10-29 09:30"`); `test_confirm_writes_only_a_new_decision_file` (every published path is under `lodge/decisions/` and absent before); `test_confirmed_decision_keeps_decided_by_and_clears_its_flag`; `test_scope_product_when_any_listed_is_product`; `test_scope_process_when_all_are_process`; `test_area_confirms_exactly_the_listed`; `test_stale_area_list_writes_nothing` (`StaleList`, `store.publishes == []`); `test_second_identical_confirmation_is_stale` (Review Focus 1); `test_words_required`; `test_words_with_specials_kept_verbatim` (Review Focus 2); `test_words_with_unstorable_character_refused` (`"\x00"`: `LodgeError`, nothing published); `test_commit_after_staged` (`store.commits == [((path,), "Author confirmation from the viewer: d-111111")]`); `test_behind_area_lists_entries_in_other_areas`; `test_show_marks_confirmable`.
- [ ] **Step 2: Run** `uv run pytest tests/core/test_confirmation.py tests/app/test_confirm.py -q`; expected: FAIL.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the builder's gate; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 6b: The viewer's write gate

**Files:**
- Modify: `src/lodge/viewer/server.py`, `src/lodge/viewer/html.py` (`page` takes a notice), `src/lodge/viewer/__init__.py` (docstring "The local web viewer"), `src/lodge/cli/parser.py` (`--allow-host` and the `view` help, at most 8 lines), `src/lodge/cli/commands.py`, `src/lodge/main.py`, `tests/viewer/world.py` (`staged_world`), `tests/viewer/test_server.py`, `tests/e2e/test_view.py`
- Create: `src/lodge/viewer/writes.py`
- Test: `tests/viewer/test_post_gate.py` (new), `tests/viewer/test_post_routes.py` (new)

**Interfaces:**
- Consumes: Task 6a's `Lodge.confirm`, `StaleList`; Task 4's `Lodge.ask`, `reply`, `close`, `Written`, `Committed`, `CommitOutcome`.
- Produces:
  ```python
  # viewer/writes.py
  MAX_BODY = 65_536
  NOTICES: Mapping[str, str]
  @dataclass(frozen=True) class Gatekeeper: token: str; hosts: frozenset[str]   # ValueError if len(token) < 32
  @dataclass(frozen=True) class Reply: status: HTTPStatus; text: str; location: str | None = None
  def allowed_hosts(port: int, extra: Sequence[str]) -> frozenset[str]   # lower case
  def done_code(written: Written) -> str
  def refuse_early(gate: Gatekeeper, headers: Mapping[str, str]) -> Reply | None  # the Host and Origin checks
  def handle_post(make_lodge: Callable[[], Lodge], gate: Gatekeeper, path: str,
                  headers: Mapping[str, str], body: bytes) -> Reply      # headers keyed in lower case
  # viewer/server.py
  def make_server(make_lodge: Callable[[], Lodge], port: int, *, token: str,
                  allow_hosts: Sequence[str] = ()) -> ThreadingHTTPServer
  def serve(make_lodge: Callable[[], Lodge], port: int, allow_hosts: Sequence[str], token: str) -> int
  def render(make_lodge: Callable[[], Lodge], url: SplitResult) -> tuple[HTTPStatus, str, str]  # was _render
  # html.py
  def page(title: str, body: str, read: Read, notice: str | None = None) -> str
  # cli
  View(port: int, allow_hosts: tuple[str, ...])   # run's view callable takes (port, allow_hosts)
  # tests/viewer/world.py
  def staged_world() -> tuple[Callable[[], Lodge], MemoryStore]   # one staged store behind every Lodge made
  ```
- The routes and their form fields, which Task 7's forms use as given:

  | Route | Fields |
  | --- | --- |
  | `POST /confirm` | `token`, `words`, `id` (one or more), `area` (from an area's page only) |
  | `POST /threads` | `token`, `about`, `kind` (`doubt` or `question`), `text` |
  | `POST /threads/<q>/reply` | `token`, `text` |
  | `POST /threads/<q>/close` | `token`, `text` (empty means none) |

- `refuse_early`: a `Host` not in `gate.hosts` is 403; no `Origin` is 403 (`a write needs an Origin header`); an `Origin` other than `http://` or `https://` followed by an allowed host, compared in lower case, is 403.
- `handle_post`, in order: `refuse_early`; a `Content-Type` other than `application/x-www-form-urlencoded` (parameters allowed) is 415; a body over `MAX_BODY` is 413; a body that is not UTF-8 is 400; `parse_qs(text, keep_blank_values=True, max_num_fields=200, errors="strict")`, a `ValueError` or `UnicodeDecodeError` being 400; anything but exactly one `token` field whose UTF-8 bytes equal `gate.token.encode("ascii")` under `hmac.compare_digest` is 403 (`this form is stale or from elsewhere; reload the page`); an `id` that is not a `d-` ID, or a `<q>` that is not a `q-` ID, is 400; then the route, writing as `author` with `where` `lodge viewer` and `commit=True`, under one module-level `threading.Lock` held from the route's first read to its last write, so a second request reads what the first wrote.
- Answers: a write answers `303` with `Location` `/r/{id}?done={code}` for a single confirmation, `/spec?area={area}&done={code}` for an area, the same two with `done=stale` on `StaleList`, and `/r/{about}?done={code}#{q}` for a thread write; each path part goes through `urllib.parse.quote(part, safe="")`; a failed check, a refused input, or empty words is 400 with the reason, a link back to the form's page, and nothing written; `NotFound` is 404; anything else is 500 with the error on stderr.
- `NOTICES`: `committed` "Written and committed."; `published` "Written and published."; `staged` "Written and staged, not committed."; `staged-base` "Written and staged, not committed: this checkout is on the base branch."; `staged-detached` "Written and staged, not committed: HEAD is detached."; `staged-in-progress` "Written and staged, not committed: a merge, rebase, cherry-pick, or revert is in progress."; `staged-locked` "Written and staged, not committed: git's index is locked by another process."; `staged-failed` "Written and staged, not committed: git could not commit; the terminal running lodge view says why."; `stale` "The list changed since the page was loaded, so nothing was written; check the new list."
  A `FAILED` commit's detail goes to stderr.
- `render` reads `done` and passes `NOTICES.get(code)` to `page`, shown as `<p class="notice" role="status">`; an unknown code shows nothing.
- `server.py`: `do_POST` runs `refuse_early` first, then reads `Content-Length` (missing 411, not `[0-9]+` 400, over `MAX_BODY` 413, the body unread in each), then calls `handle_post`, and sends `Location` on a 303; `_Handler.timeout = 10`, so a stalled body never holds the server; `PUT`, `PATCH`, `DELETE`, and `OPTIONS` stay 405 with `Allow: GET, HEAD, POST`; the `GET` host check uses `gate.hosts`; the 405 page reads "this address takes no such request".
- `lodge view --allow-host HOST`, repeatable: a value with whitespace or `/`, or empty, is a usage error, exit 2; the `view` help reads "serve the viewer on this machine: read, confirm, and raise doubts"; `main.py` mints `secrets.token_urlsafe(32)` and passes it to `serve`.

- [ ] **Step 1: Write the failing tests.**
  - `test_post_gate.py` (no socket): `test_no_origin_refused`; `test_foreign_origin_refused`; `test_origin_needs_scheme_and_allowed_host` (`ftp://127.0.0.1:8787` and `http://127.0.0.1:8788` refused, `https://localhost:8787` accepted); `test_allow_host_matches_the_whole_host` (`proxy.example:443` allowed, Host `proxy.example` refused); `test_missing_token_refused`; `test_wrong_token_refused`; `test_two_token_fields_refused`; `test_non_ascii_token_refused` (403, no exception); `test_token_compared_with_hmac` (a spy on `writes.hmac.compare_digest` is called); `test_wrong_content_type_415`; `test_body_over_limit_413`; `test_non_utf8_body_400`; `test_bad_percent_escape_400` (`words=%FF`); `test_too_many_fields_400`; `test_bad_id_400`; `test_short_token_refused_by_gatekeeper`.
  - `test_post_routes.py` (no socket; `staged_world()`): `test_confirm_redirects_with_done_code` (303, `Location == "/r/d-cccccc?done=committed"`); `test_area_confirm_redirects_to_the_area`; `test_stale_list_redirects_with_stale`; `test_two_concurrent_confirmations_write_once` (two threads, the store's first `publish` held until the second thread has entered `make_lodge`, which it calls before taking the write lock: one publish, one `done=committed`, one `done=stale`); `test_failed_check_answers_400_and_writes_nothing`; `test_ask_from_viewer_records_her_words` (message by `author`, `where == "lodge viewer"`, `when == "2026-10-29 09:30"`, text as typed); `test_unknown_kind_400`; `test_reply_and_close_redirect_to_the_thread`; `test_viewer_writes_only_new_decisions_and_thread_files` (for each route, every published path is a thread path or a decision path absent before); `test_staged_on_base_gives_staged_base` (`commit_result = Committed(CommitOutcome.ON_BASE)`); `test_get_with_done_shows_notice` (`render(make, urlsplit("/r/d-aaaaaa?done=committed"))` holds "Written and committed.").
  - `tests/e2e/test_view.py`: `test_view_passes_the_port_to_the_viewer` takes `view(port, allow_hosts)`; `test_allow_host_is_repeatable_and_passed`; `test_allow_host_with_space_slash_or_empty_exits_2`; the builder runs these three with `-k`.
  - `tests/viewer/test_server.py` (sockets; the coordinator runs them): `running` (line 20) and the direct calls at lines 135, 148, 158, and 170 pass a token; `test_only_reads_are_served` expects 403 for a `POST` without an `Origin`; new `test_post_through_the_socket_redirects`; `test_put_answers_405_allowing_post`; `test_allow_host_is_served`; `test_post_without_length_411` (allowed `Host` and `Origin`); `test_negative_length_400`.
- [ ] **Step 2: Run** `uv run pytest tests/viewer/test_post_gate.py tests/viewer/test_post_routes.py -q` and `uv run pytest tests/e2e/test_view.py -q -k "passes_the_port or allow_host"`; expected: FAIL.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the builder's gate and the `-k` run; expected: green; the coordinator runs `uv run pytest tests/viewer/test_server.py tests/e2e/test_view.py -q` outside the sandbox.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 7: The viewer's pages

**Files:**
- Modify: `src/lodge/viewer/pages.py`, `src/lodge/viewer/server.py`, `src/lodge/viewer/style.css`, `src/lodge/app/results.py` (`Shown.rests_on`, `Shown.supports`), `src/lodge/app/reads.py`, `src/lodge/core/order.py`, `src/lodge/core/__init__.py`, `tests/viewer/test_pages.py` and `tests/viewer/test_post_routes.py` (their calls pass `token`)
- Create: `src/lodge/viewer/forms.py` (the confirm, thread, reply, and close forms), `src/lodge/viewer/spec.py` (the specification and area pages)
- Test: `tests/viewer/test_forms.py` (new), `tests/viewer/test_pages_threads.py` (new), `tests/core/test_order.py`

**Interfaces:**
- Consumes: Tasks 1 to 6b: `SpecArea.placed`, `Placed`, `Shown.threads`, `Shown.confirmable`, `Lodge.behind_area`, `Behind`, `Lodge.threads_waiting`, `ThreadsWaiting.titles`, `Gatekeeper.token`, `handle_post`, and Task 6b's route and field table.
- Produces:
  ```python
  # core/order.py
  @dataclass(frozen=True) class Branch: id: str; title: str; status: str; children: tuple["Branch", ...]
  def rests_on_tree(s: Snapshot, d: Derived, entry_id: str) -> tuple[Branch, ...]  # down to the roots, cycle-safe
  # app
  Shown.rests_on: tuple[Branch, ...] = (); Shown.supports: tuple[Level1, ...] = ()
  # viewer
  def record_page(shown: Shown, token: str) -> str
  def spec_page(areas: tuple[SpecArea, ...], read: Read, token: str,
                order: Literal["dependency", "written"], area: str | None,
                behind: tuple[Behind, ...]) -> str           # order "written" when the query has order=written
  def waiting_page(listed: Listed, waiting: ThreadsWaiting) -> str
  render(make_lodge, url, token: str)       # the token reaches every page with a form
  ```
- Every form is `method="post"` with a relative `action`, a hidden `token`, and exactly the fields of Task 6b's table; every text she typed or an agent wrote is escaped with `html.e`.
- Decision page, when `confirmable`: a text area named `words`, labelled "Your words", required, beside it "The decision stays the agent's, and your words are kept exactly as written, so a caveat such as "read, not fully understood" belongs here.", a hidden `id`, and a button "Confirm".
- Every record page: below the record, its threads newest last, each a `<section class="thread" id="q-…">` with a heading "Doubt q-…" or "Question q-…" and its state, each message's `by`, `when`, and `where`, and the text as paragraphs, the closing message of a closed thread headed "Closed by BY" with its `when` and `where`, and no paragraph when its text is empty (d-a3h9f3); while open, a reply text area with button "Reply" and a form with button "Close" and an optional text area; then the forms "Raise a doubt" and "Ask a question", each a text area and a hidden `about` and `kind`.
- Entry page: "Rests on", nested lists down to the roots, and "Rests on it", one level from `supports`, each item a link with its status.
- Specification page: "By dependency" by default (`placed`, each entry in a `div` of class `depth-N`, `N = min(depth, 5)`, one line "also rests on" with links to `also`, and to `under` too when the depth is over 5, when either applies, and a line `rests on <link> (area)` per cross-area target), "As written" with `?order=written` (`entries`); both links on the page keep `area`; each area heading links to `/spec?area=NAME`.
- Area page (`/spec?area=NAME`), when `behind` is non-empty: above the entries, "Decisions behind this area, not yet confirmed", each decision a link with its title and the entries it changes with their areas, then one form with a hidden `area`, a hidden `id` per listed decision, and the field and button of the decision page.
- Waiting page, titled "Waiting": "Waiting for an agent" (`for_agent`), then "Waiting for the author" (the flagged decisions, then `for_author`); each thread a link to `/r/{about}#{q}` with its head and the title from `titles`.
- `style.css`: `.depth-1` to `.depth-5` (indent steps), `.thread`, `.notice`, and form spacing, within the existing look; no inline style, since the policy forbids it (`POLICY`).

- [ ] **Step 1: Write the failing tests.**
  - `test_forms.py`: `test_confirm_form_on_a_confirmable_decision` (`action="/confirm"`, `name="token" value="T…"`, "Your words", "Confirm", the note text); `test_no_confirm_form_on_author_confirmed_or_replaced_decisions`; `test_doubt_and_question_forms_on_every_record`; `test_open_thread_has_reply_and_close`; `test_closed_thread_has_neither`; `test_thread_text_is_escaped` (`<script>` appears as `&lt;script&gt;`); `test_forms_post_to_relative_actions_only`; `test_rendered_forms_post_through_handle_post` (each form of a decision page, an area page, and an entry page with an open thread: its `action` and field names read from the HTML, filled, and passed to `handle_post` against `staged_world()`, each answering 303).
  - `test_pages_threads.py`: `test_threads_newest_last`; `test_entry_tree_down_to_roots_and_one_level_up`; `test_spec_opens_by_dependency` (written a, b, c, with c resting on a: the order a, c, b, c in `depth-1`); `test_spec_also_rests_on_line` (an entry with a second same-area target shows "also rests on" with its link); `test_thread_closed_without_text_shows_closed_by_author` (closed from the viewer with the field empty: the page shows "Closed by author", and the thread file's closing message holds no text); `test_spec_as_written`; `test_spec_cross_area_line`; `test_area_page_lists_decisions_entries_and_hidden_ids`; `test_area_page_without_unconfirmed_has_no_form`; `test_waiting_page_has_both_groups`.
  - `test_order.py`: `test_rests_on_tree_reaches_the_roots`; `test_rests_on_tree_stops_on_a_cycle`.
- [ ] **Step 2: Run** `uv run pytest tests/viewer/test_forms.py tests/viewer/test_pages_threads.py tests/core/test_order.py -q`; expected: FAIL.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the builder's gate; expected: green; the coordinator runs the socket tests and opens one decision, one entry, `/spec`, an area page, and `/waiting` in a browser, recording what it saw in the report.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 8: `rests_on` for the existing entries

**Files:** records via `lodge add`; report `docs/superpowers/plans/2026-10-31-lodge-viewer/task-8-report.md`.

**Interfaces:**
- Consumes: Task 2's `link` action and checks; `lodge draft`, `lodge add`, `lodge spec`, `lodge show`.
- Produces: one coordinator decision per area that gains links; no other record changes.

- `lodge add` as in the Global Constraints.
- The rule for a link: entry A rests on entry B when A would not hold without B: A's statement names B by ID (s-dm37qr, s-hfjr1m, s-m83kjq, and s-582qav do today), or A states a case, check, or measure of a rule B introduces as a whole (each check's entry rests on s-j70a0k), or A uses a term only B defines; sharing a topic is not resting.
  B may lie in another area; no link may close a cycle.
- Per area with links: `lodge draft s-…` for each entry that gains `rests_on`, with the one line `rests_on: [s-…]` added and nothing else changed, plus one decision draft: `decided_by: coordinator`, `scope: product`, title `Rests-on links in area NAME`, statement `Entries of area NAME list the entries they rest on.`, `changes` listing each such entry with action `link`, and reasoning one line per link, `s-a rests on s-b: <reason in one clause>.`.
- `lodge add --dry-run` per area, then `lodge add`; the feedback asking about a named ID must be gone for the four entries.
- The report: a table of area, entry, rests on, reason, and decision ID; the areas without links; and the dry-run feedback, each line answered.

- [ ] **Step 0:** `uv run lodge waiting > .drafts/waiting-before.txt`.
- [ ] **Step 1:** Read every area with `uv run lodge spec --area NAME` and draft the links by the rule.
- [ ] **Step 2:** Dry-run each area's drafts; expected: no check line.
- [ ] **Step 3:** Add each area's drafts.
- [ ] **Step 4: Verify** `uv run lodge check` prints `ok`; `grep -l '^rests_on:' lodge/spec/*/*.md | wc -l` equals the report's count of entries with links; `uv run lodge waiting | diff .drafts/waiting-before.txt -` prints nothing.
- [ ] **Step 5: Coordinator:** `git add lodge/`, `sh scripts/check.sh`, commit the record files and the report, push.

### Tasks 9a, 9b, and 9c: This design into lodge

Each of the three is its own brief, build, and review, in this order, and each holds the rules below as well as its own part.

**Files:** records via `lodge add`; report `docs/superpowers/plans/2026-10-31-lodge-viewer/task-9-report.md`, which each part extends.

**Interfaces:**
- Consumes: Tasks 1 to 8; the design; d-7w5aq0; the records named below.
- Produces: six author decisions, six coordinator decisions, their entries, and the edits and narrowings below; about 20 to 40 new entries in all.

Rules for every part:
- `lodge add` as in the Global Constraints.
- A coordinator decision per design section, `decided_by: coordinator`, `scope: product`, creating the entries for its section's claims, one per claim a reader would look up on its own, within 150 words, saying what holds now, each with `rests_on` where it would not hold without another entry (Task 8's rule).
- An entry's area by its topic: Goals, Non-goals, and Must nots in `purpose`; a record kind, a field, or an action in `model`; a check, feedback, the review flag, or what waits in `writing`; the viewer, `lodge spec`, or a read in `reading`; where files live or how the store commits in `storage`.
- Its reasoning carries the section's reasons, names d-7w5aq0 for each claim the design marks **[advisor]**, and says which claims are the coordinator's calls.
- It narrows the coordinator decisions whose statements it makes false, never an author decision, and answers any other "looks related" feedback with no.
- After each section's add, `uv run lodge spec | grep 'changed since'`: each entry that still holds is listed in the next decision of the same part with `edit`, its text unchanged, and one reasoning line saying why it holds (design line 113); an entry that no longer holds is edited.
- Each part's report section: each new entry with its decision and the design lines it holds; each edited entry with the sentence that changed; each narrowed decision with why.

**Task 9a: her quotes, the Goals, and Confirming.**
- First six author decisions, one per quote of design lines 13 to 18, never lines 12 and 19, which d-dyrpc6 and d-2hcgav already record: `decided_by: author`, `scope: product`, `quote: {text: <only the words inside the quotation marks, verbatim>, where: "lodge build session", when: <below>}`, reasoning equal to the quote text and nothing else, and a statement saying only what the words settle:
  - line 13, `when: "2026-10-30 09:41"`: a doubt or question about an entry is raised and answered on that entry;
  - line 14, `when: "2026-10-30 09:41"`: entries are ordered or arranged by their dependencies;
  - line 15, `when: "2026-10-30 09:43"`: the arrangement shows what rests on what, so a wrong point resting on another wrong point shows;
  - line 16, `when: "2026-10-30 09:46"`: points resting on a wrong one are retired or corrected as appropriate;
  - line 17, `when: "2026-10-30 09:47"`: the author, an agent, or both work that out;
  - line 18, `when: "2026-10-30 09:37"`: confirming a record does not show it as written by the author, and who wrote what stays visible.
- Then the decision for Goals, Non-goals, and Must nots (design lines 21 to 47), then the one for Confirming (design lines 48 to 73), which edits s-j5ttw1 (no "There is no confirmation step"; a confirmation is a separate author record) and says in its reasoning that LODGE-6 (d-8nkamy) still makes a confirmed decision count as hers for the review flag.

**Task 9b: Doubts and questions, and Rests on.**
- The decision for Doubts and questions (design lines 75 to 100) says in its reasoning that threads reach decisions too, the extension of her words on entries (d-7w5aq0, design line 78); it edits s-a67fqm (three record kinds), s-evv024 (`lodge/threads/`), s-0s9m2d (the two groups of what waits), s-ms14fq (check 5 covers threads), s-wcv4en (level 1 carries the marks as well as any review flag), and s-7ah5n7 (one sentence after its first: a thread, a doubt or question on a decision or entry with its messages, is not such a kind: it holds no claim of its own, and what it settles enters lodge as a decision; its statement otherwise unchanged).
  Its entry on closing states that a close without text appends a closing message with no text, shown as "closed by" its writer, not design line 85's "Closed."; its reasoning names d-a3h9f3 for that entry and for the s-7ah5n7 edit, and names the line 13 author decision of Task 9a for the s-7ah5n7 edit.
- The decision for Rests on (design lines 102 to 114) edits s-0yzshh (the `link` action), s-01k42c (a `link` raises no flag), s-j70a0k (eight checks), s-edgt71 (all eight), s-8f6scf (`rests_on` is stored on the entry), and s-aw5a1j (check 6 covers an entry edited in the change), and narrows d-zerbz9, d-3epcjd, and d-4032xv, the coordinator decisions behind "links on the decision only" and "seven checks".

**Task 9c: Arrangement and Security.**
- The decision for Arrangement (design lines 116 to 122) edits s-v022r0 (areas by rank, entries after what they rest on); its entry on the dependency view states "dependants follow what they rest on, siblings in the area's order", and its reasoning names d-a3h9f3.
- The decision for Security (design lines 124 to 132) edits s-dm37qr, s-582qav, and s-nzhyh3 (the viewer writes confirmations and threads only).
- The report closes with every design line from 21 to 141 mapped to an entry or named as left out, with the reason.

- [ ] **Step 1 (each part):** `uv run lodge id s` per new entry; drafts of the new and edited entries and the decision; dry-run; add; the "changed since" pass.
- [ ] **Step 2: Verify (each part)** `uv run lodge check` prints `ok`; `uv run lodge spec | grep -c 'changed since'` prints 0, or the report names each remaining mark and why; in 9a, `uv run lodge search --by author --limit 50` lists the six and `uv run lodge show s-j5ttw1` no longer holds "There is no confirmation step"; in 9c, `uv run lodge spec --area reading` names the viewer's writes.
- [ ] **Step 3: Coordinator (each part):** `git add lodge/`, `sh scripts/check.sh`, commit, push.

### Task 10: The documents

**Files:**
- Modify: `README.md`, `CLAUDE.md`, `docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md` (one line at the end), `.lodge.toml` (`[hook] frozen`)

- `README.md`: What it holds (threads; `rests_on`); Reading (`threads`, `thread`, `waiting` in two groups, `spec` by rank and dependency); Writing (`rests_on`, the `link` action, `ask`, `reply`, `close`, author messages with `--where` and `--when`, threads stage like `add`); the check (eight checks, and which a thread can fail); The viewer (no longer read-only: confirming and threads; the token, `Origin`, and `--allow-host`; commits in checkout mode and when it does not commit); every command and string as built, read from `uv run lodge --help` and the code.
- `CLAUDE.md`: a line "Run `uv run --frozen --quiet lodge waiting` at the start of a session and answer what waits for an agent first."
- The design document gets its last line first, "Its content now lives in lodge (`lodge spec`, `lodge show`); this document is frozen."; only then does `.lodge.toml`'s `frozen` gain `"docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md"`, so the hook does not fire on that edit.

- [ ] **Step 1:** Edit the four files in that order.
- [ ] **Step 2: Verify** every command the README names runs (`uv run lodge <command> --help` exits 0); `git grep -n 'read-only' -- README.md src/` names nothing about the viewer; `git grep -nP '\x{2014}|\x{2013}' -- README.md CLAUDE.md` prints nothing; `printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"},"cwd":"%s"}' "$PWD/docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md" "$PWD" | uv run --frozen --quiet lodge hook post-tool-use` prints the frozen-file feedback.
- [ ] **Step 3: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 11: The areas' ranks

**Files:** the ten `_area.md` files and one decision via `lodge add`.

- `lodge add` as in the Global Constraints.
- `lodge draft area:NAME` for each area, with one line `rank: N` added after `title`: `purpose` 1, `constraints` 2, `model` 3, `levels` 4, `writing` 5, `reading` 6, `hook` 7, `storage` 8, `structure` 9, `rollout` 10, the first design's section order, as `docs/superpowers/plans/2026-10-30-lodge-on-itself.md:73` laid the areas out.
- In the same add, one decision: `decided_by: coordinator`, `scope: process`, `work_item: docs/superpowers/plans/2026-10-31-lodge-viewer.md`, title `Area ranks follow the first design's sections`, a one-sentence statement saying so, and reasoning naming that plan line; it changes no entry.

- [ ] **Step 1:** Draft, dry-run (no `rank … is shared` feedback), add.
- [ ] **Step 2: Verify** `uv run lodge spec | grep '^# '` lists the area titles in rank order; `uv run lodge check` prints `ok`.
- [ ] **Step 3: Coordinator:** `git add lodge/`, `sh scripts/check.sh`, commit, push.
