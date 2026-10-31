# Brief: Task 2 of `docs/superpowers/plans/2026-10-31-lodge-viewer.md`

You build Task 2 of the plan named above, in this repository, on its current branch.
Read `CLAUDE.md` first, then this brief; this brief is your requirements, with the exact values to use verbatim.
Read other parts of the plan only where this brief points to them by name.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Do not commit and do not push: the coordinator stages, runs `sh scripts/check.sh` outside the sandbox, commits, and pushes.
Tests that need sockets fail in your sandbox; run the rest, and name the socket-bound ones in your report.
Write your report to `docs/superpowers/plans/2026-10-31-lodge-viewer/task-2-report.md`: what you changed per file, each test you added with its first failing output, the commands you ran and their last lines, and anything you were unsure of.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.

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
