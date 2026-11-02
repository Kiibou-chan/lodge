import { expect, test } from "bun:test";
import { Action, derive, renderSpec, specView } from "#core";
import { area, at, decision, entry, snapshotOf } from "./builders.ts";
import { NOTES } from "./checks.ts";

const NONE = new Set<string>();
test("render_spec_skips_retired_follows_order", () => {
  const first = entry({ id: "s-aaaaaa", title: "First", statement: "One.", area: "storage" });
  const second = entry({ id: "s-bbbbbb", title: "Second", statement: "Two.", area: "storage" });
  const gone = entry({ id: "s-cccccc", title: "Gone", statement: "Three.", area: "storage" });
  const loose = entry({ id: "s-dddddd", title: "Loose", statement: "Four.", area: "storage" });
  const other = entry({ id: "s-eeeeee", title: "Other", statement: "Five.", area: "access" });
  const kill = decision({
    id: "d-aaaaaa",
    changes: [{ entry: "s-cccccc", action: Action.RETIRE }],
    date: at(1),
  });
  const s = snapshotOf([
    area({
      name: "storage",
      title: "Storage",
      intro: "How it keeps data.",
      order: ["s-bbbbbb", "s-aaaaaa", "s-cccccc"],
    }),
    area({ name: "access", title: "Access", intro: "", order: ["s-eeeeee"] }),
    first,
    second,
    gone,
    loose,
    other,
    kill,
  ]);
  const d = derive(s);
  expect(renderSpec(s, d, NONE)).toEqual(
    "# Access\n\n## Other (s-eeeeee)\n\nFive.\n\n# Storage\n\nHow it keeps data.\n\n## Second (s-bbbbbb)\n\nTwo.\n\n## First (s-aaaaaa)\n\nOne.\n\n## Loose (s-dddddd)\n\nFour.\n",
  );
  expect(renderSpec(s, d, NONE, "access")).toEqual("# Access\n\n## Other (s-eeeeee)\n\nFive.\n");
  expect(renderSpec(s, d, NONE, "nowhere")).toEqual("");
});

test("render_spec_entry_without_area_file_and_empty_store", () => {
  const s = snapshotOf([
    entry({ id: "s-aaaaaa", title: "Lone", statement: "Alone.", area: "misc" }),
  ]);
  expect(renderSpec(s, derive(s), NONE)).toEqual("# misc\n\n## Lone (s-aaaaaa)\n\nAlone.\n");
  const empty = snapshotOf([]);
  expect(renderSpec(empty, derive(empty), NONE)).toEqual("");
});

test("render_spec_marks_flagged_failing_and_imported_entries", () => {
  const plain = entry({ id: "s-aaaaaa", title: "Plain", statement: "One." });
  const flagged = entry({ id: "s-bbbbbb", title: "Flagged", statement: "Two." });
  const imported = entry({
    id: "s-cccccc",
    title: "Old",
    statement: "Three.",
    importedFrom: NOTES,
  });
  const change = [{ entry: "s-bbbbbb", action: Action.EDIT }];
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0), changes: change });
  const agent = decision({ id: "d-bbbbbb", date: at(1), changes: change });
  const s = snapshotOf([
    area({ order: ["s-aaaaaa", "s-bbbbbb", "s-cccccc"] }),
    plain,
    flagged,
    imported,
    author,
    agent,
  ]);
  const got = renderSpec(s, derive(s), new Set(["s-aaaaaa"]));
  expect(got).toEqual(
    "# Storage\n\n## Plain (s-aaaaaa \u00b7 fails check)\n\nOne.\n\n## Flagged (s-bbbbbb \u00b7 awaiting the author on d-bbbbbb)\n\nTwo.\n\n## Old (s-cccccc \u00b7 imported)\n\nThree.\n",
  );
});

test("spec_view_gives_areas_with_level_one_entries_in_order", () => {
  const first = entry({ id: "s-aaaaaa", title: "First", statement: "One." });
  const second = entry({ id: "s-bbbbbb", title: "Second", statement: "Two." });
  const other = entry({ id: "s-cccccc", title: "Other", statement: "Three.", area: "access" });
  const s = snapshotOf([
    area({ intro: "How it keeps data.", order: ["s-bbbbbb", "s-aaaaaa"] }),
    area({ name: "access", title: "Access", order: ["s-cccccc"] }),
    first,
    second,
    other,
  ]);
  const d = derive(s);
  const view = specView(s, d, NONE);
  expect(view.map((a) => [a.name, a.title, a.intro])).toEqual([
    ["access", "Access", ""],
    ["storage", "Storage", "How it keeps data."],
  ]);
  expect(view.map((a) => a.entries.map((v) => v.id))).toEqual([
    ["s-cccccc"],
    ["s-bbbbbb", "s-aaaaaa"],
  ]);
  expect(view[1]?.entries[0]?.statement).toEqual("Two.");
  expect(specView(s, d, NONE, "access").map((a) => a.name)).toEqual(["access"]);
  expect(specView(s, d, NONE, "nowhere")).toEqual([]);
});

test("render_spec_escapes_lines_that_start_with_a_hash", () => {
  const held = entry({
    id: "s-aaaaaa",
    title: "Held",
    statement: "One.\n\n## Fake (s-zzzzzz)\n\nUnder it.\n# Also",
  });
  const s = snapshotOf([area({ intro: "# Spoof\nPlain.", order: ["s-aaaaaa"] }), held]);
  expect(renderSpec(s, derive(s), NONE)).toEqual(
    "# Storage\n\n\\# Spoof\nPlain.\n\n## Held (s-aaaaaa)\n\nOne.\n\n\\## Fake (s-zzzzzz)\n\nUnder it.\n\\# Also\n",
  );
});

