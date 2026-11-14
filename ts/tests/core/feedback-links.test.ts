import { expect, test } from "bun:test";
import { derive, feedback, lengthGuidance } from "#core";
import { area, entry, snapshotOf } from "./builders.ts";

function notes(statement: string, restsOn: readonly string[] = []): string[] {
  const a = entry({ id: "s-aaaaaa", statement: statement, restsOn: restsOn });
  const b = entry({ id: "s-bbbbbb" });
  const s = snapshotOf([area(), a, b]);
  return feedback([a], s, derive(s), lengthGuidance()).map((f) => f.message);
}
test("statement_naming_an_unlisted_entry_asks", () => {
  expect(notes("s-bbbbbb and s-bbbbbb, s-cccccc.")).toEqual([
    "the statement names s-bbbbbb, but rests_on does not list it; does s-aaaaaa rest on s-bbbbbb? If so, add it to rests_on",
  ]);
});
test("listed_named_entry_no_feedback", () => {
  expect(notes("s-bbbbbb", ["s-bbbbbb"])).toEqual([]);
});
test("own_id_no_feedback", () => {
  expect(notes("s-aaaaaa")).toEqual([]);
});
