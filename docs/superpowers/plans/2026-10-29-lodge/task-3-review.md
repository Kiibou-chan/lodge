# Task 3 review: records, identifiers, settings, YAML, and drafts

Reviewed: `build-0.1` at 0615d5c (diff 41650f9..0615d5c), in a detached scratch worktree at 0615d5c (removed when done).
Gate in the scratch worktree: `sh scripts/check.sh` green, 388 passed.
Every test the brief names exists (checked by name with `grep`).
Test-first could not be checked from history, since code and tests landed in one commit (1df405a); the report's failing output is taken as given.

## Verdicts

Spec compliance: no.
Gap: the ledger ruling that binds this task, `slug` capped at 60 characters at a word boundary, is not implemented (I2).
Everything else in the brief, the plan's Global Constraints, and the `record_from_draft` date ruling is met: IDs, length defaults, dates with offset and the imported date-only rule, key order, the example literal, the round trip, problem 1 cases, drafts.

Task quality: not approved, 0 Blocking, 2 Important, 8 Minor.

## What I ran

All probes in the scratch worktree with `uv run python`, against `lodge.core` only.

1. Round trip of 48 hand-built decisions, 7 specification entries, and 4 areas: BOM mid and start of a title, NBSP, ZWJ emoji, U+202E, astral and private-use characters, U+FFFD, a literal `A`, `&x` and `*x`, `---`, `...`, `%YAML 1.2`, `decided_by` as `No`, `~`, `0x10`, and `the author`, codes `1234`, `null`, `1e3`, `a.`, a 20,000-character title, a 5,000-character quote, bodies holding `---` lines, tabs, NUL, ESC, lone CR, NEL, U+2028, reasoning with a second `## Reasoning`, every optional field at once, imported dates, offsets `-00:00` and `+23:59`, duplicate and self links.
   Every record `write_record` accepts reads back equal and rewrites byte for byte.
   Refusals: values with leading indentation (M1), empty list items, tab or newline in any header string (M3), upper-case or trailing-hyphen areas; all refusals are `ValueError`, as briefed.
2. 41 hostile header texts through both `parse_record` and `parse_draft`: deep nesting, recursive aliases, merge keys plain and `!!merge`, `!!int`, `!!binary`, `!!set`, `!!python/object`, local and non-specific tags, a second document, `...`, `%YAML` directives, unhashable and null keys, tab indentation, raw NUL and NEL, a leading BOM, lone CR line ends, duplicate keys in flow maps, a 100,000-digit scalar, folded and single-quoted scalars, escaped `\0`, `\N`, lone and paired surrogate escapes.
   All give a `Problem` with a line, or parse to a value the field rules then judge, except deep nesting, which raises `RecursionError` (I1).
3. A seeded fuzz (`random.Random(7)`, 20,000 records, 3,962 writable) over decisions and entries built from a hostile alphabet, with three one-character mutations of each written file fed to `parse_record` and `parse_draft`.
   Result: 0 round-trip mismatches, 0 rewrites differing, 0 exceptions, 0 mutated files that parse but cannot be written.
4. Drafts: indented first lines, whitespace-only `title` and `decided_by`, a quote written by `json.dumps` with its default `ensure_ascii=True`, date-only with import, a CRLF statement; slug lengths for long and non-ASCII titles; a 312-byte file name on the local file system.

## Findings

### I1 (Important, correctness): deep nesting in a header escapes as `RecursionError`

Handle: `src/lodge/core/yamlio.py:44-52` catches only `yaml.MarkedYAMLError` and `yaml.reader.ReaderError`.
Scenario: a draft or a record file holding `work_item: [[[[…]]]]` about 500 levels deep (300 is fine, 500 fails; less under a deeper call stack) makes `parse_record` and `parse_draft` raise `RecursionError` instead of returning `Problem`.
Run: probe 2, rows "deep nesting value", "deep nesting flow map", "deep block nesting", both functions.
One such file pushed to the store breaks every read and the check itself, so the check cannot show the record as failing (must-not 1), and Review Focus 2 ("names the file … exits 2, no traceback") fails for drafts.
Fix: in `load_yaml`, `except RecursionError: raise YamlError("the header is nested too deeply") from None`; test `load_yaml("a: " + "[" * 5000 + "]" * 5000)` raises `YamlError`, and a draft with it is problem 1.

