"""Several queries share one checked read and omit records already printed."""

from unittest.mock import patch

from builders import decision
from fakes import MemoryStore
from support import wired

from lodge.core import Filters, parse_query


def test_each_record_once_across_queries() -> None:
    a = decision(id="d-aaaaaa", title="berth crane")
    b = decision(id="d-bbbbbb", title="crane")
    result = wired(MemoryStore(a, b)).search_many(
        [parse_query("berth"), parse_query("crane")], Filters()
    )
    assert [[v.id for v in r.items] for r in result] == [[a.id], [b.id]]
    assert [r.query for r in result] == ["berth", "crane"]
    assert result[1].above == (a.id,)
    assert result[0].read is result[1].read


def test_limit_per_query_excludes_earlier_records() -> None:
    records = [decision(id=f"d-{n:06d}", title="berth crane") for n in range(4)]
    result = wired(MemoryStore(*records)).search_many(
        [parse_query("berth"), parse_query("crane")], Filters(), 2
    )
    assert [[v.id for v in r.items] for r in result] == [
        ["d-000003", "d-000002"],
        ["d-000001", "d-000000"],
    ]
    assert result[1].above == ("d-000003", "d-000002")
    assert [r.more for r in result] == [2, 0]


def test_one_read_for_many_queries() -> None:
    store = MemoryStore(decision(title="berth crane"))
    with patch.object(store, "trees", wraps=store.trees) as calls:
        result = wired(store).search_many([parse_query("berth"), parse_query("crane")], Filters())
    assert len(result) == 2
    assert calls.call_count == 1
    empty = wired(store).search_many([], Filters())
    assert len(empty) == 1 and len(empty[0].items) == 1
