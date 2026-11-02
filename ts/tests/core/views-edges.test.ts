import { expect, test } from "bun:test";
import { Action, derive, level1, level3 } from "#core";
import { decision, entry, snapshotOf } from "./builders.ts";

// TypeScript additions cover the quote trust boundary and repeated changes.
test("agent_quote_is_not_author_evidence", () => {
  const e = entry({ id: "s-aaaaaa" });
  const change = { entry: e.id, action: Action.CREATE };
  const d = decision({
    quote: { text: "Agent words.", where: "a session", when: "then" },
    changes: [change, change],
  });
  const s = snapshotOf([e, d]),
    derived = derive(s);
  expect(level1(s, derived, d.id, new Set()).quote).toBe(null);
  expect(level1(s, derived, e.id, new Set()).quote).toBe(null);
  expect(level3(s, derived, d.id).links).toEqual([["changes (create)", e.id, "current"]]);
});
