import { expect, test } from "bun:test";
import { toWire } from "#api";

test("plain_values_pass", () => {
  for (const v of [null, true, false, "astral 🦉", 42]) expect(toWire(v)).toEqual(v);
});
test("maps_and_sets_are_tagged_in_order", () => {
  expect(
    toWire(
      new Map([
        ["b", 2],
        ["a", 1],
      ]),
    ),
  ).toEqual({
    $map: [
      ["b", 2],
      ["a", 1],
    ],
  });
  expect(toWire(new Set([2, 1]))).toEqual({ $set: [2, 1] });
});
test("nested_values_are_encoded", () => {
  expect(toWire([{ m: new Map([["x", new Set([null])]]) }])).toEqual([
    { m: { $map: [["x", { $set: [null] }]] } },
  ]);
});
test("undefined_properties_are_left_out", () => {
  expect(toWire({ a: undefined, b: 1 })).toEqual({ b: 1 });
});
test.each([1n, () => 1, NaN, Infinity, Symbol("x"), { $map: [] }, { $set: [] }])(
  "unsupported_values_throw %p",
  (v) => {
    expect(() => toWire(v)).toThrow();
  },
);
