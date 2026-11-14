import { expect, test } from "bun:test";
import { AddOutcome, LodgeError, NotFound, person } from "#app";
import { filters } from "#core";
import { draft, setup } from "./held-support.ts";

test("an_agents_add_of_a_persons_decision_is_held", async () => {
  const { store, lodge } = setup();
  const result = await lodge.add([["d.md", draft()]]);
  expect(result.outcome).toBe(AddOutcome.HELD);
  expect(result.awaits).toBe("ada");
  expect(result.minted).toEqual(result.ids);
  expect(result.paths).toEqual([]);
  expect(await lodge.held()).toEqual(await store.held());
  expect(await lodge.held()).toMatchObject([
    { seq: result.held, kind: "add", person: "ada", by: "agent", drafts: [["d.md", draft()]] },
  ]);
});
test("another_persons_add_is_held", async () => {
  const { lodge } = setup(person("bo"));
  expect(await lodge.add([["d.md", draft()]])).toMatchObject({
    outcome: AddOutcome.HELD,
    awaits: "ada",
  });
});
test("a_dry_run_names_who_must_approve", async () => {
  const { lodge } = setup();
  expect(await lodge.add([["d.md", draft()]], { dryRun: true })).toMatchObject({
    outcome: AddOutcome.DRY_RUN,
    awaits: "ada",
    held: null,
  });
  expect(await lodge.held()).toEqual([]);
});
test("a_held_add_is_not_current", async () => {
  const { store, lodge } = setup();
  const result = await lodge.add([["d.md", draft()]]);
  await expect(lodge.show(result.ids[0] as string)).rejects.toThrow(NotFound);
  expect((await lodge.search("", filters())).items).toEqual([]);
  expect(store.files.size).toBe(0);
});
test("a_persons_own_decision_is_not_held", async () => {
  const { lodge } = setup(person("ada"));
  expect(await lodge.add([["d.md", draft()]])).toMatchObject({
    outcome: AddOutcome.PUBLISHED,
    awaits: null,
    held: null,
  });
  expect(await lodge.held()).toEqual([]);
});
test("an_add_for_two_people_is_refused", async () => {
  const { lodge } = setup();
  await expect(
    lodge.add([
      ["a.md", draft()],
      ["b.md", draft("bo")],
    ]),
  ).rejects.toThrow(
    new LodgeError(
      "an add holds the decisions of one person at a time; split the drafts by person",
    ),
  );
  expect(await lodge.held()).toEqual([]);
});
test("a_failing_check_is_not_held", async () => {
  const { lodge } = setup();
  const result = await lodge.add([["d.md", draft("ada", false)]]);
  expect(result.outcome).toBe(AddOutcome.CHECK_FAILED);
  expect(result.check.problems.some((p) => p.check === 3)).toBe(true);
  expect(await lodge.held()).toEqual([]);
});
