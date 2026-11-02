import { derive } from "./derive.ts";
import type { Draft } from "./drafts.ts";
import { ValueError } from "./errors.ts";
import { areaPath, writeArea } from "./fileformat.ts";
import { type Area, type Problem, problem, type SpecEntry } from "./model.ts";
import { load, type Snapshot, type Tree, tree } from "./snapshot.ts";

export interface Add {
  readonly current: Snapshot;
  readonly tree: Tree;
  readonly date: string;
  readonly importing: boolean;
  readonly newIds: string[];
  readonly draftedAreas: ReadonlySet<unknown>;
  readonly files: Map<string, string>;
  readonly ids: string[];
  readonly areas: Map<string, Area>;
  readonly newEntries: SpecEntry[];
  readonly retired: Set<string>;
}
export function refuse(draft: Draft, message: string): Problem {
  return problem({ path: draft.source, check: 1, message });
}
export function areaFiles(add: Add): Problem[] {
  const gained = new Map<string, string[]>();
  function gain(name: string, id: string) {
    const ids = gained.get(name) ?? [];
    ids.push(id);
    gained.set(name, ids);
  }
  for (const entry of add.newEntries) gain(entry.area, entry.id);
  for (const id of restored(add)) gain((add.current.entries.get(id) as SpecEntry).area, id);
  const lost = [...add.retired].flatMap((id) => {
    const entry = add.current.entries.get(id);
    return entry ? [entry.area] : [];
  });
  const problems: Problem[] = [];
  for (const name of [...new Set([...add.areas.keys(), ...gained.keys(), ...lost])].sort()) {
    const start = add.areas.get(name) ?? add.current.areas.get(name);
    if (!start) continue;
    const order = start.order.filter((id) => !add.retired.has(id));
    order.push(
      ...(gained.get(name) ?? []).filter((id) => !order.includes(id) && !add.retired.has(id)),
    );
    const area = { ...start, order };
    if (
      add.areas.has(name) ||
      order.length !== start.order.length ||
      order.some((id, i) => id !== start.order[i])
    ) {
      try {
        add.files.set(areaPath(name), writeArea(area));
      } catch (error) {
        if (!(error instanceof ValueError)) throw error;
        problems.push(problem({ path: areaPath(name), check: 1, message: error.message }));
      }
    }
  }
  return problems;
}
function restored(add: Add): string[] {
  const was = derive(add.current).status;
  if (![...was.values()].includes("retired")) return [];
  const now = derive(
    load(tree({ rev: add.tree.rev, files: new Map([...add.tree.files, ...add.files]) })),
  ).status;
  return [...add.current.entries.keys()]
    .filter((id) => was.get(id) === "retired" && now.get(id) === "current")
    .sort();
}
