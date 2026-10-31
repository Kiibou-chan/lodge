# Task 6b review: the viewer's write gate

Reviewed: commit 73af006 against 978fdfd (`git diff 978fdfd 73af006 -- src tests`), in two detached scratch worktrees of 73af006 outside the branch's working tree, removed afterwards.
Order: security first, then correctness against `task-6b-brief.md`, then practice and design.
Requirements read: `task-6b-brief.md`, `task-6b-report.md`, the Must nots, Confirming, Doubts and questions, and Security sections of `docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md`, and d-7w5aq0 and d-a3h9f3 (`uv run --frozen --quiet lodge show ID --reasoning`).

Counts: 0 Blocking, 2 Important, 8 Minor.

## Verification run

- `uv run --frozen --quiet pytest tests/viewer tests/e2e/test_view.py tests/test_structure.py -q`, sockets allowed: `120 passed`, so the socket tests the builder could not run pass.
- Every new module and test file is under 300 lines (`writes.py` 186, `server.py` 202, `test_post_gate.py` 121, `test_post_routes.py` 155, `test_server.py` 244); `cli/parser.py` went from 227 to 231 lines, inside the brief's 8.
- Live probes: a script started `make_server(staged_world()[0], 0, token="a" * 32)` and sent raw requests over a socket, counting `store.publishes` after each.
- Mutation run: 27 one-line mutations of `writes.py` and `server.py`, each followed by `pytest tests/viewer tests/e2e/test_view.py -q`; the table is under Mutation results.

### Requests the tests do not send, and what the viewer answered

Every refusal below wrote nothing (`publishes=0`).

| Request | Answer |
| --- | --- |
| `Host: 127.0.0.1.:PORT` (trailing dot) | 403 |
| `Host: localhost.:PORT`, `Origin: http://localhost.:PORT` | 403 |
| `Host: LOCALHOST:PORT` | 303, written (correct: hosts are case-insensitive) |
| `Origin: HTTP://LOCALHOST:PORT` | 303, written (correct) |
| `Origin: null` | 403 |
| `Origin` with a trailing slash, a path, userinfo, or surrounding spaces | 403 |
| no `Host` header | 403 |
| token only in the query string (`POST /confirm?token=…`) | 403: the body alone is read |
| `Content-Type: application/x-www-form-urlencoded; charset=utf-8`, or mixed case | 303, written (correct) |
| `multipart/form-data`, `text/plain` | 415 |
| `Content-Length: +5`, Arabic-Indic digits | 400 |
| `Content-Length` of 30 nines, of 65537 | 413, body unread |
| `Transfer-Encoding: chunked`, no length | 411 |
| `/threads/..%2f..%2fx/reply`, `/threads/Q-111111/reply` | 400 |
| `about=../../etc` | 404, nothing written |
| `area=../../x` | 404, nothing written |
| `words` holding NUL, or an encoded lone surrogate | 400 |
| a request line, then silence | connection closed after 10.0 s |
| headers and part of the body, then silence | connection closed after 10.0 s, nothing written |
| two `Host` headers, foreign first, allowed second | **303, written** (Minor m1) |
| two `Origin` headers, foreign first, allowed second | **303, written** (Minor m1) |
| a body shorter than its `Content-Length`, then the client's half-close | **303, the truncated words written** (Important I1) |

No form field reaches a file path: `about` and `area` are looked up in the snapshot (`app/state.py:81`, `app/confirm.py:13`), thread paths come from the minted or found thread ID (`app/threads.py:78`), and decision file names are the ID plus a slug of `[a-z0-9]` words (`core/fileformat.py:84`).
`test_viewer_writes_only_new_decisions_and_thread_files` holds for all four routes.

### Mutation results

Killed (a test fails when the rule is removed): the `Host` check in `refuse_early`; all `Origin` checks; any scheme accepted; the token check; two tokens allowed; `==` for `compare_digest`; the content type; the body limit in `handle_post`; `max_num_fields`; the `d-` check (both `is_id` and the prefix); the write lock; the 411; the digits check; `refuse_early` in `do_POST`; the `Location` header; the timeout (by a test of the constant only, see m4); `commit=True` on confirm; the `CHECK_FAILED` refusal.

Survived:

- The `q-` check at `writes.py:165` removed (Important I2).
- `do_POST`'s over-limit `Content-Length` refusal at `server.py:55` removed (Important I2).
- `Origin` matched as a prefix of an allowed origin instead of exactly (Minor m8).
- The empty-`Origin` branch at `writes.py:62` removed: equivalent, the next branch also answers 403; only the reason text is untested (Minor m8).
- `where` changed on reply and close (Minor m8).
- `quote` dropped from the area redirect (Minor m8).
- `.lower()` dropped from the `Host` check in `refuse_early`: refuses more, harmless.

## Important

### I1. A body shorter than its `Content-Length` writes truncated words as hers

