import { expect, test } from "bun:test";
import { AddOutcome, Conflict, LodgeError } from "#app";
import { Action, checkState, load, tree } from "#core";
import { areaText, decisionText, specText } from "../core/applying.ts";
import { area, at, decision, entry, filesOf } from "../core/builders.ts";
import { Interleaving } from "../store/interleaving.ts";
import { seeded } from "../store/seed.ts";
import { AREA, ENTRY, FIRST, raises, wired } from "./support.ts";

const NEW: readonly (readonly [string, string])[] = [
  ["d.md", decisionText("changes:", "  - {entry: s-bbbbbb, action: create}")],
  ["s.md", specText("id: s-bbbbbb", "area: storage", { body: "Everything is kept." })],
];
const CONCURRENT = filesOf(
  area({
    name: "storage",
    title: "Storage",
    intro: "How it keeps data.",
    order: ["s-aaaaaa", "s-cccccc"],
  }),
  entry({ id: "s-cccccc", area: "storage", title: "Another entry" }),
  decision({
    id: "d-cccccc",
    changes: [{ entry: "s-cccccc", action: Action.CREATE }],
    date: at(20),
  }),
);
const NOISE = Array.from(
  { length: 5 },
  (_, i) => new Map([[`lodge/attachments/d-aaaaaa/${i}.txt`, "x"]]),
);
async function wrapped(full = false) {
  return new Interleaving((await (full ? seeded(AREA, ENTRY, FIRST) : seeded(AREA))).store);
}
test("add_retry_keeps_concurrent_entry", async () => {
  const store = await wrapped(true);
  store.rejectNext(CONCURRENT);
  const added = await wired(store).add(NEW);
  expect(added.outcome).toBe(AddOutcome.PUBLISHED);
  expect(store.attempts).toBe(2);
  const s = load(tree({ rev: null, files: await store.files() }));
  expect(s.areas.get("storage")?.order).toEqual(["s-aaaaaa", "s-cccccc", "s-bbbbbb"]);
  expect(s.decisions.has("d-cccccc")).toBe(true);
  expect(s.decisions.has(added.ids[0] as string)).toBe(true);
  expect(checkState(s).ok).toBe(true);
});
test("add_retry_concurrent_edit_of_same_entry_conflicts", async () => {
  const store = await wrapped(true),
    lodge = wired(store);
  const draft = (await lodge.draft("s-aaaaaa")).replace("Held.", "Mine.");
  const files = await store.files();
  const path = [...files.keys()].find((p) => p.startsWith("lodge/spec/storage/s-")) as string;
  store.rejectNext(new Map([[path, (files.get(path) as string).replace("Held.", "Theirs.")]]));
  await raises(
    lodge.add([
      ["e.md", draft],
      ["d.md", decisionText("changes:", "  - {entry: s-aaaaaa, action: edit}")],
    ]),
    Conflict,
    "it changed since the draft was made",
  );
  expect(store.publishes).toEqual([]);
  expect(store.attempts).toBe(1);
  expect((await store.files()).get(path)).toContain("Theirs.");
});
test("add_gives_up_after_three", async () => {
  const store = await wrapped();
  store.rejectNext(...NOISE.slice(0, 4));
  try {
    await wired(store).add(NEW);
    throw new Error("expected conflict");
  } catch (e) {
    expect(e).toBeInstanceOf(Conflict);
    expect((e as Conflict).message).toContain("three times");
    expect((e as Conflict).exitCode).toBe(1);
  }
  expect(store.attempts).toBe(3);
  expect(store.publishes).toEqual([]);
});
test("ref_moving_between_reads_retries", async () => {
  const store = await wrapped();
  store.movesAfterRead(NOISE[0] as Map<string, string>);
  expect((await wired(store).add(NEW)).outcome).toBe(AddOutcome.PUBLISHED);
  expect(store.attempts).toBe(2);
  expect((await store.files()).has("lodge/attachments/d-aaaaaa/0.txt")).toBe(true);
});
test("area_created_by_another_add_is_a_conflict", async () => {
  const store = new Interleaving((await seeded()).store);
  store.rejectNext(filesOf(area({ name: "storage", title: "Storage" })));
  try {
    await wired(store).add([...NEW, ["a.md", areaText("name: storage")]]);
    throw new Error("expected conflict");
  } catch (e) {
    expect(e).toBeInstanceOf(Conflict);
    expect((e as Conflict).exitCode).toBe(1);
  }
  expect(store.publishes).toEqual([]);
});
test("entry_created_by_another_add_is_a_conflict", async () => {
  const store = await wrapped();
  store.rejectNext(
    filesOf(
      entry({ id: "s-bbbbbb", area: "storage", title: "Theirs" }),
      decision({
        id: "d-cccccc",
        changes: [{ entry: "s-bbbbbb", action: Action.CREATE }],
        date: at(20),
      }),
    ),
  );
  try {
    await wired(store).add(NEW);
    throw new Error("expected conflict");
  } catch (e) {
    expect(e).toBeInstanceOf(Conflict);
    expect((e as Conflict).exitCode).toBe(1);
  }
  expect(store.attempts).toBe(1);
  expect(store.publishes).toEqual([]);
});
test("refusal_on_the_first_attempt_is_a_usage_error", async () => {
  const store = await wrapped();
  store.rejectNext(NOISE[0] as Map<string, string>);
  try {
    await wired(store).add([["e.md", specText("id: s-bbbbbb")]]);
    throw new Error("expected usage error");
  } catch (e) {
    expect(e).toBeInstanceOf(LodgeError);
    expect(e).not.toBeInstanceOf(Conflict);
    expect((e as LodgeError).exitCode).toBe(2);
  }
  expect(store.attempts).toBe(0);
});
test.each([
  [areaText("name: [a, b]")],
  [specText("id: [s-bbbbbb]", "area: storage")],
  [specText("id: {x: 1}", "area: storage")],
])("unhashable_names_are_usage_errors", async (text) => {
  const store = await wrapped(true);
  try {
    await wired(store).add([["x.md", text]]);
    throw new Error("expected usage error");
  } catch (e) {
    expect(e).toBeInstanceOf(LodgeError);
    expect(e).not.toBeInstanceOf(Conflict);
  }
});
