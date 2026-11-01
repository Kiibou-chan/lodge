"""Prepare refreshed synthetic clones and compiled source copies for Task 12."""

import argparse
import compileall
import os
import shutil
import subprocess
from pathlib import Path


def prepare_store(source: Path, dest: Path, env: dict[str, str]) -> None:
    if not dest.exists():
        subprocess.run(
            ["git", "clone", "--quiet", "--no-hardlinks", str(source), str(dest)],
            env=env,
            check=True,
        )
        for key, value in [("user.name", "Synthetic"), ("user.email", "synthetic@example.invalid")]:
            subprocess.run(["git", "config", key, value], cwd=dest, env=env, check=True)
    subprocess.run(["git", "update-index", "--refresh"], cwd=dest, env=env, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(os.environ.get("LODGE_BENCH_ROOT", "/var/tmp/lodge-bench")),
    )
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[5])
    parser.add_argument("--production-only", action="store_true")
    parser.add_argument(
        "--source-ref", help="git revision for historical source copies, such as bb9fe48"
    )
    args = parser.parse_args()
    root = args.root / "task12"
    root.mkdir(parents=True, exist_ok=True)
    home = root / "home"
    home.mkdir(exist_ok=True)
    env = {
        **os.environ,
        "HOME": str(home),
        "XDG_CONFIG_HOME": str(home / "xdg"),
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_ATTR_NOSYSTEM": "1",
        "GIT_OPTIONAL_LOCKS": "0",
    }
    for size in ["s90000"] if args.production_only else ["s900", "s9000", "s90000"]:
        prepare_store(args.root / size, root / size, env)
    branches = ["b1900"] if args.production_only else ["a1500", "a1900", "b1500", "b1900"]
    for branch in branches:
        dest = root / ("source-" + branch)
        if dest.exists():
            shutil.rmtree(dest)
        if args.source_ref:
            # git writes only into the benchmark directory, never another checkout.
            files = subprocess.check_output(
                ["git", "ls-tree", "-r", "--name-only", args.source_ref, "--", "src/lodge"],
                cwd=args.workspace,
                text=True,
            ).splitlines()
            for name in files:
                target = dest / Path(name).relative_to("src")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(
                    subprocess.check_output(
                        ["git", "show", args.source_ref + ":" + name], cwd=args.workspace
                    )
                )
        else:
            shutil.copytree(
                args.workspace / "src/lodge",
                dest / "lodge",
                ignore=shutil.ignore_patterns("__pycache__"),
            )
        identity = dest / "lodge/gitstore/identity.py"
        text = identity.read_text()
        if "return None" in text.split("class CheckoutIdentity:", 1)[0]:
            if branch.startswith("b"):
                old = "    return None"
                prefix, rest = text.split("class CheckoutIdentity:", 1)
                assert prefix.count(old) == 1
                identity.write_text(
                    prefix.replace(old, "    return identity.stat_current(rev, trunk)")
                    + "class CheckoutIdentity:"
                    + rest
                )
        elif branch.startswith("a"):
            raise SystemExit(
                "R11-A requires --source-ref bb9fe48; current production has removed that branch"
            )
        space = dest / "lodge/gitstore/index_space.py"
        text = space.read_text()
        old = next(line for line in text.splitlines() if line.startswith("INDEX_BYTES_PER_FILE ="))
        space.write_text(
            text.replace(
                old, "INDEX_BYTES_PER_FILE = " + ("1_900" if branch.endswith("1900") else "1_500")
            )
        )
        compileall.compile_dir(dest, quiet=2)
        print("compiled", branch, flush=True)
    for name in ["venv", "venv-base"]:
        compileall.compile_dir(args.root / name, quiet=2)
    (root / "conversions.config").write_text("[core]\n autocrlf = input\n")
    print("setup complete", flush=True)


if __name__ == "__main__":
    main()
