# Tasks 1 and 2 build report

Work is confined to the build worktree on `read-speed-build`.
No records were added or edited in the project store.

## Task 1, complete

The task explicitly excludes pytest tests for the benchmark scripts.
The initial `uv run --frozen ruff check scripts` failed with four findings: E501 on lines 5, 7, and 49, and SIM905 on line 19 of `bench_store.py`.
After the lint-only fixes, rebuilding with `uv run --frozen python scripts/bench_store.py /var/tmp/lodge-bench/s900-ruff --decisions 900` gave tree `21480b1d4adfe40a05e7d206d7be896b162be844`, identical to the existing `s900` tree.
This verifies that the lint fixes preserve generated content before families and citers are added.

The builder now adds one sibling decision and one citing entry per fifty coded decisions, plus the entry coded `A` and its creation decision.
Rebuilt stores contain 1,607 files (`s900`), 16,120 files (`s9000`), and 160,800 files (`s90000`).
`bench_reads.py` implements argument placeholders, shell-free replay, best and median times, output and status comparison, and cold, seen, and changed modes.
The command list contains all twelve Task 1 commands.
Cold and changed smoke replays against the same installed build returned identical standard output and status; the changed store was clean afterwards.
`UV_FROZEN=true sh scripts/check.sh` passed: Ruff format and lint, strict mypy (196 files), Vulture, 1,402 tests in 47.71 s, and `lodge check --gate` (`ok`).
Timings use CPython 3.13.5, PyYAML 6.0.3, a compiled native-disk virtual environment, and stores on ext4.

### Task 1 timings: `s900`

Command: `uv run --frozen python scripts/bench_reads.py /var/tmp/lodge-bench/s900 --lodge /var/tmp/lodge-bench/venv-base/bin/lodge --against /var/tmp/lodge-bench/venv-base/bin/lodge`.
The second build is intentionally the same installed build, validating the comparison column.

Mode: `seen`; store: `s900`; runs: 3.

| Command | Build | Best (s) | Median (s) | Exit | Characters | Identical |
|---|---|---:|---:|---|---|---|
| `show {code}` | lodge | 1.076 | 1.077 | 0 | 255 | true |
| `show {code}` | against | 1.122 | 1.125 | 0 | 255 | true |
| `show {entry} --reasoning --provenance` | lodge | 1.084 | 1.084 | 0 | 454 | true |
| `show {entry} --reasoning --provenance` | against | 1.107 | 1.108 | 0 | 454 | true |
| `show {decision}` | lodge | 1.089 | 1.091 | 0 | 243 | true |
| `show {decision}` | against | 1.102 | 1.110 | 0 | 243 | true |
| `search berth --brief` | lodge | 1.123 | 1.127 | 0 | 2093 | true |
| `search berth --brief` | against | 1.134 | 1.135 | 0 | 2093 | true |
| `search "berth crane" --brief` | lodge | 1.126 | 1.136 | 0 | 2103 | true |
| `search "berth crane" --brief` | against | 1.178 | 1.193 | 0 | 2103 | true |
| `search {code} --brief` | lodge | 1.141 | 1.158 | 0 | 627 | true |
| `search {code} --brief` | against | 1.200 | 1.227 | 0 | 627 | true |
| `search berth` | lodge | 1.143 | 1.154 | 0 | 5006 | true |
| `search berth` | against | 1.128 | 1.132 | 0 | 5006 | true |
| `waiting` | lodge | 1.135 | 1.180 | 0 | 61 | true |
| `waiting` | against | 1.128 | 1.134 | 0 | 61 | true |
| `threads` | lodge | 1.141 | 1.144 | 0 | 16 | true |
| `threads` | against | 1.097 | 1.135 | 0 | 16 | true |
| `spec --area area-001` | lodge | 1.120 | 1.151 | 0 | 6217 | true |
| `spec --area area-001` | against | 1.128 | 1.135 | 0 | 6217 | true |
| `check` | lodge | 1.110 | 1.148 | 0 | 3 | true |
| `check` | against | 1.133 | 1.138 | 0 | 3 | true |
| `check --gate` | lodge | 1.635 | 1.652 | 0 | 3 | true |
| `check --gate` | against | 1.645 | 1.652 | 0 | 3 | true |

### Task 1 timings: `s9000`

