import { expect, test } from "bun:test";
import {
  Conflict,
  coreSettings,
  Forbidden,
  importStore,
  LodgeError,
  type Projects,
  Role,
} from "#app";
import { instant, tree } from "#core";
import { FixedClock, MemoryStore, START } from "./fakes.ts";
import { zeroTwoCopy } from "./zero-two-copy.ts";

const copy = zeroTwoCopy();
const settings = coreSettings(copy.settings);
function world(members: ReadonlyMap<string, Role> = new Map([["ana", Role.OWNER]])) {
  const store = new MemoryStore([], { people: new Set(["ana"]) });
  const clock = new FixedClock({ epochMs: instant("2026-11-03T00:00:00+00:00"), offsetMinutes: 0 });
  const selected: unknown[] = [];
  const projects: Pick<Projects, "members" | "storeFor"> = {
    async members(project) {
      expect(project).toBe("moved");
      return members;
    },
    storeFor(project, actor) {
      selected.push([project, actor]);
      return store;
    },
  };
  return { store, clock, selected, projects };
}

test("owner_imports_into_an_empty_project", async () => {
  const { store, clock, selected, projects } = world();
  const result = await importStore(copy, "moved", "ana", projects, settings, clock);
  expect(result).toEqual({
    kind: "imported",
    rev: copy.rev,
    decisions: 4,
    entries: 1,
    areas: 1,
    threads: 1,
    attachments: 1,
    mapped: ["d-40q44p", "d-qqrf9k", "d-t46j05", "q-j2dsgk"],
  });
  expect(selected).toEqual([["moved", { kind: "person", name: "ana" }]]);
  expect(store.publishes).toHaveLength(1);
  expect(store.publishes[0]?.[0].size).toBe(8);
  expect(store.publishes[0]?.[1]).toBe("Import the lodge 0.2 store at synthetic-revision");
  expect(store.files.size).toBe(8);
  expect(await store.held()).toEqual([]);
});

test("requester_must_be_the_owner", async () => {
  const { store, clock, selected, projects } = world();
  const result = importStore(copy, "moved", "bo", projects, settings, clock);
  await expect(result).rejects.toBeInstanceOf(Forbidden);
  await expect(result).rejects.toThrow("only ana, the owner of project moved, may import into it");
  expect(selected).toEqual([]);
  expect(store.attempts).toBe(0);
});

test("project_with_two_owners_is_refused", async () => {
  const { store, clock, selected, projects } = world(
    new Map([
      ["ana", Role.OWNER],
      ["bo", Role.OWNER],
    ]),
  );
  const result = importStore(copy, "moved", "ana", projects, settings, clock);
  await expect(result).rejects.toBeInstanceOf(LodgeError);
  await expect(result).rejects.toThrow(
    "project moved has 2 owners; lodge imports into a project with one owner",
  );
  expect(selected).toEqual([]);
  expect(store.attempts).toBe(0);
});

test("project_with_no_owner_is_refused", async () => {
  const { store, clock, selected, projects } = world(new Map([["bo", Role.MEMBER]]));
  await expect(importStore(copy, "moved", "ana", projects, settings, clock)).rejects.toThrow(
    "project moved has 0 owners; lodge imports into a project with one owner",
  );
  expect(selected).toEqual([]);
  expect(store.attempts).toBe(0);
});

test.each(["lodge/decisions/existing.md", "lodge/attachments/d-q59cdf/raw.bin"])(
  "project_with_records_is_a_conflict (%s)",
  async (path) => {
    const { store, clock, projects } = world();
    store.files.set(path, "Existing text.\n");
    const result = importStore(copy, "moved", "ana", projects, settings, clock);
    await expect(result).rejects.toBeInstanceOf(Conflict);
    await expect(result).rejects.toThrow(
      "project moved already holds records; lodge imports a store into an empty project only",
    );
    expect(store.attempts).toBe(0);
    expect(store.files).toEqual(new Map([[path, "Existing text.\n"]]));
  },
);

test("failed_check_publishes_nothing", async () => {
  const { store, clock, projects } = world();
  const result = await importStore(copy, "moved", "ana", projects, coreSettings({}), clock);
  expect(result).toMatchObject({ kind: "check-failed", stage: "server" });
  expect(store.attempts).toBe(0);
  expect(store.files.size).toBe(0);
});

test("rejected_publish_is_a_conflict", async () => {
  const { store, clock, projects } = world();
  store.rejectNext(new Map());
  const result = importStore(copy, "moved", "ana", projects, settings, clock);
  await expect(result).rejects.toBeInstanceOf(Conflict);
  await expect(result).rejects.toThrow(
    "project moved changed during the import; nothing was imported",
  );
  expect(store.attempts).toBe(1);
  expect(store.publishes).toEqual([]);
  expect(store.files.size).toBe(0);
});

test("now_is_the_clocks", async () => {
  const { store, projects } = world();
  const clock = new FixedClock(START);
  const result = await importStore(copy, "moved", "ana", projects, settings, clock);
  expect(result).toMatchObject({ kind: "check-failed", stage: "lodge 0.2" });
  if (result.kind !== "check-failed") throw new Error("expected failed check");
  expect(result.problems).toContainEqual(expect.objectContaining({ check: 1 }));
  expect(clock.calls).toBe(1);
  expect(store.attempts).toBe(0);
});

test("project_with_separate_attachments_is_a_conflict", async () => {
  const { store, clock, projects } = world();
  store.trees = async () => {
    const current = tree({
      rev: "0",
      files: new Map(),
      attachments: new Set(["lodge/attachments/d-q59cdf/raw.bin"]),
      people: store.people,
    });
    return [current, current];
  };
  await expect(importStore(copy, "moved", "ana", projects, settings, clock)).rejects.toBeInstanceOf(
    Conflict,
  );
  expect(store.attempts).toBe(0);
});
