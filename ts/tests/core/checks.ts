import { Action, type Area, coreSettings, type Decision, type SpecEntry } from "#core";
import { area, at, decision, entry, snapshotOf } from "./builders.ts";
export const SPEC = "s-aaaaaa",
  OLD = "d-aaaaaa";
export const LATER = at(30);
export const SETTINGS = coreSettings({ importSources: ["notes.md"] });
export const NOW = "2026-10-29T12:00:00+01:00";
export const NOTES = { file: "notes.md", heading: "A heading" };
export type Item = Area | Decision | SpecEntry;
function key(item: Item): string {
  return item.kind === "area" ? item.name : item.id;
}
export function creates(spec: string, kw: Partial<Decision> = {}): Decision {
  return decision({ changes: [{ entry: spec, action: Action.CREATE }], ...kw });
}
function baseItems(): Item[] {
  return [
    area({ order: [SPEC] }),
    entry({ id: SPEC }),
    creates(SPEC, { id: OLD, date: at(0), decidedBy: "author" }),
  ];
}
export function oldDecision(): Decision {
  return baseItems()[2] as Decision;
}
export function state(items: readonly Item[] = [], drop: readonly string[] = []) {
  const merged = new Map(baseItems().map((i) => [key(i), i]));
  for (const item of items) merged.set(key(item), item);
  return snapshotOf([...merged].filter(([k]) => !drop.includes(k)).map(([, i]) => i));
}
export function published() {
  return state();
}
export const REMEDY_CHECK_5 = "; a correction is a new decision that replaces it";
export const REMEDY_CHECK_5_REASONING =
  "; a correction or a shorter reasoning is a new decision that replaces it";
export const REMEDY_CHECK_4 = "; list it in the decision's changes";
export const REMEDY_CHECK_3 =
  "; add quote: {text, where, when} with the author's words, or record it under your own role";
export const REMEDY_ATTACH = "; pass the file with --attach";
