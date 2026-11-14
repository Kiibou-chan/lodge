import { expect, test } from "bun:test";
import type { KyselyPlugin, RootOperationNode } from "kysely";
import { person, Role } from "#app";
import { SqliteProjects, SqliteStore } from "#store";
import { setup } from "./support.ts";

test.each(["create", "addMember", "publish"])(
  "transaction_writes_heads_first: %s",
  async (operation) => {
    const { database, clock } = await setup();
    const statements: RootOperationNode[] = [];
    const plugin: KyselyPlugin = {
      transformQuery({ node }) {
        statements.push(node);
        return node;
      },
      async transformResult({ result }) {
        return result;
      },
    };
    const observed = { ...database, db: database.db.withPlugin(plugin) };
    const projects = new SqliteProjects(observed, clock);
    const store = new SqliteStore(observed, "storage", "ada", clock);
    const base = (await store.trees())[0];
    statements.length = 0;
    if (operation === "create") await projects.create("other", "ada");
    else if (operation === "addMember")
      await projects.addMember("storage", "bo", Role.MEMBER, person("ada"));
    else await store.publish(base, new Map([["lodge/a", "a"]]), "");
    const first = statements[0];
    expect(first?.kind).toBe(operation === "create" ? "InsertQueryNode" : "UpdateQueryNode");
    expect(first).toMatchObject(
      operation === "create"
        ? { into: { table: { identifier: { name: "heads" } } } }
        : { table: { table: { identifier: { name: "heads" } } } },
    );
  },
);
