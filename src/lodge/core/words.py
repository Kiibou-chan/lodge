"""The words of a text, as search reads them."""

import re

from lodge.core.model import Decision, SpecEntry
from lodge.core.snapshot import Parsed

_WORDS = re.compile(r"[^\W_]+")
_FUNCTION_WORDS = frozenset(
    [
        "a",
        "about",
        "after",
        "all",
        "also",
        "an",
        "and",
        "any",
        "are",
        "as",
        "at",
        "be",
        "been",
        "but",
        "by",
        "can",
        "could",
        "did",
        "do",
        "does",
        "for",
        "from",
        "had",
        "has",
        "have",
        "he",
        "her",
        "his",
        "how",
        "i",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "may",
        "me",
        "might",
        "more",
        "most",
        "my",
        "no",
        "not",
        "of",
        "on",
        "one",
        "or",
        "our",
        "out",
        "she",
        "should",
        "so",
        "some",
        "such",
        "than",
        "that",
        "the",
        "their",
        "them",
        "then",
        "there",
        "these",
        "they",
        "this",
        "those",
        "to",
        "was",
        "we",
        "were",
        "what",
        "when",
        "which",
        "who",
        "will",
        "with",
        "would",
        "you",
        "your",
    ]
)


def words(text: str) -> set[str]:
    """Runs of letters or digits, lower-cased, without English function words."""
    return set(tokens(text)) - _FUNCTION_WORDS


def tokens(text: str) -> tuple[str, ...]:
    """Lower-cased word runs, including function words, in their original order."""
    return tuple(_WORDS.findall(text.lower()))


def parse_words(parsed: Parsed | None) -> tuple[str, str]:
    """Space-joined word sets of a searchable record, empty for other parse kinds."""
    if isinstance(parsed, (Decision, SpecEntry)):
        return " ".join(sorted(words(parsed.title))), " ".join(sorted(words(parsed.statement)))
    return "", ""
