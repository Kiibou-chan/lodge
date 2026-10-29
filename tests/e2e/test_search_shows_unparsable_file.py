from e2e.conftest import Project
from e2e.support import seed

BROKEN = "lodge/decisions/d-zzzzzz-broken.md"


def test_search_shows_unparsable_file(project: Project) -> None:
    seed(project)
    (project.root / BROKEN).write_text("---\ntitle: [unclosed\n---\n", encoding="utf-8")
    result = project.run("search", "transcripts")
    assert result.code == 0
    lines = result.out.splitlines()
    assert lines[0].startswith(f"problem: {BROKEN}:2: ")
    assert lines[1].startswith("d-")
