from e2e.conftest import Project
from e2e.support import seed


def test_check_and_gate(project: Project) -> None:
    ids = seed(project)
    clean = project.run("check")
    assert (clean.code, clean.out, clean.err) == (0, "ok\n", "")
    project.publish_main()
    path = next((project.root / "lodge" / "decisions").glob(f"{ids.decision}-*.md"))
    path.write_text(path.read_text(encoding="utf-8").replace("are kept", "are dropped"))
    assert project.run("check").out == "ok\n"
    gate = project.run("check", "--gate")
    assert (gate.code, gate.err) == (1, "")
    lines = gate.out.splitlines()
    assert lines[0].startswith("check 5: ") and ids.decision in lines[0]
    assert "ok" not in lines


def test_gate_passes_with_notes_for_new_records(project: Project) -> None:
    seed(project)
    gate = project.run("check", "--gate")
    assert gate.code == 0
    assert gate.out.splitlines()[:2] == ["ok", "note: area storage: added"]
    project.publish_main()
    assert project.run("check", "--gate").out == "ok\n"


def test_check_prints_unreadable_files_and_fails(project: Project) -> None:
    seed(project)
    broken = project.root / "lodge" / "decisions" / "d-zzzzzz-broken.md"
    broken.write_text("---\ntitle: [unclosed\n---\n", encoding="utf-8")
    result = project.run("check")
    assert result.code == 1
    lines = result.out.splitlines()
    assert lines[0].startswith("problem: lodge/decisions/d-zzzzzz-broken.md:2: ")
    assert len(lines) == 1
