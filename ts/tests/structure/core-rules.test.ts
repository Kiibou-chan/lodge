import { expect, test } from "bun:test";
import { callViolations } from "./calls.ts";
import { plant } from "./plant.ts";

test.each([
  ["try {} catch (e) { return e; }", true],
  ["try {} catch { return; }", true],
  ["try {} catch (e) { if (!(e instanceof ValueError)) throw other; }", true],
  ["try {} catch (e) { if (!(e instanceof ValueError)) throw e; return refuse(e); }", false],
  ["const r = { problems, notes, ok: true }", true],
  ["const r = { problems, notes, ['ok']: true }", true],
  ["const r = checkResult(problems, notes)", false],
])("guard_and_result_construction %p", (code, refused) => {
  expect(callViolations(plant({ "src/core/apply.ts": code })).length > 0).toBe(refused);
});
test.each([
  ["src/api/a.ts", "try {} catch (e) { return answer(e); }"],
  ["src/cli/a.ts", "const r = { ok: true }"],
  ["src/app/a.ts", "/a\\s/"],
])("core_only_rules_leave_adapters_alone %p", (path, code) => {
  expect(callViolations(plant({ [path]: code }))).toEqual([]);
});
test("result_constructor_may_build_ok", () => {
  expect(
    callViolations(plant({ "src/core/check-state.ts": "const r = { problems, notes, ok: true }" })),
  ).toEqual([]);
});

test.each([
  ["/a/", true],
  ["/a/mu", true],
  [String.raw`/a\s/u`, true],
  [String.raw`/\w\d\b/u`, true],
  [String.raw`/\S\W\D\B/u`, true],
  [String.raw`/\D/u`, true],
  ["new RegExp(`a$" + "{x}`)", true],
  ["new RegExp(`a$" + '{x}`, "u")', false],
  ['new RegExp("a")', true],
  ['new RegExp("a", "um")', true],
  [String.raw`new RegExp("\\s", "u")`, true],
  ["/a/u", false],
  ['new RegExp("a", "u")', false],
  [String.raw`/\\s/u`, false],
])("portable_patterns %p", (code, refused) => {
  expect(callViolations(plant({ "src/core/a.ts": code })).length > 0).toBe(refused);
});

test.each([
  ["xs.sort()", true],
  ["xs.toSorted()", true],
  ["xs.sort(byCodePoint)", false],
  ["xs.toSorted(byCodePoint)", false],
])("explicit_sort_comparator %p", (code, refused) => {
  expect(callViolations(plant({ "src/core/a.ts": code })).length > 0).toBe(refused);
});

test("new_target_is_not_import_meta", () => {
  expect(callViolations(plant({ "src/core/a.ts": "function f() { return new.target; }" }))).toEqual(
    [],
  );
});
