"""Code families and citations obey the ASCII grammar and boundary rule."""

import random
import re

from builders import at, decision, entry, snapshot_of

from lodge.core import (
    Action,
    Change,
    citers,
    cites,
    code_tokens,
    derive,
    family,
    is_code_token,
)


def test_family_takes_dotted_siblings_not_longer_numbers() -> None:
    records = [
        decision(id=f"d-{n:06x}", code=code)
        for n, code in enumerate(["X-1", "X-1.why", "x-1.b", "X-10", "X-1a"])
    ]
    spec = entry(id="s-000000", code="X-1.spec")
    snapshot = snapshot_of(*records, spec)
    assert family(snapshot, "x-1") == tuple(
        r.id for r in (records[0], records[2], spec, records[1])
    )
    assert family(snapshot, "missing") == ()
    assert family(snapshot, "X-1.") == ()


def test_family_orders_the_code_first() -> None:
    b = decision(id="d-000001", code="X-1.B")
    a = decision(id="d-000002", code="x-1.a")
    root = entry(id="s-000001", code="x-1")
    snapshot = snapshot_of(b, a, root)
    assert family(snapshot, "X-1") == (root.id, a.id, b.id)
    assert family(snapshot, "x") == ()


def test_cites_whole_tokens_only() -> None:
    for text in ["see X-1.", "X-1,", "(X-1)", "X-1.-", "x-1"]:
        assert cites(text, "X-1"), text
    for text in ["X-10", "X-1.why", "AX-1", "\u017f-1"]:
        assert not cites(text, "X-1"), text
    assert not cites("\u017f-1", "s-1")
    assert code_tokens("See X-1.- and X-1.why.") == frozenset(
        {"see", "x-1.-", "x-1", "and", "x-1.why.", "x-1.why"}
    )


def test_cites_equals_the_boundary_rule() -> None:
    rng = random.Random(20261101)
    alphabet = "abXY019.-_ ,()\u017f"
    for _ in range(2000):
        text = "".join(rng.choices(alphabet, k=rng.randrange(1, 70)))
        start = rng.randrange(len(text))
        stop = rng.randrange(start + 1, len(text) + 1)
        code = text[start:stop].strip()
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", code):
            code = rng.choice(["a", "X-1", "b.0", "Y_9", "s-1"])
        expected = (
            re.search(
                r"(?<![a-z0-9._-])" + re.escape(code.lower()) + r"(?![a-z0-9_-]|\.[a-z0-9])",
                text.lower(),
            )
            is not None
        )
        assert cites(text, code) == expected, (text, code)


def test_citers_exclude_the_family_and_order_newest_first() -> None:
    root = decision(id="d-000001", code="X-1", statement="See X-1.")
    sibling = entry(id="s-000001", code="X-1.why", statement="X-1.")
    older = decision(id="d-000002", date=at(0), title="X-1, applies")
    newer = decision(id="d-000003", date=at(2), statement="See x-1.", replaces=(older.id,))
    tie = decision(id="d-000004", date=at(2), statement="(X-1)")
    spec = entry(id="s-000002", title="According to X-1")
    undated = entry(id="s-000003", statement="X-1")
    change = decision(id="d-000005", date=at(3), changes=(Change(spec.id, Action.CREATE),))
    reasoning = decision(id="d-000006", reasoning="X-1", statement="X-10")
    snapshot = snapshot_of(root, sibling, older, newer, tie, spec, undated, change, reasoning)
    assert citers(snapshot, derive(snapshot), "x-1") == (
        spec.id,
        tie.id,
        newer.id,
        older.id,
        undated.id,
    )


def test_is_code_token_uses_the_ascii_grammar() -> None:
    for code in ["A", "x-1", "X-1.why", "0_a.-"]:
        assert is_code_token(code)
    for code in ["", " A", "A ", "A B", ".A", "-A", "\u017f-1", "é1", "A\n"]:
        assert not is_code_token(code), code
