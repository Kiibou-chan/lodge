"""The short reading guide describes and demonstrates reads that work."""

import re
import shlex
from pathlib import Path

from e2e.conftest import Project
from e2e.support import decision_text, first_decision, seed

EXAMPLES = (
    'lodge search "several words" --brief',
    'lodge search --phrase "exact words in order" --brief',
    "lodge search CODE --brief",
    "lodge search word1 word2 --brief",
    "lodge show REF REF REF",
    "lodge show CODE.why --reasoning",
    "lodge show REF --provenance",
)


def test_guide_read_is_short_and_has_no_writing_rules(project: Project, tmp_path: Path) -> None:
    outside = tmp_path / "plain"
    outside.mkdir()
    result = project.run("guide", "--read", cwd=outside)
    assert (result.code, result.err) == (0, "")
    text = result.out
    assert 0 < len(text.splitlines()) <= 25
    assert all(word not in text for word in ("lodge add", "lodge draft", "decided_by", "—"))
    assert all(f"`{example}`" in text.splitlines() for example in EXAMPLES)
    for phrase in (
        "decision",
        "entry",
        "area",
        "start of a session",
        "all the words first",
        "quotes",
        "--phrase",
        "in order",
        "two queries",
        "family and citers first",
        "siblings",
        "citers",
        "awaiting the author",
        "in doubt",
        "fails check",
        "problem:",
        "unmarked",
        "current",
        "replaced",
        "retired",
    ):
        assert phrase in text.lower(), phrase


def test_guide_read_examples_run(project: Project) -> None:
    ids = seed(project)
    records = {
        ids.decision: "Keep transcripts\nTranscripts are kept.",
        ids.entry: "Transcripts are kept\nHeld.",
    }

    def add(title: str, body: str, *extra: str) -> str:
        result = project.run(
            "add", project.draft("example.md", decision_text(title, *extra, body=body))
        )
        assert result.code == 0, result
        ident = first_decision(result.out)
        records[ident] = f"{title}\n{body}"
        return ident

    sibling = add("Why keep transcripts", "For review.", "code: ITEM-1.why")
    add("Crane berth", "Both words, reversed.")
    add("Exact phrase", "Use the berth crane.")
    add("Crane", "Only one word.")
    guide = project.run("guide", "--read")
    assert (guide.code, guide.err) == (0, "")
    examples = re.findall(r"`(lodge [^`]+)`", guide.out)
    assert set(EXAMPLES) <= set(examples)
    for example in examples:
        command = example.replace("CODE", "ITEM-1")
        command = command.replace("several words", "berth crane")
        command = command.replace("exact words in order", "berth crane")
        command = command.replace("word1", "berth").replace("word2", "crane")
        refs = iter((ids.decision, ids.entry, sibling))
        args = [next(refs) if word == "REF" else word for word in shlex.split(command)[1:]]
        result = project.run(*args)
        assert (result.code, result.err) == (0, ""), (example, result)
        if example in EXAMPLES[:2]:
            first = re.search(r"^[ds]-[a-z0-9]{6}\b", result.out, re.MULTILINE)
            assert first is not None, result.out
            text = records[first.group()].lower()
            if "--phrase" in example:
                assert "berth crane" in text
            else:
                assert all(word in text for word in ("berth", "crane"))


def test_full_guide_points_at_read(project: Project) -> None:
    result = project.run("guide")
    assert (result.code, result.err) == (0, "")
    assert "lodge guide --read" in result.out
