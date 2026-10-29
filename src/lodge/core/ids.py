"""Identifiers: a type prefix and six characters of Crockford base32, lower case."""

import re
from typing import Literal

ALPHABET = "0123456789abcdefghjkmnpqrstvwxyz"
ID_LENGTH = 6
_ID = re.compile(rf"[ds]-[{ALPHABET}]{{{ID_LENGTH}}}")


def mint_id(prefix: Literal["d", "s"], entropy: bytes) -> str:
    """The identifier whose characters are the low five bits of the first six entropy bytes."""
    if len(entropy) < ID_LENGTH:
        raise ValueError(f"an identifier needs at least six entropy bytes, got {len(entropy)}")
    return f"{prefix}-" + "".join(ALPHABET[byte % 32] for byte in entropy[:ID_LENGTH])


def is_id(text: str) -> bool:
    return _ID.fullmatch(text) is not None
