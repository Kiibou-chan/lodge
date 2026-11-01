"""Benchmark interruptions restore edits and reject contaminated inputs."""

import importlib.util
import signal
import subprocess
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest


def benchmark() -> ModuleType:
    path = Path(__file__).resolve().parents[1] / "scripts" / "bench_reads.py"
    spec = importlib.util.spec_from_file_location("bench_reads", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_benchmark_timeout_restores_edit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = benchmark()
    entry = tmp_path / "entry.md"
    entry.write_text("A berth has a crane.\n")
    calls = []

    def replay(*args: object, **kwargs: object) -> tuple[float, int, str]:
        calls.append(kwargs.get("timeout", args[-1]))
        if len(calls) > 1:
            raise subprocess.TimeoutExpired("lodge", 0.01)
        return 0.0, 0, "ok"

    monkeypatch.setattr(module, "run", replay)
    checkout = Mock()
    monkeypatch.setattr(module.subprocess, "run", checkout)
    with pytest.raises(subprocess.TimeoutExpired):
        module.measure(
            tmp_path,
            ["lodge"],
            [("show A", ["show", "A"])],
            "changed",
            1,
            tmp_path / "cache",
            entry,
            timeout=0.01,
        )
    assert calls == [0.01, 0.01]
    checkout.assert_called_once()
    assert not list(tmp_path.glob("read-cache-*"))


@pytest.mark.parametrize("mode", ["cold", "seen", "changed"])
def test_benchmark_rejects_dirty_store(
    mode: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = benchmark()
    commands = tmp_path / "reads.txt"
    commands.write_text("show A\n")
    monkeypatch.setattr(module, "placeholders", lambda _: ({}, tmp_path / "entry.md"))
    monkeypatch.setattr(
        module.subprocess,
        "check_output",
        lambda args, **_: str(tmp_path) if "rev-parse" in args else " M lodge/spec/berth.md\n",
    )
    monkeypatch.setattr(module, "measure", lambda *_, **__: pytest.fail("dirty store timed"))
    monkeypatch.setattr(
        "sys.argv",
        [
            "bench_reads",
            str(tmp_path),
            "--lodge",
            "lodge",
            "--commands",
            str(commands),
            "--mode",
            mode,
        ],
    )
    with pytest.raises(SystemExit) as error:
        module.main()
    assert error.value.code == 2


def test_sigterm_raises_for_cleanup() -> None:
    module = benchmark()
    with pytest.raises(SystemExit) as error:
        module.terminate(signal.SIGTERM, None)
    assert error.value.code == 128 + signal.SIGTERM


def test_replay_passes_timeout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = benchmark()
    replay = Mock(return_value=subprocess.CompletedProcess(["lodge"], 0, "ok"))
    monkeypatch.setattr(module.subprocess, "run", replay)
    assert module.run(tmp_path, ["lodge"], timeout=0.01)[1:] == (0, "ok")
    assert replay.call_args.kwargs["timeout"] == 0.01