Handle: `src/lodge/viewer/server.py:63`, `self.rfile.read(int(length))`, whose result goes to `handle_post` unchecked.
`rfile.read(n)` returns fewer than `n` bytes when the client closes its side early, and `parse_qs` decodes the prefix as a whole form.
Failing request, run against the live server: `Content-Length` of the full form `token=…&id=d-cccccc&words=I%20read%20it%20and%20do%20not%20agree`, only the bytes up to `words=I%20read%20it` sent, then `shutdown(SHUT_WR)`.
Answer: `303 See Other`, and `lodge/decisions/d-111111-confirms-d-cccccc.md` holds `quote: {text: "I read it", where: "lodge viewer", …}`.
That records words she did not type as hers, against the interaction design's must-not 2 ("never records words she did not type") and the first design's must-not 1 (wrong information).
A browser on loopback rarely drops mid-body, but a tab closed, a crash, or a proxy given with `--allow-host` passing a cut request through all produce exactly this, and the record cannot then be corrected but by another decision.
Fix: in `do_POST`, `body = self.rfile.read(n)` and, when `len(body) != n`, answer 400 "the form arrived incomplete; nothing was written" without calling `handle_post`.
Test (socket, `test_server.py`): send a declared length longer than the body, half-close, assert 400 and `not store.publishes`.

### I2. Two of the brief's refusals have no test that fails when they go

Handles: `src/lodge/viewer/writes.py:165` (a `<q>` that is not a `q-` ID is 400) and `src/lodge/viewer/server.py:55` (a `Content-Length` over `MAX_BODY` is 413 with the body unread); both mutations survive the whole viewer suite.
The second one matters most: `handle_post`'s own 413 at `writes.py:102` runs only after `rfile.read`, so without `server.py:55` any local process that sends an allowed `Host` and `Origin` (no token needed, `refuse_early` precedes the token) makes the server buffer up to 9,999,999,999 bytes per connection.
The first is defence in depth, since `_find` looks the ID up in the snapshot (`app/threads.py:16`), but it is a brief rule and the build was not test-first.
Fix: a gate test posting to `/threads/s-aaaaaa/reply` and `/threads/q-11111/reply` expecting 400 and nothing written; a socket test with `Content-Length: 65537` and no body, expecting 413 within the timeout, which fails when the guard goes because the read then waits 10 s and the connection drops.

## Minor

### m1. Repeated `Host` and `Origin` headers: the last wins on `POST`, the first on `GET`

Handles: `src/lodge/viewer/server.py:47` builds `{k.lower(): v for k, v in self.headers.items()}`, so the last copy wins; `server.py:78` uses `self.headers.get("Host")`, the first.
Failing request: `Host: evil.example` then `Host: 127.0.0.1:PORT`, and likewise two `Origin` headers, foreign first: 303, written.
No browser sends either twice, so this opens nothing a non-browser client could not do with one correct header, and the token still applies; but RFC 9112 section 3.2 requires a 400 for more than one `Host`, and the two code paths disagree on which copy is the request's host.
Fix: in `do_POST` and `_answer`, answer 400 when `len(self.headers.get_all(name) or ()) > 1` for `Host`, `Origin`, `Content-Length`, or `Content-Type`.

### m2. Write refusals are bare fragments, not pages

Handles: `src/lodge/viewer/writes.py:178-183` returns `<p>…</p><a href="…">Back to the form</a>` with no document, stylesheet, or navigation; the 403, 404, 413, and 415 replies (`writes.py:60-114`, `server.py:52-56`) are bare sentences sent as `text/html`.
`GET` errors go through `pages.error_page` (`pages.py:78`), so a refused write looks unlike every other page the viewer serves, and Task 7's forms will land her on these.
Fix: `Reply` carries the plain reason and an optional `back`; `do_POST` renders every non-303 reply with `pages.error_page` plus the back link, so escaping stays in one place.

### m3. A new thread's redirect uses the raw `about` field

