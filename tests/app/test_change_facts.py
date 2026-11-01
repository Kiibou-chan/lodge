"""Published check facts are reused and still produce the gate's advice."""

import importlib
from unittest.mock import patch

import pytest
from builders import area, entry
from fakes import CountingIds, FixedClock, MemoryStore
from support import wired

from lodge import core
from lodge.app import Gate, state
from lodge.app.state import Wiring, read_checked
from lodge.cli import run
from lodge.core import CoreSettings, Snapshot


def test_derive_once_per_checked_read(monkeypatch: pytest.MonkeyPatch) -> None:
    spec = entry()
    store = MemoryStore(area(order=(spec.id,)), spec, staged=True)
    original = core.derive
    calls: dict[int, int] = {}

    def counted(snapshot: Snapshot) -> core.Derived:
        calls[id(snapshot)] = calls.get(id(snapshot), 0) + 1
        return original(snapshot)

    for name in (
        "lodge.core",
        "lodge.core.check_change",
        "lodge.core.check_state",
        "lodge.core.check_areas",
        "lodge.core.check_entries",
    ):
        module = importlib.import_module(name)
        if hasattr(module, "derive"):
            monkeypatch.setattr(module, "derive", counted)
    read_checked(Wiring(store, FixedClock(), CountingIds(), CoreSettings()))
    assert sum(calls.values()) == 1
    assert sorted(calls.values()) == [1]


def test_gate_reuses_published_facts(monkeypatch: pytest.MonkeyPatch) -> None:
    spec = entry()
    store = MemoryStore(area(order=(spec.id,)), spec, staged=True)
    current, published = store.trees()
    store.files["lodge/spec/storage/_area.md"] += "\n"
    current = core.Tree(current.rev, dict(store.files))
    monkeypatch.setattr(store, "trees", lambda: (current, published))
    store.gate_for = Gate(published, (("", current),))
    with (
        patch.object(state, "load", wraps=core.load) as loads,
        patch.object(core, "derive", wraps=core.derive) as derives,
        patch.object(core, "check_state", wraps=core.check_state) as checks,
    ):
        assert wired(store).check(gate=True)[0].ok
    assert loads.call_count == 2
    assert derives.call_count == 2
    assert checks.call_count == 2


def test_gate_prints_already_published_note(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    module = importlib.import_module("lodge.core.check_change")
    original = module.sort_key
    monkeypatch.setattr(module, "sort_key", lambda p: (*original(p)[:2], original(p)[2] + " [key]"))
    spec = entry(id="s-aaaaaa")
    store = MemoryStore(area(), spec, staged=True)
    store.files["lodge/spec/storage/_area.md"] += "\n"
    assert run(["check", "--gate"], lambda: wired(store), lambda: "", lambda *_: 0, lambda: 0) == 0
    captured = capsys.readouterr()
    assert "note: already published, check 7:" in captured.out
    assert "s-aaaaaa: is not listed in the order of area storage" in captured.out
    assert not captured.err
