import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from e2e.conftest import Project
from e2e.support import QUOTE, seed
from lodge.app import Lodge
from lodge.cli import run


def test_view_serves_the_project_until_interrupted(
    project: Project, monkeypatch: pytest.MonkeyPatch
) -> None:
    ids = seed(project, QUOTE, decided_by="author")
    served: list[tuple[int, str]] = []
    real = ThreadingHTTPServer.serve_forever

    def serve_and_ask(self: ThreadingHTTPServer, *_: float) -> None:
        worker = threading.Thread(target=real, args=(self, 0.05))
        worker.start()
        port = self.server_address[1]
        try:
            for path in ("/r/ITEM-1", "/spec", "/nowhere"):
                try:
                    with urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as response:
                        served.append((response.status, response.read().decode("utf-8")))
                except HTTPError as error:
                    served.append((error.code, ""))
        finally:
            self.shutdown()
            worker.join()
        raise KeyboardInterrupt

    monkeypatch.setattr(ThreadingHTTPServer, "serve_forever", serve_and_ask)
    result = project.run("view", "--port", "0")
    assert (result.code, result.err) == (0, "")
    assert result.out.startswith("lodge viewer: http://127.0.0.1:")
    assert [status for status, _ in served] == [200, 200, 404]
    assert ids.decision in served[0][1] and "Keep them." in served[0][1]
    assert "<h1>" in served[1][1]


def test_view_outside_a_repository_is_one_sentence(project: Project, tmp_path: Path) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()
    result = project.run("view", "--port", "0", cwd=plain)
    assert (result.code, result.out) == (2, "")
    assert result.err == f"lodge: {plain} is not inside a git repository\n"


def test_view_passes_the_port_to_the_viewer() -> None:
    ports: list[int] = []

    def view(port: int) -> int:
        ports.append(port)
        return 0

    def unused() -> Lodge:
        raise AssertionError("the viewer is started without reading the store")

    def never() -> str:
        raise AssertionError("not called")

    for argv in (["view"], ["view", "--port", "9000"]):
        assert run(argv, unused, never, view, lambda: 0) == 0
    assert ports == [8787, 9000]
