import { expect, test } from "bun:test";
import { derive, renderSpec } from "#core";
import { area, entry, snapshotOf } from "./builders.ts";

test("heading_line_breaks_at_newline_only", () => {
  const statement = "One.\u2028# x\r# x\u2029# x\n# real\n===\r\n---\u2028\n   ## real\n====\n";
  const s = snapshotOf([
    area({ intro: "Intro\u2028# x\r# x\n# real" }),
    entry({ id: "s-aaaaaa", title: "Held", statement }),
  ]);
  expect(renderSpec(s, derive(s), new Set())).toBe(
    "# Storage\n\nIntro\u2028# x\r# x\n\\# real\n\n" +
      "## Held (s-aaaaaa)\n\nOne.\u2028# x\r# x\u2029# x\n\\# real\n===\r\n---\u2028\n   \\## real\n\\====\n\n",
  );
});
