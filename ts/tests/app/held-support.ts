import { agent } from "#app";
import { decisionText } from "../core/applying.ts";
import { CountingIds, FixedClock, MemoryStore } from "./fakes.ts";
import { wired } from "./support.ts";

export function draft(name = "ada", quote = true): string {
  return decisionText().replace(
    "decided_by: coordinator",
    `decided_by: ${name}${quote ? '\nquote:\n  text: Keep it.\n  where: a session\n  when: "2026-10-29 09:00"' : ""}`,
  );
}
export function setup(actor = agent()) {
  const store = new MemoryStore([], { people: new Set(["ada", "bo"]) });
  const clock = new FixedClock();
  const lodge = wired(store, clock, new CountingIds(), actor);
  return { store, clock, lodge };
}
