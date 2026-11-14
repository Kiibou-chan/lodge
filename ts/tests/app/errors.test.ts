import { expect, test } from "bun:test";
import { Conflict, coreSettings, LodgeError, NotFound, StaleList } from "#app";
import { parseCoreSettings, SettingsError } from "#core";

test("exit_codes_follow_lodge_0_2", () => {
  for (const [ErrorClass, code] of [
    [LodgeError, 2],
    [NotFound, 2],
    [Conflict, 1],
    [StaleList, 1],
  ] as const) {
    const error = new ErrorClass("problem");
    expect(error.exitCode).toBe(code);
    expect(error).toBeInstanceOf(LodgeError);
    expect(error).toBeInstanceOf(Error);
    expect(error.name).toBe(ErrorClass.name);
  }
  expect(new StaleList("problem")).toBeInstanceOf(Conflict);
});
test("core_settings_reports_a_bad_table_as_a_lodge_error", () => {
  expect(() => coreSettings({ length: { title_chars: -1 } })).toThrow(LodgeError);
  expect(() => coreSettings({ length: { title_chars: -1 } })).toThrow(/^\.lodge\.toml: /u);
});

test("settings_error_preserves_the_full_message_and_cause", () => {
  const table = { length: { title_chars: -1 } };
  let original: SettingsError | undefined;
  try {
    parseCoreSettings(table);
  } catch (error) {
    if (!(error instanceof SettingsError)) throw error;
    original = error;
  }
  expect(original).toBeInstanceOf(SettingsError);
  if (original === undefined) throw new Error("expected SettingsError");
  try {
    coreSettings(table);
  } catch (error) {
    if (!(error instanceof LodgeError)) throw error;
    expect(error.message).toBe(`.lodge.toml: ${original?.message}`);
    expect(error.cause).toBeInstanceOf(SettingsError);
    expect((error.cause as SettingsError).message).toBe(original?.message);
    return;
  }
  throw new Error("expected LodgeError");
});
