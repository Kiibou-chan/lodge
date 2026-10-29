"""Call-level rules: purity of core and app, dynamic code, and the I/O and process confinement."""

import ast
import re
from dataclasses import dataclass, field

from structure_tables import PURE

BANNED_NAMES = {"open", "input", "print"}
CLOCK_ATTRS = {"now", "today", "utcnow", "fromtimestamp"}
DYNAMIC_IMPORTS = {"__import__", "import_module"}
DYNAMIC_CODE = {"exec", "eval", "compile"}
READ_ATTRS = {"read_text", "read_bytes", "open"}
WRITE_ATTRS = {
    "write_text",
    "write_bytes",
    "mkdir",
    "touch",
    "unlink",
    "rmdir",
    "rename",
    "symlink_to",
    "hardlink_to",
}
OS_WRITES = {
    "open",
    "remove",
    "unlink",
    "rename",
    "replace",
    "mkdir",
    "makedirs",
    "rmdir",
    "removedirs",
    "truncate",
    "symlink",
    "link",
}
OS_SPAWNS = {"system", "popen", "startfile", "fork", "forkpty", "posix_spawn", "posix_spawnp"}
OS_SPAWN_FAMILY = re.compile(r"(exec|spawn)[lv]p?e?")
ASYNC_SPAWNS = {"create_subprocess_exec", "create_subprocess_shell"}
WRITE_MODE = set("wax+")


@dataclass
class Scope:
    pkg: str
    rel: str
    os_names: set[str] = field(default_factory=set)
    importlib_names: set[str] = field(default_factory=set)
    dt_modules: set[str] = field(default_factory=set)
    dt_classes: set[str] = field(default_factory=set)
    package_data: set[str] = field(default_factory=set)
    found: list[str] = field(default_factory=list)

    def report(self, node: ast.AST, text: str) -> None:
        self.found.append(f"{self.rel}:{getattr(node, 'lineno', 0)}: {text}")

    @property
    def spawns_allowed(self) -> bool:
        return self.pkg == "gitstore" or self.pkg in PURE

    @property
    def reads_allowed(self) -> bool:
        return self.pkg in {"gitstore", "cli"}


