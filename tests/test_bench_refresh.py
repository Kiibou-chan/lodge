"""Every copied synthetic checkout refreshes git's index before reads are timed."""

import importlib.util
from pathlib import Path
from unittest.mock import Mock

import pytest

from test_bench_cleanup import benchmark


def test_replay_refreshes_once_before_measuring(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = benchmark()
    commands = tmp_path / "commands.txt"
    commands.write_text("show A\n")
    monkeypatch.setattr(module, "placeholders", lambda _: ({}, tmp_path / "entry.md"))
    monkeypatch.setattr(
        module.subprocess,
        "check_output",
        lambda args, **_: str(tmp_path) if "rev-parse" in args else "",
    )
    refresh = Mock()
    monkeypatch.setattr(module.subprocess, "run", refresh)

    def measure(*_: object) -> list[list[tuple[float, int, str]]]:
        refresh.assert_called_once()
        assert refresh.call_args.args[0] == ["git", "update-index", "--refresh"]
        assert refresh.call_args.kwargs["cwd"] == tmp_path
        assert refresh.call_args.kwargs["check"] is True
        return [[(0.01, 0, "ok")]]

    monkeypatch.setattr(module, "measure", measure)
    monkeypatch.setattr(
        "sys.argv", ["bench_reads", str(tmp_path), "--lodge", "lodge", "--commands", str(commands)]
    )
    module.main()


@pytest.mark.parametrize("exists", [False, True])
def test_task12_setup_refreshes_each_copy_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, exists: bool
) -> None:
    path = Path(__file__).resolve().parents[1] / (
        "docs/superpowers/plans/2026-10-31-lodge-at-scale/task12-tools/setup.py"
    )
    spec = importlib.util.spec_from_file_location("task12_setup", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    dest = tmp_path / "copy"
    if exists:
        dest.mkdir()
    calls = Mock()
    monkeypatch.setattr(module.subprocess, "run", calls)
    env = {"GIT_OPTIONAL_LOCKS": "0"}
    module.prepare_store(tmp_path / "synthetic-source", dest, env)
    refresh = [c for c in calls.call_args_list if "update-index" in c.args[0]]
    assert len(refresh) == 1
    assert refresh[0].args[0] == ["git", "update-index", "--refresh"]
    assert refresh[0].kwargs == {"cwd": dest, "env": env, "check": True}
    assert calls.call_args == refresh[0]
    clones = [c for c in calls.call_args_list if "clone" in c.args[0]]
    assert len(clones) == int(not exists)
