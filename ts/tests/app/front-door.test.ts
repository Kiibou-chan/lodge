import { expect, test } from "bun:test";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import ts from "typescript";

const root = resolve(import.meta.dir, "../../..");
const index = resolve(root, "ts/src/app/index.ts");
const program = ts.createProgram([index], {
  module: ts.ModuleKind.Preserve,
  moduleResolution: ts.ModuleResolutionKind.Bundler,
  allowImportingTsExtensions: true,
  noEmit: true,
});
const checker = program.getTypeChecker();
const source = program.getSourceFile(index);
if (!source) throw new Error("app front door not found");
const moduleSymbol = checker.getSymbolAtLocation(source);
if (!moduleSymbol) throw new Error("app front door is not a module");
const exports = checker.getExportsOfModule(moduleSymbol);
const python = readFileSync(resolve(root, "src/lodge/app/__init__.py"), "utf8");
const all = python.match(/__all__\s*=\s*\[([^\]]*)\]/u)?.[1];
if (!all) throw new Error("Python __all__ not found");
const names = [...all.matchAll(/"([A-Za-z_][A-Za-z_0-9]*)"/gu)].map((m) => {
  const snake = m[1];
  if (snake === undefined) throw new Error("Python export name not found");
  return snake.replace(/_([a-z])/gu, (_, c: string) => c.toUpperCase());
});
const expected = new Set(names);
const extras = new Set([
  "parseHookSettings",
  "Accounts",
  "AgentToken",
  "Passkey",
  "ServerSetup",
  "committed",
  "gate",
  "read",
  "listed",
  "added",
  "written",
  "Now",
  "Actor",
  "person",
  "agent",
  "actorText",
  "Role",
  "Projects",
  "PROJECT_NAME",
  "stampOf",
  "minuteOf",
  "Forbidden",
  "HeldDraft",
  "HeldAdd",
  "HeldMessage",
  "Held",
  "Approved",
]);

test("front_door_exports_every_python_name", () => {
  const actual = new Set(exports.map((symbol) => symbol.name));
  expect(names.filter((name) => !actual.has(name))).toEqual([]);
});

test("front_door_exports_nothing_else", () => {
  expect(
    exports.filter((s) => !expected.has(s.name) && !extras.has(s.name)).map((s) => s.name),
  ).toEqual([]);
});
