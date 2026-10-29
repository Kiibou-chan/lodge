import os
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
OFFLINE = ("error sending request", "dns error", "failed to fetch", "network", "connect")


def uv(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["uv", *args], cwd=cwd, capture_output=True, text=True, check=False)


def need(done: subprocess.CompletedProcess[str], what: str) -> None:
    """Skips when uv could not reach the network, fails on any other error."""
    if done.returncode == 0:
        return
    if any(word in done.stderr.lower() for word in OFFLINE):
        pytest.skip(f"{what} needs the network, which is not reachable: {done.stderr.strip()}")
    pytest.fail(f"{what} failed: {done.stderr}")


@pytest.mark.slow
def test_installed_wheel_runs(tmp_path: Path) -> None:
    dist, venv = tmp_path / "dist", tmp_path / "venv"
    need(uv("build", "--wheel", "--out-dir", str(dist)), "uv build")
    (wheel,) = dist.glob("lodge-*.whl")
    with zipfile.ZipFile(wheel) as built:
        assert {"lodge/viewer/style.css", "lodge/cli/guide.md"} <= set(built.namelist())
    need(uv("venv", str(venv)), "uv venv")
    need(uv("pip", "install", "--python", str(venv), str(wheel)), "uv pip install")
    bindir = venv / ("Scripts" if os.name == "nt" else "bin")
    lodge = shutil.which("lodge", path=str(bindir))
    assert lodge is not None
    where = tmp_path
    version = subprocess.run([lodge, "--version"], cwd=where, capture_output=True, text=True)
    assert (version.returncode, version.stdout) == (0, "lodge 0.1.0\n")
    guide = subprocess.run([lodge, "guide"], cwd=where, capture_output=True, text=True)
    assert guide.returncode == 0
    assert guide.stdout.startswith("# ") and "lodge add" in guide.stdout
