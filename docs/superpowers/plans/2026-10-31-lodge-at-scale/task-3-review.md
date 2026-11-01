# Review of Task 3 (libyaml behind a guard), commit 07dacb5

Reviewer: Claude (Opus), task review in three passes: correctness, practice, design.
Worktree: detached at 07dacb5 under /var/tmp/lodge-review-t3/wt, removed after the review; the fuzz scripts stay under /var/tmp/lodge-review-t3/.
Counts: 0 Blocking, 2 Important, 4 Minor.

## What was run

- Oracle: the pre-Task-3 `src/lodge/core/yamlio.py` from the parent commit bd7e03b, loaded as its own module (`/var/tmp/lodge-review-t3/old_yamlio.py`), so the oracle is the code as it was, not a copy in the test.
- Grammar fuzz (`/var/tmp/lodge-review-t3/fuzz.py`, seeds 1000 to 1015, 16 workers): 256,864 headers.
  Generator: the writer's five line shapes, keys from `abc_` (so duplicate keys are frequent), 1% keys of 1,015 to 1,030 characters (across libyaml's 1,024 simple-key limit), plain values including `yes`, `no`, `null`, `1234`, `0x1F`, `1.5`, `14:14`, `a:b`, `a::b`, `.inf`, and 1,000-character plains, JSON strings with random code points (C0, C1, U+FFFE, U+FEFF, U+2028, non-BMP), escaped surrogates (pairs, lone high, lone low, reversed, upper and lower case), YAML-only escapes (`\0`, `\e`, `\N`, `\x41`, `\U0001F600`, `\ `), and in 45% of headers one to three mutations (insert or replace a tab, space, CR, `#`, `|`, `>`, `&`, `*`, `!`, `%`, `?`, quote, backslash, BOM, U+2028, NUL, surrogate; delete a character; duplicate a line; indent a line; CRLF; trailing tab, space, `# c`, blank line).
  A fixed set of 54 cases precedes each seed: trailing tabs (`title: x\t`, `title:\tx`, `- a\t`, `title: x\t# c`, after flow collections), escaped surrogate pairs and lone halves in block, flow sequence, and flow mapping, duplicate keys in block, flow mapping, and list item, `yes`/`1234`/`~`/`null`, nesting 600 deep in sequences and 300 deep in mappings, CRLF in each shape, block scalars, anchors, tags, merge keys, directives, and document markers.
  Per header: `yamlio.load_yaml` against the old loader in value (type-aware, key order included) or in exception class, message, and line; for admitted headers, the C loader's value against the old loader's whenever the C loader succeeds.
  Result: 0 violations; 73,438 admitted, of which 57,104 parsed by libyaml with equal values and 16,334 failed in C where the old loader also failed (duplicate keys, C1 characters, U+FFFE); 0 cases of C failing where Python succeeds; 0 cases of C succeeding where Python fails.
- Writer fuzz (`/var/tmp/lodge-review-t3/fuzz_writer.py`, seeds 700 to 715): 128,000 attempts, 42,163 records, areas, and threads written by `write_record`, `write_area`, and `write_thread` with random Unicode titles, quotes (with line breaks and tabs), where/when, numbers, attachments, imports, and `decided_by` values such as `yes` and `1234`; 52,919 headers and message blocks admitted and parsed by libyaml to the old loader's value, 0 differences.
  The 1,460 written headers not admitted all hold U+FEFF inside a quoted string, which the guard refuses by d-q051s2's list; they take the Python loader (see M4).
- Targeted: `'a'*1030 + ': b'` in block, flow mapping, and list item (admitted, C fails, fallback gives the old error and line), 200,000-character plain and quoted values (admitted, equal), `x: [a:b, c:d]`, `x: {k: a:b}`, `{k: 1:2:3}` (admitted, equal under PyYAML 6.0.3 and libyaml 0.2.5).
- Without libyaml (a `sitecustomize` blocking `yaml._yaml`, so `yaml.__with_libyaml__` is False and `CSafeLoader` absent): the grammar fuzz at seeds 3000 to 3015, 64,864 headers, 0 violations; `yamlio.load_yaml` works and never touches `yamlfast.load_yaml`; but three tests fail (I1).
- Gate with libyaml: `UV_FROZEN=true sh scripts/check.sh` in the review worktree passed, 1,473 tests, `lodge check --gate` ok; `test_yaml_fuzz.py` alone 11.5 s.

