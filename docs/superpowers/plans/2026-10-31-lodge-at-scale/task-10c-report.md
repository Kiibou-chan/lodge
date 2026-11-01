# Task 10c report

## Scope and authority

Task 10a's dispatched fix round precedes Task 10c.
The review is copied to `task-10a-review.md`.
The coordinator's shared-bucket ruling supersedes per-state bucket copies; immutable blobs are collected only after their final kept-state pointer disappears, in the same transaction.
The cap remains 1,500 bytes per tree file, with a 16 MiB floor, pending DISK-1.
Task 10c follows d-n65rhr (SECOND-1), d-dxqxsn, d-4j98ph, and d-q0tb8r; d-egknpk keeps conversions beside the targets.
Task 8c's interim R11-A identity remains unchanged.
No records are created by this work.

## Progress

Read the standing rules, Global Constraints, Review Focus, Tasks 9, 10a, 10b, and 10c, the progress ledger, the dispatched review, and the named decisions through `lodge show --reasoning`.
No agent work is waiting.
The signal-during-keep window (M-5) will be reported, as the review permits; `SystemExit` continues through the deferred keep boundary.

## Task 10a fix round: red evidence

The interface skeleton passed 39 structure tests and strict mypy (283 source files) before the new tests were written.
The authorised M-2 and M-3 hand-offs extend `StoredState` with thread IDs, distinguish a damaged bucket (`None`) from proven absence (`{}`), and allow marker and parse-only writes to receive the starting epoch and all used parses.
These amendments preserve existing writer calls and do not change the cap, identity, ranking, or gate decisions.

Command: `uv run --frozen pytest tests/gitstore/test_index_shared_buckets.py tests/gitstore/test_index_closed_streams.py -q`.
Result before implementation: **24 failed, 4 passed**.
The passing cases are stderr-closed controls for commands that previously flushed only stdout.
The failure output follows.

