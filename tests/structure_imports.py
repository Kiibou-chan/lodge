"""Import rules: allowed edges, front doors, allow-list, process and I/O modules, and cycles."""

import ast
from pathlib import Path

from structure_tables import ALLOWED, CORE_MODULES, PURE, ROOT, package_of

TRACKED = CORE_MODULES | {"importlib.resources", "asyncio.subprocess"}
SPAWNING_MODULES = {"subprocess", "multiprocessing", "pty"}
WRITING_MODULES = {"shutil", "tempfile"}
READING_MODULES = {"fileinput", "pkgutil"}


def check_imports(
    name: str,
    rel: str,
    tree: ast.Module,
    src_root: Path,
    mods: dict[str, Path],
    graph: dict[str, set[str]],
) -> list[str]:
    pkg = package_of(name)
    in_function = {
        id(inner)
        for outer in ast.walk(tree)
        if isinstance(outer, ast.FunctionDef | ast.AsyncFunctionDef)
        for inner in ast.walk(outer)
    }
    found: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Import | ast.ImportFrom):
            continue
        where = f"{rel}:{node.lineno}"
        if pkg == ROOT:
            found.append(f"{where}: root imports nothing")
            continue
        if id(node) in in_function:
            found.append(f"{where}: import inside a function")
        if isinstance(node, ast.ImportFrom) and node.level:
            found.append(f"{where}: relative import")
            continue
        for target in _targets(node, src_root):
            if target.split(".")[0] == "lodge":
                reached = target
                while reached and reached not in mods:
                    reached = reached.rpartition(".")[0]
                if reached:
                    graph[name].add(reached)
                problem = _lodge_edge(pkg, target)
            else:
                problem = _outside_edge(pkg, target)
            if problem:
                found.append(f"{where}: {problem}")
    return found


def _targets(node: ast.Import | ast.ImportFrom, src_root: Path) -> list[str]:
    """Absolute dotted targets of one statement; `from P import n` is `P.n` for a submodule."""
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    base = node.module or ""
    out: list[str] = []
    for alias in node.names:
        sub = f"{base}.{alias.name}"
        on_disk = (src_root / sub.replace(".", "/")).is_dir() or (
            src_root / sub.replace(".", "/")
        ).with_suffix(".py").is_file()
        is_module = on_disk if base.split(".")[0] == "lodge" else sub in TRACKED
        out.append(sub if is_module else base)
    return list(dict.fromkeys(out))


def _lodge_edge(pkg: str, target: str) -> str | None:
    target_pkg = package_of(target)
    if target_pkg == pkg:
        return f"{pkg} imports its own front door {target}" if target == f"lodge.{pkg}" else None
    if target_pkg not in ALLOWED and target_pkg != ROOT:
        return f"{pkg} imports unknown package {target_pkg}"
    if target_pkg not in ALLOWED.get(pkg, set()):
        return f"{pkg} may not import {target_pkg}"
    if target != f"lodge.{target_pkg}":
        return f"{pkg} imports {target} past the front door lodge.{target_pkg}"
    return None


def _outside_edge(pkg: str, target: str) -> str | None:
    if pkg in PURE:
        if any(target == ok or target.startswith(f"{ok}.") for ok in CORE_MODULES):
            return None
        return f"{pkg} may not import {target}"
    top = target.split(".")[0]
    if pkg != "gitstore":
        if top in SPAWNING_MODULES or target.startswith("asyncio.subprocess"):
            return f"process spawning outside gitstore: {target}"
        if top in WRITING_MODULES:
            return f"file writing outside gitstore: {top}"
    if pkg not in {"gitstore", "cli"} and top in READING_MODULES:
        return f"file reading outside gitstore and cli: {top}"
    if target.startswith("importlib.resources") and pkg not in {"cli", "viewer"}:
        return "importlib.resources outside cli and viewer"
    return None


def cycles(graph: dict[str, set[str]]) -> list[str]:
    """Strongly connected components with a cycle, by Tarjan's algorithm."""
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    done: list[list[str]] = []

    def visit(node: str) -> None:
        index[node] = low[node] = len(index)
        stack.append(node)
        for nxt in sorted(graph.get(node, ())):
            if nxt not in index:
                visit(nxt)
                low[node] = min(low[node], low[nxt])
            elif nxt in stack:
                low[node] = min(low[node], index[nxt])
        if low[node] == index[node]:
            part = [stack.pop()]
            while part[-1] != node:
                part.append(stack.pop())
            done.append(sorted(part))

    for node in sorted(graph):
        if node not in index:
            visit(node)
    return [
        f"import cycle among {', '.join(part)}"
        for part in done
        if len(part) > 1 or part[0] in graph[part[0]]
    ]
