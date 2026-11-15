import { expect, test } from "bun:test";
import { AddOutcome, agent, Forbidden, LodgeError, NotFound, person } from "#app";
import { Action, derive, load, Raises } from "#core";
import { decisionText } from "../core/applying.ts";
import { area, at, decision, entry } from "../core/builders.ts";
import { CountingIds, FixedClock, MemoryStore } from "./fakes.ts";
import { wired } from "./support.ts";

function setup(actor = person("ada")) {
  const store = new MemoryStore(
    [
      area(),
      entry({ id: "s-aaaaaa" }),
      decision({ id: "d-aaaaaa", changes: [{ entry: "s-aaaaaa", action: Action.CREATE }] }),
    ],
    { people: new Set(["ada", "bo"]) },
  );
  return { store, lodge: wired(store, new FixedClock(), new CountingIds(), actor) };
}
test("confirm_writes_the_persons_decision", async () => {
  const { store, lodge } = setup();
  await lodge.confirm(["d-aaaaaa"], "Read.");
  const made = load((await store.trees())[0]).decisions.get("d-111111");
  expect(made?.decidedBy).toBe("ada");
  expect(made?.statement).toContain("ada confirms d-aaaaaa");
});
test("an_agent_cannot_confirm", async () => {
  const { store, lodge } = setup(agent());
  await expect(lodge.confirm(["d-aaaaaa"], "Read.")).rejects.toThrow(
    new Forbidden("only a person confirms; nothing was written"),
  );
  expect(store.publishes).toEqual([]);
});
test("a_person_not_among_the_people_cannot_confirm", async () => {
  const { store, lodge } = setup(person("cy"));
  await expect(lodge.confirm(["d-aaaaaa"], "Read.")).rejects.toThrow(
    new Forbidden("only an owner of the project confirms; nothing was written"),
  );
  expect(store.publishes).toEqual([]);
});
test("a_persons_message_needs_where", async () => {
  const { store, lodge } = setup();
  await expect(lodge.ask("d-aaaaaa", Raises.QUESTION, "ada", "Why?")).rejects.toThrow(
    "a message by ada needs where, the place of ada's words",
  );
  expect(store.publishes).toEqual([]);
});
test("author_is_a_role_where_no_person_is_author", async () => {
  const { lodge } = setup();
  await expect(lodge.ask("d-aaaaaa", Raises.QUESTION, "author", "Why?")).rejects.toThrow(
    new LodgeError("name a person of the project exactly, or use your own role"),
  );
});
test("a_person_writes_only_as_themselves", async () => {
  const { store, lodge } = setup(person("bo"));
  const ada = wired(store, new FixedClock(), new CountingIds(), person("ada"));
  const result = await ada.ask("d-aaaaaa", Raises.QUESTION, "ada", "Why?", { where: "chat" });
  expect(store.publishes).toHaveLength(1);
  const before = new Map(store.files);
  for (const operation of [
    () => lodge.ask("d-aaaaaa", Raises.QUESTION, "ada", "Why?", { where: "chat" }),
    () => lodge.reply(result.ids[0] as string, "ada", "Yes.", { where: "chat" }),
    () => lodge.close(result.ids[0] as string, "ada", { where: "chat" }),
  ]) {
    await expect(operation()).rejects.toThrow(
      new Forbidden("only ada writes as ada; nothing was written"),
    );
  }
  expect(store.files).toEqual(before);
  expect(store.publishes).toHaveLength(1);
});
test("a_persons_question_waits_for_an_agent", async () => {
  const { lodge } = setup();
  const a = await lodge.ask("d-aaaaaa", Raises.QUESTION, "ada", "Why?", { where: "chat" });
  const b = await lodge.ask("d-aaaaaa", Raises.QUESTION, "reviewer", "Why?");
  const waiting = await lodge.threadsWaiting();
  expect(waiting.forAgent.map((t) => t.id)).toEqual([...a.ids]);
  expect(waiting.forAuthor.map((t) => t.id)).toEqual([...b.ids]);
});
test("an_agent_edit_of_a_persons_entry_waits", async () => {
  const store = new MemoryStore(
    [
      area(),
      entry({ id: "s-aaaaaa" }),
      decision({
        id: "d-aaaaaa",
        decidedBy: "ada",
        changes: [{ entry: "s-aaaaaa", action: Action.CREATE }],
      }),
    ],
    { people: new Set(["ada", "bo"]) },
  );
  const lodge = wired(store, new FixedClock(), new CountingIds(), agent());
  const result = await lodge.add([
    ["d.md", decisionText("changes:", "  - {entry: s-aaaaaa, action: edit}")],
  ]);
  expect(result.feedback.some((f) => f.message.startsWith("this decision will wait for"))).toBe(
    true,
  );
  expect(derive(load((await store.trees())[0])).awaitingAuthor.has(result.ids[0] as string)).toBe(
    true,
  );
});

