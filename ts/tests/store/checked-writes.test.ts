import { expect, test } from "bun:test";
import { AddOutcome, PublishOutcome, StaleList } from "#app";
import { filters } from "#core";
import { AREA, ENTRY, FIRST, wired } from "../app/support.ts";
import { decisionText, specText } from "../core/applying.ts";
import { Interleaved } from "./interleaving.ts";
import { seeded } from "./seed.ts";
import { events } from "./support.ts";

const RETIRE: readonly (readonly [string, string])[] = [
  ["d.md", decisionText("changes:", "  - {entry: s-aaaaaa, action: retire}")],
];
const RESTS: readonly (readonly [string, string])[] = [
  ["d.md", decisionText("changes:", "  - {entry: s-bbbbbb, action: create}")],
  ["s.md", specText("id: s-bbbbbb", "area: storage", "rests_on: [s-aaaaaa]")],
];
test("every_write_is_checked_against_the_state_it_lands_on", async () => {
  const { database, store } = await seeded(AREA, ENTRY, FIRST);
  const a = wired(store);
  const interleaved = new Interleaved(store, a, RETIRE);
  const before = (await events(database)).length;
  const result = await wired(interleaved).add(RESTS);
  expect(result.outcome).toBe(AddOutcome.CHECK_FAILED);
  expect(result.check.problems.map((p) => p.check)).toEqual([6]);
  expect(interleaved.outcomes).toEqual([PublishOutcome.REJECTED]);
  expect((await events(database)).length).toBe(before + 2);
  expect((await a.search("s-bbbbbb", filters())).items).toEqual([]);
});
test("a_refused_write_leaves_no_event", async () => {
  const { database, store } = await seeded(AREA, ENTRY, FIRST);
  const lodge = wired(store),
    before = await events(database);
  const draft = (await lodge.draft(FIRST.id)).replace(FIRST.statement, "Changed.");
  expect((await lodge.add([["d.md", draft]])).outcome).toBe(AddOutcome.CHECK_FAILED);
  expect(await events(database)).toEqual(before);
  await expect(lodge.confirm([FIRST.id], "Read.")).rejects.toThrow(StaleList);
  expect(await events(database)).toEqual(before);
  expect((await lodge.add(RETIRE, { dryRun: true })).outcome).toBe(AddOutcome.DRY_RUN);
  expect(await events(database)).toEqual(before);
});
test("gate_on_the_server_is_the_current_state", async () => {
  const { store } = await seeded(AREA, ENTRY, FIRST);
  const lodge = wired(store);
  for (let i = 0; i < 3; i++) {
    expect((await lodge.add([["d.md", decisionText({ body: `Decision ${i}.` })]])).outcome).toBe(
      AddOutcome.PUBLISHED,
    );
  }
  expect(await lodge.check(true)).toEqual(await lodge.problems());
  const [current] = await store.trees();
  expect((await store.gate(current)).published).toBe(current);
});
test("a_refused_add_carries_its_feedback", async () => {
  const { store } = await seeded(AREA, ENTRY, FIRST);
  const lodge = wired(store);
  const draft = decisionText("changes:", "  - {entry: s-bbbbbb, action: create}").replace(
    "Keep transcripts",
    "x".repeat(200),
  );
  const added = await lodge.add([
    ["d.md", draft],
    ["s.md", specText("id: s-bbbbbb", "area: storage", "rests_on: [s-cccccc]")],
  ]);
  expect(added.outcome).toBe(AddOutcome.CHECK_FAILED);
  expect(
    added.feedback.some((f) => f.message.includes("the title is 200 characters; guidance is")),
  ).toBe(true);
});
