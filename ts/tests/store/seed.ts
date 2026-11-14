import { afterEach } from "bun:test";
import { PublishOutcome } from "#app";
import type { Area, Decision, SpecEntry } from "#core";
import { type LodgeDatabase, openDatabase, SqliteProjects, SqliteStore } from "#store";
import { FixedClock } from "../app/fakes.ts";
import { filesOf } from "../core/builders.ts";

const opened: LodgeDatabase[] = [];
afterEach(async () => {
  for (const database of opened.splice(0)) await database.close();
});
export async function seeded(...items: (Area | Decision | SpecEntry)[]) {
  const database = await openDatabase(":memory:");
  opened.push(database);
  const clock = new FixedClock();
  await new SqliteProjects(database, clock).create("storage-notes", "author");
  const store = new SqliteStore(database, "storage-notes", "author", clock);
  if (
    (await store.publish((await store.trees())[0], filesOf(...items), "seed")) !==
    PublishOutcome.PUBLISHED
  )
    throw new Error("seed did not publish");
  return { database, store };
}
