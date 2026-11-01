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