```text
FFFFFFFFFFFFFFFFFFF.F.FFF.F.                                             [100%]
=================================== FAILURES ===================================
__________________ test_bucket_blobs_are_shared_and_collected __________________

tmp_path = PosixPath('<pytest>/test_bucket_blobs_are_shared_a0')

    def test_bucket_blobs_are_shared_and_collected(tmp_path: Path) -> None:
        index = opened(tmp_path)
        keep(index, 'one')
>       before = index.db.execute('SELECT count(*) FROM bucket_blobs').fetchone()[0]
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       sqlite3.OperationalError: no such table: bucket_blobs

tests/gitstore/test_index_shared_buckets.py:21: OperationalError
__________________ test_bucket_rekeep_and_eviction_are_atomic __________________

tmp_path = PosixPath('<pytest>/test_bucket_rekeep_and_evictio0')

    def test_bucket_rekeep_and_eviction_are_atomic(tmp_path: Path) -> None:
        index = opened(tmp_path)
        keep(index)
>       before = index.db.execute('SELECT * FROM bucket_blobs ORDER BY hash').fetchall()
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       sqlite3.OperationalError: no such table: bucket_blobs

tests/gitstore/test_index_shared_buckets.py:44: OperationalError
______ test_nonstate_writer_retains_hits_after_clear[inside_write-marker] ______

tmp_path = PosixPath('<pytest>/test_nonstate_writer_retains_h0')
writer = 'marker', clear_at = 'inside_write'

    @pytest.mark.parametrize('writer', ['marker', 'parses'])
    @pytest.mark.parametrize('clear_at', ['inside_write', 'another_connection'])
    def test_nonstate_writer_retains_hits_after_clear(tmp_path: Path, writer: str, clear_at: str) -> None:
        index = opened(tmp_path)
        values = {('old', 'blob'): core.Problem('old', 1, 'synthetic'), ('new', 'blob'): None}
        index.keep_parses({('old', 'blob'): values['old', 'blob']}, files=2)
        epoch = index.epoch()
        if clear_at == 'another_connection':
            other = opened(tmp_path)
            with other.reading():
                assert other.parses([('old', 'blob')])
            other.db.execute('BEGIN IMMEDIATE')
            index_space.clear(other.db)
            other.db.execute('COMMIT')
            other.close()
        with patch.object(index_space, 'used_bytes', return_value=index_space.MIN_FILE_CAP + 1):
            if writer == 'marker':
                index.mark_seen('changed', {('new', 'blob'): None}, {}, files=1, used=values, epoch=epoch)
            else:
                index.keep_parses({('new', 'blob'): None}, files=1, used=values, epoch=epoch)
        assert index.epoch() > epoch
>       assert index.parses(list(values)) == values
E       AssertionError: assert {('new', 'blob'): None} == {('old', 'blo...'blob'): None}
E
E         Omitting 1 identical items, use -vv to show
E         Right contains 1 more item:
E         {('old', 'blob'): Problem(path='old', check=1, message='synthetic', line=None)}
E         Use -v to get more diff

tests/gitstore/test_index_shared_buckets.py:78: AssertionError
______ test_nonstate_writer_retains_hits_after_clear[inside_write-parses] ______

tmp_path = PosixPath('<pytest>/test_nonstate_writer_retains_h1')
writer = 'parses', clear_at = 'inside_write'

    @pytest.mark.parametrize('writer', ['marker', 'parses'])
    @pytest.mark.parametrize('clear_at', ['inside_write', 'another_connection'])
    def test_nonstate_writer_retains_hits_after_clear(tmp_path: Path, writer: str, clear_at: str) -> None:
        index = opened(tmp_path)
        values = {('old', 'blob'): core.Problem('old', 1, 'synthetic'), ('new', 'blob'): None}
        index.keep_parses({('old', 'blob'): values['old', 'blob']}, files=2)
        epoch = index.epoch()
        if clear_at == 'another_connection':
            other = opened(tmp_path)
            with other.reading():
                assert other.parses([('old', 'blob')])
            other.db.execute('BEGIN IMMEDIATE')
            index_space.clear(other.db)
            other.db.execute('COMMIT')
            other.close()
        with patch.object(index_space, 'used_bytes', return_value=index_space.MIN_FILE_CAP + 1):
            if writer == 'marker':
                index.mark_seen('changed', {('new', 'blob'): None}, {}, files=1, used=values, epoch=epoch)
            else:
                index.keep_parses({('new', 'blob'): None}, files=1, used=values, epoch=epoch)
        assert index.epoch() > epoch
>       assert index.parses(list(values)) == values
E       AssertionError: assert {('new', 'blob'): None} == {('old', 'blo...'blob'): None}
E
E         Omitting 1 identical items, use -vv to show
E         Right contains 1 more item:
E         {('old', 'blob'): Problem(path='old', check=1, message='synthetic', line=None)}
E         Use -v to get more diff

tests/gitstore/test_index_shared_buckets.py:78: AssertionError
___ test_nonstate_writer_retains_hits_after_clear[another_connection-marker] ___

tmp_path = PosixPath('<pytest>/test_nonstate_writer_retains_h2')
writer = 'marker', clear_at = 'another_connection'

    @pytest.mark.parametrize('writer', ['marker', 'parses'])
    @pytest.mark.parametrize('clear_at', ['inside_write', 'another_connection'])
    def test_nonstate_writer_retains_hits_after_clear(tmp_path: Path, writer: str, clear_at: str) -> None:
        index = opened(tmp_path)
        values = {('old', 'blob'): core.Problem('old', 1, 'synthetic'), ('new', 'blob'): None}
        index.keep_parses({('old', 'blob'): values['old', 'blob']}, files=2)
        epoch = index.epoch()
        if clear_at == 'another_connection':
            other = opened(tmp_path)
            with other.reading():
                assert other.parses([('old', 'blob')])
            other.db.execute('BEGIN IMMEDIATE')
            index_space.clear(other.db)
            other.db.execute('COMMIT')
            other.close()
        with patch.object(index_space, 'used_bytes', return_value=index_space.MIN_FILE_CAP + 1):
            if writer == 'marker':
                index.mark_seen('changed', {('new', 'blob'): None}, {}, files=1, used=values, epoch=epoch)
            else:
                index.keep_parses({('new', 'blob'): None}, files=1, used=values, epoch=epoch)
        assert index.epoch() > epoch
>       assert index.parses(list(values)) == values
E       AssertionError: assert {('new', 'blob'): None} == {('old', 'blo...'blob'): None}
E
E         Omitting 1 identical items, use -vv to show
E         Right contains 1 more item:
E         {('old', 'blob'): Problem(path='old', check=1, message='synthetic', line=None)}
E         Use -v to get more diff

tests/gitstore/test_index_shared_buckets.py:78: AssertionError
___ test_nonstate_writer_retains_hits_after_clear[another_connection-parses] ___

tmp_path = PosixPath('<pytest>/test_nonstate_writer_retains_h3')
writer = 'parses', clear_at = 'another_connection'

    @pytest.mark.parametrize('writer', ['marker', 'parses'])
    @pytest.mark.parametrize('clear_at', ['inside_write', 'another_connection'])
    def test_nonstate_writer_retains_hits_after_clear(tmp_path: Path, writer: str, clear_at: str) -> None:
        index = opened(tmp_path)
        values = {('old', 'blob'): core.Problem('old', 1, 'synthetic'), ('new', 'blob'): None}
        index.keep_parses({('old', 'blob'): values['old', 'blob']}, files=2)
        epoch = index.epoch()
        if clear_at == 'another_connection':
            other = opened(tmp_path)
            with other.reading():
                assert other.parses([('old', 'blob')])
            other.db.execute('BEGIN IMMEDIATE')
            index_space.clear(other.db)
            other.db.execute('COMMIT')
            other.close()
        with patch.object(index_space, 'used_bytes', return_value=index_space.MIN_FILE_CAP + 1):
            if writer == 'marker':
                index.mark_seen('changed', {('new', 'blob'): None}, {}, files=1, used=values, epoch=epoch)
            else:
                index.keep_parses({('new', 'blob'): None}, files=1, used=values, epoch=epoch)
        assert index.epoch() > epoch
>       assert index.parses(list(values)) == values
E       AssertionError: assert {('new', 'blob'): None} == {('old', 'blo...'blob'): None}
E
E         Omitting 1 identical items, use -vv to show
E         Right contains 1 more item:
E         {('old', 'blob'): Problem(path='old', check=1, message='synthetic', line=None)}
E         Use -v to get more diff

tests/gitstore/test_index_shared_buckets.py:78: AssertionError
_____________ test_app_marker_clear_retains_its_whole_working_set ______________

tmp_path = PosixPath('<pytest>/test_app_marker_clear_retains_0')

    def test_app_marker_clear_retains_its_whole_working_set(tmp_path: Path) -> None:
        store, index = project(True), opened(tmp_path)
        seed(store, index)
        path = next(p for p in store.files if FIRST.id in p)
        store.files[path] = store.files[path].replace('evidence', 'logs')
        with patch.object(index_space, 'used_bytes', return_value=index_space.MIN_FILE_CAP + 1):
            assert printed(app(store, index), ['show', FIRST.id]) == printed(app(store), ['show', FIRST.id])
        keys = set().union(*(set(zip(t.files, (t.blobs[p] for p in t.files))) for t in store.trees()))
>       assert set(index.parses(keys)) == keys
E       AssertionError: assert {('lodge/deci...688e7da03a6')} == {('lodge/deci...3d01ebfa985')}
E
E         Extra items in the right set:
E         ('lodge/spec/storage/_area.md', '954e112968e446a4a2dce36ffcc4c2e0151b5aff')
E         ('lodge/spec/storage/s-aaaaaa-transcripts-are-kept.md', 'fc2529e2cf4d4f6e1b2d18d537d893d01ebfa985')
E         ('lodge/decisions/d-aaaaaa-keep-whole-transcripts.md', '35ba5aa527706c3a4c0127804d9d2c246d916860')
E         Use -v to get more diff

tests/gitstore/test_index_shared_buckets.py:90: AssertionError
___________ test_parse_snapshot_clear_retains_its_whole_working_set ____________

tmp_path = PosixPath('<pytest>/test_parse_snapshot_clear_reta0')

    def test_parse_snapshot_clear_retains_its_whole_working_set(tmp_path: Path) -> None:
        store, index = project(), opened(tmp_path)
        snapshot_of(store.trees()[0], index)
        path = next(p for p in store.files if FIRST.id in p)
        store.files[path] = store.files[path].replace('evidence', 'logs')
        with patch.object(index_space, 'used_bytes', return_value=index_space.MIN_FILE_CAP + 1):
            snapshot_of(store.trees()[0], index)
        tree = store.trees()[0]
        keys = list(tree.blobs.items())
>       assert set(index.parses(keys)) == set(keys)
E       AssertionError: assert {('lodge/deci...688e7da03a6')} == {('lodge/deci...3d01ebfa985')}
E
E         Extra items in the right set:
E         ('lodge/spec/storage/_area.md', '954e112968e446a4a2dce36ffcc4c2e0151b5aff')
E         ('lodge/spec/storage/s-aaaaaa-transcripts-are-kept.md', 'fc2529e2cf4d4f6e1b2d18d537d893d01ebfa985')
E         Use -v to get more diff

tests/gitstore/test_index_shared_buckets.py:103: AssertionError
__________________________ test_cap_is_named_and_used __________________________

tmp_path = PosixPath('<pytest>/test_cap_is_named_and_used0')

    def test_cap_is_named_and_used(tmp_path: Path) -> None:
>       assert index_space.index_file_cap(1) == index_space.MIN_FILE_CAP
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/gitstore/test_index_shared_buckets.py:108:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

files = 1

    def index_file_cap(files: int) -> int:
>       raise NotImplementedError
E       NotImplementedError

src/lodge/gitstore/index_space.py:22: NotImplementedError
_________ test_unknown_ref_uses_complete_stored_state[False-d-zzzzzz] __________

tmp_path = PosixPath('<pytest>/test_unknown_ref_uses_complete0')
ref = 'd-zzzzzz', broken = False

    @pytest.mark.parametrize('ref', ['d-zzzzzz', 'nosuchcode', 'q-zzzzzz'])
    @pytest.mark.parametrize('broken', [False, True])
    def test_unknown_ref_uses_complete_stored_state(tmp_path: Path, ref: str, broken: bool) -> None:
        store, index = project(True), opened(tmp_path)
        if broken:
            store.files['lodge/decisions/broken.md'] = 'broken'
        seed(store, index)
        args = ['thread' if ref.startswith('q-') else 'show', ref]
        expected = printed(app(store), args)
        with patch.object(core, 'assemble', side_effect=AssertionError('rebuilt unknown ref')):
>           assert printed(app(store, index), args) == expected
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/gitstore/test_index_shared_buckets.py:129:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests/app/indexed_support.py:75: in printed
    code = run(args, lambda: lodge, lambda: "", lambda *_: 0, lambda: 0)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/commands.py:72: in run
    status = _show(lodge, refs, reasoning, provenance)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/commands.py:116: in _show
    result = lodge.show_many(refs, reasoning, provenance)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/lodge.py:76: in show_many
    result, self._keep = indexed.show_many(self._w, refs, reasoning, provenance)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:132: in show_many
    return _run(
src/lodge/app/indexed.py:97: in _run
    state, misses = _built(w, now, epoch)
                    ^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:48: in _built
    s = snapshot(current)
        ^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:46: in snapshot
    return core.assemble({path: parses[path, blob] for path, blob in keys}, listing.attachments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/lib/python3.13/unittest/mock.py:1169: in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/lib/python3.13/unittest/mock.py:1173: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <MagicMock name='assemble' id='140695276418928'>
args = ({'lodge/spec/storage/_area.md': Area(name='storage', title='Storage', intro='How it keeps data.', order=('s-aaaaaa',)...t='Do it.', where='a session', when='2026-10-28 10:00'), numbers=(), attachments=(), imported_from=None)}, frozenset())
kwargs = {}

    def _execute_mock_call(self, /, *args, **kwargs):
        # separate from _increment_mock_call so that awaited functions are
        # executed separately from their call, also AsyncMock overrides this method

        effect = self.side_effect
        if effect is not None:
            if _is_exception(effect):
>               raise effect
E               AssertionError: rebuilt unknown ref

<python>/lib/python3.13/unittest/mock.py:1228: AssertionError
________ test_unknown_ref_uses_complete_stored_state[False-nosuchcode] _________

tmp_path = PosixPath('<pytest>/test_unknown_ref_uses_complete1')
ref = 'nosuchcode', broken = False

    @pytest.mark.parametrize('ref', ['d-zzzzzz', 'nosuchcode', 'q-zzzzzz'])
    @pytest.mark.parametrize('broken', [False, True])
    def test_unknown_ref_uses_complete_stored_state(tmp_path: Path, ref: str, broken: bool) -> None:
        store, index = project(True), opened(tmp_path)
        if broken:
            store.files['lodge/decisions/broken.md'] = 'broken'
        seed(store, index)
        args = ['thread' if ref.startswith('q-') else 'show', ref]
        expected = printed(app(store), args)
        with patch.object(core, 'assemble', side_effect=AssertionError('rebuilt unknown ref')):
>           assert printed(app(store, index), args) == expected
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/gitstore/test_index_shared_buckets.py:129:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests/app/indexed_support.py:75: in printed
    code = run(args, lambda: lodge, lambda: "", lambda *_: 0, lambda: 0)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/commands.py:72: in run
    status = _show(lodge, refs, reasoning, provenance)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/commands.py:116: in _show
    result = lodge.show_many(refs, reasoning, provenance)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/lodge.py:76: in show_many
    result, self._keep = indexed.show_many(self._w, refs, reasoning, provenance)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:132: in show_many
    return _run(
src/lodge/app/indexed.py:97: in _run
    state, misses = _built(w, now, epoch)
                    ^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:48: in _built
    s = snapshot(current)
        ^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:46: in snapshot
    return core.assemble({path: parses[path, blob] for path, blob in keys}, listing.attachments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/lib/python3.13/unittest/mock.py:1169: in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/lib/python3.13/unittest/mock.py:1173: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <MagicMock name='assemble' id='140695276417584'>
args = ({'lodge/spec/storage/_area.md': Area(name='storage', title='Storage', intro='How it keeps data.', order=('s-aaaaaa',)...t='Do it.', where='a session', when='2026-10-28 10:00'), numbers=(), attachments=(), imported_from=None)}, frozenset())
kwargs = {}

    def _execute_mock_call(self, /, *args, **kwargs):
        # separate from _increment_mock_call so that awaited functions are
        # executed separately from their call, also AsyncMock overrides this method

        effect = self.side_effect
        if effect is not None:
            if _is_exception(effect):
>               raise effect
E               AssertionError: rebuilt unknown ref

<python>/lib/python3.13/unittest/mock.py:1228: AssertionError
_________ test_unknown_ref_uses_complete_stored_state[False-q-zzzzzz] __________

tmp_path = PosixPath('<pytest>/test_unknown_ref_uses_complete2')
ref = 'q-zzzzzz', broken = False

    @pytest.mark.parametrize('ref', ['d-zzzzzz', 'nosuchcode', 'q-zzzzzz'])
    @pytest.mark.parametrize('broken', [False, True])
    def test_unknown_ref_uses_complete_stored_state(tmp_path: Path, ref: str, broken: bool) -> None:
        store, index = project(True), opened(tmp_path)
        if broken:
            store.files['lodge/decisions/broken.md'] = 'broken'
        seed(store, index)
        args = ['thread' if ref.startswith('q-') else 'show', ref]
        expected = printed(app(store), args)
        with patch.object(core, 'assemble', side_effect=AssertionError('rebuilt unknown ref')):
>           assert printed(app(store, index), args) == expected
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/gitstore/test_index_shared_buckets.py:129:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests/app/indexed_support.py:75: in printed
    code = run(args, lambda: lodge, lambda: "", lambda *_: 0, lambda: 0)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/commands.py:97: in run
    status = run_thread(command, lodge)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/threads.py:93: in run_thread
    print(thread_text(lodge.thread(command.ref)))
                      ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/lodge.py:161: in thread
    result, self._keep = indexed.thread(self._w, ref)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:171: in thread
    return _run(w, lambda w: thread_reads.show(w, ref), cached)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:97: in _run
    state, misses = _built(w, now, epoch)
                    ^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:48: in _built
    s = snapshot(current)
        ^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:46: in snapshot
    return core.assemble({path: parses[path, blob] for path, blob in keys}, listing.attachments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/lib/python3.13/unittest/mock.py:1169: in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/lib/python3.13/unittest/mock.py:1173: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <MagicMock name='assemble' id='140695276418928'>
args = ({'lodge/spec/storage/_area.md': Area(name='storage', title='Storage', intro='How it keeps data.', order=('s-aaaaaa',)...t='Do it.', where='a session', when='2026-10-28 10:00'), numbers=(), attachments=(), imported_from=None)}, frozenset())
kwargs = {}

    def _execute_mock_call(self, /, *args, **kwargs):
        # separate from _increment_mock_call so that awaited functions are
        # executed separately from their call, also AsyncMock overrides this method

        effect = self.side_effect
        if effect is not None:
            if _is_exception(effect):
>               raise effect
E               AssertionError: rebuilt unknown ref

<python>/lib/python3.13/unittest/mock.py:1228: AssertionError
__________ test_unknown_ref_uses_complete_stored_state[True-d-zzzzzz] __________

tmp_path = PosixPath('<pytest>/test_unknown_ref_uses_complete3')
ref = 'd-zzzzzz', broken = True

    @pytest.mark.parametrize('ref', ['d-zzzzzz', 'nosuchcode', 'q-zzzzzz'])
    @pytest.mark.parametrize('broken', [False, True])
    def test_unknown_ref_uses_complete_stored_state(tmp_path: Path, ref: str, broken: bool) -> None:
        store, index = project(True), opened(tmp_path)
        if broken:
            store.files['lodge/decisions/broken.md'] = 'broken'
        seed(store, index)
        args = ['thread' if ref.startswith('q-') else 'show', ref]
        expected = printed(app(store), args)
        with patch.object(core, 'assemble', side_effect=AssertionError('rebuilt unknown ref')):
>           assert printed(app(store, index), args) == expected
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/gitstore/test_index_shared_buckets.py:129:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests/app/indexed_support.py:75: in printed
    code = run(args, lambda: lodge, lambda: "", lambda *_: 0, lambda: 0)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/commands.py:72: in run
    status = _show(lodge, refs, reasoning, provenance)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/commands.py:116: in _show
    result = lodge.show_many(refs, reasoning, provenance)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/lodge.py:76: in show_many
    result, self._keep = indexed.show_many(self._w, refs, reasoning, provenance)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:132: in show_many
    return _run(
src/lodge/app/indexed.py:97: in _run
    state, misses = _built(w, now, epoch)
                    ^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:48: in _built
    s = snapshot(current)
        ^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:46: in snapshot
    return core.assemble({path: parses[path, blob] for path, blob in keys}, listing.attachments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/lib/python3.13/unittest/mock.py:1169: in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/lib/python3.13/unittest/mock.py:1173: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <MagicMock name='assemble' id='140695276415568'>
args = ({'lodge/spec/storage/_area.md': Area(name='storage', title='Storage', intro='How it keeps data.', order=('s-aaaaaa',)...isions/broken.md', check=1, message='the file must start with a --- line opening its header', line=None)}, frozenset())
kwargs = {}

    def _execute_mock_call(self, /, *args, **kwargs):
        # separate from _increment_mock_call so that awaited functions are
        # executed separately from their call, also AsyncMock overrides this method

        effect = self.side_effect
        if effect is not None:
            if _is_exception(effect):
>               raise effect
E               AssertionError: rebuilt unknown ref

<python>/lib/python3.13/unittest/mock.py:1228: AssertionError
_________ test_unknown_ref_uses_complete_stored_state[True-nosuchcode] _________

tmp_path = PosixPath('<pytest>/test_unknown_ref_uses_complete4')
ref = 'nosuchcode', broken = True

    @pytest.mark.parametrize('ref', ['d-zzzzzz', 'nosuchcode', 'q-zzzzzz'])
    @pytest.mark.parametrize('broken', [False, True])
    def test_unknown_ref_uses_complete_stored_state(tmp_path: Path, ref: str, broken: bool) -> None:
        store, index = project(True), opened(tmp_path)
        if broken:
            store.files['lodge/decisions/broken.md'] = 'broken'
        seed(store, index)
        args = ['thread' if ref.startswith('q-') else 'show', ref]
        expected = printed(app(store), args)
        with patch.object(core, 'assemble', side_effect=AssertionError('rebuilt unknown ref')):
>           assert printed(app(store, index), args) == expected
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/gitstore/test_index_shared_buckets.py:129:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests/app/indexed_support.py:75: in printed
    code = run(args, lambda: lodge, lambda: "", lambda *_: 0, lambda: 0)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/commands.py:72: in run
    status = _show(lodge, refs, reasoning, provenance)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/commands.py:116: in _show
    result = lodge.show_many(refs, reasoning, provenance)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/lodge.py:76: in show_many
    result, self._keep = indexed.show_many(self._w, refs, reasoning, provenance)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:132: in show_many
    return _run(
src/lodge/app/indexed.py:97: in _run
    state, misses = _built(w, now, epoch)
                    ^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:48: in _built
    s = snapshot(current)
        ^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:46: in snapshot
    return core.assemble({path: parses[path, blob] for path, blob in keys}, listing.attachments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/lib/python3.13/unittest/mock.py:1169: in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/lib/python3.13/unittest/mock.py:1173: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <MagicMock name='assemble' id='140695276418256'>
args = ({'lodge/spec/storage/_area.md': Area(name='storage', title='Storage', intro='How it keeps data.', order=('s-aaaaaa',)...isions/broken.md', check=1, message='the file must start with a --- line opening its header', line=None)}, frozenset())
kwargs = {}

    def _execute_mock_call(self, /, *args, **kwargs):
        # separate from _increment_mock_call so that awaited functions are
        # executed separately from their call, also AsyncMock overrides this method

        effect = self.side_effect
        if effect is not None:
            if _is_exception(effect):
>               raise effect
E               AssertionError: rebuilt unknown ref

<python>/lib/python3.13/unittest/mock.py:1228: AssertionError
__________ test_unknown_ref_uses_complete_stored_state[True-q-zzzzzz] __________

tmp_path = PosixPath('<pytest>/test_unknown_ref_uses_complete5')
ref = 'q-zzzzzz', broken = True

    @pytest.mark.parametrize('ref', ['d-zzzzzz', 'nosuchcode', 'q-zzzzzz'])
    @pytest.mark.parametrize('broken', [False, True])
    def test_unknown_ref_uses_complete_stored_state(tmp_path: Path, ref: str, broken: bool) -> None:
        store, index = project(True), opened(tmp_path)
        if broken:
            store.files['lodge/decisions/broken.md'] = 'broken'
        seed(store, index)
        args = ['thread' if ref.startswith('q-') else 'show', ref]
        expected = printed(app(store), args)
        with patch.object(core, 'assemble', side_effect=AssertionError('rebuilt unknown ref')):
>           assert printed(app(store, index), args) == expected
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/gitstore/test_index_shared_buckets.py:129:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests/app/indexed_support.py:75: in printed
    code = run(args, lambda: lodge, lambda: "", lambda *_: 0, lambda: 0)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/commands.py:97: in run
    status = run_thread(command, lodge)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/cli/threads.py:93: in run_thread
    print(thread_text(lodge.thread(command.ref)))
                      ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/lodge.py:161: in thread
    result, self._keep = indexed.thread(self._w, ref)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:171: in thread
    return _run(w, lambda w: thread_reads.show(w, ref), cached)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:97: in _run
    state, misses = _built(w, now, epoch)
                    ^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:48: in _built
    s = snapshot(current)
        ^^^^^^^^^^^^^^^^^
src/lodge/app/indexed.py:46: in snapshot
    return core.assemble({path: parses[path, blob] for path, blob in keys}, listing.attachments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/lib/python3.13/unittest/mock.py:1169: in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<python>/lib/python3.13/unittest/mock.py:1173: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <MagicMock name='assemble' id='140695276417920'>
args = ({'lodge/spec/storage/_area.md': Area(name='storage', title='Storage', intro='How it keeps data.', order=('s-aaaaaa',)...isions/broken.md', check=1, message='the file must start with a --- line opening its header', line=None)}, frozenset())
kwargs = {}

    def _execute_mock_call(self, /, *args, **kwargs):
        # separate from _increment_mock_call so that awaited functions are
        # executed separately from their call, also AsyncMock overrides this method

        effect = self.side_effect
        if effect is not None:
            if _is_exception(effect):
>               raise effect
E               AssertionError: rebuilt unknown ref

<python>/lib/python3.13/unittest/mock.py:1228: AssertionError
_________________ test_unknown_id_with_damaged_bucket_rebuilds _________________

tmp_path = PosixPath('<pytest>/test_unknown_id_with_damaged_b0')

    def test_unknown_id_with_damaged_bucket_rebuilds(tmp_path: Path) -> None:
        store, index = project(), opened(tmp_path)
        seed(store, index)
>       index.db.execute("UPDATE buckets SET hash='missing' WHERE name='zz'")
E       sqlite3.OperationalError: no such column: hash

tests/gitstore/test_index_shared_buckets.py:136: OperationalError
_______________ test_closed_output_descriptor[False-command0-1] ________________

tmp_path = PosixPath('<pytest>/test_closed_output_descriptor_0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7ff62bef1db0>, fd = 1
command = ['show', 'd-aaaaaa'], index_off = False

    @pytest.mark.parametrize('fd', [1, 2])
    @pytest.mark.parametrize('command', [['show', 'd-aaaaaa'], ['waiting'], ['threads']])
    @pytest.mark.parametrize('index_off', [False, True])
    def test_closed_output_descriptor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fd: int, command: list[str], index_off: bool) -> None:
        _, repo = checkout_project(tmp_path)
        for path, text in files_of(decision(id='d-aaaaaa')).items():
            write(repo, path, text)
        git(repo, 'add', '--', 'lodge')
        git(repo, 'commit', '-m', 'Synthetic records')
        if index_off:
            monkeypatch.setenv('LODGE_INDEX', 'off')
        result = subprocess.run(['bash', '-c', f'exec "$@" {fd}>&-', 'closed-output', sys.executable, '-m', 'lodge.main', *command], cwd=repo, capture_output=True, text=True, timeout=10)
>       assert result.returncode == 0, result.stderr
E       AssertionError: Traceback (most recent call last):
E           File "<frozen runpy>", line 198, in _run_module_as_main
E           File "<frozen runpy>", line 88, in _run_code
E           File "/var/tmp/lodge-build/src/lodge/main.py", line 141, in <module>
E             raise SystemExit(main())
E                              ~~~~^^
E           File "/var/tmp/lodge-build/src/lodge/main.py", line 131, in main
E             return run(args, make, _init, _view, _hook)
E           File "/var/tmp/lodge-build/src/lodge/cli/commands.py", line 73, in run
E             sys.stdout.flush()
E             ^^^^^^^^^^^^^^^^
E         AttributeError: 'NoneType' object has no attribute 'flush'
E
E       assert 1 == 0
E        +  where 1 = CompletedProcess(args=['bash', '-c', 'exec "$@" 1>&-', 'closed-output', '/var/tmp/lodge-build/.venv/bin/python', '-m',...n run\n    sys.stdout.flush()\n    ^^^^^^^^^^^^^^^^\nAttributeError: \'NoneType\' object has no attribute \'flush\'\n').returncode

tests/gitstore/test_index_closed_streams.py:25: AssertionError
_______________ test_closed_output_descriptor[False-command0-2] ________________

tmp_path = PosixPath('<pytest>/test_closed_output_descriptor_1')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7ff62beccad0>, fd = 2
command = ['show', 'd-aaaaaa'], index_off = False

    @pytest.mark.parametrize('fd', [1, 2])
    @pytest.mark.parametrize('command', [['show', 'd-aaaaaa'], ['waiting'], ['threads']])
    @pytest.mark.parametrize('index_off', [False, True])
    def test_closed_output_descriptor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fd: int, command: list[str], index_off: bool) -> None:
        _, repo = checkout_project(tmp_path)
        for path, text in files_of(decision(id='d-aaaaaa')).items():
            write(repo, path, text)
        git(repo, 'add', '--', 'lodge')
        git(repo, 'commit', '-m', 'Synthetic records')
        if index_off:
            monkeypatch.setenv('LODGE_INDEX', 'off')
        result = subprocess.run(['bash', '-c', f'exec "$@" {fd}>&-', 'closed-output', sys.executable, '-m', 'lodge.main', *command], cwd=repo, capture_output=True, text=True, timeout=10)
>       assert result.returncode == 0, result.stderr
E       AssertionError:
E       assert 1 == 0
E        +  where 1 = CompletedProcess(args=['bash', '-c', 'exec "$@" 2>&-', 'closed-output', '/var/tmp/lodge-build/.venv/bin/python', '-m',...eturncode=1, stdout='d-aaaaaa · current · coordinator · 2026-10-28 · product\nA decision\n\nA statement.\n', stderr='').returncode

tests/gitstore/test_index_closed_streams.py:25: AssertionError
_______________ test_closed_output_descriptor[False-command1-1] ________________

tmp_path = PosixPath('<pytest>/test_closed_output_descriptor_2')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7ff62bf7cc90>, fd = 1
command = ['waiting'], index_off = False

    @pytest.mark.parametrize('fd', [1, 2])
    @pytest.mark.parametrize('command', [['show', 'd-aaaaaa'], ['waiting'], ['threads']])
    @pytest.mark.parametrize('index_off', [False, True])
    def test_closed_output_descriptor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fd: int, command: list[str], index_off: bool) -> None:
        _, repo = checkout_project(tmp_path)
        for path, text in files_of(decision(id='d-aaaaaa')).items():
            write(repo, path, text)
        git(repo, 'add', '--', 'lodge')
        git(repo, 'commit', '-m', 'Synthetic records')
        if index_off:
            monkeypatch.setenv('LODGE_INDEX', 'off')
        result = subprocess.run(['bash', '-c', f'exec "$@" {fd}>&-', 'closed-output', sys.executable, '-m', 'lodge.main', *command], cwd=repo, capture_output=True, text=True, timeout=10)
>       assert result.returncode == 0, result.stderr
E       AssertionError: Traceback (most recent call last):
E           File "<frozen runpy>", line 198, in _run_module_as_main
E           File "<frozen runpy>", line 88, in _run_code
E           File "/var/tmp/lodge-build/src/lodge/main.py", line 141, in <module>
E             raise SystemExit(main())
E                              ~~~~^^
E           File "/var/tmp/lodge-build/src/lodge/main.py", line 131, in main
E             return run(args, make, _init, _view, _hook)
E           File "/var/tmp/lodge-build/src/lodge/cli/commands.py", line 93, in run
E             sys.stdout.flush()
E             ^^^^^^^^^^^^^^^^
E         AttributeError: 'NoneType' object has no attribute 'flush'
E
E       assert 1 == 0
E        +  where 1 = CompletedProcess(args=['bash', '-c', 'exec "$@" 1>&-', 'closed-output', '/var/tmp/lodge-build/.venv/bin/python', '-m',...n run\n    sys.stdout.flush()\n    ^^^^^^^^^^^^^^^^\nAttributeError: \'NoneType\' object has no attribute \'flush\'\n').returncode

tests/gitstore/test_index_closed_streams.py:25: AssertionError
_______________ test_closed_output_descriptor[False-command2-1] ________________

tmp_path = PosixPath('<pytest>/test_closed_output_descriptor_4')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7ff62bf7e740>, fd = 1
command = ['threads'], index_off = False

    @pytest.mark.parametrize('fd', [1, 2])
    @pytest.mark.parametrize('command', [['show', 'd-aaaaaa'], ['waiting'], ['threads']])
    @pytest.mark.parametrize('index_off', [False, True])
    def test_closed_output_descriptor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fd: int, command: list[str], index_off: bool) -> None:
        _, repo = checkout_project(tmp_path)
        for path, text in files_of(decision(id='d-aaaaaa')).items():
            write(repo, path, text)
        git(repo, 'add', '--', 'lodge')
        git(repo, 'commit', '-m', 'Synthetic records')
        if index_off:
            monkeypatch.setenv('LODGE_INDEX', 'off')
        result = subprocess.run(['bash', '-c', f'exec "$@" {fd}>&-', 'closed-output', sys.executable, '-m', 'lodge.main', *command], cwd=repo, capture_output=True, text=True, timeout=10)
>       assert result.returncode == 0, result.stderr
E       AssertionError: Traceback (most recent call last):
E           File "<frozen runpy>", line 198, in _run_module_as_main
E           File "<frozen runpy>", line 88, in _run_code
E           File "/var/tmp/lodge-build/src/lodge/main.py", line 141, in <module>
E             raise SystemExit(main())
E                              ~~~~^^
E           File "/var/tmp/lodge-build/src/lodge/main.py", line 131, in main
E             return run(args, make, _init, _view, _hook)
E           File "/var/tmp/lodge-build/src/lodge/cli/commands.py", line 99, in run
E             sys.stdout.flush()
E             ^^^^^^^^^^^^^^^^
E         AttributeError: 'NoneType' object has no attribute 'flush'
E
E       assert 1 == 0
E        +  where 1 = CompletedProcess(args=['bash', '-c', 'exec "$@" 1>&-', 'closed-output', '/var/tmp/lodge-build/.venv/bin/python', '-m',...n run\n    sys.stdout.flush()\n    ^^^^^^^^^^^^^^^^\nAttributeError: \'NoneType\' object has no attribute \'flush\'\n').returncode

tests/gitstore/test_index_closed_streams.py:25: AssertionError
________________ test_closed_output_descriptor[True-command0-1] ________________

tmp_path = PosixPath('<pytest>/test_closed_output_descriptor_6')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7ff62bf7f8c0>, fd = 1
command = ['show', 'd-aaaaaa'], index_off = True

    @pytest.mark.parametrize('fd', [1, 2])
    @pytest.mark.parametrize('command', [['show', 'd-aaaaaa'], ['waiting'], ['threads']])
    @pytest.mark.parametrize('index_off', [False, True])
    def test_closed_output_descriptor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fd: int, command: list[str], index_off: bool) -> None:
        _, repo = checkout_project(tmp_path)
        for path, text in files_of(decision(id='d-aaaaaa')).items():
            write(repo, path, text)
        git(repo, 'add', '--', 'lodge')
        git(repo, 'commit', '-m', 'Synthetic records')
        if index_off:
            monkeypatch.setenv('LODGE_INDEX', 'off')
        result = subprocess.run(['bash', '-c', f'exec "$@" {fd}>&-', 'closed-output', sys.executable, '-m', 'lodge.main', *command], cwd=repo, capture_output=True, text=True, timeout=10)
>       assert result.returncode == 0, result.stderr
E       AssertionError: Traceback (most recent call last):
E           File "<frozen runpy>", line 198, in _run_module_as_main
E           File "<frozen runpy>", line 88, in _run_code
E           File "/var/tmp/lodge-build/src/lodge/main.py", line 141, in <module>
E             raise SystemExit(main())
E                              ~~~~^^
E           File "/var/tmp/lodge-build/src/lodge/main.py", line 131, in main
E             return run(args, make, _init, _view, _hook)
E           File "/var/tmp/lodge-build/src/lodge/cli/commands.py", line 73, in run
E             sys.stdout.flush()
E             ^^^^^^^^^^^^^^^^
E         AttributeError: 'NoneType' object has no attribute 'flush'
E
E       assert 1 == 0
E        +  where 1 = CompletedProcess(args=['bash', '-c', 'exec "$@" 1>&-', 'closed-output', '/var/tmp/lodge-build/.venv/bin/python', '-m',...n run\n    sys.stdout.flush()\n    ^^^^^^^^^^^^^^^^\nAttributeError: \'NoneType\' object has no attribute \'flush\'\n').returncode

tests/gitstore/test_index_closed_streams.py:25: AssertionError
________________ test_closed_output_descriptor[True-command0-2] ________________

tmp_path = PosixPath('<pytest>/test_closed_output_descriptor_7')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7ff62bf7f380>, fd = 2
command = ['show', 'd-aaaaaa'], index_off = True

    @pytest.mark.parametrize('fd', [1, 2])
    @pytest.mark.parametrize('command', [['show', 'd-aaaaaa'], ['waiting'], ['threads']])
    @pytest.mark.parametrize('index_off', [False, True])
    def test_closed_output_descriptor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fd: int, command: list[str], index_off: bool) -> None:
        _, repo = checkout_project(tmp_path)
        for path, text in files_of(decision(id='d-aaaaaa')).items():
            write(repo, path, text)
        git(repo, 'add', '--', 'lodge')
        git(repo, 'commit', '-m', 'Synthetic records')
        if index_off:
            monkeypatch.setenv('LODGE_INDEX', 'off')
        result = subprocess.run(['bash', '-c', f'exec "$@" {fd}>&-', 'closed-output', sys.executable, '-m', 'lodge.main', *command], cwd=repo, capture_output=True, text=True, timeout=10)
>       assert result.returncode == 0, result.stderr
E       AssertionError:
E       assert 1 == 0
E        +  where 1 = CompletedProcess(args=['bash', '-c', 'exec "$@" 2>&-', 'closed-output', '/var/tmp/lodge-build/.venv/bin/python', '-m',...eturncode=1, stdout='d-aaaaaa · current · coordinator · 2026-10-28 · product\nA decision\n\nA statement.\n', stderr='').returncode

tests/gitstore/test_index_closed_streams.py:25: AssertionError
________________ test_closed_output_descriptor[True-command1-1] ________________

tmp_path = PosixPath('<pytest>/test_closed_output_descriptor_8')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7ff62bf7f850>, fd = 1
command = ['waiting'], index_off = True

    @pytest.mark.parametrize('fd', [1, 2])
    @pytest.mark.parametrize('command', [['show', 'd-aaaaaa'], ['waiting'], ['threads']])
    @pytest.mark.parametrize('index_off', [False, True])
    def test_closed_output_descriptor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fd: int, command: list[str], index_off: bool) -> None:
        _, repo = checkout_project(tmp_path)
        for path, text in files_of(decision(id='d-aaaaaa')).items():
            write(repo, path, text)
        git(repo, 'add', '--', 'lodge')
        git(repo, 'commit', '-m', 'Synthetic records')
        if index_off:
            monkeypatch.setenv('LODGE_INDEX', 'off')
        result = subprocess.run(['bash', '-c', f'exec "$@" {fd}>&-', 'closed-output', sys.executable, '-m', 'lodge.main', *command], cwd=repo, capture_output=True, text=True, timeout=10)
>       assert result.returncode == 0, result.stderr
E       AssertionError: Traceback (most recent call last):
E           File "<frozen runpy>", line 198, in _run_module_as_main
E           File "<frozen runpy>", line 88, in _run_code
E           File "/var/tmp/lodge-build/src/lodge/main.py", line 141, in <module>
E             raise SystemExit(main())
E                              ~~~~^^
E           File "/var/tmp/lodge-build/src/lodge/main.py", line 131, in main
E             return run(args, make, _init, _view, _hook)
E           File "/var/tmp/lodge-build/src/lodge/cli/commands.py", line 93, in run
E             sys.stdout.flush()
E             ^^^^^^^^^^^^^^^^
E         AttributeError: 'NoneType' object has no attribute 'flush'
E
E       assert 1 == 0
E        +  where 1 = CompletedProcess(args=['bash', '-c', 'exec "$@" 1>&-', 'closed-output', '/var/tmp/lodge-build/.venv/bin/python', '-m',...n run\n    sys.stdout.flush()\n    ^^^^^^^^^^^^^^^^\nAttributeError: \'NoneType\' object has no attribute \'flush\'\n').returncode

tests/gitstore/test_index_closed_streams.py:25: AssertionError
________________ test_closed_output_descriptor[True-command2-1] ________________

tmp_path = PosixPath('<pytest>/test_closed_output_descriptor_10')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7ff62bf7f700>, fd = 1
command = ['threads'], index_off = True

    @pytest.mark.parametrize('fd', [1, 2])
    @pytest.mark.parametrize('command', [['show', 'd-aaaaaa'], ['waiting'], ['threads']])
    @pytest.mark.parametrize('index_off', [False, True])
    def test_closed_output_descriptor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fd: int, command: list[str], index_off: bool) -> None:
        _, repo = checkout_project(tmp_path)
        for path, text in files_of(decision(id='d-aaaaaa')).items():
            write(repo, path, text)
        git(repo, 'add', '--', 'lodge')
        git(repo, 'commit', '-m', 'Synthetic records')
        if index_off:
            monkeypatch.setenv('LODGE_INDEX', 'off')
        result = subprocess.run(['bash', '-c', f'exec "$@" {fd}>&-', 'closed-output', sys.executable, '-m', 'lodge.main', *command], cwd=repo, capture_output=True, text=True, timeout=10)
>       assert result.returncode == 0, result.stderr
E       AssertionError: Traceback (most recent call last):
E           File "<frozen runpy>", line 198, in _run_module_as_main
E           File "<frozen runpy>", line 88, in _run_code
E           File "/var/tmp/lodge-build/src/lodge/main.py", line 141, in <module>
E             raise SystemExit(main())
E                              ~~~~^^
E           File "/var/tmp/lodge-build/src/lodge/main.py", line 131, in main
E             return run(args, make, _init, _view, _hook)
E           File "/var/tmp/lodge-build/src/lodge/cli/commands.py", line 99, in run
E             sys.stdout.flush()
E             ^^^^^^^^^^^^^^^^
E         AttributeError: 'NoneType' object has no attribute 'flush'
E
E       assert 1 == 0
E        +  where 1 = CompletedProcess(args=['bash', '-c', 'exec "$@" 1>&-', 'closed-output', '/var/tmp/lodge-build/.venv/bin/python', '-m',...n run\n    sys.stdout.flush()\n    ^^^^^^^^^^^^^^^^\nAttributeError: \'NoneType\' object has no attribute \'flush\'\n').returncode

tests/gitstore/test_index_closed_streams.py:25: AssertionError
=========================== short test summary info ============================
FAILED tests/gitstore/test_index_shared_buckets.py::test_bucket_blobs_are_shared_and_collected
FAILED tests/gitstore/test_index_shared_buckets.py::test_bucket_rekeep_and_eviction_are_atomic
FAILED tests/gitstore/test_index_shared_buckets.py::test_nonstate_writer_retains_hits_after_clear[inside_write-marker]
FAILED tests/gitstore/test_index_shared_buckets.py::test_nonstate_writer_retains_hits_after_clear[inside_write-parses]
FAILED tests/gitstore/test_index_shared_buckets.py::test_nonstate_writer_retains_hits_after_clear[another_connection-marker]
FAILED tests/gitstore/test_index_shared_buckets.py::test_nonstate_writer_retains_hits_after_clear[another_connection-parses]
FAILED tests/gitstore/test_index_shared_buckets.py::test_app_marker_clear_retains_its_whole_working_set
FAILED tests/gitstore/test_index_shared_buckets.py::test_parse_snapshot_clear_retains_its_whole_working_set
FAILED tests/gitstore/test_index_shared_buckets.py::test_cap_is_named_and_used
FAILED tests/gitstore/test_index_shared_buckets.py::test_unknown_ref_uses_complete_stored_state[False-d-zzzzzz]
FAILED tests/gitstore/test_index_shared_buckets.py::test_unknown_ref_uses_complete_stored_state[False-nosuchcode]
FAILED tests/gitstore/test_index_shared_buckets.py::test_unknown_ref_uses_complete_stored_state[False-q-zzzzzz]
FAILED tests/gitstore/test_index_shared_buckets.py::test_unknown_ref_uses_complete_stored_state[True-d-zzzzzz]
FAILED tests/gitstore/test_index_shared_buckets.py::test_unknown_ref_uses_complete_stored_state[True-nosuchcode]
FAILED tests/gitstore/test_index_shared_buckets.py::test_unknown_ref_uses_complete_stored_state[True-q-zzzzzz]
FAILED tests/gitstore/test_index_shared_buckets.py::test_unknown_id_with_damaged_bucket_rebuilds
FAILED tests/gitstore/test_index_closed_streams.py::test_closed_output_descriptor[False-command0-1]
FAILED tests/gitstore/test_index_closed_streams.py::test_closed_output_descriptor[False-command0-2]
FAILED tests/gitstore/test_index_closed_streams.py::test_closed_output_descriptor[False-command1-1]
FAILED tests/gitstore/test_index_closed_streams.py::test_closed_output_descriptor[False-command2-1]
FAILED tests/gitstore/test_index_closed_streams.py::test_closed_output_descriptor[True-command0-1]
FAILED tests/gitstore/test_index_closed_streams.py::test_closed_output_descriptor[True-command0-2]
FAILED tests/gitstore/test_index_closed_streams.py::test_closed_output_descriptor[True-command1-1]
FAILED tests/gitstore/test_index_closed_streams.py::test_closed_output_descriptor[True-command2-1]
24 failed, 4 passed in 3.39s
```