test("render_spec_escapes_indented_hashes_and_underline_headings", () => {
  const held = entry({
    id: "s-aaaaaa",
    title: "Held",
    statement: "One.\n   ## Fake\nTitle\n===\nOther\n---  \n\n----\nlast",
  });
  const s = snapshotOf([area({ intro: "Intro\n---", order: ["s-aaaaaa"] }), held]);
  expect(renderSpec(s, derive(s), NONE)).toEqual(
    "# Storage\n\nIntro\n\\---\n\n## Held (s-aaaaaa)\n\nOne.\n   \\## Fake\nTitle\n\\===\nOther\n\\---  \n\n\\----\nlast\n",
  );
});

test("render_spec_follows_rank_then_derived_order", () => {
  const s = snapshotOf([
    area({ rank: 0, order: ["s-aaaaaa", "s-bbbbbb"] }),
    area({ name: "access" }),
    entry({ id: "s-aaaaaa", title: "Later", restsOn: ["s-bbbbbb"] }),
    entry({ id: "s-bbbbbb", title: "First" }),
  ]);
  const text = renderSpec(s, derive(s), NONE);
  expect(text.indexOf("# Storage")).toBeLessThan(text.indexOf("## First"));
  expect(text.indexOf("## First")).toBeLessThan(text.indexOf("## Later"));
  expect(specView(s, derive(s), NONE).map((a) => a.name)).toEqual(["storage", "access"]);
});

test("render_spec_lists_cross_area_targets", () => {
  const s = snapshotOf([
    entry({ id: "s-aaaaaa", statement: "Held.", restsOn: ["s-bbbbbb"] }),
    entry({ id: "s-bbbbbb", area: "other" }),
  ]);
  expect(renderSpec(s, derive(s), NONE)).toContain("Held.\nrests on s-bbbbbb (other)");
});

test("spec_view_places_with_depth_under_and_also", () => {
  const s = snapshotOf([
    area({ order: ["s-aaaaaa", "s-bbbbbb", "s-cccccc"] }),
    entry({ id: "s-aaaaaa" }),
    entry({ id: "s-bbbbbb" }),
    entry({ id: "s-cccccc", restsOn: ["s-aaaaaa", "s-bbbbbb"] }),
  ]);
  const view = specView(s, derive(s), NONE)[0];
  const p = view?.placed[2];
  expect([p?.entry.id, p?.depth, p?.under, p?.also, p?.across]).toEqual([
    "s-cccccc",
    1,
    "s-bbbbbb",
    ["s-aaaaaa"],
    [],
  ]);
  expect(view?.entries.map((e) => e.id)).toEqual(["s-aaaaaa", "s-bbbbbb", "s-cccccc"]);
});

test("cross_area_target_is_across_not_also", () => {
  const s = snapshotOf([
    entry({ id: "s-aaaaaa" }),
    entry({ id: "s-bbbbbb", area: "other" }),
    entry({ id: "s-cccccc", restsOn: ["s-bbbbbb", "s-aaaaaa"] }),
  ]);
  const p = specView(s, derive(s), NONE, "storage")[0]?.placed[1];
  expect([p?.under, p?.also, p?.across]).toEqual(["s-aaaaaa", [], [["s-bbbbbb", "other"]]]);
});

test("retired_same_area_target_is_not_also", () => {
  const s = snapshotOf([
    entry({ id: "s-aaaaaa" }),
    entry({ id: "s-bbbbbb" }),
    entry({ id: "s-cccccc", restsOn: ["s-aaaaaa", "s-bbbbbb"] }),
    decision({ changes: [{ entry: "s-bbbbbb", action: Action.RETIRE }] }),
  ]);
  const p = specView(s, derive(s), NONE)[0]?.placed[1];
  expect([p?.under, p?.also]).toEqual(["s-aaaaaa", []]);
});

test("retired_cross_area_target_remains_across", () => {
  const s = snapshotOf([
    entry({ id: "s-aaaaaa", restsOn: ["s-bbbbbb"] }),
    entry({ id: "s-bbbbbb", area: "other" }),
    decision({ changes: [{ entry: "s-bbbbbb", action: Action.RETIRE }] }),
  ]);
  const p = specView(s, derive(s), NONE, "storage")[0]?.placed[0];
  expect(p?.across).toEqual([["s-bbbbbb", "other"]]);
  expect(renderSpec(s, derive(s), NONE)).toContain("rests on s-bbbbbb (other)");
});

test("duplicate_targets_are_shown_once", () => {
  const s = snapshotOf([
    area({ order: ["s-aaaaaa", "s-bbbbbb", "s-cccccc"] }),
    entry({ id: "s-aaaaaa" }),
    entry({ id: "s-bbbbbb" }),
    entry({ id: "s-dddddd", area: "other" }),
    entry({
      id: "s-cccccc",
      restsOn: ["s-aaaaaa", "s-aaaaaa", "s-bbbbbb", "s-dddddd", "s-dddddd"],
    }),
  ]);
  const p = specView(s, derive(s), NONE, "storage")[0]?.placed[2];
  expect(p?.also).toEqual(["s-aaaaaa"]);
  expect(p?.across).toEqual([["s-dddddd", "other"]]);
});
