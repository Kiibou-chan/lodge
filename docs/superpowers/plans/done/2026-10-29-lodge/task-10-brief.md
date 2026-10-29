### Task 10: The command line and composition root

**Files:**
- Create: `src/lodge/cli/parser.py`, `src/lodge/cli/commands.py`, `src/lodge/cli/output.py`, `src/lodge/cli/guide.md` (package data)
- Modify: `src/lodge/main.py`, `pyproject.toml` (package data)
- Test: `tests/e2e/conftest.py` (a project clone with a bare remote, `.lodge.toml` per test, `run(*argv) -> Result(code, out, err)` calling `main()` in-process after `chdir`), `tests/e2e/test_<command>.py` per command, `tests/test_wheel.py`

**Interfaces:**
- Consumes: `lodge.app.Lodge`, `lodge.gitstore`.
- Produces: `cli.run(argv: Sequence[str], make_lodge: Callable[[], Lodge], init: Callable[[], str], view: Callable[[int], int], hook: Callable[[], int]) -> int`, which owns all parsing; `main.main()` finds the repository and loads settings lazily, inside the callables that need them (so `--version`, `guide`, and `hook` work anywhere), wires `open_store`, a clock (`datetime.now().astimezone()`), and `secrets.token_bytes(8)`, passes the viewer's and hook's entry points as callables, and catches every `LodgeError` once (prints `lodge: <message>` to stderr, returns its code); the `hook` callable never raises and never needs a repository.
- Commands and output (every read first prints the freshness line when not `None`, then one line per unrecorded problem, `problem: <path>: <message>`):
  - `lodge init`: the line from `init_store`.
  - `lodge id d|s`: one new ID.
  - `lodge search QUERY [--kind decision|spec] [--scope product|process] [--status current|replaced|retired|any] [--area A] [--by WHO]`: `format_level1` blocks separated by a blank line, or `no matches`.
  - `lodge show REF [--reasoning] [--provenance]`: level 1, then `## Reasoning` and `## Provenance` when asked.
  - `lodge draft REF`: the file text with `base:`.
  - `lodge add [--import] FILE...`: `feedback: <id>: <message>` lines, `note: <text>` lines, `check <n>: <message>` lines, then `published <ids>`, `staged <ids>`, or `not published: the check failed`; exit 1 on a failed check or conflict.
  - `lodge check [--gate]`: problems, then notes; `ok` when no problems; exit 1 on problems.
  - `lodge spec [--area A]`, `lodge waiting` (or `nothing waits for the author`), `lodge guide`, `lodge view [--port N]` (default 8787), `lodge hook post-tool-use`.
- `guide.md`, at most 60 lines, for an agent: what decisions, entries, and areas are; the three levels and that `show` gives level 1 unless asked; the write path (`lodge id s`, drafts kept outside `lodge/`, `lodge draft` for edits, `lodge add` with the decision and its entries together); never edit record files by hand; quoting the author (`quote: {text, where, when}`, her words verbatim only); feedback is advice, the check is a gate.

- [ ] **Step 1: Write failing end-to-end tests**, one file per command, checkout mode unless named: `test_init`, `test_init_branch_mode`, `test_id`, `test_search`, `test_search_shows_unparsable_file`, `test_show_levels`, `test_show_ambiguous_code_one_line`, `test_draft_then_add_edit`, `test_add_new_decision_entry_area`, `test_add_branch_mode_publishes`, `test_add_failing_check_exits_1`, `test_add_bad_yaml_exits_2_naming_file_and_line`, `test_add_non_string_scalar_exits_2`, `test_check_and_gate`, `test_spec`, `test_waiting`, `test_guide`, `test_help_lists_every_command`, `test_outside_repository_one_sentence_exit_2`, `test_before_init_one_sentence_exit_2`, `test_malformed_settings_one_sentence_exit_2`, `test_hook_outside_repository_exit_0_silent`.
- [ ] **Step 2: Write `test_wheel.py::test_installed_wheel_runs`**: `uv build --wheel` into `tmp_path`, install into a fresh venv made with `uv venv`, run `lodge --version` and `lodge guide`; marked slow, run in `check.sh`.
- [ ] **Step 3: Run**; expected: FAIL.
- [ ] **Step 4: Implement** parser, commands, output, guide, and `main.py`, reading `guide.md` with `importlib.resources`.
- [ ] **Step 5: Run** `sh scripts/check.sh`; expected: green.
- [ ] **Step 6: Commit and push.**


## Carried from earlier tasks (ledger rulings, binding)

- `lodge add --dry-run` (Task 7 I2, Task 8): runs `Lodge.add(..., dry_run=True)`, prints feedback, notes, and check lines as a real add, then `dry run: nothing published`; exit 1 when the check fails, else 0.
  Tests: `test_add_dry_run_publishes_nothing`, `test_add_dry_run_failing_check_exits_1`.
- The guide says to run `lodge add --dry-run` before `lodge add`, since feedback can only be acted on before publishing (a published decision is immutable).
- The guide says attachments live at `lodge/attachments/<decision id>/<name>` and a decision lists them by `<name>` (Task 5 M3).
- Unreadable files print as `problem:` lines above every read's output, before anything else but the freshness line (Task 6 I4). Test: `test_broken_agent_decision_warns_above_show`: an agent decision's file is broken by hand in checkout mode, and `lodge show` of the entry it changed prints the `problem:` line first.
- An add that changes nothing carries the note `nothing changed` and prints `published` with no IDs; print it as given (Task 8 M7).
- Five core names are also core module names (`check_change`, `check_state`, `derive`, `feedback`, `search`): reach them as `from lodge import core` and `core.<name>`.
- Settings: `lodge.gitstore.load_settings(root)` gives `ProjectSettings`; `ProjectSettings.raw` is the whole TOML table. The hook package (Task 12) does not exist yet: `main` passes a `hook` callable that reads stdin and returns 0 silently, and a `view` callable that raises `LodgeError("the viewer is not built yet")`; Tasks 11 and 12 replace them. Task 12 adds the `parse_hook_settings(raw.get("hook", {}))` call.