Missing-blob completeness regression, before its fix: `uv run --frozen pytest tests/gitstore/test_index_shared_buckets.py::test_missing_blob_invalidates_completeness -q`.

```text
F                                                                        [100%]
=================================== FAILURES ===================================
__________________ test_missing_blob_invalidates_completeness __________________

tmp_path = PosixPath('<pytest>/test_missing_blob_invalidates_0')

    def test_missing_blob_invalidates_completeness(tmp_path: Path) -> None:
        index = opened(tmp_path)
        keep(index)
        index.db.execute("DELETE FROM bucket_blobs WHERE hash IN (SELECT hash FROM buckets WHERE name='aa')")
>       assert index.state('one') is None
E       AssertionError: assert StoredState(key='one', current='one', published='published', promised=(1024, 1, 1), valid_from=None, valid_until=None, codes={'a': ('s-aaaaaa',)}, citers={'a': 0}, unrecorded=(), threads=()) is None
E        +  where StoredState(key='one', current='one', published='published', promised=(1024, 1, 1), valid_from=None, valid_until=None, codes={'a': ('s-aaaaaa',)}, citers={'a': 0}, unrecorded=(), threads=()) = state('one')
E        +    where state = <lodge.gitstore.index_db.IndexDB object at 0x7f2dfd3c0d70>.state

tests/gitstore/test_index_shared_buckets.py:160: AssertionError
=========================== short test summary info ============================
FAILED tests/gitstore/test_index_shared_buckets.py::test_missing_blob_invalidates_completeness
1 failed in 0.22s
```

