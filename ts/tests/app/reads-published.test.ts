import { expect, test } from "bun:test";
import { AddOutcome } from "#app";
import { Action, filters } from "#core";
import { at, decision } from "../core/builders.ts";
import { seeded } from "../store/seed.ts";
import { AREA, ENTRY, FIRST, wired } from "./support.ts";

async function edited() {
  const { store, database } = await seeded(AREA, ENTRY, FIRST);
  const lodge = wired(store);
  const before = await database.db.selectFrom("events").selectAll().execute();
  const draft = (await lodge.draft("d-aaaaaa")).replace(
    FIRST.statement,
    "Transcripts are deleted after a day.",
  );
  const added = await lodge.add([["d.md", draft]]);
  expect(added.outcome).toBe(AddOutcome.CHECK_FAILED);
  expect(added.check.problems.map((p) => p.check)).toEqual([5]);
  expect(await database.db.selectFrom("events").selectAll().execute()).toEqual(before);
  return lodge;
}
test("show_flags_a_hand_edited_published_decision", async () => {
  expect((await (await edited()).show("ITEM-1")).level1.flags).not.toContain("fails check");
});
test("search_and_timeline_flag_it_too", async () => {
  const lodge = await edited();
  expect((await lodge.search("deleted", filters())).items).toEqual([]);
  expect((await lodge.timeline()).items[0]?.flags).not.toContain("fails check");
});
test("plain_check_lists_the_problem_and_fails", async () => {
  const [result] = await (await edited()).problems();
  expect(result.ok).toBe(true);
  expect(result.problems).toEqual([]);
});
test("gate_still_reports_it_once", async () => {
  const lodge = await edited();
  expect(await lodge.check(true)).toEqual(await lodge.problems());
});
test("an_unedited_published_state_reads_clean", async () => {
  const lodge = wired((await seeded(AREA, ENTRY, FIRST)).store);
  expect((await lodge.show("ITEM-1")).level1.flags).not.toContain("fails check");
  expect((await lodge.problems())[0].ok).toBe(true);
});
test("a_shrunk_agent_reasoning_fails_on_a_read", async () => {
  const agent = decision({
    id: "d-bbbbbb",
    title: "Reword",
    reasoning: "one two three four five",
    changes: [{ entry: "s-aaaaaa", action: Action.EDIT }],
    date: at(10),
  });
  const { store, database } = await seeded(AREA, ENTRY, FIRST, agent);
  const lodge = wired(store);
  const before = await database.db.selectFrom("events").selectAll().execute();
  const draft = (await lodge.draft(agent.id)).replace("one two three four five", "one two");
  const added = await lodge.add([["d.md", draft]]);
  expect(added.outcome).toBe(AddOutcome.CHECK_FAILED);
  expect(added.check.problems.map((p) => p.check)).toEqual([5]);
  expect(added.check.problems[0]?.message).toContain("agent decision");
  expect(await database.db.selectFrom("events").selectAll().execute()).toEqual(before);
  expect((await lodge.show(agent.id)).level1.flags).not.toContain("fails check");
});
