import { expect, test } from "bun:test";
import { parse } from "#cli";
import cases from "./argparse-fix-cases.json";

// Captured from lodge 0.2 argparse on Python 3.13.5 with COLUMNS=80.
for (const { argv, expected } of cases) {
  test(`argparse parity: ${argv.join(" ")}`, () => {
    expect(parse(argv, "0.2.0")).toEqual({ ...expected, kind: "exit" });
  });
}

test("double dash before command", () => {
  expect(parse(["--", "show", "d"], "0.2.0")).toEqual({
    kind: "show",
    ref: "d",
    reasoning: false,
    provenance: false,
  });
});
