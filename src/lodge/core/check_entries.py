"""Check 4: each entry created, edited, or retired is named by a decision of the same change."""

from collections.abc import Iterator

from lodge.core.check_state import new_decisions, problem_at
from lodge.core.derive import derive
from lodge.core.model import Action, Problem, Record
from lodge.core.settings import CoreSettings
from lodge.core.snapshot import Snapshot


def check_entries(
    published: Snapshot, after: Snapshot, settings: CoreSettings
) -> Iterator[Problem]:
    added = new_decisions(published, after)
    listed = {(c.entry, c.action) for d in added for c in d.changes}
    was = derive(published).status
    now = derive(after).status
    for entry_id in sorted(after.entries):
        entry = after.entries[entry_id]
        before = published.entries.get(entry_id)
        wanted = []
        if before is None:
            wanted.append((Action.CREATE, "created"))
        elif before != entry:
            wanted.append((Action.EDIT, "edited"))
        if now[entry_id] == "retired" and was.get(entry_id) != "retired":
            wanted.append((Action.RETIRE, "retired"))
        exempt = before is None and entry.imported_from is not None
        for action, verb in wanted:
            if not exempt and (entry_id, action) not in listed:
                message = (
                    f"{verb}, but no new decision in this change lists it with action {action}; "
                    "list it in the decision's changes"
                )
                yield problem_at(after, entry_id, 4, message)
    for d in added:
        for change in dict.fromkeys(d.changes):
            if change.action is Action.CREATE and change.entry in published.entries:
                message = f"lists create for {change.entry}, which already exists"
                yield problem_at(after, d.id, 4, message)
    yield from _unlisted_sources(published, after, settings)


def _unlisted_sources(
    published: Snapshot, after: Snapshot, settings: CoreSettings
) -> Iterator[Problem]:
    new: list[Record] = [
        *new_decisions(published, after),
        *(e for i, e in sorted(after.entries.items()) if i not in published.entries),
    ]
    for record in new:
        source = record.imported_from
        if source is not None and source.file not in settings.import_sources:
            message = f"imported from {source.file}, which is not listed in [import] sources"
            yield problem_at(after, record.id, 4, message)
