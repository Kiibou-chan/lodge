import type { Decision } from "./model.ts";
import type { Snapshot } from "./snapshot.ts";

export function isAuthor(d: Decision): boolean {
  return d.decidedBy === "author";
}
export function confirmedByHer(oldest: readonly Decision[]): Set<string> {
  return new Set(
    oldest.filter((d) => isAuthor(d) && d.importedFrom === null).flatMap((d) => d.confirms),
  );
}
export function countsFor(d: Decision, hers: ReadonlySet<string>): (other: Decision) => boolean {
  return (other) =>
    (isAuthor(other) || hers.has(other.id)) &&
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
export function flagged(
  s: Snapshot,
  oldest: readonly Decision[],
  touches: ReadonlyMap<string, readonly string[]>,
  changes: ReadonlyMap<string, readonly Decision[]>,
  hers: ReadonlySet<string>,
): Set<string> {
  const cleared = new Set<string>();
  const undone = new Set<string>();
  const order = new Map(oldest.map((d, i) => [d.id, i]));
  for (const later of oldest) {
    if (!isAuthor(later) || later.importedFrom !== null) continue;
    for (const target of [...later.confirms, ...later.replaces]) {
      const index = order.get(target);
      if (index !== undefined && index < (order.get(later.id) as number)) cleared.add(target);
    }
    for (const target of later.replaces) {
      const other = s.decisions.get(target);
      if (other && !isAuthor(other) && !hers.has(target)) undone.add(target);
    }
  }
  const found = new Set<string>();
  for (const d of oldest) {
    if (cleared.has(d.id) || (isAuthor(d) && d.importedFrom === null)) continue;
    const counts = countsFor(d, hers);
    const touchesAuthor = [...d.replaces, ...d.narrows].some((t) => {
      const other = s.decisions.get(t);
      return other !== undefined && counts(other);
    });
    const followsAuthor = (touches.get(d.id) as readonly string[]).some((entry) => {
      const edits = changes.get(entry) as readonly Decision[];
      const before = edits.slice(0, edits.indexOf(d)).filter((c) => !undone.has(c.id));
      const last = before.at(-1);
      return last !== undefined && counts(last);
    });
    if (touchesAuthor || followsAuthor) found.add(d.id);
  }
  return found;
}
