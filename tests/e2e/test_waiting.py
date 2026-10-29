from e2e.conftest import Project
from e2e.support import QUOTE, decision_text, first_decision, seed


def test_waiting(project: Project) -> None:
    ids = seed(project, QUOTE, decided_by="author")
    assert project.run("waiting").out == "nothing waits for the author\n"
    edited = project.run("draft", ids.entry).out.replace("Held.", "Held, whole.")
    agent = decision_text(
        "Keep them whole", "changes:", f"  - {{entry: {ids.entry}, action: edit}}", body="Say so."
    )
    added = project.run(
        "add", project.draft("decision.md", agent), project.draft("entry.md", edited)
    )
    assert added.code == 0, added
    flagged = first_decision(added.out)
    waiting = project.run("waiting")
    assert (waiting.code, waiting.err) == (0, "")
    assert waiting.out.startswith(f"{flagged} · current · coordinator")
    assert "awaiting the author" in waiting.out.splitlines()[0]
    assert ids.decision not in waiting.out
