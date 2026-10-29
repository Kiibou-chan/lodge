"""Reading the files of a committed tree, and the text encoding of the store's files."""

from collections.abc import Sequence
from pathlib import Path

from lodge.app import LodgeError
from lodge.core import ATTACHMENTS, Tree
from lodge.gitstore.git import run_bytes

DATA = "lodge"
KEPT = (f"{DATA}/decisions/.gitkeep", f"{DATA}/spec/.gitkeep")


def decode(raw: bytes) -> str:
    """The text of a file; bytes that are not UTF-8 become lone surrogates, which `load` reports."""
    return raw.decode("utf-8", errors="surrogateescape")


def encode(text: str) -> bytes:
    return text.encode("utf-8", errors="surrogateescape")


def read_tree(root: Path, rev: str) -> Tree:
    """The files under `lodge/` at `rev`; attachments are listed, never read."""
    listing = run_bytes(["ls-tree", "-r", "-z", "--full-tree", rev, "--", DATA], root)
    blobs: dict[str, str] = {}
    attachments: set[str] = set()
    other: dict[str, str] = {}
    for item in listing.split(b"\0"):
        meta, _, raw_path = item.partition(b"\t")
        fields = meta.split(b" ")
        path = decode(raw_path)
        if len(fields) != 3 or not path.startswith(f"{DATA}/"):
            continue
        if path.startswith(ATTACHMENTS):
            attachments.add(path)
        elif fields[1] == b"blob":
            blobs[path] = fields[2].decode()
        else:
            other[path] = ""
    contents = _contents(root, sorted(set(blobs.values())))
    files = {**other, **{path: decode(contents[sha]) for path, sha in blobs.items()}}
    return Tree(rev, files, frozenset(attachments))


def _contents(root: Path, shas: Sequence[str]) -> dict[str, bytes]:
    """The blobs named by `shas`, read in one `cat-file --batch`."""
    if not shas:
        return {}
    out = run_bytes(["cat-file", "--batch"], root, input="\n".join(shas) + "\n")
    found: dict[str, bytes] = {}
    position = 0
    for sha in shas:
        end = out.index(b"\n", position)
        header = out[position:end].split(b" ")
        if len(header) != 3 or header[1] != b"blob":
            raise LodgeError(f"git cannot read the file {sha}")
        start = end + 1
        found[sha] = out[start : start + int(header[2])]
        position = start + int(header[2]) + 1
    return found
