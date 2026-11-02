import { doubtMarks } from "./doubts.ts";
import { Action, type Decision } from "./model.ts";
import type { Snapshot } from "./snapshot.ts";
import { orderInstant } from "./stamps.ts";
import { byCodePoint } from "./text.ts";

type Status = "current" | "replaced" | "retired";
type Links = ReadonlyMap<string, readonly string[]>;
/** Each list of decisions is newest first, ties by ID.
 * Maps hold known records only, so dangling targets leave no trace.
 * A reviving decision replaces the last standing retirement and counts as changing the entry.
 */
export interface Derived {
  readonly status: ReadonlyMap<string, Status>;
  readonly replacedBy: Links;
  readonly narrowedBy: Links;
  readonly changedBy: Links;
  readonly confirmedBy: Links;
  readonly awaitingAuthor: ReadonlySet<string>;
  readonly touchedByFlagged: Links;
  readonly revived: Links;
  readonly linkedBy: Links;
  readonly supports: Links;
  readonly doubts: Links;
}
function orderKey(d: Decision): readonly [number, string] {
  return [orderInstant(d.date), d.id];
}
export function compareOrderKeys(a: Decision, b: Decision): number {
  const [at, ai] = orderKey(a),
    [bt, bi] = orderKey(b);
  return at - bt || byCodePoint(ai, bi);
}
function append<T>(map: Map<string, T[]>, key: string, value: T): void {
  const values = map.get(key) ?? [];
  values.push(value);
  map.set(key, values);
}
function reverse(
  newest: readonly Decision[],
  targetsOf: (d: Decision) => Iterable<string>,
  known: ReadonlyMap<string, unknown>,
): Links {
  const found = new Map<string, string[]>();
  for (const d of newest)
    for (const target of targetsOf(d)) if (known.has(target)) append(found, target, d.id);
  return found;
}
function revivedEntries(oldest: readonly Decision[], replacedBy: Links): Map<string, string[]> {
  const retirements = new Map<string, string[]>();
  for (const d of oldest) {
    for (const entry of new Set(
      d.changes.filter((c) => c.action === Action.RETIRE).map((c) => c.entry),
    ))
      append(retirements, entry, d.id);
  }
  const order = new Map(oldest.map((d, i) => [d.id, i]));
  const first = (id: string): number | null => {
    const replacements = replacedBy.get(id) ?? [];
    return replacements.length
      ? Math.min(...replacements.map((r) => order.get(r) as number))
      : null;
  };
  const found = new Map<string, string[]>();
  for (const [entry, ids] of retirements) {
    for (const retirement of ids) {
      const at = first(retirement);
      if (at === null) continue;
      const reviver = (oldest[at] as Decision).id;
      if (ids.includes(reviver)) continue;
      const others = ids.filter((u) => u !== retirement && (order.get(u) as number) < at);
      if (
        others.every((u) => {
          const f = first(u);
          return f !== null && f <= at;
        }) &&
        !found.get(reviver)?.includes(entry)
      )
        append(found, reviver, entry);
    }
  }
  return found;
}
export function derive(s: Snapshot): Derived {
  const oldest = [...s.decisions.values()].sort(compareOrderKeys);
  const newest = [...oldest].reverse();
  const replacedBy = reverse(newest, (d) => d.replaces, s.decisions);
  const narrowedBy = reverse(newest, (d) => d.narrows, s.decisions);
  const revived = revivedEntries(oldest, replacedBy);
  const touches = new Map(
    oldest.map((d) => [
      d.id,
      [
        ...new Set([
          ...d.changes.filter((c) => c.action !== Action.LINK).map((c) => c.entry),
          ...(revived.get(d.id) ?? []),
        ]),
      ],
    ]),
  );
  const changedBy = reverse(newest, (d) => touches.get(d.id) ?? [], s.entries);
  const confirmedBy = reverse(newest, (d) => (isAuthor(d) ? d.confirms : []), s.decisions);
  const retired = new Set(
    oldest
      .filter((d) => !replacedBy.has(d.id))
      .flatMap((d) => d.changes.filter((c) => c.action === Action.RETIRE).map((c) => c.entry)),
  );
  const status = new Map<string, Status>();
  for (const id of s.decisions.keys()) status.set(id, replacedBy.has(id) ? "replaced" : "current");
  for (const id of s.entries.keys()) status.set(id, retired.has(id) ? "retired" : "current");
  const changes = new Map<string, Decision[]>();
  for (const d of oldest) for (const entry of touches.get(d.id) ?? []) append(changes, entry, d);
  const hers = confirmedByHer(oldest);
  const awaitingAuthor = flagged(s, oldest, touches, changes, hers);
  const touchedByFlagged = new Map<string, string[]>();
  for (const d of newest) {
    if (!awaitingAuthor.has(d.id)) continue;
    const entries = touches.get(d.id) ?? [];
    const behind = behindEntryEdits(d, entries, changes, countsFor(d, hers), replacedBy);
    const targets = new Set([...d.replaces, ...d.narrows, ...entries, ...behind]);
    for (const target of [...targets].sort(byCodePoint))
      if (s.decisions.has(target) || s.entries.has(target)) append(touchedByFlagged, target, d.id);
  }
  const linkedBy = reverse(
    newest,
    (d) => d.changes.filter((c) => c.action === Action.LINK).map((c) => c.entry),
    s.entries,
  );
  const supports = new Map<string, string[]>();
  for (const id of [...s.entries.keys()].sort(byCodePoint)) {
    for (const target of new Set(s.entries.get(id)?.restsOn ?? []))
      if (s.entries.has(target)) append(supports, target, id);
  }
  return {
    status,
    replacedBy,
    narrowedBy,
    changedBy,
    confirmedBy,
    awaitingAuthor,
    touchedByFlagged,
    revived: new Map(
      [...revived]
        .map(([id, entries]) => [id, entries.filter((e) => s.entries.has(e))] as const)
        .filter(([, entries]) => entries.length),
    ),
    linkedBy,
    supports,
    doubts: doubtMarks(s, changedBy),
  };
}

export function isAuthor(d: Decision): boolean {
  return d.decidedBy === "author";
}
function confirmedByHer(oldest: readonly Decision[]): Set<string> {
  return new Set(
    oldest.filter((d) => isAuthor(d) && d.importedFrom === null).flatMap((d) => d.confirms),
  );
}
// An imported decision is flagged only by non-imported ones.
function countsFor(d: Decision, hers: ReadonlySet<string>): (other: Decision) => boolean {
  return (other) =>
    (isAuthor(other) || hers.has(other.id)) &&
    (d.importedFrom === null || other.importedFrom === null);
}
function behindEntryEdits(
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
    if (!isAuthor(later) || later.importedFrom !== null) continue;
    for (const target of later.replaces) {
      const other = s.decisions.get(target);
      if (other && !isAuthor(other) && !hers.has(target)) undone.add(target);
    }
  }
  const found = new Set<string>();
  for (const d of oldest) {
    if (clearedIds.has(d.id) || (isAuthor(d) && d.importedFrom === null)) continue;
    const counts = countsFor(d, hers);
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
    if (!isAuthor(later) || later.importedFrom !== null) continue;
    for (const id of [...later.confirms, ...later.replaces]) {
      const target = s.decisions.get(id);
      if (target && compareOrderKeys(target, later) < 0) found.add(id);
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
