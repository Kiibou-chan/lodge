// Probe C: Kysely's SQLite driver serialises transactions on its one connection.
import { sql } from "kysely";
import { open } from "./db.ts";
interface DB { e: { seq: number; who: string } }
const { db } = open<DB>(":memory:");
await sql`create table e (seq integer primary key autoincrement, who text not null)`.execute(db);
const log: string[] = [];
const tick = () => new Promise((r) => setTimeout(r, 5));
async function writer(who: string): Promise<void> {
  await db.transaction().execute(async (tx) => {
    log.push(`${who} begin`);
    const top = await tx.selectFrom("e").select((eb) => eb.fn.max("seq").as("m")).executeTakeFirst();
    await tick();
    await tx.insertInto("e").values({ who } as never).execute();
    log.push(`${who} insert after ${top?.m ?? 0}`);
  });
}
async function reader(): Promise<void> {
  await tick();
  const n = await db.selectFrom("e").select((eb) => eb.fn.countAll().as("n")).executeTakeFirst();
  log.push(`reader saw ${n?.n}`);
}
await Promise.all([writer("a"), writer("b"), reader()]);
console.log(log.join("; "));
// append-only triggers
await sql`create trigger e_no_update before update on e begin select raise(abort, 'events are append-only'); end`.execute(db);
await sql`create trigger e_no_delete before delete on e begin select raise(abort, 'events are append-only'); end`.execute(db);
for (const q of [sql`update e set who = 'x'`, sql`delete from e`]) {
  try { await q.execute(db); console.log("allowed"); } catch (e) { console.log("refused:", (e as Error).message); }
}
