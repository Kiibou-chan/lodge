import { expect, test } from "bun:test";
import {
  Action,
  AmbiguousRef,
  byCodePoint,
  derive,
  type Filters,
  filters,
  related,
  resolve,
  Scope,
  search,
  searchCounted,
} from "#core";
import { at, decision, entry, snapshotOf } from "./builders.ts";

test("resolve_case_insensitive", () => {
  const a = decision({ id: "d-aaaaaa", code: "ITEM-1" });
  const s = snapshotOf([a, entry({ id: "s-bbbbbb", code: "SPEC-2" })]);
  expect(resolve(s, "D-AAAAAA")).toEqual("d-aaaaaa");
  expect(resolve(s, "item-1")).toEqual("d-aaaaaa");
  expect(resolve(s, "Spec-2")).toEqual("s-bbbbbb");
  expect(resolve(s, "s-bbbbbb")).toEqual("s-bbbbbb");
  expect(resolve(s, "nothing")).toEqual(null);
});

test("resolve_ambiguous_code_raises", () => {
  const s = snapshotOf([
    decision({ id: "d-aaaaaa", code: "ITEM-1" }),
    entry({ id: "s-bbbbbb", code: "ITEM-1" }),
  ]);
  expect(() => resolve(s, "item-1")).toThrow(AmbiguousRef);
  expect(() => resolve(s, "item-1")).toThrow(/d-aaaaaa, s-bbbbbb/u);
});

test("search_title_over_statement", () => {
  const inStatement = decision({
    id: "d-aaaaaa",
    title: "Other",
    statement: "Retry the upload.",
    date: at(5),
  });
  const inTitle = decision({
    id: "d-bbbbbb",
    title: "Retry upload",
    statement: "Nothing.",
    date: at(1),
  });
  const s = snapshotOf([inStatement, inTitle]);
  expect(search(s, derive(s), "retry", filters())).toEqual(["d-bbbbbb", "d-aaaaaa"]);
});

test("search_exact_id_or_code_first_then_ties_newest_first", () => {
  const older = decision({ id: "d-aaaaaa", title: "Cache", date: at(1) });
  const newer = decision({ id: "d-bbbbbb", title: "Cache", date: at(9) });
  const coded = decision({ id: "d-cccccc", title: "Unrelated", code: "ITEM-1", date: at(0) });
  const s = snapshotOf([older, newer, coded]);
  expect(search(s, derive(s), "cache", filters())).toEqual(["d-bbbbbb", "d-aaaaaa"]);
  expect(search(s, derive(s), "item-1 cache", filters())).toEqual(["d-bbbbbb", "d-aaaaaa"]);
  expect(search(s, derive(s), "ITEM-1", filters())).toEqual(["d-cccccc"]);
  expect(search(s, derive(s), "d-AAAAAA", filters())).toEqual(["d-aaaaaa"]);
});

test("search_words_split_on_non_letters_and_limit", () => {
  const ds = [..."abc"].map((c, i) =>
    decision({ id: `d-aaaaa${c}`, title: "Cache-key", date: at(i) }),
  );
  const s = snapshotOf([...ds]);
  expect(search(s, derive(s), "KEY!", filters(), 2)).toEqual(["d-aaaaac", "d-aaaaab"]);
});

test("search_empty_query_lists_what_the_filters_allow", () => {
  const a = decision({ id: "d-aaaaaa", date: at(1) });
  const b = decision({ id: "d-bbbbbb", date: at(2) });
  const s = snapshotOf([a, b]);
  expect(search(s, derive(s), "", filters())).toEqual(["d-bbbbbb", "d-aaaaaa"]);
});

