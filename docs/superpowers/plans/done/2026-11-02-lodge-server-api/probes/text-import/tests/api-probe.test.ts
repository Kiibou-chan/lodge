import { expect, test } from "bun:test";
import { asset } from "#api";

test("text_imports", () => {
  expect(asset("/")).toContain("<title>lodge</title>");
  expect(asset("/page.js")).toContain("b64");
});
