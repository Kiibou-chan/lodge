import { expect, test } from "bun:test";
import { coreSettings, gate, type Lodge, LodgeError, NotFound } from "#app";
import { contentHash, filters, tree } from "#core";
import { area, at, decision } from "../core/builders.ts";
import { MemoryStore } from "./fakes.ts";
import { AREA, ENTRY, FIRST, project, raises, wired } from "./support.ts";

test("problems_run_the_one_state_checks", async () => {
  const [result] = await wired(
    new MemoryStore([
      AREA,
      ENTRY,
      FIRST,
      decision({ id: "d-cccccc", decidedBy: "author", quote: null, date: at(5) }),
    ]),
  ).problems();
  expect(result.problems.map((p) => p.check)).toEqual([3]);
});
function edited(store: MemoryStore) {
  const files = new Map(store.files);
  for (const [p, t] of files)
    if (p.startsWith("lodge/spec/storage/s-")) files.set(p, t.replace("Held.", "Changed."));
  return tree({ rev: null, files });
}
test("check_gate_compares_with_the_published_state", async () => {
  const store = project({ staged: true });
  store.files = new Map(edited(store).files);
  expect((await wired(store).check(false))[0].problems.map((p) => p.check)).toEqual([4]);
  expect((await wired(store).check(true))[0].problems.map((p) => p.check)).toEqual([4]);
});
test("check_gate_names_the_state_that_fails", async () => {
  const store = project(),
    bad = edited(store),
    current = tree({ rev: null, files: new Map(store.files) });
  store.gateFor = gate({
    published: current,
    checked: [
      ["committed", bad],
      ["working tree", current],
    ],
  });
  const [result] = await wired(store).check(true);
  expect(result.problems.map((p) => [p.check, p.message.split(":")[0]])).toEqual([
    [4, "committed"],
  ]);
  expect(result.problems[0]?.message).toStartWith("committed: s-aaaaaa: edited");
});
test("check_gate_merges_a_problem_both_states_have", async () => {
  const store = project(),
    bad = edited(store);
  store.gateFor = gate({
    published: tree({ rev: null, files: new Map(store.files) }),
    checked: [
      ["committed", bad],
      ["working tree", bad],
    ],
  });
  expect(
    (await wired(store).check(true))[0].problems.map((p) =>
      p.message.startsWith("committed and working tree: s-aaaaaa"),
    ),
  ).toEqual([true]);
});
test("check_gate_prints_the_gate_notes", async () => {
  const store = project(),
    current = tree({ rev: null, files: new Map(store.files) });
  store.gateFor = gate({ published: current, checked: [["", current]], notes: ["hello"] });
  const [result] = await wired(store).check(true);
  expect(result.ok).toBe(true);
  expect(result.notes).toEqual(["hello"]);
});
test("draft_prints_file_with_base", async () => {
  const store = project();
  for (const [ref, prefix] of [
    ["s-aaaaaa", "lodge/spec/storage/s-"],
    ["item-1", "lodge/decisions/"],
  ]) {
    const text = [...store.files].find(([p]) => p.startsWith(prefix ?? ""))?.[1] ?? "";
    expect(await wired(store).draft(ref ?? "")).toBe(
      text.replace("---\n", `---\nbase: ${contentHash(text)}\n`),
    );
  }
});
test("draft_area", async () => {
  const store = project();
  expect(await wired(store).draft("area:storage")).toStartWith(
    `---\nname: storage\nbase: ${contentHash(store.files.get("lodge/spec/storage/_area.md") ?? "")}\n`,
  );
  await raises(wired(store).draft("area:nowhere"), NotFound, "no area named nowhere");
  await raises(wired(store).draft("nothing"), NotFound, "no record named nothing");
});
test("core_settings_error_becomes_lodge_error", () => {
  expect(coreSettings({ length: { title_chars: 50 } }).length.titleChars).toBe(50);
  expect(() => coreSettings({ bogus: 1 })).toThrow(LodgeError);
  expect(() => coreSettings({ bogus: 1 })).toThrow("unknown key");
});
const GHOST = "lodge/spec/ghost/_area.md",
  UNREADABLE = "lodge/decisions/d-aaaaaa-keep-whole-transcripts.md";
const calls: readonly (readonly [string, (l: Lodge) => Promise<unknown>])[] = [
  [UNREADABLE, (l) => l.show("d-aaaaaa")],
  [UNREADABLE, (l) => l.draft("d-aaaaaa")],
  [GHOST, (l) => l.spec({ area: "ghost" })],
  [GHOST, (l) => l.draft("area:ghost")],
];
test.each(calls.map((c) => [c]))(
  "not_found_names_the_files_lodge_cannot_read",
  async ([path, call]) => {
    const store = project();
    store.files.set(path, "no header here\n");
    await raises(call(wired(store)), NotFound, `lodge could not read ${path}`);
  },
);
test("not_found_lists_all_unreadable_files_when_none_matches", async () => {
  const store = project();
  store.files.set(GHOST, "no header here\n");
  store.files.set("lodge/decisions/d-bbbbbb-other.md", "nothing\n");
  await raises(
    wired(store).show("d-zzzzzz"),
    NotFound,
    `lodge/decisions/d-bbbbbb-other.md, ${GHOST}, which`,
  );
});
test("timeline_refuses_a_negative_limit", async () => {
  await raises(wired(project()).timeline({ limit: -1 }), LodgeError, "limit");
});
test("not_found_does_not_call_a_missing_file_unreadable", async () => {
  const lodge = wired(new MemoryStore([ENTRY, FIRST]));
  expect((await lodge.search("", filters())).read.unrecorded.map((p) => p.path)).toEqual([
    "lodge/spec/storage/_area.md",
  ]);
  await expect(lodge.show("d-zzzzzz")).rejects.toThrow("no record named d-zzzzzz");
  await lodge.show("d-zzzzzz").catch((e) => expect(e.message).toBe("no record named d-zzzzzz"));
});
test("search_says_how_many_more_matched_beyond_the_limit", async () => {
  const lodge = wired(
    new MemoryStore([
      area(),
      ...Array.from({ length: 21 }, (_, i) =>
        decision({ id: `d-0000${String(i).padStart(2, "0")}`, title: "Cache", date: at(i) }),
      ),
    ]),
  );
  const cut = await lodge.search("", filters());
  expect([cut.items.length, cut.more]).toEqual([20, 1]);
  expect((await lodge.search("cache", filters())).more).toBe(1);
  const all = await lodge.search("", filters(), { limit: 21 });
  expect([all.items.length, all.more]).toEqual([21, 0]);
});