Command: `uv run --frozen python scripts/bench_reads.py /var/tmp/lodge-bench/s9000 --lodge /var/tmp/lodge-bench/venv-base/bin/lodge`.

Mode: `seen`; store: `s9000`; runs: 3.

| Command | Build | Best (s) | Median (s) | Exit | Characters | Identical |
|---|---|---:|---:|---|---|---|
| `show {code}` | lodge | 15.552 | 15.672 | 0 | 249 | n/a |
| `show {entry} --reasoning --provenance` | lodge | 14.663 | 15.195 | 0 | 438 | n/a |
| `show {decision}` | lodge | 16.147 | 17.151 | 0 | 261 | n/a |
| `search berth --brief` | lodge | 15.589 | 15.868 | 0 | 2112 | n/a |
| `search "berth crane" --brief` | lodge | 15.429 | 15.705 | 0 | 2175 | n/a |
| `search {code} --brief` | lodge | 15.631 | 16.157 | 0 | 1804 | n/a |
| `search berth` | lodge | 15.405 | 15.487 | 0 | 5038 | n/a |
| `waiting` | lodge | 15.132 | 15.606 | 0 | 61 | n/a |
| `threads` | lodge | 15.342 | 15.608 | 0 | 16 | n/a |
| `spec --area area-001` | lodge | 15.228 | 16.155 | 0 | 8013 | n/a |
| `check` | lodge | 19.061 | 20.094 | 0 | 3 | n/a |
| `check --gate` | lodge | 24.674 | 27.579 | 0 | 3 | n/a |

### Task 1 large-store limit and concerns

The command file `/var/tmp/lodge-bench/show-code.txt` contains only `show {code}`.
Command: `timeout 900 uv run --frozen python scripts/bench_reads.py /var/tmp/lodge-bench/s90000 --lodge /var/tmp/lodge-bench/venv-base/bin/lodge --commands /var/tmp/lodge-bench/show-code.txt --runs 1 --mode cold`.
Result: exit status 124, not finished in 900 s, with no completed timing row.
This build has no index, so cold and seen modes have the same cache behaviour.
The large-store run is the explicitly requested single bounded attempt, rather than a best-of-three measurement.
The native-disk baseline build is preserved in `venv-base` for subsequent comparisons.
No existing tests were edited, and there are no unresolved Task 1 implementation concerns.

Task 1 commit: `d8cb076`, pushed to `origin/read-speed-build`.

## Task 2, complete

Step 0: the `ChangeFacts`, `change_facts`, `facts`, `derived`, and supplied-area-status interfaces were introduced before the tests.
`uv run --frozen pytest tests/test_structure.py -q` passed (39 tests), and `uv run --frozen mypy` passed (199 files).
The three new oracle support modules preserve the original algorithms; `linear_fixtures.py` supplies synthetic shapes and operation counters.
No existing tests were edited.

### Failing tests before implementation

Command: `uv run --frozen pytest tests/core/test_linear_checks.py tests/core/test_linear_derive.py tests/core/test_deep_chains.py tests/test_collector.py -q --tb=short`.
All eleven named tests failed before their implementations.
The following is the failing output with captured guide text omitted.

