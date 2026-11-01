"""Seeded checkout histories keep every indexed read equal to the exact reader."""

import os
import random

from builders import decision, files_of

from e2e.conftest import Project
from e2e.index_property_support import harbour, memory_read
from lodge.gitstore.index_db import IndexDB, open_index
from lodge.gitstore.index_states import KEPT_STATES


def test_index_reads_equal_memory_under_random_edits(project: Project) -> None:
    seed = 1060
    rng = random.Random(seed)
    paths = harbour(project)
    original = paths[0].read_bytes()
    history = [p.read_bytes() for p in paths[:20]]
    commands = [
        ["show", "CODE-0"],
        ["search", "berth", "tide", "--brief"],
        ["waiting"],
        ["threads"],
        ["thread", "q-aaaaaa"],
        ["search", "--phrase", "berth crane"],
        ["search", "CODE-0"],
    ]
    kinds = [
        "create",
        "edit",
        "delete",
        "untracked",
        "touch",
        "stage",
        "commit",
        "revert",
        "crlf",
        "assume",
        "skip",
    ]
    actions = kinds * 5 + kinds[:5]
    rng.shuffle(actions)
    # Explicitly keep enough distinct states before returning to the original contents.
    actions[: KEPT_STATES + 2] = ["edit"] * (KEPT_STATES + 1) + ["revert"]
    for step, kind in enumerate(actions):
        path = paths[0] if step < KEPT_STATES + 2 else rng.choice(paths[:20])
        if not path.exists():
            path.write_bytes(history[paths.index(path)])
        if kind in {"edit", "stage", "commit", "assume"}:
            if kind == "assume":
                project.git(
                    "update-index", "--assume-unchanged", str(path.relative_to(project.root))
                )
            path.write_text(
                path.read_text().replace(
                    "A berth has a crane.", f"A berth has a crane. Synthetic edit {step}."
                )
            )
            # Keep forced edits distinct after the first replacement too.
            with path.open("a") as handle:
                handle.write(f"\nSynthetic step {step}.\n")
            if kind in {"stage", "commit"}:
                project.git("add", str(path.relative_to(project.root)))
            if kind == "commit":
                project.git("commit", "-m", "Synthetic edit")
        elif kind in {"create", "untracked"}:
            for name, text in files_of(
                decision(id=f"d-{step + 512:06x}", title="Untracked crane")
            ).items():
                (project.root / name).write_text(text)
            if kind == "create":
                project.git("add", "lodge")
        elif kind in {"delete", "skip"}:
            if kind == "skip":
                project.git("update-index", "--skip-worktree", str(path.relative_to(project.root)))
            path.unlink()
        elif kind == "touch":
            stat = path.stat()
            os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 2_000_000_000))
        elif kind == "revert":
            path.write_bytes(original if step == KEPT_STATES + 1 else history[paths.index(path)])
        elif kind == "crlf":
            (project.root / ".gitattributes").write_text("*.md text eol=crlf\n")
            path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        args = commands[step % len(commands)] if step < len(commands) else rng.choice(commands)
        expected = memory_read(project, args)
        # Two sightings populate this state; a third read exercises its stored answer.
        for sighting in range(3):
            assert project.run(*args) == expected, (seed, step, kind, sighting, args)
        project.git(
            "update-index",
            "--no-assume-unchanged",
            "--no-skip-worktree",
            str(path.relative_to(project.root)),
        )
    index = open_index(project.root / ".git")
    assert isinstance(index, IndexDB)
    try:
        assert index.candidates(["berth"], False), seed
        assert index.db.execute("SELECT count(*) FROM states").fetchone()[0] > 0, seed
    finally:
        index.close()
