# Task 3 report: libyaml behind a guard

Status: complete.

Scope: the writer-shape guard, the optional C text loader, the `yamlio.load_yaml` dispatch, and the two new test files named in Task 3.
No existing tests or Tasks 1 and 2 files are changed.
Decisions d-q051s2 and d-1bww1r were read through `lodge show --reasoning`.
There is nothing waiting for an agent.

## Skeleton

Added the `admitted(header: str) -> bool` and C-path `load_yaml(text: str) -> object` signatures in `core/yamlfast.py`, with `NotImplementedError` bodies.
The module is internal to core, so no front-door export is needed.
`uv run --frozen pytest tests/test_structure.py -q` passed: 39 tests in 0.55 s.
`uv run --frozen mypy` passed: 205 source files.

## Failing tests

Command: `uv run --frozen pytest tests/core/test_yaml_guard.py tests/core/test_yaml_fuzz.py -q --tb=short`.
All 60 new cases failed before implementation, including each named Task 3 test.
The full captured output follows.

```text
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF             [100%]
=================================== FAILURES ===================================
____________________ test_every_written_header_is_admitted _____________________
tests/core/test_yaml_guard.py:65: in test_every_written_header_is_admitted
    assert yamlfast.admitted(header), header
           ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_______ test_trailing_tab_is_not_admitted_and_fails_as_today[title: x\t] _______
tests/core/test_yaml_guard.py:78: in test_trailing_tab_is_not_admitted_and_fails_as_today
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_______ test_trailing_tab_is_not_admitted_and_fails_as_today[title:\tx] ________
tests/core/test_yaml_guard.py:78: in test_trailing_tab_is_not_admitted_and_fails_as_today
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_________ test_trailing_tab_is_not_admitted_and_fails_as_today[- a\t] __________
tests/core/test_yaml_guard.py:78: in test_trailing_tab_is_not_admitted_and_fails_as_today
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_____ test_trailing_tab_is_not_admitted_and_fails_as_today[title: x\t# c] ______
tests/core/test_yaml_guard.py:78: in test_trailing_tab_is_not_admitted_and_fails_as_today
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
___________ test_block_scalar_bom_and_nesting_not_admitted[key: |#] ____________
tests/core/test_yaml_guard.py:95: in test_block_scalar_bom_and_nesting_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
______ test_block_scalar_bom_and_nesting_not_admitted[a: b\n\ufeffkey: c] ______
tests/core/test_yaml_guard.py:95: in test_block_scalar_bom_and_nesting_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
___________ test_block_scalar_bom_and_nesting_not_admitted[header2] ____________
tests/core/test_yaml_guard.py:95: in test_block_scalar_bom_and_nesting_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
___________________ test_c_loader_used_for_admitted_headers ____________________
tests/core/test_yaml_guard.py:108: in test_c_loader_used_for_admitted_headers
    assert calls == ["key: yes"]
E   AssertionError: assert [] == ['key: yes']
E     
E     Right contains one more item: 'key: yes'
E     Use -v to get more diff
_______________________ test_falls_back_without_libyaml ________________________
tests/core/test_yaml_guard.py:112: in test_falls_back_without_libyaml
    assert yamlfast.admitted('key: "berth"')
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_________ test_c_failures_fall_back_with_python_diagnostics[failure0] __________
tests/core/test_yaml_guard.py:126: in test_c_failures_fall_back_with_python_diagnostics
    assert yamlfast.admitted("title: a\ntitle: b")
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_________ test_c_failures_fall_back_with_python_diagnostics[failure1] __________
tests/core/test_yaml_guard.py:126: in test_c_failures_fall_back_with_python_diagnostics
    assert yamlfast.admitted("title: a\ntitle: b")
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
____________________ test_writer_shapes_are_admitted[a: b] _____________________
tests/core/test_yaml_guard.py:147: in test_writer_shapes_are_admitted
    assert yamlfast.admitted(header)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
____________________ test_writer_shapes_are_admitted[a: ""] ____________________
tests/core/test_yaml_guard.py:147: in test_writer_shapes_are_admitted
    assert yamlfast.admitted(header)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
__________________ test_writer_shapes_are_admitted[a: 14:14] ___________________
tests/core/test_yaml_guard.py:147: in test_writer_shapes_are_admitted
    assert yamlfast.admitted(header)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
__________________ test_writer_shapes_are_admitted[a: [a, b]] __________________
tests/core/test_yaml_guard.py:147: in test_writer_shapes_are_admitted
    assert yamlfast.admitted(header)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
____________________ test_writer_shapes_are_admitted[a: []] ____________________
tests/core/test_yaml_guard.py:147: in test_writer_shapes_are_admitted
    assert yamlfast.admitted(header)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_______________ test_writer_shapes_are_admitted[a: {b: c, d: e}] _______________
tests/core/test_yaml_guard.py:147: in test_writer_shapes_are_admitted
    assert yamlfast.admitted(header)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
________ test_writer_shapes_are_admitted[a:\n  - {b: "c"}\n  - {d: 3}] _________
tests/core/test_yaml_guard.py:147: in test_writer_shapes_are_admitted
    assert yamlfast.admitted(header)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
____________ test_writer_shapes_are_admitted[a: "# | > & * ! % ?"] _____________
tests/core/test_yaml_guard.py:147: in test_writer_shapes_are_admitted
    assert yamlfast.admitted(header)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
______ test_writer_shapes_are_admitted[a: "\\u0000\\u0041\\uD7FF\\ue000"] ______
tests/core/test_yaml_guard.py:147: in test_writer_shapes_are_admitted
    assert yamlfast.admitted(header)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_______ test_writer_shapes_are_admitted[a: "\\b\\f\\n\\r\\t\\/\\\\\\""] ________
tests/core/test_yaml_guard.py:147: in test_writer_shapes_are_admitted
    assert yamlfast.admitted(header)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_____________________ test_other_shapes_are_not_admitted[] _____________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
____________________ test_other_shapes_are_not_admitted[a:] ____________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_________________ test_other_shapes_are_not_admitted[a:\nb: c] _________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
________________ test_other_shapes_are_not_admitted[  - {a: b}] ________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
________________ test_other_shapes_are_not_admitted[a:\n  - b] _________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
__________________ test_other_shapes_are_not_admitted[a: {}] ___________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
__________________ test_other_shapes_are_not_admitted[a: b ] ___________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_________________ test_other_shapes_are_not_admitted[a: b\n\n] _________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_________________ test_other_shapes_are_not_admitted[a: b # c] _________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
__________________ test_other_shapes_are_not_admitted[a: a:] ___________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
___________________ test_other_shapes_are_not_admitted[a: ~] ___________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
___________________ test_other_shapes_are_not_admitted[A: b] ___________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
__________________ test_other_shapes_are_not_admitted[a1: b] ___________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
__________________ test_other_shapes_are_not_admitted[a-b: c] __________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
______________ test_other_shapes_are_not_admitted[a: {b: {c: d}}] ______________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_______________ test_other_shapes_are_not_admitted[a: [a, [b]]] ________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_________________ test_other_shapes_are_not_admitted[a: [a,b]] _________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
______________ test_other_shapes_are_not_admitted[a: {b: c,d: e}] ______________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
___________________ test_other_shapes_are_not_admitted[a: |] ___________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
___________________ test_other_shapes_are_not_admitted[a: >] ___________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_________________ test_other_shapes_are_not_admitted[a: &b c] __________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
__________________ test_other_shapes_are_not_admitted[a: *b] ___________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
________________ test_other_shapes_are_not_admitted[a: !str b] _________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
________________ test_other_shapes_are_not_admitted[%YAML 1.1] _________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
___________________ test_other_shapes_are_not_admitted[? a] ____________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_______________ test_other_shapes_are_not_admitted[a: "\\uD800"] _______________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_______________ test_other_shapes_are_not_admitted[a: "\\udfff"] _______________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
___________ test_other_shapes_are_not_admitted[a: "\\ud83d\\ude00"] ____________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
________________ test_other_shapes_are_not_admitted[a: "\\x41"] ________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
________________ test_other_shapes_are_not_admitted[a: "\x7f"] _________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
________________ test_other_shapes_are_not_admitted[a: "\x85"] _________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_______________ test_other_shapes_are_not_admitted[a: "\u2028"] ________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_______________ test_other_shapes_are_not_admitted[a: "\u2029"] ________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_______________ test_other_shapes_are_not_admitted[a: "\ufeff"] ________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_______________ test_other_shapes_are_not_admitted[a: "\ud800"] ________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_________________ test_other_shapes_are_not_admitted[a: b\r\n] _________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_________________ test_other_shapes_are_not_admitted[a: "\t"] __________________
tests/core/test_yaml_guard.py:163: in test_other_shapes_are_not_admitted
    assert not yamlfast.admitted(header)
               ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
_____________________ test_admitted_headers_parse_the_same _____________________
tests/core/test_yaml_fuzz.py:73: in test_admitted_headers_parse_the_same
    if yamlfast.admitted(header):
       ^^^^^^^^^^^^^^^^^^^^^^^^^
src/lodge/core/yamlfast.py:6: in admitted
    raise NotImplementedError
E   NotImplementedError
=========================== short test summary info ============================
FAILED tests/core/test_yaml_guard.py::test_every_written_header_is_admitted
FAILED tests/core/test_yaml_guard.py::test_trailing_tab_is_not_admitted_and_fails_as_today[title: x\t]
FAILED tests/core/test_yaml_guard.py::test_trailing_tab_is_not_admitted_and_fails_as_today[title:\tx]
FAILED tests/core/test_yaml_guard.py::test_trailing_tab_is_not_admitted_and_fails_as_today[- a\t]
FAILED tests/core/test_yaml_guard.py::test_trailing_tab_is_not_admitted_and_fails_as_today[title: x\t# c]
FAILED tests/core/test_yaml_guard.py::test_block_scalar_bom_and_nesting_not_admitted[key: |#]
FAILED tests/core/test_yaml_guard.py::test_block_scalar_bom_and_nesting_not_admitted[a: b\n\ufeffkey: c]
FAILED tests/core/test_yaml_guard.py::test_block_scalar_bom_and_nesting_not_admitted[header2]
FAILED tests/core/test_yaml_guard.py::test_c_loader_used_for_admitted_headers
FAILED tests/core/test_yaml_guard.py::test_falls_back_without_libyaml - NotIm...
FAILED tests/core/test_yaml_guard.py::test_c_failures_fall_back_with_python_diagnostics[failure0]
FAILED tests/core/test_yaml_guard.py::test_c_failures_fall_back_with_python_diagnostics[failure1]
FAILED tests/core/test_yaml_guard.py::test_writer_shapes_are_admitted[a: b]
FAILED tests/core/test_yaml_guard.py::test_writer_shapes_are_admitted[a: ""]
FAILED tests/core/test_yaml_guard.py::test_writer_shapes_are_admitted[a: 14:14]
FAILED tests/core/test_yaml_guard.py::test_writer_shapes_are_admitted[a: [a, b]]
FAILED tests/core/test_yaml_guard.py::test_writer_shapes_are_admitted[a: []]
FAILED tests/core/test_yaml_guard.py::test_writer_shapes_are_admitted[a: {b: c, d: e}]
FAILED tests/core/test_yaml_guard.py::test_writer_shapes_are_admitted[a:\n  - {b: "c"}\n  - {d: 3}]
FAILED tests/core/test_yaml_guard.py::test_writer_shapes_are_admitted[a: "# | > & * ! % ?"]
FAILED tests/core/test_yaml_guard.py::test_writer_shapes_are_admitted[a: "\\u0000\\u0041\\uD7FF\\ue000"]
FAILED tests/core/test_yaml_guard.py::test_writer_shapes_are_admitted[a: "\\b\\f\\n\\r\\t\\/\\\\\\""]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[] - ...
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a:]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a:\nb: c]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[  - {a: b}]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a:\n  - b]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: {}]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: b ]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: b\n\n]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: b # c]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: a:]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: ~]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[A: b]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a1: b]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a-b: c]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: {b: {c: d}}]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: [a, [b]]]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: [a,b]]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: {b: c,d: e}]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: |]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: >]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: &b c]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: *b]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: !str b]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[%YAML 1.1]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[? a]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: "\\uD800"]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: "\\udfff"]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: "\\ud83d\\ude00"]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: "\\x41"]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: "\x7f"]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: "\x85"]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: "\u2028"]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: "\u2029"]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: "\ufeff"]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: "\ud800"]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: b\r\n]
FAILED tests/core/test_yaml_guard.py::test_other_shapes_are_not_admitted[a: "\t"]
FAILED tests/core/test_yaml_fuzz.py::test_admitted_headers_parse_the_same - N...
60 failed in 0.23s
```

