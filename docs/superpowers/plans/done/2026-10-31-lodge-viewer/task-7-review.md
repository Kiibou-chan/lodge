# Task 7 review: the viewer's pages

Commit 871dae4, diff `git diff 3d1bff2 871dae4 -- src tests`, reviewed in a detached scratch worktree of that commit (removed).
Result: 0 Blocking, 2 Important, 6 Minor.

Read: the brief, the report, `CLAUDE.md`, the design (all), d-7w5aq0 and d-a3h9f3, the Task 6b brief table, and in full at 871dae4: `viewer/forms.py`, `viewer/spec.py`, `viewer/pages.py`, `viewer/server.py`, `viewer/writes.py`, `viewer/html.py`, `viewer/style.css`, `core/order.py`, `core/render.py` (`Placed`), `app/reads.py`, `tests/viewer/test_forms.py`, `tests/viewer/test_pages_threads.py`, the test_order additions, and the test_pages and test_post_routes diffs.
Not read: `tests/viewer/test_server.py` and the e2e view tests (socket-bound, not changed by this commit), `core/threads.py` beyond the parse guard, Task 3's `derived_order` internals (taken as reviewed).
Ran in the scratch worktree: the viewer and order tests (89 passed), the whole non-socket suite (1327 passed), ruff format, ruff check, mypy (clean), vulture (one finding, below).
Rendered a decision page, an entry page with two threads, an area page, and `/waiting` from the `staged_world()` fixture and read the HTML.
Probes and mutations (listed per finding) ran against the scratch copy only.

## Correctness pass

Every brief item holds on the rendered HTML.
The confirm form has `action="/confirm"`, the hidden token and `id`, the required `words` text area labelled "Your words", the hint text verbatim, and the "Confirm" button; it is absent on author-confirmed and replaced decisions.
The area page lists each decision as a link with the entries it changes and their areas, then one form with hidden `area` and one hidden `id` per decision.
Threads sit newest last with "Doubt q-…" or "Question q-…", state, and each message's `by`, `when`, `where`; a closed thread's last message is headed "Closed by author" with no paragraph; open threads carry Reply and Close forms; both new-thread forms carry `about` and `kind`.
The dependency view puts each dependant directly after its parent, the depth-over-5 cap and the "also rests on" line with `under` render correctly (probed on a nine-entry chain: classes 0 to 5, then 5 5 5 5, with the line on entries 6 to 8 only), and cross-area lines render.
Waiting shows both groups in order.
Every value I traced from a record goes through `e()` (`forms.py` 46-67, `spec.py`, `pages.py` 63-88, `hidden`, `_form`); no raw interpolation found.
Every form is built by `_form`, so every form carries the token.

### Important

**I1 · `rests_on_tree` expands a shared dependency once per path, so the entry page can grow exponentially**
`src/lodge/core/order.py:80-93` (rendered by `src/lodge/viewer/pages.py:83-88`).
It guards only against ancestors, so an entry reached by two routes is expanded in full each time; check 8 allows any acyclic graph, so such graphs are valid data.
Scenario, run: 26 entries, each resting on the two before it, then `GET /r/<last>` returns a page of 18 MB in about 1 s; 22 entries give 2.6 MB, 16 give 148 KB.
A project whose entries commonly rest on two or three neighbours reaches this inside the 82-entry specification, and a page that large hangs the browser.
Fix: expand each id once per tree (a repeat appears as a leaf `Branch` with empty `children`, and `_branches` renders it with a "see above" marker, or without marker as the same link), and add `test_rests_on_tree_expands_a_shared_dependency_once` (diamond A, B and C on A, D on B and C: A appears once with children).

**I2 · The commit does not pass `uv run vulture`; the allow-list line the report names is not in it**
`tests/viewer/test_forms.py:20` (`Forms.handle_starttag`); `vulture_allow.py` is not in `git show --stat 871dae4`.
At 871dae4, `uv run vulture` prints `tests/viewer/test_forms.py:20: unused method 'handle_starttag' (60% confidence)` and exits 3, so `sh scripts/check.sh` fails on the commit as it stands.
The report says it added `HTMLParser.handle_starttag` to `vulture_allow.py`; that edit sits in the working tree, uncommitted, beside the Task 6b fix round's lines in the same file.
Fix: the commit that carries the 6b fix round must stage `vulture_allow.py` with the `HTMLParser.handle_starttag  # noqa: B018` line, or the Task 7 fix round commits it on its own; check by running `uv run vulture` on a clean checkout of the resulting commit.

