"""A 300-record harbour fixture, adapted from the benchmark store's builder logic."""

import os
import random
from pathlib import Path

from builders import area, decision, entry, files_of, thread

from e2e.conftest import Project, Result
from lodge.core import Action, Change


def harbour(project: Project) -> list[Path]:
    rng = random.Random(1060)
    entries = [entry(id=f"s-{n:06x}", title=f"Berth {n}") for n in range(128)]
    records = []
    for n in range(170):
        target = entries[n % len(entries)]
        action = Action.CREATE if n < len(entries) else Action.EDIT
        records.append(
            decision(
                id=f"d-{n:06x}",
                title=f"{rng.choice(['Berth', 'Crane', 'Tide'])} schedule",
                statement="A berth has a crane.",
                code=f"CODE-{n}",
                date=f"2026-10-28T{n // 60:02d}:{n % 60:02d}:00+00:00",
                changes=(Change(target.id, action),),
            )
        )
    files = files_of(
        area(order=tuple(e.id for e in entries)),
        *entries,
        *records,
        thread(id="q-aaaaaa", about=entries[0].id),
    )
    assert len(files) == 300
    project.configure('[store]\nmode = "checkout"\n')
    for path, text in files.items():
        destination = project.root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text)
    project.git("add", "-A")
    project.publish_main()
    return sorted(project.root.glob("lodge/decisions/*.md"))


def memory_read(project: Project, args: list[str]) -> Result:
    before = os.environ.get("LODGE_INDEX")
    os.environ["LODGE_INDEX"] = "off"
    try:
        return project.run(*args)
    finally:
        if before is None:
            os.environ.pop("LODGE_INDEX", None)
        else:
            os.environ["LODGE_INDEX"] = before
