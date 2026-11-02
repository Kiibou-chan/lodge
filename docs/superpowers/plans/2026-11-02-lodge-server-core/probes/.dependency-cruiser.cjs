module.exports = {
  forbidden: [
    { name: "allowed-imports", severity: "error", from: { path: "^src/core/" }, to: { path: "^src/", pathNot: "^src/core/" } },
    { name: "no-cycles", severity: "error", from: {}, to: { circular: true } },
    { name: "front-door", severity: "error", from: { path: "^src/([^/]+)/" }, to: { path: "^src/[^/]+/", pathNot: ["^src/$1/", "^src/[^/]+/index\\.ts$"] } },
    { name: "core-no-node", severity: "error", from: { path: "^src/core/" }, to: { dependencyTypes: ["core"] } },
  ],
  options: { tsConfig: { fileName: "tsconfig.json" }, doNotFollow: { path: "node_modules" } },
};
