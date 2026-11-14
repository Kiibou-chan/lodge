import { expect, test } from "bun:test";
import { PublishOutcome } from "#app";
import { MemoryStore } from "../app/fakes.ts";
import { Interleaving } from "./interleaving.ts";

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
