# Task 11 review: the viewer

Commit 52ee558 (base 018c17b), branch `build-0.1`.
Reviewer: `reviewer`, three passes (correctness, practice, design).

## Verdicts

Spec compliance: no.
Gaps: the specification page lets a statement or an area intro forge headings, so text of a flagged entry can read as an unflagged entry (must-not 1, I1); IDs linked inside decision reasoning carry no status, against the brief's "every linked ID ... with its status beside it" (M1).
Task quality: not approved, pending I1.

Counts: 0 Blocking, 1 Important, 4 Minor.

## What I ran

- Scratch copy: `git archive 52ee558 | tar -x` into `scratchpad/t11src`; Python from the build worktree's `.venv` with `PYTHONPATH=src`, so the copy's code ran (checked: `lodge.__file__` is the scratch path); `GIT_CONFIG_GLOBAL` an empty file, `GIT_CONFIG_NOSYSTEM=1`.
- `pytest -q tests/viewer tests/e2e/test_view.py tests/test_structure.py tests/test_structure_io.py`: 256 passed.
  I did not rerun the whole `scripts/check.sh`; the builder reports it green with 948 passed.
- `probes-t11/probe_pages.py`: a project whose area title, area intro, entry title, decision title, statement, reasoning, quote text, quote place and time, work item, attachment name, unreadable file path and message, search query, and area and decided-by filters all hold `"'><script>x()</script><img src=x onerror=y>`, plus an entry statement with a `## ... (s-zzzzzz)` paragraph.
  Every page (three record pages, spec, search, timeline, waiting, problems, error) rendered with no raw `<script`, `<img`, or broken attribute; the banner sat above `<main>` on all eight content pages.
  Rendered pages saved as `probes-t11/*.html`.
- `probes-t11/probe_server.py`: raw socket requests against `make_server(world, 0)`.
  Results: bound to `('127.0.0.1', port)`, `::1` refused; no `Host` (HTTP/1.0) 403; `localhost.:port` 403; two `Host` headers, foreign first, 403 (good first gives 200, which a browser cannot send, so no finding); absolute URI `GET http://evil.example/spec` serves `/spec` (harmless, the `Host` check still applies); `//evil.example/style.css` 404; `/x/../style.css` 404; `/r/..%2F..%2Fpyproject.toml` 400 "no record named ../../pyproject.toml" (resolved in memory by `resolve_ref`, no file read); `/r/%3Cscript%3E%22` 400 with the name escaped; `?kind=<b>` 400 escaped; `/spec?area=<b>nope` 400 escaped; `HEAD /spec` 200 with headers and an empty body; `POST` 405 with `Allow: GET, HEAD`; `TRACE` 501 from the standard library.

## Correctness

### I1 (Important): a statement or area intro forges headings on the specification page

