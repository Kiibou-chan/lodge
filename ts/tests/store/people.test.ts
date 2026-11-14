import { expect, test } from "bun:test";
import { PublishOutcome, person, Role } from "#app";
import { setup } from "./support.ts";

test("owners_are_the_people_of_the_tree", async () => {
  const { projects, store } = await setup();
  await projects.addMember("storage", "bo", Role.MEMBER, person("ada"));
  expect((await store.trees()).map((t) => t.people)).toEqual([new Set(["ada"]), new Set(["ada"])]);
  await projects.addMember("storage", "cy", Role.OWNER, person("ada"));
  expect((await store.trees())[0].people).toEqual(new Set(["ada", "cy"]));
});
test("a_new_member_moves_the_rev", async () => {
  const { projects, store } = await setup();
  const [before] = await store.trees();
  await projects.addMember("storage", "bo", Role.MEMBER, person("ada"));
  expect(await store.publish(before, new Map(), "stale")).toBe(PublishOutcome.REJECTED);
});
