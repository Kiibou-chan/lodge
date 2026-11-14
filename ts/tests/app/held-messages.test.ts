import { expect, test } from "bun:test";
import { AddOutcome, Forbidden, LodgeError } from "#app";
import { setup } from "./held-messages-support.ts";

test("an_agent_relaying_a_persons_words_is_held", async () => {
  const { store, lodge, relay } = await setup();
  const result = await relay();
  expect(result).toMatchObject({
    outcome: AddOutcome.HELD,
    awaits: "ada",
    held: expect.any(Number),
  });
  expect(store.publishes).toEqual([]);
  expect(await lodge.held()).toMatchObject([
    {
      seq: result.held,
      kind: "message",
      person: "ada",
      by: "agent coordinator",
      operation: "reply",
      text: "Yes.",
      where: "chat",
      when: "2026-10-29 09:00",
    },
  ]);
});
for (const own of [false, true]) {
  test(
    own ? "a_persons_thread_still_waits_for_an_agent" : "the_thread_still_waits_for_the_person",
    async () => {
      const { lodge, ada, id, relay } = await setup(own);
      const result = await relay();
      const key = own ? "forAgent" : "forAuthor";
      expect((await lodge.threadsWaiting())[key].map((t) => t.id)).toEqual([id]);
      expect((await lodge.waitingAll())[1][key].map((t) => t.id)).toEqual([id]);
      expect((await lodge.thread(id)).thread.messages.at(-1)?.text).toBe("Why?");
      expect(await lodge.held()).toHaveLength(1);
      await ada.approve(result.held as number);
      expect((await lodge.threadsWaiting()).forAgent.map((t) => t.id)).toEqual([id]);
      expect((await lodge.thread(id)).thread.messages.at(-1)?.text).toBe("Yes.");
    },
  );
}
test("a_persons_own_message_is_published_at_once", async () => {
  const { ada, id } = await setup();
  expect(await ada.reply(id, "ada", "Yes.", { where: "chat" })).toMatchObject({
    outcome: AddOutcome.PUBLISHED,
    held: null,
    awaits: null,
  });
});
test("one_person_cannot_write_as_another", async () => {
  const { bo, lodge, store, id } = await setup();
  await expect(bo.reply(id, "ada", "Yes.", { where: "chat" })).rejects.toThrow(Forbidden);
  expect(await lodge.held()).toEqual([]);
  expect(store.publishes).toEqual([]);
});
test("a_relay_without_where_is_refused_as_lodge_0_2_refuses_it", async () => {
  const { lodge, id } = await setup();
  await expect(lodge.reply(id, "ada", "Yes.")).rejects.toThrow(
    new LodgeError("a message by ada needs where, the place of ada's words"),
  );
  expect(await lodge.held()).toEqual([]);
});
test("a_relay_to_a_closed_thread_is_refused", async () => {
  const { lodge, id, relay } = await setup();
  await lodge.close(id, "reviewer");
  await expect(relay()).rejects.toThrow(`${id} is closed`);
  expect(await lodge.held()).toEqual([]);
});
