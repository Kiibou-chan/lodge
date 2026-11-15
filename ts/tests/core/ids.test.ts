import { expect, test } from "bun:test";
import { isId, mintId, ValueError } from "#core";

test("mint_id", () => {
  expect(mintId("d", new Uint8Array(8))).toBe("d-000000");
  expect(mintId("s", new Uint8Array(8).fill(255))).toBe("s-zzzzzz");
  expect(isId("d-3m8qk2")).toBe(true);
  expect(isId("d-3m8qkI")).toBe(false);
  expect(isId("x-3m8qk2")).toBe(false);
});
test("mint_id_reads_six_bytes_into_the_alphabet", () => {
  expect(mintId("d", new Uint8Array([0, 1, 9, 10, 17, 31]))).toBe("d-019ahz");
});
test("mint_id_needs_six_bytes", () => {
  const f = () => mintId("d", new Uint8Array(5));
  expect(f).toThrow(ValueError);
  expect(f).toThrow(/six/u);
});
test.each(["i", "l", "o", "u"].map((c) => [c]))("excluded_letters_are_not_ids %p", (letter) => {
  expect(isId(`d-00000${letter}`)).toBe(false);
});
test.each(
  ["d-3m8qk", "d-3m8qk22", "d-3M8QK2", "d-3m8qk2\n", " d-3m8qk2", "d3m8qk2"].map((c) => [c]),
)("wrong_shapes_are_not_ids %p", (text) => {
  expect(isId(text)).toBe(false);
});
