### Task 11: The viewer

**Files:**
- Create: `src/lodge/viewer/server.py`, `src/lodge/viewer/pages.py`, `src/lodge/viewer/html.py`, `src/lodge/viewer/style.css` (package data)
- Modify: `src/lodge/main.py` (pass `view`)
- Test: `tests/viewer/test_pages.py`, `tests/viewer/test_server.py`

**Interfaces:**
- Consumes: `lodge.app` (`Lodge`, `Shown`, `Listed`, `Read`), `lodge.core` view types.
- Produces: `pages.search_page(listed: Listed, query: str, filters: Filters) -> str`, `pages.record_page(shown: Shown) -> str` (level 1 visible, reasoning and provenance in `<details>`, every linked ID a link to `/r/<id>` with its status beside it), `pages.spec_page(markdown: str, read: Read) -> str` (headings and paragraphs only), `pages.timeline_page(listed: Listed) -> str`, `pages.waiting_page(listed: Listed) -> str`, `pages.problems_page(result: CheckResult, read: Read) -> str`; `server.make_server(make_lodge: Callable[[], Lodge], port: int) -> ThreadingHTTPServer` and `server.serve(make_lodge, port) -> int`.
- Routes `/`, `/r/<ref>`, `/spec`, `/timeline`, `/waiting`, `/problems`, `/style.css`; a fresh `Lodge` per request; every page shows the freshness line and, when any, a banner counting unrecorded problems linking to `/problems`; 404 for anything else; a `LodgeError` shown as a page with its message; a request whose `Host` is not `127.0.0.1:<port>` or `localhost:<port>` gets 403; bound to `127.0.0.1`; light and dark through `prefers-color-scheme`; all text escaped with `html.escape`.

- [ ] **Step 1: Write failing tests:** `test_record_page_escapes_html` (a statement `<script>alert(1)</script>` appears escaped), `test_record_page_flags_and_both_link_directions`, `test_search_page_keeps_filters`, `test_every_page_shows_freshness_and_problem_banner`, `test_waiting_page`, `test_problems_page`, `test_server_routes` (`make_server(…, 0)`, port from `server.server_address[1]`, a thread, GET each route for 200, `/nope` for 404, a foreign `Host` for 403, then `shutdown()`).
- [ ] **Step 2: Run**; expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check.sh`; then run `uv run lodge view` over a scratch clone with records and look at each page in a browser, light and dark; list what was looked at in the task report.
- [ ] **Step 5: Commit and push.**


## Carried from earlier tasks (ledger rulings, binding)

- The unrecorded-problems banner names each file lodge cannot read (path and message), above the page's content, not only a count (Task 6 I4: a broken agent-decision file leaves her quote under the agent's text, so the warning must come first). Test: `test_broken_file_named_above_record_page`.
- Level 1 carries `quote`, printed after the statement (Task 6 B1); the record page shows it at level 1, not inside `<details>`.
- `render_spec(s, d, failing, area=None)` puts flags in entry headings (Task 6 I1); `spec_page` keeps them visible.
- The record page lists attachment names with their path `lodge/attachments/<decision id>/<name>`; no route serves them in 0.1.
- `tests/e2e/test_view.py::test_view_is_not_built_yet` pins Task 10's placeholder: replace it with a test that `lodge view --port 0`'s callable starts the server.
- Step 4: if a browser tool is available, look at each page light and dark; otherwise fetch every route with `urllib` against a scratch clone with records, check the HTML, and say in the report that no browser was used.