```text
FFFFFFFFFFF                                                              [100%]
=================================== FAILURES ===================================
______________________ test_missing_builds_the_union_once ______________________
tests/core/test_linear_checks.py:44: in test_missing_builds_the_union_once
    assert [decisions.keys_calls, specs.keys_calls, threads.keys_calls] == [1, 1, 1]
E   assert [2000, 2000, 2000] == [1, 1, 1]
E     
E     At index 0 diff: 2000 != 1
E     Use -v to get more diff
___________________ test_check_areas_same_problems_as_before ___________________
tests/core/test_linear_checks.py:64: in test_check_areas_same_problems_as_before
    assert not calls, "check_areas must use the supplied statuses"
E   AssertionError: check_areas must use the supplied statuses
E   assert not [Snapshot(decisions={'d-24w000': Decision(id='d-24w000', title='A decision', scope=<Scope.PRODUCT: 'product'>, decided...an-entry.md', 'd-24w000': 'lodge/decisions/d-24w000-a-decision.md'}, problems=(), attachments=frozenset(), threads={})]
_______________________ test_cycles_same_as_reachability _______________________
tests/core/test_linear_checks.py:81: in test_cycles_same_as_reachability
    assert counted.reads <= 8 * len(counted), "cycle detection must not walk from every entry"
E   AssertionError: cycle detection must not walk from every entry
E   assert 6400 <= (8 * 80)
E    +  where 6400 = <linear_fixtures.Counted object at 0x7f08bcab88a0>.reads
E    +  and   80 = len(<linear_fixtures.Counted object at 0x7f08bcab88a0>)
__________________________ test_dates_same_as_before ___________________________
tests/core/test_linear_checks.py:121: in test_dates_same_as_before
    assert ReadDecision.changes_reads <= 300, "earlier changes must be indexed once"
E   AssertionError: earlier changes must be indexed once
E   assert 930 <= 300
E    +  where 930 = ReadDecision.changes_reads
_________________ test_check_change_with_facts_equals_without __________________
tests/core/test_linear_checks.py:148: in test_check_change_with_facts_equals_without
    facts = change_facts(before, after)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/check_change.py:33: in change_facts
    raise NotImplementedError
E   NotImplementedError
__________________________ test_derive_same_as_before __________________________
tests/core/test_linear_derive.py:78: in test_derive_same_as_before
    assert ComparedDecision.comparisons <= 240, (
E   AssertionError: predecessors must not use list.index or prefix scans
E   assert 1800 <= 240
E    +  where 1800 = ComparedDecision.comparisons
_______________________ test_doubt_marks_same_as_before ________________________
tests/core/test_linear_derive.py:112: in test_doubt_marks_same_as_before
    assert counted.reads <= 8 * len(counted), "no doubts must not trigger a walk from every entry"
E   AssertionError: no doubts must not trigger a walk from every entry
E   assert 10100 <= (8 * 100)
E    +  where 10100 = <linear_fixtures.Counted object at 0x7f08bcefb230>.reads
E    +  and   100 = len(<linear_fixtures.Counted object at 0x7f08bcefb230>)
______________________ test_derive_once_per_checked_read _______________________
tests/core/test_linear_derive.py:137: in test_derive_once_per_checked_read
    assert sum(calls.values()) == 2
E   assert 8 == 2
E    +  where 8 = sum(dict_values([5, 3]))
E    +    where dict_values([5, 3]) = <built-in method values of dict object at 0x7f08bc647ec0>()
E    +      where <built-in method values of dict object at 0x7f08bc647ec0> = {139675499855312: 5, 139675499854672: 3}.values
__________________ test_chain_of_5000_checks_shows_and_orders __________________
tests/core/test_deep_chains.py:54: in test_chain_of_5000_checks_shows_and_orders
    branches = rests_on_tree(snapshot, derived, last)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/order.py:101: in rests_on_tree
    return children(entry_id, frozenset({entry_id}))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/order.py:95: in children
    return tuple(
src/lodge/core/order.py:96: in <genexpr>
    branch(target, ancestors)
src/lodge/core/order.py:88: in branch
    () if seen else children(target, ancestors | {target}),
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/order.py:95: in children
    return tuple(
src/lodge/core/order.py:96: in <genexpr>
    branch(target, ancestors)
src/lodge/core/order.py:88: in branch
    () if seen else children(target, ancestors | {target}),
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/order.py:95: in children
    return tuple(
src/lodge/core/order.py:96: in <genexpr>
    branch(target, ancestors)
src/lodge/core/order.py:96: in <genexpr>
    branch(target, ancestors)
src/lodge/core/order.py:88: in branch
    () if seen else children(target, ancestors | {target}),
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/order.py:95: in children
    return tuple(
src/lodge/core/order.py:96: in <genexpr>
    branch(target, ancestors)
src/lodge/core/order.py:88: in branch
    () if seen else children(target, ancestors | {target}),
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/order.py:95: in children
    return tuple(
src/lodge/core/order.py:96: in <genexpr>
    branch(target, ancestors)
src/lodge/core/order.py:88: in branch
    () if seen else children(target, ancestors | {target}),
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/order.py:95: in children
    return tuple(
src/lodge/core/order.py:96: in <genexpr>
    branch(target, ancestors)
E   RecursionError: maximum recursion depth exceeded
!!! Recursion error detected, but the origin of the recursion could not be located.
  Displaying first and last 10 stack frames out of 970.
  Pass `--full-trace` to see all frames.
____________ test_main_disables_the_collector_for_one_shot_commands ____________
tests/test_collector.py:20: in test_main_disables_the_collector_for_one_shot_commands
    assert not gc.isenabled()
E   assert not True
E    +  where True = <built-in function isenabled>()
E    +    where <built-in function isenabled> = gc.isenabled
________________________ test_view_keeps_the_collector _________________________
tests/test_collector.py:45: in test_view_keeps_the_collector
    assert not gc.isenabled(), "view and one-shot commands must take different collector paths"
E   AssertionError: view and one-shot commands must take different collector paths
E   assert not True
E    +  where True = <built-in function isenabled>()
E    +    where <built-in function isenabled> = gc.isenabled
=========================== short test summary info ============================
FAILED tests/core/test_linear_checks.py::test_missing_builds_the_union_once
FAILED tests/core/test_linear_checks.py::test_check_areas_same_problems_as_before
FAILED tests/core/test_linear_checks.py::test_cycles_same_as_reachability - A...
FAILED tests/core/test_linear_checks.py::test_dates_same_as_before - Assertio...
FAILED tests/core/test_linear_checks.py::test_check_change_with_facts_equals_without
FAILED tests/core/test_linear_derive.py::test_derive_same_as_before - Asserti...
FAILED tests/core/test_linear_derive.py::test_doubt_marks_same_as_before - As...
FAILED tests/core/test_linear_derive.py::test_derive_once_per_checked_read - ...
FAILED tests/core/test_deep_chains.py::test_chain_of_5000_checks_shows_and_orders
FAILED tests/test_collector.py::test_main_disables_the_collector_for_one_shot_commands
FAILED tests/test_collector.py::test_view_keeps_the_collector - AssertionErro...
11 failed in 5.21s
```

