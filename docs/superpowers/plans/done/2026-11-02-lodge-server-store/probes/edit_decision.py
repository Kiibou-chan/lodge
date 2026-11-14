import sys
sys.path[:0] = ["tests/core", "tests/app"]
from support import project, wired, FIRST
from lodge.app import LodgeError
store = project()
lodge = wired(store)
d = lodge.draft("d-aaaaaa").replace(FIRST.statement, "Transcripts are deleted after a day.")
try:
    added = lodge.add([("d.md", d)])
    print("outcome", added.outcome, [(p.check, p.message) for p in added.check.problems])
except LodgeError as e:
    print("refused", type(e).__name__, e)
d2 = lodge.draft("d-aaaaaa").replace("Because they are evidence.", "Because.")
try:
    added = lodge.add([("d.md", d2)])
    print("outcome", added.outcome, [(p.check, p.message) for p in added.check.problems])
except LodgeError as e:
    print("refused", type(e).__name__, e)
print("show flags", lodge.show("ITEM-1").level1.flags, "problems ok", lodge.problems()[0].ok)
