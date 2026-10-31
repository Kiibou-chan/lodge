import http.client
import socket
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from http.server import ThreadingHTTPServer

import pytest

from lodge.app import Lodge, LodgeError
from lodge.viewer import server
from viewer.world import BAD, staged_world, world

ROUTES = ["/", "/?q=keep&kind=decision", "/r/d-aaaaaa", "/r/ITEM-1", "/spec", "/timeline"]
ROUTES += ["/waiting", "/problems", "/style.css"]


@contextmanager
def running(make_lodge: Callable[[], Lodge]) -> Iterator[int]:
    httpd = server.make_server(make_lodge, 0, token="a" * 32)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.start()
    try:
        yield httpd.server_address[1]
    finally:
        httpd.shutdown()
        thread.join()
        httpd.server_close()


def get(
    port: int, path: str, host: str | None = None, method: str = "GET"
) -> tuple[int, dict[str, str], str]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    connection.putrequest(method, path, skip_host=True)
    connection.putheader("Host", host if host is not None else f"127.0.0.1:{port}")
    connection.endheaders()
    response = connection.getresponse()
    body = response.read().decode("utf-8")
    headers = {k.lower(): v for k, v in response.getheaders()}
    connection.close()
    return response.status, headers, body


def test_server_routes() -> None:
    with running(world) as port:
        for route in ROUTES:
            assert get(port, route)[0] == 200, route
        assert get(port, "/nope")[0] == 404
        assert get(port, "/r/")[0] == 404
        assert get(port, "/spec/")[0] == 404
        assert get(port, "/", host="evil.example:80")[0] == 403
        assert get(port, "/", host=f"127.0.0.1:{port + 1}")[0] == 403
        assert get(port, "/", host="127.0.0.1")[0] == 403
        assert get(port, "/", host=f"localhost:{port}")[0] == 200
        assert get(port, "/", host=f"LOCALHOST:{port}")[0] == 200


def test_pages_are_html_and_style_is_css() -> None:
    with running(world) as port:
        _, headers, body = get(port, "/")
        assert headers["content-type"] == "text/html; charset=utf-8"
        assert '<link rel="stylesheet" href="/style.css">' in body
        assert "prefers-color-scheme" in get(port, "/style.css")[2]
        assert get(port, "/style.css")[1]["content-type"] == "text/css; charset=utf-8"


def test_search_filters_arrive_from_the_query() -> None:
    with running(world) as port:
        body = get(port, "/?q=&kind=spec")[2]
        assert "s-aaaaaa" in body and "Reword transcripts" not in body
        assert '<option value="spec" selected>' in body


def test_a_fresh_lodge_for_each_request() -> None:
    made: list[Lodge] = []

    def make() -> Lodge:
        made.append(world())
        return made[-1]

    with running(make) as port:
        get(port, "/")
        get(port, "/")
    assert len(made) == 2 and made[0] is not made[1]


def test_lodge_error_is_a_page_with_its_message() -> None:
    with running(world) as port:
        status, _, body = get(port, "/r/nothing")
        assert status == 404 and "no record named nothing" in body
        assert get(port, "/spec?area=nowhere")[0] == 404
        assert get(port, "/?kind=bogus")[0] == 400

    def refuse() -> Lodge:
        raise LodgeError("not inside a git repository <here>")

    with running(refuse) as port:
        status, _, body = get(port, "/")
        assert status == 400 and "not inside a git repository &lt;here&gt;" in body


def test_other_failures_are_a_plain_500() -> None:
    def broken() -> Lodge:
        raise RuntimeError("secret detail")

    with running(broken) as port:
        status, _, body = get(port, "/")
        assert status == 500 and "secret detail" not in body


def test_unreadable_file_banner_reaches_the_browser() -> None:
    with running(lambda: world(broken=True)) as port:
        body = get(port, "/r/d-aaaaaa")[2]
        assert BAD in body and 'href="/problems"' in body


