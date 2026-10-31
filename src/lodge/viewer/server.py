"""The local server: the routes, the host and write gate, and a fresh `Lodge` for each request."""

import re
import sys
from collections.abc import Callable, Sequence
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from typing import Literal, cast
from urllib.parse import SplitResult, parse_qs, unquote, urlsplit

from lodge.app import Lodge, LodgeError, NotFound
from lodge.core import Filters, Scope
from lodge.viewer import pages, writes

HTML = "text/html; charset=utf-8"
CSS = "text/css; charset=utf-8"
POLICY = "default-src 'none'; style-src 'self'; form-action 'self'; frame-ancestors 'none'"
Query = dict[str, list[str]]


class _Server(ThreadingHTTPServer):
    allow_reuse_address = sys.platform != "win32"
    daemon_threads = False

    def __init__(
        self, port: int, make_lodge: Callable[[], Lodge], token: str, allow_hosts: Sequence[str]
    ) -> None:
        super().__init__(("127.0.0.1", port), _Handler)
        self.make_lodge = make_lodge
        self.gate = writes.Gatekeeper(
            token, writes.allowed_hosts(self.server_address[1], allow_hosts)
        )


class _Handler(BaseHTTPRequestHandler):
    server: _Server
    timeout = 10

    def do_GET(self) -> None:
        self._answer()

    def do_HEAD(self) -> None:
        self._answer()

    def do_POST(self) -> None:
        if self._repeated_headers():
            return
        headers = {k.lower(): v for k, v in self.headers.items()}
        reply = writes.refuse_early(self.server.gate, headers)
        if reply is None:
            length = headers.get("content-length")
            if length is None:
                reply = writes.Reply(HTTPStatus.LENGTH_REQUIRED, "a write needs Content-Length")
            elif re.fullmatch(r"[0-9]+", length) is None:
                reply = writes.Reply(HTTPStatus.BAD_REQUEST, "Content-Length needs digits")
            elif len(length) > 10 or int(length) > writes.MAX_BODY:
                reply = writes.Reply(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "the form is too large")
            else:
                body = self.rfile.read(int(length))
                if len(body) != int(length):
                    reply = writes.Reply(
                        HTTPStatus.BAD_REQUEST, "the form arrived incomplete; nothing was written"
                    )
                else:
                    reply = writes.handle_post(
                        self.server.make_lodge,
                        self.server.gate,
                        urlsplit(self.path).path,
                        headers,
                        body,
                    )
        text = (
            reply.text
            if reply.status == HTTPStatus.SEE_OTHER
            else pages.error_page(reply.text, reply.back)
        )
        self._send(reply.status, text, location=reply.location)

    def do_PUT(self) -> None:
        self._send(
            HTTPStatus.METHOD_NOT_ALLOWED, pages.error_page("this address takes no such request")
        )

    do_PATCH = do_DELETE = do_OPTIONS = do_PUT

    def log_message(self, format: str, *args: object) -> None:
        """Requests are not logged."""

    def _repeated_headers(self) -> bool:
        for name in ("Host", "Origin", "Content-Length", "Content-Type"):
            if len(self.headers.get_all(name) or ()) > 1:
                self._send(HTTPStatus.BAD_REQUEST, pages.error_page(f"repeated {name} header"))
                return True
        return False

    def _answer(self) -> None:
        if self._repeated_headers():
            return
        if self.headers.get("Host", "").lower() not in self.server.gate.hosts:
            self._send(HTTPStatus.FORBIDDEN, pages.error_page("this address is not served"))
            return
        status, text, kind = render(
            self.server.make_lodge, urlsplit(self.path), self.server.gate.token
        )
        self._send(status, text, kind)

    def _send(
        self, status: HTTPStatus, text: str, kind: str = HTML, location: str | None = None
    ) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", POLICY)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        if status is HTTPStatus.METHOD_NOT_ALLOWED:
            self.send_header("Allow", "GET, HEAD, POST")
        if location is not None:
            self.send_header("Location", location)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)


def make_server(
    make_lodge: Callable[[], Lodge], port: int, *, token: str, allow_hosts: Sequence[str] = ()
) -> ThreadingHTTPServer:
    """A server bound to the loopback address; port 0 takes a free one."""
    return _Server(port, make_lodge, token, allow_hosts)


def serve(
    make_lodge: Callable[[], Lodge], port: int, allow_hosts: Sequence[str], token: str
) -> int:
    try:
        httpd = make_server(make_lodge, port, token=token, allow_hosts=allow_hosts)
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


def render(
    make_lodge: Callable[[], Lodge], url: SplitResult, token: str
) -> tuple[HTTPStatus, str, str]:
    path = url.path
    if path == "/style.css":
        css = files("lodge.viewer").joinpath("style.css").read_text(encoding="utf-8")
        return HTTPStatus.OK, css, CSS
    ref = _record_ref(path)
    if path not in {"/", "/spec", "/timeline", "/waiting", "/problems"} and ref is None:
        return HTTPStatus.NOT_FOUND, pages.error_page("there is nothing at this address"), HTML
    try:
        return HTTPStatus.OK, _page(make_lodge(), path, ref, parse_qs(url.query), token), HTML
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


def _page(lodge: Lodge, path: str, ref: str | None, query: Query, token: str) -> str:
    notice = writes.NOTICES.get(_first(query, "done") or "")
    if ref is not None:
        return pages.record_page(lodge.show(ref, reasoning=True, provenance=True), token, notice)
    match path:
        case "/":
            filters = _filters(query)
            text = _first(query, "q") or ""
            return pages.search_page(lodge.search(text, filters), text, filters, notice)
        case "/spec":
            area = _first(query, "area")
            _, read, areas = lodge.spec(area)
            order: Literal["dependency", "written"] = (
                "written" if _first(query, "order") == "written" else "dependency"
            )
            behind = lodge.behind_area(area) if area is not None else ()
            return pages.spec_page(areas, read, token, order, area, behind, notice)
        case "/timeline":
            return pages.timeline_page(lodge.timeline(), notice)
        case "/waiting":
            return pages.waiting_page(*lodge.waiting_all(), notice)
        case _:
            result, read = lodge.problems()
            return pages.problems_page(result, read, notice)


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
