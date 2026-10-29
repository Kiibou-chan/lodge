"""The local server: the routes, the host check, and a fresh `Lodge` for each request."""

import sys
from collections.abc import Callable
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from typing import Literal, cast
from urllib.parse import SplitResult, parse_qs, unquote, urlsplit

from lodge.app import Lodge, LodgeError, NotFound
from lodge.core import Filters, Scope
from lodge.viewer import pages

HTML = "text/html; charset=utf-8"
CSS = "text/css; charset=utf-8"
POLICY = "default-src 'none'; style-src 'self'; form-action 'self'; frame-ancestors 'none'"
Query = dict[str, list[str]]


class _Server(ThreadingHTTPServer):
    allow_reuse_address = sys.platform != "win32"
    daemon_threads = False

    def __init__(self, port: int, make_lodge: Callable[[], Lodge]) -> None:
        super().__init__(("127.0.0.1", port), _Handler)
        self.make_lodge = make_lodge


class _Handler(BaseHTTPRequestHandler):
    server: _Server

    def do_GET(self) -> None:
        self._answer()

    def do_HEAD(self) -> None:
        self._answer()

    def do_POST(self) -> None:
        self._send(HTTPStatus.METHOD_NOT_ALLOWED, pages.error_page("this viewer only reads"))

    do_PUT = do_PATCH = do_DELETE = do_OPTIONS = do_POST

    def log_message(self, format: str, *args: object) -> None:
        """Requests are not logged."""

    def _answer(self) -> None:
        port = self.server.server_address[1]
        if self.headers.get("Host", "").lower() not in {f"127.0.0.1:{port}", f"localhost:{port}"}:
            self._send(HTTPStatus.FORBIDDEN, pages.error_page("this address is not served"))
            return
        status, text, kind = _render(self.server.make_lodge, urlsplit(self.path))
        self._send(status, text, kind)

    def _send(self, status: HTTPStatus, text: str, kind: str = HTML) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", POLICY)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        if status is HTTPStatus.METHOD_NOT_ALLOWED:
            self.send_header("Allow", "GET, HEAD")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)


def make_server(make_lodge: Callable[[], Lodge], port: int) -> ThreadingHTTPServer:
    """A server bound to the loopback address; port 0 takes a free one."""
    return _Server(port, make_lodge)


def serve(make_lodge: Callable[[], Lodge], port: int) -> int:
    try:
        httpd = make_server(make_lodge, port)
    except (OSError, OverflowError) as error:
        reason = getattr(error, "strerror", None) or error
        raise LodgeError(
            f"cannot listen on port {port}: {reason}; give another with --port"
        ) from error
    print(
        f"lodge viewer: http://127.0.0.1:{httpd.server_address[1]}/ (Ctrl-C stops it)", flush=True
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


def _render(make_lodge: Callable[[], Lodge], url: SplitResult) -> tuple[HTTPStatus, str, str]:
    path = url.path
    if path == "/style.css":
        css = files("lodge.viewer").joinpath("style.css").read_text(encoding="utf-8")
        return HTTPStatus.OK, css, CSS
    ref = _record_ref(path)
    if path not in {"/", "/spec", "/timeline", "/waiting", "/problems"} and ref is None:
        return HTTPStatus.NOT_FOUND, pages.error_page("there is nothing at this address"), HTML
    try:
        return HTTPStatus.OK, _page(make_lodge(), path, ref, parse_qs(url.query)), HTML
    except NotFound as error:
        return HTTPStatus.NOT_FOUND, pages.error_page(str(error)), HTML
    except LodgeError as error:
        return HTTPStatus.BAD_REQUEST, pages.error_page(str(error)), HTML
    except Exception as error:
        print(f"lodge: viewer: {type(error).__name__}: {error}", file=sys.stderr)
        return HTTPStatus.INTERNAL_SERVER_ERROR, pages.error_page("lodge could not answer"), HTML


def _record_ref(path: str) -> str | None:
    rest = path.removeprefix("/r/")
    if rest == path or not rest or "/" in rest:
        return None
    return unquote(rest)


def _page(lodge: Lodge, path: str, ref: str | None, query: Query) -> str:
    if ref is not None:
        return pages.record_page(lodge.show(ref, reasoning=True, provenance=True))
    match path:
        case "/":
            filters = _filters(query)
            text = _first(query, "q") or ""
            return pages.search_page(lodge.search(text, filters), text, filters)
        case "/spec":
            _, read, areas = lodge.spec(_first(query, "area"))
            return pages.spec_page(areas, read)
        case "/timeline":
            return pages.timeline_page(lodge.timeline())
        case "/waiting":
            return pages.waiting_page(lodge.waiting())
        case _:
            result, read = lodge.problems()
            return pages.problems_page(result, read)


def _first(query: Query, name: str) -> str | None:
    values = query.get(name)
    return values[0].strip() or None if values else None


def _filters(query: Query) -> Filters:
    kind, scope = _first(query, "kind"), _first(query, "scope")
    status = _first(query, "status") or "current"
    if kind is not None and kind not in pages.KINDS:
        raise LodgeError(f"unknown kind {kind}; use decision or spec")
    if status not in pages.STATUSES:
        raise LodgeError(f"unknown status {status}; use current, replaced, retired, or any")
    try:
        chosen = None if scope is None else Scope(scope)
    except ValueError:
        raise LodgeError(f"unknown scope {scope}; use product or process") from None
    return Filters(
        cast(Literal["decision", "spec"] | None, kind),
        chosen,
        cast(Literal["current", "replaced", "retired", "any"], status),
        _first(query, "area"),
        _first(query, "decided_by"),
    )