Answer to the brief's main question: no header the Python loader rejects was accepted, and no header got a different value, error message, or line, across 321,728 grammar headers (with and without libyaml) and 52,919 writer headers.

## Correctness

### I1 (Important): three tests fail where PyYAML has no libyaml

Handle: `tests/core/test_yaml_fuzz.py:125` (`assert c_successes > 1000`), `tests/core/test_yaml_guard.py:68` and `:72` (`yamlfast.load_yaml` called directly), `tests/core/test_yaml_guard.py:107-108` (expects the C path to be called).
Scenario: a contributor on a platform without a PyYAML wheel (a source build without libyaml headers, or a new CPython before wheels exist) runs `sh scripts/check.sh`; run: `PYTHONPATH=/var/tmp/lodge-review-t3/nolib uv run --frozen pytest tests -q` gives `3 failed, 1470 passed`, the first two with `assert 0 > 1000` and `NameError: name '_CTextLoader' is not defined`.
lodge itself behaves correctly there; only the gate is red, for a configuration the plan names as supported ("otherwise today's loader").
Fix: `LIBYAML = getattr(yaml, "__with_libyaml__", False)`; mark `test_c_loader_used_for_admitted_headers` with `pytest.mark.skipif(not LIBYAML, reason=...)`; in `test_every_written_header_is_admitted` and the fuzz keep the `admitted` and `yamlio.load_yaml`-equals-oracle assertions unconditional and guard only the direct C calls and the `c_successes` floor with `if LIBYAML`.

### M1 (Minor): `yamlfast.load_yaml` raises `NameError` when libyaml is absent, and its interface differs from the plan's

Handle: `src/lodge/core/yamlfast.py:77-79` against the plan's Task 3 Produces (`load_yaml(text)`: "the C loader when libyaml is present and admitted(text); otherwise today's loader").
Scenario: any later caller that takes the plan's interface at its word and calls `yamlfast.load_yaml` directly gets `NameError: name '_CTextLoader' is not defined` without libyaml, and the C loader's result for unadmitted text with it (the dispatch lives in `yamlio.load_yaml:58`, not here); the docstring's "raising on absence" names no exception.
Fix: either define the absent branch explicitly (`else: def load_yaml(text): raise RuntimeError("libyaml is not available")`), or keep the code and correct the plan's Produces line to say the dispatch is `yamlio.load_yaml` and `yamlfast.load_yaml` is the bare C loader; the second is the smaller change.

### M2 (Minor, not verified on other versions): the guard admits two forms whose meaning varies across PyYAML and libyaml versions, though the writer never produces them

Handle: `src/lodge/core/yamlfast.py:12` (`:` allowed inside `_PLAIN`, also in flow context through `_MAP` and `_SEQUENCE` at `:16-17`) and `:13` (the `\/` escape); `pyproject.toml:7` (`dependencies = ["PyYAML"]`, no version bound), and a source build links whatever system libyaml there is.
Scenario: equivalence is shown only for PyYAML 6.0.3 with libyaml 0.2.5 (the lock and the wheel); colons inside flow plain scalars (`[a:b]`, `{k: a:b}`) changed meaning between libyaml releases (0.2.1 era) and PyYAML's scanner (the `flow_level` clause at `yaml/scanner.py:1292-1295` in 6.0.3), and `\/` is a YAML 1.2 escape added late to both; an install pairing a Python scanner and a libyaml that disagree on one of these would give the C value for an admitted header the Python loader reads differently or rejects.
I could not build an older libyaml here to show a concrete differing pair, so this is a residual risk, not a demonstrated failure.
Fix (costs no admitted writer output: flow plains in written headers are IDs and action words, which hold no colon, and `json.dumps` never writes `\/`): use a colon-free plain (`[A-Za-z0-9][A-Za-z0-9._+-]*`) inside `_MAP` and `_SEQUENCE`, keep the colon form only for `KEY: PLAIN` lines (the `date:` and `when:` stamps), and drop `/` from the escape class; alternatively gate the C path on `yaml._yaml.get_version() >= (0, 2, 5)`.

## Practice

### I2 (Important): the constructors that define a header's value exist twice