def check_calls(pkg: str, rel: str, tree: ast.Module) -> list[str]:
    scope = Scope(pkg, rel)
    _collect_aliases(scope, tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and _is_package_data(scope, node.value):
            scope.package_data |= {t.id for t in node.targets if isinstance(t, ast.Name)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            _name(scope, node)
        elif isinstance(node, ast.Attribute):
            _attribute(scope, node)
        elif isinstance(node, ast.Call):
            _call(scope, node)
        elif isinstance(node, ast.ImportFrom):
            _import_from(scope, node)
    return scope.found


def _collect_aliases(scope: Scope, tree: ast.Module) -> None:
    tracked = {
        "os": scope.os_names,
        "importlib": scope.importlib_names,
        "datetime": scope.dt_modules,
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top in tracked and (alias.asname is None or alias.name == top):
                    tracked[top].add(alias.asname or top)
        elif isinstance(node, ast.ImportFrom) and node.module == "datetime":
            wanted = {"datetime", "date"}
            scope.dt_classes |= {a.asname or a.name for a in node.names if a.name in wanted}


def _name(scope: Scope, node: ast.Name) -> None:
    if node.id in DYNAMIC_CODE:
        scope.report(node, f"dynamic code: {node.id}")
    if node.id in DYNAMIC_IMPORTS:
        scope.report(node, "dynamic import")
    if node.id in ASYNC_SPAWNS and not scope.spawns_allowed:
        scope.report(node, f"process spawning outside gitstore: {node.id}")
    if node.id == "open":
        if scope.pkg in PURE:
            scope.report(node, f"{scope.pkg} may not use open")
        elif not scope.reads_allowed:
            scope.report(node, "file reading outside gitstore and cli: open")
    elif node.id in BANNED_NAMES and scope.pkg in PURE:
        scope.report(node, f"{scope.pkg} may not use {node.id}")


def _attribute(scope: Scope, node: ast.Attribute) -> None:
    owner = node.value.id if isinstance(node.value, ast.Name) else None
    attr = node.attr
    if attr in DYNAMIC_IMPORTS:
        scope.report(node, "dynamic import")
    if attr in ASYNC_SPAWNS and not scope.spawns_allowed:
        scope.report(node, f"process spawning outside gitstore: {attr}")
    if (
        attr == "resources"
        and owner in scope.importlib_names
        and scope.pkg not in PURE | {"cli", "viewer"}
    ):
        scope.report(node, "importlib.resources outside cli and viewer")
    if _reads_clock(scope, node):
        scope.report(node, f"{scope.pkg} may not use {ast.unparse(node)}")
    if owner in scope.os_names:
        _os_attribute(scope, node)
        return
    if attr in READ_ATTRS and not scope.reads_allowed and not _reads_package_data(scope, node):
        scope.report(node, f"file reading outside gitstore and cli: {attr}")
    if attr in WRITE_ATTRS and scope.pkg != "gitstore":
        scope.report(node, f"file writing outside gitstore: {attr}")


def _is_package_data(scope: Scope, node: ast.expr) -> bool:
    """Whether an expression is a `Traversable` reached from a call of `files(...)`."""
    while True:
        if isinstance(node, ast.Call):
            func = node.func
            if (isinstance(func, ast.Name) and func.id == "files") or (
                isinstance(func, ast.Attribute) and func.attr == "files"
            ):
                return True
            node = func
        elif isinstance(node, ast.Attribute):
            node = node.value
        elif isinstance(node, ast.BinOp):
            node = node.left
        else:
            return isinstance(node, ast.Name) and node.id in scope.package_data


def _reads_package_data(scope: Scope, node: ast.Attribute) -> bool:
    """A read on package data in `viewer` (`cli` reads anything), or a browser's `open`."""
    if isinstance(node.value, ast.Name) and node.value.id == "webbrowser":
        return True
    return scope.pkg == "viewer" and _is_package_data(scope, node.value)


def _os_attribute(scope: Scope, node: ast.Attribute) -> None:
    if _spawns(node.attr) and not scope.spawns_allowed:
        scope.report(node, f"process spawning outside gitstore: os.{node.attr}")
    if node.attr in OS_WRITES and scope.pkg != "gitstore":
        scope.report(node, f"file writing outside gitstore: os.{node.attr}")


def _spawns(attr: str) -> bool:
    return attr in OS_SPAWNS or OS_SPAWN_FAMILY.fullmatch(attr) is not None


def _reads_clock(scope: Scope, node: ast.Attribute) -> bool:
    """`core` names the clock on any receiver; `app` only on the `datetime` classes."""
    if node.attr not in CLOCK_ATTRS:
        return False
    if scope.pkg == "core":
        return True
    if scope.pkg != "app":
        return False
    owner = node.value
    if isinstance(owner, ast.Name):
        return owner.id in scope.dt_classes
    return (
        isinstance(owner, ast.Attribute)
        and owner.attr in {"datetime", "date"}
        and isinstance(owner.value, ast.Name)
        and owner.value.id in scope.dt_modules
    )


def _call(scope: Scope, node: ast.Call) -> None:
    func = node.func
    if (
        isinstance(func, ast.Name)
        and func.id == "getattr"
        and len(node.args) > 1
        and isinstance(node.args[1], ast.Constant)
        and node.args[1].value in DYNAMIC_IMPORTS
    ):
        scope.report(node, "dynamic import")
    if scope.pkg == "gitstore":
        return
    if isinstance(func, ast.Name):
        if func.id == "FileIO" or (func.id == "open" and scope.pkg not in PURE):
            _open_mode(scope, node, 1)
    elif isinstance(func, ast.Attribute) and _opens_a_file(scope, func):
        io_style = isinstance(func.value, ast.Name) and func.value.id in {"io", "codecs"}
        _open_mode(scope, node, 1 if io_style or func.attr == "FileIO" else 0)


def _opens_a_file(scope: Scope, func: ast.Attribute) -> bool:
    """`x.open(...)` or `x.FileIO(...)`, except `os.open` and package data or a browser."""
    return (
        func.attr in {"open", "FileIO"}
        and not _is_os(scope, func)
        and not _reads_package_data(scope, func)
    )


def _is_os(scope: Scope, func: ast.Attribute) -> bool:
    return isinstance(func.value, ast.Name) and func.value.id in scope.os_names


def _open_mode(scope: Scope, node: ast.Call, position: int) -> None:
    modes = [kw.value for kw in node.keywords if kw.arg == "mode"]
    modes += node.args[position : position + 1]
    for mode in modes:
        constant = isinstance(mode, ast.Constant) and isinstance(mode.value, str)
        if not constant or WRITE_MODE & set(str(getattr(mode, "value", ""))):
            scope.report(node, "file writing outside gitstore: open for writing")
            return


def _import_from(scope: Scope, node: ast.ImportFrom) -> None:
    names = {alias.name for alias in node.names}
    if node.module == "importlib" and "import_module" in names:
        scope.report(node, "dynamic import")
    if node.module == "asyncio" and names & ASYNC_SPAWNS and not scope.spawns_allowed:
        scope.report(node, "process spawning outside gitstore: asyncio")
    if node.module == "os":
        if any(_spawns(n) for n in names) and not scope.spawns_allowed:
            scope.report(node, "process spawning outside gitstore: os")
        if names & OS_WRITES and scope.pkg != "gitstore":
            scope.report(node, "file writing outside gitstore: os")
