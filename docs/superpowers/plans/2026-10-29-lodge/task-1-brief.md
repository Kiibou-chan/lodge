### Task 1: Project skeleton, structure test, and the gate script

**Files:**
- Create: `pyproject.toml`, `uv.lock`, `scripts/check.sh`, `vulture_allow.py`
- Modify: `.gitignore` (add `__pycache__/`, `.venv/`, `dist/`, `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`)
- Create: empty `src/lodge/__init__.py`, `src/lodge/main.py`, and front doors `src/lodge/{core,app,gitstore,cli,viewer,hook}/__init__.py`
- Create: `tests/structure_rules.py`, `tests/test_structure.py`, `tests/test_entry_point.py`

**Interfaces:**
- Produces: `lodge.main:main(argv: list[str] | None = None) -> int`, console script `lodge`, version from `importlib.metadata.version("lodge")`; `tests/structure_rules.py` with `ALLOWED: dict[str, set[str]]`, `CORE_MODULES: set[str]`, `MAX_LINES = 300`, `def violations(src_root: Path, tests_root: Path) -> list[str]`.

- [ ] **Step 1: Write the failing structure tests**, each building a throwaway tree under `tmp_path` and asserting one violation message:
  - `test_core_importing_app`, `test_adapter_importing_adapter` (`cli` importing `gitstore`), `test_import_past_front_door` (`from lodge.core.check import x` in `app`), `test_submodule_through_front_door` (`from lodge.core import check` where `core/check.py` exists), `test_from_lodge_import_package` (`from lodge import gitstore` in `cli`), `test_import_statement_form` (`import lodge.gitstore.git as g` in `cli`), `test_relative_import` (`from ..gitstore import x` in `cli`), `test_import_inside_function`, `test_dynamic_import` (`importlib.import_module` or `__import__` anywhere in `src`), `test_own_front_door_import` (`from lodge.core import Snapshot` inside `core/check.py`), `test_unknown_package` (`src/lodge/importer/`), `test_import_cycle` (message contains `cycle`; `__init__` modules are graph nodes), `test_long_module` (301 lines, also under `tests`), `test_core_disallowed_module` (each of `os`, `time`, `random`, `secrets`, `subprocess`, `pathlib`, `io`, `sys`), `test_core_banned_name` (`dt.datetime.now()` with `import datetime as dt`, `date.today()`, `open(...)`, `print(...)`), `test_subprocess_outside_gitstore`.
  - `test_real_tree_is_clean`: paths rooted at `Path(__file__).parents[1]`; asserts `violations(...) == []` and that the scan visited all six packages.
- [ ] **Step 2: Run** `uv run pytest tests/test_structure.py -q`; expected: FAIL (`violations` not defined).
- [ ] **Step 3: Implement `violations`** with `ast.walk` over every module: resolve each `Import` and `ImportFrom` (relative ones against the module's dotted name) to a target module, treating `from P import n` as `P.n` when `P/n.py` or `P/n/` exists; map modules to packages; the root `lodge/__init__.py` may import nothing.
  ```python
  ALLOWED = {"core": set(), "app": {"core"}, "gitstore": {"app", "core"},
             "cli": {"app", "core"}, "viewer": {"app", "core"}, "hook": {"app", "core"},
             "main": {"core", "app", "gitstore", "cli", "viewer", "hook"}}
  ```
- [ ] **Step 4: Write `test_entry_point.py::test_version`** calling `main(["--version"])` in-process and capturing `lodge 0.1.0.dev0`; implement with `argparse`.
- [ ] **Step 5: Write `scripts/check.sh`** (`set -eu`, the commands of Global Constraints with `uv run`); configure Ruff, mypy (`files = ["src", "tests"]`), Vulture in `pyproject.toml`; run `sh scripts/check.sh`; expected: green.
- [ ] **Step 6: Commit and push**; tag `v0.1.0.dev0` and push the tag (Task 2 needs it).

