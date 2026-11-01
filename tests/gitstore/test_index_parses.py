"""Parse units are content addressed by both their path and their bytes."""

from pathlib import Path

from gitstore.index_helpers import KEY, opened
from lodge.core import Area, parse_file


def test_hit_after_keep(tmp_path: Path) -> None:
    index = opened(tmp_path)
    value = parse_file(KEY[0], "broken")
    assert index.parses([KEY]) == {}
    index.keep_parses({KEY: value, ("lodge/spec/.gitkeep", "empty"): None})
    assert index.parses([KEY, ("lodge/spec/.gitkeep", "empty")]) == {
        KEY: value,
        ("lodge/spec/.gitkeep", "empty"): None,
    }
    index.close()
    again = opened(tmp_path)
    assert again.parses([KEY]) == {KEY: value}
    again.close()


def test_key_is_path_and_blob(tmp_path: Path) -> None:
    index = opened(tmp_path)
    text = "---\nkind: area\ntitle: Berths\norder: []\n---\n\nBerths.\n"
    a = ("lodge/spec/berths/_area.md", "same")
    b = ("lodge/spec/cranes/_area.md", "same")
    first, second = parse_file(a[0], text), parse_file(b[0], text)
    assert isinstance(first, Area) and isinstance(second, Area) and first.name != second.name
    index.keep_parses({a: first, b: second})
    assert index.parses([a, b, (a[0], "other")]) == {a: first, b: second}
    index.close()


def test_undecodable_row_is_a_miss(tmp_path: Path) -> None:
    index = opened(tmp_path)
    index.db.execute("INSERT INTO parses(path,blob,value) VALUES(?,?,?)", (*KEY, b"garbage"))
    assert index.parses([KEY]) == {}
    index.close()
