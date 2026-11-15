"""Write the made-up lodge 0.2 store of zero-two-store/ as a TypeScript map of path to text."""

import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
paths = sorted(p for p in root.rglob("*") if p.is_file())
lines = [
    "// The made-up lodge 0.2 store of docs/superpowers/plans/2026-11-02-lodge-server-import/probes/zero-two-store/, written by lodge 0.2 (probe 6).",
    "export const ZERO_TWO_STORE: ReadonlyMap<string, string> = new Map([",
]
for path in paths:
    text = path.read_bytes().decode("utf-8")
    lines.append(f"  [{json.dumps(path.relative_to(root).as_posix())}, {json.dumps(text)}],")
lines.append("]);")
sys.stdout.write("\n".join(lines) + "\n")
