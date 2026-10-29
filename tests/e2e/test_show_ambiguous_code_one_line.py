from e2e.conftest import Project
from e2e.support import seed

TWIN = """---
id: {id}
kind: decision
code: item-1
title: Another
scope: product
decided_by: coordinator
date: 2026-10-29T12:00:00+01:00
---

Another statement.
"""


def test_show_ambiguous_code_one_line(project: Project) -> None:
    first = seed(project)
    other = project.run("id", "d").out.strip()
    twin = project.root / "lodge" / "decisions" / f"{other}-another.md"
    twin.write_text(TWIN.format(id=other), encoding="utf-8")
    result = project.run("show", "ITEM-1")
    assert result.code == 2 and result.out == ""
    assert result.err.count("\n") == 1
    assert result.err.startswith("lodge: the code ITEM-1 names more than one record: ")
    assert first.decision in result.err and other in result.err
