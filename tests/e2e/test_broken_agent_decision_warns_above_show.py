from e2e.conftest import Project
from e2e.support import QUOTE, decision_text, first_decision, seed


def test_broken_agent_decision_warns_above_show(project: Project) -> None:
    ids = seed(project, QUOTE, decided_by="author")
    edited = project.run("draft", ids.entry).out.replace("Held.", "Held, whole.")
    agent = decision_text(
        "Keep them whole", "changes:", f"  - {{entry: {ids.entry}, action: edit}}", body="Say so."
    )
    added = project.run(
        "add", project.draft("decision.md", agent), project.draft("entry.md", edited)
    )
    flagged = first_decision(added.out)
    path = next((project.root / "lodge" / "decisions").glob(f"{flagged}-*.md"))
    path.write_text("---\ntitle: [unclosed\n---\n", encoding="utf-8")
    lines = project.run("show", ids.entry).out.splitlines()
    assert lines[0].startswith(f"problem: lodge/decisions/{path.name}:2: ")
    assert lines[1].startswith(f"{ids.entry} · current")
    assert 'quote: "Keep them."' in "\n".join(lines)
