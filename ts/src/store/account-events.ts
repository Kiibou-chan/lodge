import type { Selectable, Transaction } from "kysely";
import { decodeUtf8, encodeUtf8 } from "#core";

const json = (value: unknown): Uint8Array => encodeUtf8(JSON.stringify(value));

import type { Tables } from "./schema.ts";

export async function applyAccountEvent(
  tx: Transaction<Tables>,
  row: Selectable<Tables["events"]>,
): Promise<boolean> {
  const body = JSON.parse(decodeUtf8(row.body)) as { id?: string; hash?: string; counter?: number };
  const tables = {
    "server-set-up": "setup",
    "setup-code-issued": "setup_codes",
    "passkey-added": "passkeys",
    "session-started": "sessions",
    "token-issued": "tokens",
  } as const;
  if (row.kind in tables) {
    const table = tables[row.kind as keyof typeof tables];
    const id = table === "setup" ? "server" : String(body.id ?? body.hash);
    await tx
      .insertInto(table)
      .values({ id, body: row.body, seq: row.seq })
      .onConflict((c) => c.column("id").doUpdateSet({ body: row.body, seq: row.seq }))
      .execute();
    return true;
  }
  switch (row.kind) {
    case "setup-code-spent":
    case "session-ended": {
      const table = row.kind === "setup-code-spent" ? "setup_codes" : "sessions";
      await tx.deleteFrom(table).where("id", "=", String(body.hash)).execute();
      // A spent newest code must still supersede every older code.
      if (table === "setup_codes") await tx.deleteFrom(table).execute();
      return true;
    }
    case "passkey-used":
    case "token-revoked": {
      const table = row.kind === "passkey-used" ? "passkeys" : "tokens";
      const id = String(body.id);
      const old = await tx
        .selectFrom(table)
        .select("body")
        .where("id", "=", id)
        .executeTakeFirstOrThrow();
      const value = JSON.parse(decodeUtf8(old.body)) as Record<string, unknown>;
      const updated =
        row.kind === "passkey-used"
          ? { ...value, counter: body.counter }
          : { ...value, revoked: row.at };
      await tx
        .updateTable(table)
        .set({ body: json(updated) })
        .where("id", "=", id)
        .execute();
      return true;
    }
    default:
      return false;
  }
}
