# Task 3 recheck, fix round 1

Rechecked: `build-0.1` at 1b6f314 against dba944f, diff `.superpowers/sdd/2026-10-29-lodge/review-dba944f..1b6f314.diff`.
Scope: findings I1, I2, M1 to M8 of `task-3-review.md`, and the two ledger rulings (quote text line breaks and tabs, surrogate pairs).
Scratch worktree: detached at 1b6f314 under `.claude/worktrees/recheck-3-1`, removed when done.
Gate in the scratch worktree: `sh scripts/check.sh` green, 410 passed.
Test diff: additions only (`tests/core/test_drafts.py` +34, `tests/core/test_yamlio.py` +16, new `tests/core/test_fileformat_text.py`); no existing test was changed or removed.

## Verdicts per finding

- I1 deep nesting: answered, `src/lodge/core/yamlio.py:62-63`.
  Probe: depths 50 to 5,000 under `work_item`, `code`, `title`, `quote`, `changes`, and `numbers`, through `parse_record`, `parse_draft`, and `record_from_draft`: every one a `Problem`, none raised; depth 120 under a caller 800 frames deep is also a `Problem` ("nested too deeply"), not a traceback.
- I2 slug cap: answered, `src/lodge/core/fileformat.py:82-88`, computed once at `:71`.
  Probe: titles of one word of 55 to 65 letters, each alone, with ` yz`, and with five short words after it: every slug at most 60 characters, no leading or trailing hyphen, only whole words unless the first word is over 60, and every such decision round-trips.
  The longest spec path for a 50-character area and a 300-letter title is 134 characters.
- M1 first-line indentation: answered, `src/lodge/core/document.py:47-52`, used at `document.py:60-61`, `headers.py:93`, `headers.py:112`, and `drafts.py:45`; no `body.strip()` is left in `src/lodge/core/`.
- M2 blank strings: answered, `src/lodge/core/fields.py:43`.
  `"　"`, `"\xa0"`, and `"\x85"` titles are problem 1; `"​"` is accepted, as Unicode does not count it as whitespace, which is outside the finding.
- M3, as ruled: answered, `src/lodge/core/yamlio.py:16`, `fields.py:68-90`, `headers.py:136`, and the quote line in `fileformat.py` (`_quoted("quote.text", …, LINE_BREAKS_AND_TABS)`).
  `quote.where`, `quote.when`, `title`, `work_item`, `decided_by`, `imported_from.heading`, and `numbers.value` still refuse a newline or tab (probe); `quote.text` still refuses VT, FF, NEL, U+2029, NUL, U+001F, and a lone surrogate.
- M4, as ruled: answered, `src/lodge/core/yamlio.py:35-37` with `_join_pair`.
  Drafts quoting `Ship it 😀`, a ZWJ family emoji, U+10FFFD, and `a\nb 😀\tc` with `json.dumps` defaults all become the intended `Quote`, in `where` too, and the record round-trips; a lone or reversed pair stays lone and is problem 1.
- M5 wrong cause: answered, `src/lodge/core/fileformat.py:53`, `:66`, `:106-111`.
- M6 draft lines: answered, `src/lodge/core/drafts.py:33`, `:45`, `:70`, with `document.py:79-82`.
  Probe: a draft's bad `quote.text`, `work_item`, `changes.entry`, and `date` each carry line 6, the line of their top-level key.
  The `Draft` signature gained `header_text: str = ""`; the report says it is to be noted in the ledger, and the ledger at 1b6f314 does not note it yet (`grep header_text` in `2026-10-29-lodge-progress.md` finds nothing).
- M7: answered, `src/lodge/core/settings.py:33-35` and `src/lodge/core/ids.py:8`; the built pattern is `[ds]-[0123456789abcdefghjkmnpqrstvwxyz]{6}`, the same set as before.
- M8: unchanged, as ruled.

## Round-trip probe over the changed paths

Script `probe.py` in the scratchpad, run with `uv run python` in the scratch worktree; output in `probe-out.txt` beside it.
For every record `write_record` accepts: `t = write_record(r)`, then `parse_record(new_record_path(r), t) == r` and `write_record(parse_record(…)) == t`.

- Indentation: 40 decisions (10 statements with indented first lines, spaces, tab, U+3000, an indented `## Reasoning`, ` ---`, `   ...`, times 4 indented reasonings), 10 specification entries, and 3 areas: all equal and byte-identical on rewrite.
- Quotes: 14 multi-line or emoji texts (`\n`, `\r\n`, lone `\r`, leading and trailing `\n`, tabs, ZWJ sequence, combining accent, U+10FFFD, a literal backslash-n): all round-trip, written as JSON escapes on one line.
- Slugs: 33 titles at the cut points, all round-trip.
- Seeded fuzz (`random.Random(7)`, 20,000 candidates over an alphabet with indentation, tabs, CR, emoji, `## Reasoning`, and `---`): 3,048 written in all, 0 mismatches, 0 rewrites differing, 0 exceptions; 3 one-character mutations of each of 2,947 fuzz files gave 0 exceptions and 1 file that parses but cannot be rewritten (below).

## New problems introduced by the fix

None at Blocking or Important.

## Observations outside the findings

- Pre-existing, Minor, parkable: a body holding `\r\r\n` parses (`normalise_newlines`, `src/lodge/core/document.py:14-15`, turns it into `\r\n`, not `\n`) but `write_record` then refuses it, since the rewrite normalises once more; the same happens at dba944f, so the fix did not introduce it.
  Scenario: a record file edited by hand or by a tool with `\r\r\n` line ends is valid for the check but cannot be edited through lodge.
  Fix: normalise to a fixed point, or treat a lone `\r` in a body as problem 1.
- Harmless: `_TextLoader.construct_mapping` checks duplicate keys on the raw scalar, so `"😀": a` and `😀: b` collapse silently to one key after the pair join; every header and nested map rejects non-ASCII key names as unknown, so no record can be affected.

Scratch worktree removed (`git worktree list` shows no `recheck-3-1`).
