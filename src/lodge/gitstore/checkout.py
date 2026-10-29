"""The store on the current checkout: reads the working tree, writes files, stages them."""

import os
import stat
from collections.abc import Iterable, Mapping
from pathlib import Path

from lodge.app import Gate, LodgeError, PublishOutcome
from lodge.core import ATTACHMENTS, Tree
from lodge.gitstore.errors import NOT_INITIALISED, NotInitialised
from lodge.gitstore.git import run
from lodge.gitstore.lock import locked
from lodge.gitstore.plumbing import check_writes
from lodge.gitstore.published import Published, committed_gate, published_state
from lodge.gitstore.settings import StoreSettings
from lodge.gitstore.trees import DATA, decode, encode

_TEMPORARY_SUFFIX = ".lodge-tmp"


class CheckoutStore:
    def __init__(
        self, root: Path, settings: StoreSettings, common_dir: Path, lock_wait_seconds: float
    ) -> None:
        self._root = root
        self._settings = settings
        self._common = common_dir
        self._wait = lock_wait_seconds
        self._published: Published | None = None

    def trees(self) -> tuple[Tree, Tree]:
        """The working tree, and the tree at the merge base of `HEAD` with the base branch."""
        if not data_folder_exists(self._root):
            raise NotInitialised(NOT_INITIALISED)
        self._published = published_state(self._root, self._settings)
        return disk_tree(self._root), self._published.tree

    def freshness(self) -> str | None:
        """Only that the published state is missing; None otherwise."""
        return None if self._published is None else self._published.missing

    def gate(self, current: Tree) -> Gate:
        published = self._published or published_state(self._root, self._settings)
        if published.missing is not None:
            raise LodgeError(published.missing)
        return committed_gate(self._root, current, published.tree)

    def publish(self, base: Tree, writes: Mapping[str, str], message: str) -> PublishOutcome:
        """Write and stage `writes`; REJECTED when a path no longer has the text `base` read.

        All of it or none: the files go to temporaries first, and a failure at a later step
        puts back what was there.
        """
        check_writes(base, writes)
        with locked(self._common, self._wait):
            before: dict[str, bytes | None] = {}
            for path in writes:
                _refuse_links(self._root, path)
                before[path] = _on_disk(self._root, path)
            for path, raw in before.items():
                if (None if raw is None else decode(raw)) != base.files.get(path):
                    return PublishOutcome.REJECTED
            _write_all(self._root, writes, before)
        return PublishOutcome.STAGED


def data_folder_exists(root: Path) -> bool:
    """Whether `lodge/` is a folder here; a link or a file in its place is an error."""
    try:
        mode = os.lstat(root / DATA).st_mode
    except FileNotFoundError:
        return False
    if stat.S_ISLNK(mode):
        raise LodgeError(f"{DATA} is a symbolic link, which lodge does not follow")
    if not stat.S_ISDIR(mode):
        raise LodgeError(f"{DATA} is a file, not a folder")
    return True


def disk_tree(root: Path) -> Tree:
    """Every file on disk under `lodge/`, tracked or not; links are not followed.

    A link reads as its target text, anything but a regular file or a link as empty text, and
    attachments are listed, never read.
    """
    files: dict[str, str] = {}
    attachments: set[str] = set()
    for folder, dirs, names in os.walk(root / DATA):
        linked = [name for name in dirs if (Path(folder) / name).is_symlink()]
        for name in [*names, *linked]:
            full = Path(folder) / name
            path = full.relative_to(root).as_posix()
            if path.startswith(ATTACHMENTS):
                attachments.add(path)
            else:
                files[path] = _read(full)
    return Tree(None, files, frozenset(attachments))


def _read(full: Path) -> str:
    try:
        mode = os.lstat(full).st_mode
        if stat.S_ISLNK(mode):
            return decode(os.fsencode(os.readlink(full)))
        return decode(full.read_bytes()) if stat.S_ISREG(mode) else ""
    except OSError:
        return ""


def _refuse_links(root: Path, path: str) -> None:
    """Refuse a path that passes through a link, or through anything but folders to a file."""
    parts = path.split("/")
    current = root
    for index, part in enumerate(parts):
        current = current / part
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError:
            return
        except OSError as error:
            raise LodgeError(f"cannot read {path}: {error.strerror}") from error
        if stat.S_ISLNK(mode):
            raise LodgeError(f"{path} passes through a symbolic link, which lodge does not follow")
        wanted = stat.S_ISREG if index == len(parts) - 1 else stat.S_ISDIR
        if not wanted(mode):
            raise LodgeError(f"{path} cannot be written: {part} is not a regular file or a folder")


