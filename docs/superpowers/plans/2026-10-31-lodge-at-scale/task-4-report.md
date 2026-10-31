# Task 4 build report

Status: in progress on `read-speed-build`.
Only Task 4's application state, new test files, the explicitly named derivation test, and this report are in scope.
No project records are opened directly, added, or edited.

## Requirements and approach

`read_checked` will compare the current and published file mappings and attachment sets, independently of their revisions.
Equal inputs will return the already loaded and checked state, preserving its snapshot, derivation, problems, notes, failing IDs, and read metadata.
Different inputs will retain the existing published-state load and change check.
No interface is added or moved, so the interface skeleton step does not apply.
The authority read through lodge includes `d-zyqzkg`, `d-c0q20c`, and the current specification.

The plan expects failures on call counts before implementation.
The core self-comparison property is a proof regression test and is expected to pass against the existing implementation.
Failing output, validation, the proof against the built code, and benchmark comparisons will be recorded below as they complete.

## Tests before implementation

Command: `uv run --frozen pytest tests/core/test_identical_change.py tests/app/test_identical_reads.py tests/core/test_linear_derive.py::test_derive_once_per_checked_read -q --tb=short`.
The expected count failures were observed: 25 failed and 53 passed.
All 48 core self-comparisons and the five different-input guard cases already passed.
Each output comparison matched before its count assertion failed.
The output test disables the shortcut by making only raw mapping equality false, leaving parsed inputs unchanged, and checks both exit status and captured standard output and error.
The only existing test edit tightens `test_derive_once_per_checked_read` from two derivations to one.

