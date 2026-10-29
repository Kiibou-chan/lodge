import pytest
from applying import area_text, decision_text, spec_text
from fakes import MemoryStore
from support import AREA, wired

from lodge.app import AddOutcome, LodgeError
from lodge.core import Tree, load

LOG = ("run.log", "line one\nline two\n")
PATH = "lodge/attachments/d-111111/run.log"
ENTRY = spec_text("id: s-bbbbbb", "area: storage", body="Everything is kept.")


def new_decision(*extra: str) -> tuple[str, str]:
    created = ["changes:", "  - {entry: s-bbbbbb, action: create}"]
    return ("d.md", decision_text(*created, *extra))


def test_attachment_is_written_beside_the_new_decision() -> None:
    store = MemoryStore(AREA)
    added = wired(store).add(
        [new_decision("attachments: [run.log]"), ("s.md", ENTRY)], attachments=[LOG]
    )
    assert added.outcome is AddOutcome.PUBLISHED
    assert store.files[PATH] == LOG[1]
    assert PATH in store.publishes[0][0]
    s = load(Tree(None, store.files))
    assert s.decisions["d-111111"].attachments == ("run.log",)
    assert PATH in s.attachments


def test_dry_run_writes_no_attachment() -> None:
    store = MemoryStore(AREA)
    drafts = [new_decision("attachments: [run.log]"), ("s.md", ENTRY)]
    added = wired(store).add(drafts, dry_run=True, attachments=[LOG])
    assert added.outcome is AddOutcome.DRY_RUN
    assert store.publishes == [] and PATH not in store.files


def test_attachment_needs_exactly_one_new_decision() -> None:
    store = MemoryStore(AREA)
    with pytest.raises(LodgeError, match=r"--attach needs the add to create one decision, not 0"):
        wired(store).add([("a.md", area_text("name: storage"))], attachments=[LOG])
    two = [new_decision("attachments: [run.log]"), new_decision(), ("s.md", ENTRY)]
    with pytest.raises(LodgeError, match=r"--attach needs the add to create one decision, not 2"):
        wired(store).add(two, attachments=[LOG])
    assert store.attempts == 0


def test_decision_must_list_exactly_the_attached_names() -> None:
    store = MemoryStore(AREA)
    with pytest.raises(
        LodgeError, match=r"lists \[\] in attachments, but the attached files are \[run.log\]"
    ):
        wired(store).add([new_decision(), ("s.md", ENTRY)], attachments=[LOG])
    other = new_decision("attachments: [run.log, more.log]")
    with pytest.raises(LodgeError, match=r"lists \[more.log, run.log\] in attachments"):
        wired(store).add([other, ("s.md", ENTRY)], attachments=[LOG])
    assert store.attempts == 0


@pytest.mark.parametrize("name", ["", ".", "..", "a/b", "a\\b", ".git"])
def test_attachment_names_are_plain_file_names(name: str) -> None:
    drafts = [new_decision("attachments: [x]"), ("s.md", ENTRY)]
    with pytest.raises(LodgeError, match="not a plain file name"):
        wired(MemoryStore(AREA)).add(drafts, attachments=[(name, "x")])


def test_two_attachments_with_one_name_are_refused() -> None:
    drafts = [new_decision("attachments: [run.log]"), ("s.md", ENTRY)]
    with pytest.raises(LodgeError, match=r"run\.log is attached twice"):
        wired(MemoryStore(AREA)).add(drafts, attachments=[LOG, LOG])
