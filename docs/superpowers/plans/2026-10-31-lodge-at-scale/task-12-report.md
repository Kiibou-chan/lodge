# Task 12 report

## Task 10c fix round, complete

B-2 and B-1 have app and end-to-end regressions written before their fixes.
The published-status regression kills a substitution of current statuses for published ones.
M-3 has exact-reader boundary tests; their injected facts lookup fails before implementation.
I-2 will follow the explicit dispatch: only published identities and their statuses are stored, with no published state check on indexed reads.
M-1 is left as a reported conflict: replacing or deleting a referenced bucket blob conflicts with Global Constraint 1, and reads already fall back to memory.
M-2 removes the thread default, and M-4 documents the facts-backed constructor.
No record operation has been run.

### Failing-test evidence

`uv run --frozen pytest` (focused regression or deliberate status mutant):

```text
FFFFFFFF                                                                 [100%]
=================================== FAILURES ===================================
________________ test_exact_hit_over_cap_writes_nothing[args0] _________________
tests/e2e/test_index_review_regressions.py:45: in test_exact_hit_over_cap_writes_nothing
    assert "BEGIN IMMEDIATE" not in statements
E   assert 'BEGIN IMMEDIATE' not in ['BEGIN IMMEDIATE', 'PRAGMA page_count', 'PRAGMA freelist_count', 'PRAGMA page_size', 'SELECT kept,written FROM meta', "SELECT k, v FROM 'main'.'words_config'", ...]
________________ test_exact_hit_over_cap_writes_nothing[args1] _________________
tests/e2e/test_index_review_regressions.py:45: in test_exact_hit_over_cap_writes_nothing
    assert "BEGIN IMMEDIATE" not in statements
E   assert 'BEGIN IMMEDIATE' not in ['BEGIN IMMEDIATE', 'PRAGMA page_count', 'PRAGMA freelist_count', 'PRAGMA page_size', 'SELECT kept,written FROM meta', "SELECT k, v FROM 'main'.'words_config'", ...]
________________ test_exact_hit_over_cap_writes_nothing[args2] _________________
tests/e2e/test_index_review_regressions.py:45: in test_exact_hit_over_cap_writes_nothing
    assert "BEGIN IMMEDIATE" not in statements
E   assert 'BEGIN IMMEDIATE' not in ['BEGIN IMMEDIATE', 'PRAGMA page_count', 'PRAGMA freelist_count', 'PRAGMA page_size', 'SELECT kept,written FROM meta', "SELECT k, v FROM 'main'.'words_config'", ...]
________________ test_exact_hit_over_cap_writes_nothing[args3] _________________
tests/e2e/test_index_review_regressions.py:45: in test_exact_hit_over_cap_writes_nothing
    assert "BEGIN IMMEDIATE" not in statements
E   assert 'BEGIN IMMEDIATE' not in ['BEGIN IMMEDIATE', 'PRAGMA page_count', 'PRAGMA freelist_count', 'PRAGMA page_size', 'SELECT kept,written FROM meta', "SELECT k, v FROM 'main'.'words_config'", ...]
__________ test_stored_id_shaped_code_prints_as_memory[False-d-fast] ___________
tests/e2e/test_index_review_regressions.py:75: in test_stored_id_shaped_code_prints_as_memory
    assert actual == expected
E   AssertionError: assert Result(code=2...med d-fast\n') == Result(code=0...t.\n', err='')
E
E     Differing attributes:
E     ['code', 'out', 'err']
E
E     Drill down into differing attribute code:
E       code: 2 != 0
E     ...
E
E     ...Full output truncated, use '-vv' to show
___________ test_stored_id_shaped_code_prints_as_memory[False-S-ab] ____________
tests/e2e/test_index_review_regressions.py:75: in test_stored_id_shaped_code_prints_as_memory
    assert actual == expected
E   AssertionError: assert Result(code=2...named S-ab\n') == Result(code=0...t.\n', err='')
E
E     Differing attributes:
E     ['code', 'out', 'err']
E
E     Drill down into differing attribute code:
E       code: 2 != 0
E     ...
E
E     ...Full output truncated, use '-vv' to show
___________ test_stored_id_shaped_code_prints_as_memory[True-d-fast] ___________
tests/e2e/test_index_review_regressions.py:75: in test_stored_id_shaped_code_prints_as_memory
    assert actual == expected
E   AssertionError: assert Result(code=2...med d-fast\n') == Result(code=2..., d-bbbbbb\n')
E
E     Omitting 2 identical items, use -vv to show
E     Differing attributes:
E     ['err']
E
E     Drill down into differing attribute err:
E       err: 'lodge: no record named d-fast\n' != 'lodge: the code d-fast names more than one record: d-aaaaaa, d-bbbbbb\n'
E       - lodge: the code d-fast names more than one record: d-aaaaaa, d-bbbbbb
E       + lodge: no record named d-fast
____________ test_stored_id_shaped_code_prints_as_memory[True-S-ab] ____________
tests/e2e/test_index_review_regressions.py:75: in test_stored_id_shaped_code_prints_as_memory
    assert actual == expected
E   AssertionError: assert Result(code=2...named S-ab\n') == Result(code=2..., d-bbbbbb\n')
E
E     Omitting 2 identical items, use -vv to show
E     Differing attributes:
E     ['err']
E
E     Drill down into differing attribute err:
E       err: 'lodge: no record named S-ab\n' != 'lodge: the code S-ab names more than one record: d-aaaaaa, d-bbbbbb\n'
E       - lodge: the code S-ab names more than one record: d-aaaaaa, d-bbbbbb
E       + lodge: no record named S-ab
=========================== short test summary info ============================
FAILED tests/e2e/test_index_review_regressions.py::test_exact_hit_over_cap_writes_nothing[args0]
FAILED tests/e2e/test_index_review_regressions.py::test_exact_hit_over_cap_writes_nothing[args1]
FAILED tests/e2e/test_index_review_regressions.py::test_exact_hit_over_cap_writes_nothing[args2]
FAILED tests/e2e/test_index_review_regressions.py::test_exact_hit_over_cap_writes_nothing[args3]
FAILED tests/e2e/test_index_review_regressions.py::test_stored_id_shaped_code_prints_as_memory[False-d-fast]
FAILED tests/e2e/test_index_review_regressions.py::test_stored_id_shaped_code_prints_as_memory[False-S-ab]
FAILED tests/e2e/test_index_review_regressions.py::test_stored_id_shaped_code_prints_as_memory[True-d-fast]
FAILED tests/e2e/test_index_review_regressions.py::test_stored_id_shaped_code_prints_as_memory[True-S-ab]
8 failed in 1.78s
```

