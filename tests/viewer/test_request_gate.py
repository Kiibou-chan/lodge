"""Exercise the HTTP boundary with in-memory streams, without opening sockets."""

from email.message import Message
from io import BytesIO
from types import SimpleNamespace
from typing import cast
from urllib.parse import urlencode

import pytest

from lodge.viewer import server, writes
from viewer.test_post_gate import HEADERS, TOKEN
from viewer.world import staged_world


class BodyReader(BytesIO):
    def read(self, size: int | None = -1) -> bytes:
        self.read_sizes.append(size)
        return super().read(size)

    def __init__(self, body: bytes) -> None:
        super().__init__(body)
        self.read_sizes: list[int | None] = []


def request(
    method: str, extra: list[tuple[str, str]], body: bytes, *, prepend: bool = False
) -> tuple[bytes, BodyReader, int]:
    make, store = staged_world()
    handler = object.__new__(server._Handler)
    handler.server = cast(
        server._Server,
        SimpleNamespace(
            make_lodge=make, gate=writes.Gatekeeper(TOKEN, writes.allowed_hosts(8787, ()))
        ),
    )
    handler.headers = Message()
    pairs = [*extra, *HEADERS.items()] if prepend else [*HEADERS.items(), *extra]
    for key, value in pairs:
        handler.headers[key] = value
    reader = BodyReader(body)
    output = BytesIO()
    handler.rfile, handler.wfile = reader, output
    handler.command, handler.path = method, "/confirm"
    handler.request_version = "HTTP/1.1"
    handler.requestline = f"{method} /confirm HTTP/1.1"
    if method == "POST":
        handler.do_POST()
    else:
        handler.do_GET()
    return output.getvalue(), reader, len(store.publishes)


def form() -> bytes:
    return urlencode({"token": TOKEN, "id": "d-cccccc", "words": "I read it"}).encode()


def test_short_body_refused_without_writing() -> None:
    body = form()
    response, reader, publishes = request("POST", [("Content-Length", str(len(body) + 20))], body)
    assert b"400 Bad Request" in response
    assert b"the form arrived incomplete; nothing was written" in response
    assert reader.read_sizes == [len(body) + 20]
    assert publishes == 0


def test_excessive_declared_length_refused_without_reading() -> None:
    response, reader, publishes = request("POST", [("Content-Length", "65537")], form())
    assert b"HTTP/1.0 413 " in response
    assert reader.read_sizes == []
    assert publishes == 0


@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize("name", ["Host", "Origin", "Content-Length", "Content-Type"])
@pytest.mark.parametrize("foreign_first", [False, True])
def test_repeated_headers_refused(method: str, name: str, foreign_first: bool) -> None:
    extra = [("Content-Length", str(len(form())))]
    if name == "Content-Length":
        extra.append((name, str(len(form()))))
    else:
        extra.append((name, "evil.example"))
    # HEADERS supplies the first Host, Origin, and Content-Type.
    response, reader, publishes = request(method, extra, form(), prepend=foreign_first)
    assert b"400 Bad Request" in response
    assert reader.read_sizes == []
    assert publishes == 0


def test_write_refusal_is_a_complete_page() -> None:
    response, _, publishes = request("POST", [], b"")
    assert b"411 Length Required" in response
    assert b"<!doctype html>" in response.lower()
    assert b"/style.css" in response
    assert publishes == 0
