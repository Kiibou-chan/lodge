import { afterEach } from "bun:test";
import { type LodgeDatabase, openDatabase, SqliteProjects, SqliteStore } from "#store";
import { FixedClock } from "../app/fakes.ts";

const opened: LodgeDatabase[] = [];
afterEach(async () => {
  for (const db of opened.splice(0)) await db.close();
});
export async function setup(name = "storage", owner = "author") {
  const database = await openDatabase(":memory:");
  opened.push(database);
  const clock = new FixedClock();
  const projects = new SqliteProjects(database, clock);
  await projects.create(name, owner);
  const store = new SqliteStore(database, name, owner, clock);
  return { database, projects, store, clock };
}
export async function events(database: LodgeDatabase) {
  return database.db.selectFrom("events").selectAll().orderBy("seq", "asc").execute();
}
