import { type Problem, problem } from "./model.ts";
import type { Snapshot } from "./snapshot.ts";
import { byCodePoint } from "./text.ts";
export function* checkCycles(s: Snapshot): Generator<Problem> {
  const reach = new Map<string, Set<string>>();
  for (const [id, entry] of s.entries) {
    const found = new Set<string>(),
      pending = [...entry.restsOn];
    while (pending.length) {
      const target = pending.pop() as string;
      const linked = s.entries.get(target);
      if (found.has(target) || !linked) continue;
      found.add(target);
      pending.push(...linked.restsOn);
    }
    reach.set(id, found);
  }
  for (const id of [...reach.keys()].sort(byCodePoint)) {
    const targets = reach.get(id) as Set<string>;
    const others = [...targets].filter((t) => t !== id && reach.get(t)?.has(id)).sort(byCodePoint);
    if (targets.has(id) && others.length)
      yield problem({
        path: s.paths.get(id) ?? "",
        check: 8,
        message: `${id}: is in a cycle of rests_on links with ${others.join(", ")}`,
      });
  }
}
