// Probe A: does a TEXT column round-trip a lone surrogate, U+0000, CRLF, and an astral character?
import { sql } from "kysely";
import { open } from "./db.ts";
interface DB { t: { k: string; v: string } }
const { db } = open<DB>(":memory:");
await sql`create table t (k text, v text)`.execute(db);
const cases: Record<string, string> = {
  lone_low: "a\uDC80b", lone_high: "a\uD83Db", nul: "a\u0000b", crlf: "a\r\nb", astral: "a😀b", bom: "﻿a",
};
for (const [k, v] of Object.entries(cases)) await db.insertInto("t").values({ k, v }).execute();
for (const row of await db.selectFrom("t").selectAll().execute()) {
  const want = cases[row.k] as string;
  const same = row.v === want;
  console.log(row.k, same ? "same" : `differs: ${[...row.v].map((c) => c.codePointAt(0)?.toString(16)).join(" ")}`);
}