## Task 10a fix round: implementation

Schema 5 stores distinct immutable bucket blobs by full content hash and per-state bucket pointers.
Eviction and replacement remove pointers, insert the new pointers, and collect blobs with no remaining kept-state pointer in the same write transaction.
Completeness checks join pointers to blobs, so a missing blob cannot yield a partial stored answer.
The existing WAL snapshot, interruption-at-every-statement, process-death, and immutable-unit checks also exercise the new layout.

M-1: explicit flushes tolerate absent standard streams and skip the deferred keep when output was unavailable.
Real subprocess tests close descriptor 1 or 2, with and without the index; the historical exit status is retained without a traceback.
M-2: intact buckets prove an ID absent, the complete codes mapping proves an unknown code absent, and stored thread IDs prove a thread absent.
The resulting errors preserve the in-memory unreadable-file diagnostic; damaged buckets still rebuild.
M-3: marker and parse-only writers receive the full used parse set and the build's starting epoch, and rewrite those hits after a clear.
The existing epoch-count test caught an extra epoch lookup during this change; forwarding the build's original epoch through subsequent snapshots fixed it.
M-4: `index_file_cap(files)` names the unchanged formula and is used by the writer and cap tests.
M-5: a termination signal during the deferred keep still passes through as `SystemExit`, as the plan requires.
There remains a window after successful output during which a supervisor can terminate the command and change its exit status.
M-6: the dead text-presence branch is removed, and the listing assembler's docstring names its coupling to the exact assembler and the differential test.