test("search_each_filter", () => {
  const spec = entry({ id: "s-aaaaaa", title: "Cache", area: "storage" });
  const prod = decision({
    id: "d-aaaaaa",
    title: "Cache",
    changes: [{ entry: "s-aaaaaa", action: Action.CREATE }],
  });
  const proc = decision({
    id: "d-bbbbbb",
    title: "Cache",
    scope: Scope.PROCESS,
    decidedBy: "author",
  });
  const s = snapshotOf([spec, prod, proc]);
  const d = derive(s);
  const ids = (kw: Partial<Filters> = {}) => search(s, d, "cache", filters(kw)).sort(byCodePoint);
  expect(ids()).toEqual(["d-aaaaaa", "d-bbbbbb", "s-aaaaaa"]);
  expect(ids({ kind: "spec" })).toEqual(["s-aaaaaa"]);
  expect(ids({ kind: "decision" })).toEqual(["d-aaaaaa", "d-bbbbbb"]);
  expect(ids({ scope: Scope.PROCESS })).toEqual(["d-bbbbbb"]);
  expect(ids({ area: "storage" })).toEqual(["d-aaaaaa", "s-aaaaaa"]);
  expect(ids({ area: "other" })).toEqual([]);
  expect(ids({ decidedBy: "author" })).toEqual(["d-bbbbbb"]);
  expect(ids({ decidedBy: "coordinator" })).toEqual(["d-aaaaaa", "s-aaaaaa"]);
});

test("search_hides_replaced_unless_asked", () => {
  const old = decision({ id: "d-aaaaaa", title: "Cache", date: at(0) });
  const newer = decision({ id: "d-bbbbbb", title: "Cache", date: at(1), replaces: ["d-aaaaaa"] });
  const spec = entry({ id: "s-aaaaaa", title: "Cache" });
  const kill = decision({
    id: "d-cccccc",
    title: "Other",
    date: at(2),
    changes: [{ entry: "s-aaaaaa", action: Action.RETIRE }],
  });
  const s = snapshotOf([old, newer, spec, kill]);
  const d = derive(s);
  expect(search(s, d, "cache", filters())).toEqual(["d-bbbbbb"]);
  expect(search(s, d, "cache", filters({ status: "replaced" }))).toEqual(["d-aaaaaa"]);
  expect(search(s, d, "cache", filters({ status: "retired" }))).toEqual(["s-aaaaaa"]);
  expect(search(s, d, "cache", filters({ status: "any" }))).toEqual([
    "s-aaaaaa",
    "d-bbbbbb",
    "d-aaaaaa",
  ]);
});

test("related_shared_entry_first", () => {
  const spec = entry({ id: "s-aaaaaa" });
  const change = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const held = decision({
    id: "d-aaaaaa",
    title: "Cache the sessions",
    statement: "Hold.",
    changes: change,
  });
  const shares = decision({ id: "d-bbbbbb", title: "Unlike", changes: change, date: at(1) });
  const gone = decision({ id: "d-cccccc", title: "Unlike", changes: change, date: at(2) });
  const words = decision({
    id: "d-dddddd",
    title: "Cache sessions",
    statement: "Hold.",
    date: at(3),
  });
  const weak = decision({ id: "d-eeeeee", title: "Other", statement: "Sessions.", date: at(4) });
  const last = decision({ id: "d-ffffff", title: "Last", replaces: ["d-cccccc"], date: at(5) });
  const s = snapshotOf([spec, held, shares, gone, words, weak, last]);
  const d = derive(s);
  expect(related(s, d, held, 10)).toEqual(["d-bbbbbb", "d-dddddd"]);
  expect(related(s, d, held, 1)).toEqual(["d-bbbbbb"]);
});

test("search_without_words_returns_exact_match_only", () => {
  const a = decision({
    id: "d-aaaaaa",
    title: "Cache",
    statement: "Holds 42 items.",
    code: "ITEM-1",
  });
  const b = decision({ id: "d-bbbbbb", title: "Cache", statement: "Holds few.", date: at(1) });
  const s = snapshotOf([a, b]);
  const d = derive(s);
  expect(search(s, d, "%", filters())).toEqual([]);
  expect(search(s, d, "the of", filters())).toEqual([]);
  expect(search(s, d, "  ", filters())).toEqual(["d-bbbbbb", "d-aaaaaa"]);
  expect(search(s, d, "42", filters())).toEqual(["d-aaaaaa"]);
});

