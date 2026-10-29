"""The rule tables and the module map shared by the structure checks."""

from pathlib import Path

ALLOWED: dict[str, set[str]] = {
    "core": set(),
    "app": {"core"},
    "gitstore": {"app", "core"},
    "cli": {"app", "core"},
    "viewer": {"app", "core"},
    "hook": {"app", "core"},
    "main": {"core", "app", "gitstore", "cli", "viewer", "hook"},
}
CORE_MODULES: set[str] = {
    "dataclasses",
    "enum",
    "typing",
    "collections.abc",
    "re",
    "hashlib",
    "datetime",
    "tomllib",
    "functools",
    "itertools",
    "json",
    "yaml",
}
MAX_LINES = 300

ROOT = "root"
PURE = {"core", "app"}
FRONT_DOORS = sorted(ALLOWED.keys() - {"main"})


def modules(src_root: Path) -> dict[str, Path]:
    """Dotted module name to file for every module under `src_root/lodge`."""
    found: dict[str, Path] = {}
    for path in sorted((src_root / "lodge").rglob("*.py")):
        parts = list(path.relative_to(src_root).with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        found[".".join(parts)] = path
    return found


def package_of(module: str) -> str:
    parts = module.split(".")
    return parts[1] if len(parts) > 1 else ROOT
