from e2e.conftest import Project
from e2e.support import QUOTE, seed


def test_search(project: Project) -> None:
    ids = seed(project)
    result = project.run("search", "transcripts")
    assert (result.code, result.err) == (0, "")
    lines = result.out.splitlines()
    assert lines[0].startswith(f"{ids.decision} ITEM-1 · current · coordinator")
    assert lines[1:4] == ["Keep transcripts", "", "Transcripts are kept."]
    assert lines[4] == ""
    assert lines[5].startswith(f"{ids.entry} · current · coordinator")
    assert lines[6:] == ["Transcripts are kept", "", "Held."]


def test_search_by_code_and_filters(project: Project) -> None:
    seed(project)
    assert project.run("search", "item-1").out.startswith("d-")
    only_spec = project.run("search", "transcripts", "--kind", "spec").out
    assert only_spec.startswith("s-") and "d-" not in only_spec.split("\n")[0]
    assert project.run("search", "transcripts", "--scope", "process").out == "no matches\n"
    assert "d-" in project.run("search", "--by", "coordinator", "--kind", "decision").out
    assert project.run("search", "transcripts", "--area", "storage", "--status", "any").code == 0


def test_search_without_hits(project: Project) -> None:
    seed(project)
    result = project.run("search", "zebra")
    assert (result.code, result.out) == (0, "no matches\n")


def test_search_bad_filter_is_a_usage_error(project: Project) -> None:
    seed(project)
    result = project.run("search", "x", "--status", "gone")
    assert result.code == 2 and "invalid choice" in result.err


def test_search_shows_quote_of_author_decision(project: Project) -> None:
    seed(project, QUOTE, decided_by="author")
    assert 'quote: "Keep them." (chat, 2026-10-29 10:00)' in project.run("search", "keep").out
