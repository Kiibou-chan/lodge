from e2e.conftest import Project
from e2e.support import QUOTE, decision_text, first_decision, seed


def test_waiting(project: Project) -> None:
    ids = seed(project, QUOTE, decided_by="author")
    assert (
        project.run("waiting").out
        == "waiting for an agent\nnothing\n\nwaiting for the author\nnothing\n"
    )
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
    assert f"waiting for the author\n{flagged} · current · coordinator" in waiting.out
    assert "awaiting the author" in waiting.out.split("waiting for the author\n")[1].splitlines()[0]
    assert ids.decision not in waiting.out
    thread = project.run(
        "ask",
        ids.entry,
        "--kind",
        "question",
        "--by",
        "reviewer",
        project.draft("thread.txt", "Why?"),
    ).out.split()[-1]
    out = project.run("waiting").out
    assert out.index("waiting for an agent") < out.index("waiting for the author")
    first, second = out.split("waiting for the author")
    assert flagged not in first and thread not in first
    assert second.index(flagged) < second.index(thread)


def test_waiting_groups_threads(project: Project) -> None:
    entry = seed(project).entry
    author = project.run(
        "ask",
        entry,
        "--kind",
        "question",
        "--by",
        "author",
        "--where",
        "chat",
        "--when",
        "2026-10-31 12:00",
        project.draft("author.txt", "Why?"),
    )
    agent = project.run(
        "ask",
        entry,
        "--kind",
        "doubt",
        "--by",
        "reviewer",
        project.draft("agent.txt", "Check storage."),
    )
    assert author.code == agent.code == 0
    out = project.run("waiting").out
    assert out.index("waiting for an agent") < out.index("waiting for the author")
    first, second = out.split("waiting for the author")
    assert author.out.split()[-1] in first and agent.out.split()[-1] not in first
    assert agent.out.split()[-1] in second and author.out.split()[-1] not in second
