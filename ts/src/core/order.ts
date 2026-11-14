import type { Derived } from "./derive.ts";
import type { SpecEntry } from "./model.ts";
import type { Snapshot } from "./snapshot.ts";
import { byCodePoint } from "./text.ts";

export interface Placement {
  readonly id: string;
  readonly depth: number;
  readonly under: string | null;
}
export function areaNames(s: Snapshot): readonly string[] {
  const names = new Set([...s.areas.keys(), ...[...s.entries.values()].map((e) => e.area)]);
  return [...names].sort((a, b) => {
    const ar = s.areas.get(a)?.rank ?? null;
    const br = s.areas.get(b)?.rank ?? null;
    return Number(ar === null) - Number(br === null) || (ar ?? 0) - (br ?? 0) || byCodePoint(a, b);
  });
}
export function writtenOrder(s: Snapshot, d: Derived, area: string): readonly string[] {
  const current = new Set(
    [...s.entries]
      .filter(([id, e]) => e.area === area && d.status.get(id) === "current")
      .map(([id]) => id),
  );
  const ordered = (s.areas.get(area)?.order ?? []).filter((id) => current.has(id));
  return [
    ...new Set([
      ...ordered,
      ...[...current].filter((id) => !ordered.includes(id)).sort(byCodePoint),
    ]),
  ];
}
export function derivedOrder(s: Snapshot, d: Derived, area: string): readonly Placement[] {
  const ordered = writtenOrder(s, d, area);
  const targets = new Map(
    ordered.map((id) => [
      id,
      (s.entries.get(id) as SpecEntry).restsOn.filter((t) => ordered.includes(t)),
    ]),
  );
  const placed = new Map<string, Placement>();
  const result: Placement[] = [];
  function visit(id: string, under: string | null = null): void {
    const depth = under === null ? 0 : (placed.get(under) as Placement).depth + 1;
    const p = { id, depth, under };
    placed.set(id, p);
    result.push(p);
    let child = ordered.find(
      (j) =>
        !placed.has(j) &&
        (targets.get(j) as readonly string[]).includes(id) &&
        (targets.get(j) as readonly string[]).every((t) => placed.has(t)),
    );
    while (child !== undefined) {
      visit(child, id);
      child = ordered.find(
        (j) =>
          !placed.has(j) &&
          (targets.get(j) as readonly string[]).includes(id) &&
          (targets.get(j) as readonly string[]).every((t) => placed.has(t)),
      );
    }
  }
  let remaining = ordered.filter((id) => !placed.has(id));
  while (remaining.length) {
    const ready =
      remaining.find((id) => (targets.get(id) as readonly string[]).every((t) => placed.has(t))) ??
      (remaining[0] as string);
    visit(ready);
    remaining = ordered.filter((id) => !placed.has(id));
  }
  return result;
}
export interface Branch {
  readonly id: string;
  readonly title: string;
  readonly status: string;
  readonly children: readonly Branch[];
}
export function restsOnTree(s: Snapshot, d: Derived, entryId: string): readonly Branch[] {
  const expanded = new Set([entryId]);
  function branch(target: string, ancestors: ReadonlySet<string>): Branch {
    const seen = expanded.has(target);
    expanded.add(target);
    return {
      id: target,
      title: (s.entries.get(target) as SpecEntry).title,
      status: d.status.get(target) as string,
      children: seen ? [] : children(target, new Set([...ancestors, target])),
    };
  }
  function children(id: string, ancestors: ReadonlySet<string>): readonly Branch[] {
    const entry = s.entries.get(id);
    if (!entry) return [];
    return [...new Set(entry.restsOn)]
      .filter((t) => s.entries.has(t) && !ancestors.has(t))
      .map((t) => branch(t, ancestors));
  }
  return children(entryId, new Set([entryId]));
}