`uv run --frozen pytest` (focused regression or deliberate status mutant):

```text
F                                                                        [100%]
=================================== FAILURES ===================================
_________________ test_published_statuses_differ_from_current __________________
tests/app/test_index_review_facts.py:43: in test_published_statuses_differ_from_current
    assert build(store, index).result == full.result
E   AssertionError: assert CheckResult(p...e)), notes=()) == CheckResult(p...e)), notes=())
E
E     Omitting 1 identical items, use -vv to show
E     Differing attributes:
E     ['problems']
E
E     Drill down into differing attribute problems:
E       problems: (Problem(path='lodge/decisions/d-aaaaaa-keep-whole-transcripts.md', check=2, message='d-aaaaaa: changes s-aaaaaa, which does not exist', line=None), Problem(path='lodge/decisions/d-bbbbbb-a-decision.md', check=2, message='d-bbbbbb: was published and is missing from this state', line=None)) != (Problem(path='lodge/decisions/d-aaaaaa-keep-whole-transcripts.md', check=2, message='d-aaaaaa: changes s-aaaaaa, which does not exist', line=None), ...
E
E     ...Full output truncated, use '-vv' to show
=========================== short test summary info ============================
FAILED tests/app/test_index_review_facts.py::test_published_statuses_differ_from_current
1 failed in 0.19s
```

Additional red evidence (the status-only and required-thread assertions fail on the old implementation; the exact-reader boundary is a deliberate mutant):

```text
FFFF..FFFFFF.FF....                                                      [100%]
=================================== FAILURES ===================================
________________ test_exact_hit_over_cap_writes_nothing[args0] _________________
tests/e2e/test_index_review_regressions.py:45: in test_exact_hit_over_cap_writes_nothing
    assert "BEGIN IMMEDIATE" not in statements
E   assert 'BEGIN IMMEDIATE' not in ['BEGIN IMMEDIATE', 'PRAGMA page_count', 'PRAGMA freelist_count', 'PRAGMA page_size', 'SELECT kept,written FROM meta', "SELECT k, v FROM 'main'.'words_config'", ...]
________________ test_exact_hit_over_cap_writes_nothing[args1] _________________
tests/e2e/test_index_review_regressions.py:45: in test_exact_hit_over_cap_writes_nothing
    assert "BEGIN IMMEDIATE" not in statements
E   assert 'BEGIN IMMEDIATE' not in ['BEGIN IMMEDIATE', 'PRAGMA page_count', 'PRAGMA freelist_count', 'PRAGMA page_size', 'SELECT kept,written FROM meta', "SELECT k, v FROM 'main'.'words_config'", ...]
________________ test_exact_hit_over_cap_writes_nothing[args2] _________________
tests/e2e/test_index_review_regressions.py:45: in test_exact_hit_over_cap_writes_nothing
    assert "BEGIN IMMEDIATE" not in statements
E   assert 'BEGIN IMMEDIATE' not in ['BEGIN IMMEDIATE', 'PRAGMA page_count', 'PRAGMA freelist_count', 'PRAGMA page_size', 'SELECT kept,written FROM meta', "SELECT k, v FROM 'main'.'words_config'", ...]
________________ test_exact_hit_over_cap_writes_nothing[args3] _________________
tests/e2e/test_index_review_regressions.py:45: in test_exact_hit_over_cap_writes_nothing
    assert "BEGIN IMMEDIATE" not in statements
E   assert 'BEGIN IMMEDIATE' not in ['BEGIN IMMEDIATE', 'PRAGMA page_count', 'PRAGMA freelist_count', 'PRAGMA page_size', 'SELECT kept,written FROM meta', "SELECT k, v FROM 'main'.'words_config'", ...]
____________ test_stored_id_shaped_code_prints_as_memory[True-d-x] _____________
tests/e2e/test_index_review_regressions.py:68: in test_stored_id_shaped_code_prints_as_memory
    assert index.db.execute("SELECT count(*) FROM states").fetchone()[0] >= 2
E   assert 1 >= 2
____________ test_stored_id_shaped_code_prints_as_memory[True-S-1] _____________
tests/e2e/test_index_review_regressions.py:68: in test_stored_id_shaped_code_prints_as_memory
    assert index.db.execute("SELECT count(*) FROM states").fetchone()[0] >= 2
E   assert 1 >= 2
_________________ test_id_shaped_codes_match_memory[False-d-x] _________________
tests/app/test_index_review_facts.py:26: in test_id_shaped_codes_match_memory
    assert actual == printed(app(store), ["show", code])
E   AssertionError: assert (2, '', 'lodg... named d-x\n') == (0, 'fetched ...10:00)\n', '')
E
E     At index 0 diff: 2 != 0
E     Use -v to get more diff
_________________ test_id_shaped_codes_match_memory[False-S-1] _________________
tests/app/test_index_review_facts.py:26: in test_id_shaped_codes_match_memory
    assert actual == printed(app(store), ["show", code])
E   AssertionError: assert (2, '', 'lodg... named S-1\n') == (0, 'fetched ...10:00)\n', '')
E
E     At index 0 diff: 2 != 0
E     Use -v to get more diff
_________________ test_id_shaped_codes_match_memory[True-d-x] __________________
tests/app/test_index_review_facts.py:26: in test_id_shaped_codes_match_memory
    assert actual == printed(app(store), ["show", code])
E   AssertionError: assert (2, '', 'lodg... named d-x\n') == (2, '', 'lodg..., d-bbbbbb\n')
E
E     At index 2 diff: 'lodge: no record named d-x\n' != 'lodge: the code d-x names more than one record: d-aaaaaa, d-bbbbbb\n'
E     Use -v to get more diff
_________________ test_id_shaped_codes_match_memory[True-S-1] __________________
tests/app/test_index_review_facts.py:26: in test_id_shaped_codes_match_memory
    assert actual == printed(app(store), ["show", code])
E   AssertionError: assert (2, '', 'lodg... named S-1\n') == (2, '', 'lodg..., d-bbbbbb\n')
E
E     At index 2 diff: 'lodge: no record named S-1\n' != 'lodge: the code S-1 names more than one record: d-aaaaaa, d-bbbbbb\n'
E     Use -v to get more diff
___________________ test_facts_store_only_published_statuses ___________________
tests/app/test_index_review_facts.py:53: in test_facts_store_only_published_statuses
    assert set(index.fact_values) == {published}
E   AssertionError: assert {'lodge/decis...93d01ebfa985'} == {'lodge/decis...93d01ebfa985'}
E
E     Extra items in the left set:
E     'lodge/decisions/d-aaaaaa-keep-whole-transcripts.md:86b675fe5f84a510da8601f8487509fa8636a51f\x00lodge/spec/storage/_ar...dce36ffcc4c2e0151b5aff\x00lodge/spec/storage/s-aaaaaa-transcripts-are-kept.md:fc2529e2cf4d4f6e1b2d18d537d893d01ebfa985'
E     Use -v to get more diff
_______________________ test_stored_threads_are_required _______________________
tests/app/test_index_review_facts.py:60: in test_stored_threads_are_required
    with pytest.raises(TypeError):
         ^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE TypeError
=========================== short test summary info ============================
FAILED tests/e2e/test_index_review_regressions.py::test_exact_hit_over_cap_writes_nothing[args0]
FAILED tests/e2e/test_index_review_regressions.py::test_exact_hit_over_cap_writes_nothing[args1]
FAILED tests/e2e/test_index_review_regressions.py::test_exact_hit_over_cap_writes_nothing[args2]
FAILED tests/e2e/test_index_review_regressions.py::test_exact_hit_over_cap_writes_nothing[args3]
FAILED tests/e2e/test_index_review_regressions.py::test_stored_id_shaped_code_prints_as_memory[True-d-x]
FAILED tests/e2e/test_index_review_regressions.py::test_stored_id_shaped_code_prints_as_memory[True-S-1]
FAILED tests/app/test_index_review_facts.py::test_id_shaped_codes_match_memory[False-d-x]
FAILED tests/app/test_index_review_facts.py::test_id_shaped_codes_match_memory[False-S-1]
FAILED tests/app/test_index_review_facts.py::test_id_shaped_codes_match_memory[True-d-x]
FAILED tests/app/test_index_review_facts.py::test_id_shaped_codes_match_memory[True-S-1]
FAILED tests/app/test_index_review_facts.py::test_facts_store_only_published_statuses
FAILED tests/app/test_index_review_facts.py::test_stored_threads_are_required
12 failed, 7 passed in 1.77s
```

