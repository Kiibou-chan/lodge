import { expect, test } from "bun:test";
import { type HeldDraft, NotFound, PublishOutcome } from "#app";
import { MemoryStore } from "./fakes.ts";

test("memory_store_settles_a_hold_once", async () => {
  const store = new MemoryStore();
  const draft: HeldDraft = {
    kind: "add",
    person: "ada",
    by: "agent",
    drafts: [],
    attachments: [],
    importing: false,
    message: "add",
  };
  const [stale] = await store.trees();
  const seq = await store.hold(draft);
  expect(seq).toBe(1);
  expect((await store.held())[0]).toMatchObject({ ...draft, seq, at: expect.any(String) });
  expect(await store.publish(stale, new Map(), "yes", seq)).toBe(PublishOutcome.REJECTED);
  await store.decline(seq, "no");
  expect(store.rev).toBe(2);
  expect(await store.publish((await store.trees())[0], new Map(), "yes", seq)).toBe(
    PublishOutcome.REJECTED,
  );
  await expect(store.decline(seq, "again")).rejects.toThrow(NotFound);
  const next = await store.hold(draft);
  expect(await store.publish((await store.trees())[0], new Map(), "yes", next)).toBe(
    PublishOutcome.PUBLISHED,
  );
  expect(store.rev).toBe(5);
  expect(await store.publish((await store.trees())[0], new Map(), "yes", next)).toBe(
    PublishOutcome.REJECTED,
  );
  await expect(store.decline(next, "no")).rejects.toThrow(NotFound);
  expect(await store.held()).toEqual([]);
});
