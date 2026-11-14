import { Database } from "bun:sqlite";
import { type Generated, Kysely, SqliteDialect } from "kysely";
import { LodgeError } from "#app";

interface EventsTable {
  seq: Generated<number>;
  project: string;
  at: string;
  actor: string;
  kind: string;
  path: string | null;
  body: Uint8Array;
  message: string | null;
}
interface HeadsTable {
  project: string;
  rev: number;
}
interface FilesTable {
  project: string;
  path: string;
  body: Uint8Array;
  seq: number;
}
interface MembersTable {
  project: string;
  person: string;
  role: string;
}
export interface Tables {
  events: EventsTable;
  heads: HeadsTable;
  files: FilesTable;
  members: MembersTable;
}
export interface LodgeDatabase {
  readonly db: Kysely<Tables>;
  close(): Promise<void>;
}
const MIGRATIONS = [
  `
create table events(seq integer primary key autoincrement, project text not null,
  at text not null, actor text not null, kind text not null, path text, body blob not null, message text);
create trigger events_no_replace before insert on events
  when exists (select 1 from events where seq = new.seq) begin
  select raise(abort, 'events are append-only'); end;
create trigger events_no_update before update on events begin
  select raise(abort, 'events are append-only'); end;
create trigger events_no_delete before delete on events begin
  select raise(abort, 'events are append-only'); end;
create table heads(project text primary key, rev integer not null);
create table files(project text not null, path text not null, body blob not null,
  seq integer not null, primary key(project, path));
create table members(project text not null, person text not null, role text not null,
  primary key(project, person));
`,
];
export async function openDatabase(path: string): Promise<LodgeDatabase> {
  const raw = new Database(path, { strict: true, create: true });
  try {
    raw.exec("PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000");
    raw
      .transaction(() => {
        const version = (raw.query("PRAGMA user_version").get() as { user_version: number })
          .user_version;
        if (version > MIGRATIONS.length)
          throw new LodgeError(
            `the database at ${path} has schema ${version}, newer than this lodge's ${MIGRATIONS.length}`,
          );
        for (const migration of MIGRATIONS.slice(version)) raw.exec(migration);
        raw.exec(`PRAGMA user_version=${MIGRATIONS.length}`);
      })
      .immediate();
  } catch (error) {
    raw.close();
    throw error;
  }
  const adapted = {
    close: () => raw.close(),
    prepare: (query: string) => {
      const statement = raw.prepare(query);
      return {
        reader: statement.columnNames.length > 0,
        all: (parameters: unknown[]) => statement.all(...(parameters as never[])),
        run: (parameters: unknown[]) => {
          const result = statement.run(...(parameters as never[]));
          return { changes: result.changes, lastInsertRowid: result.lastInsertRowid };
        },
        iterate: (parameters: unknown[]) => statement.iterate(...(parameters as never[])),
      };
    },
  };
  const db = new Kysely<Tables>({ dialect: new SqliteDialect({ database: adapted as never }) });
  return { db, close: () => db.destroy() };
}