Additional red evidence (the status-only and required-thread assertions fail on the old implementation; the exact-reader boundary is a deliberate mutant):

```text
FFFF                                                                     [100%]
=================================== FAILURES ===================================
_______________ test_exact_commands_ignore_poisoned_facts[args0] _______________
tests/app/test_index_review_facts.py:79: in test_exact_commands_ignore_poisoned_facts
    assert printed(app(store, index), args) == expected
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/app/indexed_support.py:75: in printed
    code = run(args, lambda: lodge, lambda: "", lambda *_: 0, lambda: 0)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/commands.py:85: in run
    return _check(make_lodge(), gate)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/commands.py:161: in _check
    result, read = lodge.check(gate)
                   ^^^^^^^^^^^^^^^^^
src/lodge/app/lodge.py:98: in check
    return reads.check(self._w, gate)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/reads.py:138: in check
    state = read_checked(w)
            ^^^^^^^^^^^^^^^
src/lodge/app/state.py:122: in read_checked
    state = read_state(w.store, w.index)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/state.py:95: in read_state
    snapshot = snapshot_of(current, index, parses, epoch=epoch)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/state.py:69: in snapshot_of
    index.facts(tree.rev)
<python>/unittest/mock.py:1169: in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/unittest/mock.py:1173: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/unittest/mock.py:1228: in _execute_mock_call
    raise effect
E   AssertionError: exact reader used facts
_______________ test_exact_commands_ignore_poisoned_facts[args1] _______________
tests/app/test_index_review_facts.py:79: in test_exact_commands_ignore_poisoned_facts
    assert printed(app(store, index), args) == expected
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/app/indexed_support.py:75: in printed
    code = run(args, lambda: lodge, lambda: "", lambda *_: 0, lambda: 0)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/commands.py:85: in run
    return _check(make_lodge(), gate)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/commands.py:161: in _check
    result, read = lodge.check(gate)
                   ^^^^^^^^^^^^^^^^^
src/lodge/app/lodge.py:98: in check
    return reads.check(self._w, gate)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/reads.py:138: in check
    state = read_checked(w)
            ^^^^^^^^^^^^^^^
src/lodge/app/state.py:122: in read_checked
    state = read_state(w.store, w.index)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/state.py:95: in read_state
    snapshot = snapshot_of(current, index, parses, epoch=epoch)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/state.py:69: in snapshot_of
    index.facts(tree.rev)
<python>/unittest/mock.py:1169: in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/unittest/mock.py:1173: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/unittest/mock.py:1228: in _execute_mock_call
    raise effect
E   AssertionError: exact reader used facts
_______________ test_exact_commands_ignore_poisoned_facts[args2] _______________
tests/app/test_index_review_facts.py:79: in test_exact_commands_ignore_poisoned_facts
    assert printed(app(store, index), args) == expected
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/app/indexed_support.py:75: in printed
    code = run(args, lambda: lodge, lambda: "", lambda *_: 0, lambda: 0)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/commands.py:87: in run
    text, read, _ = make_lodge().spec(area)
                    ^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/lodge.py:92: in spec
    return reads.spec(self._w, area)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/reads.py:128: in spec
    state = read_checked(w)
            ^^^^^^^^^^^^^^^
src/lodge/app/state.py:122: in read_checked
    state = read_state(w.store, w.index)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/state.py:95: in read_state
    snapshot = snapshot_of(current, index, parses, epoch=epoch)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/state.py:69: in snapshot_of
    index.facts(tree.rev)
<python>/unittest/mock.py:1169: in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/unittest/mock.py:1173: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/unittest/mock.py:1228: in _execute_mock_call
    raise effect
E   AssertionError: exact reader used facts
_______________ test_exact_commands_ignore_poisoned_facts[args3] _______________
tests/app/test_index_review_facts.py:75: in test_exact_commands_ignore_poisoned_facts
    assert app(store, index).add(drafts, dry_run=True) == expected
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/lodge.py:115: in add
    return writes.add(self._w, drafts, importing, dry_run, attachments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/writes.py:60: in add
    state = read_state(w.store, w.index)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/state.py:95: in read_state
    snapshot = snapshot_of(current, index, parses, epoch=epoch)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/state.py:69: in snapshot_of
    index.facts(tree.rev)
<python>/unittest/mock.py:1169: in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/unittest/mock.py:1173: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/unittest/mock.py:1228: in _execute_mock_call
    raise effect
E   AssertionError: exact reader used facts
=========================== short test summary info ============================
FAILED tests/app/test_index_review_facts.py::test_exact_commands_ignore_poisoned_facts[args0]
FAILED tests/app/test_index_review_facts.py::test_exact_commands_ignore_poisoned_facts[args1]
FAILED tests/app/test_index_review_facts.py::test_exact_commands_ignore_poisoned_facts[args2]
FAILED tests/app/test_index_review_facts.py::test_exact_commands_ignore_poisoned_facts[args3]
4 failed in 0.35s
```

