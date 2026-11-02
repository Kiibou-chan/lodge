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
  ["core", "new WebSocket(x)"],
  ["core", "console"],
  ["core", "setTimeout"],
  ["core", "setInterval"],
  ["core", "queueMicrotask"],
  ["core", "navigator"],
  ["core", "globalThis"],
  ["app", "Date.now()"],
  ["app", "new Date()"],
  ["app", "Date()"],
  ["app", 'Date("x")'],
  ["core", 'Date("x")'],
  ["app", "Intl"],
  ["app", "performance"],
  ["app", "Math.random()"],
  ["app", "crypto"],
  ["app", "process"],
  ["app", "Bun"],
  ["app", "fetch"],
  ["app", "new WebSocket(x)"],
  ["app", "console"],
  ["app", "setTimeout"],
  ["app", "setInterval"],
  ["app", "queueMicrotask"],
  ["app", "navigator"],
  ["app", "globalThis"],
])("core_disallowed_global %p %p", (pkg, code) => {
  const name = code.replace(/\(.*$/u, "").replace(/^new /u, "");
  expect(callViolations(plant({ [`src/${pkg}/a.ts`]: code }))).toEqual([
    `src/${pkg}/a.ts:1: ${pkg} may not use ${name}`,
  ]);
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
  const message = code.startsWith("new Date")
    ? `${pkg} may not use Date`
    : `${pkg} may not use local time: ${code.slice(2, -2)}`;
  expect(callViolations(plant({ [`src/${pkg}/a.ts`]: code }))).toEqual([
    `src/${pkg}/a.ts:1: ${message}`,
  ]);
});
test.each([
  ["core", 'new Date("2026-10-29T12:00:00+01:00")'],
  ["core", "Date.UTC(2026,9,29)"],
])("core_may_not_use_date %p %p", (pkg, code) => {
  expect(callViolations(plant({ [`src/${pkg}/a.ts`]: code }))).toEqual([
    `src/${pkg}/a.ts:1: core may not use Date`,
  ]);
});
test.each([
  ["core", "d.now()"],
  ["core", "d.today()"],
  ["core", "d.utcnow()"],
])("core_names_the_clock_on_any_receiver %p %p", (pkg, code) => {
  expect(callViolations(plant({ [`src/${pkg}/a.ts`]: code }))).toEqual([
    `src/${pkg}/a.ts:1: core may not use ${code.slice(0, -2)}`,
  ]);
});
test.each([
  ["cli", "eval(x)"],
  ["cli", "new Function(x)"],
  ["cli", "import(x)"],
  ["cli", "require(x)"],
])("dynamic_code_anywhere %p %p", (pkg, code) => {
  const message =
    code.startsWith("import") || code.startsWith("require") ? "dynamic import" : "dynamic code";
  expect(callViolations(plant({ [`src/${pkg}/a.ts`]: code }))).toEqual([
    `src/${pkg}/a.ts:1: ${message}`,
  ]);
});
test.each([
  ["cli", "Bun.spawn(x)"],
  ["cli", "Bun.spawnSync(x)"],
  ["cli", "Bun.$`x`"],
])("spawn_outside_git %p %p", (pkg, code) => {
  expect(callViolations(plant({ [`src/${pkg}/a.ts`]: code }))).toEqual([
    `src/${pkg}/a.ts:1: process spawning outside git`,
  ]);
});
test.each([["store", "Bun.file(x)"]])("file_reading_outside_git_and_cli %p %p", (pkg, code) => {
  expect(callViolations(plant({ [`src/${pkg}/a.ts`]: code }))).toEqual([
    `src/${pkg}/a.ts:1: file reading outside git and cli`,
  ]);
});
test.each([
  ["cli", "Bun.write(x)"],
  ["cli", "writeFileSync(x)"],
  ["cli", 'createWriteStream("p")'],
  ["cli", "write(x)"],
  ["cli", "writeSync(x)"],
  ["cli", "writev(x)"],
  ["cli", "writevSync(x)"],
  ["cli", "link(x)"],
  ["cli", "linkSync(x)"],
  ["cli", "mkdtemp(x)"],
  ["cli", "mkdtempSync(x)"],
  ["cli", 'open("p")'],
  ["cli", 'openSync("p", flags)'],
  ["cli", 'fs.promises.open("p", "w")'],
  ["cli", 'openSync("p", "a")'],
  ["cli", 'openSync("p", "r+")'],
  ["cli", 'Bun.file("p").write("x")'],
  ["cli", 'Bun.file("p").writer()'],
  ["cli", 'Bun.file("p").delete()'],
])("file_writing_outside_git %p %p", (pkg, code) => {
  expect(callViolations(plant({ [`src/${pkg}/a.ts`]: code }))).toEqual([
    `src/${pkg}/a.ts:1: file writing outside git`,
  ]);
});
test.each([
  ["cli", "Bun.serve(x)"],
  ["cli", "Bun.listen(x)"],
  ["cli", "Bun.connect(x)"],
  ["store", "fetch(x)"],
  ["git", "new WebSocket(x)"],
  ["git", "fetch(x)"],
  ["store", "new WebSocket(x)"],
])("sockets_outside_api %p %p", (pkg, code) => {
  expect(callViolations(plant({ [`src/${pkg}/a.ts`]: code }))).toEqual([
    `src/${pkg}/a.ts:1: sockets outside api`,
  ]);
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
        "src/git/a.ts": `Bun.spawn(x); Bun.write(x); writeFileSync(x);
          createWriteStream(x); write(x); writeSync(x); writev(x); writevSync(x);
          link(x); linkSync(x); mkdtemp(x); mkdtempSync(x); open(x); openSync(x, flags);
          fs.promises.open(x, "w"); Bun.file(x).write(x); Bun.file(x).writer();
          Bun.file(x).delete();`,
        "src/cli/a.ts": 'Bun.file(x); openSync("p", "r"); fetch(x); new WebSocket(x);',
        "src/hook/a.ts": "fetch(x); new WebSocket(x);",
        "src/api/a.ts": "Bun.serve(x); fetch(x); new WebSocket(x);",
      }),
    ),
  ).toEqual([]);
});

test.each(["core", "app"])("property_names_are_not_globals %p", (pkg) => {
  const code = `const o = { process: 1, console: 2 };
    interface I { readonly fetch: string; crypto(): void }
    class C { process = 1; console() {} }
    const { navigator: n } = o;`;
  expect(callViolations(plant({ [`src/${pkg}/a.ts`]: code }))).toEqual([]);
});
