"""Review regressions for exact readers and ID-shaped record codes."""

from dataclasses import replace
from unittest.mock import patch

import pytest
from builders import decision

from e2e.conftest import Project
from e2e.test_indexed_reads import prepared
from lodge.core import Decision, parse_file, write_record
from lodge.gitstore.index_db import IndexDB, open_index


@pytest.mark.parametrize("args", [("spec",), ("check",), ("check", "--gate"), ("add",)])
def test_exact_hit_over_cap_writes_nothing(project: Project, args: tuple[str, ...]) -> None:
    prepared(project)
    if args == ("add",):
        draft = project.draft(
            "decision.md",
            (
                "---\nkind: decision\ntitle: Synthetic change\nscope: product\n"
                "decided_by: coordinator\n---\n\nBerths hold cranes.\n"
            ),
        )
        args = ("add", draft, "--dry-run")
    index = open_index(project.root / ".git")
    assert isinstance(index, IndexDB)

    def contents() -> list[list[tuple[object, ...]]]:
        return [
            index.db.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall()
            for table in ("meta", "states", "facts", "seen")
        ]

    before = contents()
    assert before[1] and before[2] and before[3]
    statements: list[str] = []
    original = IndexDB.keep_parses

    def traced(self: IndexDB, *a: object, **kw: object) -> None:
        self.db.set_trace_callback(statements.append)
        original(self, *a, **kw)  # type: ignore[arg-type]

    with (
        patch("lodge.gitstore.index_space.index_file_cap", return_value=0),
        patch.object(IndexDB, "keep_parses", traced),
    ):
        result = project.run(*args)
    assert result.code == 0
    assert "BEGIN IMMEDIATE" not in statements
    assert contents() == before
    index.close()


@pytest.mark.parametrize("code", ["d-fast", "S-ab"])
@pytest.mark.parametrize("ambiguous", [False, True])
def test_stored_id_shaped_code_prints_as_memory(
    project: Project, monkeypatch: pytest.MonkeyPatch, code: str, ambiguous: bool
) -> None:
    path = prepared(project)
    record = parse_file(str(path.relative_to(project.root)), path.read_text())
    assert isinstance(record, Decision)
    path.write_text(write_record(replace(record, code=code)))
    if ambiguous:
        other = path.parent / "d-bbbbbb-other.md"
        other.write_text(write_record(decision(id="d-bbbbbb", code=code)))
    project.git("add", "lodge")
    project.publish_main()
    for _ in range(2):
        project.run("waiting")
    index = open_index(project.root / ".git")
    assert isinstance(index, IndexDB)
    assert index.db.execute("SELECT count(*) FROM states").fetchone()[0] >= 2
    index.close()
    actual = project.run("show", code)
    monkeypatch.setenv("LODGE_INDEX", "off")
    expected = project.run("show", code)
    assert expected.code == (2 if ambiguous else 0), expected
    assert code in expected.out or "more than one record" in expected.err, expected
    assert actual == expected
