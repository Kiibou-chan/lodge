import pytest
from builders import area, entry

from lodge.core import Problem, parse_area, parse_record, write_area, write_record


def test_rests_on_round_trips() -> None:
    e = entry(id="s-aaaaaa", rests_on=("s-bbbbbb", "s-cccccc"))
    text = write_record(e)
    assert 'title: "An entry"\nrests_on: [s-bbbbbb, s-cccccc]' in text
    assert parse_record("lodge/spec/storage/a.md", text) == e


def test_rank_round_trips() -> None:
    a = area(rank=0)
    assert 'title: "Storage"\nrank: 0' in write_area(a)
    assert parse_area("lodge/spec/storage/_area.md", write_area(a)) == a


@pytest.mark.parametrize("value", ["2", '"2"'])
def test_rank_reads_quoted_and_plain_alike(value: str) -> None:
    assert parse_area(
        "lodge/spec/storage/_area.md", f"---\nkind: area\ntitle: Storage\nrank: {value}\n---\n"
    ) == area(rank=2)


@pytest.mark.parametrize("value", ["-1", "1.5", "true", "two", "01", '""'])
def test_rank_must_be_a_whole_number(value: str) -> None:
    p = parse_area(
        "lodge/spec/storage/_area.md", f"---\nkind: area\ntitle: Storage\nrank: {value}\n---\n"
    )
    assert isinstance(p, Problem) and p.check == 1 and p.line == 4
    assert "rank" in p.message and "unknown key" not in p.message


def test_rests_on_holds_entry_ids_only() -> None:
    p = parse_record(
        "lodge/spec/storage/a.md",
        "---\nid: s-aaaaaa\nkind: spec\ntitle: Entry\nrests_on: [d-3m8qk2]\n---\n\nHeld.\n",
    )
    assert isinstance(p, Problem) and p.check == 1
    assert "rests_on" in p.message and "not a specification entry id" in p.message


def test_area_without_rank_writes_as_before() -> None:
    assert write_area(area()) == '---\nkind: area\ntitle: "Storage"\n---\n'
