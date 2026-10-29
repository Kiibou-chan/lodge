from e2e.conftest import Project
from e2e.support import seed


def test_search_limit_says_what_it_left_out(project: Project) -> None:
    seed(project)
    cut = project.run("search", "transcripts", "--limit", "1")
    assert (cut.code, cut.err) == (0, "")
    assert cut.out.splitlines()[-1] == "1 of 2 shown; narrow the query or give --limit 2"
    whole = project.run("search", "transcripts", "--limit", "2")
    assert " shown;" not in whole.out


def test_search_limit_must_be_a_positive_whole_number(project: Project) -> None:
    seed(project)
    for bad in ("0", "-1", "many"):
        result = project.run("search", "transcripts", "--limit", bad)
        assert result.code == 2 and "is not a positive whole number" in result.err
