import { expect, test } from "bun:test";
import type { KyselyPlugin, RootOperationNode } from "kysely";
import { type HeldDraft, NotFound, person, Role } from "#app";
import { SqliteProjects, SqliteStore } from "#store";
import { events, setup } from "./support.ts";

const draft: HeldDraft = {
  kind: "add",
  person: "ada",
  by: "agent",
  drafts: [],
  attachments: [],
  importing: false,
  message: "add",
};

test.each(["create", "addMember", "publish", "decline", "approve"])(
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
    const seq = await store.hold(draft);
    const base = (await store.trees())[0];
    statements.length = 0;
    if (operation === "create") await projects.create("other", "ada");
    else if (operation === "addMember")
      await projects.addMember("storage", "bo", Role.MEMBER, person("author"));
    else if (operation === "decline") await store.decline(seq, "no");
    else if (operation === "approve")
      await store.publish(base, new Map([["lodge/a", "a"]]), "", seq);
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

test.each(["hold", "decline"])("missing_project: %s", async (operation) => {
  const { database, clock } = await setup();
  const store = new SqliteStore(database, "missing", "ada", clock);
  const before = await events(database);
  const refusal = operation === "hold" ? store.hold(draft) : store.decline(1, "no");
  await expect(refusal).rejects.toBeInstanceOf(NotFound);
  await expect(refusal).rejects.toThrow("no project named missing");
  expect(await events(database)).toEqual(before);
});
