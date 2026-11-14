import { expect, test } from "bun:test";
import { PublishOutcome } from "#app";
import { MemoryStore } from "../app/fakes.ts";
import { Interleaving } from "./interleaving.ts";
import { setup } from "./support.ts";

test("reject_next_lands_one_change_per_attempt_and_records_only_publications", async () => {
  const inner = new MemoryStore();
  const store = new Interleaving(inner);
  const first = new Map([["lodge/a", "a"]]);
  const second = new Map([["lodge/b", "b"]]);
  const writes = new Map([["lodge/c", "c"]]);
  store.rejectNext(first, second);
  for (const change of [first, second]) {
    const [base] = await store.trees();
    expect(await store.publish(base, writes, "ours")).toBe(PublishOutcome.REJECTED);
    for (const [path, text] of change) expect((await store.files()).get(path)).toBe(text);
  }
  expect(store.publishes).toEqual([]);
  expect(await store.publish((await store.trees())[0], writes, "ours")).toBe(
    PublishOutcome.PUBLISHED,
  );
  writes.clear();
  expect(store.attempts).toBe(3);
  expect(store.publishes).toEqual([[new Map([["lodge/c", "c"]]), "ours"]]);
});
test("moves_after_read_returns_stale_tree_and_files_include_attachments", async () => {
  const inner = new MemoryStore();
  const store = new Interleaving(inner);
  const path = "lodge/attachments/d-aaaaaa/log.txt";
  store.movesAfterRead(new Map([[path, "log"]]));
  const [base] = await store.trees();
  expect(base.rev).toBe("0");
  expect(await store.publish(base, new Map(), "stale")).toBe(PublishOutcome.REJECTED);
  expect((await store.files()).get(path)).toBe("log");
  expect((await store.trees())[0].rev).toBe("1");
  expect(await store.attachmentTexts()).toEqual(await inner.attachmentTexts());
  expect(await store.freshness()).toBe(await inner.freshness());
  expect(await store.gate(base)).toEqual(await inner.gate(base));
  expect(await store.commit([path], "commit")).toEqual(inner.commitResult);
  expect(inner.commits).toEqual([[[path], "commit"]]);
});

test("memory_store_attachment_texts_include_attachment_paths", async () => {
  const inner = new MemoryStore();
  const path = "lodge/attachments/d-aaaaaa/log.txt";
  inner.files.set(path, "log");
  inner.files.set("lodge/other", "other");
  expect(await inner.attachmentTexts()).toEqual(new Map([[path, "log"]]));
});
test("sqlite_interleaving_includes_and_forwards_attachment_texts", async () => {
  const { store: inner } = await setup();
  const store = new Interleaving(inner);
  const path = "lodge/attachments/d-aaaaaa/log.txt";
  const attachments = new Map([[path, "log"]]);
  expect(await inner.publish((await inner.trees())[0], attachments, "attachment")).toBe(
    PublishOutcome.PUBLISHED,
  );
  expect((await inner.trees())[0].files.has(path)).toBe(false);
  expect(await store.files()).toEqual(attachments);
  expect(await store.attachmentTexts()).toEqual(attachments);
});
test("interleaving_refuses_a_change_that_did_not_publish", async () => {
  const inner = new MemoryStore([], { staged: true });
  const store = new Interleaving(inner);
  store.rejectNext(new Map([["lodge/a", "a"]]));
  const [base] = await store.trees();
  await expect(store.publish(base, new Map(), "ours")).rejects.toThrow(
    "the interleaved change did not publish",
  );
  expect(store.publishes).toEqual([]);
});
