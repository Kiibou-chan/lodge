### Task 12: The hook

**Files:**
- Create: `src/lodge/hook/post_tool_use.py`
- Modify: `src/lodge/main.py` (pass `hook`), `README.md` (the settings snippet)
- Test: `tests/hook/test_post_tool_use.py`

**Interfaces:**
- Consumes: from `main`, the repository root (or `None`), `data_root`, and the raw settings table.
- Produces: `def parse_hook_settings(table: Mapping[str, object]) -> tuple[str, ...]` (the `frozen` globs; an unknown key raises `LodgeError` naming it) and `def respond(payload: Mapping[str, object], repo_root: Path, data_root: Path | None, frozen: Sequence[str]) -> dict[str, object] | None` and `def run(stdin: TextIO, stdout: TextIO, context: Callable[[], tuple[Path, Path | None, Sequence[str]] | None]) -> int`, always 0, swallowing every exception.
- Fires when `tool_name` is `Edit`, `Write`, or `MultiEdit` and `tool_input.file_path` resolves under `data_root` (outside `lodge/attachments/`), or matches a `[hook] frozen` glob relative to the repository root; output `{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": <text>}}`, the text naming the file and what to use instead (`lodge draft` then `lodge add` for records; a new decision through `lodge add` for frozen files). In branch mode there is no record file to protect, so only frozen globs apply. Bash edits are out of scope for 0.1.
- README snippet: the `PostToolUse` entry with matcher `Edit|Write|MultiEdit` and command `lodge hook post-tool-use`.

- [ ] **Step 1: Write failing tests:** `test_record_edit_gets_feedback`, `test_attachment_edit_gets_nothing`, `test_frozen_edit_gets_feedback`, `test_other_edit_gets_nothing`, `test_bad_payload_exit_0_silent`, `test_context_failure_exit_0_silent`.
- [ ] **Step 2: Run**; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check.sh`; expected: green.
- [ ] **Step 5: Commit and push.**


## Carried from earlier tasks (ledger rulings, binding)

- `main` replaces Task 10's placeholder `hook` callable (which reads stdin and returns 0) with `hook.run`, and calls `parse_hook_settings(raw.get("hook", {}))` for every command except the hook route (Task 9 concern 1: `ProjectSettings.raw` is the whole table); an unknown `[hook]` key is one sentence, exit 2.
- Any argv starting with `hook` skips argument parsing and exits 0 (Task 10 ruling); keep that.
- The text the hook gives names `lodge add --dry-run` before `lodge add` (Task 7 I2).
- `README.md` may not exist yet: create it with only the hook snippet section if absent; Task 13 writes the rest.
