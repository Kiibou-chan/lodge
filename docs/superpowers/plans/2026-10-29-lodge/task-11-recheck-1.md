# Task 11 recheck 1: fix round de95297

Fix diff dc173dd..de95297, against task-11-review.md (I1, M1 to M4) and the two Task 11 rulings in the ledger (`core.spec_view`, `NotFound`).
Rechecker: `rechecker`.

## Verdict

Clean: 0 Blocking, 0 Important, 2 Minor (N1, N2), both parkable.
All five findings answered.

## What I ran

- Fresh copy `git archive de95297` into `scratchpad/t11fix`, its own environment (`UV_PROJECT_ENVIRONMENT=scratchpad/t11venv`), `GIT_CONFIG_GLOBAL` empty, `GIT_CONFIG_NOSYSTEM=1`: `sh scripts/check.sh` green, 953 passed (ruff format, ruff, mypy, vulture all passed before pytest, since the script is `set -eu`).
- Red on the old code: `scratchpad/t11old` = de95297's tests over dc173dd's `src`, `PYTHONPATH=src`, checked that `lodge.__file__` is the old copy.
  13 failed, 2 collection errors (`tests/core/test_render.py`, `tests/app/test_reads.py`, both on the missing `spec_view` import or the three-value `spec`).
  The ones that fail on behaviour, not only on the new signature: `test_record_page_links_only_ids_whose_status_is_known` (old page linked `d-zzzzzz` and gave `d-aaaaaa` no status), `test_record_page_flags_and_both_link_directions` (no status after the flag's link), `test_lodge_error_is_a_page_with_its_message` (400 != 404), `test_spec_escapes_hash_lines_inside_a_statement` (no `\## Fake` line).
  `test_spec_page_builds_headings_from_fields_never_from_text` fails on the old code only by unpacking (expected 3, got 2); its assertions are the ones the old page broke in my review probe, so it pins I1, but it was not seen red on an assertion.
- Probes: `probes-t11/probe_pages_r1.py` (my first probe adapted to the new `spec` signature, plus a statement line `   ## Indented (s-yyyyyy)`), output in `probes-t11/r1/`; `probes-t11/probe_server.py` unchanged.
  No raw tag or broken attribute on any page; banner above `<main>` on all eight content pages; the spec page now has one `<h1>` and one `<h2>` with every statement and intro line inside `<p>`.
  Server: 127.0.0.1 only, `::1` refused, foreign or missing `Host` 403, `/r/..%2F..%2Fpyproject.toml` and `/r/<script>"` 404 with the name escaped, `/spec?area=<b>nope` 404, `?kind=<b>` 400, HEAD 200 with no body, POST 405.

## Findings

- I1: answered.
  `core/render.py:23-28` (`spec_view`) returns `SpecArea` with `Level1` entries; `viewer/pages.py:108-116` builds headings from `title`, `id`, and `flags`, and statements and intros only through `paragraphs`; `_ENTRY_HEADING` and its coupling to the ` · ` format are gone.
  `render_spec` escapes intro and statement lines starting with `#` (`render.py:63`), as the ruling says.
- M1: answered, in a narrower way that loses some links (see the judgement below).
  `viewer/html.py:29-39` links an ID only when the map gives its status and writes the status beside it; `pages.py:21-23` builds the map from the record and its provenance links.
- M2: answered (`pages.py:7-9`, `server.py:147-149`; scopes from `Scope`).
- M3: answered (`server.py:46-67`; HEAD body suppressed by `self.command` alone, probe confirms).
- M4: answered (`app/errors.py:14`, `app/state.py:69-75`, `server.py:103`); the CLI still exits 2 because `NotFound` keeps `exit_code = 2`; an ambiguous code stays a plain `LodgeError` (400), which is right.

## The builder's M1 reading: IDs in flags on list and spec pages are now plain text

It holds the brief (no link without its status) and costs navigation, not correctness: the flag's own words still say what happened ("replaced by d-x"), and the record's own status sits in the meta line.
What is lost: on search and timeline rows, "replaced by", "narrowed by", "retired by", and "its decision replaced by" no longer jump to the record that supersedes the one shown; on the specification page, "awaiting the author on d-x" no longer jumps to the agent decision that waits for her, which is the page where she is most likely to meet a flag.
Each is now two clicks (the entry, then its flag on the record page, where the link and status are present) or a copied ID.
The waiting page loses nothing: its rows are the agent decisions themselves, flagged "awaiting the author" with no ID, and the title links.
Recorded as N2 (Minor).

## New problems introduced by the round

### N1 (Minor): the hash escape misses indented headings and setext underlines in `lodge spec`

`core/render.py:10` matches `^#` only; CommonMark still reads a line indented by up to three spaces (`   ## Indented (s-yyyyyy)`, probe output) as a heading, and a line followed by `---` or `===` as a setext heading.
Failure: `lodge spec` piped into a Markdown renderer shows a statement line as a heading; the viewer is unaffected (probe: `<p>## Indented (s-yyyyyy)</p>`).
The ruling's literal wording ("a line starting with `#`") is met.
Fix: `re.compile(r"^( {0,3})#", re.MULTILINE)` with replacement `r"\1\\#"`, and the same treatment for a line made only of `-` or `=` after a non-blank line; one more case in `test_render_spec_escapes_lines_that_start_with_a_hash`.

### N2 (Minor): IDs in flags on list and spec pages are not links

`viewer/html.py:63-65` with no map from `pages.py:77` (`_results`) and `pages.py:115` (`_spec_entry`).
Failure: as described above, one click becomes two to reach the superseding or waiting decision.
Cheap fix: carry the whole status map on `Read` (`statuses: Mapping[str, str] = field(default_factory=dict)`, filled in `read_state` from `state.derived.status`, which already holds every record's status), and pass `read.statuses` to `linked` on every page; that also links reasoning mentions of records outside the provenance links, with their status, and lets `record_page` drop its own map.
Cost: one field on `Read` and one argument per page call.

## Files read

Read: `.claude/agents/rechecker.md`; the ledger's last lines (both rulings); the report's "Fix round 1"; the source and test diff dc173dd..de95297 for `src/` (app errors, `lodge.py`, `reads.py`, `state.py`, `cli/commands.py`, `core/__init__.py`, `core/render.py`, viewer `html.py`, `pages.py`, `server.py`), `tests/viewer/`, and `tests/core/test_render.py`.
Not read: the diffs of `tests/app/test_reads.py` and `tests/e2e/test_spec.py` (seen only through their failures on the old code); the review package file as a whole.
