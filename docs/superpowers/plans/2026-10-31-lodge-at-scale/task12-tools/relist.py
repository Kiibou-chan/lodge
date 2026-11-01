"""Measure full folder relists on a synthetic copy, counting every git spawn."""

import argparse
import json
import os
import shutil
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from lodge.gitstore import open_index, open_store
from lodge.gitstore.settings import StoreSettings


class Clock:
    def now(self) -> datetime:
        return datetime(2026, 1, 1, tzinfo=UTC)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(os.environ.get("LODGE_BENCH_ROOT", "/var/tmp/lodge-bench")),
    )
    parser.add_argument("--source-store", type=Path)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--label", default="current")
    args = parser.parse_args()
    repo = args.root / "task12-fix/relist-store"
    repo.parent.mkdir(parents=True, exist_ok=True)
    home = args.root / "task12/home"
    home.mkdir(parents=True, exist_ok=True)
    env = {
        **os.environ,
        "HOME": str(home),
        "XDG_CONFIG_HOME": str(home / "xdg"),
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_ATTR_NOSYSTEM": "1",
        "GIT_OPTIONAL_LOCKS": "0",
    }
    os.environ.update(env)

    def git(*arguments: str) -> None:
        subprocess.run(
            ["git", "-C", str(repo), *arguments], env=env, check=True, capture_output=True
        )

    if not repo.exists():
        subprocess.run(
            [
                "git",
                "clone",
                "--quiet",
                "--no-hardlinks",
                str(args.source_store or args.root / "s90000"),
                str(repo),
            ],
            env=env,
            check=True,
        )
    git("config", "user.name", "Synthetic")
    git("config", "user.email", "synthetic@example.invalid")
    git("update-index", "--refresh")
    index = open_index(repo / ".git")
    assert index is not None
    entry = next((repo / "lodge").rglob("s-*.md"))
    try:
        for sample in range(1, args.samples + 1):
            open_store(repo, StoreSettings(), Clock(), index=index).identities()
            entry.write_text(entry.read_text() + f"\nSynthetic relist edit {sample}.\n")
            git("add", "--", str(entry.relative_to(repo)))
            git("commit", "-qm", "Synthetic relist base")
            for mode in ["new-commit", "cold-index"]:
                if mode == "cold-index":
                    index.close()
                    shutil.rmtree(repo / ".git/lodge")
                    index = open_index(repo / ".git")
                    assert index is not None
                git("update-index", "--refresh")
                original = subprocess.Popen
                processes = 0

                def spawn(*positional, **keywords):
                    nonlocal processes
                    if positional and positional[0][0] == "git":
                        processes += 1
                    return original(*positional, **keywords)

                with patch.object(subprocess, "Popen", spawn):
                    start = time.perf_counter()
                    open_store(repo, StoreSettings(), Clock(), index=index).identities()
                    seconds = time.perf_counter() - start
                print(
                    json.dumps(
                        dict(
                            label=args.label,
                            sample=sample,
                            mode=mode,
                            seconds=seconds,
                            processes=processes,
                        )
                    ),
                    flush=True,
                )
    finally:
        index.close()


if __name__ == "__main__":
    main()
