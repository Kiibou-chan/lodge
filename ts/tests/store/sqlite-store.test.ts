import { expect, test } from "bun:test";
import { AddOutcome, CommitOutcome, PublishOutcome } from "#app";
import { decodeUtf8, load, tree } from "#core";
import { AREA, wired } from "../app/support.ts";
import { decisionText, specText } from "../core/applying.ts";
import { filesOf } from "../core/builders.ts";
import { events, setup } from "./support.ts";

test("trees_give_one_state", async () => {
  const { store } = await setup();
  const [a, b] = await store.trees();
  expect(a).toBe(b);
  expect(a.rev).toBe("2");
  expect(a.files.size).toBe(0);
});
test("a_write_is_one_event_per_file", async () => {
  const { store, database } = await setup();
  expect(
    await store.publish(
      (await store.trees())[0],
      new Map([
        ["lodge/a", "a"],
        ["lodge/b", "b"],
      ]),
      "write",
    ),
  ).toBe(PublishOutcome.PUBLISHED);
  expect(
    (await events(database)).slice(2).map(({ kind, path, message, actor, at }) => ({
      kind,
      path,
      message: message === null ? null : decodeUtf8(message),
      actor,
      at,
    })),
  ).toEqual(
    ["lodge/a", "lodge/b"].map((path) => ({
      kind: "file",
      path,
      message: "write",
      actor: "author",
      at: "2026-10-29T09:30:00+01:00",
    })),
  );
});
test("file_bytes_survive_exactly", async () => {
  const { store, database } = await setup();
  const text = "\uFEFFa\r\n\0😀\uDC80";
  await store.publish((await store.trees())[0], new Map([["lodge/a", text]]), "");
  expect((await store.trees())[0].files.get("lodge/a")).toBe(text);
  expect((await events(database))[2]?.body.at(-1)).toBe(128);
});
test("stale_base_is_rejected_and_writes_nothing", async () => {
  const { store, database } = await setup();
  const base = (await store.trees())[0];
  await store.publish(base, new Map([["lodge/a", "a"]]), "");
  const before = await events(database);
  const live = (await store.trees())[0];
  for (const rev of [base.rev, null, "x", "2.0", "-1", ` ${live.rev}`, `${live.rev}.0`])
    expect(await store.publish(tree({ ...base, rev }), new Map([["lodge/b", "b"]]), "")).toBe(
      PublishOutcome.REJECTED,
    );
  expect(await events(database)).toEqual(before);
});
test("attachments_are_listed_not_read", async () => {
  const { store } = await setup();
  const path = "lodge/attachments/d-aaaaaa/run.log";
  await store.publish((await store.trees())[0], new Map([[path, "\uFEFF\uDC80"]]), "");
  const current = (await store.trees())[0];
  expect(current.attachments.has(path)).toBe(true);
  expect(current.files.has(path)).toBe(false);
  expect(await store.attachmentTexts()).toEqual(new Map([[path, "\uFEFF\uDC80"]]));
});
test("gate_compares_the_current_state_with_itself", async () => {
  const { store } = await setup();
  const current = (await store.trees())[0];
  const result = await store.gate(current);
  expect(result.published).toBe(current);
  expect(result.checked).toEqual([["", current]]);
  expect(result.notes).toEqual([]);
});
test("freshness_is_null_and_commit_is_refused", async () => {
  const { store, database, clock } = await setup();
  const before = await events(database);
  const calls = clock.calls;
  expect(await store.freshness()).toBeNull();
  expect(await store.commit([], "")).toEqual({
    outcome: CommitOutcome.FAILED,
    detail: "the server keeps no checkout; its writes are published at once",
  });
  expect(await events(database)).toEqual(before);
  expect(clock.calls).toBe(calls);
});
test("lodge_adds_through_the_store", async () => {
  const { store } = await setup();
  await store.publish((await store.trees())[0], filesOf(AREA), "area");
  const result = await wired(store).add(
    [
      [
        "d.md",
        decisionText("changes:", "  - {entry: s-bbbbbb, action: create}", "attachments: [run.log]"),
      ],
      ["s.md", specText("id: s-bbbbbb", "area: storage")],
    ],
    { attachments: [["run.log", "log"]] },
  );
  expect(result.outcome).toBe(AddOutcome.PUBLISHED);
  const current = (await store.trees())[0];
  expect(load(current).entries.has("s-bbbbbb")).toBe(true);
  expect(current.attachments.has("lodge/attachments/d-111111/run.log")).toBe(true);
});

test.each(["t\uDC80 tail", "\uFEFFlead"])(
  "event_message_bytes_survive_exactly",
  async (message) => {
    const { store, database } = await setup();
    await store.publish((await store.trees())[0], new Map([["lodge/a", "a"]]), message);
    const saved = (await events(database))[2]?.message;
    expect(saved).toBeInstanceOf(Uint8Array);
    expect(decodeUtf8(saved as Uint8Array)).toBe(message);
  },
);