### Task 2 implementation and current validation

The checks now group area entries and count order duplicates once, find cycles with iterative Tarjan components, build the missing-ID union once, and index earlier decisions by changed entry.
Derivation uses running predecessors for both skip sets and constructs the known-ID set once; `derive.py` grows from 243 to 259 lines, within its twenty-line growth allowance.
Doubts propagate from their sources through reverse dependencies, preserving mark and dictionary order.
Dependency placement, dependency trees, and viewer branch HTML use explicit stacks.
Checked reads share `ChangeFacts` and supplied derived state, with exactly two derivations on the staged-store regression, one per snapshot.
The command-line entry point disables cyclic collection only for `argv=None` and a command other than `view`.
The eleven new tests pass (1.97 s); the deep regression covers all five requested check, core, spec, and viewer paths.
During validation, a synthetic fixture needed the new decision path added, test helper imports needed to follow the existing namespace layout, and Vulture rejected an unused copied `area_names` oracle, which was removed.
No production rule or tool configuration was weakened.

### Shape timings

Command: `uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/shapes.py`.
The fixtures are in-memory synthetic snapshots on the same native-disk Python environment, with collection disabled as in the one-shot CLI.
Every cell is the best of three runs, with snapshot construction outside the measured phases.

| Shape | Size | Derive (s) | State checks (s) | Change checks (s) | Total (s) |
|---|---:|---:|---:|---:|---:|
| one entry, many decisions | 2000 | 0.0043 | 0.0024 | 0.0036 | 0.0104 |
| chain, no doubts | 2000 | 0.0016 | 0.0019 | 0.0020 | 0.0056 |
| new decisions, published state | 2000 | 0.0165 | 0.0106 | 0.0136 | 0.0407 |
| one entry, many decisions | 4000 | 0.0085 | 0.0049 | 0.0070 | 0.0204 |
| chain, no doubts | 4000 | 0.0032 | 0.0039 | 0.0041 | 0.0111 |
| new decisions, published state | 4000 | 0.0341 | 0.0218 | 0.0278 | 0.0837 |
| one entry, many decisions | 8000 | 0.0174 | 0.0099 | 0.0143 | 0.0418 |
| chain, no doubts | 8000 | 0.0067 | 0.0080 | 0.0084 | 0.0231 |
| new decisions, published state | 8000 | 0.0719 | 0.0459 | 0.0585 | 0.1768 |

All three shapes roughly double their total time when their size doubles.

### Final gate

`UV_FROZEN=true sh scripts/check.sh` passed: 575 files formatted, Ruff clean, strict mypy clean (204 files), Vulture clean, 1,413 tests in 46.66 s, and `lodge check --gate` (`ok`).
The new fixture and typing corrections were included in this gate.

