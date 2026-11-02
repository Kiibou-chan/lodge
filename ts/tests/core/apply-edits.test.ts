import { expect, test } from "bun:test";
import assert from "node:assert/strict";
import { areaPath, contentHash, newRecordPath, parseArea, parseRecord, Scope } from "#core";
import {
  applied,
  apply,
  areaText,
  isStale,
  present,
  problems,
  specText,
  state,
} from "./applying.ts";
import { at, decision, entry, area as makeArea, snapshotOf } from "./builders.ts";
import { document } from "./samples.ts";

test("decision_reasoning_edit_keeps_date_and_fails_check_5", () => {
  // After the checking lane merges, also assert checkChange reports exactly check 5.
  const old = decision({
    id: "d-aaaaaa",
    title: "Keep transcripts",
    date: at(3),
    scope: Scope.PROCESS,
    statement: "It is kept.",
    reasoning: "one two three four five six",
  });
  const [s, tree] = state(old);
  const base = contentHash(present(tree.files.get(newRecordPath(old))));
  const text = document(
    [
      "id: d-aaaaaa",
      "kind: decision",
      'title: "Keep transcripts"',
      "scope: process",
      "decided_by: coordinator",
      `date: ${at(3)}`,
      `base: ${base}`,
    ],
    "It is kept.\n\n## Reasoning\n\none two three",
  );
  const result = applied(apply(s, tree, text));
  expect([...result.files.keys()]).toEqual([newRecordPath(old)]);
  expect(result.ids).toEqual(["d-aaaaaa"]);
  const written = parseRecord("x", present(result.files.get(newRecordPath(old))));
  assert(written.kind === "decision");
  expect(written.date).toEqual(at(3));
});

test("decision_edit_changing_statement_is_judged_by_the_check", () => {
  // After the checking lane merges, also assert checkChange refuses the written tree.
  const old = decision({
    id: "d-aaaaaa",
    title: "Keep transcripts",
    date: at(3),
    scope: Scope.PROCESS,
  });
  const [s, tree] = state(old);
  const base = contentHash(present(tree.files.get(newRecordPath(old))));
  const text = document(
    [
      "id: d-aaaaaa",
      "kind: decision",
      'title: "Keep transcripts"',
      "scope: process",
      "decided_by: coordinator",
      `date: ${at(3)}`,
      `base: ${base}`,
    ],
    "Changed.",
  );
  const result = applied(apply(s, tree, text));
  const written = parseRecord("x", present(result.files.get(newRecordPath(old))));
  assert(written.kind === "decision");
  expect(written.statement).toBe("Changed.");
});

test("area_edit_needs_current_base_and_keeps_new_entries", () => {
  const old = entry({ id: "s-aaaaaa" });
  const area = makeArea({ order: ["s-aaaaaa"], intro: "Old intro." });
  const [s, tree] = state(old, area);
  const base = contentHash(present(tree.files.get(areaPath("storage"))));
  const stale = problems(apply(s, tree, areaText("name: storage", "base: 0123456789ab")));
  assert(isStale(present(stale[0])));
  const result = applied(
    apply(
      s,
      tree,
      areaText("name: storage", `base: ${base}`, "order: [s-aaaaaa]", { body: "New intro." }),
      specText("id: s-cccccc", "area: storage"),
    ),
  );
  const written = parseArea(
    "lodge/spec/storage/_area.md",
    present(result.files.get(areaPath("storage"))),
  );
  assert(written.kind === "area");
  expect([written.intro, written.order]).toEqual(["New intro.", ["s-aaaaaa", "s-cccccc"]]);
});

test("missing_edit_file_is_stale_and_names_the_missing_file", () => {
  const old = entry({ id: "s-aaaaaa" });
  const snapshot = snapshotOf([old, makeArea()]);
  const [, tree] = state();
  const found = problems(apply(snapshot, tree, specText("id: s-aaaaaa", "base: 0123456789ab")));
  expect(found).toHaveLength(1);
  assert(isStale(present(found[0])));
  expect(found[0]?.message).toContain("differs from (the file is missing), the hash of");
});
