import { expect, test } from "bun:test";
import { coreSettings, lengthGuidance, parseCoreSettings, SettingsError } from "#core";

function toml(text: string): Record<string, unknown> {
  return Bun.TOML.parse(text) as Record<string, unknown>;
}
function refuses(value: Record<string, unknown>, pattern: RegExp) {
  const f = () => parseCoreSettings(value);
  expect(f).toThrow(SettingsError);
  expect(f).toThrow(pattern);
}
test("settings_defaults_when_empty", () => {
  const s = parseCoreSettings({});
  expect(s).toEqual(coreSettings({ length: lengthGuidance(), importSources: [] }));
  expect(s.length).toEqual({
    titleChars: 100,
    decisionStatementWords: 80,
    specStatementWords: 150,
    reasoningWords: 1000,
  });
});
test("settings_reads_every_key", () => {
  const s = parseCoreSettings(
    toml(
      '[length]\ntitle_chars = 60\ndecision_statement_words = 40\nspec_statement_words = 90\nreasoning_words = 500\n[import]\nsources = ["docs/old.md", "notes.md"]\n',
    ),
  );
  expect(s).toEqual(
    coreSettings({
      length: lengthGuidance({
        titleChars: 60,
        decisionStatementWords: 40,
        specStatementWords: 90,
        reasoningWords: 500,
      }),
      importSources: ["docs/old.md", "notes.md"],
    }),
  );
  expect(s.length.titleChars).toBe(60);
  expect(s.length.decisionStatementWords).toBe(40);
  expect(s.length.specStatementWords).toBe(90);
  expect(s.length.reasoningWords).toBe(500);
  expect(s.importSources).toEqual(["docs/old.md", "notes.md"]);
});
test("settings_keeps_the_defaults_of_keys_left_out", () => {
  expect(parseCoreSettings({ length: { reasoning_words: 300 } }).length).toEqual(
    lengthGuidance({ reasoningWords: 300 }),
  );
});
test("settings_rejects_unknown_key_naming_it", () =>
  refuses(toml("[length]\ntitle = 5\n"), /length\.title/u));
test("settings_rejects_unknown_import_key_and_section", () => {
  refuses({ import: { source: [] } }, /import\.source/u);
  refuses({ lenght: {} }, /\[lenght\]/u);
  refuses({ colour: "red" }, /colour/u);
});
test("settings_leaves_the_tables_of_other_packages_alone", () => {
  expect(parseCoreSettings({ store: { mode: "branch" }, hook: {} })).toEqual(parseCoreSettings({}));
});
test.each([0, -3, true, "80", 1.5].map((c) => [c]))(
  "settings_rejects_a_length_that_is_not_a_positive_integer %p",
  (value) => refuses({ length: { title_chars: value } }, /length\.title_chars/u),
);
test.each(["docs/a.md", [1], [""], 7].map((c) => [c]))(
  "settings_rejects_sources_that_are_not_a_list_of_strings %p",
  (value) => refuses({ import: { sources: value } }, /import\.sources/u),
);
test("settings_rejects_a_section_that_is_not_a_table", () => refuses({ length: 5 }, /length/u));
