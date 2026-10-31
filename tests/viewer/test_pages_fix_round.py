from dataclasses import replace

import pytest
from builders import area, entry, snapshot_of
from fakes import MemoryStore
from support import wired

from lodge.core import Raises, SpecEntry, derive, rests_on_tree
from lodge.viewer import pages, spec
from viewer.test_post_gate import TOKEN
from viewer.world import staged_world


def chain(count: int, shared: bool = False) -> tuple[SpecEntry, ...]:
    ids = tuple(f"s-{n:06d}" for n in range(count))
    return tuple(
        entry(id=ident, rests_on=ids[max(0, n - (2 if shared else 1)) : n])
        for n, ident in enumerate(ids)
    )


def test_rests_on_tree_expands_a_shared_dependency_once() -> None:
    root, shared, left, right, tip = (f"s-{n:06d}" for n in range(5))
    s = snapshot_of(
        entry(id=root),
        entry(id=shared, rests_on=(root,)),
        entry(id=left, rests_on=(shared,)),
        entry(id=right, rests_on=(shared,)),
        entry(id=tip, rests_on=(left, right)),
    )
    tree = rests_on_tree(s, derive(s), tip)
    assert tree[0].children[0].children
    assert tree[1].children[0].children == ()


def test_shared_dependency_page_stays_small() -> None:
    lodge = wired(MemoryStore(*chain(26, shared=True)))
    text = pages.record_page(lodge.show("s-000025"), TOKEN)
    assert len(text) < 20000
    assert text.count("see above") == 24


def test_empty_dependency_lists() -> None:
    text = pages.record_page(wired(MemoryStore(entry(id="s-aaaaaa"))).show("s-aaaaaa"), TOKEN)
    assert "<h2>Rests on</h2><p>Nothing.</p>" in text
    assert "<h2>Rests on it</h2><p>Nothing.</p>" in text
    assert pages._branches(()) == ""


def test_spec_depth_cap_and_under_links() -> None:
    lodge = wired(MemoryStore(area(), *chain(9)))
    _, read, areas = lodge.spec()
    text = spec.spec_page(areas, read, TOKEN, "dependency", None, ())
    for n in range(9):
        section = text.split('<div class="depth-')[n + 1].split("</div>")[0]
        assert section.startswith(f'{min(n, 5)}">')
        if n > 5:
            assert f'also rests on <a href="/r/s-{n - 1:06d}">' in section
        else:
            assert "also rests on" not in section


def test_dependency_link_keeps_area() -> None:
    lodge = wired(MemoryStore(area(), entry()))
    _, read, areas = lodge.spec("storage")
    text = spec.spec_page(areas, read, TOKEN, "written", "storage", ())
    assert '<a href="/spec?area=storage">By dependency</a>' in text


@pytest.mark.parametrize("field", ["by", "where", "entry_title", "area_title"])
def test_record_values_are_escaped(field: str) -> None:
    value = "<b>synthetic</b>"
    make, _ = staged_world()
    lodge = make()
    lodge.ask("s-aaaaaa", Raises.QUESTION, "author", "Why?", where="viewer")
    shown = lodge.show("s-aaaaaa")
    thread = shown.threads[0]
    if field in {"by", "where"}:
        message = replace(thread.messages[0], **{field: value})
        shown = replace(shown, threads=(replace(thread, messages=(message,)),))
        text = pages.record_page(shown, TOKEN)
    elif field == "entry_title":
        listed, waiting = lodge.waiting_all()
        waiting = replace(waiting, titles={"s-aaaaaa": value})
        text = pages.waiting_page(listed, waiting)
    else:
        _, read, areas = lodge.spec()
        text = spec.spec_page(
            (replace(areas[0], title=value),), read, TOKEN, "dependency", None, ()
        )
    assert value not in text
    assert "&lt;b&gt;synthetic&lt;/b&gt;" in text