The Files list and interfaces are amended for the required adapter, lookup, fake-index, and epoch-forwarding hand-offs.
Existing test edits follow the bucket storage location, the optional writer arguments, and the named cap formula; no correctness assertion is removed.
The focused checks pass: 62 tests across the new regressions and existing read contracts, then 100 tests across the epoch, shared-bucket, command-contract, and structure checks.

The space experiment runs on copies of the synthetic stores with FTS present.
The two-state layout comparison temporarily suppresses cap clearing in the probe only, since even one complete state with words is already over the production cap.
The ten-cycle edit/read/read/read walk uses the unchanged production cap.
The source snapshots used for the before/after probes are fixed copies of build 12099d1 and this fix round; no other worktree is modified.
Timings are not inferred from concurrent space probes.

## Task 10a fix round: gate and space measurements

`sh scripts/check.sh` is green: formatting, Ruff, strict mypy (285 source files), Vulture, 2,135 passed, six skipped, and `lodge check --gate` (`ok`; the existing storage-order note).

Probe commands: `uv run --frozen python /var/tmp/lodge-bench/t10c-fix-bench.py before` and the same command with `after`.
Both source snapshots were bytecode-compiled with the same frozen CPython environment, and both stores and indexes reside on native disk.
Used bytes are `(page_count - freelist_count) * page_size`, with decimal MB below.
The diagnostic holds two states despite the cap solely to measure their layout; production clearing is enabled for the cycle walk.

