const { PACKAGES, CORE_NPM } = require("./tests/structure/table.ts");
const packages = [...PACKAGES.keys()].filter((name) => name !== "main");

/** @type {import("dependency-cruiser").IConfiguration} */
module.exports = {
  forbidden: [
    {
      name: "front-door",
      severity: "error",
      from: { path: "^src/" },
      to: { path: "^(?:tests|scripts)/" },
    },
    ...packages.map((pkg) => ({
      name: "allowed-imports",
      severity: "error",
      from: { path: `^src/${pkg}/` },
      to: {
        path: `(?:^src/(?:${packages
          .filter((q) => q !== pkg && !PACKAGES.get(pkg).includes(q))
          .join("|")})/|^src/main\\.ts$)`,
      },
    })),
    {
      name: "front-door",
      severity: "error",
      from: { path: "^src/([^/]+)/" },
      to: {
        path: "^src/",
        pathNot: "^src/$1/",
        dependencyTypesNot: ["aliased-subpath-import"],
      },
    },
    {
      name: "front-door",
      severity: "error",
      from: { path: "^(?:tests/|scripts/|src/main\\.ts$)" },
      to: { path: "^src/", dependencyTypesNot: ["aliased-subpath-import"] },
    },
    {
      name: "no-circular",
      severity: "error",
      from: { path: "^(src|tests|scripts)/" },
      to: { circular: true },
    },
    {
      name: "core-imports",
      severity: "error",
      from: { path: "^src/core/" },
      to: { dependencyTypes: ["core"] },
    },
    {
      name: "core-imports",
      severity: "error",
      from: { path: "^src/core/" },
      to: {
        dependencyTypes: ["npm", "npm-dev", "npm-optional", "npm-peer", "npm-no-pkg"],
        pathNot: `^(?:node_modules/)?(?:${CORE_NPM.join("|")})(?:/|$)`,
      },
    },
    {
      name: "app-imports",
      severity: "error",
      from: { path: "^src/app/" },
      to: { dependencyTypes: ["core", "npm", "npm-dev", "npm-optional", "npm-peer", "npm-no-pkg"] },
    },
    {
      name: "process-confinement",
      severity: "error",
      from: { path: "^src/", pathNot: "^src/(?:git)/" },
      to: { path: "^(?:node:)?child_process$" },
    },
    {
      name: "sqlite-confinement",
      severity: "error",
      from: { path: "^src/", pathNot: "^src/(?:store)/" },
      to: { path: "^bun:sqlite$" },
    },
    {
      name: "file-confinement",
      severity: "error",
      from: { path: "^src/", pathNot: "^src/(?:git|cli)/" },
      to: { path: "^(?:node:)?fs(?:/promises)?$" },
    },
    {
      name: "network-confinement",
      severity: "error",
      from: { path: "^src/", pathNot: "^src/(?:api)/" },
      to: { path: "^(?:node:)?(?:net|http|https|tls|dgram)$" },
    },
    {
      name: "not-to-unresolvable",
      severity: "error",
      from: { path: "^(src|tests|scripts)/" },
      to: { couldNotResolve: true },
    },
  ],
  options: {
    tsConfig: { fileName: "tsconfig.json" },
    tsPreCompilationDeps: true,
    preserveSymlinks: true,
    doNotFollow: { path: "node_modules" },
  },
};
