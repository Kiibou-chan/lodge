"""Print the Python core's differential reference without changing the store."""

import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path

from lodge.core import (
    Filters,
    Problem,
    Tree,
    check_state,
    derive,
    failing_ids,
    format_level1,
    format_level3,
    level1,
    level2,
    level3,
    load,
    parse_area,
    parse_core_settings,
    parse_record,
    render_spec,
    search,
    write_area,
    write_record,
)


def main() -> None:
    root = Path(sys.argv[1])
    files = {
        path.relative_to(root).as_posix(): path.read_bytes().decode("utf-8")
        for path in sorted((root / "lodge").rglob("*"))
        if path.is_file()
    }
    table = tomllib.loads((root / ".lodge.toml").read_text(encoding="utf-8"))
    parse_core_settings({key: table[key] for key in ("length", "import") if key in table})
    snapshot = load(Tree(None, files))
    derived = derive(snapshot)
    checked = check_state(snapshot)
    failing = failing_ids(snapshot, checked)
    records = {**snapshot.decisions, **snapshot.entries}
    levels = {
        rid: [
            format_level1(level1(snapshot, derived, rid, failing)),
            level2(snapshot, derived, rid, failing),
            format_level3(level3(snapshot, derived, rid)),
        ]
        for rid in records
    }
    queries = {record.title.split()[0] for record in records.values() if record.title.split()}
    rewrite = {}
    for path, text in files.items():
        if path.startswith("lodge/spec/") and path.endswith("/_area.md"):
            area = parse_area(path, text)
            if isinstance(area, Problem):
                continue
            written = write_area(area)
        elif re.fullmatch(r"lodge/(?:decisions/[^/]+|spec/[^/]+/[^/]+)\.md", path):
            record = parse_record(path, text)
            if isinstance(record, Problem):
                continue
            written = write_record(record)
        else:
            continue
        rewrite[path] = [hashlib.sha256(written.encode("utf-8")).hexdigest(), written == text]
    result = {
        "spec": render_spec(snapshot, derived, failing),
        "problems": sorted((p.path, p.check, p.line, p.message) for p in checked.problems),
        "levels": levels,
        "search": {q: search(snapshot, derived, q, Filters(), 20) for q in sorted(queries)},
        "rewrite": rewrite,
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
