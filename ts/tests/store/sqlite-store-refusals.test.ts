import { expect, test } from "bun:test";
import { LodgeError, PublishOutcome } from "#app";
import { writeRecord } from "#core";
import { decision } from "../core/builders.ts";
import { events, setup } from "./support.ts";

test.each(
  [
    "notes/x",
    "lodge",
    "lodge/../x",
    "lodge//x",
    "lodge/./x",
    "lodge/.git/x",
    "lodge\\x",
    "lodge/x\0",
  ].map((c) => [c]),
)("path_outside_lodge_is_refused", async (path) => {
  const { store, database } = await setup();
  const before = await events(database);
  await expect(store.publish((await store.trees())[0], new Map([[path, "x"]]), "")).rejects.toThrow(
    `${path} is outside lodge/, which is all the store writes`,
  );
  expect(await events(database)).toEqual(before);
});
test("lone_surrogate_outside_the_escapes_is_refused", async () => {
  const { store, database } = await setup();
  const before = await events(database);
  await expect(
    store.publish(
      (await store.trees())[0],
      new Map([
        ["lodge/good", "ok"],
        ["lodge/a", "\uD800"],
      ]),
      "",
    ),
  ).rejects.toThrow(LodgeError);
  expect(await events(database)).toEqual(before);
});
test.each(["\uDC80", "\uD800", "😀"].map((c) => [c]))(
  "a_path_holding_a_surrogate_is_refused",
  async (ch) => {
    const { store, database } = await setup();
    const before = await events(database);
    const path = `lodge/${ch}`;
    if (ch === "😀") {
      expect(await store.publish((await store.trees())[0], new Map([[path, "x"]]), "")).toBe(
        PublishOutcome.PUBLISHED,
      );
      return;
    }
    await expect(
      store.publish((await store.trees())[0], new Map([[path, "x"]]), ""),
    ).rejects.toThrow(`${path}: a path holding a lone surrogate cannot be stored`);
    expect(await events(database)).toEqual(before);
  },
);
test("an_attachment_is_never_overwritten", async () => {
  const { store, database } = await setup();
  const path = "lodge/attachments/d-aaaaaa/run.log";
  await store.publish((await store.trees())[0], new Map([[path, "first"]]), "");
  const before = await events(database);
  await expect(
    store.publish((await store.trees())[0], new Map([[path, "second"]]), ""),
  ).rejects.toThrow(`${path} is an attachment, and lodge never overwrites an attachment`);
  expect(await events(database)).toEqual(before);
  expect((await store.attachmentTexts()).get(path)).toBe("first");
});
test("a_published_decision_is_never_rewritten", async () => {
  const { store, database } = await setup();
  const path = "lodge/decisions/d-aaaaaa.md";
  const text = writeRecord(decision({ id: "d-aaaaaa" }));
  await store.publish((await store.trees())[0], new Map([[path, text]]), "");
  const before = await events(database);
  await expect(
    store.publish((await store.trees())[0], new Map([[path, `${text}\n`]]), ""),
  ).rejects.toThrow(`${path} is a published decision, and lodge never rewrites a decision`);
  expect(await events(database)).toEqual(before);
  expect(await store.publish((await store.trees())[0], new Map([[path, text]]), "")).toBe(
    PublishOutcome.PUBLISHED,
  );
});
