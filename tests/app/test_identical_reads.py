"""Equal file mappings and attachments reuse the checked state without changing output."""

from dataclasses import replace
from unittest.mock import patch

import pytest
from builders import at, decision, entry, files_of, thread
from fakes import CountingIds, FixedClock, MemoryStore
from support import AREA, ENTRY, FIRST, project, wired

from lodge import core
from lodge.app import Index, Store, state
from lodge.app.state import State, Wiring, read_checked
from lodge.cli import run


@pytest.mark.parametrize("staged", [False, True])
@pytest.mark.parametrize("different_revision", [False, True])
def test_identical_trees_load_once(
    monkeypatch: pytest.MonkeyPatch, staged: bool, different_revision: bool
) -> None:
    store = project(staged=staged)
    if different_revision:
        current, published = store.trees()
        monkeypatch.setattr(store, "trees", lambda: (current, replace(published, rev="another")))
    with (
        patch.object(state, "load", wraps=core.load) as loads,
        patch.object(core, "derive", wraps=core.derive) as derives,
        patch.object(core, "check_change", wraps=core.check_change) as changes,
    ):
        checked = read_checked(Wiring(store, FixedClock(), CountingIds(), core.CoreSettings()))
    assert checked.result.ok
    assert loads.call_count == 1
    assert derives.call_count == 1
    assert changes.call_count == 0


@pytest.mark.parametrize(
    "difference", ["bytes", "added", "removed", "attachment-added", "attachment-removed"]
)
def test_different_trees_keep_change_check(
    monkeypatch: pytest.MonkeyPatch, difference: str
) -> None:
    store = project(staged=True)
    current, published = store.trees()
    files = dict(current.files)
    path = next(p for p in files if FIRST.id in p)
    if difference == "bytes":
        files[path] += "\n"
    elif difference == "added":
        files["lodge/notes.txt"] = "A stray file."
    elif difference == "removed":
        del files[path]
    attachments = frozenset({"lodge/attachments/d-aaaaaa/probe.txt"})
    current = replace(
        current,
        files=files,
        attachments=attachments if difference == "attachment-added" else frozenset(),
    )
    if difference == "attachment-removed":
        published = replace(published, attachments=attachments)
    monkeypatch.setattr(store, "trees", lambda: (current, published))
    with (
        patch.object(state, "load", wraps=core.load) as loads,
        patch.object(core, "check_change", wraps=core.check_change) as changes,
    ):
        checked = read_checked(Wiring(store, FixedClock(), CountingIds(), core.CoreSettings()))
    assert loads.call_count == 2
    assert changes.call_count == 1
    if difference == "removed":
        assert any(p.check == 2 and "missing" in p.message for p in checked.result.problems)


class UnequalFiles(dict[str, str]):
    """Force the existing comparison path without changing any input to the parser."""

    def __eq__(self, other: object) -> bool:
        return False

    def __ne__(self, other: object) -> bool:
        return True


def sample_store(sample: str) -> MemoryStore:
    store = project(staged=True)
    if sample == "broken":
        store.files["lodge/decisions/d-bbbbbb-broken.md"] = "---\ninvalid\n"
        store.files.update(files_of(replace(FIRST, title="Duplicate")))
    elif sample == "cycle":
        other = entry(id="s-bbbbbb", rests_on=(ENTRY.id,))
        store.files.update(
            files_of(
                replace(ENTRY, rests_on=(other.id,)),
                other,
                replace(AREA, order=(ENTRY.id, other.id)),
            )
        )
    elif sample == "history":
        later = decision(
            id="d-bbbbbb", decided_by="author", quote=None, date=at(10), replaces=(FIRST.id,)
        )
        store.files.update(files_of(later, thread(about=ENTRY.id)))
        path = next(p for p in store.files if FIRST.id in p)
        store.files[path] = store.files[path].replace(FIRST.statement, "A published hand edit.")
    store.published = dict(store.files)
    return store


@pytest.mark.parametrize("sample", ["clean", "broken", "cycle", "history"])
@pytest.mark.parametrize(
    "command",
    [
        ["show", "s-aaaaaa", "--reasoning", "--provenance"],
        ["search", "transcripts"],
        ["waiting"],
        ["check"],
        ["check", "--gate"],
    ],
)
def test_identical_read_output_unchanged(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    sample: str,
    command: list[str],
) -> None:
    store = sample_store(sample)
    original = state.read_state

    def shortcut_disabled(store: Store, index: Index | None = None) -> State:
        checked = original(store, index)
        published = replace(checked.published, files=UnequalFiles(checked.published.files))
        return replace(checked, published=published)

    def unused(*args: object) -> int:
        raise AssertionError("this read must not invoke another command")

    with monkeypatch.context() as context:
        context.setattr(state, "read_state", shortcut_disabled)
        with patch.object(core, "check_change", wraps=core.check_change) as changes:
            before = run(command, lambda: wired(store), lambda: "", unused, unused)
        assert changes.call_count >= 1
        before_output = capsys.readouterr()
    with patch.object(core, "check_change", wraps=core.check_change) as changes:
        after = run(command, lambda: wired(store), lambda: "", unused, unused)
    after_output = capsys.readouterr()
    assert (after, after_output) == (before, before_output)
    assert changes.call_count == (1 if "--gate" in command else 0)
