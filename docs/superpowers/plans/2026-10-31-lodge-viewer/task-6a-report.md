# Task 6a report

Implemented core and application confirmation support.
No commit or push was made.

## Files changed

- `src/lodge/core/confirmation.py`: added `VIEWER`, confirmable decision selection, area creator and last changer selection including retired entries, chronological ordering, and quoted confirmation drafts with the required titles, statements, and Oxford comma.
- `src/lodge/core/__init__.py`: exported the confirmation interfaces.
- `src/lodge/app/confirm.py`: added area rows with deduplicated entry and area pairs, unknown area errors, word cleaning and validation, stale list validation, scope selection, clock provenance, ordinary decision writes, and optional commits of the added paths.
- `src/lodge/app/errors.py`: added `StaleList` as a conflict.
- `src/lodge/app/results.py`: added `Behind` and the defaulted `Shown.confirmable` field.
- `src/lodge/app/reads.py`: populated `Shown.confirmable`.
- `src/lodge/app/lodge.py`: exposed `confirm` and `behind_area`.
- `src/lodge/app/__init__.py`: exported `Behind` and `StaleList`.
- `tests/core/test_confirmation.py`: added the five core tests below.
- `tests/app/test_confirm.py`: added the fourteen application tests below, with two word validation cases.
- This report records the implementation and verification.

No existing test assertion needed changing.
No record was created by this task.
Other working tree changes appeared during the run in the progress ledger, a record, and the task 4 review; they were left untouched.

## First failing run

Both test files were written before implementation, then run together with:

```sh
uv run pytest tests/core/test_confirmation.py tests/app/test_confirm.py -q
```

The first run stopped at collection, so each test below shared its file's import failure rather than reaching its assertions.
The core failure was:

```text
E   ImportError: cannot import name 'behind_area' from 'lodge.core'
```

The application failure was:

```text
E   ImportError: cannot import name 'StaleList' from 'lodge.app'
```

The final lines were:

```text
ERROR tests/core/test_confirmation.py
ERROR tests/app/test_confirm.py
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!
2 errors in 0.24s
```

### Core tests

Each had the core import failure above on the first run.

- `test_confirmable_ids_skip_author_confirmed_and_replaced`: excludes author, confirmed, and replaced decisions.
- `test_behind_area_lists_creators_and_last_changers_oldest_first`: includes creators and the latest changer, excludes intermediate edits, and orders by date.
- `test_behind_area_includes_the_retirer_of_a_retired_entry`: includes a retired entry's last changer.
- `test_confirmation_draft_single`: parses the draft into a decision and checks the title, statement, reasoning, and quote location.
- `test_confirmation_draft_area_lists_with_the_oxford_comma`: checks the area title and three-item statement.

### Application tests

Each had the application import failure above on the first run.

- `test_confirm_one_decision`: publishes an author confirmation with the fixed clock's minute and does not commit a branch publication.
- `test_confirm_writes_only_a_new_decision_file`: checks that exactly one previously absent decision path is published.
- `test_confirmed_decision_keeps_decided_by_and_clears_its_flag`: retains the agent attribution and clears the review flag.
- `test_scope_product_when_any_listed_is_product`: checks product scope for an area confirmation.
- `test_scope_process_when_all_are_process`: checks process scope for a process decision.
- `test_area_confirms_exactly_the_listed`: accepts the same submitted set in another order and writes the chronological list.
- `test_stale_area_list_writes_nothing`: refuses a changed list with the exact error and no publication.
- `test_second_identical_confirmation_is_stale`: refuses a repeated confirmation against staged files, with only one publication.
- `test_words_required`: refuses empty and whitespace-only words without publication.
- `test_words_with_specials_kept_verbatim`: preserves quotation marks, backslashes, punctuation, Unicode, tabs, and an isolated carriage return, while removing CR before LF and outer whitespace.
- `test_words_with_unstorable_character_refused`: converts the NUL draft error into the required `LodgeError` without publication.
- `test_commit_after_staged`: commits only the new path with the exact message and returns the commit result.
- `test_behind_area_lists_entries_in_other_areas`: includes entries in another area, removes duplicates, omits missing entries, and checks an unknown area raises `NotFound`.
- `test_show_marks_confirmable`: checks agent, entry, confirmed agent, and author confirmation pages.

## Commands and results

Repository instructions, existing implementation, test helpers, and the confirming section of the interaction design were read with `cat`, `rg`, and `sed`.

```text
uv run ruff format src/lodge/core/confirmation.py src/lodge/app tests/core/test_confirmation.py tests/app/test_confirm.py
5 files reformatted, 8 files left unchanged

uv run pytest tests/core/test_confirmation.py tests/app/test_confirm.py -q
20 passed in 0.18s
```

The first builder gate stopped at three import or export ordering errors.
`uv run ruff check --fix src/lodge/app/__init__.py src/lodge/core/__init__.py` ended with `Found 3 errors (3 fixed, 0 remaining).`
The next gate stopped at two mypy errors from repeatedly calling the test helper while narrowing an optional quote.
The tests now bind each quote once before checking it.

The final builder gate was:

```sh
uv run ruff format --check && uv run ruff check && uv run mypy && uv run vulture && uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py && uv run lodge check --gate
```

It exited 0 with:

```text
423 files already formatted
All checks passed!
Success: no issues found in 184 source files
1249 passed in 33.68s
ok
```

Vulture produced no output.
The lodge check also reported area additions and ended with `note: uncommitted record changes in lodge/; commit them before you push`.
Those record changes were not made by this task.

```text
uv run pytest tests/e2e/test_view.py -q -k test_view_passes_the_port_to_the_viewer
1 passed, 2 deselected in 0.29s

git diff --check
(no output, exit 0)
```

## Limits and concerns

The coordinator still needs to run `sh scripts/check.sh` outside the sandbox.
The socket-bound coverage excluded here is `tests/viewer/test_server.py` and the remaining tests in `tests/e2e/test_view.py`, particularly `test_view_serves_the_project_until_interrupted`.

Stale lists are checked against the current tree, including staged confirmations, before calling the required `writes.add` path.
This validation is not atomic with publication: an intervening change after validation, including one encountered during an ordinary add retry, is not revalidated by this task's confirmation layer.
The brief's named repeated-submission and stale-list tests pass, but no concurrent-publication guarantee was added to `writes.add`.

No disagreement with the cited design text was found.
