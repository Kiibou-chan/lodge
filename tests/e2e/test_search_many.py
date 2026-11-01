"""Several queries, phrases, and default brief status through the CLI."""

from e2e.conftest import Project
from e2e.support import decision_text, first_decision, seed


def test_two_queries_with_headers(project: Project) -> None:
    ids = seed(project)
    result = project.run(
        "search", "transcripts", "ITEM-1", "--phrase", "transcripts are", "--brief"
    )
    assert (result.code, result.err) == (0, "")
    assert "query: transcripts · 2 matches\n" in result.out
    assert f"query: ITEM-1 · 1 matches · also {ids.decision} above\n" in result.out
    assert "query: transcripts are · 2 matches" in result.out
    assert result.out.count(" · Keep transcripts\n") == 1
    assert result.out.count(" · Transcripts are kept\n") == 1
    assert result.out.count("records are current unless marked") == 1


def test_phrase_option_is_one_query(project: Project) -> None:
    ids = seed(project)
    result = project.run("search", "--phrase", "transcripts are", "--brief")
    assert result.code == 0 and ids.decision in result.out and ids.entry in result.out
    assert "query:" not in result.out
    repeated = project.run(
        "search", "--phrase", "transcripts are", "--phrase", "are kept", "--brief"
    )
    assert repeated.code == 0 and repeated.out.count("query:") == 2


def test_quoted_words_are_all_words(project: Project) -> None:
    seed(project)
    a = project.draft("both.md", decision_text("Crane berth", body="Held."))
    both = first_decision(project.run("add", a).out)
    b = project.draft("one.md", decision_text("Berth", body="Held."))
    one = first_decision(project.run("add", b).out)
    result = project.run("search", "berth crane", "--brief")
    assert result.code == 0 and result.out.index(both) < result.out.index(one)
    assert "query:" not in result.out
    phrase = project.run("search", "--phrase", "berth crane", "--brief")
    assert phrase.code == 0 and both not in phrase.out


def test_brief_omits_current_and_says_so(project: Project) -> None:
    ids = seed(project)
    result = project.run("search", "transcripts", "--brief")
    assert result.code == 0
    assert result.out.startswith("records are current unless marked\n")
    assert " · current · " not in result.out
    assert ids.decision in result.out
    assert "records are current" not in project.run("search", "transcripts").out


def test_brief_with_status_any_prints_status(project: Project) -> None:
    seed(project)
    result = project.run("search", "transcripts", "ITEM-1", "--brief", "--status", "any")
    assert result.code == 0 and " · current · " in result.out
    assert "records are current unless marked" not in result.out
