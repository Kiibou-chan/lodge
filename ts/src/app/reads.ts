import {
  areaPath,
  byCodePoint,
  checkChange,
  checkResult,
  confirmableIds,
  contentHash,
  type Filters,
  instant,
  level1,
  level2,
  level2Views,
  level3,
  load,
  newestLast,
  type Problem,
  renderSpec,
  restsOnTree,
  type SpecArea,
  searchCounted,
  specView,
} from "#core";
import { LodgeError } from "./errors.ts";
import { type Listed, listed, type Read, type Shown } from "./results.ts";
import { notFound, readChecked, readState, resolveRef, type State, type Wiring } from "./state.ts";
import { waitingIn } from "./threads.ts";
import { stampOf } from "./time.ts";

export async function searchRecords(
  w: Wiring,
  query: string,
  filters: Filters,
  limit: number,
): Promise<Listed> {
  const state = await readChecked(w);
  const [ids, total] = searchCounted(state.snapshot, state.derived, query, filters, limit);
  return listed({ items: views(state, ids), read: state.read, more: total - ids.length });
}
export async function show(
  w: Wiring,
  ref: string,
  reasoning: boolean,
  provenance: boolean,
): Promise<Shown> {
  const state = await readChecked(w),
    id = resolveRef(state, ref),
    s = state.snapshot,
    d = state.derived;
  return {
    level1: level1(s, d, id, state.failing),
    level2: reasoning ? level2(s, d, id, state.failing) : null,
    level3: provenance ? level3(s, d, id) : null,
    read: state.read,
    changing: reasoning ? level2Views(s, d, id, state.failing) : [],
    threads: newestLast([...s.threads.values()].filter((t) => t.about === id)),
    confirmable: confirmableIds(s, d).has(id),
    restsOn: restsOnTree(s, d, id),
    supports: views(state, d.supports.get(id) ?? []),
  };
}
export async function waitingAll(w: Wiring) {
  const state = await readChecked(w);
  return [
    listed({ items: newestFirst(state, state.derived.awaitingAuthor), read: state.read }),
    waitingIn(state),
  ] as const;
}
export async function timeline(w: Wiring, limit: number): Promise<Listed> {
  if (limit < 0) throw new LodgeError(`the limit must not be negative, got ${limit}`);
  const state = await readChecked(w),
    all = newestFirst(state, state.snapshot.decisions.keys());
  return listed({
    items: all.slice(0, limit),
    read: state.read,
    more: Math.max(0, all.length - limit),
  });
}
export async function spec(
  w: Wiring,
  area: string | null,
): Promise<readonly [string, Read, readonly SpecArea[]]> {
  const state = await readChecked(w),
    s = state.snapshot;
  if (area !== null && !s.areas.has(area) && [...s.entries.values()].every((e) => e.area !== area))
    throw notFound(state, `area named ${area}`, area);
  return [
    renderSpec(s, state.derived, state.failing, area),
    state.read,
    specView(s, state.derived, state.failing, area),
  ];
}
export async function check(w: Wiring, gate: boolean) {
  const state = await readChecked(w);
  if (!gate) return [state.result, state.read] as const;
  const base = await w.store.gate(state.current),
    published = load(base.published),
    now = stampOf(w.clock.now());
  const found = new Map<string, { problem: Problem; labels: string[] }>(),
    notes = new Set<string>();
  for (const [label, tree] of base.checked) {
    const snapshot = tree === state.current ? state.snapshot : load(tree);
    const result = checkChange(published, snapshot, w.settings, now);
    for (const p of result.problems) {
      const key = JSON.stringify([p.path, p.check, p.line, p.message]);
      const item = found.get(key);
      if (item) item.labels.push(label);
      else found.set(key, { problem: p, labels: [label] });
    }
    for (const note of result.notes) notes.add(note);
  }
  for (const note of base.notes) notes.add(note);
  const problems = [...found.values()]
    .sort(
      (a, b) =>
        byCodePoint(a.problem.path, b.problem.path) ||
        a.problem.check - b.problem.check ||
        byCodePoint(a.problem.message, b.problem.message),
    )
    .map(({ problem, labels }) => {
      const named = labels.filter(Boolean).join(" and ");
      return named ? { ...problem, message: `${named}: ${problem.message}` } : problem;
    });
  return [checkResult(problems, [...notes]), state.read] as const;
}
export async function draft(w: Wiring, ref: string): Promise<string> {
  const state = await readState(w.store),
    s = state.snapshot;
  let path: string,
    extra = "";
  if (ref.startsWith("area:")) {
    const name = ref.slice(5);
    if (!s.areas.has(name)) throw notFound(state, `area named ${name}`, name);
    path = areaPath(name);
    extra = `name: ${name}\n`;
  } else {
    const id = resolveRef(state, ref),
      found = s.paths.get(id);
    if (found === undefined) throw new Error(`missing path for ${id}`);
    path = found;
  }
  const raw = state.current.files.get(path);
  if (raw === undefined) throw new Error(`missing file ${path}`);
  const text = raw.replaceAll("\r\n", "\n");
  return text.replace("---\n", `---\n${extra}base: ${contentHash(text)}\n`);
}
function newestFirst(state: State, ids: Iterable<string>) {
  const decisions = state.snapshot.decisions;
  return views(
    state,
    [...ids].sort(
      (a, b) =>
        instant(decisions.get(b)?.date ?? "") - instant(decisions.get(a)?.date ?? "") ||
        byCodePoint(b, a),
    ),
  );
}
function views(state: State, ids: Iterable<string>) {
  return [...ids].map((id) => level1(state.snapshot, state.derived, id, state.failing));
}
