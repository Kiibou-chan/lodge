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

    def replay(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        if "timeout" not in kwargs:
            entry.write_text("A berth has a crane.\n")
            return subprocess.CompletedProcess(command, 0, "")
        calls.append(kwargs["timeout"])
        if len(calls) > 1:
            raise subprocess.TimeoutExpired("lodge", 0.01)
        return subprocess.CompletedProcess(command, 0, "ok")

    checkout = Mock(side_effect=replay)
    monkeypatch.setattr(module.subprocess, "run", checkout)
    results = module.measure(
        tmp_path,
        ["lodge"],
        [("show A", ["show", "A"])],
        "changed",
        1,
        tmp_path / "cache",
        entry,
        timeout=0.01,
    )
    assert results == [[(0.01, None, None)]]
    assert calls == [0.01, 0.01]
    assert checkout.call_args.args[0] == ["git", "checkout", "--", "lodge"]
    assert entry.read_text() == "A berth has a crane.\n"
    assert not list(tmp_path.glob("read-cache-*"))


@pytest.mark.parametrize("mode", ["cold", "seen", "changed"])
def test_timeout_keeps_measured_rows_and_continues(
    mode: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = benchmark()
    commands = tmp_path / "reads.txt"
    commands.write_text("show first\nshow slow\nshow last\n")
    entry = tmp_path / "entry.md"
    entry.write_text("Berths are held.\n")
    monkeypatch.setattr(module, "placeholders", lambda _: ({}, entry))
    monkeypatch.setattr(
        module.subprocess,
        "check_output",
        lambda args, **_: str(tmp_path) if "rev-parse" in args else "",
    )

    def replay(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        if command[-1] == "slow":
            raise subprocess.TimeoutExpired(command, 0.01, output="partial output")
        return subprocess.CompletedProcess(command, 0, "ok")

    monkeypatch.setattr(module.subprocess, "run", replay)
    monkeypatch.setattr(
        "sys.argv",
        [
            "bench_reads",
            str(tmp_path),
            "--lodge",
            "lodge",
            "--against",
            "old-lodge",
            "--commands",
            str(commands),
            "--mode",
            mode,
            "--runs",
            "1",
            "--timeout",
            "0.01",
        ],
    )
    module.main()
    output = capsys.readouterr().out
    rows = [line for line in output.splitlines() if line.startswith("| `show")]
    assert len(rows) == 6
    assert "`show first`" in rows[0] and "| true |" in rows[0]
    assert "`show slow`" in rows[2] and "| >0.010 | >0.010 | timeout | n/a | false |" in rows[2]
    assert "`show last`" in rows[4] and "| true |" in rows[4]


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


def test_timeout_keeps_successful_samples_in_the_same_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = benchmark()
    commands = tmp_path / "reads.txt"
    commands.write_text("show A\n")
    monkeypatch.setattr(module, "placeholders", lambda _: ({}, tmp_path / "entry.md"))
    monkeypatch.setattr(
        module.subprocess,
        "check_output",
        lambda args, **_: str(tmp_path) if "rev-parse" in args else "",
    )
    monkeypatch.setattr(module, "measure", lambda *_: [[(0.001, 0, "ok"), (0.01, None, None)]])
    monkeypatch.setattr(
        "sys.argv",
        [
            "bench_reads",
            str(tmp_path),
            "--lodge",
            "lodge",
            "--commands",
            str(commands),
            "--timeout",
            "0.01",
            "--runs",
            "2",
        ],
    )
    module.main()
    assert "| 0.001 | includes >0.010 | 0, timeout | 2, n/a |" in capsys.readouterr().out


def test_replay_passes_timeout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = benchmark()
    replay = Mock(return_value=subprocess.CompletedProcess(["lodge"], 0, "ok"))
    monkeypatch.setattr(module.subprocess, "run", replay)
    assert module.run(tmp_path, ["lodge"], timeout=0.01)[1:] == (0, "ok")
    assert replay.call_args.kwargs["timeout"] == 0.01
