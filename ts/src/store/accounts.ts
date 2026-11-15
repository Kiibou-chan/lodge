import { sql, type Transaction } from "kysely";
import {
  type Accounts,
  type AgentToken,
  type Clock,
  Conflict,
  type Passkey,
  type ServerSetup,
  stampOf,
} from "#app";
import { compareStamps, decodeUtf8 } from "#core";
import { appendEvents, json } from "./events.ts";
import type { LodgeDatabase, Tables } from "./schema.ts";

type AccountTable = "setup" | "setup_codes" | "passkeys" | "sessions" | "tokens";
export class SqliteAccounts implements Accounts {
  constructor(
    private readonly database: LodgeDatabase,
    private readonly clock: Clock,
  ) {}
  private async read<T>(table: AccountTable, id: string): Promise<T | null> {
    const row = await this.database.db
      .selectFrom(table)
      .select("body")
      .where("id", "=", id)
      .executeTakeFirst();
    return row ? (JSON.parse(decodeUtf8(row.body)) as T) : null;
  }
  private async list<T>(table: AccountTable): Promise<readonly T[]> {
    const rows = await this.database.db
      .selectFrom(table)
      .select("body")
      .orderBy("seq", "asc")
      .execute();
    return rows.map((row) => JSON.parse(decodeUtf8(row.body)) as T);
  }
  private async append(tx: Transaction<Tables>, kind: string, body: unknown): Promise<void> {
    await appendEvents(tx, "", "server", stampOf(this.clock.now()), [
      { kind, body: json(body), path: null, message: null },
    ]);
  }
  private async write(kind: string, body: unknown): Promise<void> {
    await this.database.db.transaction().execute((tx) => this.append(tx, kind, body));
  }
  // A write starts the transaction before any decision is read.
  private async lock(tx: Transaction<Tables>, table: AccountTable): Promise<void> {
    await tx
      .updateTable(table)
      .set({ seq: sql.ref("seq") })
      .execute();
  }
  setup(): Promise<ServerSetup | null> {
    return this.read("setup", "server");
  }
  async setUp(setup: ServerSetup): Promise<void> {
    await this.database.db.transaction().execute(async (tx) => {
      await this.lock(tx, "setup");
      if (await tx.selectFrom("setup").select("id").executeTakeFirst())
        throw new Conflict("the server is already set up");
      await this.append(tx, "server-set-up", setup);
    });
  }
  issueSetupCode(hash: string, expires: string): Promise<void> {
    return this.write("setup-code-issued", { hash, expires });
  }
  private async valid(tx: Transaction<Tables>, hash: string): Promise<boolean> {
    const row = await tx
      .selectFrom("setup_codes")
      .selectAll()
      .orderBy("seq", "desc")
      .limit(1)
      .executeTakeFirst();
    if (!row || row.id !== hash) return false;
    const { expires } = JSON.parse(decodeUtf8(row.body)) as { expires: string };
    return compareStamps(stampOf(this.clock.now()), expires) < 0;
  }
  async setupCodeValid(hash: string): Promise<boolean> {
    return this.database.db.transaction().execute((tx) => this.valid(tx, hash));
  }
  async spendSetupCode(hash: string): Promise<boolean> {
    return this.database.db.transaction().execute(async (tx) => {
      await this.lock(tx, "setup_codes");
      if (!(await this.valid(tx, hash))) return false;
      await this.append(tx, "setup-code-spent", { hash });
      return true;
    });
  }
  passkeys(): Promise<readonly Passkey[]> {
    return this.list("passkeys");
  }
  addPasskey(passkey: Passkey): Promise<void> {
    return this.write("passkey-added", passkey);
  }
  usePasskey(id: string, counter: number): Promise<void> {
    return this.write("passkey-used", { id, counter });
  }
  startSession(hash: string, expires: string): Promise<void> {
    return this.write("session-started", { hash, expires });
  }
  async sessionExpiry(hash: string): Promise<string | null> {
    return (await this.read<{ expires: string }>("sessions", hash))?.expires ?? null;
  }
  endSession(hash: string): Promise<void> {
    return this.write("session-ended", { hash });
  }
  issueToken(token: AgentToken, hash: string): Promise<void> {
    const { id, project, role, label, issued, revoked } = token;
    return this.database.db.transaction().execute(async (tx) => {
      await this.lock(tx, "tokens");
      if (await tx.selectFrom("tokens").select("id").where("id", "=", id).executeTakeFirst())
        throw new Conflict(`a token already exists under ID ${id}`);
      await this.append(tx, "token-issued", { id, project, role, label, issued, revoked, hash });
    });
  }
  private token(value: AgentToken & { hash: string }): AgentToken {
    const { hash: _hash, ...token } = value;
    return token;
  }
  async tokenFor(hash: string): Promise<AgentToken | null> {
    const tokens = await this.list<AgentToken & { hash: string }>("tokens");
    const value = tokens.find((token) => token.hash === hash && token.revoked === null);
    return value ? this.token(value) : null;
  }
  async revokeToken(id: string): Promise<boolean> {
    return this.database.db.transaction().execute(async (tx) => {
      await this.lock(tx, "tokens");
      const row = await tx
        .selectFrom("tokens")
        .select("body")
        .where("id", "=", id)
        .executeTakeFirst();
      if (!row || (JSON.parse(decodeUtf8(row.body)) as AgentToken).revoked !== null) return false;
      await this.append(tx, "token-revoked", { id });
      return true;
    });
  }
  async tokens(): Promise<readonly AgentToken[]> {
    return (await this.list<AgentToken & { hash: string }>("tokens")).map((token) =>
      this.token(token),
    );
  }
}
