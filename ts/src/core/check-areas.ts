import { derive } from "./derive.ts";
import { areaPath } from "./fileformat.ts";
import { type Problem, problem } from "./model.ts";
import type { Snapshot } from "./snapshot.ts";
import { byCodePoint } from "./text.ts";
export function* checkAreas(s: Snapshot): Generator<Problem> {
  const status = derive(s).status;
  const folders = new Set([...s.entries.values()].map((e) => e.area));
  for (const name of s.areas.keys()) folders.add(name);
  for (const name of [...folders].sort(byCodePoint)) {
    const entries = [...s.entries.values()]
      .filter((e) => e.area === name)
      .map((e) => e.id)
      .sort(byCodePoint);
    const area = s.areas.get(name);
    if (!area) {
      yield problem({
        path: areaPath(name),
        check: 7,
        message: `area ${name}: has entries but no _area.md`,
      });
      continue;
    }
    const current = new Set(entries.filter((id) => status.get(id) === "current"));
    for (const id of entries)
      if (current.has(id) && !area.order.includes(id))
        yield problem({
          path: s.paths.get(id) as string,
          check: 7,
          message: `${id}: is not listed in the order of area ${name}`,
        });
    for (const id of new Set(area.order)) {
      const message = !current.has(id)
        ? `area ${name}: order lists ${id}, which is not a current entry of the area`
        : area.order.filter((i) => i === id).length > 1
          ? `area ${name}: order lists ${id} more than once`
          : null;
      if (message !== null) yield problem({ path: areaPath(name), check: 7, message });
    }
  }
}