## Fix-round implementation

B-2 returns from an empty `keep_parses` before any write transaction, retaining used parses and epoch recovery for non-empty writes.
B-1 checks the intact ID bucket, then resolves the code and its ambiguity exactly as the in-memory reader does.
The end-to-end codes are `d-fast` and `S-ab`, whose suffixes have real buckets; shorter `d-x` and `S-1` would fall back on a missing bucket and mask the defect, so the app tests cover those separately.
I-1 proves the published replaced status differs from current current status, and kills the swapped-status mutant.
I-2 stores status-only facts for published identities; the dispatch explicitly authorises this narrowing of the earlier d-dxqxsn policy.
A clean current identity equal to published still supplies its statuses without a second derivation.
Schema 7 prevents old value shapes from being reused.
M-2 makes threads required, M-3 proves all exact commands ignore poisoned facts and kills an injected facts lookup, and M-4 documents the sole constructor allowed to omit the derived object.
M-1 remains a plan conflict, as described above, with memory fallback retained.

Existing tests edited: `test_published_facts.py` follows the status-only shape and now compares against the exact `read_checked` oracle, `state_helpers.py` supplies required threads and status-only facts, and `test_index_states.py` follows that facts constructor.
The Task 10c Files list and facts hand-off are amended for these changes; no new port or package is introduced.
The focused suite passes 47 tests before the full gate.

Required-thread mutant, run against the final assertion:

```text
F                                                                        [100%]
=================================== FAILURES ===================================
_______________________ test_stored_threads_are_required _______________________
tests/app/test_index_review_facts.py:59: in test_stored_threads_are_required
    assert next(f for f in fields(StoredState) if f.name == "threads").default is MISSING
E   AssertionError: assert () is <dataclasses._MISSING_TYPE object at 0x7f6451dda270>
E    +  where () = Field(name='threads',type=tuple[str, ...],default=(),default_factory=<dataclasses._MISSING_TYPE object at 0x7f6451dda270>,init=True,repr=True,hash=None,compare=True,metadata=mappingproxy({}),kw_only=False,_field_type=_FIELD).default
E    +    where Field(name='threads',type=tuple[str, ...],default=(),default_factory=<dataclasses._MISSING_TYPE object at 0x7f6451dda270>,init=True,repr=True,hash=None,compare=True,metadata=mappingproxy({}),kw_only=False,_field_type=_FIELD) = next(<generator object test_stored_threads_are_required.<locals>.<genexpr> at 0x7f6450d4f780>)
=========================== short test summary info ============================
FAILED tests/app/test_index_review_facts.py::test_stored_threads_are_required
1 failed in 0.21s
```

The first full gate found `test_known_id_reads_its_bucket_once`: two bucket reads instead of one (2,207 passed, 39 skipped, one failed in 216.53 s).
The resolver now catches only a proven NotFound from its existing single bucket lookup before trying the code; damaged buckets still fall back.
The complete focused suite then passes 51 tests in 2.57 s.
The final `UV_FROZEN=1 sh scripts/check.sh` exits 0: Ruff format and lint, strict mypy over 295 files, Vulture, 2,208 tests passed and 39 skipped in 226.58 s, and `lodge check --gate` prints `ok` with the existing area-order note.
No timing is claimed in this fix round; Task 12 follows its push.

