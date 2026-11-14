import { expect, test } from "bun:test";
import { AddOutcome, agent, Forbidden, LodgeError, NotFound, person, stampOf } from "#app";
import { Action, load } from "#core";
import { decisionText, specText } from "../core/applying.ts";
import { area, decision, entry, filesOf } from "../core/builders.ts";
import { CountingIds, FixedClock } from "./fakes.ts";
import { draft, setup } from "./held-support.ts";
import { wired } from "./support.ts";

async function pending() {
  const context = setup();
  const added = await context.lodge.add([["d.md", draft()]]);
  const clock = new FixedClock({
    ...context.clock.start,
    epochMs: context.clock.start.epochMs + 60000,
  });
  return {
    ...context,
    seq: added.held as number,
    ada: wired(context.store, clock, new CountingIds(), person("ada")),
    approvalClock: clock,
  };
}
test("the_person_approves_and_it_becomes_current", async () => {
  const { store, seq, ada, approvalClock } = await pending();
  const result = await ada.approve(seq);
  expect(result.kind).toBe("add");
  if (result.kind !== "add") throw new Error("expected add");
  expect(result.added.outcome).toBe(AddOutcome.PUBLISHED);
  expect(load((await store.trees())[0]).decisions.get(result.added.ids[0] as string)?.date).toBe(
    stampOf(approvalClock.start),
  );
  expect(await ada.held()).toEqual([]);
});
test("another_person_or_an_agent_cannot_approve", async () => {
  const { store, seq } = await pending();
  for (const actor of [person("bo"), agent()]) {
    await expect(
      wired(store, new FixedClock(), new CountingIds(), actor).approve(seq),
    ).rejects.toThrow(new Forbidden("only ada approves this; nothing was written"));
  }
  expect(store.files.size).toBe(0);
});
test("approval_runs_the_check_again", async () => {
  const { store, lodge } = setup();
  const initial = filesOf(
    area(),
    entry({ id: "s-aaaaaa" }),
    decision({ changes: [{ entry: "s-aaaaaa", action: Action.CREATE }] }),
  );
  store.files = new Map(initial);
  store.published = new Map(initial);
  const held = await lodge.add([
    [
      "d.md",
      draft().replace(
        "scope: process",
        "scope: product\nchanges: [{entry: s-bbbbbb, action: create}]",
      ),
    ],
    ["s.md", specText("id: s-bbbbbb", "area: storage", "rests_on: [s-aaaaaa]")],
  ]);
  expect(held.outcome).toBe(AddOutcome.HELD);
  const retired = await lodge.add([
    ["retire.md", decisionText("changes: [{entry: s-aaaaaa, action: retire}]")],
  ]);
  expect(retired.outcome).toBe(AddOutcome.PUBLISHED);
  const ada = wired(store, new FixedClock(), new CountingIds(8), person("ada"));
  const seq = held.held as number;
  const result = await ada.approve(seq);
  expect(result.kind).toBe("add");
  if (result.kind !== "add") throw new Error("expected add");
  expect(result.added.outcome).toBe(AddOutcome.CHECK_FAILED);
  expect(result.added.check.problems.some((p) => p.check === 6)).toBe(true);
  expect(await ada.held()).toHaveLength(1);
});
test("a_declined_hold_cannot_be_approved", async () => {
  const { seq, ada } = await pending();
  await ada.decline(seq, "No.");
  await expect(ada.approve(seq)).rejects.toThrow(
    new NotFound(`nothing is held under number ${seq}`),
  );
});
test("decline_needs_the_person_and_a_reason", async () => {
  const { store, seq, ada, lodge } = await pending();
  await expect(lodge.decline(seq, "No.")).rejects.toThrow(Forbidden);
  const bo = wired(store, new FixedClock(), new CountingIds(), person("bo"));
  await expect(bo.decline(seq, " ")).rejects.toThrow(Forbidden);
  await expect(ada.decline(seq, " \n ")).rejects.toThrow(
    new LodgeError("a reason is required; nothing was written"),
  );
  expect(await ada.held()).toHaveLength(1);
  await ada.decline(seq, " No. \n");
  expect(store.declined).toEqual([[seq, "No."]]);
  expect(await ada.held()).toEqual([]);
  await expect(ada.decline(seq, "Again.")).rejects.toThrow(NotFound);
});

test("a_hold_settled_during_the_last_rejection_is_not_found", async () => {
  const { store, seq, ada } = await pending();
  store.publish = async () => {
    store.attempts += 1;
    if (store.attempts === 3) await store.decline(seq, "No.");
    return "rejected";
  };
  await expect(ada.approve(seq)).rejects.toThrow(
    new NotFound(`nothing is held under number ${seq}`),
  );
  expect(store.attempts).toBe(3);
  expect(store.files.size).toBe(0);
});

test("a_hold_settled_after_the_first_rejection_stops_the_next_attempt", async () => {
  const { store, seq, ada } = await pending();
  store.publish = async () => {
    store.attempts += 1;
    if (store.attempts === 1) await store.decline(seq, "No.");
    return "rejected";
  };
  await expect(ada.approve(seq)).rejects.toThrow(NotFound);
  expect(store.attempts).toBe(1);
  expect(store.files.size).toBe(0);
});
