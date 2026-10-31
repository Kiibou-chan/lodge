# Brief: Task 1 of `docs/superpowers/plans/2026-10-31-lodge-viewer.md`

You build Task 1 of the plan named above, in this repository, on its current branch.
Read `CLAUDE.md` first, then this brief; this brief is your requirements, with the exact values to use verbatim.
Read other parts of the plan only where this brief points to them by name.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Do not commit and do not push: the coordinator stages, runs `sh scripts/check.sh` outside the sandbox, commits, and pushes.
Tests that need sockets fail in your sandbox; run the rest, and name the socket-bound ones in your report.
Write your report to `docs/superpowers/plans/2026-10-31-lodge-viewer/task-1-report.md`: what you changed per file, each test you added with its first failing output, the commands you ran and their last lines, and anything you were unsure of.
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
