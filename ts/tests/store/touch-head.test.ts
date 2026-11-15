import { expect, test } from "bun:test";
import { PublishOutcome } from "#app";
import { setup } from "./support.ts";

test("touching_a_head_keeps_its_revision", async () => {
  const { database, store } = await setup();
  const before = await database.db.selectFrom("heads").selectAll().execute();
  expect(await store.publish((await store.trees())[0], new Map(), "empty")).toBe(
    PublishOutcome.PUBLISHED,
  );
  expect(await database.db.selectFrom("heads").selectAll().execute()).toEqual(before);
});