def _on_disk(root: Path, path: str) -> bytes | None:
    """The bytes of the regular file at `path`, None when there is none."""
    try:
        return (root / path).read_bytes()
    except FileNotFoundError:
        return None
    except OSError as error:
        raise LodgeError(f"cannot read {path}: {error.strerror}") from error


def _write_all(root: Path, writes: Mapping[str, str], before: Mapping[str, bytes | None]) -> None:
    """Write every file and stage it, or leave the folder as it was and raise.

    An error from the file system is a `LodgeError`; an exit or an interrupt passes through.
    """
    made: list[Path] = []
    temporaries: dict[str, Path] = {}
    replaced: list[str] = []
    staged: dict[str, tuple[str, str]] | None = None
    current = ""
    try:
        for current, text in writes.items():
            target = root / current
            made += _make_folders(target.parent, root)
            temporaries[current] = _temporary(target, encode(text), before[current] is not None)
        for current, temporary in temporaries.items():
            os.replace(temporary, root / current)
            replaced.append(current)
        current = ""
        staged = _staged(root, writes)
        run(["add", "--", *writes], root)
    except OSError as error:
        _put_back(root, before, replaced, temporaries, made)
        raise LodgeError(f"cannot write {current}: {error.strerror}") from error
    except BaseException:
        _put_back(root, before, replaced, temporaries, made)
        if staged is not None:
            _restage(root, staged, writes)
        raise


def _temporary(target: Path, data: bytes, exists: bool) -> Path:
    """A new file beside `target` holding `data`, with the mode `target` has or a new file gets.

    The name is unused and never followed through a link: `O_EXCL` and `O_NOFOLLOW` refuse both.
    A new file is created with mode 0o666, which the process's umask narrows.
    """
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    while True:
        temporary = target.parent / f".{target.name}.{os.urandom(6).hex()}{_TEMPORARY_SUFFIX}"
        try:
            descriptor = os.open(temporary, flags, 0o600 if exists else 0o666)
        except FileExistsError:
            continue
        break
    try:
        with os.fdopen(descriptor, "wb") as handle:
            if exists:
                os.fchmod(handle.fileno(), _mode_of(target))
            handle.write(data)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def _mode_of(target: Path) -> int:
    return stat.S_IMODE(os.stat(target).st_mode)


def _make_folders(folder: Path, root: Path) -> list[Path]:
    """Create `folder` and the missing folders above it; the ones created, deepest first."""
    missing: list[Path] = []
    while not folder.exists() and folder != root:
        missing.append(folder)
        folder = folder.parent
    for item in reversed(missing):
        item.mkdir()
    return missing


def _put_back(
    root: Path,
    before: Mapping[str, bytes | None],
    replaced: list[str],
    temporaries: Mapping[str, Path],
    made: list[Path],
) -> None:
    for temporary in temporaries.values():
        temporary.unlink(missing_ok=True)
    for path in replaced:
        previous = before[path]
        try:
            if previous is None:
                (root / path).unlink(missing_ok=True)
            else:
                (root / path).write_bytes(previous)
        except OSError:
            continue
    for folder in made:
        try:
            folder.rmdir()
        except OSError:
            continue


def _staged(root: Path, paths: Iterable[str]) -> dict[str, tuple[str, str]]:
    """The mode and object of each of `paths` in the index now."""
    out = run(["ls-files", "-s", "-z", "--", *paths], root)
    found: dict[str, tuple[str, str]] = {}
    for item in out.split("\0"):
        meta, _, path = item.partition("\t")
        fields = meta.split(" ")
        if len(fields) == 3 and fields[2] == "0":
            found[path] = (fields[0], fields[1])
    return found


def _restage(root: Path, staged: Mapping[str, tuple[str, str]], paths: Iterable[str]) -> None:
    """Put the index entries of `paths` back as `staged` has them, after a `git add` that failed."""
    for path in paths:
        try:
            if path in staged:
                mode, sha = staged[path]
                run(["update-index", "--add", "--cacheinfo", f"{mode},{sha},{path}"], root)
            else:
                run(["update-index", "--force-remove", "--", path], root)
        except LodgeError:
            continue
