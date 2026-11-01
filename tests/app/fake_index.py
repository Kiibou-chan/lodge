"""A state and parse index with the adapter's immutable-unit contract."""

from collections.abc import Collection, Mapping
from contextlib import AbstractContextManager, nullcontext

from lodge.app import FileKey, Row, StateFacts, StoredState
from lodge.core import Parsed, parse_words


class MemoryIndex:
    def __init__(self) -> None:
        self.values: dict[FileKey, Parsed | None] = {}
        self.lookups = 0
        self.epochs = 0
        self.states: dict[str, StoredState] = {}
        self.row_values: dict[str, dict[str, Row]] = {}
        self.citer_values: dict[str, dict[str, tuple[str, ...]]] = {}
        self.answer_values: dict[str, dict[str, object]] = {}
        self.fact_values: dict[str, StateFacts] = {}
        self.markers: dict[str, None] = {}

    def close(self) -> None:
        pass

    def epoch(self) -> int:
        self.epochs += 1
        return 1

    def candidates(
        self, words: Collection[str], every: bool
    ) -> dict[FileKey, tuple[frozenset[str], frozenset[str]]] | None:
        found = {}
        wanted = set(words)
        for key, parsed in self.values.items():
            title, statement = (frozenset(text.split()) for text in parse_words(parsed))
            held = title | statement
            if wanted and (wanted <= held if every else wanted & held):
                found[key] = (title, statement)
        return found

    def parses(self, keys: Collection[FileKey]) -> dict[FileKey, Parsed | None]:
        self.lookups += 1
        return {key: self.values[key] for key in keys if key in self.values}

    def keep_parses(self, parsed: Mapping[FileKey, Parsed | None], *, files: int) -> None:
        for key, value in parsed.items():
            self.values.setdefault(key, value)

    def reading(self) -> AbstractContextManager[None]:
        return nullcontext()

    def state(self, key: str) -> StoredState | None:
        return self.states.get(key)

    def rows(self, key: str, ids: Collection[str]) -> dict[str, Row]:
        return {i: r for i, r in self.row_values.get(key, {}).items() if i in ids}

    def all_rows(self, key: str) -> dict[str, Row]:
        return dict(self.row_values.get(key, {}))

    def answer(self, key: str, name: str) -> object | None:
        return self.answer_values.get(key, {}).get(name)

    def citing(self, key: str, code: str, limit: int | None) -> tuple[str, ...] | None:
        ids = self.citer_values.get(key, {}).get(code)
        return ids if ids is None or limit is None else ids[:limit]

    def facts(self, ident: str) -> StateFacts | None:
        return self.fact_values.get(ident)

    def seen(self, key: str) -> bool:
        return key in self.markers

    def mark_seen(
        self,
        key: str,
        parses: Mapping[FileKey, Parsed | None],
        facts: Mapping[str, StateFacts],
        *,
        files: int,
    ) -> None:
        self.keep_parses(parses, files=files)
        for ident, fact in facts.items():
            self.fact_values.setdefault(ident, fact)
        self.markers.pop(key, None)
        self.markers[key] = None
        if len(self.markers) > 64:
            self.markers.pop(next(iter(self.markers)))

    def keep_state(
        self,
        state: StoredState,
        rows: Mapping[str, Row],
        answers: Mapping[str, object],
        citing: Mapping[str, tuple[str, ...]],
        facts: Mapping[str, StateFacts],
        parses: Mapping[FileKey, Parsed | None],
        misses: Collection[FileKey],
        epoch: int,
        *,
        files: int,
    ) -> None:
        self.keep_parses(parses, files=files)
        for ident, fact in facts.items():
            self.fact_values.setdefault(ident, fact)
        self.states.pop(state.key, None)
        self.states[state.key] = state
        self.row_values[state.key] = dict(rows)
        self.citer_values[state.key] = dict(citing)
        self.answer_values[state.key] = dict(answers)
        if len(self.states) > 4:
            key = next(iter(self.states))
            for table in (self.states, self.row_values, self.citer_values, self.answer_values):
                table.pop(key)
