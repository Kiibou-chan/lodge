import type { Derived } from "./derive.ts";
import { areaNames, derivedOrder, writtenOrder } from "./order.ts";
import type { Snapshot } from "./snapshot.ts";
import { type Level1, level1 } from "./views.ts";

const HEADING_LINE = /(?<=^|\n)( {0,3})(#|=+[ \t]*(?=\n|$)|-+[ \t]*(?=\n|$))/gu;

export interface Placed {
  readonly entry: Level1;
  readonly depth: number;
  readonly under: string | null;
  readonly also: readonly string[];
  readonly across: readonly (readonly [string, string])[];
}
export interface SpecArea {
  readonly name: string;
  readonly title: string;
  readonly intro: string;
  readonly entries: readonly Level1[];
  readonly placed: readonly Placed[];
}
export function specView(
  s: Snapshot,
  d: Derived,
  failing: ReadonlySet<string>,
  area: string | null = null,
): readonly SpecArea[] {
  return areaNames(s)
    .filter((name) => area === null || area === name)
    .map((name) => heldArea(s, d, failing, name));
}
export function renderSpec(
  s: Snapshot,
  d: Derived,
  failing: ReadonlySet<string>,
  area: string | null = null,
): string {
  const blocks: string[] = [];
  for (const held of specView(s, d, failing, area)) {
    blocks.push(`# ${held.title}`);
    if (held.intro) blocks.push(escaped(held.intro));
    for (const p of held.placed) {
      const links = p.across.map(([target, other]) => `\nrests on ${target} (${other})`).join("");
      blocks.push(entryBlock(p.entry) + links);
    }
  }
  return blocks
    .map((block) => `${block}\n\n`)
    .join("")
    .replace(/\n$/u, "");
}
function heldArea(s: Snapshot, d: Derived, failing: ReadonlySet<string>, name: string): SpecArea {
  const held = s.areas.get(name);
  const shown = new Map(writtenOrder(s, d, name).map((id) => [id, level1(s, d, id, failing)]));
  const placed = derivedOrder(s, d, name).map((p): Placed => {
    const targets = [...new Set(s.entries.get(p.id)?.restsOn ?? [])];
    const also = targets.filter(
      (t) => t !== p.under && s.entries.get(t)?.area === name && d.status.get(t) === "current",
    );
    const across: (readonly [string, string])[] = [];
    for (const t of targets) {
      const target = s.entries.get(t);
      if (target && target.area !== name) across.push([t, target.area]);
    }
    return { entry: shown.get(p.id) as Level1, depth: p.depth, under: p.under, also, across };
  });
  return {
    name,
    title: held ? held.title : name,
    intro: held ? held.intro : "",
    entries: [...shown.values()],
    placed,
  };
}
function entryBlock(v: Level1): string {
  const marks = [v.id, ...v.flags].join(" · ");
  return `## ${v.title} (${marks})\n\n${escaped(v.statement)}`;
}
function escaped(text: string): string {
  return text.replace(HEADING_LINE, "$1\\$2");
}
