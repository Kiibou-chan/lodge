import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { parse, TomlDate } from "smol-toml";
import { LodgeError, parseHookSettings } from "#app";
import { type CoreSettings, parseCoreSettings, SettingsError } from "#core";
import { CliError } from "./errors.ts";
import { readExact } from "./files.ts";

export interface ServerPlace {
  readonly url: string;
  readonly project: string;
}
export interface ProjectSettings {
  readonly server: ServerPlace | null;
  readonly core: Readonly<Record<string, unknown>>;
  readonly coreSettings: CoreSettings;
}
export const NO_SERVER =
  "this repository's .lodge.toml names no lodge server; add [server] with url and project";
export function repositoryRoot(cwd: string): string {
  let current = cwd;
  while (true) {
    if (existsSync(join(current, ".git"))) return current;
    const parent = dirname(current);
    if (parent === current) throw new CliError(`${cwd} is not inside a git repository`);
    current = parent;
  }
}
export function table(value: unknown): value is Record<string, unknown> {
  return (
    value !== null && typeof value === "object" && !Array.isArray(value) && !(value instanceof Date)
  );
}
function convert(value: unknown): unknown {
  if (typeof value === "bigint") return Number(value);
  if (typeof value === "number" || value instanceof TomlDate || value instanceof Date) return null;
  if (Array.isArray(value)) return value.map(convert);
  if (table(value))
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, convert(item)]));
  return value;
}
function serverPlace(value: unknown): ServerPlace {
  if (!table(value)) throw new CliError(".lodge.toml: server must be a table");
  for (const key of Object.keys(value))
    if (key !== "url" && key !== "project")
      throw new CliError(`.lodge.toml: unknown key server.${key}`);
  if (!Object.hasOwn(value, "url") || !Object.hasOwn(value, "project"))
    throw new CliError(".lodge.toml: [server] needs url and project");
  const { url, project } = value;
  const badUrl = () =>
    new CliError(".lodge.toml: server.url must be an https URL, or an http URL on this machine");
  if (typeof url !== "string" || !/^https?:\/\/[^/\s@?#]+\/?$/u.test(url)) throw badUrl();
  let parsed: URL;
  try {
    parsed = new URL(url);
  } catch {
    throw badUrl();
  }
  if (
    !(
      parsed.protocol === "https:" ||
      (parsed.protocol === "http:" && ["localhost", "127.0.0.1", "[::1]"].includes(parsed.hostname))
    ) ||
    (parsed.protocol === "http:" &&
      !/^http:\/\/(?:localhost|127\.0\.0\.1|\[::1\])(?::[0-9]+)?\/?$/u.test(url)) ||
    parsed.username ||
    parsed.password ||
    parsed.pathname !== "/" ||
    url.includes("?") ||
    url.includes("#")
  )
    throw badUrl();
  if (typeof project !== "string" || !/^[a-z0-9][a-z0-9-]{0,62}$/u.test(project))
    throw new CliError(
      ".lodge.toml: server.project must be lower-case letters, digits, and hyphens",
    );
  return { url: url.replace(/\/$/u, ""), project };
}
export function readSettings(root: string): ProjectSettings {
  try {
    return loadSettings(root);
  } catch (error) {
    if (!(error instanceof CliError)) throw error;
    throw new CliError(error.message.replace(/[\r\n]+/gu, " "));
  }
}
function loadSettings(root: string): ProjectSettings {
  const path = join(root, ".lodge.toml");
  let parsed: Readonly<Record<string, unknown>> = {};
  if (existsSync(path)) {
    let text: string;
    try {
      text = readExact(path, "cannot be read: not UTF-8 text");
    } catch (error) {
      if (!(error instanceof CliError)) throw error;
      throw new CliError(error.message.replace(`${path}:`, ".lodge.toml:"));
    }
    parsed = tomlTable(text);
  }
  const core: Record<string, unknown> = {};
  for (const [name, value] of Object.entries(parsed)) {
    if (!["server", "hook", "length", "import"].includes(name))
      throw new CliError(
        `.lodge.toml: ${table(value) ? `unknown section [${name}]` : `unknown key ${name}`}`,
      );
    if (name === "length" || name === "import") core[name] = value;
  }
  const server = Object.hasOwn(parsed, "server") ? serverPlace(parsed["server"]) : null;
  try {
    parseHookSettings(Object.hasOwn(parsed, "hook") ? parsed["hook"] : {});
    return { server, core, coreSettings: parseCoreSettings(core) };
  } catch (error) {
    if (error instanceof LodgeError) throw new CliError(error.message);
    if (!(error instanceof SettingsError)) throw error;
    throw new CliError(`.lodge.toml: ${error.message}`);
  }
}
export function serverOf(settings: ProjectSettings): ServerPlace {
  if (settings.server === null) throw new CliError(NO_SERVER);
  return settings.server;
}
export function tokenOf(env: Readonly<Record<string, string | undefined>>): string | null {
  return env["LODGE_TOKEN"] || null;
}

export function tomlTable(text: string): Readonly<Record<string, unknown>> {
  try {
    const parsed = parse(text, { integersAsBigInt: true });
    return Object.fromEntries(
      Object.entries(parsed).map(([name, value]) => [name, convert(value)]),
    );
  } catch (error) {
    throw new CliError(
      `.lodge.toml: ${String(error instanceof Error ? error.message : error).split(/[\r\n]/u)[0]}`,
    );
  }
}