```text
................................................FFFF.....FFFFFFFFFFFFFFF [ 92%]
FFFFFF                                                                   [100%]
=================================== FAILURES ===================================
_________________ test_identical_trees_load_once[False-False] __________________
tests/app/test_identical_reads.py:34: in test_identical_trees_load_once
    assert loads.call_count == 1
E   AssertionError: assert 2 == 1
E    +  where 2 = <MagicMock name='load' id='139685558544976'>.call_count
__________________ test_identical_trees_load_once[False-True] __________________
tests/app/test_identical_reads.py:34: in test_identical_trees_load_once
    assert loads.call_count == 1
E   AssertionError: assert 2 == 1
E    +  where 2 = <MagicMock name='load' id='139685558547664'>.call_count
__________________ test_identical_trees_load_once[True-False] __________________
tests/app/test_identical_reads.py:34: in test_identical_trees_load_once
    assert loads.call_count == 1
E   AssertionError: assert 2 == 1
E    +  where 2 = <MagicMock name='load' id='139685558548672'>.call_count
__________________ test_identical_trees_load_once[True-True] ___________________
tests/app/test_identical_reads.py:34: in test_identical_trees_load_once
    assert loads.call_count == 1
E   AssertionError: assert 2 == 1
E    +  where 2 = <MagicMock name='load' id='139685558549680'>.call_count
_____________ test_identical_read_output_unchanged[command0-clean] _____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 1 == 0
E    +  where 1 = <MagicMock name='check_change' id='139685557695696'>.call_count
____________ test_identical_read_output_unchanged[command0-broken] _____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 1 == 0
E    +  where 1 = <MagicMock name='check_change' id='139685558550016'>.call_count
_____________ test_identical_read_output_unchanged[command0-cycle] _____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 1 == 0
E    +  where 1 = <MagicMock name='check_change' id='139685558549680'>.call_count
____________ test_identical_read_output_unchanged[command0-history] ____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 1 == 0
E    +  where 1 = <MagicMock name='check_change' id='139685558549344'>.call_count
_____________ test_identical_read_output_unchanged[command1-clean] _____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 1 == 0
E    +  where 1 = <MagicMock name='check_change' id='139685558549008'>.call_count
____________ test_identical_read_output_unchanged[command1-broken] _____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 1 == 0
E    +  where 1 = <MagicMock name='check_change' id='139685558548672'>.call_count
_____________ test_identical_read_output_unchanged[command1-cycle] _____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 1 == 0
E    +  where 1 = <MagicMock name='check_change' id='139685558548000'>.call_count
____________ test_identical_read_output_unchanged[command1-history] ____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 1 == 0
E    +  where 1 = <MagicMock name='check_change' id='139685558548336'>.call_count
_____________ test_identical_read_output_unchanged[command2-clean] _____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 1 == 0
E    +  where 1 = <MagicMock name='check_change' id='139685558547664'>.call_count
____________ test_identical_read_output_unchanged[command2-broken] _____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 1 == 0
E    +  where 1 = <MagicMock name='check_change' id='139685558544640'>.call_count
_____________ test_identical_read_output_unchanged[command2-cycle] _____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 1 == 0
E    +  where 1 = <MagicMock name='check_change' id='139685558545984'>.call_count
____________ test_identical_read_output_unchanged[command2-history] ____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 1 == 0
E    +  where 1 = <MagicMock name='check_change' id='139685558545648'>.call_count
_____________ test_identical_read_output_unchanged[command3-clean] _____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 1 == 0
E    +  where 1 = <MagicMock name='check_change' id='139685558544976'>.call_count
____________ test_identical_read_output_unchanged[command3-broken] _____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 1 == 0
E    +  where 1 = <MagicMock name='check_change' id='139685558545648'>.call_count
_____________ test_identical_read_output_unchanged[command3-cycle] _____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 1 == 0
E    +  where 1 = <MagicMock name='check_change' id='139685558545984'>.call_count
____________ test_identical_read_output_unchanged[command3-history] ____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 1 == 0
E    +  where 1 = <MagicMock name='check_change' id='139685558544640'>.call_count
_____________ test_identical_read_output_unchanged[command4-clean] _____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 2 == 1
E    +  where 2 = <MagicMock name='check_change' id='139685558547664'>.call_count
____________ test_identical_read_output_unchanged[command4-broken] _____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 2 == 1
E    +  where 2 = <MagicMock name='check_change' id='139685558548336'>.call_count
_____________ test_identical_read_output_unchanged[command4-cycle] _____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 2 == 1
E    +  where 2 = <MagicMock name='check_change' id='139685558548000'>.call_count
____________ test_identical_read_output_unchanged[command4-history] ____________
tests/app/test_identical_reads.py:148: in test_identical_read_output_unchanged
    assert changes.call_count == (1 if "--gate" in command else 0)
E   AssertionError: assert 2 == 1
E    +  where 2 = <MagicMock name='check_change' id='139685558548672'>.call_count
______________________ test_derive_once_per_checked_read _______________________
tests/core/test_linear_derive.py:143: in test_derive_once_per_checked_read
    assert sum(calls.values()) == 1
E   assert 2 == 1
E    +  where 2 = sum(dict_values([1, 1]))
E    +    where dict_values([1, 1]) = <built-in method values of dict object at 0x7f0b13ff7180>()
E    +      where <built-in method values of dict object at 0x7f0b13ff7180> = {139685557433040: 1, 139685556776272: 1}.values
=========================== short test summary info ============================
FAILED tests/app/test_identical_reads.py::test_identical_trees_load_once[False-False]
FAILED tests/app/test_identical_reads.py::test_identical_trees_load_once[False-True]
FAILED tests/app/test_identical_reads.py::test_identical_trees_load_once[True-False]
FAILED tests/app/test_identical_reads.py::test_identical_trees_load_once[True-True]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command0-clean]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command0-broken]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command0-cycle]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command0-history]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command1-clean]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command1-broken]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command1-cycle]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command1-history]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command2-clean]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command2-broken]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command2-cycle]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command2-history]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command3-clean]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command3-broken]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command3-cycle]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command3-history]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command4-clean]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command4-broken]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command4-cycle]
FAILED tests/app/test_identical_reads.py::test_identical_read_output_unchanged[command4-history]
FAILED tests/core/test_linear_derive.py::test_derive_once_per_checked_read - ...
25 failed, 53 passed in 0.55s
```

## Implementation and proof

`read_checked` returns `read_state` directly when `(current.files, current.attachments)` equals `(published.files, published.attachments)`.
This is content equality, so differing revisions do not prevent reuse, while a byte difference, added or removed file, or attachment-set difference retains the original comparison.
The returned state retains the single current load, derivation, state-check result, failing IDs, and read metadata.
No published load, derivation, second state check, clock read, or change check is needed on equal inputs.
The gate in `app/reads.py` still loads its published tree and runs its existing comparison.

The proof against the existing checks is as follows.
Every problem of `check_state(after)` is in the published `known` set and would contribute only an already-published note, which `read_checked` already discards.
`_missing` finds every published decision, entry, and thread ID in the identical after-state.
`_dates`, `_imports_over_live`, `_unlisted_sources`, and the decision half of `_links_to_dead` iterate over new decisions or new records, of which there are none.
Check 4 compares each entry with itself, with equal derived statuses, so no create, edit, or retirement is wanted, and there are no new decisions listing create or link.
Check 5 compares each decision and thread with itself, so fields, messages, and thread states cannot differ.
The entry half of check 6 considers only `rests_on` targets absent from the published entry, of which there are none.
Area notes are also empty on identical inputs.

