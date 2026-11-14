import type { Decision } from "./model.ts";
import type { Snapshot } from "./snapshot.ts";
import { byCodePoint } from "./text.ts";

export function reviewFlags(
  s: Snapshot,
  oldest: readonly Decision[],
  touches: ReadonlyMap<string, readonly string[]>,
  changes: ReadonlyMap<string, readonly Decision[]>,
): ReadonlyMap<string, readonly string[]> {
  const awaiting = new Map<string, string[]>();
  for (const person of [...s.people].sort(byCodePoint)) {
    const people = new Set([person]);
    const confirmed = confirmedByPeople(oldest, people);
    for (const id of flagged(s.decisions, s.people, person, oldest, touches, changes, confirmed)) {
      const parts = awaiting.get(id) ?? [];
      parts.push(person);
      awaiting.set(id, parts);
    }
  }
  return awaiting;
}
export function countsForPeople(
  oldest: readonly Decision[],
  people: ReadonlySet<string>,
  d: Decision,
): (other: Decision) => boolean {
  return countsFor(d, confirmedByPeople(oldest, people), people);
}
function confirmedByPeople(oldest: readonly Decision[], people: ReadonlySet<string>): Set<string> {
  return new Set(
    oldest
      .filter((d) => people.has(d.decidedBy) && d.importedFrom === null)
      .flatMap((d) => d.confirms),
  );
}
// An imported decision is flagged only by non-imported ones.
function countsFor(
  d: Decision,
  confirmed: ReadonlySet<string>,
  people: ReadonlySet<string>,
): (other: Decision) => boolean {
  return (other) =>
    (people.has(other.decidedBy) || confirmed.has(other.id)) &&
    (d.importedFrom === null || other.importedFrom === null);
}
export function behindEntryEdits(
  d: Decision,
  entries: readonly string[],
  changes: ReadonlyMap<string, readonly Decision[]>,
  counts: (other: Decision) => boolean,
  replacedBy: ReadonlyMap<string, readonly string[]>,
): string[] {
  const behind: string[] = [];
  for (const entry of entries) {
    const edits = changes.get(entry) as readonly Decision[];
    const standing = edits.slice(0, edits.indexOf(d)).filter((c) => !replacedBy.has(c.id));
    const last = standing.at(-1);
    if (last && counts(last)) behind.push(last.id);
  }
  return behind;
}
// Skip changes undone by the person when that person has not confirmed them.
function flagged(
  decisions: ReadonlyMap<string, Decision>,
  people: ReadonlySet<string>,
  person: string,
  oldest: readonly Decision[],
  touches: ReadonlyMap<string, readonly string[]>,
  changes: ReadonlyMap<string, readonly Decision[]>,
  confirmed: ReadonlySet<string>,
): Set<string> {
  const personOnly = new Set([person]);
  const clearedIds = cleared(decisions, person, oldest);
  const undone = new Set<string>();
  for (const later of oldest) {
    if (later.decidedBy !== person || later.importedFrom !== null) continue;
    for (const target of later.replaces) {
      const other = decisions.get(target);
      if (other && other.decidedBy !== person && !confirmed.has(target)) undone.add(target);
    }
  }
  const found = new Set<string>();
  for (const d of oldest) {
    if (clearedIds.has(d.id) || (people.has(d.decidedBy) && d.importedFrom === null)) continue;
    const counts = countsFor(d, confirmed, personOnly);
    const touchesPerson = [...d.replaces, ...d.narrows].some((t) => {
      const other = decisions.get(t);
      return other !== undefined && counts(other);
    });
    const followsPerson = (touches.get(d.id) as readonly string[]).some((entry) =>
      followsPersonChange(d, counts, changes.get(entry) as readonly Decision[], undone),
    );
    if (touchesPerson || followsPerson) found.add(d.id);
  }
  return found;
}

// Decisions confirmed or replaced by a later, non-imported decision of the person.
function cleared(
  decisions: ReadonlyMap<string, Decision>,
  person: string,
  oldest: readonly Decision[],
): Set<string> {
  const found = new Set<string>();
  for (const later of oldest) {
    if (later.decidedBy !== person || later.importedFrom !== null) continue;
    for (const id of [...later.confirms, ...later.replaces]) {
      const target = decisions.get(id);
      if (target && oldest.indexOf(target) < oldest.indexOf(later)) found.add(id);
    }
  }
  return found;
}
// Whether the latest preceding change, skipping undone changes, raises a flag.
function followsPersonChange(
  d: Decision,
  counts: (other: Decision) => boolean,
  edits: readonly Decision[],
  undone: ReadonlySet<string>,
): boolean {
  const before = edits.slice(0, edits.indexOf(d)).filter((c) => !undone.has(c.id));
  const last = before.at(-1);
  return last !== undefined && counts(last);
}
