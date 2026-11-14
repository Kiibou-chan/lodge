import { expect, test } from "bun:test";
import { agent, person } from "#app";
import { decodeUtf8, Raises } from "#core";
import { CountingIds, FixedClock } from "../app/fakes.ts";
import { AREA, ENTRY, FIRST, wired } from "../app/support.ts";
import { seeded } from "./seed.ts";
import { events } from "./support.ts";

test("a_relayed_message_lands_with_its_approval", async () => {
  const { store, database } = await seeded(AREA, ENTRY, FIRST);
  const clock = new FixedClock();
  const ids = new CountingIds();
  const lodge = wired(store, clock, ids, agent("coordinator"));
  const question = await lodge.ask("s-aaaaaa", Raises.QUESTION, "reviewer", "Why?");
  const id = question.ids[0] as string;
  const relay = await lodge.reply(id, "author", "Yes.", { where: "chat" });
  const before = await events(database);
  const approves: (number | null | undefined)[] = [];
  const publish = store.publish.bind(store);
  store.publish = async (base, writes, message, seq) => {
    approves.push(seq);
    return publish(base, writes, message, seq);
  };
  await wired(store, clock, ids, person("author")).approve(relay.held as number);
  expect(approves).toEqual([relay.held]);
  const landed = (await events(database)).slice(before.length);
  expect(landed.map((e) => e.kind)).toEqual(["file", "approved"]);
  expect(JSON.parse(decodeUtf8(landed[1]?.body ?? new Uint8Array()))).toEqual({ held: relay.held });
  expect((await store.trees())[0].files.get(landed[0]?.path ?? "")).toContain("Yes.");
  expect((await lodge.thread(id)).thread.messages.at(-1)?.by).toBe("author");
  expect(await store.held()).toEqual([]);
});