## Task 12 benchmark implementation

The fix round is committed and pushed as `a92836c`.
The replay gains chained distinct edits without cache restoration, epoch observations around every chained sample, isolated git configuration for every child, and start-up timings using the selected build's Python, best of nine.
Seen and changed baselines now prime both SECOND-1 sightings.
The README describes the disposable index and safe space reclamation.
The Task 12 Files list includes the new replay regression file and the existing timeout test's required two-sighting expectation.

Every new regression ran red before its implementation:

```text
E   assert 0 == 3
E    +  where 0 = len(set())
E    +    where set() = set([])
E   AssertionError: assert 4 == 5
E    +  where 4 = <Mock id='139728169448320'>.call_count
E   argparse.ArgumentError: argument --mode: invalid choice: 'chained' (choose from cold, seen, changed)
E   SystemExit: 2
E   SystemExit: 2
FAILED tests/test_bench_replay_options.py::test_chained_keeps_cache_and_distinct_edits
FAILED tests/test_bench_replay_options.py::test_seen_primes_both_sightings - ...
FAILED tests/test_bench_replay_options.py::test_git_config_reaches_every_child
FAILED tests/test_bench_replay_options.py::test_startup_uses_build_python_best_of_nine
4 failed in 0.77s
```

```text
E   TypeError: 'NoneType' object is not subscriptable
FAILED tests/test_bench_replay_options.py::test_epoch_probe_skips_incomplete_index
1 failed in 0.19s
```

Native-disk measurement follows, with production R11-A and 1,500 bytes per file unchanged.

Measurement completed: `s900`, `a1500`, every selected replay row compared with the exact reader in stdout, stderr, and exit status; three complete processes per timing.

Measurement completed: `s9000`, `a1500`, every selected replay row compared with the exact reader in stdout, stderr, and exit status; three complete processes per timing.

Preliminary native results: production seen `show {code}` is 0.142737 s at s900 and 0.304214 s at s9000, and seen `search berth --brief` is 0.163930 s and 0.585501 s respectively, best of three.
The s9000 baseline holds one complete state at 26,804,224 used bytes, above its 24,180,000-byte production cap; its changed samples clear and are cold.
Large-store cold measurement is in progress, with all completed samples equal to the exact reader.

The start-up helper also resolves an installed lodge command from PATH before selecting its sibling Python.
Its regression ran red first:

```text
E   AssertionError: assert ['python', '-c', 'pass'] == ['/synthetic/... '-c', 'pass']
E
E     At index 0 diff: 'python' != '/synthetic/venv/bin/python'
E     Use -v to get more diff
FAILED tests/test_bench_replay_options.py::test_startup_resolves_installed_lodge_python
1 failed in 0.15s
```

The replay-focused suite now passes 16 tests in 0.10 s, with strict mypy and Ruff green.
The four scratch sources were verified at runtime: every import comes from its intended copy, each cap has the requested value, and only the B copies call stat_current.
The base runtime matches the completed build: CPython 3.13.5, SQLite 3.47.1, PyYAML 6.0.3, and libyaml enabled.
No inherited attributes or injected git configuration overrides the no-conversion experiment.

The first complete large-store production point row is recorded: show by code is 2.002969 s seen, then 10.124897 s on the first changed sighting (epoch 1 to 2, cold clear), 12.010507 s on the second sighting through the complete keep, and 2.010119 s on the third, best of three.
The second sighting misses 3 s, and the seen rows miss 0.3 s.
The one complete state is 251,666,432 used and physical bytes against the 241,200,000-byte cap.
Every corresponding output and exit status equals the exact reader.

Measurement completed: `s90000`, `a1500`, every selected replay row compared with the exact reader in stdout, stderr, and exit status; three complete processes per timing.

The full large-store production command table is complete with exact-reader parity.
All three no-edit spec, check, and gate samples preserve the epoch, kept-state count, facts, and markers; the best gate time is 9.017 s.
The first five ten-cycle observations each clear once on the first read, keep one complete state on the second, and read it without a write on the third.
Facts remain one 3,329,566-byte published status map, with no dirty-ident growth.
The chained regression is strengthened to two commands; a deliberate counter reset reuses three edits and fails, while the implementation keeps all six edits distinct.

```text
E   AssertionError: assert 6 == 3
E    +  where 6 = len(['Berths hold cranes.\nBenchmark run 1.\n', 'Berths hold cranes.\nBenchmark run 2.\n', 'Berths hold cranes.\nBenchmark...old cranes.\nBenchmark run 1.\n', 'Berths hold cranes.\nBenchmark run 2.\n', 'Berths hold cranes.\nBenchmark run 3.\n'])
E    +  and   3 = len({'Berths hold cranes.\nBenchmark run 1.\n', 'Berths hold cranes.\nBenchmark run 2.\n', 'Berths hold cranes.\nBenchmark run 3.\n'})
E    +    where {'Berths hold cranes.\nBenchmark run 1.\n', 'Berths hold cranes.\nBenchmark run 2.\n', 'Berths hold cranes.\nBenchmark run 3.\n'} = set(['Berths hold cranes.\nBenchmark run 1.\n', 'Berths hold cranes.\nBenchmark run 2.\n', 'Berths hold cranes.\nBenchmark...old cranes.\nBenchmark run 1.\n', 'Berths hold cranes.\nBenchmark run 2.\n', 'Berths hold cranes.\nBenchmark run 3.\n'])
FAILED tests/test_bench_replay_options.py::test_chained_keeps_cache_and_distinct_edits
1 failed in 0.15s
```

The focused replay suite passes 16 tests in 0.11 s after that mutation is restored.

Ten edit/read/read/read cycles completed: `a1500`; epoch changes and complete-state counts are retained for every sighting.

