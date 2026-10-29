from e2e.conftest import Project
from e2e.support import initialise

OLD = """---
kind: decision
title: "Keep old transcripts"
scope: product
decided_by: author
date: 2026-01-05
imported_from: {file: docs/choices.md, heading: "ITEM-9"}
---

Old transcripts are kept.
"""


def test_import_needs_the_flag_and_a_listed_source(project: Project) -> None:
    project.configure('[import]\nsources = ["docs/choices.md"]\n')
    initialise(project)
    path = project.draft("old.md", OLD)
    refused = project.run("add", path)
    assert refused.code == 2 and "imported_from" in refused.err
    added = project.run("add", "--import", path)
    assert (added.code, added.err) == (0, "")
    assert added.out.splitlines()[-1].startswith("staged d-")
    shown = project.run("show", added.out.split()[-1])
    assert "imported" in shown.out and "unquoted" in shown.out


def test_import_from_an_unlisted_source_fails_the_check(project: Project) -> None:
    initialise(project)
    result = project.run("add", "--import", project.draft("old.md", OLD))
    assert result.code == 1
    assert result.out.splitlines()[-1] == "not published: the check failed"
