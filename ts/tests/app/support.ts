import { Lodge, type Store } from "#app";
import { Action, coreSettings } from "#core";
import { area, at, decision, entry } from "../core/builders.ts";
import { CountingIds, FixedClock, MemoryStore } from "./fakes.ts";

export const AREA = area({
  name: "storage",
  title: "Storage",
  intro: "How it keeps data.",
  order: ["s-aaaaaa"],
});
export const ENTRY = entry({
  id: "s-aaaaaa",
  area: "storage",
  title: "Transcripts are kept",
  statement: "Held.",
});
export const FIRST = decision({
  id: "d-aaaaaa",
  title: "Keep whole transcripts",
  code: "ITEM-1",
  decidedBy: "author",
  reasoning: "Because they are evidence.",
  changes: [{ entry: "s-aaaaaa", action: Action.CREATE }],
  date: at(0),
});
export function project({ staged = false } = {}) {
  return new MemoryStore([AREA, ENTRY, FIRST], { staged });
}

export function wired(store: Store, clock = new FixedClock(), ids = new CountingIds()) {
  return new Lodge(store, clock, ids, coreSettings());
}
