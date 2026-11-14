import { Database } from "bun:sqlite";
import { Kysely, SqliteDialect } from "kysely";
export function open<DB>(path: string): { db: Kysely<DB>; raw: Database } {
  const raw = new Database(path, { strict: true });
  const adapted = {
    close: () => raw.close(),
    prepare: (sql: string) => {
      const st = raw.prepare(sql);
      return {
        reader: st.columnNames.length > 0,
        all: (p: unknown[]) => st.all(...(p as never[])),
        run: (p: unknown[]) => {
          const r = st.run(...(p as never[]));
          return { changes: r.changes, lastInsertRowid: r.lastInsertRowid };
        },
        iterate: (p: unknown[]) => st.iterate(...(p as never[])),
      };
    },
  };
  return { db: new Kysely<DB>({ dialect: new SqliteDialect({ database: adapted as never }) }), raw };
}