| Store | Layout | First state, bytes | Second state, bytes | Second state's added bytes |
|---|---|---:|---:|---:|
| s9000 | before | 25,763,840 | 32,440,320 | 6,676,480 |
| s9000 | after | 26,771,456 | 27,725,824 | 954,368 |
| s90000 | before | 250,286,080 | 309,874,688 | 59,588,608 |
| s90000 | after | 251,326,464 | 259,715,072 | 8,388,608 |

At s90000 the whole second state's added space falls from 59.59 MB to 8.39 MB.
The shared layout contains 1,024 distinct blobs for the first state and 1,025 for the pair, with all 1,024 pointers per state retained.
The review's roughly 0.12 MB prototype described additional bucket storage; this build also retains each new ident's facts and each state's citers and metadata.
Those other rows account for most of the remaining 8.39 MB; this round changes only the bucket ownership ruled by the coordinator.
The first shared state costs about 1.04 MB more in the changed layout.

With Task 10b's words present, **zero complete states fit under the current cap** at either measured size.
At s9000, one shared state uses 26,771,456 bytes against 24,186,000; at s90000, 251,326,464 against 241,201,500.
The larger stores' kept working sets exceed the production cap with FTS, so changed samples that clear are reported as cold, following Task 10b's wording.
The cap, targets, and Task 12 stop are unchanged; DISK-1 remains with the author.

A final lookup regression caught a duplicate bucket read on known IDs while adding proven absence.
The fix retains the loaded record, preserving the one-bucket-per-ID contract.

```text
F                                                                        [100%]
=================================== FAILURES ===================================
_____________________ test_known_id_reads_its_bucket_once ______________________

tmp_path = PosixPath('<pytest>/test_known_id_reads_its_bucket0')

    def test_known_id_reads_its_bucket_once(tmp_path: Path) -> None:
        store, index = project(), opened(tmp_path)
        seed(store, index)
        expected = printed(app(store), ["show", FIRST.id])
        with patch.object(index, "rows", wraps=index.rows) as rows:
            assert printed(app(store, index), ["show", FIRST.id]) == expected
>       assert rows.call_count == 1
E       AssertionError: assert 2 == 1
E        +  where 2 = <MagicMock name='rows' id='139866736224848'>.call_count

tests/gitstore/test_index_shared_buckets.py:174: AssertionError
=========================== short test summary info ============================
FAILED tests/gitstore/test_index_shared_buckets.py::test_known_id_reads_its_bucket_once
1 failed in 0.84s
```

The final fix-round gate was rerun after the known-ID lookup regression: 2,135 passed, six skipped, in 199.94 s, with every other check green.
Machine-specific interpreter and pytest roots in the captured red output are replaced by `<python>` and `<pytest>` for this public report.

The production walk starts with the baseline read twice, then appends one distinct synthetic edit per cycle and reads it three times, without restoring the saved index between cycles.

| Store | Layout | Cycles | Clears |
|---|---|---:|---:|
| s9000 | before | 10 | 10 |
| s9000 | after | 10 | 10 |
| s90000 | before | 10 | 10 |
| s90000 | after | 10 | 10 |

Sharing buckets saves substantial space between kept states, but does not remove these clears because a single kept working set with FTS exceeds the unchanged cap.
M-3's regressions verify that the clearing marker retains every parse already held, so the next read reuses those units rather than reparsing the whole tree.
The remaining per-state facts, citers, and metadata, and the signal window are reported concerns; no extra compaction policy or cap increase is inferred.

Task 10a fix round is complete; Task 10c implementation follows its pushed commit.

## Task 10c: skeleton and red evidence

The required hand-offs also touch `app/state.py` and the core front door; the Task 10c Files list is amended accordingly.
`Checked` can carry stored facts without a published `Derived`, and `finish_checked` accepts explicitly supplied `ChangeFacts`.
Core's existing `Status` type is exported to type the validated conversion, while the persisted `StateFacts` shape remains unchanged.
The skeleton passed 39 structure tests and strict mypy (285 source files) before the new tests were written.

All eleven new cases fail before implementation.
The cycle fixture was corrected before implementation to use the entry `rests_on` graph, which is the graph lodge checks for cycles; the final red run fails at the intended derivation-count assertion.
The equal-result cases also vary cached problem line numbers, checking that only `(path, check, message)` defines a published problem's identity.
Additional cases cover carrying facts hits through marker and keep clears and refusing invalid cached status values.

