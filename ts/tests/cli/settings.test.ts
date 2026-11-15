import { afterEach, expect, test } from "bun:test";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { CliError, NO_SERVER, readSettings, repositoryRoot, serverOf, tokenOf } from "#cli";
import { coreSettings } from "#core";

const roots: string[] = [];
afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});
function root(): string {
  const dir = mkdtempSync(join(tmpdir(), "lodge-settings-"));
  roots.push(dir);
  return dir;
}
function settings(text: string) {
  const dir = root();
  writeFileSync(join(dir, ".lodge.toml"), text);
  return readSettings(dir);
}
function refusal(text: string, message: string) {
  expect(() => settings(text)).toThrow(CliError);
  expect(() => settings(text)).toThrow(`.lodge.toml: ${message}`);
}

test.each(["folder", "file"])("root_is_the_nearest_folder_with_git %s", (kind) => {
  const dir = root();
  mkdirSync(join(dir, ".git"));
  const inner = join(dir, "inner");
  mkdirSync(inner);
  if (kind === "folder") mkdirSync(join(inner, ".git"));
  else writeFileSync(join(inner, ".git"), "gitdir: elsewhere");
  const nested = join(inner, "nested");
  mkdirSync(nested);
  expect(repositoryRoot(nested)).toBe(inner);
});
test("outside_a_repository_is_one_sentence", () => {
  const dir = root();
  expect(() => repositoryRoot(dir)).toThrow(`${dir} is not inside a git repository`);
});
test("no_settings_file_has_no_server", () => {
  expect(readSettings(root())).toEqual({ server: null, core: {}, coreSettings: coreSettings() });
});
test.each([
  "[length]\ntitle_chars = 80.0",
  "[length]\ntitle_chars = 8e1",
  "length = {title_chars = 80.0}",
  "length.title_chars = 80.0",
])("whole_number_float_is_refused %s", (text) =>
  refusal(text, "length.title_chars must be a positive whole number"),
);
test.each([
  ["80", 80],
  ["0x50", 80],
  ["+80", 80],
  ["1_000", 1000],
  ["99999999999999999999", 1e20],
] as const)("integer_forms_are_read %s", (text, value) => {
  expect(settings(`[length]\ntitle_chars = ${text}`).coreSettings.length.titleChars).toBe(value);
});
test.each(["inf", "nan", "2026-11-02", "12:00:00"])("inf_and_a_date_are_refused %s", (value) =>
  refusal(`[length]\ntitle_chars = ${value}`, "length.title_chars must be a positive whole number"),
);
test("float_in_sources_is_refused", () =>
  refusal("[import]\nsources = [80.0]", "import.sources must be a list of file names"));
test("unclosed_table_header_is_one_sentence", () => {
  try {
    settings("[store");
    throw new Error("accepted");
  } catch (error) {
    expect(error).toBeInstanceOf(CliError);
    expect((error as Error).message).toMatch(/^\.lodge\.toml: [^\r\n]+$/);
  }
});
test("store_is_an_unknown_section", () =>
  refusal('[store]\nmode = "tree"', "unknown section [store]"));
test.each([
  ["[zebra]\nx=1\n[other]", "unknown section [zebra]"],
  ["other=1\n[zebra]", "unknown key other"],
])("first_unknown_name_in_file_order_is_named %s", (text, message) => refusal(text, message));
test("server_is_read", () => {
  const value = settings('[server]\nurl="https://lodge.example.org/"\nproject="work"');
  expect(serverOf(value)).toEqual({ url: "https://lodge.example.org", project: "work" });
});
test("server_is_needed", () => {
  expect(NO_SERVER).toBe(
    "this repository's .lodge.toml names no lodge server; add [server] with url and project",
  );
  try {
    serverOf({ server: null, core: {}, coreSettings: coreSettings() });
    throw new Error("accepted");
  } catch (error) {
    expect(error).toBeInstanceOf(CliError);
    expect((error as CliError).message).toBe(NO_SERVER);
    expect((error as CliError).exitCode).toBe(2);
  }
});
test.each([
  "http://example.org",
  "https://host/path",
  "https://host?x=1",
  "https://host#x",
  "https://user@host",
  "ftp://host",
  "http://127.0.0.2",
  "bad",
  "https://host?",
  "https://host#",
])("server_url_must_be_https_or_this_machine refused %s", (url) =>
  refusal(
    `[server]\nurl="${url}"\nproject="work"`,
    "server.url must be an https URL, or an http URL on this machine",
  ),
);
test.each([
  "http://localhost:8787",
  "http://127.0.0.1:9",
  "http://[::1]:9",
  "https://lodge.example.org",
])("server_url_must_be_https_or_this_machine accepted %s", (url) => {
  expect(settings(`[server]\nurl="${url}"\nproject="work"`).server?.url).toBe(url);
});
test.each(["A", "-work", "a_b", "a".repeat(64), "", "a\n"])(
  "server_project_is_a_name %s",
  (project) =>
    refusal(
      `[server]\nurl="https://host"\nproject=${JSON.stringify(project)}`,
      "server.project must be lower-case letters, digits, and hyphens",
    ),
);
test.each(["[server]", '[server]\nurl="https://host"', '[server]\nproject="work"'])(
  "server_needs_url_and_project %s",
  (text) => refusal(text, "[server] needs url and project"),
);
test("server_table_and_keys_are_checked", () => {
  refusal("server=1", "server must be a table");
  refusal("[server]\nextra=1", "unknown key server.extra");
});
test("hook_is_left_alone", () => {
  expect(settings("hook=42").core).toEqual({});
});
test("core_table_holds_length_and_import_only", () => {
  expect(
    settings('[length]\ntitle_chars=80\n[import]\nsources=["notes"]\n[hook]\nx=1').core,
  ).toEqual({ length: { title_chars: 80 }, import: { sources: ["notes"] } });
});
test("token_comes_from_the_environment", () => {
  expect(tokenOf({ LODGE_TOKEN: "synthetic-token" })).toBe("synthetic-token");
  expect(tokenOf({})).toBeNull();
  expect(tokenOf({ LODGE_TOKEN: "" })).toBeNull();
});
test("settings_not_utf8_is_one_sentence", () => {
  const dir = root();
  writeFileSync(join(dir, ".lodge.toml"), new Uint8Array([255]));
  expect(() => readSettings(dir)).toThrow(/^\.lodge\.toml: cannot be read: [^\n]+$/);
});
test.each([
  "https://host/a/..",
  "https://host/.",
  "https://@host",
  "https:host",
  " https://host",
  "http://127.1",
])("server_url_rejects_normalised_disallowed_parts %s", (url) =>
  refusal(
    `[server]\nurl="${url}"\nproject="work"`,
    "server.url must be an https URL, or an http URL on this machine",
  ),
);
test("unreadable_settings_is_one_sentence", () => {
  const dir = root();
  mkdirSync(join(dir, ".lodge.toml"));
  expect(() => readSettings(dir)).toThrow(".lodge.toml: cannot be read: Is a directory");
});
test("unknown_names_remain_one_sentence", () => {
  try {
    settings('"bad\\nname"=1');
    throw new Error("accepted");
  } catch (error) {
    expect(error).toBeInstanceOf(CliError);
    expect((error as Error).message).toMatch(/^\.lodge\.toml: [^\r\n]+$/);
  }
});
