import { expect, test } from "bun:test";
import { CliError, tomlTable, zeroTwoCoreTable } from "#cli";
import { parseCoreSettings } from "#core";

test("core_tables_are_kept", () => {
  expect(
    zeroTwoCoreTable('[length]\ntitle_chars = 80\n[import]\nsources = ["docs/choices.md"]'),
  ).toEqual({ length: { title_chars: 80 }, import: { sources: ["docs/choices.md"] } });
});
test("store_and_hook_are_ignored", () => {
  expect(zeroTwoCoreTable('[store]\nmode = "branch"\n[hook]\non = true\nextra = 1')).toEqual({});
});
test("whole_number_float_is_refused_as_the_command_refuses_it", () => {
  expect(() => parseCoreSettings(zeroTwoCoreTable("[length]\ntitle_chars = 80.0"))).toThrow(
    "length.title_chars must be a positive whole number",
  );
});
test("not_utf8_is_one_sentence", () => {
  expect(() => zeroTwoCoreTable("# \uDCFF")).toThrow(
    new CliError(".lodge.toml: cannot be read: not UTF-8"),
  );
});
test("not_toml_is_one_sentence", () => {
  expect(() => zeroTwoCoreTable("[broken")).toThrow(/^\.lodge\.toml: [^\r\n]+$/u);
});

test("toml_table_converts_every_top_level_value", () => {
  expect(
    tomlTable(
      "count = 80\nratio = 80.0\ninfinity = inf\nmissing = nan\nday = 2026-11-02\ntime = 18:56:28\nitems = [1, 2.0]\n[other]\ncount = 3\nratio = 4.0",
    ),
  ).toEqual({
    count: 80,
    ratio: null,
    infinity: null,
    missing: null,
    day: null,
    time: null,
    items: [1, null],
    other: { count: 3, ratio: null },
  });
});