The initial targeted run passed 125 tests in 0.92 s.
The first gate attempts caught an unused import, test references to imported names that strict mypy does not export, and import ordering.
Those test-only issues were corrected without changing test behaviour.

## Full gate

`UV_FROZEN=true sh scripts/check.sh` passed: 583 files formatted, Ruff clean, strict mypy clean on 209 files, Vulture clean, 1,550 tests passed in 106.04 s, and `lodge check --gate` returned `ok`.
`git diff --check` passed.
The new files contain 48 self-comparison cases and 29 application cases; no timing assertions were added.
A separate review workload was running during the gate and initial small-store replay.
Only the named derivation-count test from Task 2 is edited; all other existing tests and Tasks 1 to 3 files remain unchanged.

## Timings

The stores are Task 1 synthetic stores under `/var/tmp/lodge-bench`, containing 1,607 (`s900`), 16,120 (`s9000`), and 160,800 (`s90000`) files.
The current executable is `/var/tmp/lodge-build/.venv/bin/lodge`; the preserved Task 1 executable is `/var/tmp/lodge-bench/venv-base/bin/lodge`.
Both use CPython 3.13.5 and PyYAML 6.0.3 on native disk.
Source and dependency bytecode were compiled with `uv run --frozen python -m compileall -q src .venv/lib` and the baseline environment's `python -m compileall -q` before timing.
The default command list is unchanged, with all twelve Task 1 commands, three measured runs per build, and seen mode.
Task 1 previously recorded a 900-second timeout for a single large-store baseline read; that baseline cost remains relevant to the comparison.

### s900

Command: `uv run --frozen python scripts/bench_reads.py /var/tmp/lodge-bench/s900 --lodge /var/tmp/lodge-build/.venv/bin/lodge --against /var/tmp/lodge-bench/venv-base/bin/lodge`.

Mode: `seen`; store: `s900`; runs: 3.

| Command | Build | Best (s) | Median (s) | Exit | Characters | Identical |
|---|---|---:|---:|---|---|---|
| `show {code}` | lodge | 0.945 | 0.947 | 0 | 255 | true |
| `show {code}` | against | 2.181 | 2.200 | 0 | 255 | true |
| `show {entry} --reasoning --provenance` | lodge | 0.881 | 0.903 | 0 | 454 | true |
| `show {entry} --reasoning --provenance` | against | 2.099 | 2.333 | 0 | 454 | true |
| `show {decision}` | lodge | 0.852 | 0.904 | 0 | 243 | true |
| `show {decision}` | against | 2.105 | 2.144 | 0 | 243 | true |
| `search berth --brief` | lodge | 0.931 | 1.081 | 0 | 2093 | true |
| `search berth --brief` | against | 2.120 | 2.267 | 0 | 2093 | true |
| `search "berth crane" --brief` | lodge | 0.938 | 0.948 | 0 | 2103 | true |
| `search "berth crane" --brief` | against | 2.178 | 2.282 | 0 | 2103 | true |
| `search {code} --brief` | lodge | 0.966 | 1.678 | 0 | 627 | true |
| `search {code} --brief` | against | 1.220 | 1.742 | 0 | 627 | true |
| `search berth` | lodge | 1.461 | 1.736 | 0 | 5006 | true |
| `search berth` | against | 1.189 | 1.202 | 0 | 5006 | true |
| `waiting` | lodge | 1.257 | 1.312 | 0 | 61 | true |
| `waiting` | against | 1.191 | 1.198 | 0 | 61 | true |
| `threads` | lodge | 0.963 | 1.052 | 0 | 16 | true |
| `threads` | against | 2.022 | 2.069 | 0 | 16 | true |
| `spec --area area-001` | lodge | 0.770 | 0.770 | 0 | 6217 | true |
| `spec --area area-001` | against | 1.729 | 1.996 | 0 | 6217 | true |
| `check` | lodge | 0.654 | 0.704 | 0 | 3 | true |
| `check` | against | 1.536 | 2.081 | 0 | 3 | true |
| `check --gate` | lodge | 0.947 | 0.959 | 0 | 3 | true |
| `check --gate` | against | 1.820 | 1.829 | 0 | 3 | true |

All twelve commands had identical standard output and exit status across all three measured runs.
These initial timings overlapped the gate and a separate review workload, so they are reported as observed and do not isolate the shortcut's speedup.
