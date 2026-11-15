import { expect, test } from "bun:test";
import { AddOutcome } from "#app";
import { instant, load, tree } from "#core";
import { decisionText } from "../core/applying.ts";
import { at } from "../core/builders.ts";
import { FixedClock, type MemoryStore, START } from "./fakes.ts";
import { FIRST, project, wired } from "./support.ts";

const NEWEST = { epochMs: instant(FIRST.date), offsetMinutes: 60 };
async function edit(store: MemoryStore, statement: string) {
  return [
    ["d.md", decisionText("changes:", "  - {entry: s-aaaaaa, action: edit}", { body: "Edited." })],
    ["s.md", (await wired(store).draft("s-aaaaaa")).replace("Held.", statement)],
  ] as const;
}
function dated(store: MemoryStore) {
  return [...load(tree({ rev: null, files: store.files })).decisions.values()]
    .map((d) => d.date)
    .sort();
}
test("add_in_the_second_of_the_newest_decision_waits_for_the_next", async () => {
  const store = project(),
    clock = new FixedClock(NEWEST);
  expect((await wired(store, clock).add(await edit(store, "Held, whole."))).outcome).toBe(
    AddOutcome.PUBLISHED,
  );
  expect(clock.slept).toEqual([1]);
  expect(dated(store)).toEqual([at(0), "2026-10-28T10:00:01+01:00"]);
});
test("add_sleeps_to_the_next_whole_second", async () => {
  const store = project(),
    clock = new FixedClock({ ...NEWEST, epochMs: NEWEST.epochMs + 400 });
  await wired(store, clock).add(await edit(store, "Held, whole."));
  expect(clock.slept).toEqual([0.6]);
});
test("add_after_the_newest_second_does_not_wait", async () => {
  const store = project(),
    clock = new FixedClock(START);
  expect((await wired(store, clock).add(await edit(store, "Held, whole."))).outcome).toBe(
    AddOutcome.PUBLISHED,
  );
  expect(clock.slept).toEqual([]);
  expect(clock.calls).toBe(1);
});
test("two_adds_in_one_second_are_dated_a_second_apart", async () => {
  const store = project({ staged: true }),
    clock = new FixedClock(START);
  await wired(store, clock).add(await edit(store, "Held, whole."));
  expect((await wired(store, clock).add(await edit(store, "Held, compressed."))).outcome).toBe(
    AddOutcome.STAGED,
  );
  expect(clock.slept).toEqual([1]);
  expect(dated(store).slice(1)).toEqual(["2026-10-29T09:30:00+01:00", "2026-10-29T09:30:01+01:00"]);
});
test("a_decision_far_ahead_of_the_clock_is_not_waited_for", async () => {
  const store = project(),
    clock = new FixedClock({ ...NEWEST, epochMs: NEWEST.epochMs - 86400000 });
  expect((await wired(store, clock).add(await edit(store, "Held, whole."))).outcome).toBe(
    AddOutcome.CHECK_FAILED,
  );
  expect(clock.slept).toEqual([]);
});
test("a_decision_a_few_seconds_ahead_of_the_clock_is_waited_for", async () => {
  const store = project(),
    clock = new FixedClock({ ...NEWEST, epochMs: NEWEST.epochMs - 2000 });
  expect((await wired(store, clock).add(await edit(store, "Held, whole."))).outcome).toBe(
    AddOutcome.PUBLISHED,
  );
  expect(clock.slept.length).toBe(3);
});
