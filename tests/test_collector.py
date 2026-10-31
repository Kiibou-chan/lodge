"""Only the real, one-shot entry point disables cyclic collection."""

import gc

import pytest

import lodge.main as entrypoint


def test_main_disables_the_collector_for_one_shot_commands(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(entrypoint, "_exit_on_signals", lambda: None)
    monkeypatch.setattr("sys.argv", ["lodge", "guide"])
    gc.enable()
    try:
        assert entrypoint.main(["guide"]) == 0
        assert gc.isenabled()
        assert entrypoint.main() == 0
        assert not gc.isenabled()
    finally:
        gc.enable()
    capsys.readouterr()


def test_view_keeps_the_collector(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(entrypoint, "_exit_on_signals", lambda: None)
    monkeypatch.setattr(entrypoint, "_make_lodge", lambda: None)
    seen = []

    def serve(*args: object) -> int:
        seen.append(gc.isenabled())
        return 0

    monkeypatch.setattr(entrypoint, "serve", serve)
    gc.enable()
    try:
        monkeypatch.setattr("sys.argv", ["lodge", "view"])
        assert entrypoint.main() == 0
        assert seen == [True] and gc.isenabled()
        monkeypatch.setattr("sys.argv", ["lodge", "guide"])
        assert entrypoint.main() == 0
        assert not gc.isenabled(), "view and one-shot commands must take different collector paths"
    finally:
        gc.enable()
    capsys.readouterr()
