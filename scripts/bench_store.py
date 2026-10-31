"""Build a synthetic store of a given size for timing lodge's reads.

  uv run python scripts/bench_store.py DIR --decisions N [--seed S]

Writes a git repository at DIR in checkout mode, every record through lodge's own writer, committed once.
The project is made up: a harbour's cargo scheduling, so no real project's records appear.
About one decision in four edits an existing entry; the rest create one, so entries come to about three quarters of N.
"""

import argparse
import random
import subprocess
from pathlib import Path

from lodge.core import Action, Area, Change, Decision, Scope, SpecEntry
from lodge.core.fileformat import area_path, new_record_path, write_area, write_record
from lodge.core.ids import mint_id

WORDS = (
    "berth crane manifest pallet tide pilot quay ledger hold draught tug lock gantry convoy "
    "reefer bunker lashing stow sling hatch winch bollard fender dredge buoy channel mooring "
    "customs tally weighbridge forklift straddle carrier yard gate slot window shift crew "
    "roster tariff invoice claim damage survey seal container chassis rail barge feeder"
).split()
AREAS_PER_THOUSAND = 25


def sentence(rng: random.Random, n: int) -> str:
    words = [rng.choice(WORDS) for _ in range(n)]
    return " ".join(words).capitalize() + "."


def fresh(rng: random.Random, prefix: str, used: set[str]) -> str:
    while True:
        ident = mint_id(prefix, bytes(rng.randrange(256) for _ in range(6)))  # type: ignore[arg-type]
        if ident not in used:
            used.add(ident)
            return ident


def build(root: Path, decisions: int, seed: int) -> None:
    rng = random.Random(seed)
    used: set[str] = set()
    areas = [f"area-{i:03d}" for i in range(max(2, decisions * AREAS_PER_THOUSAND // 1000))]
    entries: dict[str, SpecEntry] = {}
    order: dict[str, list[str]] = {a: [] for a in areas}
    files: dict[str, str] = {}
    for n in range(decisions):
        date = f"2026-{1 + n * 12 // decisions:02d}-{1 + n % 28:02d}T12:{n % 60:02d}:{(n // 60) % 60:02d}+00:00"
        if entries and rng.random() < 0.25:
            old = entries[rng.choice(list(entries))]
            entry = SpecEntry(
                old.id, old.area, old.title, sentence(rng, 25), old.code, None, old.rests_on
            )
            action = Action.EDIT
        else:
            area = rng.choice(areas)
            rests = (
                tuple(rng.sample(order[area], min(2, len(order[area]))))
                if rng.random() < 0.3
                else ()
            )
            entry = SpecEntry(
                fresh(rng, "s", used),
                area,
                sentence(rng, 6).rstrip("."),
                sentence(rng, 25),
                None,
                None,
                rests,
            )
            order[area].append(entry.id)
            action = Action.CREATE
        entries[entry.id] = entry
        d = Decision(
            id=fresh(rng, "d", used),
            title=sentence(rng, 7).rstrip("."),
            scope=Scope.PRODUCT if rng.random() < 0.8 else Scope.PROCESS,
            decided_by="coordinator",
            date=date,
            statement=sentence(rng, 20),
            reasoning=sentence(rng, 40) + "\n" + sentence(rng, 30),
            code=f"CODE-{n}" if rng.random() < 0.3 else None,
            changes=(Change(entry.id, action),),
        )
        files[new_record_path(d)] = write_record(d)
    for entry in entries.values():
        files[new_record_path(entry)] = write_record(entry)
    for i, a in enumerate(areas):
        files[area_path(a)] = write_area(
            Area(a, f"Area {i}", sentence(rng, 12), tuple(order[a]), i + 1)
        )
    root.mkdir(parents=True)
    for path, text in files.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    (root / ".lodge.toml").write_text('[store]\nmode = "checkout"\n', encoding="utf-8")
    env = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1", "PATH": "/usr/bin:/bin"}
    for args in (
        ["init", "-q", "-b", "main"],
        ["add", "-A"],
        [
            "-c",
            "user.name=bench",
            "-c",
            "user.email=bench@example.invalid",
            "commit",
            "-q",
            "-m",
            "bench",
        ],
    ):
        subprocess.run(["git", *args], cwd=root, check=True, env=env)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("dir", type=Path)
    p.add_argument("--decisions", type=int, required=True)
    p.add_argument("--seed", type=int, default=1)
    a = p.parse_args()
    build(a.dir, a.decisions, a.seed)


if __name__ == "__main__":
    main()
