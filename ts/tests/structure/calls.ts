import { existsSync, readdirSync, readFileSync } from "node:fs";
import ts from "typescript";
import { fsImports, guardedCatch, unsafePattern } from "./guards.ts";
import { MAX_LINES, PACKAGES } from "./table.ts";

function files(root: string, folder: string): string[] {
  if (!existsSync(`${root}/${folder}`)) return [];
  return readdirSync(`${root}/${folder}`, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory()
      ? files(root, `${folder}/${e.name}`)
      : e.name.endsWith(".ts")
        ? [`${folder}/${e.name}`]
        : [],
  );
}
const banned = new Set([
  "Intl",
  "performance",
  "crypto",
  "process",
  "Bun",
  "fetch",
  "WebSocket",
  "console",
  "setTimeout",
  "setInterval",
  "queueMicrotask",
  "navigator",
  "globalThis",
  "self",
  "global",
  "window",
  "setImmediate",
  "clearImmediate",
  "prompt",
  "alert",
  "confirm",
]);
const local = new Set([
  "getTimezoneOffset",
  "toLocaleString",
  "toLocaleDateString",
  "toLocaleTimeString",
  "toDateString",
  "toTimeString",
  ...["get", "set"].flatMap((p) =>
    ["FullYear", "Month", "Date", "Day", "Hours", "Minutes", "Seconds", "Milliseconds"].map(
      (s) => p + s,
    ),
  ),
]);
const writes = new Set(
  [
    "createWriteStream",
    "write",
    "writev",
    "link",
    "mkdtemp",
    "writeFile",
    "appendFile",
    "mkdir",
    "rm",
    "rmdir",
    "unlink",
    "rename",
    "copyFile",
    "cp",
    "symlink",
    "truncate",
  ].flatMap((n) => [n, `${n}Sync`]),
);
export function callViolations(root: string): string[] {
  const found: string[] = [];
  for (const path of files(root, "src")) {
    const pkg = path.split("/")[1];
    const pure = pkg === "core" || pkg === "app";
    const source = ts.createSourceFile(
      path,
      readFileSync(`${root}/${path}`, "utf8"),
      ts.ScriptTarget.Latest,
      true,
    );
    const imported = fsImports(source);
    function report(node: ts.Node, message: string): void {
      found.push(
        `${path}:${source.getLineAndCharacterOfPosition(node.getStart(source)).line + 1}: ${message}`,
      );
    }
    function visit(node: ts.Node): void {
      if (pkg === "core" && unsafePattern(node)) report(node, "use portable Unicode patterns");
      if (pure && ts.isMetaProperty(node)) report(node, `${pkg} may not use import.meta`);
      if (pkg === "core" && ts.isCatchClause(node) && !guardedCatch(node))
        report(node, "catch must rethrow other errors");
      if (
        pkg === "core" &&
        ts.isObjectLiteralExpression(node) &&
        path !== "src/core/check-state.ts" &&
        node.properties.some((p) => {
          const name = p.name;
          if (!name) return false;
          if (ts.isComputedPropertyName(name))
            return ts.isStringLiteral(name.expression) && name.expression.text === "ok";
          return (ts.isIdentifier(name) || ts.isStringLiteral(name)) && name.text === "ok";
        })
      )
        report(node, "build check results through checkResult");
      if (ts.isIdentifier(node)) {
        const parent = node.parent;
        const property =
          ((ts.isPropertyAccessExpression(parent) ||
            ts.isPropertyAssignment(parent) ||
            ts.isPropertySignature(parent) ||
            ts.isPropertyDeclaration(parent) ||
            ts.isMethodDeclaration(parent) ||
            ts.isMethodSignature(parent)) &&
            parent.name === node) ||
          (ts.isBindingElement(parent) && parent.propertyName === node);
        const reportedDate =
          ts.isPropertyAccessExpression(parent) &&
          parent.expression === node &&
          parent.getText(source) === "Date.now";
        if (!property && pure && banned.has(node.text))
          report(node, `${pkg} may not use ${node.text}`);
        if (!property && !reportedDate && pkg === "core" && node.text === "Date")
          report(node, "core may not use Date");
        if (!property && ["eval", "Function"].includes(node.text)) report(node, "dynamic code");
      }
      if (ts.isPropertyAccessExpression(node) && pure) {
        const name = node.getText(source);
        if (name === "Date.now" || name === "Math.random")
          report(node, `${pkg} may not use ${name}`);
      }
      if (
        ts.isCallExpression(node) ||
        ts.isNewExpression(node) ||
        ts.isTaggedTemplateExpression(node)
      ) {
        const expr = ts.isTaggedTemplateExpression(node) ? node.tag : node.expression;
        const name = expr.getText(source);
        const attr = ts.isPropertyAccessExpression(expr) ? expr.name.text : name;
        if (expr.kind === ts.SyntaxKind.ImportKeyword || name === "require")
          report(node, "dynamic import");
        if (
          pkg === "app" &&
          name === "Date" &&
          !ts.isTaggedTemplateExpression(node) &&
          (!ts.isNewExpression(node) || node.arguments?.length !== 1)
        )
          report(node, `${pkg} may not use Date`);
        if (pure && ts.isPropertyAccessExpression(expr) && local.has(attr))
          report(node, `${pkg} may not use local time: ${attr}`);
        if (
          pkg === "core" &&
          ts.isPropertyAccessExpression(expr) &&
          name !== "Date.now" &&
          ["now", "today", "utcnow"].includes(attr)
        )
          report(node, `core may not use ${name}`);
        if (pkg !== "git" && ["Bun.spawn", "Bun.spawnSync", "Bun.$"].includes(name))
          report(node, "process spawning outside git");
        if (pkg !== "git" && pkg !== "cli" && name === "Bun.file")
          report(node, "file reading outside git and cli");
        const fsName = imported(expr);
        const flags = ts.isTaggedTemplateExpression(node) ? undefined : node.arguments?.[1];
        const writingOpen =
          ["open", "openSync"].includes(fsName ?? attr) &&
          !!flags &&
          (!ts.isStringLiteralLike(flags) || /[wa+]/u.test(flags.text));
        const bunFileWrite =
          ts.isPropertyAccessExpression(expr) &&
          ts.isCallExpression(expr.expression) &&
          expr.expression.expression.getText(source) === "Bun.file" &&
          ["write", "writer", "delete"].includes(attr);
        if (
          pkg !== "git" &&
          (name === "Bun.write" ||
            (writes.has(fsName ?? attr) &&
              (!["write", "writeSync", "writev", "writevSync"].includes(attr) ||
                fsName !== undefined)) ||
            writingOpen ||
            bunFileWrite)
        )
          report(node, "file writing outside git");
        if (
          (pkg !== "api" && ["Bun.serve", "Bun.listen", "Bun.connect"].includes(name)) ||
          (["store", "git"].includes(pkg ?? "") &&
            (name === "fetch" || (ts.isNewExpression(node) && name === "WebSocket")))
        )
          report(node, "sockets outside api");
      }
      ts.forEachChild(node, visit);
    }
    visit(source);
  }
  return found;
}
export function sizeViolations(root: string): string[] {
  return ["src", "tests", "scripts"]
    .flatMap((dir) => files(root, dir))
    .flatMap((path) => {
      const text = readFileSync(`${root}/${path}`, "utf8");
      const n =
        text === ""
          ? 0
          : text.split(/\r\n|\n|\r/u).length - (text.endsWith("\n") || text.endsWith("\r") ? 1 : 0);
      return n > MAX_LINES ? [`${path}: ${n} lines (limit ${MAX_LINES})`] : [];
    });
}
export function layoutViolations(root: string): string[] {
  const found: string[] = [];
  const packages = existsSync(`${root}/src`)
    ? readdirSync(`${root}/src`, { withFileTypes: true })
        .filter((e) => e.isDirectory())
        .map((e) => e.name)
    : [];
  for (const path of files(root, "src")) {
    if (path.split("/").length === 2 && path !== "src/main.ts")
      found.push(`${path}: unknown package ${path.slice(4, -3)}`);
  }
  for (const pkg of packages) {
    if (!PACKAGES.has(pkg) || pkg === "main") found.push(`src/${pkg}: unknown package ${pkg}`);
    if (!existsSync(`${root}/src/${pkg}/index.ts`)) found.push(`src/${pkg}: missing front door`);
    for (const e of readdirSync(`${root}/src/${pkg}`, { withFileTypes: true }))
      if (e.isDirectory()) found.push(`src/${pkg}/${e.name}: nested folder`);
  }
  const imports = JSON.parse(readFileSync(`${root}/package.json`, "utf8")).imports ?? {};
  const expected = Object.fromEntries(packages.map((pkg) => [`#${pkg}`, `./src/${pkg}/index.ts`]));
  if (
    Object.keys(imports).length !== packages.length ||
    Object.entries(expected).some(([key, value]) => imports[key] !== value)
  )
    found.push("imports does not match the packages");
  return found;
}