test("unknown_reference_is_refused_before_impersonation", async () => {
  const { store, lodge } = setup(person("bo"));
  await expect(
    lodge.ask("d-ffffff", Raises.QUESTION, "ada", "Why?", { where: "chat" }),
  ).rejects.toThrow(NotFound);
  await expect(lodge.reply("q-ffffff", "ada", "Yes.", { where: "chat" })).rejects.toThrow(NotFound);
  expect(store.publishes).toEqual([]);
});
test("closed_thread_is_refused_before_impersonation", async () => {
  const { store, lodge } = setup();
  const question = await lodge.ask("d-aaaaaa", Raises.QUESTION, "ada", "Why?", { where: "chat" });
  const id = question.ids[0] as string;
  await lodge.close(id, "ada", { where: "chat" });
  const before = new Map(store.files);
  const bo = wired(store, new FixedClock(), new CountingIds(), person("bo"));
  await expect(bo.reply(id, "ada", "Yes.", { where: "chat" })).rejects.toThrow(`${id} is closed`);
  expect(store.files).toEqual(before);
  expect(store.publishes).toHaveLength(2);
});
test("an_agent_is_refused_before_reading_state", async () => {
  const { store, lodge } = setup(agent());
  let reads = 0;
  store.trees = async () => {
    reads += 1;
    throw new Error("state must not be read");
  };
  await expect(lodge.confirm(["d-aaaaaa"], "Read.")).rejects.toThrow(
    new Forbidden("only a person confirms; nothing was written"),
  );
  expect(reads).toBe(0);
});

for (const both of [true, false]) {
  test(`confirmations_remain_available_to_each_person_${both ? "both" : "ada"}`, async () => {
    const quote = { text: "Agreed.", where: "chat", when: "2026-10-28 10:00" };
    const store = new MemoryStore(
      [
        area(),
        decision({ id: "d-aaaaaa", decidedBy: "ada", quote }),
        decision({ id: "d-cccccc", decidedBy: "bo", quote }),
        decision({
          id: "d-bbbbbb",
          date: at(1),
          replaces: ["d-aaaaaa"],
          narrows: both ? ["d-cccccc"] : [],
        }),
      ],
      { people: new Set(["ada", "bo"]) },
    );
    const ids = new CountingIds();
    const ada = wired(store, new FixedClock(), ids, person("ada"));
    const bo = wired(store, new FixedClock(), ids, person("bo"));
    const awaiting = async () => derive(load((await store.trees())[0])).awaiting;
    expect((await awaiting()).get("d-bbbbbb")).toEqual(both ? ["ada", "bo"] : ["ada"]);
    const first = both ? ada : bo;
    const second = both ? bo : ada;
    expect((await first.confirm(["d-bbbbbb"], "Read.")).outcome).toBe(AddOutcome.PUBLISHED);
    expect((await awaiting()).get("d-bbbbbb")).toEqual([both ? "bo" : "ada"]);
    expect((await first.show("d-bbbbbb")).confirmable).toBe(false);
    expect((await second.show("d-bbbbbb")).confirmable).toBe(true);
    expect((await second.confirm(["d-bbbbbb"], "Read too.")).outcome).toBe(AddOutcome.PUBLISHED);
    expect(await awaiting()).toEqual(new Map());
  });
}
