from collections.abc import Mapping
from pathlib import Path

from structure_rules import ALLOWED, violations

PACKAGES = sorted(p for p in ALLOWED if p != "main")


Files = Mapping[str, str | bytes | None]


def put(base: Path, files: Files) -> None:
    for rel, content in files.items():
        target = base / rel
        if content is None:
            target.unlink(missing_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content if isinstance(content, bytes) else content.encode())


def scan(tmp_path: Path, files: Files, tests: Files | None = None) -> list[str]:
    """Build `src/lodge` with the six empty front doors, then apply `files` (`None` removes)."""
    pkg = tmp_path / "src" / "lodge"
    tree = {"__init__.py": "", "main.py": ""} | {f"{n}/__init__.py": "" for n in PACKAGES}
    put(pkg, tree)
    put(pkg, files)
    put(tmp_path / "tests", tests or {})
    return violations(tmp_path / "src", tmp_path / "tests")


def only(found: list[str], fragment: str) -> None:
    assert len(found) == 1 and fragment in found[0], found
