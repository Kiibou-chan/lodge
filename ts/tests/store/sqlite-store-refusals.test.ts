import { expect, test } from "bun:test";
import { PublishOutcome } from "#app";
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
    "lodge/a\\b",
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
  ).rejects.toThrow("lodge/a: cannot encode lone surrogate '\\ud800'");
  expect(await events(database)).toEqual(before);
});
test.each(["\uDC80", "\uD800"].map((c) => [c]))(
  "a_path_holding_a_surrogate_is_refused",
  async (ch) => {
    const { store, database } = await setup();
    const before = await events(database);
    const path = `lodge/${ch}`;
    await expect(
      store.publish((await store.trees())[0], new Map([[path, "x"]]), ""),
    ).rejects.toThrow(`${path}: a path holding a lone surrogate cannot be stored`);
    expect(await events(database)).toEqual(before);
    expect(await store.publish((await store.trees())[0], new Map([["lodge/😀", "x"]]), "")).toBe(
      PublishOutcome.PUBLISHED,
    );
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

test("refusals_follow_phases_across_all_paths", async () => {
  const { store, database } = await setup();
  const path = "lodge/decisions/d-aaaaaa.md";
  await store.publish((await store.trees())[0], new Map([[path, "first"]]), "");
  const base = (await store.trees())[0];
  const before = await events(database);
  await expect(
    store.publish(
      base,
      new Map([
        [path, "changed"],
        ["notes/x", "x"],
      ]),
      "",
    ),
  ).rejects.toThrow("notes/x is outside lodge/, which is all the store writes");
  await expect(
    store.publish(
      base,
      new Map([
        [path, "changed"],
        ["lodge/\uD800", "x"],
      ]),
      "",
    ),
  ).rejects.toThrow("a path holding a lone surrogate cannot be stored");
  await expect(
    store.publish(
      base,
      new Map([
        ["lodge/a", "\uD800"],
        [path, "changed"],
      ]),
      "",
    ),
  ).rejects.toThrow(`${path} is a published decision, and lodge never rewrites a decision`);
  expect(await events(database)).toEqual(before);
});
