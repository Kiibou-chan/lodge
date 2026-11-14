import { open } from "./db.ts";
import { sql } from "kysely";
const db = open(":memory:");
await sql`create table events (seq integer primary key autoincrement, kind text not null, body text not null)`.execute(db);
await db.insertInto("events").values({ kind: "k", body: "b" }).execute();
console.log(JSON.stringify(await db.selectFrom("events").selectAll().execute()));
