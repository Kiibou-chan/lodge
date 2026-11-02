import { expect, test } from "bun:test";
import { Action, contentHash, newRecordPath } from "#core";
import { applied, apply, decisionText, present, problems, specText, state } from "./applying.ts";
import { area, at, decision, entry } from "./builders.ts";

// TypeScript addition for Python's uncovered provenance heading comparison.
test("changing_only_import_heading_is_refused", () => {
  const old = entry({ id: "s-aaaaaa", importedFrom: { file: "notes.md", heading: "Old" } });
  const [s, tree] = state(old, area());
  const base = contentHash(present(tree.files.get(newRecordPath(old))));
  expect(
    problems(
      apply(
        s,
        tree,
        specText("id: s-aaaaaa", `base: ${base}`, "imported_from: {file: notes.md, heading: New}"),
      ),
    )[0]?.message,
  ).toBe("this draft changes imported_from of s-aaaaaa; keep it as lodge draft printed it");
});
test("replacing_one_of_two_retirements_does_not_restore_order", () => {
  const e = entry({ id: "s-aaaaaa" });
  const changes = [{ entry: e.id, action: Action.RETIRE }];
  const first = decision({ id: "d-aaaaaa", date: at(0), changes });
  const second = decision({ id: "d-bbbbbb", date: at(1), changes });
  const [s, tree] = state(e, area(), first, second);
  const result = applied(
    apply(s, tree, decisionText("replaces: [d-aaaaaa]"), { ids: ["d-cccccc"] }),
  );
  expect([...result.files.keys()]).toEqual(["lodge/decisions/d-cccccc-keep-transcripts.md"]);
});
