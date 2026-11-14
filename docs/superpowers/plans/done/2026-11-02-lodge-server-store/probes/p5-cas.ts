// Probe E: a compare whose update leaves the value as it is still counts the row it matched.
import { sql } from "kysely";
import { open } from "./db.ts";
interface DB { heads: { project: string; rev: number } }
const { db } = open<DB>(":memory:");
await sql`create table heads (project text primary key, rev integer not null)`.execute(db);
await db.insertInto("heads").values({ project: "p", rev: 7 }).execute();
for (const base of [7, 6]) {
  const r = await db.updateTable("heads").set((eb) => ({ rev: eb.ref("rev") })).where("project", "=", "p").where("rev", "=", base).executeTakeFirst();
  console.log(`base ${base}: updated rows ${r.numUpdatedRows}`);
}
