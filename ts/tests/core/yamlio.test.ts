import { expect, test } from "bun:test";
import { loadYaml, YamlError } from "#core";

function bad(text: string, pattern?: RegExp, line?: number | null) {
  try {
    loadYaml(text);
    throw new Error("accepted YAML");
  } catch (e) {
    expect(e).toBeInstanceOf(YamlError);
    if (!(e instanceof YamlError)) throw e;
    if (pattern) expect(e.message).toMatch(pattern);
    if (line !== undefined) expect(e.line).toBe(line);
  }
}
test.each(
  ["yes", "no", "on", "~", "null", "14:14", "2026-10-29", "1234", "0x10", "1.5", "true"].map(
    (c) => [c],
  ),
)("yaml_scalars_stay_strings %p", (scalar) => {
  expect(loadYaml(`key: ${scalar}\n`)).toEqual(new Map([["key", scalar]]));
  expect(loadYaml(`[${scalar}, b]`)).toEqual([scalar, "b"]);
});
test("empty_value_is_an_empty_string", () =>
  expect(loadYaml("key:\n")).toEqual(new Map([["key", ""]])));
test("nested_flow_and_block_collections_load", () =>
  expect(loadYaml("a: {b: c}\nd:\n  - {e: f}\n  - g\n")).toEqual(
    new Map<string, unknown>([
      ["a", new Map([["b", "c"]])],
      ["d", [new Map([["e", "f"]]), "g"]],
    ]),
  ));
test.each(["key: !!int 5\n", "key: !!set {a}\n", "key: !!python/name:os.system\n"].map((c) => [c]))(
  "explicit_tags_beyond_text_are_refused %p",
  (text) => bad(text, /tag/u),
);
test("bad_yaml_carries_the_line", () => bad("a: b\nc: d: e\n", undefined, 2));
test("duplicate_key_is_an_error_naming_it", () =>
  bad("title: a\nscope: b\ntitle: c\n", /'title'/u, 3));
test("unreadable_character_carries_the_line", () => bad("a: b\nc: \x01\n", undefined, 2));
test("two_documents_are_an_error", () => bad("a: b\n---\nc: d\n"));
test("deep_nesting_is_an_error_not_a_crash", () =>
  bad(`a: ${"[".repeat(5000)}${"]".repeat(5000)}`, /nested/u));
test("surrogate_pair_escapes_join_into_one_character", () => {
  expect(loadYaml('a: "Ship it \\ud83d\\ude00"')).toEqual(new Map([["a", "Ship it 😀"]]));
  expect(loadYaml('["\\ud83d\\ude00"]')).toEqual(["😀"]);
  expect(loadYaml('"\\ud83d\\ude00": b')).toEqual(new Map([["😀", "b"]]));
});
test("lone_surrogate_escape_stays_lone", () => {
  expect(loadYaml('a: "\\ud83d"')).toEqual(new Map([["a", "\ud83d"]]));
  expect(loadYaml('a: "\\ude00\\ud83d"')).toEqual(new Map([["a", "\ude00\ud83d"]]));
});
test.each(["[title]: x", "{a: b}: c", "? [a, b]\n: c"].map((c) => [c]))(
  "collection_key_is_refused %p",
  (text) => bad(text, /found unhashable key/u, 1),
);
test("integer_like_keys_keep_their_order", () => {
  const value = loadYaml("zz: a\n1: b\n");
  expect(value).toBeInstanceOf(Map);
  if (value instanceof Map) expect([...value.keys()]).toEqual(["zz", "1"]);
});
test("non_specific_tag_is_text", () => expect(loadYaml("a: ! b\n")).toEqual(new Map([["a", "b"]])));
test("str_tag_on_a_mapping_is_refused", () => bad("!!str {a: b}", /tag/u));
test("nesting_beyond_the_bound_has_no_line", () =>
  bad("[".repeat(101) + "]".repeat(101), /^the header is nested too deeply$/u, null));

test("aliases_resolve_to_text_collections", () => {
  expect(loadYaml("a: &value [yes, no]\nb: *value\n")).toEqual(
    new Map([
      ["a", ["yes", "no"]],
      ["b", ["yes", "no"]],
    ]),
  );
});

test("one_hundred_collection_levels_are_allowed", () => {
  const value = loadYaml(`${"[".repeat(100)}leaf${"]".repeat(100)}`);
  let leaf = value;
  for (let i = 0; i < 100; i++) {
    expect(Array.isArray(leaf)).toBe(true);
    if (!Array.isArray(leaf)) throw new Error("missing sequence");
    leaf = leaf[0];
  }
  expect(leaf).toBe("leaf");
});

test("scalar_alias_keys_are_allowed", () => {
  expect(loadYaml("a: &key foo\n*key: bar\n")).toEqual(
    new Map([
      ["a", "foo"],
      ["foo", "bar"],
    ]),
  );
  expect(loadYaml('a: "*key:"\n')).toEqual(new Map([["a", "*key:"]]));
  expect(loadYaml("a: |\n  *key:\n")).toEqual(new Map([["a", "*key:\n"]]));
  expect(loadYaml("a: &key foo\n*key : bar\n")).toEqual(
    new Map([
      ["a", "foo"],
      ["foo", "bar"],
    ]),
  );
});
