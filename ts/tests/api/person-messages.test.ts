import { expect, test } from "bun:test";
import { draft } from "./person-fixtures.ts";
import { signed } from "./signed.ts";

test.each([
  "held_lists_a_relayed_message",
  "approve_publishes_the_relayed_message",
  "decline_drops_the_relayed_message",
])("%s", async (name) => {
  const w = await signed();
  const add = (
    await (
      await w.fetch(w.request("add", { project: "work", drafts: [["d.md", draft("reviewer")]] }))
    )
      .text()
      .then(JSON.parse)
  ).result;
  const ask = (
    await (
      await w.fetch(
        w.request("ask", {
          project: "work",
          ref: add.ids[0],
          raises: "question",
          by: "reviewer",
          text: "Keep these?",
        }),
      )
    )
      .text()
      .then(JSON.parse)
  ).result;
  await w.fetch(w.request("add", { project: "work", drafts: [["held.md", draft()]] }));
  const relay = (
    await (
      await w.fetch(
        w.request("reply", {
          project: "work",
          thread: ask.ids[0],
          by: "ada",
          text: "Yes.",
          where: "chat",
          when: "2026-10-29 10:00",
        }),
      )
    )
      .text()
      .then(JSON.parse)
  ).result;
  expect(relay.outcome).toBe("held for approval");
  const list = (await (await w.call("held", { project: "work" })).text().then(JSON.parse)).result;
  expect(list.map((h: { kind: string }) => h.kind)).toEqual(["add", "message"]);
  expect(list[1]).toMatchObject({
    seq: relay.held,
    operation: "reply",
    ref: ask.ids[0],
    text: "Yes.",
    where: "chat",
    when: "2026-10-29 10:00",
  });
  await w.call("decline", { project: "work", seq: list[0].seq, reason: "No." });
  if (name === "decline_drops_the_relayed_message") {
    expect(
      await (await w.call("decline", { project: "work", seq: relay.held, reason: "No." }))
        .text()
        .then(JSON.parse),
    ).toEqual({ result: null });
    const r = await w.call("approve", { project: "work", seq: relay.held });
    expect(r.status).toBe(404);
    expect(await r.text().then(JSON.parse)).toMatchObject({
      error: { message: `nothing is held under number ${relay.held}` },
    });
  } else {
    expect(
      await (await w.call("approve", { project: "work", seq: relay.held })).text().then(JSON.parse),
    ).toMatchObject({ result: { kind: "message", written: { outcome: "published" } } });
  }
  const thread = (
    await (await w.call("thread", { project: "work", ref: ask.ids[0] })).text().then(JSON.parse)
  ).result.thread;
  expect(thread.messages.at(-1).by).toBe(
    name === "decline_drops_the_relayed_message" ? "reviewer" : "ada",
  );
  if (name !== "decline_drops_the_relayed_message")
    expect(thread.messages.at(-1)).toMatchObject({ where: "chat", when: "2026-10-29 10:00" });
  expect(await (await w.call("held", { project: "work" })).text().then(JSON.parse)).toEqual({
    result: [],
  });
  await w.database.close();
});