def test_post_without_origin_and_other_methods_refused() -> None:
    with running(world) as port:
        assert get(port, "/", method="POST")[0] == 403
        assert get(port, "/", method="DELETE")[0] == 405
        status, _, body = get(port, "/", method="HEAD")
        assert status == 200 and body == ""


def test_response_headers_lock_the_page_down() -> None:
    with running(world) as port:
        headers = get(port, "/")[1]
        assert "default-src 'none'" in headers["content-security-policy"]
        assert headers["x-content-type-options"] == "nosniff"
        assert headers["cache-control"] == "no-store"


def test_bound_to_loopback_only() -> None:
    httpd = server.make_server(world, 0, token="a" * 32)
    try:
        assert httpd.server_address[0] == "127.0.0.1"
    finally:
        httpd.server_close()


def test_serve_reports_a_port_in_use_as_one_sentence() -> None:
    with socket.socket() as held:
        held.bind(("127.0.0.1", 0))
        held.listen()
        port = held.getsockname()[1]
        with pytest.raises(LodgeError, match=f"cannot listen on port {port}.*--port"):
            server.serve(world, port, (), "a" * 32)


def test_serve_announces_the_address_and_stops_on_interrupt(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def interrupt(self: ThreadingHTTPServer, *_: float) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(ThreadingHTTPServer, "serve_forever", interrupt)
    assert server.serve(world, 0, (), "a" * 32) == 0
    assert "http://127.0.0.1:" in capsys.readouterr().out


def test_closing_the_server_waits_for_a_request_that_is_running() -> None:
    started, release = threading.Event(), threading.Event()

    def slow() -> Lodge:
        started.set()
        release.wait(10)
        return world()

    httpd = server.make_server(slow, 0, token="a" * 32)
    port = httpd.server_address[1]
    serving = threading.Thread(target=httpd.serve_forever)
    serving.start()
    asking = threading.Thread(target=get, args=(port, "/"))
    asking.start()
    assert started.wait(10)
    httpd.shutdown()
    serving.join()
    closing = threading.Thread(target=httpd.server_close)
    closing.start()
    closing.join(0.3)
    waiting = closing.is_alive()
    release.set()
    closing.join(10)
    asking.join(10)
    assert waiting and not closing.is_alive()


def test_post_through_the_socket_redirects() -> None:
    make, _ = staged_world()
    with running(make) as port:
        status, headers = post_request(port, "token=" + "a" * 32 + "&id=d-cccccc&words=Yes")
        assert status == 303
        assert headers["location"] == "/r/d-cccccc?done=committed"


def test_put_answers_405_allowing_post() -> None:
    with running(world) as port:
        status, headers, body = get(port, "/", method="PUT")
        assert status == 405
        assert headers["allow"] == "GET, HEAD, POST"
        assert "this address takes no such request" in body


def test_allow_host_is_served() -> None:
    httpd = server.make_server(world, 0, token="a" * 32, allow_hosts=("proxy.example:443",))
    thread = threading.Thread(target=httpd.serve_forever)
    thread.start()
    try:
        assert get(httpd.server_address[1], "/", host="PROXY.example:443")[0] == 200
        assert get(httpd.server_address[1], "/", host="proxy.example")[0] == 403
    finally:
        httpd.shutdown()
        thread.join()
        httpd.server_close()


def test_post_without_length_411() -> None:
    with running(world) as port:
        assert post_request(port, None)[0] == 411


def test_negative_length_400() -> None:
    with running(world) as port:
        assert post_request(port, None, "-1")[0] == 400


def post_request(
    port: int, body: str | None, length: str | None = None
) -> tuple[int, dict[str, str]]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    connection.putrequest("POST", "/confirm")
    connection.putheader("Origin", f"http://127.0.0.1:{port}")
    connection.putheader("Content-Type", "application/x-www-form-urlencoded")
    if body is not None or length is not None:
        connection.putheader(
            "Content-Length", length if length is not None else str(len(body or ""))
        )
    connection.endheaders(None if body is None else body.encode())
    response = connection.getresponse()
    response.read()
    result = response.status, {k.lower(): v for k, v in response.getheaders()}
    connection.close()
    return result
