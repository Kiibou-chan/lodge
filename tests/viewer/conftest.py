import sys
from pathlib import Path

for sibling in ("core", "app"):
    path = str(Path(__file__).resolve().parents[1] / sibling)
    if path not in sys.path:
        sys.path.insert(0, path)
