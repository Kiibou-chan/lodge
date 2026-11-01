"""Parse units are content addressed by both their path and their bytes."""

from pathlib import Path

import pytest

from gitstore.index_helpers import KEY, opened
from lodge.core import Area, parse_file
from lodge.gitstore import index_db


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


def test_unencodable_key_skips_only_that_unit(tmp_path: Path) -> None:
    index = opened(tmp_path)
    bad = ("lodge/decisions/stray-\udcff.md", "blob")
    index.keep_parses({bad: None, KEY: None, ("last", "blob"): None})
    assert index.parses([bad, KEY, ("last", "blob")]) == {KEY: None, ("last", "blob"): None}
    index.close()


@pytest.mark.parametrize("method", ["parses", "keep_parses", "epoch"])
def test_any_adapter_exception_is_a_miss(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, method: str
) -> None:
    index = opened(tmp_path)

    def fail(*args: object, **kwargs: object) -> None:
        raise RuntimeError("injected adapter failure")

    monkeypatch.setattr(index_db, "transaction", fail)
    if method == "parses":
        assert index.parses([KEY]) == {}
    elif method == "keep_parses":
        index.keep_parses({KEY: None})
    else:
        assert index.epoch() == 0
    index.close()
