"""The scan shortcut agrees with the original decoder on arbitrary git tags."""

from random import Random

from lodge.gitstore.flags import Flagged, config_values, scan
from lodge.gitstore.trees import decode


def test_scan_equals_the_loop() -> None:
    rng = Random(827)
    for _ in range(500):
        raw = (
            b"\0".join(
                rng.choice(b"HSMRCK?hs mrck".replace(b" ", b"")).to_bytes()
                + b" "
                + rng.choice(
                    [
                        b"lodge/old.md",
                        b".gitattributes",
                        b"lodge/a/.gitattributes",
                        b"lodge/\xff.md",
                        b"other",
                    ]
                )
                for _ in range(rng.randrange(60))
            )
            + b"\0"
        )
        paths, attributes = set(), set()
        for item in raw.split(b"\0"):
            if len(item) < 3:
                continue
            tag, path = chr(item[0]), decode(item[2:])
            if path.startswith("lodge/") and (tag == "S" or tag.islower()):
                paths.add(path)
            if path.rsplit("/", 1)[-1] == ".gitattributes":
                attributes.add(path)
        assert scan(raw) == Flagged(frozenset(paths), frozenset(attributes))
        assert scan(raw.rstrip(b"\0")) == Flagged(frozenset(paths), frozenset(attributes))
    assert scan(b"H lodge/old.md\0H lodge/.gitattributes\0") == Flagged(
        frozenset(), frozenset({"lodge/.gitattributes"})
    )


def test_config_values_spellings() -> None:
    for value in (
        None,
        "",
        "input",
        "true",
        "yes",
        "on",
        "1",
        "false",
        "no",
        "off",
        "0",
        "line\nvalue",
    ):
        raw = b"core.autocrlf" + (b"" if value is None else b"\n" + value.encode()) + b"\0"
        assert config_values(raw) == {"core.autocrlf": value}
    assert config_values(b"core.autocrlf\nfalse\0core.autocrlf\ntrue\0") == {
        "core.autocrlf": "true"
    }
