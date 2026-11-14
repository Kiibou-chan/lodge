import { expect, test } from "bun:test";
import { AddOutcome, PublishOutcome, person, Role } from "#app";
import { Action, load, Raises } from "#core";
import { AREA, ENTRY, wired } from "../app/support.ts";
import { decision, filesOf } from "../core/builders.ts";
import { setup } from "./support.ts";

test("owners_are_the_people_of_the_tree", async () => {
  const { projects, store } = await setup();
  await projects.addMember("storage", "bo", Role.MEMBER, person("author"));
  expect((await store.trees()).map((t) => t.people)).toEqual([
    new Set(["author"]),
    new Set(["author"]),
  ]);
  await projects.addMember("storage", "cy", Role.OWNER, person("author"));
  expect((await store.trees())[0].people).toEqual(new Set(["author", "cy"]));
});
test("a_new_member_moves_the_rev", async () => {
  const { projects, store } = await setup();
  const [before] = await store.trees();
  await projects.addMember("storage", "bo", Role.MEMBER, person("author"));
  expect(await store.publish(before, new Map(), "stale")).toBe(PublishOutcome.REJECTED);
});

test("the_wired_owner_confirms_and_writes_as_author", async () => {
  const { store } = await setup();
  await store.publish(
    (await store.trees())[0],
    filesOf(
      AREA,
      ENTRY,
      decision({ id: "d-aaaaaa", changes: [{ entry: ENTRY.id, action: Action.CREATE }] }),
    ),
    "seed",
  );
  const lodge = wired(store);
  const question = await lodge.ask("d-aaaaaa", Raises.QUESTION, "author", "Why?", {
    where: "chat",
  });
  expect(question.outcome).toBe(AddOutcome.PUBLISHED);
  const confirmation = await lodge.confirm(["d-aaaaaa"], "Read.");
  expect(confirmation.outcome).toBe(AddOutcome.PUBLISHED);
  const snapshot = load((await store.trees())[0]);
  expect(snapshot.threads.get(question.ids[0] as string)?.messages[0]?.by).toBe("author");
  expect(snapshot.decisions.get(confirmation.ids[0] as string)?.decidedBy).toBe("author");
});
