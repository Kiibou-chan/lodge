"""For each core dataclass with a defaulted field, count the calls in src/lodge and tests that leave one out."""

import ast
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
classes: dict[str, tuple[str, list[str], int]] = {}
for f in sorted((root / "src/lodge/core").glob("*.py")):
    for c in ast.parse(f.read_text()).body:
        if isinstance(c, ast.ClassDef) and any("dataclass" in ast.unparse(d) for d in c.decorator_list):
            fields = [s.target.id for s in c.body if isinstance(s, ast.AnnAssign)]
            required = sum(1 for s in c.body if isinstance(s, ast.AnnAssign) and s.value is None)
            if required < len(fields):
                classes[c.name] = (f.name, fields, required)
filled: dict[str, list[str]] = {name: [] for name in classes}
for f in sorted([*(root / "src/lodge").rglob("*.py"), *(root / "tests").rglob("*.py")]):
    tree = ast.parse(f.read_text())
    own = {c.name for c in tree.body if isinstance(c, ast.ClassDef)} if not f.is_relative_to(root / "src/lodge/core") else set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and getattr(n.func, "id", None) not in own and isinstance(n.func, ast.Name) and n.func.id in classes:
            _, fields, _ = classes[n.func.id]
            if any(isinstance(a, ast.Starred) for a in n.args) or any(k.arg is None for k in n.keywords):
                continue
            given = set(fields[: len(n.args)]) | {k.arg for k in n.keywords}
            if set(fields) - given:
                filled[n.func.id].append(f"{f.relative_to(root)}:{n.lineno}")
for name, (module, _, _) in classes.items():
    calls = filled[name]
    print(f"{module} {name}: {len(calls)} calls leave a default out", calls[:2])