Command: `uv run --frozen pytest tests/app/test_published_facts.py -q --tb=short`.

```text
FFFFFFFFFFF                                                              [100%]
=================================== FAILURES ===================================
_______________ test_published_facts_equal_full[duplicate_code] ________________
tests/app/test_published_facts.py:93: in test_published_facts_equal_full
    assert derive.call_count == check.call_count == compare.call_count == 1
E   AssertionError: assert 2 == 1
E    +  where 2 = <MagicMock name='check_state' id='140600155680320'>.call_count
E    +  and   1 = <MagicMock name='check_change' id='140600155679648'>.call_count
_________________ test_published_facts_equal_full[hand_edited] _________________
tests/app/test_published_facts.py:93: in test_published_facts_equal_full
    assert derive.call_count == check.call_count == compare.call_count == 1
E   AssertionError: assert 2 == 1
E    +  where 2 = <MagicMock name='check_state' id='140600155678976'>.call_count
E    +  and   1 = <MagicMock name='check_change' id='140600155681328'>.call_count
________________ test_published_facts_equal_full[out_of_order] _________________
tests/app/test_published_facts.py:93: in test_published_facts_equal_full
    assert derive.call_count == check.call_count == compare.call_count == 1
E   AssertionError: assert 2 == 1
E    +  where 2 = <MagicMock name='check_state' id='140600155682000'>.call_count
E    +  and   1 = <MagicMock name='check_change' id='140600155682336'>.call_count
____________________ test_published_facts_equal_full[cycle] ____________________
tests/app/test_published_facts.py:93: in test_published_facts_equal_full
    assert derive.call_count == check.call_count == compare.call_count == 1
E   AssertionError: assert 2 == 1
E    +  where 2 = <MagicMock name='check_state' id='140600155683008'>.call_count
E    +  and   1 = <MagicMock name='check_change' id='140600155683344'>.call_count
_______________________ test_facts_keyed_by_ident_alone ________________________
tests/app/test_published_facts.py:107: in test_facts_keyed_by_ident_alone
    assert lookup.call_count == 4 and all(c.args == (ident,) for c in lookup.call_args_list)
E   AssertionError: assert (0 == 4)
E    +  where 0 = <MagicMock name='facts' id='140600155683680'>.call_count
___________________ test_absent_facts_are_computed_and_kept ____________________
tests/app/test_published_facts.py:116: in test_absent_facts_are_computed_and_kept
    assert index.facts(ident) == expected
E   AssertionError: assert None == StateFacts(status={'d-aaaaaa': 'current', 's-aaaaaa': 'current'}, problems=())
E    +  where None = facts('lodge/decisions/d-aaaaaa-keep-whole-transcripts.md:35ba5aa527706c3a4c0127804d9d2c246d916860\x00lodge/spec/storage/_ar...dce36ffcc4c2e0151b5aff\x00lodge/spec/storage/s-aaaaaa-transcripts-are-kept.md:fc2529e2cf4d4f6e1b2d18d537d893d01ebfa985')
E    +    where facts = <fake_index.MemoryIndex object at 0x7fe0063a7950>.facts
_____________________ test_facts_written_on_the_first_read _____________________
tests/app/test_published_facts.py:137: in test_facts_written_on_the_first_read
    assert index.facts(ident) == expected
E   AssertionError: assert None == StateFacts(status={'d-aaaaaa': 'current', 's-aaaaaa': 'current'}, problems=())
E    +  where None = facts('lodge/decisions/d-aaaaaa-keep-whole-transcripts.md:35ba5aa527706c3a4c0127804d9d2c246d916860\x00lodge/spec/storage/_ar...dce36ffcc4c2e0151b5aff\x00lodge/spec/storage/s-aaaaaa-transcripts-are-kept.md:fc2529e2cf4d4f6e1b2d18d537d893d01ebfa985')
E    +    where facts = <fake_index.MemoryIndex object at 0x7fe0063f57c0>.facts
_________________ test_other_published_ident_reads_other_facts _________________
tests/app/test_published_facts.py:167: in test_other_published_ident_reads_other_facts
    assert lookup.call_args_list and all(c.args == (new,) for c in lookup.call_args_list)
E   AssertionError: assert ([])
E    +  where [] = <MagicMock name='facts' id='140600155683344'>.call_args_list
_____________ test_used_facts_are_carried_through_a_clear[marker] ______________
tests/app/test_published_facts.py:191: in test_used_facts_are_carried_through_a_clear
    assert derive.call_count == 1
E   AssertionError: assert 2 == 1
E    +  where 2 = <MagicMock name='derive' id='140600155682672'>.call_count
______________ test_used_facts_are_carried_through_a_clear[keep] _______________
tests/app/test_published_facts.py:191: in test_used_facts_are_carried_through_a_clear
    assert derive.call_count == 1
E   AssertionError: assert 2 == 1
E    +  where 2 = <MagicMock name='derive' id='140600155682336'>.call_count
________________________ test_invalid_status_is_a_miss _________________________
tests/app/test_published_facts.py:199: in test_invalid_status_is_a_miss
    assert read_model.change_facts_of(state, StateFacts({FIRST.id: "invalid"}, ())) is None
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/app/read_model.py:91: in change_facts_of
    raise NotImplementedError
E   NotImplementedError
=========================== short test summary info ============================
FAILED tests/app/test_published_facts.py::test_published_facts_equal_full[duplicate_code]
FAILED tests/app/test_published_facts.py::test_published_facts_equal_full[hand_edited]
FAILED tests/app/test_published_facts.py::test_published_facts_equal_full[out_of_order]
FAILED tests/app/test_published_facts.py::test_published_facts_equal_full[cycle]
FAILED tests/app/test_published_facts.py::test_facts_keyed_by_ident_alone - A...
FAILED tests/app/test_published_facts.py::test_absent_facts_are_computed_and_kept
FAILED tests/app/test_published_facts.py::test_facts_written_on_the_first_read
FAILED tests/app/test_published_facts.py::test_other_published_ident_reads_other_facts
FAILED tests/app/test_published_facts.py::test_used_facts_are_carried_through_a_clear[marker]
FAILED tests/app/test_published_facts.py::test_used_facts_are_carried_through_a_clear[keep]
FAILED tests/app/test_published_facts.py::test_invalid_status_is_a_miss - Not...
11 failed in 0.27s
```

The moved-published fixture now rewrites the new published record's reasoning rather than searching for text that the simulated commit had already replaced.
The corrected case was rerun against Task 10a's pre-Task-10c indexed reader and failed at the intended missing-lookup assertion.

```text
F                                                                        [100%]
=================================== FAILURES ===================================
_________________ test_other_published_ident_reads_other_facts _________________
tests/app/test_published_facts.py:170: in test_other_published_ident_reads_other_facts
    assert lookup.call_args_list and all(c.args == (new,) for c in lookup.call_args_list)
E   AssertionError: assert ([])
E    +  where [] = <MagicMock name='facts' id='140299884160272'>.call_args_list
=========================== short test summary info ============================
FAILED tests/app/test_published_facts.py::test_other_published_ident_reads_other_facts
1 failed in 0.19s
```

Two additional fault cases expose status mappings with a missing or extra record ID; both failed before the completeness guard was added.

```text
FF                                                                       [100%]
=================================== FAILURES ===================================
_______________ test_incomplete_status_facts_are_a_miss[missing] _______________
tests/app/test_published_facts.py:224: in test_incomplete_status_facts_are_a_miss
    assert rebuilt.result == expected.result and derive.call_count == 2
E   AssertionError: assert (CheckResult(p...),), notes=()) == CheckResult(p...),), notes=())
E
E     Omitting 2 identical items, use -vv to show and 1 == 2)
E    +  where 1 = <MagicMock name='derive' id='140479038483696'>.call_count
________________ test_incomplete_status_facts_are_a_miss[extra] ________________
tests/app/test_published_facts.py:224: in test_incomplete_status_facts_are_a_miss
    assert rebuilt.result == expected.result and derive.call_count == 2
E   AssertionError: assert (CheckResult(p...),), notes=()) == CheckResult(p...),), notes=())
E
E     Omitting 2 identical items, use -vv to show and 1 == 2)
E    +  where 1 = <MagicMock name='derive' id='140479040800816'>.call_count
=========================== short test summary info ============================
FAILED tests/app/test_published_facts.py::test_incomplete_status_facts_are_a_miss[missing]
FAILED tests/app/test_published_facts.py::test_incomplete_status_facts_are_a_miss[extra]
2 failed in 0.18s
```

## Task 10c: implementation

A changed indexed read still assembles both pinned snapshots and runs the complete `check_change`.
When the published ident has complete stored facts with valid status values, only the current snapshot runs `derive` and `check_state`.
`ChangeFacts` takes the published statuses and `(path, check, message)` keys from those facts and the current snapshot's own derivation and standing problems.
Absent, invalid, or incomplete facts take the full published derivation and check path.
The equal-listing shortcut remains unchanged.

Every first-sighting marker now carries the current snapshot's own facts and the published facts it computed or used.
The deferred keep carries the same facts, including hits, for epoch recovery.
Facts remain keyed by ident alone, immutable, and retained across state evictions.
The gate still takes only parse units from the index and computes its own derived data.
Core's checks and their helpers are unchanged.

The new thirteen cases and the directly affected existing contracts pass: 60 tests in 5.55 s, with strict mypy green across 286 source files.
The full gate and native-disk measurements are recorded below.
The replay follows Task 1's changed mode: warm all replay commands, save the index, then restore that saved index and make one edit before each measured read.
The separate phase probe starts from one first sighting's parse units and facts, below the cap, to measure facts hit and miss without a cap clear obscuring the comparison.
Its controlled miss removes the published facts only in a synthetic benchmark index, never in production code.