### Task 2 phase timings, original probe call pattern

A scratch copy of `probes/phases.py` removes both its `_missing` replacement function and its monkeypatch assignment, and puts its temporary SQLite file under the benchmark folder.
The repository probe remains unchanged.
Command, three times per store: `uv run --frozen python /var/tmp/lodge-bench/phases-task2.py /var/tmp/lodge-bench/STORE`.
These are best-of-three seconds, on the same compiled native-disk Python and stores as Task 1.
The existing probe enables its experimental C loader, which reported zero fallbacks in every run; this is diagnostic parse acceleration, not Task 3 implemented.
The original probe bypasses `main`, so cyclic collection remains enabled, and its `check_state(current)` phase also derives its own state.

| Phase | s9000 | s90000 |
|---|---:|---:|
| store.trees (walk and read, merge base, ls-tree, cat-file) | 0.509 | 5.035 |
| load(current) | 0.617 | 6.326 |
| check_state(current) | 0.069 | 1.819 |
| derive(current) | 0.040 | 1.398 |
| load(published) | 0.604 | 6.596 |
| check_change(published, current) | 0.228 | 5.002 |
| level1 of every record | 0.026 | 0.775 |
| search_counted('berth crane', 20) | 0.143 | 2.246 |
| pickle.dumps of every parsed record, one by one | 0.051 | 0.943 |
| pickle.loads of every parsed record, one by one | 0.058 | 1.605 |
| sqlite insert of every parsed record | 0.107 | 1.409 |
| sqlite select of every parsed record | 0.019 | 0.188 |
| sqlite insert of every level-1 line for one state | 0.043 | 0.572 |
| sqlite select of ten level-1 lines | 0.000 | 0.000 |

The illustrative SQLite files were 47.6 MB and 476.3 MB, respectively, and were removed by the probe.
Concern: the original standalone `check_state` call exceeds the expected one-second phase at the largest store, including its internal derivation.
A supplementary measurement below separates the supplied-derived check used in checked reads and disables collection as the one-shot CLI now does.

### Supplementary phase timings with the CLI collector setting

A second scratch copy adds `gc.disable()` and, after the existing derivation phase, times `check_state(s, derived=d)` separately.
This isolates the supplied-derived check used by the new read path; the original standalone check remains in the probe too.
Command, three times per store: `uv run --frozen python /var/tmp/lodge-bench/phases-task2-cli.py /var/tmp/lodge-bench/STORE`.
Everything else, including the experimental C loader, Python, and stores, matches the original probe measurements above.

| Phase | s9000 | s90000 |
|---|---:|---:|
| store.trees (walk and read, merge base, ls-tree, cat-file) | 0.489 | 4.943 |
| load(current) | 0.581 | 6.117 |
| check_state(current) | 0.068 | 1.395 |
| derive(current) | 0.036 | 0.950 |
| check_state(current, derived=d) | 0.024 | 0.424 |
| load(published) | 0.579 | 5.998 |
| check_change(published, current) | 0.187 | 3.680 |
| level1 of every record | 0.025 | 0.313 |
| search_counted('berth crane', 20) | 0.131 | 1.676 |
| pickle.dumps of every parsed record, one by one | 0.049 | 0.500 |
| pickle.loads of every parsed record, one by one | 0.054 | 0.531 |
| sqlite insert of every parsed record | 0.103 | 1.407 |
| sqlite select of every parsed record | 0.019 | 0.182 |
| sqlite insert of every level-1 line for one state | 0.041 | 0.585 |
| sqlite select of ten level-1 lines | 0.000 | 0.000 |

### Concerns and delivery

The supplied-derived state check is below one second at 160,800 files (0.424 s), while the standalone call including its derivation remains above it (1.395 s with collection disabled, 1.819 s with collection enabled).
This distinction is retained as a concern rather than treating the standalone phase as meeting the expectation.
The phase probe still computes standalone change facts and invokes derivation separately, so its phase sum is not an end-to-end checked-read timing.
The shape totals roughly double, and no correctness, structure, or gate concern remains.
Task 1 is commit `d8cb076`; Task 2 is the separate commit carrying this report.
The report includes both tasks as requested; no project records or existing tests were edited.