test("search_ties_larger_id_first", () => {
  const [a, b] = [
    decision({ id: "d-aaaaaa", title: "Cache" }),
    decision({ id: "d-bbbbbb", title: "Cache" }),
  ];
  const s = snapshotOf([a, b]);
  expect(search(s, derive(s), "cache", filters())).toEqual(["d-bbbbbb", "d-aaaaaa"]);
  expect(search(s, derive(s), "", filters())).toEqual(["d-bbbbbb", "d-aaaaaa"]);
});

test("search_ignores_function_words", () => {
  const a = decision({ id: "d-aaaaaa", title: "The cache", statement: "It is small." });
  const b = decision({ id: "d-bbbbbb", title: "The queue", statement: "It is long." });
  const s = snapshotOf([a, b]);
  expect(search(s, derive(s), "the cache is", filters())).toEqual(["d-aaaaaa"]);
});

test("related_ignores_function_words_and_numbers", () => {
  const held = decision({
    id: "d-aaaaaa",
    title: "Cache",
    statement: "The cache is small on 2026 10.",
  });
  const other = decision({
    id: "d-bbbbbb",
    title: "Queue",
    statement: "The queue is long on 2026 10.",
  });
  const s = snapshotOf([held, other]);
  expect(related(s, derive(s), held)).toEqual([]);
});

test("search_area_matches_decisions_changing_its_entries", () => {
  const spec = entry({ id: "s-aaaaaa", area: "storage", title: "Other" });
  const change = decision({
    id: "d-aaaaaa",
    title: "Cache",
    changes: [{ entry: "s-aaaaaa", action: Action.CREATE }],
  });
  const plain = decision({ id: "d-bbbbbb", title: "Cache" });
  const s = snapshotOf([spec, change, plain]);
  expect(search(s, derive(s), "cache", filters({ area: "storage" }))).toEqual(["d-aaaaaa"]);
});

test("related_needs_two_shared_words_not_one", () => {
  const draft = decision({
    id: "d-aaaaaa",
    title: "Records name the project they belong to",
    date: at(9),
  });
  const one = [
    decision({ id: "d-bbbbbb", title: "Records", statement: "Kept.", date: at(1) }),
    decision({ id: "d-cccccc", title: "Project", statement: "Kept.", date: at(2) }),
    decision({ id: "d-dddddd", title: "Other", statement: "They belong.", date: at(3) }),
  ];
  const two = decision({
    id: "d-eeeeee",
    title: "Records belong",
    statement: "Kept.",
    date: at(4),
  });
  const s = snapshotOf([draft, ...one, two]);
  expect(related(s, derive(s), draft)).toEqual(["d-eeeeee"]);
});

test("related_ignores_a_word_most_decisions_carry", () => {
  const names = ["alpha", "beta", "gamma", "delta", "epsilon"];
  const common = [..."bcdef"].map((c, i) =>
    decision({
      id: `d-aaaaa${c}`,
      title: `Lodge ${names[i]}`,
      statement: "Records held.",
      date: at(i),
    }),
  );
  const draft = decision({
    id: "d-aaaaaa",
    title: "Lodge zeta",
    statement: "Records held; zeta holds it.",
    date: at(9),
  });
  let s = snapshotOf([draft, ...common]);
  expect(related(s, derive(s), draft)).toEqual([]);
  const twin = decision({ id: "d-aaaaag", title: "Zeta holds", statement: "Held.", date: at(8) });
  s = snapshotOf([draft, twin, ...common]);
  expect(related(s, derive(s), draft)).toEqual(["d-aaaaag"]);
});

test("search_reports_how_many_matched_beyond_the_limit", () => {
  const ds = [..."abcde"].map((c, i) =>
    decision({ id: `d-aaaaa${c}`, title: "Cache", date: at(i) }),
  );
  const s = snapshotOf([...ds]);
  const [ids, total] = searchCounted(s, derive(s), "cache", filters(), 2);
  expect([ids, total]).toEqual([["d-aaaaae", "d-aaaaad"], 5]);
  expect(searchCounted(s, derive(s), "", filters(), 2)[1]).toEqual(5);
});
