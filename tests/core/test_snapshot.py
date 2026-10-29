from builders import area, decision, entry, files_of

from lodge.core import (
    Tree,
    check_state,
    derive,
    failing_ids,
    level1,
    load,
    new_record_path,
    unrecorded_problems,
)


def tree_of(files: dict[str, str], attachments: frozenset[str] = frozenset()) -> Tree:
    return Tree("abc123", files, attachments)


def test_load_keeps_good_records_beside_problems() -> None:
    good, spec, boxed = decision(id="d-aaaaaa"), entry(id="s-aaaaaa"), area()
    files = files_of(good, spec, boxed)
    bad = "lodge/decisions/d-bbbbbb-broken.md"
    files[bad] = "---\nid: d-bbbbbb\nkind: decision\n---\n\nNothing else.\n"
    snap = load(tree_of(files))
    assert snap.decisions == {"d-aaaaaa": good}
    assert snap.entries == {"s-aaaaaa": spec}
    assert snap.areas == {"storage": boxed}
    assert snap.paths == {"d-aaaaaa": new_record_path(good), "s-aaaaaa": new_record_path(spec)}
    assert [(p.path, p.check) for p in snap.problems] == [(bad, 1)]


def test_duplicate_id_is_problem_2_with_both_paths() -> None:
    first = decision(id="d-aaaaaa", title="First")
    second = decision(id="d-aaaaaa", title="Second")
    files = files_of(first) | files_of(second)
    snap = load(tree_of(files))
    kept, dropped = new_record_path(first), new_record_path(second)
    assert snap.decisions == {"d-aaaaaa": first}
    assert snap.paths == {"d-aaaaaa": kept}
    assert sorted((p.path, p.check) for p in snap.problems) == sorted([(kept, 2), (dropped, 2)])
    assert all(kept in p.message and dropped in p.message for p in snap.problems)


def test_stray_file_is_problem_1() -> None:
    files = {
        "lodge/notes.txt": "x",
        "lodge/decisions/readme.txt": "x",
        "lodge/spec/storage/deeper/s-aaaaaa-x.md": "x",
        "lodge/decisions/.gitkeep": "",
        "lodge/spec/storage/.gitkeep": "",
        "lodge/attachments/log.txt": "x",
        "README.md": "x",
    }
    snap = load(tree_of(files))
    assert sorted((p.path, p.check) for p in snap.problems) == [
        ("lodge/decisions/readme.txt", 1),
        ("lodge/notes.txt", 1),
        ("lodge/spec/storage/deeper/s-aaaaaa-x.md", 1),
    ]


def test_record_in_the_wrong_folder_is_problem_1() -> None:
    spec = entry(id="s-aaaaaa")
    misplaced = "lodge/decisions/s-aaaaaa-an-entry.md"
    snap = load(tree_of({misplaced: files_of(spec)[new_record_path(spec)]}))
    assert snap.entries == {}
    assert [(p.path, p.check) for p in snap.problems] == [(misplaced, 1)]


def test_attachments_listed_not_parsed() -> None:
    listed = frozenset({"lodge/attachments/run.log"})
    files = {"lodge/attachments/other.log": "not a record", **files_of(decision())}
    snap = load(tree_of(files, listed))
    assert snap.attachments == listed | {"lodge/attachments/other.log"}
    assert snap.problems == ()
    assert len(snap.decisions) == 1


def test_duplicate_id_marks_kept_record_failing() -> None:
    first = decision(id="d-aaaaaa", title="First", statement="A holds.")
    second = decision(id="d-aaaaaa", title="Second", statement="B holds.")
    snap = load(tree_of(files_of(first) | files_of(second)))
    result = check_state(snap)
    assert failing_ids(snap, result) == {"d-aaaaaa"}
    assert [p.path for p in unrecorded_problems(snap, result)] == [new_record_path(second)]
    assert "fails check" in level1(snap, derive(snap), "d-aaaaaa", failing_ids(snap, result)).flags
