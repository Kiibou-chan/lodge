"""Replay options preserve the experiment's edits, environment, and warm state."""

import json
import os
import subprocess
from hashlib import sha256
from pathlib import Path
from unittest.mock import Mock

import pytest

from test_bench_cleanup import benchmark


def test_chained_keeps_cache_and_distinct_edits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = benchmark()
    entry = tmp_path / "entry.md"
    original = "Berths hold cranes.\n"
    entry.write_text(original)
    edits: list[str] = []

    def replay(*_: object, **__: object) -> tuple[float, int, str]:
        if "Benchmark run" in entry.read_text():
            edits.append(entry.read_text())
        return 0.01, 0, "ok"

    monkeypatch.setattr(module, "run", replay)
    monkeypatch.setattr(module, "clear", lambda _: pytest.fail("chained cleared the cache"))
    monkeypatch.setattr(module.shutil, "copytree", lambda *_: pytest.fail("chained copied cache"))
    monkeypatch.setattr(module, "epochs", lambda _: {"index-test.sqlite": 7}, raising=False)
    checkout = Mock(side_effect=lambda *_, **__: entry.write_text(original))
    monkeypatch.setattr(module.subprocess, "run", checkout)
    results = module.measure(
        tmp_path,
        ["lodge"],
        [("show A", ["show", "A"]), ("waiting", ["waiting"])],
        "chained",
        3,
        tmp_path / "cache",
        entry,
        timeout=1,
    )
    assert len(edits) == len(set(edits)) == 6
    assert [len(samples) for samples in results] == [3, 3]
    events = [
        json.loads(line.removeprefix("Epochs: "))
        for line in capsys.readouterr().out.splitlines()
        if line.startswith("Epochs: ")
    ]
    assert len(events) == 6
    assert all(e["exit"] == 0 and e["stdout_sha256"] == sha256(b"ok").hexdigest() for e in events)
    assert entry.read_text() == original
    assert checkout.call_args.args[0] == ["git", "checkout", "--", "lodge"]


def test_seen_primes_both_sightings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = benchmark()
    entry = tmp_path / "entry.md"
    entry.write_text("Berths hold cranes.\n")
    replay = Mock(return_value=(0.01, 0, "ok"))
    monkeypatch.setattr(module, "run", replay)
    module.measure(
        tmp_path,
        ["lodge"],
        [("show A", ["show", "A"])],
        "seen",
        3,
        tmp_path / "cache",
        entry,
        timeout=1,
    )
    assert replay.call_count == 5


def test_git_config_reaches_every_child(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = benchmark()
    commands = tmp_path / "commands.txt"
    commands.write_text("show A\n")
    config = tmp_path / "global.config"
    config.write_text("[core]\n autocrlf = input\n")
    entry = tmp_path / "entry.md"
    entry.write_text("Berths hold cranes.\n")
    monkeypatch.setattr(module, "placeholders", lambda _: ({}, entry))
    environments: list[dict[str, str]] = []

    def git(args: list[str], **kw: object) -> str:
        environments.append(kw["env"])  # type: ignore[arg-type]
        return str(tmp_path) if "rev-parse" in args else ""

    def replay(args: list[str], **kw: object) -> subprocess.CompletedProcess[str]:
        environments.append(kw["env"])  # type: ignore[arg-type]
        return subprocess.CompletedProcess(args, 0, "ok")

    monkeypatch.setattr(module.subprocess, "check_output", git)
    monkeypatch.setattr(module.subprocess, "run", replay)
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
            "chained",
            "--runs",
            "1",
            "--git-config",
            str(config),
        ],
    )
    module.main()
    assert len(environments) >= 5
    assert all(env["GIT_CONFIG_GLOBAL"] == str(config) for env in environments)
    assert all(
        env["GIT_CONFIG_NOSYSTEM"] == env["GIT_ATTR_NOSYSTEM"] == "1" for env in environments
    )
    assert all(env["PATH"] == os.environ["PATH"] for env in environments)


def test_startup_uses_build_python_best_of_nine(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = benchmark()
    commands: list[list[str]] = []

    def replay(_: Path, command: list[str], **__: object) -> tuple[float, int, str]:
        commands.append(command)
        return 0.01, 0, "ok"

    monkeypatch.setattr(module, "run", replay)
    monkeypatch.setattr(
        "sys.argv",
        [
            "bench_reads",
            str(tmp_path),
            "--lodge",
            "/synthetic/bin/python -m lodge.main",
            "--startup",
            "--git-config",
            "/dev/null",
        ],
    )
    module.main()
    assert commands.count(["/synthetic/bin/python", "-c", "pass"]) == 9
    assert commands.count(["/synthetic/bin/python", "-c", "import lodge.main"]) == 9
    assert commands.count(["/synthetic/bin/python", "-m", "lodge.main", "guide", "--read"]) == 9
    assert "0.010" in capsys.readouterr().out


def test_epoch_probe_skips_incomplete_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = benchmark()
    (tmp_path / "index-empty.sqlite").touch()
    db = Mock()
    db.execute.return_value.fetchone.return_value = None
    monkeypatch.setattr(module.sqlite3, "connect", Mock(return_value=db))
    assert module.epochs(tmp_path) == {}
    db.close.assert_called_once()


def test_startup_resolves_installed_lodge_python(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = benchmark()
    monkeypatch.setattr(module.shutil, "which", lambda _: "/synthetic/venv/bin/lodge")
    replay = Mock(return_value=(0.01, 0, "ok"))
    monkeypatch.setattr(module, "run", replay)
    module.startup(tmp_path, ["lodge"], 1, {})
    assert replay.call_args_list[0].args[1] == ["/synthetic/venv/bin/python", "-c", "pass"]


def test_replay_observes_shared_common_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = benchmark()
    commands = tmp_path / "commands.txt"
    commands.write_text("show A\n")
    common = tmp_path / "common"
    administrative = tmp_path / "worktree-admin"
    monkeypatch.setattr(module, "placeholders", lambda _: ({}, tmp_path / "entry.md"))

    def git(args: list[str], **_: object) -> str:
        if "rev-parse" in args:
            return str(common if "--git-common-dir" in args else administrative)
        return ""

    replay = Mock(return_value=[[(0.01, 0, "ok")]])
    monkeypatch.setattr(module.subprocess, "check_output", git)
    monkeypatch.setattr(module, "measure", replay)
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
            "chained",
        ],
    )
    module.main()
    assert replay.call_args.args[5] == common / "lodge"