### I2 (Important, spec compliance): `slug` has no length cap, contrary to the ledger ruling

Handle: `src/lodge/core/fileformat.py:79-80`; ruling in `docs/superpowers/plans/2026-10-29-lodge-progress.md` ("`slug` gets a 60-character cap, cut at a word boundary").
Scenario: a title of one 300-letter word gives `d-3m8qk2-aaa….md`, 312 bytes; creating that name locally fails with `OSError: [Errno 36] File name too long` (run in probe 4), so the checkout-mode store cannot write the record, and a branch-mode tree holding it cannot be checked out.
Six 34-letter words give a 231-character path, already near the limit.
Fix: after joining the six words, if the slug exceeds 60 characters cut it at the last `-` at or before position 60, and when the first word alone is longer, cut that word at 60; compute it once in `new_record_path` (`fileformat.py:69` calls `slug` twice).
Tests: a 300-letter word gives 60 characters; six 15-letter words give the longest prefix of whole words within 60; a slug under 60 is unchanged.
Note for the author, not part of the fix: non-ASCII titles slug lossily (`Größenänderung über İstanbul` gives `gr-en-nderung-ber-i-stanbul`); folding needs `unicodedata`, which is not on the core allow-list, so that is her call.

### M1 (Minor, correctness): the first line's indentation of a statement or reasoning is silently dropped

Handle: `src/lodge/core/document.py:52-53`, `src/lodge/core/drafts.py:41`, `src/lodge/core/headers.py:88` and `:107` use `str.strip()`.
Scenario: a draft whose reasoning starts `  - a nested-looking item\n  - b` is stored as `- a nested-looking item\n  - b`, and a statement starting with an indented code block loses the block on its first line only; no problem is reported, so the stored text differs from what was written.
`write_record` refuses such a record when built directly ("not trimmed"), so only the draft route mangles it.
Fix: trim only blank lines at the ends and trailing whitespace (`"\n".join(lines).strip("\n").rstrip()` after dropping leading blank lines), in all four places; canonical files written today never start with indentation, so the relaxed rule reads them identically.

### M2 (Minor, correctness): whitespace-only required strings are accepted

Handle: `src/lodge/core/fields.py:43` checks `not value` only.
Scenario: a draft with `title: "   "` and `decided_by: " "` becomes a decision with a blank title at `lodge/decisions/d-3m8qk2.md` (probe 4).
Tightening this after records exist would make published records fail, so it is cheapest now.
Fix: `if not isinstance(value, str) or not value.strip()`; test a blank `title` and `decided_by` are problem 1.

### M3 (Minor, design; the brief mandates the current behaviour, so a ruling): a quote cannot hold a line break

Handle: `src/lodge/core/yamlio.py:12` includes `\t` and `\n` in `_UNREADABLE`; `src/lodge/core/fields.py:45-47`.
Scenario: her words copied verbatim from a source written one sentence per line contain `\n`; `quote.text` refuses them, so the recording agent must join the lines, which changes her words.
The brief's reason ("YAML cannot read some of them back") does not hold for `\n` and `\t`: a JSON-escaped `"a\nb"` reads back unchanged.
Fix: allow `\n` (and `\t`) in `quote.text` only, keep the rest of the rule; accepting more later is compatible, so this can wait for the final wave if the author prefers.

### M4 (Minor, correctness): drafts quoted with `json.dumps` defaults are refused for any emoji

