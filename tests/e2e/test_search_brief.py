from e2e.conftest import Project
from e2e.support import seed


def test_search_brief_gives_one_line_per_record(project: Project) -> None:
    ids = seed(project)
    result = project.run("search", "transcripts", "--brief")
    assert (result.code, result.err) == (0, "")
    lines = result.out.splitlines()
    assert len(lines) == 2
    assert lines[0].startswith(f"{ids.decision} ITEM-1 · current · coordinator")
    assert lines[0].endswith(" · Keep transcripts")
    assert lines[1].startswith(f"{ids.entry} · current · coordinator")
    assert lines[1].endswith(" · Transcripts are kept")
    assert "Held." not in result.out


def test_search_brief_still_says_what_it_left_out(project: Project) -> None:
    seed(project)
    lines = project.run("search", "transcripts", "--brief", "--limit", "1").out.splitlines()
    assert len(lines) == 2
    assert lines[-1] == "1 of 2 shown; narrow the query or give --limit 2"


def test_search_brief_without_hits(project: Project) -> None:
    seed(project)
    assert project.run("search", "zebra", "--brief").out == "no matches\n"
