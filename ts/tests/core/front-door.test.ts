import { expect, test } from "bun:test";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import ts from "typescript";

const root = resolve(import.meta.dir, "../../..");
const index = resolve(root, "ts/src/core/index.ts");
const program = ts.createProgram([index], {
  module: ts.ModuleKind.Preserve,
  moduleResolution: ts.ModuleResolutionKind.Bundler,
  allowImportingTsExtensions: true,
  noEmit: true,
});
const checker = program.getTypeChecker();
const source = program.getSourceFile(index);
if (!source) throw new Error("core front door not found");
const moduleSymbol = checker.getSymbolAtLocation(source);
if (!moduleSymbol) throw new Error("core front door is not a module");
const exports = checker.getExportsOfModule(moduleSymbol);
const python = readFileSync(resolve(root, "src/lodge/core/__init__.py"), "utf8");
const all = python.match(/__all__\s*=\s*\[([^\]]*)\]/u)?.[1];
if (!all) throw new Error("Python __all__ not found");
const names = [...all.matchAll(/"([A-Za-z_][A-Za-z_0-9]*)"/gu)].map((m) =>
  m[1] === m[1]?.toUpperCase()
    ? m[1]
    : m[1]?.replace(/_([a-z])/gu, (_, c: string) => c.toUpperCase()),
);
const expected = new Set(names);
const constructors = new Map([
  ["decision", "Decision"],
  ["specEntry", "SpecEntry"],
  ["area", "Area"],
  ["problem", "Problem"],
  ["message", "Message"],
  ["coreSettings", "CoreSettings"],
  ["lengthGuidance", "LengthGuidance"],
  ["tree", "Tree"],
  ["filters", "Filters"],
  ["checkResult", "CheckResult"],
]);
function declarations(symbol: ts.Symbol): readonly ts.Declaration[] {
  const target = symbol.flags & ts.SymbolFlags.Alias ? checker.getAliasedSymbol(symbol) : symbol;
  return target.getDeclarations() ?? [];
}
function isAllowedExtra(symbol: ts.Symbol): boolean {
  const definitions = declarations(symbol);
  if (
    definitions.some((d) =>
      ["errors.ts", "text.ts", "stamps.ts"].some(
        (file) => d.getSourceFile().fileName === resolve(root, "ts/src/core", file),
      ),
    )
  )
    return true;
  const typeName = constructors.get(symbol.name);
  const type = exports.find((s) => s.name === typeName && expected.has(s.name));
  return (
    type !== undefined &&
    definitions.some(
      (d) =>
        ts.isFunctionDeclaration(d) &&
        declarations(type).some(
          (t) => ts.isInterfaceDeclaration(t) && t.getSourceFile() === d.getSourceFile(),
        ),
    )
  );
}

test("front_door_exports_every_python_name", () => {
  const actual = new Set(exports.map((symbol) => symbol.name));
  expect(names.filter((name) => !actual.has(name ?? ""))).toEqual([]);
});

test("front_door_exports_nothing_else", () => {
  expect(
    exports.filter((s) => !expected.has(s.name) && !isAllowedExtra(s)).map((s) => s.name),
  ).toEqual([]);
});