`src/lodge/viewer/pages.py:130-133` and `:204-209` re-parse the Markdown that `core/render.py:35-38` produced, treating any blank-line block that starts with `## ` as an entry heading and `# ` as an area heading.
`render_spec` writes statements and intros verbatim (`render.py:25`, `:38`), so the parser cannot tell its own headings from text inside a record (the builder's concern 3).
Failure, reproduced by `probe_pages.py`: entry `s-aaaaaa` is flagged "awaiting the author on d-bbbbbb" and its statement is `Held.\n\n## A clean looking entry (s-zzzzzz)\n\nThis paragraph now sits under it.`; the page shows
`<h2>T ... (s-aaaaaa · awaiting the author on d-bbbbbb)</h2><p>Held.</p><h2>A clean looking entry (<a href="/r/s-zzzzzz">s-zzzzzz</a>)</h2><p>This paragraph now sits under it.</p>`.
The second half of a flagged entry reads as a separate, unflagged entry with a link to a record that does not exist: a short entry reading more settled than it is (must-not 1).
An ordinary Markdown sub-heading in a statement (`## Details`) does the same without any intent, and an intro starting `# ` becomes a second area heading (seen in the probe).
The same ambiguity sits in the CLI's `lodge spec` output, where a reader cannot tell either.
Fix (recommended): stop re-parsing.
Have `core` return the specification as structure, for instance `spec_sections(s, d, failing, area) -> tuple[SpecSection, ...]` with each section's area title, intro, and `Level1` entries; `render_spec` becomes a formatter over it (CLI text unchanged); `Lodge.spec` (or a sibling) returns the sections with the `Read`; `spec_page(sections, read)` builds each heading from `Level1` fields and each statement and intro with `paragraphs`, so no record text can become markup.
This changes the brief's `spec_page(markdown, read)` signature, so it needs a ledger ruling; it also removes the coupling of `_ENTRY_HEADING` (`pages.py:106`) to the exact ` · ` format in `render.py:37`.
Fix (if the signature must stay): `render_spec` escapes every intro and statement line matching `^ {0,3}#` with a leading backslash (also correct Markdown for the CLI), and `spec_page` renders a block as a heading only when it starts with `#`/`## `, turning `\#` back into `#` inside paragraphs.
Test either way: an entry flagged "awaiting the author" whose statement holds `## Fake (s-zzzzzz)` and an area intro starting `# ` render with exactly one `<h1>` and one `<h2>`, and the fake text inside `<p>`.

### Must-not 1, the rest: holds

- Flags: `level1_body` (`html.py:70-72`) prints meta (ID, code, status, who decided, day, scope or area), then flags, then statement, then quote, on the record page and on every search, timeline, and waiting row; "fails check" and "decision fails check" come through as flags (`core/views.py:186-189`).
- Quote at level 1: outside `<details>` (`test_record_page_shows_the_quote_outside_the_details`, and probe `record_a.html`); provenance repeats it only when level 1 has none (`pages.py:184`).
- Replaced or retired status: beside every provenance link (`pages.py:193-196`), and in the meta of every result row; spec entries are current only.
- Banner: names each unreadable file with path, line, and message above `<main>` on all six pages (`test_broken_file_named_above_page_content`, parametrised; the brief's name `test_broken_file_named_above_record_page` became this, covering more).
- Unknown filters are a 400 rather than silently ignored (`server.py:391-401`), which keeps a mistyped status from quietly showing only current records.

### Safety: holds

Escaping everywhere I could reach (probe above); the CSP `default-src 'none'; style-src 'self'` blocks scripts even if an escape were missed; the `Host` check is an exact match on `127.0.0.1:<port>` or `localhost:<port>` (`server.py:50-52`), which stops DNS rebinding; bound to `127.0.0.1` only; `/style.css` reads one fixed package file (`server.py:100`); `/r/<ref>` resolves in memory; no route writes, and other methods are 405.

## Practice

### M1 (Minor): IDs linked in decision reasoning and flags have no status beside them

`pages.py:123` renders reasoning through `paragraphs(..., link_ids=True)`, and `html.py:56` links IDs inside flags; `linked` (`html.py:28-30`) adds no status.
Failure: a reasoning saying "as d-xxxxxx settles" where d-xxxxxx was replaced shows a bare link; the reader learns it was replaced only by clicking.
The brief asks for every linked ID with its status beside it; the CLI shows reasoning as plain text, so this is a gap the viewer opened by linking.
Fix: link only where the status is known: build a map from `shown.level3.links` (and the record itself) and have `linked` append `<span class="status">…</span>` for IDs in it; leave IDs outside the map as escaped text, not links.

### M2 (Minor): kind and status lists defined twice

`pages.py:107-109` and `server.py:263-264` both hold `("decision", "spec")` and `("current", "replaced", "retired", "any")`.
Failure: a new status added to one leaves the form and the validator disagreeing (the form offers a value the server rejects with 400).
Fix: one definition (in `pages.py`, imported by `server.py`, or derived from `Filters`' `Literal` types with `typing.get_args`).

### M3 (Minor): `with_body` and the `HEAD` check do the same job

`server.py:282-283` passes `with_body=False` for HEAD, and `server.py:315` also tests `self.command != "HEAD"`; the second alone covers both (it is the one that keeps the 403 body off a HEAD).
Fix: drop the `with_body` parameter from `_answer` and `_send`.

## Design

### M4 (Minor): "no record named x" is a 400

`server.py:352-353` maps every `LodgeError` to 400, so a missing record or area is 400, not 404 (the builder's concern 1).
Failure: none for a person in a browser; a script or link checker reads a dead link as a bad request.
Fix: none required for 0.1; if wanted later, `app` raises a `NotFound(LodgeError)` from `not_found` (`app/state.py:69`) and the viewer maps it to 404.

### The builder's additions beyond the brief

Security headers, HEAD, 405 with `Allow`, no request logging, `SO_REUSEADDR` off Windows only, `/spec?area=`, the 400 for unknown filters, and the `LodgeError` page as 400: each is sound and tested (`test_response_headers_lock_the_page_down`, `test_only_reads_are_served`, `test_lodge_error_is_a_page_with_its_message`, `test_search_filters_arrive_from_the_query`); `/spec?area=` matches the CLI's area argument and errors through the same `not_found`.
`main._view` probing `_make_lodge()` before `serve` gives the one-sentence exit 2 outside a repository (`test_view_outside_a_repository_is_one_sentence`), and the Task 10 placeholder test is replaced as the carried ruling asked.

## Files read

Read: `.claude/agents/reviewer.md`; the task 11 brief and report; `src/lodge/viewer/{__init__,html,pages,server}.py`; `src/lodge/main.py` diff; `src/lodge/core/render.py`; `src/lodge/core/views.py` (lines 15-190); `src/lodge/app/errors.py` (head), `app/state.py` (`not_found`), `app/reads.py` (`spec`), `app/results.py` (`Read`); `tests/viewer/{world,conftest}.py`, `tests/viewer/test_pages.py`, `tests/viewer/test_server.py` (lines 1-60 and test names); `tests/e2e/test_view.py` diff; `tests/core/builders.py`, `tests/app/support.py`; the spec's Must nots, Levels, Reading, The viewer, and Review flag lines; the plan's Global Constraints, Calls made, and Review Focus.
Not read: `style.css` beyond grepping for `prefers-color-scheme` and external URLs (one dark block, none external); `tests/viewer/test_server.py` bodies past line 60; `vulture_allow.py` and `tests/test_wheel.py` diffs; the review package diff file as a whole (read the sources directly instead).
