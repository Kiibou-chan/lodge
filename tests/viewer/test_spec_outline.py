from builders import entry

from viewer.test_pages_threads import A, B, C, specification


def test_each_area_folds_and_starts_open() -> None:
    text = specification(entry(id=A), entry(id=B))
    assert '<details class="area" id="area-storage" open><summary>' in text
    assert text.index('id="area-storage"') < text.index("/r/" + A)


def test_outline_lists_areas_and_entries_in_reading_order() -> None:
    text = specification(entry(id=A), entry(id=B), entry(id=C, rests_on=(A,)))
    outline = text.split('<nav class="outline">')[1].split("</nav>")[0]
    assert '<a href="#area-storage">Storage</a>' in outline and "3 entries" in outline
    assert outline.index("#" + A) < outline.index("#" + C) < outline.index("#" + B)


def test_outline_follows_the_written_order() -> None:
    text = specification(entry(id=A), entry(id=B), entry(id=C, rests_on=(A,)), written=True)
    outline = text.split('<nav class="outline">')[1].split("</nav>")[0]
    assert outline.index("#" + A) < outline.index("#" + B) < outline.index("#" + C)


def test_outline_targets_exist_in_both_orders() -> None:
    for written in (False, True):
        text = specification(entry(id=A), entry(id=B, rests_on=(A,)), written=written)
        assert f'id="{A}"' in text and f'id="{B}"' in text