## Implementation and validation

`yamlfast.admitted` checks the character exclusions, the exact scalar and shallow collection grammar, and that a block-list key is followed by at least one flow-mapping item.
The optional `CSafeLoader` keeps only the original constructors, clears implicit resolvers, joins escaped surrogate pairs, and refuses duplicate keys without two-argument `super()`.
`yamlio.load_yaml` tries this loader only when libyaml is available and the guard admits the header.
Any C exception falls through to the unchanged Python loader and its error conversion.
The module remains internal to core.

The tests cover synthetic builder and sample records, all optional decision fields, areas, thread headers and author and agent message blocks, Unicode, JSON escapes, the explicit rejected shapes, the trailing-tab regression, a C-call counter, absent libyaml, and injected C exceptions.
The seeded differential test constructs 20,000 headers with random keys, random plain and JSON-string values, edge cases including surrogate escapes, and single-character mutations.
The pre-change Python loader and its error conversion are retained as the test oracle.
Seed `20261101`: libyaml parsed 8,466 of 8,637 admitted headers (98.02%); all 20,000 public-load outcomes matched the oracle in value or error message and line.
C failures among admitted headers are expected, including YAML-unreadable characters and duplicate keys, and take the Python fallback.

Command: `uv run --frozen pytest tests/core/test_yaml_guard.py tests/core/test_yaml_fuzz.py tests/core/test_yamlio.py tests/core/test_fileformat.py tests/core/test_fileformat_problems.py tests/core/test_thread_files.py tests/test_structure.py -q -s --tb=short`.
Result: 250 passed in 5.91 s.
Strict mypy passed (207 files), Vulture passed, and targeted Ruff checks passed.
A test fixture initially put a literal tab in a title that the existing writer refuses; it was corrected to use valid titles, while the quote fixture still covers escaped tabs and newlines.
The mixed record list also received an explicit `list[Record]` annotation for strict mypy.
No existing test was edited, and no structure or tool rule was changed.