The first full gate found the existing real-index surrogate-path regression on `show`.
The fake store's opaque ident can contain a surrogate; writing its first-sighting facts then raised `UnicodeEncodeError` and rolled back unrelated valid parse units.
The production adapter now skips only the unencodable facts unit, matching its existing parse-unit handling.
SQLite errors still roll back the whole transaction, preserving the fault-injection contract.
The Task 10c Files list includes this required facts-writer hand-off.
The new regression and the existing path cases were run before this fix.

```text
FF..                                                                     [100%]
=================================== FAILURES ===================================
_________________ test_unencodable_facts_do_not_discard_parses _________________
tests/app/test_published_facts.py:236: in test_unencodable_facts_do_not_discard_parses
    assert index.parses([key]) == {key: None}
E   AssertionError: assert {} == {('lodge/deci...'blob'): None}
E
E     Right contains 1 more item:
E     {('lodge/decisions/d-aaaaaa-synthetic.md', 'blob'): None}
E     Use -v to get more diff
__________________ test_surrogate_path_with_real_index[show] ___________________
tests/app/test_parse_cache.py:139: in test_surrogate_path_with_real_index
    assert (path, tree.blobs[path]) in index.parses([(path, tree.blobs[path])])
E   AssertionError: assert ('lodge/decisions/d-aaaaaa-a-decision.md', '37afeb157cbc48f4f9cb9d216f5aa72a7ec53d5f') in {}
E    +  where {} = parses([('lodge/decisions/d-aaaaaa-a-decision.md', '37afeb157cbc48f4f9cb9d216f5aa72a7ec53d5f')])
E    +    where parses = <lodge.gitstore.index_db.IndexDB object at 0x7f1f9139a490>.parses
=========================== short test summary info ============================
FAILED tests/app/test_published_facts.py::test_unencodable_facts_do_not_discard_parses
FAILED tests/app/test_parse_cache.py::test_surrogate_path_with_real_index[show]
2 failed, 2 passed in 0.23s
```

## Task 10c: full gate

After the surrogate-unit fix, `sh scripts/check.sh` is green: formatting, Ruff, strict mypy (286 source files), Vulture, 2,149 passed, six skipped, and `lodge check --gate` (`ok`, with the existing storage-order note).
The pytest part completed in 173.22 s.
The final focused rerun passes 51 tests across published facts, parse-cache handling, and state storage.
Task 10a's fix-round commit is `2e779c0`, pushed before Task 10c's skeleton and tests.

The timing environment is CPython 3.13.5, SQLite 3.47.1, PyYAML 6.0.3 with libyaml, and git 2.56.0.
The frozen worktree environment and source bytecode were compiled before measurement, and all benchmark stores and saved indexes are under `/var/tmp/lodge-bench/` on native disk.
The timed child commands run `python -m lodge.main` with the frozen environment's interpreter; the diagnostic explicitly disables cyclic GC too.
Git uses isolated empty global and system configuration, with interim R11-A and no conversion source.
CONV-1 and the conversion measurements from Task 8c remain separate; this task changes no identity code.

## Task 10c: changed-read phases and facts growth

Command: `uv run --frozen python /var/tmp/lodge-bench/t10c-bench.py`.
Store: `/var/tmp/lodge-bench/task10c/s90000`, a synthetic copy with 160,801 files, one edited record, and no conversion source.
The representative read is `show A`; its in-memory answer also scans code citers, unlike the `waiting` example in plan fix 7b.
Each uninstrumented read's stdout, stderr, and exit status equals the index-off reader's.
The diagnostic also produces identical output, with its metrics removed from stderr before comparison.

| Published facts | Uninstrumented samples, s | Best of three, s | Added facts value bytes | Clears |
|---|---|---:|---:|---:|
| hit | 8.643198, 8.415025, 8.496814 | 8.415025 | 3,329,571 | 0 |
| miss | 9.672830, 9.781577, 9.736098 | 9.672830 | 6,659,142 | 0 |

The facts-hit baseline has parse units and one facts row, no kept state, and uses 194,068,480 bytes.
The controlled miss has the same parse units and no facts row, using 190,738,432 bytes.
Both finish at 197,406,720 used bytes, with two facts rows, no kept state, and the epoch unchanged.
A hit adds only the new current ident's 3,329,571-byte facts value; a miss adds that and the published ident's value, 6,659,142 bytes in all.
The values repeat when an edit leaves statuses unchanged, since facts remain immutable and keyed by ident, as ruled.
These sizes are JSON value bytes, while the used-page figures include SQLite overhead.

The disjoint phase values below are the best of three for each row, so their sum is not a timed command.
The uninstrumented exit times above are measured separately.

| Phase | Facts hit, s | Facts miss, s |
|---|---:|---:|
| Startup, wiring, digest, identity, and listings | 2.045376 | 1.964158 |
| Current parse lookup and decode | 1.075460 | 1.103845 |
| Current missed text and parse | 0.000240 | 0.000241 |
| Current assemble | 0.102707 | 0.101381 |
| Current derive | 0.955591 | 0.954427 |
| Current check_state | 0.444828 | 0.442455 |
| Published snapshot, including memo and assemble | 0.277414 | 0.281753 |
| Published facts lookup, decode, and conversion | 0.092590 | 0.000097 |
| Published derive | 0.000000 | 0.955095 |
| Published check_state | 0.000000 | 0.447998 |
| change_facts and complete check_change | 0.777460 | 0.793696 |
| failing_ids and unrecorded_problems | 0.050039 | 0.050148 |
| Marker facts construction, encoding, and insertion | 0.144343 | 0.162857 |
| Marker parse insertion | 0.000263 | 0.000264 |
| Marker other SQL and cap check | 0.004584 | 0.016767 |
| Build/check glue | 0.210256 | 0.170779 |
| Read dispatch and answer preparation | 2.139091 | 2.176336 |
| Rendering and output | 0.013201 | 0.015503 |

On a hit, the published `derive` and `check_state` phases disappear; the current derivation, current checks, and full change check still run.
The representative read remains above the provisional 3 s changed-read target with interim R11-A and its code-citer answer cost.
The target and Task 12 stop are unchanged.
The complete changed-mode replay is recorded below.

<!-- task10c-replay:start -->

## Task 10c: changed-mode replay

All 16 commands completed, with three timed samples each: 48 timed reads, all equal to the exact reader.
Each sample compares stdout, stderr, and exit status with one exact index-off read of the same edited store.
The saved replay baseline uses 251,318,272 bytes, holds 1 state, and starts at epoch 2.
It exceeds the unchanged 241,201,500-byte cap with words; the clearing samples below are cold, following Task 10b.

| Command | Best of three, s | Exit | Clears in three samples | Net facts value bytes per sample | Equal |
|---|---:|---:|---:|---:|---|
| `show {code}` | 11.334526 | 0 | 3 | 3,329,571 | yes |
| `show {entry} --reasoning --provenance` | 11.212901 | 0 | 3 | 3,329,571 | yes |
| `show {decision}` | 11.259641 | 0 | 3 | 3,329,571 | yes |
| `search berth --brief` | 13.857747 | 0 | 3 | 3,329,571 | yes |
| `search "berth crane" --brief` | 13.773231 | 0 | 3 | 3,329,571 | yes |
| `search {code} --brief` | 13.759142 | 0 | 3 | 3,329,571 | yes |
| `search berth` | 13.773140 | 0 | 3 | 3,329,571 | yes |
| `waiting` | 11.246684 | 0 | 3 | 3,329,571 | yes |
| `threads` | 11.250213 | 0 | 3 | 3,329,571 | yes |
| `spec --area area-001` | 15.922088 | 0 | 3 | -3,329,571 | yes |
| `check` | 15.828666 | 1 | 3 | -3,329,571 | yes |
| `check --gate` | 22.456801 | 1 | 3 | -3,329,571 | yes |
| `show {code} {code2} {entry}` | 11.495818 | 0 | 3 | 3,329,571 | yes |
| `show A` | 13.288062 | 0 | 3 | 3,329,571 | yes |
| `search berth tide --brief` | 16.295303 | 0 | 3 | 3,329,571 | yes |
| `search --phrase "berth crane" --brief` | 14.811764 | 0 | 3 | 3,329,571 | yes |

Net facts bytes compare stored JSON values before and after the read, including any clear.
Exact readers do not populate derived facts, so a clear on their path can make that net change negative.
The phase probe above measures a new current facts value and a missing published facts value separately, without a clear.

<!-- task10c-replay:end -->

## Final result and concerns

Task 10c is built, with fourteen new regression cases seen failing before their fixes.
The final full gate is green, and all 48 changed-mode replay samples match stdout, stderr, and exit status byte for byte.
All 48 replay samples clear the over-cap saved index once, so their timings are cold, as Task 10b reports such reads.
The replay's `check` and `check --gate` exits of 1 are the exact reader's expected failures for the edited synthetic fixture; the repository's own gate passes.
The separate no-clear phase comparison measures 8.415025 s with a facts hit and 9.672830 s with a miss, best of three, for `show A` at s90000.

DISK-1 remains with the author: zero complete states fit under the unchanged cap with FTS at the measured sizes, even after sharing buckets.
Each new current ident also adds about 3.33 MB of immutable facts values on this store, even when its statuses are unchanged.
No facts-eviction policy is introduced; the ledger's W6 remains deferred to the measurements and rulings for Task 12.
Interim R11-A remains in production, conversions remain beside the targets under CONV-1, and the provisional read targets are still missed.
A termination signal during a deferred keep can still change the exit status after complete output, as permitted and documented for M-5.
No record was added, no other worktree was modified, and no task is stopped for missing context.
