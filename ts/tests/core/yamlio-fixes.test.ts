import { expect, test } from "bun:test";
import { loadYaml, YamlError } from "#core";

function failure(text: string): YamlError {
  try {
    loadYaml(text);
  } catch (error) {
    if (error instanceof YamlError) return error;
    throw error;
  }
  throw new Error("expected YamlError");
}
test("nine_shared_anchor_levels_load_within_one_second", () => {
  const text = [
    "a0: &a0 [x, x]",
    ...Array.from({ length: 8 }, (_, i) => `a${i + 1}: &a${i + 1} [*a${i}, *a${i}]`),
  ].join("\n");
  const start = performance.now();
  const result = loadYaml(text) as Map<string, unknown[]>;
  expect(performance.now() - start).toBeLessThan(1000);
  expect(result.get("a8")?.[0]).toBe(result.get("a7"));
});
test("recursive_alias_shares_its_container", () => {
  const result = loadYaml("a: &x [*x]") as Map<string, unknown[]>;
  expect(result.get("a")?.[0]).toBe(result.get("a"));
});
test("unreadable_character_names_decimal_code_point", () => {
  expect(failure("a: b\nc: \x01\n").message).toBe("unreadable character 1");
});
test("parser_message_has_no_excerpt_or_embedded_line", () => {
  const error = failure("a: b\n  c: d");
  expect(error.message).toBe("Nested mappings are not allowed in compact mappings");
  expect(error.line).toBe(1);
});
test.each([
  ["a: !!int 5\nb: [\n", 3],
  ["a: b\na: c\nd: [\n", 4],
  ["[a]: b\nc: [\n", 3],
])("syntax_precedes_construction %p %p", (text, line) => {
  expect(failure(text as string).line).toBe(line as number);
});
test.each(["*x: y", "a: *x"])("undefined_alias_names_source %p", (text) => {
  expect(failure(text).message).toBe("found undefined alias 'x'");
  expect(failure(text).line).toBe(1);
});
test.each([
  ["tab_after_colon", "scope:\tproduct", new Map([["scope", "product"]])],
  ["tab_only_line", "a: b\n\t\n", new Map([["a", "b"]])],
  ["empty_block_key", ": v", new Map([["", "v"]])],
  ["empty_flow_key", "{: v}", new Map([["", "v"]])],
  [
    "dot_anchor",
    "a: &a.b x\nb: *a.b",
    new Map([
      ["a", "x"],
      ["b", "x"],
    ]),
  ],
  [
    "slash_anchor",
    "a: &a/b x\nb: *a/b",
    new Map([
      ["a", "x"],
      ["b", "x"],
    ]),
  ],
  ["nel_after_colon", "a: \x85b", new Map([["a", "\x85b"]])],
])("parser_difference_reads %p", (_, text, expected) => {
  expect(loadYaml(text as string)).toEqual(expected);
});
test.each([
  ["nel_break", "a: b\x85c: d"],
  ["line_separator", "a: b\u2028c: d"],
  ["paragraph_separator", "a: b\u2029c: d"],
  ["bare_cr", "a: b\rc: d\r"],
  ["quoted_column_zero", 'a: "b\nc"'],
  ["flow_column_zero", "a: [b,\nc]"],
])("parser_difference_refuses %p", (_, text) => {
  expect(() => loadYaml(text)).toThrow(YamlError);
});
