# Task 3 fix round report

Status: complete.

The fix round addresses I1, I2, and M1 to M4 from the copied `task-3-review.md`.
Only Task 3 implementation, tests, and reports are in scope.
The dispatch forbids `lodge add`, and no record change is needed for these fixes.
Decisions d-q051s2 and d-3g6ard, and entry s-3n0ndk, were read with `lodge show --reasoning`.

## Validation in progress

The shared constructor skeleton precedes the regression tests and implementation.

## Built

I1: the writer-header test and seeded fuzz always compare the public loader with the Python oracle.
Only direct C calls and the C-success floor depend on libyaml availability; only the C-call-counter test is skipped without it.
I2: `yamlfast.TextConstructor` owns the empty implicit resolvers, filtered constructor table, surrogate joining, and duplicate-key check.
Both loaders inherit that one mixin and use zero-argument `super()`.
The skeleton passed structure checks (39 tests in 0.60 s) and strict mypy (209 source files) before regression tests were added.
M1: the bare C loader now raises `RuntimeError("libyaml is not available")` when absent, and its docstring identifies `yamlio.load_yaml` as the admission, dispatch, and fallback interface.
M2: flow plain scalars exclude colons, and the quoted-string guard excludes the escaped slash; top-level plain timestamps still admit colons.
All four narrowed forms are compared through the public loader with the Python oracle, with a forbidden C call.
M3: the original report retains the command, the first seven lines of one failure per test function, and the `60 failed` summary.
M4: the writer-header test is renamed `test_written_headers_without_bom_are_admitted`, and a new BOM-title case proves the writer emits it and the public loader reads it unchanged through Python.

## Failing tests before implementation

Command: `uv run --frozen pytest tests/core/test_yaml_guard.py -q -k 'value_constructors or version_sensitive or written_bom' --tb=short`.
The first lines per failing case follow; the BOM test already passed because it records existing behaviour.

```text
test_value_constructors_are_shared
    assert issubclass(yamlio._TextLoader, yamlfast.TextConstructor)
E   AssertionError: assert False

test_version_sensitive_shapes_use_python[a: [a:b]]
    assert not yamlfast.admitted(header)
E   AssertionError: assert not True

test_version_sensitive_shapes_use_python[a: {b: a:b}]
    assert not yamlfast.admitted(header)
E   AssertionError: assert not True

test_version_sensitive_shapes_use_python[a:\n  - {b: a:b}]
    assert not yamlfast.admitted(header)
E   AssertionError: assert not True

test_version_sensitive_shapes_use_python[a: "\\/"]
    assert not yamlfast.admitted(header)
E   assert not True

5 failed, 1 passed, 60 deselected in 0.12s
```

Command with libyaml hidden: `PYTHONPATH=/var/tmp/lodge-review-t3/nolib uv run --frozen pytest tests/core/test_yaml_guard.py tests/core/test_yaml_fuzz.py -q -k 'every_written or c_loader_used or admitted_headers_parse or bare_c_loader' --tb=short`.

```text
test_every_written_header_is_admitted
    return yaml.load(text, Loader=_CTextLoader)
E   NameError: name '_CTextLoader' is not defined

test_c_loader_used_for_admitted_headers
    assert calls == ["key: yes"]
E   AssertionError: assert [] == ['key: yes']

test_bare_c_loader_reports_absence
    return yaml.load(text, Loader=_CTextLoader)
E   NameError: name '_CTextLoader' is not defined

test_admitted_headers_parse_the_same
    assert c_successes > 1000
E   assert 0 > 1000

4 failed, 63 deselected in 4.71s
```

The hidden-libyaml directory supplies a `sitecustomize.py` that inserts an import finder into `sys.meta_path` and raises `ImportError` for `yaml._yaml` and `_yaml`.
PyYAML therefore sets `__with_libyaml__` false and exposes no `CSafeLoader`; this tests import-time absence rather than only patching an availability flag.
No installed library files are changed.

## Verification so far

Targeted command: `uv run --frozen pytest tests/core/test_yaml_guard.py tests/core/test_yaml_fuzz.py -q -s --tb=short`.
Result: 66 passed, 1 skipped in 4.86 s; strict mypy passed (209 source files).
Seed 20261101: libyaml parsed 4,935 of 5,031 admitted headers; all 20,000 public outcomes equal the Python oracle.

Independent reviewer oracle command: `uv run --frozen python /var/tmp/lodge-review-t3/fuzz.py 1000 16 16000`.
The oracle is the pre-Task-3 loader, not the refactored constructor.

```text
libyaml True seeds 1000 .. 1015 per 16000
{'total': 256864, 'admitted': 47628, 'c_ok': 39577, 'c_fail_py_ok': 0, 'c_fail_py_err': 8051}
violations 0
```

The first gate attempt stopped at Ruff's import-spacing check; Ruff fixed the extra blank line, and both complete gates were restarted.
Full gate with libyaml: `UV_FROZEN=true sh scripts/check.sh` passed, with 1,556 tests passed and 1 skipped in 49.51 s, and `lodge check --gate` reporting `ok`.
Full gate without libyaml: `PYTHONPATH=/var/tmp/lodge-review-t3/nolib UV_FROZEN=true sh scripts/check.sh` passed, with 1,556 tests passed and 1 skipped in 49.94 s, and `lodge check --gate` reporting `ok`.
Both gates passed formatting (583 files), Ruff, strict mypy (209 source files), and Vulture.
The skip with libyaml is the absence-only direct-loader test; the skip without libyaml is the C-call-counter test.
`git diff --check` passed, and `cmp` confirmed the copied review exactly matches the supplied review.

## Existing test edits

`test_yaml_guard.py`: renamed the writer-header test, made only direct C assertions conditional, added unconditional public-loader equality checks, marked the C-call-counter test as skipped without libyaml, and changed the admitted JSON-escape fixture from an escaped slash to the literal slash the writer emits.
`test_yaml_fuzz.py`: counted admitted headers and compared all public outcomes unconditionally, while guarding direct C calls and their success floor by libyaml availability.
No Task 4 implementation, tests, or report changed.
The copied review, trimmed original report, this fix report, the two implementation files, and the two YAML test files form the fix-round commit.
The Task 5 context report is delivered in a separate documentation commit.

## Concerns

Task 5 is stopped before implementation under the dispatch's record-writing rule; see `task-5-report.md`.
No Task 3 correctness concern is known after the independent differential comparison.
The narrower guard intentionally routes additional hand-written forms through Python.
No speed benchmark is required by this fix round, and the earlier Task 3 timings remain historical measurements.
