import pytest

from lodge.core import is_id, mint_id


def test_mint_id() -> None:
    assert mint_id("d", bytes(8)) == "d-000000"
    assert mint_id("s", b"\xff" * 8) == "s-zzzzzz"
    assert is_id("d-3m8qk2")
    assert not is_id("d-3m8qkI")
    assert not is_id("x-3m8qk2")


def test_mint_id_reads_six_bytes_into_the_alphabet() -> None:
    assert mint_id("d", bytes([0, 1, 9, 10, 17, 31])) == "d-01" + "9a" + "hz"


def test_mint_id_needs_six_bytes() -> None:
    with pytest.raises(ValueError, match="six"):
        mint_id("d", bytes(5))


@pytest.mark.parametrize("letter", ["i", "l", "o", "u"])
def test_excluded_letters_are_not_ids(letter: str) -> None:
    assert not is_id(f"d-00000{letter}")


@pytest.mark.parametrize(
    "text", ["d-3m8qk", "d-3m8qk22", "d-3M8QK2", "d-3m8qk2\n", " d-3m8qk2", "d3m8qk2"]
)
def test_wrong_shapes_are_not_ids(text: str) -> None:
    assert not is_id(text)
