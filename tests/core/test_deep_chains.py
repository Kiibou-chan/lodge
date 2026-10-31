"""Deep reads finish, and small traversals keep the pre-Task-2 order and HTML."""

import importlib

import pytest
from builders import area, entry, snapshot_of
from linear_fixtures import chain
from linear_order_oracle import old_branches, old_derived_order, old_rests_on_tree

from lodge.app import Read, Shown
from lodge.core import check_state, derive, derived_order, level1, render_spec, rests_on_tree
from lodge.viewer import pages


def test_chain_of_5000_checks_shows_and_orders(monkeypatch: pytest.MonkeyPatch) -> None:
    a, b, c, d = (f"s-{n:06x}" for n in range(4))
    diamond = snapshot_of(
        area(order=(d, c, b, a)),
        entry(id=a),
        entry(id=b, rests_on=(a,)),
        entry(id=c, rests_on=(a,)),
        entry(id=d, rests_on=(b, c, b)),
    )
    for snapshot in (chain(30), diamond):
        derived = derive(snapshot)
        last = tuple(snapshot.entries)[-1]
        branches = rests_on_tree(snapshot, derived, last)
        assert branches == old_rests_on_tree(snapshot, derived, last)
        assert derived_order(snapshot, derived, "storage") == old_derived_order(
            snapshot, derived, "storage"
        )
        assert pages._branches(branches) == old_branches(branches)
        shown = Shown(
            level1(snapshot, derived, last, frozenset()),
            None,
            None,
            Read(None, ()),
            rests_on=branches,
        )
        text = render_spec(snapshot, derived, frozenset())
        html = pages.record_page(shown, "token")
        with monkeypatch.context() as patch:
            patch.setattr(
                importlib.import_module("lodge.core.render"), "derived_order", old_derived_order
            )
            patch.setattr(pages, "_branches", old_branches)
            assert render_spec(snapshot, derived, frozenset()) == text
            assert pages.record_page(shown, "token") == html
    assert "(see above)" in old_branches(old_rests_on_tree(diamond, derive(diamond), d))
    snapshot = chain(5000)
    derived = derive(snapshot)
    assert check_state(snapshot).ok
    last = tuple(snapshot.entries)[-1]
    branches = rests_on_tree(snapshot, derived, last)
    depth, pending = 0, branches
    while pending:
        assert len(pending) == 1
        depth += 1
        pending = pending[0].children
    assert depth == 4999
    placed = derived_order(snapshot, derived, "storage")
    assert len(placed) == 5000 and placed[-1].depth == 4999
    assert render_spec(snapshot, derived, frozenset()).count("## An entry") == 5000
    shown = Shown(
        level1(snapshot, derived, last, frozenset()), None, None, Read(None, ()), rests_on=branches
    )
    assert pages.record_page(shown, "token").count("<li>") == 4999
