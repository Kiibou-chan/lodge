import { expect, test } from "bun:test";
import { AddOutcome, Forbidden, NotFound, PublishOutcome } from "#app";
import { Raises } from "#core";
import { setup } from "./held-messages-support.ts";

test("the_person_approves_and_the_message_is_published", async () => {
  const { lodge, ada, id, relay } = await setup();
  const result = await relay();
  expect(await ada.approve(result.held as number)).toMatchObject({
    kind: "message",
    written: { outcome: AddOutcome.PUBLISHED },
  });
  expect((await lodge.thread(id)).thread.messages.at(-1)).toMatchObject({
    by: "ada",
    text: "Yes.",
    where: "chat",
    when: "2026-10-29 09:00",
  });
  expect((await lodge.threadsWaiting()).forAgent.map((t) => t.id)).toEqual([id]);
  expect(await lodge.held()).toEqual([]);
});
test("a_relayed_question_mints_its_thread_at_approval", async () => {
  const { lodge, ada } = await setup();
  const before = (await lodge.threads()).items.map((t) => t.id);
  const result = await lodge.ask("s-aaaaaa", Raises.QUESTION, "ada", "Another?", { where: "chat" });
  expect(result.outcome).toBe(AddOutcome.HELD);
  expect((await lodge.threads()).items.map((t) => t.id)).toEqual(before);
  const approved = await ada.approve(result.held as number);
  expect(approved.kind).toBe("message");
  if (approved.kind !== "message") throw new Error("message expected");
  expect(approved.written.ids).not.toEqual(result.ids);
  expect((await lodge.thread(approved.written.ids[0] as string)).thread.messages[0]?.by).toBe(
    "ada",
  );
});
test("decline_publishes_nothing", async () => {
  const { store, lodge, ada, id, relay } = await setup();
  const result = await relay();
  await ada.decline(result.held as number, "No.");
  expect(store.publishes).toEqual([]);
  expect(await lodge.held()).toEqual([]);
  expect((await lodge.threadsWaiting()).forAuthor.map((t) => t.id)).toEqual([id]);
});
test("another_person_or_an_agent_cannot_approve_a_message", async () => {
  const { lodge, bo, relay } = await setup();
  const result = await relay();
  for (const actor of [bo, lodge])
    await expect(actor.approve(result.held as number)).rejects.toThrow(Forbidden);
});
test("approval_after_the_thread_closed_leaves_it_held", async () => {
  const { lodge, ada, id, relay } = await setup();
  const result = await relay();
  await lodge.close(id, "reviewer");
  await expect(ada.approve(result.held as number)).rejects.toThrow(`${id} is closed`);
  expect(await lodge.held()).toMatchObject([{ seq: result.held }]);
});

test("a_hold_settled_on_the_last_attempt_is_not_found", async () => {
  const { store, ada, relay } = await setup();
  const result = await relay();
  let attempts = 0;
  store.publish = async () => {
    if (++attempts === 3) await store.decline(result.held as number, "No.");
    return PublishOutcome.REJECTED;
  };
  await expect(ada.approve(result.held as number)).rejects.toThrow(NotFound);
  expect(attempts).toBe(3);
});
