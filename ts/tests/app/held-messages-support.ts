import { agent, person } from "#app";
import { Raises } from "#core";
import { CountingIds, FixedClock, MemoryStore } from "./fakes.ts";
import { AREA, ENTRY, FIRST, wired } from "./support.ts";

export async function setup(by = "reviewer") {
  const store = new MemoryStore([AREA, ENTRY, FIRST], { people: new Set(["ada", "bo"]) });
  const clock = new FixedClock();
  const ids = new CountingIds();
  const lodge = wired(store, clock, ids, agent("coordinator"));
  const ada = wired(store, clock, ids, person("ada"));
  const bo = wired(store, clock, ids, person("bo"));
  const question = await (by === "ada" ? ada : lodge).ask(
    "s-aaaaaa",
    Raises.QUESTION,
    by,
    "Why?",
    by === "ada" ? { where: "chat" } : {},
  );
  store.publishes.length = 0;
  const id = question.ids[0] as string;
  const relay = async (where = "chat") => {
    const result = await lodge.reply(id, "ada", "  Yes.  ", { where, when: "2026-10-29 09:00" });
    if (result.held === null) throw new Error("expected a held message");
    return { ...result, held: result.held };
  };
  return { store, lodge, ada, bo, id, relay };
}
