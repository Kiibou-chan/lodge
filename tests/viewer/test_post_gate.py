from urllib.parse import urlencode

import pytest

from lodge.viewer import server, writes
from viewer.world import world

TOKEN = "a" * 32
HEADERS = {
    "host": "127.0.0.1:8787",
    "origin": "http://127.0.0.1:8787",
    "content-type": "application/x-www-form-urlencoded",
}


def post(body: bytes | None = None, **headers: str) -> writes.Reply:
    return writes.handle_post(
        world,
        writes.Gatekeeper(TOKEN, writes.allowed_hosts(8787, ())),
        "/confirm",
        HEADERS | headers,
        body
        if body is not None
        else urlencode({"token": TOKEN, "id": "d-cccccc", "words": "Read."}).encode(),
    )


def test_no_origin_refused() -> None:
    assert post(origin="").status == 403


def test_foreign_origin_refused() -> None:
    assert post(origin="http://evil.example").status == 403


@pytest.mark.parametrize(
    "origin,status",
    [
        ("ftp://127.0.0.1:8787", 403),
        ("http://127.0.0.1:8788", 403),
        ("https://localhost:8787", 303),
    ],
)
def test_origin_needs_scheme_and_allowed_host(origin: str, status: int) -> None:
    assert post(origin=origin).status == status


def test_allow_host_matches_the_whole_host() -> None:
    gate = writes.Gatekeeper(TOKEN, writes.allowed_hosts(8787, ["PROXY.example:443"]))
    assert (
        writes.refuse_early(
            gate, HEADERS | {"host": "proxy.example:443", "origin": "https://proxy.example:443"}
        )
        is None
    )
    assert writes.refuse_early(gate, HEADERS | {"host": "proxy.example"}) is not None


def test_missing_token_refused() -> None:
    assert post(b"words=x").status == 403


def test_wrong_token_refused() -> None:
    assert post(b"token=wrong").status == 403


def test_two_token_fields_refused() -> None:
    assert post(f"token={TOKEN}&token={TOKEN}".encode()).status == 403


def test_non_ascii_token_refused() -> None:
    assert post("token=é".encode()).status == 403


def test_token_compared_with_hmac(monkeypatch: pytest.MonkeyPatch) -> None:
    called = []
    real = writes.hmac.compare_digest

    def spy(a: bytes, b: bytes) -> bool:
        called.append((a, b))
        return bool(real(a, b))

    monkeypatch.setattr(writes.hmac, "compare_digest", spy)
    post()
    assert called == [(TOKEN.encode(), TOKEN.encode())]


def test_wrong_content_type_415() -> None:
    assert post(None, **{"content-type": "text/plain"}).status == 415


def test_body_over_limit_413() -> None:
    assert post(b"x" * (writes.MAX_BODY + 1)).status == 413


def test_non_utf8_body_400() -> None:
    assert post(b"\xff").status == 400


def test_bad_percent_escape_400() -> None:
    assert post(b"words=%FF").status == 400


def test_too_many_fields_400() -> None:
    assert post(b"a=1&" * 201).status == 400


def test_bad_id_400() -> None:
    assert (
        post(urlencode({"token": TOKEN, "id": "s-aaaaaa", "words": "yes"}).encode()).status == 400
    )


def test_short_token_refused_by_gatekeeper() -> None:
    with pytest.raises(ValueError):
        writes.Gatekeeper("short", frozenset())


def test_handler_dispatch_and_timeout() -> None:
    assert callable(server._Handler.do_POST)
    assert server._Handler.timeout == 10
