import { expect, test } from "bun:test";
import { Conflict, coreSettings, LodgeError, NotFound, StaleList } from "#app";

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
