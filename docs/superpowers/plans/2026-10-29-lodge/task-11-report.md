# Task 11 report: the viewer

Branch `build-0.1`, from 018c17b.
`sh scripts/check.sh` green: ruff format, ruff, mypy strict, vulture, 948 passed (the wheel test included).

## Built

- `src/lodge/viewer/html.py`: `e`, `link`, `linked` (escapes, then turns each record ID into a link), `paragraphs`, the level-1 body (meta line with status, flags, statement, then the author's quote), and `page`, the frame with navigation, freshness line, and the banner above `<main>`.
- `src/lodge/viewer/pages.py`: `search_page`, `record_page`, `spec_page`, `timeline_page`, `waiting_page`, `problems_page`, plus `error_page` for 400, 403, 404, 405, and 500.
- `src/lodge/viewer/server.py`: `make_server`, `serve`, the routes, the host check, security headers.
- `src/lodge/viewer/style.css`: package data, light and dark through `prefers-color-scheme`.
- `src/lodge/main.py`: `view` now probes `_make_lodge()` (so outside a repository it is one sentence, exit 2) and then calls `serve`.
- `vulture_allow.py`: the `http.server` names it dispatches by name.
- `tests/viewer/` (`__init__.py`, `conftest.py`, `world.py`, `test_pages.py`, `test_server.py`): 31 tests; `tests/e2e/test_view.py`: `test_view_is_not_built_yet` replaced by `test_view_serves_the_project_until_interrupted` and `test_view_outside_a_repository_is_one_sentence`; `tests/test_wheel.py`: asserts `lodge/viewer/style.css` is in the wheel.

## Test-first

The viewer tests were first run before any viewer code existed and failed at collection: `ImportError: cannot import name 'server' from 'lodge.viewer'`.
The e2e placeholder test pinned the old `lodge: the viewer is not built yet` and exit 2; it was replaced rather than run against the new code.
Three assertions of my own were wrong on the first green run and were corrected in the tests, not the code: the broken file's message text, and a filter test that looked for an ID which the flag links.

## Carried rulings

- Banner names each unreadable file (path, and `:line` when known, then the message) above `<main>`, with the count linking to `/problems`: `test_broken_file_named_above_page_content` for all six pages, `test_unreadable_file_banner_reaches_the_browser` over HTTP.
- Level 1 carries the quote, outside `<details>`: `test_record_page_shows_the_quote_outside_the_details`.
- `spec_page` keeps the flags in the entry headings, each ID in them a link.
- Attachments are listed as `lodge/attachments/<decision id>/<name>`; nothing serves them.

## Choices and concerns

1. A `LodgeError` is a 400 page with its message (also "no record named x", which could be a 404; `Lodge` gives no way to tell the two apart); any other exception is a plain 500 page whose cause goes to stderr, not to the page.
2. Search filters come from the query string (`q`, `kind`, `scope`, `status`, `area`, `decided_by`); an unknown kind, scope, or status is a 400 page, not silently ignored. `/spec?area=<name>` is also accepted (not in the brief).
3. `spec_page` parses the markdown line by line: a statement paragraph that starts with `# ` or `## ` would render as a heading. The renderer gives no way to tell them apart.
4. Beyond the brief: security headers (`Content-Security-Policy: default-src 'none'; style-src 'self'; form-action 'self'; frame-ancestors 'none'`, `X-Content-Type-Options`, `Referrer-Policy`, `Cache-Control: no-store`), HEAD, 405 with `Allow` for other methods, no request logging, and `SO_REUSEADDR` only off Windows (on Windows it would let a second server share the port).
5. `lodge view` prints one line to stdout, the address, and stops on Ctrl-C with exit 0; a port that cannot be bound is `cannot listen on port N: <reason>`, exit 2.
6. Freshness line shows only when the store gives one (branch mode); the scratch clone below is checkout mode, so it was not seen there, only in the tests (`test_every_page_shows_freshness_and_problem_banner`).

## Step 4: looked at

Scratch clone in checkout mode: an author decision with a quote and two entries, an agent edit awaiting her, a replaced and a replacing process decision, and a hand-made broken decision file; `lodge view --port 8791`.
Looked at in the browser pane (dark first, then light via colour-scheme emulation, 800 px wide): search (empty and with `q=review&scope=process&status=any`, filter fields kept, a replaced record with its flag link), a decision record (quote visible, reasoning and provenance collapsed), an entry record (both details opened: reasoning lists the two deciding decisions, provenance lists `changed by` links with status), specification (flag with linked ID in the heading), waiting, timeline (newest first), and problems.
The banner with the broken file sat above the content on every page.
`curl` with a foreign `Host` gave 403, an unknown path 404.
Not looked at: a phone width, and the page with a freshness line.

## Fix round 1

- I1: `core.spec_view` returns `SpecArea(name, title, intro, entries: Level1...)`; `render_spec` formats it and backslash-escapes every intro or statement line starting with `#`; `Lodge.spec` returns `(text, read, areas)`; `spec_page(areas, read)` builds headings from the fields and renders intros and statements as paragraphs only. Tests: `test_spec_view_gives_areas_with_level_one_entries_in_order`, `test_render_spec_escapes_lines_that_start_with_a_hash`, `test_spec_page_builds_headings_from_fields_never_from_text` (one `<h1>`, one `<h2>`, fake heading inside `<p>`), `test_spec_escapes_hash_lines_inside_a_statement` (`lodge spec`). Spec headings no longer link IDs inside flags (no status known there).
- M1: `linked` links an ID only when its status is known and writes the status beside it; the record page's map is the record and its provenance links; other IDs in reasoning and flags, and all IDs in flags on list and spec pages, are escaped text. Test: `test_record_page_links_only_ids_whose_status_is_known`; the flag test now expects the status span.
- M2: `pages.KINDS` and `pages.STATUSES` are the one definition, `server` uses them; scopes come from `Scope`.
- M3: `with_body` dropped from `_answer` and `_send`; HEAD is decided by `self.command`.
- M4: `NotFound(LodgeError)` raised by `not_found` (unknown record or area; an ambiguous code stays a `LodgeError`); the viewer answers 404, the CLI still exits 2. Tests: `test_lodge_error_is_a_page_with_its_message` (404, plus `/spec?area=nowhere`), `test_show_unknown_ref_is_an_error` and the other not-found tests expect `NotFound`.
- `sh scripts/check.sh` green, 953 passed.
