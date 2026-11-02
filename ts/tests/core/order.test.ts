import { expect, test } from "bun:test";
import { Action, areaNames, derive, derivedOrder, restsOnTree, writtenOrder } from "#core";
import { area, decision, entry, snapshotOf } from "./builders.ts";

const [A, B, C, D] = ["s-aaaaaa", "s-bbbbbb", "s-cccccc", "s-dddddd"] as const;
test("ranked_areas_first_then_by_name", () => {
  const s = snapshotOf([
    area({ name: "b", rank: 2 }),
    area({ name: "a", rank: 1 }),
    area({ name: "z" }),
    area({ name: "c" }),
  ]);
  expect(areaNames(s)).toEqual(["a", "b", "c", "z"]);
});
test("shared_rank_ordered_by_name", () => {
  expect(
    areaNames(snapshotOf([area({ name: "x", rank: 1 }), area({ name: "w", rank: 1 })])),
  ).toEqual(["w", "x"]);
});
test("folder_without_area_file_sorts_with_unranked", () => {
  expect(
    areaNames(
      snapshotOf([area({ name: "z", rank: 0 }), entry({ area: "a" }), area({ name: "b" })]),
    ),
  ).toEqual(["z", "a", "b"]);
});
test("entry_after_what_it_rests_on", () => {
  const s = snapshotOf([
    area({ order: [A, B, C] }),
    entry({ id: A, restsOn: [C] }),
    entry({ id: B }),
    entry({ id: C }),
  ]);
  expect(derivedOrder(s, derive(s), "storage").map((p) => p.id)).toEqual([B, C, A]);
});
test("no_links_keeps_written_order", () => {
  const s = snapshotOf([
    area({ order: [B, A] }),
    entry({ id: A }),
    entry({ id: B }),
    entry({ id: C }),
  ]);
  expect(writtenOrder(s, derive(s), "storage")).toEqual([B, A, C]);
  expect(derivedOrder(s, derive(s), "storage").map((p) => p.id)).toEqual([B, A, C]);
});
test("under_is_the_target_placed_last", () => {
  const s = snapshotOf([
    area({ order: [A, B, C] }),
    entry({ id: A }),
    entry({ id: B }),
    entry({ id: C, restsOn: [A, B] }),
  ]);
  const got = derivedOrder(s, derive(s), "storage");
  expect(got.map((p) => p.id)).toEqual([A, B, C]);
  expect([got[2]?.under, got[2]?.depth]).toEqual([B, 1]);
});
test("dependant_follows_what_it_rests_on", () => {
  const s = snapshotOf([
    area({ order: [A, B, C] }),
    entry({ id: A }),
    entry({ id: B }),
    entry({ id: C, restsOn: [A] }),
  ]);
  const got = derivedOrder(s, derive(s), "storage");
  expect(got.map((p) => p.id)).toEqual([A, C, B]);
  expect([got[1]?.depth, got[1]?.under, got[2]?.depth]).toEqual([1, A, 0]);
});
test("cycle_falls_back_to_written_order", () => {
  const s = snapshotOf([
    area({ order: [A, B] }),
    entry({ id: A, restsOn: [B] }),
    entry({ id: B, restsOn: [A] }),
  ]);
  expect(derivedOrder(s, derive(s), "storage").map((p) => p.id)).toEqual([A, B]);
});
test("retired_target_does_not_hold_an_entry_back", () => {
  const s = snapshotOf([
    area({ order: [A, C] }),
    entry({ id: A, restsOn: [B] }),
    entry({ id: B }),
    entry({ id: C }),
    decision({ changes: [{ entry: B, action: Action.RETIRE }] }),
  ]);
  const got = derivedOrder(s, derive(s), "storage");
  expect(got.map((p) => p.id)).toEqual([A, C]);
  expect([got[0]?.depth, got[0]?.under]).toEqual([0, null]);
});
test("dependants_follow_depth_first", () => {
  const s = snapshotOf([
    area({ order: [A, B, C, D] }),
    entry({ id: A }),
    entry({ id: B, restsOn: [A] }),
    entry({ id: C, restsOn: [A] }),
    entry({ id: D, restsOn: [B] }),
  ]);
  const got = derivedOrder(s, derive(s), "storage");
  expect(got.map((p) => p.id)).toEqual([A, B, D, C]);
  expect(got.map((p) => [p.depth, p.under])).toEqual([
    [0, null],
    [1, A],
    [2, B],
    [1, A],
  ]);
});
test("diamond_uses_last_placed_target_at_depth_two", () => {
  const s = snapshotOf([
    area({ order: [A, B, C, D] }),
    entry({ id: A }),
    entry({ id: B, restsOn: [A] }),
    entry({ id: C, restsOn: [A] }),
    entry({ id: D, restsOn: [B, C] }),
  ]);
  const got = derivedOrder(s, derive(s), "storage");
  expect(got.map((p) => p.id)).toEqual([A, B, C, D]);
  expect(got.map((p) => [p.depth, p.under])).toEqual([
    [0, null],
    [1, A],
    [1, A],
    [2, C],
  ]);
});
test("rests_on_tree_reaches_the_roots", () => {
  const s = snapshotOf([
    entry({ id: A }),
    entry({ id: B, restsOn: [A] }),
    entry({ id: C, restsOn: [B] }),
  ]);
  const tree = restsOnTree(s, derive(s), C);
  expect(tree[0]?.id).toEqual(B);
  expect(tree[0]?.children[0]?.id).toEqual(A);
  expect(tree[0]?.children[0]?.children).toEqual([]);
  expect(tree[0]?.title).toEqual(s.entries.get(B)?.title);
  expect(tree[0]?.status).toEqual("current");
});
test("rests_on_tree_stops_on_a_cycle", () => {
  const s = snapshotOf([entry({ id: A, restsOn: [B] }), entry({ id: B, restsOn: [A] })]);
  const tree = restsOnTree(s, derive(s), A);
  expect(tree[0]?.id).toEqual(B);
  expect(tree[0]?.children).toEqual([]);
});
