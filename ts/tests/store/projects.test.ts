import { expect, test } from "bun:test";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { Conflict, LodgeError, NotFound, person, Role } from "#app";
import { openDatabase, SqliteProjects, SqliteStore } from "#store";
import { FixedClock } from "../app/fakes.ts";
import { decision, filesOf, message, thread } from "../core/builders.ts";
import { events, setup } from "./support.ts";

test("create_writes_the_project_and_its_owner", async () => {
  const { database, projects } = await setup();
  expect(
    (await events(database)).map((e) => [
      e.kind,
      e.actor,
      JSON.parse(new TextDecoder().decode(e.body)),
    ]),
  ).toEqual([
    ["project", "ada", { owner: "ada" }],
    ["member", "ada", { person: "ada", role: "owner" }],
  ]);
  expect(await projects.members("storage")).toEqual(new Map([["ada", Role.OWNER]]));
  expect(projects.storeFor("storage", person("ada"))).toBeInstanceOf(SqliteStore);
});
test("existing_project_conflicts", async () => {
  const { projects } = await setup();
  await expect(projects.create("storage", "bo")).rejects.toThrow(
    new Conflict("a project named storage exists"),
  );
});
test.each([
  ["Lodge", "ada"],
  ["-x", "ada"],
  ["x".repeat(64), "ada"],
  ["storage", "Ada"],
  ["storage", "1ada"],
])("names_are_checked", async (project, owner) => {
  const { projects, database } = await setup();
  const before = await events(database);
  await expect(projects.create(project, owner)).rejects.toThrow(LodgeError);
  expect(await events(database)).toEqual(before);
});
test("add_member_needs_a_new_name", async () => {
  const { projects, database } = await setup();
  await projects.addMember("storage", "bo", Role.MEMBER, person("ada"));
  expect([...(await projects.members("storage"))]).toEqual([
    ["ada", Role.OWNER],
    ["bo", Role.MEMBER],
  ]);
  expect((await events(database)).at(-1)?.actor).toBe("ada");
  await expect(projects.addMember("storage", "bo", Role.OWNER, person("ada"))).rejects.toThrow(
    "bo is a member of storage",
  );
  await expect(projects.addMember("storage", "Ada", Role.MEMBER, person("ada"))).rejects.toThrow(
    LodgeError,
  );
});
test("unknown_project_is_not_found", async () => {
  const { projects, database, clock } = await setup();
  await expect(projects.members("unknown")).rejects.toThrow(
    new NotFound("no project named unknown"),
  );
  await expect(projects.addMember("unknown", "bo", Role.MEMBER, person("ada"))).rejects.toThrow(
    NotFound,
  );
  await expect(new SqliteStore(database, "unknown", "ada", clock).trees()).rejects.toThrow(
    NotFound,
  );
});
test("a_second_create_conflicts_across_connections", async () => {
  const folder = mkdtempSync(join(tmpdir(), "lodge-store-"));
  const a = await openDatabase(join(folder, "store.db"));
  const b = await openDatabase(join(folder, "store.db"));
  try {
    const clock = new FixedClock();
    await new SqliteProjects(a, clock).create("storage", "ada");
    await expect(new SqliteProjects(b, clock).create("storage", "bo")).rejects.toThrow(Conflict);
  } finally {
    await a.close();
    await b.close();
    rmSync(folder, { recursive: true });
  }
});
test("a_name_used_as_a_role_cannot_join", async () => {
  const { store, projects, database } = await setup();
  await store.publish(
    (await store.trees())[0],
    filesOf(
      decision({ id: "d-aaaaaa", decidedBy: "reviewer" }),
      thread({ id: "q-aaaaaa", messages: [message({ by: "builder" })] }),
    ),
    "",
  );
  const before = await events(database);
  for (const [name, id] of [
    ["reviewer", "d-aaaaaa"],
    ["builder", "q-aaaaaa"],
  ] as const)
    await expect(projects.addMember("storage", name, Role.MEMBER, person("ada"))).rejects.toThrow(
      `${name} is a role in ${id}, so it cannot name a person`,
    );
  expect(await events(database)).toEqual(before);
});
