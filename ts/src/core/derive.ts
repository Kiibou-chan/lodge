import { behindEntryEdits, confirmedByHer, countsFor, flagged, isAuthor } from "./derive-review.ts";
import { doubtMarks } from "./doubts.ts";
import { Action, type Decision } from "./model.ts";
import type { Snapshot } from "./snapshot.ts";
import { orderInstant } from "./stamps.ts";
import { byCodePoint } from "./text.ts";

export { isAuthor } from "./derive-review.ts";

type Status = "current" | "replaced" | "retired";
type Links = ReadonlyMap<string, readonly string[]>;
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
export function orderKey(d: Decision): readonly [number, string] {
  return [orderInstant(d.date), d.id];
}
function compare(a: Decision, b: Decision): number {
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
  const oldest = [...s.decisions.values()].sort(compare);
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
