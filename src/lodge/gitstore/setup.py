"""Finding the repository, opening the store for a mode, and creating its data."""

from pathlib import Path

from lodge.app import Clock, LodgeError, Store
from lodge.gitstore.branch import BranchStore, init_branch
from lodge.gitstore.checkout import CheckoutStore, data_folder_exists
from lodge.gitstore.errors import GitMissing, NotARepository
from lodge.gitstore.git import run
from lodge.gitstore.lock import locked
from lodge.gitstore.settings import StoreSettings
from lodge.gitstore.trees import DATA, KEPT

LOCK_WAIT_SECONDS = 30.0


def repo_root(cwd: Path) -> Path:
    """The top of the working tree that contains `cwd`."""
    try:
        return Path(run(["rev-parse", "--show-toplevel"], cwd))
    except GitMissing:
        raise
    except LodgeError as error:
        raise NotARepository(f"{cwd} is not inside a git repository") from error


def open_store(
    root: Path,
    settings: StoreSettings,
    clock: Clock,
    *,
    lock_wait_seconds: float = LOCK_WAIT_SECONDS,
    index_retry_seconds: float = 1.0,
) -> Store:
    common = _common_dir(root)
    if settings.mode == "branch":
        return BranchStore(root, settings, clock, common, lock_wait_seconds)
    return CheckoutStore(root, settings, common, lock_wait_seconds, index_retry_seconds)


def init_store(root: Path, settings: StoreSettings) -> str:
    """Create the empty store, refusing when it exists; says what it made."""
    common = _common_dir(root)
    if settings.mode == "branch":
        return init_branch(root, settings, common, LOCK_WAIT_SECONDS)
    with locked(common, LOCK_WAIT_SECONDS):
        if data_folder_exists(root):
            raise LodgeError(f"lodge is already initialised: {DATA}/ exists")
        for path in KEPT:
            try:
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                (root / path).write_bytes(b"")
            except OSError as error:
                raise LodgeError(f"cannot create {path}: {error.strerror}") from error
        run(["add", "--", *KEPT], root)
    return f"created {DATA}/decisions and {DATA}/spec, staged"


def data_root(root: Path, settings: StoreSettings) -> Path | None:
    """The folder that holds the record files; None when they live on a branch."""
    return None if settings.mode == "branch" else root / DATA


def holds_records(root: Path, settings: StoreSettings) -> bool:
    """Whether `lodge init` has been run in this checkout; in branch mode nothing here says."""
    if settings.mode == "branch":
        return True
    return all((root / DATA / name).is_dir() for name in ("decisions", "spec"))


def _common_dir(root: Path) -> Path:
    return Path(run(["rev-parse", "--path-format=absolute", "--git-common-dir"], root))
