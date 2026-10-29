from e2e.conftest import Project
from e2e.support import QUOTE, seed


def test_show_levels(project: Project) -> None:
    ids = seed(project, QUOTE, decided_by="author")
    level1 = project.run("show", ids.decision)
    assert level1.code == 0
    assert level1.out.startswith(f"{ids.decision} ITEM-1 · current · author")
    assert 'quote: "Keep them."' in level1.out
    assert "## Reasoning" not in level1.out and "## Provenance" not in level1.out
    reasoning = project.run("show", ids.decision, "--reasoning")
    assert reasoning.out.startswith(level1.out.rstrip("\n"))
    assert "\n## Reasoning\n" in reasoning.out and "## Provenance" not in reasoning.out
    provenance = project.run("show", "ITEM-1", "--provenance")
    assert "\n## Provenance\n" in provenance.out
    assert f"changes (create): {ids.entry} (current)" in provenance.out
    both = project.run("show", ids.decision.upper(), "--provenance", "--reasoning")
    assert both.out.index("## Reasoning") < both.out.index("## Provenance")


def test_show_entry_reasoning_lists_its_decisions(project: Project) -> None:
    ids = seed(project)
    shown = project.run("show", ids.entry, "--reasoning").out
    assert shown.index("## Reasoning") < shown.index(ids.decision)


def test_show_unknown_record(project: Project) -> None:
    seed(project)
    result = project.run("show", "d-zzzzzz")
    assert (result.code, result.out) == (2, "")
    assert result.err == "lodge: no record named d-zzzzzz\n"
