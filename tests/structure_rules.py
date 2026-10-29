"""The spec's structure rules, checked with `ast`: imports, front doors, cycles, size, purity."""

import ast
from pathlib import Path

from structure_calls import check_calls
from structure_imports import check_imports, cycles
from structure_tables import ALLOWED, CORE_MODULES, FRONT_DOORS, MAX_LINES, modules, package_of

__all__ = ["ALLOWED", "CORE_MODULES", "MAX_LINES", "modules", "violations"]


def violations(src_root: Path, tests_root: Path) -> list[str]:
    found: list[str] = []
    mods = modules(src_root)
    found += _layout(src_root, mods)
    graph: dict[str, set[str]] = {name: set() for name in mods}
    for name, path in mods.items():
        rel = str(path.relative_to(src_root))
        tree, problems = _parse(rel, path)
        found += problems
        if tree is not None:
            found += check_imports(name, rel, tree, src_root, mods, graph)
            found += check_calls(package_of(name), rel, tree)
    found += cycles(graph)
    for path in sorted(tests_root.rglob("*.py")):
        found += _parse(f"{tests_root.name}/{path.relative_to(tests_root)}", path)[1]
    return found


def _parse(rel: str, path: Path) -> tuple[ast.Module | None, list[str]]:
    """The syntax tree of a file, plus its size and decoding problems."""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None, [f"{rel}: not UTF-8"]
    lines = len(text.splitlines())
    found = [f"{rel}: {lines} lines (limit {MAX_LINES})"] if lines > MAX_LINES else []
    try:
        return ast.parse(text), found
    except SyntaxError as error:
        return None, [*found, f"{rel}:{error.lineno}: cannot parse: {error.msg}"]


def _layout(src_root: Path, mods: dict[str, Path]) -> list[str]:
    """Unknown packages, missing front doors, and directories without `__init__.py`."""
    found = [
        f"lodge/{pkg}: unknown package {pkg}"
        for pkg in sorted({package_of(name) for name in mods} - ALLOWED.keys() - {"root"})
    ]
    doors = {src_root / "lodge" / pkg for pkg in FRONT_DOORS}
    for door in sorted(doors):
        if not (door / "__init__.py").is_file():
            found.append(f"{door.relative_to(src_root)}/__init__.py: missing front door")
    bare = {path.parent for path in mods.values() if not (path.parent / "__init__.py").is_file()}
    for folder in sorted(bare - doors):
        found.append(f"{folder.relative_to(src_root)}: no __init__.py")
    return found