## Timings

The benchmark store is `/var/tmp/lodge-bench/s9000`, generated by `scripts/bench_store.py`, holding 16,120 files on native ext4.
Both modes use the same native-disk virtual environment: CPython 3.13.5, PyYAML 6.0.3, and libyaml 0.2.5.
`uv run --frozen python -m compileall -q src .venv/lib` compiled source and dependency bytecode before timing.
A scratch copy of `probes/phases.py` removes both the `_missing` and experimental C-loader patches, so it measures the production code from Tasks 2 and 3.
Its `--pure-yaml` mode sets `yaml.__with_libyaml__ = False`; the other mode uses the production guard and loader, with a counter on guard calls.
Its temporary SQLite files live under the benchmark folder.
The repository probe is unchanged, and collection remains enabled as in its original call pattern.

Commands, each run three times sequentially:

```sh
uv run --frozen python /var/tmp/lodge-bench/phases-task3.py /var/tmp/lodge-bench/s9000
uv run --frozen python /var/tmp/lodge-bench/phases-task3.py /var/tmp/lodge-bench/s9000 --pure-yaml
```

Each cell below is the best of three seconds.

| Phase | Guarded libyaml (s) | Python only (s) |
|---|---:|---:|
| store.trees (walk and read, merge base, ls-tree, cat-file) | 0.488 | 0.500 |
| load(current) | 0.661 | 3.116 |
| check_state(current) | 0.068 | 0.069 |
| derive(current) | 0.039 | 0.038 |
| load(published) | 0.653 | 3.096 |
| check_change(published, current) | 0.227 | 0.226 |
| level1 of every record | 0.026 | 0.025 |
| search_counted('berth crane', 20) | 0.137 | 0.144 |
| pickle.dumps of every parsed record, one by one | 0.050 | 0.050 |
| pickle.loads of every parsed record, one by one | 0.055 | 0.055 |
| sqlite insert of every parsed record | 0.100 | 0.102 |
| sqlite select of every parsed record | 0.018 | 0.019 |
| sqlite insert of every level-1 line for one state | 0.041 | 0.042 |
| sqlite select of ten level-1 lines | 0.000 | 0.000 |

Every guarded run admitted 32,240 of 32,240 headers across the current and published loads, a share of 100%.
The current load fell from 3.116 s to 0.661 s, about 4.7 times faster, and the published load fell from 3.096 s to 0.653 s, also about 4.7 times faster.
These are phase timings, not end-to-end read timings; the probe independently calls derivation and checks.
The illustrative SQLite file was 47.6 MB in both modes and was removed by the probe.

## Final gate and delivery

`UV_FROZEN=true sh scripts/check.sh` passed: 581 files already formatted, Ruff clean, strict mypy clean (207 source files), Vulture clean, 1,473 tests in 50.46 s, and `lodge check --gate` (`ok`).
`git diff --check` passed.
The task is delivered by the commit carrying this report, on `read-speed-build`.
Only `core/yamlfast.py`, `core/yamlio.py`, the two new YAML test files, and this report are included.
No project records, existing tests, benchmark source files, or Tasks 1 and 2 files were changed.

## Concerns

No unresolved correctness or implementation concern.
Headers outside the specified grammar and admitted headers rejected by libyaml intentionally retain the Python loader's speed and diagnostics.
The timing improvement is for snapshot loading at `s9000`; this task makes no end-to-end latency claim.
