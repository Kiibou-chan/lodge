from e2e.conftest import Project
from e2e.support import seed


def test_gate_fails_for_a_partial_commit(project: Project) -> None:
    seed(project)
    project.git("commit", "-m", "Spec only", "--", "lodge/spec")
    gate = project.run("check", "--gate")
    assert gate.code == 1
    lines = gate.out.splitlines()
    assert lines[0].startswith("check 4: committed: s-") and "no new decision" in lines[0]
    assert "note: uncommitted record changes in lodge/; commit them before you push" in lines


def test_gate_names_the_working_tree_when_only_it_fails(project: Project) -> None:
    ids = seed(project)
    project.publish_main()
    path = next((project.root / "lodge" / "decisions").glob(f"{ids.decision}-*.md"))
    path.write_text(path.read_text(encoding="utf-8").replace("are kept", "are dropped"))
    gate = project.run("check", "--gate")
    assert gate.code == 1
    lines = gate.out.splitlines()
    assert lines[0].startswith("check 5: working tree: ") and ids.decision in lines[0]
    assert lines[-1].startswith("note: uncommitted record changes")


def test_gate_without_a_base_exits_2(project: Project) -> None:
    seed(project)
    project.configure('[store]\nbase = "trunk"\n')
    gate = project.run("check", "--gate")
    assert (gate.code, gate.out) == (2, "")
    assert "origin/trunk" in gate.err and "base" in gate.err and gate.err.count("\n") == 1
    shown = project.run("search", "transcripts")
    assert shown.code == 0 and "origin/trunk" in shown.out.splitlines()[0]
