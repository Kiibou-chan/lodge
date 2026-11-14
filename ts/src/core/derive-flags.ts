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
    const hers = confirmedByHer(oldest, people);
    for (const id of flagged({ ...s, people }, oldest, touches, changes, hers)) {
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
  return countsFor(d, confirmedByHer(oldest, people), people);
}
function confirmedByHer(oldest: readonly Decision[], people: ReadonlySet<string>): Set<string> {
  return new Set(
    oldest
      .filter((d) => people.has(d.decidedBy) && d.importedFrom === null)
      .flatMap((d) => d.confirms),
  );
}
// An imported decision is flagged only by non-imported ones.
function countsFor(
  d: Decision,
  hers: ReadonlySet<string>,
  people: ReadonlySet<string>,
): (other: Decision) => boolean {
  return (other) =>
    (people.has(other.decidedBy) || hers.has(other.id)) &&
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
// Skip changes undone by a non-imported author replacement when they are not hers.
function flagged(
  s: Snapshot,
  oldest: readonly Decision[],
  touches: ReadonlyMap<string, readonly string[]>,
  changes: ReadonlyMap<string, readonly Decision[]>,
  hers: ReadonlySet<string>,
): Set<string> {
  const clearedIds = cleared(s, oldest);
  const undone = new Set<string>();
  for (const later of oldest) {
    if (!s.people.has(later.decidedBy) || later.importedFrom !== null) continue;
    for (const target of later.replaces) {
      const other = s.decisions.get(target);
      if (other && !s.people.has(other.decidedBy) && !hers.has(target)) undone.add(target);
    }
  }
  const found = new Set<string>();
  for (const d of oldest) {
    if (clearedIds.has(d.id) || (s.people.has(d.decidedBy) && d.importedFrom === null)) continue;
    const counts = countsFor(d, hers, s.people);
    const touchesAuthor = [...d.replaces, ...d.narrows].some((t) => {
      const other = s.decisions.get(t);
      return other !== undefined && counts(other);
    });
    const followsAuthor = (touches.get(d.id) as readonly string[]).some((entry) =>
      followsAuthorChange(d, counts, changes.get(entry) as readonly Decision[], undone),
    );
    if (touchesAuthor || followsAuthor) found.add(d.id);
  }
  return found;
}

// Decisions confirmed or replaced by a later, non-imported author decision.
function cleared(s: Snapshot, oldest: readonly Decision[]): Set<string> {
  const found = new Set<string>();
  for (const later of oldest) {
    if (!s.people.has(later.decidedBy) || later.importedFrom !== null) continue;
    for (const id of [...later.confirms, ...later.replaces]) {
      const target = s.decisions.get(id);
      if (target && oldest.indexOf(target) < oldest.indexOf(later)) found.add(id);
    }
  }
  return found;
}
// Whether the latest preceding change, skipping undone changes, raises a flag.
function followsAuthorChange(
  d: Decision,
  counts: (other: Decision) => boolean,
  edits: readonly Decision[],
  undone: ReadonlySet<string>,
): boolean {
  const before = edits.slice(0, edits.indexOf(d)).filter((c) => !undone.has(c.id));
  const last = before.at(-1);
  return last !== undefined && counts(last);
}