Handle: `src/lodge/core/yamlio.py:12` (lone surrogates) applied by `fields.py:45`.
Scenario: an agent writing a draft's quote with `json.dumps("Ship it 😀")` gets `"Ship it 😀"`; PyYAML decodes the escapes one by one into lone surrogates, and the draft is problem 1 with "holds U+D83D, which a header cannot carry" (probe 4).
The format itself says free text is a JSON string, so this is the natural way to write one.
Fix: in `load_yaml`'s scalar construction, or in `read_str`, rejoin surrogate pairs with `value.encode("utf-16", "surrogatepass").decode("utf-16")` before the check, falling back to the check when a lone surrogate remains.

### M5 (Minor, practice): `write_record` names the wrong cause for a mismatch

Handle: `src/lodge/core/fileformat.py:51`, `:64` ("as a value is not trimmed").
Scenario: an imported decision with `date="2026-10-28"` and a statement holding `\r\n` are both refused with "not trimmed" (probe 4), though the causes are date normalisation and line-end normalisation.
Fix: name the first field that differs, e.g. `next(f.name for f in fields(record) if getattr(back, f.name) != getattr(record, f.name))`.

### M6 (Minor, design): problems from `record_from_draft` carry no line

Handle: `src/lodge/core/drafts.py:65-66`.
Scenario: a draft with `title: [a, b]` passes `parse_draft` (key names only) and fails in `record_from_draft` with `line=None`, while the same header as a record file reports its line; Review Focus 2 asks for the line where known.
Fix: keep the header text on the draft (a private field or a `lines: Mapping[str, int]`), and use `_key_line` for the problem; the plan's `Draft` signature would gain a field, so note it in the ledger.

### M7 (Minor, practice): small clarity items

- `src/lodge/core/settings.py:33-36` computes `kind` and then branches on it twice; write the two messages in one `if`.
- `src/lodge/core/ids.py:8` repeats `ALPHABET` by hand as `[0-9a-hjkmnp-tv-z]`; build it as `re.compile(rf"[ds]-[{ALPHABET}]{{{ID_LENGTH}}}")` so the two cannot drift.

### M8 (Minor, design): core knows the other packages' section names

Handle: `src/lodge/core/settings.py:25` and `:31` (`OTHER_PACKAGES = {"store", "hook"}`); the plan's Task 9 `load_settings` (plan line 405) also checks "known sections".
Scenario: a section added for a new adapter must be added in two places, and core's check rejects it if only `load_settings` learns of it.
Fix: let `parse_core_settings` take only `[length]` and `[import]` tables (or the whole table and ignore other sections), and leave unknown-section detection to `load_settings`, which sees every package; or record the split as a ruling.

## Design notes without findings

- The round trip holds by construction: `write_record` re-parses its own output and refuses any record that does not read back equal (`fileformat.py:47-51`), so `write_record(parse_record(p, t)) == t` follows for every text it emits; the fuzz confirms it.
- Header equality is exact: parsed values are frozen dataclasses with tuples, the imported date-only form is normalised on parse, and plain against quoted spellings (`decided_by: author` and `"author"`) parse equal, so the later immutability check can compare parsed headers.
- The `record_from_draft` date ruling is implemented as written and tested (`tests/core/test_drafts.py:326-353`).
- Codes, `decided_by`, and dates are written plain, as briefed; a generic YAML 1.1 reader would read `code: 1234` or `decided_by: No` as a number or a boolean, which is acceptable only while lodge is the format's sole reader.

## Files read

Read: `CLAUDE.md`; `.claude/agents/reviewer.md`; plan sections Global Constraints, Process, Calls made, Review Focus, Task 3, and grep hits for later uses of Task 3's interfaces; spec sections Must nots, Constraints, The model, Levels, Storage; ledger tail; task 3 brief and report; every file under `src/lodge/core/`; every file under `tests/core/`; `vulture_allow.py`.
Not read: the review package diff itself (read the files at 0615d5c instead, same content per `git diff --stat`); `tests/structure_rules.py` and the structure test (their pass in the gate taken as evidence of purity and size); plan Tasks 4 to 14 beyond grep hits; the rest of the spec.
