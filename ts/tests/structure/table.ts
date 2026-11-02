export const PACKAGES: ReadonlyMap<string, readonly string[]> = new Map([
  ["core", []],
  ["app", ["core"]],
  ["store", ["app", "core"]],
  ["git", ["app", "core"]],
  ["api", ["app", "core"]],
  ["cli", ["app", "core"]],
  ["hook", ["app", "core"]],
  ["main", ["core", "app", "store", "git", "api", "cli", "hook"]],
]);
export const CORE_NPM: readonly string[] = ["yaml", "@noble/hashes"];
export const MAX_LINES = 300;
