import { expect, test } from "bun:test";
import { type HeldDraft, NotFound, PublishOutcome } from "#app";
import { decodeUtf8, encodeUtf8 } from "#core";
import { rebuild, SqliteStore } from "#store";
import { events, setup } from "./support.ts";

const draft: HeldDraft = {
  kind: "add",
  person: "ada",
  by: "agent",
  drafts: [["draft", "text"]],
  attachments: [],
  importing: false,
  message: "add",
};
const writes = new Map([["lodge/specs/new.md", "new"]]);
test("a_hold_is_an_event_and_not_a_file", async () => {
  const { store, database } = await setup();
  const [before] = await store.trees();
  const seq = await store.hold(draft);
  const event = (await events(database)).at(-1);
  expect(event?.kind).toBe("held");
  expect(event?.seq).toBe(seq);
  expect(JSON.parse(decodeUtf8(event?.body ?? new Uint8Array()))).toEqual(draft);
  expect((await store.trees())[0].files).toEqual(before.files);
  expect((await store.trees())[0].rev).toBe(String(seq));
  expect(await store.held()).toEqual([{ ...draft, seq, at: "2026-10-29T09:30:00+01:00" }]);
});
test("approval_and_files_land_together", async () => {
  const { store, database } = await setup();
  const [stale] = await store.trees();
  const seq = await store.hold(draft);
  const before = await events(database);
  expect(await store.publish(stale, writes, "approve", seq)).toBe(PublishOutcome.REJECTED);
  expect(await events(database)).toEqual(before);
  expect(await store.publish((await store.trees())[0], writes, "approve", seq)).toBe(
    PublishOutcome.PUBLISHED,
  );
  expect(
    (await events(database))
      .slice(-2)
      .map((e) => [
        e.kind,
        e.kind === "approved" ? JSON.parse(decodeUtf8(e.body)) : decodeUtf8(e.body),
      ]),
  ).toEqual([
    ["file", "new"],
    ["approved", { held: seq }],
  ]);
  expect((await store.trees())[0].files.get("lodge/specs/new.md")).toBe("new");
  expect(await store.held()).toEqual([]);
});
test("a_declined_hold_cannot_be_approved", async () => {
  const { store, database } = await setup();
  const seq = await store.hold(draft);
  const [stale] = await store.trees();
  await store.decline(seq, "no");
  expect((await store.trees())[0].rev).not.toBe(stale.rev);
  const before = await events(database);
  expect(JSON.parse(decodeUtf8(before.at(-1)?.body ?? new Uint8Array()))).toEqual({
    held: seq,
    reason: "no",
  });
  expect(await store.publish((await store.trees())[0], writes, "approve", seq)).toBe(
    PublishOutcome.REJECTED,
  );
  expect(await events(database)).toEqual(before);
});
test("a_hold_is_approved_once", async () => {
  const { store, database } = await setup();
  const seq = await store.hold(draft);
  await store.publish((await store.trees())[0], writes, "approve", seq);
  const before = await events(database);
  expect(await store.publish((await store.trees())[0], writes, "again", seq)).toBe(
    PublishOutcome.REJECTED,
  );
  expect(await events(database)).toEqual(before);
});
test("a_settled_hold_cannot_be_declined", async () => {
  const { store } = await setup();
  for (const approve of [false, true]) {
    const seq = await store.hold(draft);
    if (approve) await store.publish((await store.trees())[0], new Map(), "approve", seq);
    else await store.decline(seq, "no");
    const refusal = store.decline(seq, "again");
    await expect(refusal).rejects.toBeInstanceOf(NotFound);
    await expect(refusal).rejects.toThrow(`nothing is held under number ${seq}`);
  }
});
test("a_held_message_round_trips", async () => {
  const { store } = await setup();
  const message: HeldDraft = {
    kind: "message",
    person: "ada",
    by: "agent builder",
    operation: "ask",
    ref: "d-123456",
    raises: null,
    text: "words",
    where: "review",
    when: "2026-10-29 09:30",
  };
  const seq = await store.hold(message);
  expect(await store.held()).toEqual([{ ...message, seq, at: "2026-10-29T09:30:00+01:00" }]);
});
test("holds_rebuild", async () => {
  const { store, database } = await setup();
  const first = await store.hold(draft);
  await store.decline(first, "no");
  const second = await store.hold(draft);
  await store.publish((await store.trees())[0], writes, "yes", second);
  await store.hold(draft);
  const before = await database.db.selectFrom("held").selectAll().orderBy("seq").execute();
  await rebuild(database);
  expect(await database.db.selectFrom("held").selectAll().orderBy("seq").execute()).toEqual(before);
});
test("rebuild_refuses_an_impossible_history", async () => {
  const { store, database } = await setup();
  const seq = await store.hold(draft);
  await store.decline(seq, "no");
  const snapshot = async () =>
    Promise.all([
      database.db.selectFrom("held").selectAll().execute(),
      database.db.selectFrom("heads").selectAll().execute(),
      database.db.selectFrom("files").selectAll().execute(),
      database.db.selectFrom("members").selectAll().execute(),
    ]);
  const before = await snapshot();
  await database.db
    .insertInto("events")
    .values({
      project: "storage",
      actor: "ada",
      at: "now",
      kind: "approved",
      path: null,
      body: encodeUtf8(JSON.stringify({ held: seq })),
      message: null,
    })
    .execute();
  await expect(rebuild(database)).rejects.toThrow();
  expect(await snapshot()).toEqual(before);
});

test("holds_belong_to_their_project", async () => {
  const { store, database, projects, clock } = await setup();
  await projects.create("other", "ada");
  const other = new SqliteStore(database, "other", "ada", clock);
  const ownSeq = await store.hold(draft);
  const otherSeq = await other.hold(draft);
  expect((await store.held()).map((held) => held.seq)).toEqual([ownSeq]);
  expect((await other.held()).map((held) => held.seq)).toEqual([otherSeq]);
  const before = await events(database);
  await expect(store.decline(otherSeq, "no")).rejects.toBeInstanceOf(NotFound);
  expect(await events(database)).toEqual(before);
  expect(await store.publish((await store.trees())[0], writes, "yes", otherSeq)).toBe(
    PublishOutcome.REJECTED,
  );
  expect(await events(database)).toEqual(before);
});

test("holds_are_returned_in_event_order", async () => {
  const { store } = await setup();
  const first = await store.hold(draft);
  const second = await store.hold(draft);
  expect((await store.held()).map((held) => held.seq)).toEqual([first, second]);
});