## Practice pass

### Minor

**M1 · Tests do not pin three behaviours the brief fixes**
`tests/viewer/test_pages_threads.py:46-49, 82-87`; `tests/viewer/test_forms.py:67-69`.
Mutations that all left the three page test files green (44 passed):
- `min(p.depth, 5)` replaced by `p.depth` (`spec.py:59`): no test has an entry deeper than 5, so a `depth-6` class with no CSS would ship.
- the `under` link at depth over 5 dropped (`spec.py:55`): same cause.
- the area removed from the "By dependency" link (`spec.py:22`): line 87 of the test is satisfied by the area heading's own link, `/spec?area=storage`.
- `by`, `where`, the waiting-page title, and the area title left unescaped (`forms.py:61-65`, `pages.py:68`, `spec.py:36`): `test_thread_text_is_escaped` only covers the message text; the brief's "every value from a record escaped" is untested for these.
Fix: add a nine-entry chain test (classes `depth-5` for entries 5 to 8, "also rests on" only from entry 6), assert the exact dependency link `<a href="/spec?area=storage">By dependency</a>` with the heading link excluded, and one parametrised escape test with `<b>` in the role name, `where`, an entry title, and an area title.

**M2 · `Lodge.waiting` and `reads.waiting` are dead in `src`**
`src/lodge/app/lodge.py:33`, `src/lodge/app/reads.py:56`.
The server and the CLI both call `waiting_all` now; only tests (`tests/viewer/test_pages.py:130,183,209`, `tests/app/test_reads.py`) keep the older read, so vulture cannot see it.
Fix: move those tests to `waiting_all()[0]` and delete the two functions, or say in the progress ledger why the old read stays.

**M3 · The doubt-or-question head is written twice, and compared with a string**
`src/lodge/viewer/forms.py:52` and `src/lodge/viewer/pages.py:67`: `'Doubt' if t.raises == 'doubt' else 'Question'`.
Fix: one `thread_head(thread)` in `forms.py`, comparing against `Raises.DOUBT`; `waiting_page` imports it.
Related: `forms.hidden` (`forms.py:12`) is used only inside `forms.py`, so make it `_hidden`; `forms.threads_body` sorts with `newest_last` (`forms.py:50`) though `reads.show` already did (`app/reads.py:48`), so drop one.

**M4 · The page-level re-export is an indirection**
`src/lodge/viewer/pages.py:7` imports `spec_page as spec_page` only so `server.py` and tests can write `pages.spec_page`.
Fix: `server.py` and the tests import `lodge.viewer.spec` directly, or `pages.py` lists it in an `__all__`; the brief's `spec_page` lives in `spec.py`, so the former matches it.

**M5 · Literal `·` against `&middot;`**
`src/lodge/viewer/spec.py:25`, `src/lodge/viewer/pages.py:69-70` write the character; `html.py` writes `&middot;` throughout.
Fix: use `&middot;`, as every other page does.

## Design pass

### Minor

**M6 · Empty "Rests on" and "Rests on it" headings with an empty list under them**
`src/lodge/viewer/pages.py:41-49, 83-88` (rendered, entry `s-aaaaaa`: `<h2>Rests on</h2><ul></ul><h2>Rests on it</h2><ul></ul>`).
Until the migration adds `rests_on`, all 82 entries show two headings over nothing, which reads as a broken page.
Fix: render the empty case as `<p>Nothing.</p>` (or leave the heading out); `_branches` returns `""` for no branches and a test asserts it.

Observations that are not findings:
the page-level `.notice` and the confirm hint share one class, so the hint is yellow like a status message; harmless, but a separate `.hint` rule would let the two differ later.
The area page makes two reads (`lodge.spec` then `lodge.behind_area`, `server.py:174-178`), so freshness and the list can differ by one write; the form's carried IDs make that safe, as design line 52 intends.
The current ordering is not marked on the "By dependency" and "As written" links.
