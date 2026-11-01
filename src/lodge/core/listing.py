"""Content keys and listings shared by exact and indexed reads."""

from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha1


def blob_id(raw: bytes) -> str:
    """Git's blob object ID for the given bytes."""
    return sha1(b"blob %d\0" % len(raw) + raw).hexdigest()


@dataclass(frozen=True)
class Listing:
    """Equal identities imply equal file mappings and attachment sets."""

    rev: str | None
    ident: str
    blobs: Mapping[str, str]
    attachments: frozenset[str]
