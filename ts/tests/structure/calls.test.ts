import { expect, test } from "bun:test";
import { callViolations } from "./calls.ts";
import { plant } from "./plant.ts";

test.each([
  ["core", "Date.now()"],
  ["core", "new Date()"],
  ["core", "Date()"],
  ["core", "Intl"],
  ["core", "performance"],
  ["core", "Math.random()"],
  ["core", "crypto"],
  ["core", "process"],
  ["core", "Bun"],
  ["core", "fetch"],
  ["core", "console"],
  ["core", "setTimeout"],
  ["core", "setInterval"],
  ["core", "queueMicrotask"],
  ["core", "navigator"],
  ["core", "globalThis"],
  ["app", "Date.now()"],
  ["app", "new Date()"],
  ["app", "Date()"],
  ["app", "Intl"],
  ["app", "performance"],
  ["app", "Math.random()"],
  ["app", "crypto"],
  ["app", "process"],
  ["app", "Bun"],
  ["app", "fetch"],
  ["app", "console"],
  ["app", "setTimeout"],
  ["app", "setInterval"],
  ["app", "queueMicrotask"],
  ["app", "navigator"],
  ["app", "globalThis"],
])("core_disallowed_global %p %p", (pkg, code) => {
  expect(
    callViolations(plant({ [`src/${pkg}/a.ts`]: code })).some((v) => v.includes("may not use")),
  ).toBe(true);
});
test.each([
  ["core", "d.getTimezoneOffset()"],
  ["core", "d.toLocaleString()"],
  ["core", "d.toLocaleDateString()"],
  ["core", "d.toLocaleTimeString()"],
  ["core", "d.toDateString()"],
  ["core", "d.toTimeString()"],
  ["core", "d.getFullYear()"],
  ["core", "d.getMonth()"],
  ["core", "d.getDate()"],
  ["core", "d.getDay()"],
  ["core", "d.getHours()"],
  ["core", "d.getMinutes()"],
  ["core", "d.getSeconds()"],
  ["core", "d.getMilliseconds()"],
  ["core", "d.setFullYear()"],
  ["core", "d.setMonth()"],
  ["core", "d.setDate()"],
  ["core", "d.setDay()"],
  ["core", "d.setHours()"],
  ["core", "d.setMinutes()"],
  ["core", "d.setSeconds()"],
  ["core", "d.setMilliseconds()"],
  ["core", "new Date(2026, 2, 29)"],
  ["app", "d.getTimezoneOffset()"],
  ["app", "d.toLocaleString()"],
  ["app", "d.toLocaleDateString()"],
  ["app", "d.toLocaleTimeString()"],
  ["app", "d.toDateString()"],
  ["app", "d.toTimeString()"],
  ["app", "d.getFullYear()"],
  ["app", "d.getMonth()"],
  ["app", "d.getDate()"],
  ["app", "d.getDay()"],
  ["app", "d.getHours()"],
  ["app", "d.getMinutes()"],
  ["app", "d.getSeconds()"],
  ["app", "d.getMilliseconds()"],
  ["app", "d.setFullYear()"],
  ["app", "d.setMonth()"],
  ["app", "d.setDate()"],
  ["app", "d.setDay()"],
  ["app", "d.setHours()"],
  ["app", "d.setMinutes()"],
  ["app", "d.setSeconds()"],
  ["app", "d.setMilliseconds()"],
  ["app", "new Date(2026, 2, 29)"],
])("local_time_in_core_and_app %p %p", (pkg, code) => {
  expect(
    callViolations(plant({ [`src/${pkg}/a.ts`]: code })).some((v) => v.includes("may not use")),
  ).toBe(true);
});
test.each([
  ["core", 'new Date("2026-10-29T12:00:00+01:00")'],
  ["core", "Date.UTC(2026,9,29)"],
])("core_may_not_use_date %p %p", (pkg, code) => {
  expect(
    callViolations(plant({ [`src/${pkg}/a.ts`]: code })).some((v) =>
      v.includes("core may not use Date"),
    ),
  ).toBe(true);
});
test.each([
  ["core", "d.now()"],
  ["core", "d.today()"],
  ["core", "d.utcnow()"],
])("core_names_the_clock_on_any_receiver %p %p", (pkg, code) => {
  expect(
    callViolations(plant({ [`src/${pkg}/a.ts`]: code })).some((v) =>
      v.includes("core may not use d."),
    ),
  ).toBe(true);
});
test.each([
  ["cli", "eval(x)"],
  ["cli", "new Function(x)"],
  ["cli", "import(x)"],
  ["cli", "require(x)"],
])("dynamic_code_anywhere %p %p", (pkg, code) => {
  expect(
    callViolations(plant({ [`src/${pkg}/a.ts`]: code })).some((v) => v.includes("dynamic")),
  ).toBe(true);
});
test.each([
  ["cli", "Bun.spawn(x)"],
  ["cli", "Bun.spawnSync(x)"],
  ["cli", "Bun.$`x`"],
])("spawn_outside_git %p %p", (pkg, code) => {
  expect(
    callViolations(plant({ [`src/${pkg}/a.ts`]: code })).some((v) =>
      v.includes("process spawning outside git"),
    ),
  ).toBe(true);
});
test.each([["store", "Bun.file(x)"]])("file_reading_outside_git_and_cli %p %p", (pkg, code) => {
  expect(
    callViolations(plant({ [`src/${pkg}/a.ts`]: code })).some((v) =>
      v.includes("file reading outside git and cli"),
    ),
  ).toBe(true);
});
test.each([
  ["cli", "Bun.write(x)"],
  ["cli", "writeFileSync(x)"],
])("file_writing_outside_git %p %p", (pkg, code) => {
  expect(
    callViolations(plant({ [`src/${pkg}/a.ts`]: code })).some((v) =>
      v.includes("file writing outside git"),
    ),
  ).toBe(true);
});
test.each([
  ["cli", "Bun.serve(x)"],
  ["cli", "Bun.listen(x)"],
  ["cli", "Bun.connect(x)"],
])("sockets_outside_api %p %p", (pkg, code) => {
  expect(
    callViolations(plant({ [`src/${pkg}/a.ts`]: code })).some((v) =>
      v.includes("sockets outside api"),
    ),
  ).toBe(true);
});
test("clock_port_call_is_not_a_clock_read", () => {
  expect(callViolations(plant({ "src/app/a.ts": "clock.now()" }))).toEqual([]);
});
test("app_may_parse_a_stamp", () => {
  expect(
    callViolations(
      plant({ "src/app/a.ts": 'new Date("2026-10-29T12:00:00+01:00").getUTCHours()' }),
    ),
  ).toEqual([]);
});
test("confined_calls_are_allowed_where_ruled", () => {
  expect(
    callViolations(
      plant({
        "src/git/a.ts": "Bun.spawn(x); Bun.write(x); writeFileSync(x);",
        "src/cli/a.ts": "Bun.file(x);",
        "src/api/a.ts": "Bun.serve(x);",
      }),
    ),
  ).toEqual([]);
});
