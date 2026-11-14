import { Database } from "bun:sqlite";
import { Kysely, SqliteDialect, type Generated } from "kysely";
interface Events { seq: Generated<number>; kind: string; body: string }
interface DB { events: Events }
export function open(path: string): Kysely<DB> {
  const db = new Database(path, { strict: true });
  db.exec("PRAGMA journal_mode=WAL");
  // bun:sqlite Database is close to better-sqlite3; adapt
  const adapted = {
    close: () => db.close(),
    prepare: (sql: string) => {
      const st = db.prepare(sql);
      return {
        reader: st.columnNames.length > 0,
        all: (p: unknown[]) => st.all(...(p as never[])),
        run: (p: unknown[]) => { const r = st.run(...(p as never[])); return { changes: r.changes, lastInsertRowid: r.lastInsertRowid }; },
        iterate: (p: unknown[]) => st.iterate(...(p as never[])),
      };
    },
  };
  return new Kysely<DB>({ dialect: new SqliteDialect({ database: adapted as never }) });
}
export async function handler(req: Request): Promise<Response> {
  const url = new URL(req.url);
  if (req.method === "POST" && url.pathname === "/api/echo") return Response.json(await req.json());
  return new Response("not found", { status: 404 });
}