Handle: `src/lodge/viewer/writes.py:148` and `:173`.
Failing request: `POST /threads` with `about=S-AAAAAA` redirects to `/r/S-AAAAAA?done=committed#q-…`; it renders, but the canonical address is `/r/s-aaaaaa`, and a reference other than an ID would land on that reference too.
Fix: build the location from `written.about` (Task 4's `Written.about`, `app/results.py:63`), keeping the raw field only for the back link before the write.

### m4. `test_handler_dispatch_and_timeout` only feeds vulture

Handle: `tests/viewer/test_post_gate.py:119-121` asserts `callable(_Handler.do_POST)` and `_Handler.timeout == 10`; the report says it was added after vulture flagged both.
The repository's idiom for names `http.server` reads is `vulture_allow.py:17-27`, where `do_GET`, `do_PUT`, and the rest sit.
Fix: add `_Handler.do_POST` and `_Handler.timeout` to `vulture_allow.py` and delete the test; the timeout's behaviour is better pinned by I2's socket test.

### m5. `handle_post` is one 100-line function with a nested helper and a printing mapper

Handles: `src/lodge/viewer/writes.py:87-186`; the helper `one` is defined inside `try` after a blank line (`:116-122`); the route is chosen by `path.split("/")` inline (`:157-163`); `done_code` (`:69-84`) prints the commit detail to stderr while computing a code.
Fix: `_confirm(lodge, fields) -> tuple[str, Written]`, `_ask(…)`, and `_on_thread(lodge, path, fields)` each returning the back link and the result; `one` at module level; the stderr line moved to `handle_post`, so `done_code` stays a mapping.

### m6. `--allow-host` has no help or metavar

Handle: `src/lodge/cli/parser.py:143`; `uv run lodge view --help` prints `--allow-host ALLOW_HOST` with no description, beside `--port PORT  default 8787`.
Fix: `metavar="HOST"`, `help="also answer this Host header, name:port; repeatable"`, within the brief's 8-line budget (6 used).

### m7. Stale names and docstrings after the gate

Handles: `tests/viewer/test_server.py:118`, `test_only_reads_are_served`, now asserts a `POST` refusal and the 405s; `src/lodge/viewer/server.py:1`, "the routes, the host check, and a fresh `Lodge` for each request", omits the write path.
Fix: rename the test `test_post_without_origin_and_other_methods_refused`; the docstring "The local server: the routes, the host and write gate, and a fresh `Lodge` for each request."

### m8. Security tests that pass with the wrong rule

Handles and surviving mutations:
- `tests/viewer/test_post_gate.py:36-45`: `Origin` matched with `startswith` passes; add `http://127.0.0.1:8787.evil.example` and `http://127.0.0.1:87870`, both 403.
- `test_post_gate.py:28-29`: only the status is asserted, so the brief's reason "a write needs an Origin header" is unpinned; assert the text, and send no `origin` key at all rather than an empty one.
- `tests/viewer/test_post_routes.py:206-212`: changing `where` on reply and close passes; assert `by`, `where`, and `when` on the reply and the closing message, as `test_ask_from_viewer_records_her_words` does for `ask`.
- `test_post_routes.py:163-168`: dropping `quote` from the area redirect passes, since `storage` needs no quoting; use an area whose name holds a space or `&`, or assert on a unit test of the location builder.

## Correctness against the brief

Matches, each checked in the code and by a test or probe: the `Produces` signatures; `refuse_early`'s three refusals and their order in `handle_post`; 415, 413, 400 for UTF-8, escapes, and field count; one token under `hmac.compare_digest` on UTF-8 bytes; `d-` and `q-` shapes; `author`, `lodge viewer`, `commit=True`; one module-level lock from the first read to the last write, `make_lodge` before it; the 303 locations with `quote(part, safe="")`, `done=stale` on `StaleList`, the thread anchor; 400 with a back link on a failed check, refused input, or empty words; 404 on `NotFound`; 500 with the error on stderr; `NOTICES` verbatim; `render` with an unknown code showing nothing; `do_POST`'s 411, 400, and 413 before reading; `timeout = 10`; 405 with `Allow: GET, HEAD, POST` and "this address takes no such request"; `--allow-host` validation with exit 2; the `view` help text; `secrets.token_urlsafe(32)` in `main.py`.
The report's deviation, `pages.py` threading the notice, is needed because the page builders own the calls to `page`; it is in the commit and adds no logic.
The report's test-first gap is real: eight route tests and the socket tests were written after the code; the mutation run above stands in for the missing first failures, and I2 and m8 list what it found.

## Files

Read: `CLAUDE.md`; `task-6b-brief.md`; `task-6b-report.md`; the interaction design, lines 1 to 160; the first design's Must nots and viewer lines (`docs/superpowers/specs/2026-10-29-lodge-design.md:53-66`, grep for "viewer"); d-7w5aq0 and d-a3h9f3; at 73af006, `src/lodge/viewer/writes.py`, `server.py`, and the diffs of `html.py`, `pages.py`, `__init__.py`, `cli/commands.py`, `cli/parser.py`, `main.py`; `src/lodge/app/confirm.py`, `app/threads.py`, `app/lodge.py:55-130`, `app/state.py:59-95`, `app/results.py:58-64`, `core/ids.py`, `core/fileformat.py:84-90`, `gitstore/checkout.py:15-70`, `gitstore/branch.py:15-50`, `gitstore/setup.py:27-38`; `tests/viewer/test_post_gate.py`, `test_post_routes.py`, `test_server.py` (diff and lines 1-60), `world.py` diff, `tests/e2e/test_view.py` diff, `tests/app/fakes.py:55-80`; `vulture_allow.py`; `README.md:95-106`; plan lines 401, 447, and 569-576.
Not read: the rest of the plan; `core/confirmation_draft` and `app/writes.add` beyond their call sites; `gitstore` commit code; `tests/structure_rules.py` (its tests pass); the rest of the first design.
README.md:101 still says the viewer is read-only; the plan's README task (plan line 571) owns that, so it is not a finding here.
