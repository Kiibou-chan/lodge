"""Review regressions for build naming, partial hits, pruning, and factory lifetime."""

import sqlite3
from pathlib import Path

import pytest
import yaml

from gitstore.index_helpers import KEY, filename, opened
from gitstore.test_index_db import old_file
from lodge.core import CoreSettings
from lodge.gitstore import index_db, index_space
from lodge.gitstore.index_db import IndexDB


def test_orphan_does_not_abort_pruning(tmp_path: Path) -> None:
    index = opened(tmp_path)
    folder = filename(tmp_path).parent
    orphan = old_file(folder, "f" * 16, 8)
    orphan.with_suffix(".lock").unlink()
    old = old_file(folder, "a" * 16, 8)
    index_space.prune(folder, filename(tmp_path))
    assert not orphan.exists() and not old.exists()
    assert orphan.with_suffix(".lock").exists()
    index.close()


def test_digest_includes_libyaml_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    if not yaml.__with_libyaml__:
        pytest.skip("libyaml unavailable")
    before = index_db.build_digest(tmp_path)
    monkeypatch.setattr(yaml._yaml, "get_version_string", lambda: "new-libyaml")
    assert index_db.build_digest(tmp_path) != before


class OneBadKey(sqlite3.Connection):
    def execute(self, sql: str, parameters: object = (), /) -> sqlite3.Cursor:
        if sql.startswith("SELECT value") and parameters == ("bad", "blob"):
            raise sqlite3.DatabaseError("injected bad page")
        return super().execute(sql, parameters)  # type: ignore[arg-type]


def test_lookup_keeps_partial_hits(tmp_path: Path) -> None:
    initial = opened(tmp_path)
    initial.keep_parses({KEY: None, ("last", "blob"): None})
    initial.close()
    db = sqlite3.connect(filename(tmp_path), isolation_level=None, factory=OneBadKey)
    index = IndexDB(db, None)
    assert index.parses([KEY, ("bad", "blob"), ("last", "blob")]) == {
        KEY: None,
        ("last", "blob"): None,
    }
    index.close()


def test_parse_only_module_has_no_settings_key() -> None:
    assert not hasattr(index_db, "settings_key")


def test_project_index_skips_open_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def broken(*args: object) -> None:
        raise RuntimeError("injected opening failure")

    monkeypatch.setattr(index_db, "open_index", broken)
    assert index_db.project_index(tmp_path) is None


def test_parse_only_opening_needs_no_settings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[Path] = []

    def opened(common: Path) -> None:
        calls.append(common)

    def forbidden(settings: CoreSettings) -> str:
        raise AssertionError("parse-only opening computed a settings digest")

    monkeypatch.setattr(index_db, "open_index", opened)
    monkeypatch.setattr(index_db, "settings_key", forbidden, raising=False)
    assert index_db.project_index(tmp_path) is None
    assert calls == [tmp_path]
