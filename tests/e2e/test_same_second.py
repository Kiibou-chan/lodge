from e2e.conftest import Project, StuckClock
from e2e.support import QUOTE, decision_text, first_decision, seed

BRANCH = '[store]\nmode = "branch"\n'


def agent_edit(project: Project, entry: str) -> str:
    """The chain a script runs: draft, change the text, add an agent decision editing it."""
    edited = project.run("draft", entry).out.replace("Held.", "Held, whole.")
    decision = decision_text(
        "Keep them whole", "changes:", f"  - {{entry: {entry}, action: edit}}", body="Say so."
    )
    added = project.run(
        "add", project.draft("decision.md", decision), project.draft("entry.md", edited)
    )
    assert (added.code, added.err) == (0, ""), added
    return first_decision(added.out)


def test_agent_edit_in_the_same_second_is_flagged(
    project: Project, stuck_clock: StuckClock
) -> None:
    ids = seed(project, QUOTE, decided_by="author")
    flagged = agent_edit(project, ids.entry)
    assert stuck_clock.slept == [0.75]
    waiting = project.run("waiting")
    assert waiting.out.startswith(f"{flagged} · current · coordinator")
    shown = project.run("show", ids.entry).out.splitlines()[0]
    assert "coordinator" in shown and "awaiting the author" in shown
    assert project.run("check", "--gate").code == 0


def test_agent_edit_in_the_same_second_publishes_in_branch_mode(
    project: Project, stuck_clock: StuckClock
) -> None:
    project.configure(BRANCH)
    ids = seed(project, QUOTE, decided_by="author")
    flagged = agent_edit(project, ids.entry)
    assert stuck_clock.slept == [0.75]
    tree = project.git("--git-dir", str(project.remote), "ls-tree", "-r", "--name-only", "lodge")
    assert any(line.startswith(f"lodge/decisions/{flagged}-") for line in tree.splitlines())
    assert project.run("waiting").out.splitlines()[1].startswith(f"{flagged} ·")
    gated = project.run("check", "--gate").out.splitlines()
    assert "ok" in gated and gated[-1].startswith("note: in branch mode the gate runs inside")