The production ten-cycle run completes with ten clears in ten edit/read/read/read cycles.
One complete state is held after each second sighting, but zero fit under the cap.
The first changed read clears, the second keeps, and the third reads that state; facts remain one published map.
Chained epoch observations also carry each subprocess's exit status and stdout digest, enabling the hundred-read output audit.
The new audit assertion ran red before those fields were added:

```text
E   KeyError: 'exit'
FAILED tests/test_bench_replay_options.py::test_chained_keeps_cache_and_distinct_edits
1 failed in 0.14s
```

The focused replay suite passes 16 tests in 0.10 s, with Ruff and strict mypy green.

CONV-1 rows completed: `a1500`, seen and all three changed sightings, three samples, against the exact reader.

## Reproduction method

The scratch drivers and durable JSONL samples are retained under `/var/tmp/lodge-bench/task12/`.
The setup clones Task 1's synthetic stores without hard links and makes four compiled source copies of the completed application.
Its only application-code differences are the one R11 function body and the cap constant.
The commands run in the build worktree with the frozen environment:

```sh
uv run --frozen python /var/tmp/lodge-bench/task12/setup.py
uv run --frozen python /var/tmp/lodge-bench/task12/measure.py matrix
uv run --frozen python /var/tmp/lodge-bench/task12/measure.py small-options
uv run --frozen python /var/tmp/lodge-bench/task12/measure.py base
uv run --frozen python /var/tmp/lodge-bench/task12/measure.py diagnostics
uv run --frozen python /var/tmp/lodge-bench/task12/measure.py clear
```

These stages run sequentially, with no concurrent timed workload.
The base stage compares clean and edited inputs, with three attempts each.
Large-store base attempts are bounded to 20 s, with Task 1's original 900 s timeout recorded separately; no output equality is asserted for a timeout.
Every completed-build replay sample compares stdout, stderr, and status with `LODGE_INDEX=off` on the same bytes.
The changed samples restore the same primed baseline before each distinct edit, then time three successive commands through process exit.
The second includes the deferred complete keep after the successful output flush.
The third is read from the newly kept state.
The cap comparison uses ten distinct edits, each followed by three reads, without restoring the index.
The hundred-read chained experiment uses the product replay's new mode directly, without restoration between edits.

The synthetic generator has no threads, so the supplemental thread timing is a kept-state not-found answer, exit 2, rather than a successful thread read.
The main command list remains unchanged.
Changed check and gate samples intentionally exit 1 because the synthetic entry edit has no changing decision.
The optional FUSE timing is unavailable because no synthetic s90000 copy is at hand on FUSE under the permitted benchmark root.

Measurement completed: `s90000`, `a1900`, every selected replay row compared with the exact reader in stdout, stderr, and exit status; three complete processes per timing.

Ten edit/read/read/read cycles completed: `a1900`; epoch changes and complete-state counts are retained for every sighting.

R11-A with the scratch 1,900-byte cap completes ten cycles without a clear and holds four complete states.
Final used space is 266,768,384 bytes, physical size 267,333,632 bytes, against the 305,520,000-byte cap.
Facts remain one 3,329,566-byte map.
Its show-by-code row is 2.008 s seen, 6.134 s first changed, 11.661 s second changed, and 2.001 s third changed, rounded from best of three, with no clears.
The larger cap fixes this fixture's four-state capacity, but the target stop still applies independently to the read timings.

CONV-1 rows completed: `a1900`, seen and all three changed sightings, three samples, against the exact reader.

Measurement completed: `s90000`, `b1500`, every selected replay row compared with the exact reader in stdout, stderr, and exit status; three complete processes per timing.

Ten edit/read/read/read cycles completed: `b1500`; epoch changes and complete-state counts are retained for every sighting.

CONV-1 rows completed: `b1500`, seen and all three changed sightings, three samples, against the exact reader.

The preserved native base package is verified byte for byte against Task 1 commit d8cb076 for every Python and Markdown package source.
The three alternative source copies differ from the production copy only in the required R11 and cap files.
R11-B with the scratch 1,900-byte cap records show by code at 0.477424 s seen, 4.800864 s first changed, 10.317305 s second changed, and 0.478916 s third changed, best of three with no clears.
This row independently misses the point and changed limits.

Measurement completed: `s90000`, `b1900`, every selected replay row compared with the exact reader in stdout, stderr, and exit status; three complete processes per timing.

Ten edit/read/read/read cycles completed: `b1900`; epoch changes and complete-state counts are retained for every sighting.

All targeted large-store command rows are complete under all four combinations, with exact-reader output and status parity.
Both 1,500-byte variants clear ten times in ten cycles, holding one over-cap state and fitting zero complete states within the cap.
Both 1,900-byte variants retain four states and clear zero times.
R11-B with 1,900 bytes per file ends its cycles at 266,752,000 used bytes and 267,313,152 physical bytes.
The measured show-by-code seen miss independently triggers the stop under each combination, even before the search candidate counts are classified.
The conversion completion, hundred-read chained experiment, smaller-store alternatives, historical-base audit, and phase diagnostics remain in progress.

CONV-1 rows completed: `b1900`, seen and all three changed sightings, three samples, against the exact reader.

The production `--mode chained --runs 100` experiment completed without restoring the saved index, with the epoch before and after every edit/read.

Ten edit/read/read/read cycles completed: `a1500`; epoch changes and complete-state counts are retained for every sighting.

Measurement completed: `s900`, `a1900`, every selected replay row compared with the exact reader in stdout, stderr, and exit status; three complete processes per timing.

Ten edit/read/read/read cycles completed: `a1900`; epoch changes and complete-state counts are retained for every sighting.

The complete large-store matrix stage exits 0.
Its 1,122 timed replay samples all match the exact reader in stdout, stderr, and exit status.
The product replay's hundred-read chained run completes with one clear in 100 distinct changed reads, best 6.074 s and median 6.127 s through exit.
All hundred exit statuses are zero, and all stdout digests match the exact-reader reference.
This count is separate from the ten repeated-sighting cycles: every chained state is read once, so only markers and computed units are written.
The smaller-store alternatives are running next.

