import { expect, test } from "bun:test";
import { type Lodge, LodgeError, NotFound, type Read } from "#app";
import { Action, filters } from "#core";
import { area, at, decision, entry } from "../core/builders.ts";
import { MemoryStore } from "./fakes.ts";
import { FIRST, project, raises, wired } from "./support.ts";

test("show_of_an_entry_carries_the_deciding_views_with_its_reasoning", async () => {
  const lodge = wired(project());
  expect((await lodge.show("s-aaaaaa")).changing).toEqual([]);
  expect((await lodge.show("d-aaaaaa", { reasoning: true })).changing).toEqual([]);
  expect((await lodge.show("s-aaaaaa", { reasoning: true })).changing.map((v) => v.id)).toEqual([
    "d-aaaaaa",
  ]);
});
test("show_resolves_code_and_levels", async () => {
  const lodge = wired(project()),
    shown = await lodge.show("item-1");
  expect([shown.level1.id, shown.level1.code, shown.level1.decidedBy]).toEqual([
    "d-aaaaaa",
    "ITEM-1",
    "author",
  ]);
  expect([shown.level2, shown.level3]).toEqual([null, null]);
  const full = await lodge.show("D-AAAAAA", { reasoning: true, provenance: true });
  expect(full.level2).toBe("Because they are evidence.");
  expect(full.level3?.quote).toEqual({
    text: "Do it.",
    where: "a session",
    when: "2026-10-28 10:00",
  });
  expect(full.read.freshness).toBe("fetched 2026-10-29T08:00:00+00:00");
});
test("show_unknown_ref_is_an_error", async () => {
  const call = wired(project()).show("nothing");
  await raises(call, NotFound, "no record named nothing");
  await expect(call).rejects.toMatchObject({ exitCode: 2 });
});
test("show_ambiguous_code_is_an_error", async () => {
  const call = wired(
    new MemoryStore([area(), FIRST, decision({ id: "d-cccccc", code: "item-1", date: at(5) })]),
  ).show("ITEM-1");
  await raises(call, LodgeError, "more than one record");
  await call.catch((e) => expect(e).not.toBeInstanceOf(NotFound));
});
test("show_flags_a_failing_record", async () => {
  const shown = await wired(
    new MemoryStore([
      FIRST,
      decision({ id: "d-cccccc", decidedBy: "author", quote: null, date: at(5) }),
    ]),
  ).show("d-cccccc");
  expect(shown.level1.flags).toContain("fails check");
});
test("search_listed_with_read", async () => {
  const listed = await wired(project()).search("transcripts", filters());
  expect(listed.items.map((v) => v.id)).toEqual(["s-aaaaaa", "d-aaaaaa"]);
  expect(listed.read.freshness).toBe("fetched 2026-10-29T08:00:00+00:00");
  expect(listed.read.unrecorded).toEqual([]);
});
test("search_honours_filters", async () => {
  expect(
    (await wired(project()).search("", filters({ kind: "decision" }))).items.map((v) => v.id),
  ).toEqual(["d-aaaaaa"]);
});
const reads: ((lodge: Lodge) => Promise<Read>)[] = [
  async (l) => (await l.search("", filters())).read,
  async (l) => (await l.show("d-aaaaaa")).read,
  async (l) => (await l.waitingAll())[0].read,
  async (l) => (await l.timeline()).read,
  async (l) => (await l.spec())[1],
  async (l) => (await l.problems())[1],
  async (l) => (await l.check(false))[1],
  async (l) => (await l.check(true))[1],
];
test.each(reads.map((c) => [c]))("unparsable_file_reported_by_every_read", async (read) => {
  const store = project(),
    bad = "lodge/decisions/d-bbbbbb-broken.md";
  store.files.set(bad, "no header here\n");
  expect((await read(wired(store))).unrecorded.map((p) => p.path)).toEqual([bad]);
});
test("waiting_lists_flagged", async () => {
  const agent = decision({
    id: "d-cccccc",
    title: "Reword transcripts",
    changes: [{ entry: "s-aaaaaa", action: Action.EDIT }],
    date: at(10),
  });
  const listed = (
    await wired(
      new MemoryStore([area({ order: ["s-aaaaaa"] }), entry({ id: "s-aaaaaa" }), FIRST, agent]),
    ).waitingAll()
  )[0];
  expect(listed.items.map((v) => v.id)).toEqual(["d-cccccc"]);
  expect(listed.items[0]?.flags).toContain("awaiting the author");
  expect((await wired(project()).waitingAll())[0].items).toEqual([]);
});
test("timeline_newest_first_and_limited", async () => {
  const later = [
    [5, "c"],
    [9, "d"],
    [7, "e"],
  ] as const;
  const lodge = wired(
    new MemoryStore([
      FIRST,
      ...later.map(([i, c]) =>
        decision({ id: `d-${c.repeat(6)}`, title: `Later ${c}`, date: at(i) }),
      ),
    ]),
  );
  expect((await lodge.timeline()).items.map((v) => v.id)).toEqual([
    "d-dddddd",
    "d-eeeeee",
    "d-cccccc",
    "d-aaaaaa",
  ]);
  const cut = await lodge.timeline({ limit: 2 });
  expect(cut.items.map((v) => v.id)).toEqual(["d-dddddd", "d-eeeeee"]);
  expect(cut.more).toBe(2);
  expect((await lodge.timeline()).more).toBe(0);
});
test("spec_renders_and_narrows_to_an_area", async () => {
  const lodge = wired(
    new MemoryStore([
      area({ order: ["s-aaaaaa"] }),
      entry({ id: "s-aaaaaa" }),
      area({ name: "access", title: "Access", order: ["s-bbbbbb"] }),
      entry({ id: "s-bbbbbb", area: "access", title: "Open to all", statement: "Anyone." }),
      FIRST,
    ]),
  );
  const [text, read, areas] = await lodge.spec();
  expect(text).toContain("# Access");
  expect(text).toContain("## An entry (s-aaaaaa)");
  expect(read.unrecorded).toEqual([]);
  expect(areas.map((a) => [a.name, a.entries.map((v) => v.id)])).toEqual([
    ["access", ["s-bbbbbb"]],
    ["storage", ["s-aaaaaa"]],
  ]);
  const narrowed = await lodge.spec({ area: "access" });
  expect(narrowed[0]).toBe("# Access\n\n## Open to all (s-bbbbbb)\n\nAnyone.\n");
  expect(narrowed[2].map((a) => a.name)).toEqual(["access"]);
  await raises(lodge.spec({ area: "nowhere" }), NotFound, "no area named nowhere");
});