Handle: `src/lodge/core/yamlfast.py:20` (`_SURROGATE_PAIR`), `:21` (`_KEPT_TAGS`), `:42-43` (`_join_pair`), `:46-75` (`_CTextLoader` with its own `construct_scalar` and `construct_mapping`), against `src/lodge/core/yamlio.py:13`, `:17`, `:29-53`.
Scenario: the invariant this task rests on is that the C path yields the Python loader's value; a later change to `_TextLoader` (a kept tag, the duplicate-key wording, how a scalar is post-processed) that is not repeated in `_CTextLoader` makes admitted headers read differently from unadmitted ones, and the fuzz catches it only if the change touches a shape the generator emits; the copies are also already not identical in reach: the surrogate-pair joining in `_CTextLoader` is unreachable, because `_STRING` (`yamlfast.py:13`) refuses escaped surrogates and `_FORBIDDEN` (`:10`) literal ones.
Fix: one mixin, for example in `yamlfast.py`, `class TextConstructor(SafeConstructor)` holding the cleared `yaml_implicit_resolvers`, the filtered `yaml_constructors`, `construct_scalar`, and `construct_mapping` with zero-argument `super()`; then `class _TextLoader(TextConstructor, yaml.SafeLoader)` in `yamlio.py` and `class _CTextLoader(TextConstructor, yaml.CSafeLoader)`; the MRO puts the mixin before `SafeConstructor` in both, which the plan's "without the two-argument super()" allows.
Verify by running `uv run --frozen python /var/tmp/lodge-review-t3/fuzz.py 1000 16 16000` in the fixed checkout (expects `violations 0`; it compares against `/var/tmp/lodge-review-t3/old_yamlio.py`).

### M3 (Minor): the report carries about 490 lines of captured failing output

Handle: `docs/superpowers/plans/2026-10-31-lodge-at-scale/task-3-report.md:17-508`.
Scenario: the plan folder is read by later builders and reviewers; 60 near-identical `NotImplementedError` tracebacks bury the 70 lines that matter (implementation, timings, gate).
Fix: keep the command, the line `60 failed`, and one representative traceback per test function.

### M4 (Minor): `test_every_written_header_is_admitted` claims more than holds

Handle: `tests/core/test_yaml_guard.py:28`, against `src/lodge/core/yamlio.py:14` (`_UNREADABLE` does not hold U+FEFF, so the writer writes it) and `src/lodge/core/yamlfast.py:10` (the guard refuses it).
Scenario: a title such as `"a﻿b"` is written by `write_record` and is not admitted (1,460 of 42,163 writer outputs in the writer fuzz, every one holding U+FEFF); behaviour is correct (the Python loader reads it), but the test's name tells the next reader that written headers always take the fast path.
Fix: name it `test_written_headers_without_bom_are_admitted`, and add one case asserting a U+FEFF title is written, not admitted, and read back equal through `yamlio.load_yaml`.

## Design

No further finding.
`load_yaml`'s dispatch (`yamlio.py:58-62`) is the one place the C path is chosen, every failure falls back to the unchanged Python branch, and error text and lines come only from it, which the fuzz confirms.
The broad `except Exception` hides a broken C path as a slowdown, but the fuzz's `c_successes` floor (`test_yaml_fuzz.py:125`) turns that into a red test wherever libyaml is present.
The guard's character set and grammar match the plan's Task 3 text and d-q051s2 line by line (`yamlfast.py:10-19`).

## Files

Read: `.claude/agents/reviewer.md` (lodge), `CLAUDE.md`, the plan's Task 3 section and Review Focus item 7 (`docs/superpowers/plans/2026-10-31-lodge-at-scale.md:93`, `:167-198`), `task-3-report.md` (implementation, timings, gate, concerns; the failing-output dump skimmed), `src/lodge/core/yamlfast.py`, `src/lodge/core/yamlio.py` (new and at bd7e03b), `src/lodge/core/document.py:1-45`, `src/lodge/core/fields.py:1-80`, `src/lodge/core/fileformat.py:1-60` and `:110-175`, `src/lodge/core/threads.py:85-140`, `tests/core/test_yaml_guard.py`, `tests/core/test_yaml_fuzz.py`, `tests/core/builders.py:1-60`, PyYAML 6.0.3 `yaml/scanner.py` escape table and plain scanner, d-q051s2 through `lodge show --reasoning`.
Not read: the rest of the plan and its other task reports, `lodge spec`, `src/lodge/core/headers.py`, `tests/core/samples.py`, the structure rules, and the Task 4 work in /var/tmp/lodge-build.