Measurement completed: `s900`, `b1500`, every selected replay row compared with the exact reader in stdout, stderr, and exit status; three complete processes per timing.

Ten edit/read/read/read cycles completed: `b1500`; epoch changes and complete-state counts are retained for every sighting.

Measurement completed: `s900`, `b1900`, every selected replay row compared with the exact reader in stdout, stderr, and exit status; three complete processes per timing.

Ten edit/read/read/read cycles completed: `b1900`; epoch changes and complete-state counts are retained for every sighting.

Ten edit/read/read/read cycles completed: `a1500`; epoch changes and complete-state counts are retained for every sighting.

Measurement completed: `s9000`, `a1900`, every selected replay row compared with the exact reader in stdout, stderr, and exit status; three complete processes per timing.

Ten edit/read/read/read cycles completed: `a1900`; epoch changes and complete-state counts are retained for every sighting.

Measurement completed: `s9000`, `b1500`, every selected replay row compared with the exact reader in stdout, stderr, and exit status; three complete processes per timing.

Ten edit/read/read/read cycles completed: `b1500`; epoch changes and complete-state counts are retained for every sighting.

Measurement completed: `s9000`, `b1900`, every selected replay row compared with the exact reader in stdout, stderr, and exit status; three complete processes per timing.

Ten edit/read/read/read cycles completed: `b1900`; epoch changes and complete-state counts are retained for every sighting.

Task 1 base replay completed: `s900`, clean and changed inputs; large-store attempts are bounded to 20 s each, with the original 900 s point-read timeout retained separately.

Task 1 base replay completed: `s9000`, clean and changed inputs; large-store attempts are bounded to 20 s each, with the original 900 s point-read timeout retained separately.

The smaller-store historical-base audit completes with no differences outside show and search.
For both sizes, clean and edited spec, check, gate, waiting, and threads outputs and statuses match; level-1 search berth also matches.
A 36-case audit verifies that original show bodies remain unchanged and that single-word brief ranking is identical after removing Task 6's documented current labels and heading.
The remaining differences are Task 5's context and multi-ref syntax, and Task 6's ranking, brief format, multi-query syntax, and phrase option.
At s90000, the historical base's completed attempts so far are censored at 20 s; equality is unavailable for those attempts.

### Rulings received during measurement

Commits `23a51e5` and `164e43e` arrived on the shared build branch during the historical-base replay.
Read through `lodge show --reasoning`, d-jwpwe7 chooses R11-B for STALE-1 and d-j51qmy chooses 1,900 bytes per file for DISK-1.
These questions are now ruled; the four-way table already includes the chosen combination.
The timed production source remains `a92836c`, R11-A and 1,500 bytes per file, as this dispatch explicitly requires.
Task 12 changes neither production switch nor cap; applying the new choices is a coordinator hand-off.
The benchmark source copies remain unchanged throughout the experiment.

Task 1 base replay completed: `s90000`, clean and changed inputs; large-store attempts are bounded to 20 s each, with the original 900 s point-read timeout retained separately.

### Completed historical-base replay

All 288 bounded base attempts finished: 210 processes completed, and 78 s90000 attempts timed out.
There are no unexpected differences in completed samples.
The eight differing show/search lines are named individually in `timings.md`, including their intentional Task 5 or Task 6 changes.
Large-store base equality remains unavailable for the 78 censored attempts.
This replay uses a shorter 20 s diagnostic bound for those fresh attempts; it does not claim to reproduce Task 1's 900 s timeout on every command.
Task 1's original bound is retained separately, and d-xc4nz9's reasoning explicitly distinguishes the smaller-store old/new proof from Task 12's largest-store measurement of the new build alone.
The shorter bound is a reported measurement limitation, with no fabricated equality or speed-up ratio.
The base stage exits 0, and the phase diagnostic stage now runs.

### Phase progress

The R11-A probes attribute about 1.76 s of a seen show read to identity and about 0.12 s to complete-state metadata decoding.
The second changed sighting includes complete-keep construction, particularly citers, rows, and bucket encoding, through process exit.
Candidate counts are measured before status filtering: 543 for the large-store code query, 69,208 for berth, 68,183 for tide, and 108,331 for the two-word and phrase queries.
The code query is judged against the 0.3 s seen limit and misses it; the other large-store searches are reported separately against the 1.0 s broad-search limit.
Start-up floors are 0.097967 to 0.102820 s for guide read, leaving about 0.20 s of the 0.3 s seen budget.
Phase timings are separate diagnostic runs with exclusive nested timings, rather than components spliced into the uninstrumented replay results.

Phase diagnostics completed for every targeted large-store seen row and all three changed sightings of show, in each combination; candidate counts are recorded for every search at every size.

### Phase diagnostics complete

All 216 phase samples completed, covering every targeted large-store seen row in all four combinations, all three changed show sightings, the supplemental thread miss, and candidate counts at both smaller sizes.
Every diagnostic stream matches its exact-reader reference after removing the diagnostic trailer.
R11-B diagnostics ran faster than the earlier uninstrumented matrix, so six additional same-state audit processes compare the probe with ordinary execution.
For R11-B/1,900, ordinary seen show is 0.335951 s best of three, and the probe is 0.338646 s, with equal output and unchanged metadata in every sample.
This check finds no probe-caused speed-up; it does not establish the reason for the difference from the earlier 0.477424 s matrix result.
The original matrix and later audit are both retained, and both trigger the 0.3 s stop.
The current full-state clear stage now runs on three independent SQLite copies.

A current full-state in-place clear is measured three times on independent SQLite copies, with unchanged inode and physical size, an incremented epoch, and secure_delete=OFF.

### Runtime verification and clear result

