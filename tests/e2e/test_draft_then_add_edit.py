from e2e.conftest import Project
from e2e.support import decision_text, seed


def test_draft_then_add_edit(project: Project) -> None:
    ids = seed(project)
    drafted = project.run("draft", ids.entry)
    assert drafted.code == 0
    assert drafted.out.startswith("---\nbase: ")
    assert f"id: {ids.entry}" in drafted.out
    edited = drafted.out.replace("Held.", "Held, whole.")
    decision = decision_text(
        "Keep them whole",
        "changes:",
        f"  - {{entry: {ids.entry}, action: edit}}",
        body="Entries say so.",
    )
    added = project.run(
        "add", project.draft("decision.md", decision), project.draft("entry.md", edited)
    )
    assert added.code == 0, added
    assert added.out.splitlines()[-1].startswith("staged d-")
    assert "Held, whole." in project.run("show", ids.entry).out


def test_draft_of_an_area(project: Project) -> None:
    seed(project)
    drafted = project.run("draft", "area:storage")
    assert drafted.out.startswith("---\nname: storage\nbase: ")


def test_draft_of_an_unknown_record(project: Project) -> None:
    seed(project)
    result = project.run("draft", "s-zzzzzz")
    assert (result.code, result.err) == (2, "lodge: no record named s-zzzzzz\n")


def test_draft_text_is_printed_without_an_extra_newline(project: Project) -> None:
    ids = seed(project)
    path = next((project.root / "lodge" / "spec" / "storage").glob(f"{ids.entry}-*.md"))
    on_disk = path.read_text(encoding="utf-8")
    assert project.run("draft", ids.entry).out.count("\n") == on_disk.count("\n") + 1


def test_draft_of_a_decision_says_decisions_are_immutable(project: Project) -> None:
    ids = seed(project)
    drafted = project.run("draft", ids.decision)
    assert drafted.code == 0 and drafted.out.startswith("---\nbase: ")
    assert drafted.err == (
        "note: decisions are immutable; to change one, "
        "write a new decision with replaces or narrows\n"
    )
    assert project.run("draft", ids.entry).err == ""
    assert "a decision is immutable" in " ".join(project.run("draft", "--help").out.split())
