import sys
from pathlib import Path

CORE_TESTS = str(Path(__file__).resolve().parents[1] / "core")
if CORE_TESTS not in sys.path:
    sys.path.insert(0, CORE_TESTS)