The final runtime check corrected an inaccurate draft environment label: the completed-build executable is native CPython 3.13.16 with SQLite 3.53.1, while the preserved Task 1 base is CPython 3.13.5 with SQLite 3.47.1.
Both use PyYAML 6.0.3 with libyaml and git 2.56.0.
The native executable and its virtual-environment link date from before Task 12; its current source/runtime digest, `fdf2cb6b420c3d85`, matches the index filename recorded by the completed matrix's chained run.
The draft's single-runtime claim was wrong, rather than a detected runtime replacement during measurement.
`timings.md` now distinguishes the runtimes, and no code-only speed-up ratio is claimed from that historical comparison.
The frozen workspace gate uses CPython 3.13.5 and SQLite 3.47.1, providing separate functional validation there.

The current full-state clear completes in 0.078891 s best of three on SQLite 3.53.1, with secure_delete=OFF.
It reduces used pages from 251,641,856 to 94,208 bytes, leaves the 251,641,856-byte physical file and inode unchanged, and increments the epoch once in every sample.
The source index is primed independently; its FTS layout can differ slightly from the earlier replay's complete state.
Task 9's 0.049078 s parse-only clear at 144,568,320 used bytes, SQLite 3.47.1, remains a separate historical row.

### Final helper regression

Final review found that the replay located its cache under a worktree's administrative git directory rather than the common git directory used by lodge.
A seventh new regression runs red on that mismatch before the lookup changes to `git rev-parse --path-format=absolute --git-common-dir`.
All three measured stores are standalone clones, where both directories are identical, so their existing timing and epoch samples remain applicable.
The focused replay suites now pass 17 tests, with Ruff lint and formatting checks green.
The full gate is repeated after this final helper change.

```text
F                                                                        [100%]
=================================== FAILURES ===================================
___________________ test_replay_observes_shared_common_cache ___________________
tests/test_bench_replay_options.py:209: in test_replay_observes_shared_common_cache
    assert replay.call_args.args[5] == common / "lodge"
E   AssertionError: assert PosixPath('/tmp/pytest-session/test_replay_observes_shared_co0/worktree-admin/lodge') == (PosixPath('/tmp/pytest-session/test_replay_observes_shared_co0/common') / 'lodge')
----------------------------- Captured stdout call -----------------------------
Mode: `chained`; store: `test_replay_observes_shared_co0`; runs: 3.

| Command | Build | Best (s) | Median (s) | Exit | Characters | Identical |
|---|---|---:|---:|---|---|---|
| `show A` | lodge | 0.010 | 0.010 | 0 | 2 | n/a |
=========================== short test summary info ============================
FAILED tests/test_bench_replay_options.py::test_replay_observes_shared_common_cache
1 failed in 0.16s
```

## Task 12 outcome

The replay options, README index paragraph, regression tests, amended Files list, and complete `timings.md` are built.
The final coverage audit exits 0:

```text
replay_samples=1602, cycle_samples=360, base_samples=288, base_timeouts=78
phase_samples=216, clear_samples=3, chained_samples=100, chained_clears=1
```

All 1,602 replay samples match the exact reader's stdout, stderr, and status.
All cycle streams and chained stdout digests and statuses match their references, and every seen or third-sighting replay leaves the recorded index metadata unchanged.
The complete timing table separates cold clears, searches over 5,000 candidates, and CONV-1 conversions, and includes the start-up floor, phases, clear cost, cap occupancy, and base audit.
The final production and scratch show-by-code summary at 160,800 files follows, in seconds through process exit:

| Rule / cap | Seen | Changed first | Changed second, including keep | Changed third | Complete states fitting | Clears in ten cycles | Stop |
|---|---:|---:|---:|---:|---:|---:|---|
| R11-A / 1,500 | 2.002969 | 10.124897 cold | 12.010507 | 2.010119 | 0 | 10 | STOP |
| R11-A / 1,900 | 2.008090 | 6.134215 | 11.660802 | 2.001470 | 4 | 0 | STOP |
| R11-B / 1,500 | 0.481090 | 8.802426 cold | 10.735255 | 0.477769 | 0 | 10 | STOP |
| R11-B / 1,900 | 0.477424 | 4.800864 | 10.317305 | 0.478916 | 4 | 0 | STOP |

Every combination triggers the stop, including the newly ruled R11-B/1,900 combination.
The server question goes to the coordinator; no server is implemented.
Production remains R11-A/1,500 as dispatched, and applying d-jwpwe7 and d-j51qmy is explicitly handed off.
No `lodge add` or other record-writing command was run.
Only the dispatched build worktree and synthetic benchmark area were changed.

### Concerns and limitations

- M-1 remains the reported conflict with referenced-blob immutability; memory fallback is retained.
- Historical-base equality is unavailable for 78 large-store attempts censored at the shorter 20 s bound; Task 1's original 900 s show timeout is reported separately.
- The historical base and completed build use different Python patch and SQLite versions, so their times do not isolate a code-only speed-up.
- Later R11-B ordinary and diagnostic reads are faster than the original matrix; both measurements remain recorded, and both exceed the target.
- The synthetic stores have no successful thread case, and no FUSE-mounted synthetic copy is at hand under the permitted benchmark root.
- The newly arrived author rulings are measured but intentionally not applied to production by this dispatch.

### Final validation

The gate before the final common-directory helper correction exits 0: 2,214 tests passed, 39 skipped in 203.17 s, with format, Ruff, strict mypy, Vulture, and `lodge check --gate` green.
The fresh full gate after the final correction exits 0: `UV_FROZEN=1 sh scripts/check.sh` passes formatting, Ruff, strict mypy over 296 source files, Vulture, and all 2,215 tests, with 39 skipped in 203.56 s.
`lodge check --gate` prints `ok` and the existing `area storage: order changed` note.
`git diff --check` and the public-path scan are clean.
Task 12 is complete and ready for review; the performance stop remains the recorded outcome.
