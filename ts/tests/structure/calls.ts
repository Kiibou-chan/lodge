import { existsSync, readdirSync, readFileSync } from "node:fs";
import ts from "typescript";
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
  "console",
  "setTimeout",
  "setInterval",
  "queueMicrotask",
  "navigator",
  "globalThis",
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
    function report(node: ts.Node, message: string): void {
      found.push(
        `${path}:${source.getLineAndCharacterOfPosition(node.getStart(source)).line + 1}: ${message}`,
      );
    }
    function visit(node: ts.Node): void {
      if (ts.isIdentifier(node)) {
        const property = ts.isPropertyAccessExpression(node.parent) && node.parent.name === node;
        if (!property && pure && banned.has(node.text))
          report(node, `${pkg} may not use ${node.text}`);
        if (!property && pkg === "core" && node.text === "Date")
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
          pure &&
          name === "Date" &&
          !ts.isTaggedTemplateExpression(node) &&
          node.arguments?.length !== 1
        )
          report(node, `${pkg} may not use Date`);
        if (pure && ts.isPropertyAccessExpression(expr) && local.has(attr))
          report(node, `${pkg} may not use local time: ${attr}`);
        if (
          pkg === "core" &&
          ts.isPropertyAccessExpression(expr) &&
          ["now", "today", "utcnow"].includes(attr)
        )
          report(node, `core may not use ${name}`);
        if (pkg !== "git" && ["Bun.spawn", "Bun.spawnSync", "Bun.$"].includes(name))
          report(node, "process spawning outside git");
        if (pkg !== "git" && pkg !== "cli" && name === "Bun.file")
          report(node, "file reading outside git and cli");
        if (pkg !== "git" && (name === "Bun.write" || writes.has(attr)))
          report(node, "file writing outside git");
        if (pkg !== "api" && ["Bun.serve", "Bun.listen", "Bun.connect"].includes(name))
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
