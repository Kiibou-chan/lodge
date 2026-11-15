import { afterEach, beforeEach, expect, test } from "bun:test";
import { mkdirSync, mkdtempSync, rmSync, symlinkSync } from "node:fs";
import { tmpdir } from "node:os";
import { LodgeError, parseHookSettings } from "#app";
import { type HookContext, respond, run } from "#hook";
import { context, drive, payload, resolve, reversal, text } from "./support.ts";

let root: string;
beforeEach(() => {
  root = mkdtempSync(`${tmpdir()}/lodge-hook-`);
});
afterEach(() => {
  rmSync(root, { recursive: true, force: true });
});
const record = "lodge/decisions/d-abc123-slug.md";

test("record_edit_gets_feedback", () => {
  for (const tool of ["Edit", "Write", "MultiEdit"]) {
    const value = text(respond(payload(`${root}/${record}`, tool), context(root), resolve));
    expect(value).toContain(record);
    expect(value.indexOf("lodge draft")).toBeGreaterThanOrEqual(0);
    expect(value.indexOf("lodge draft")).toBeLessThan(value.indexOf("lodge add --dry-run"));
    expect(value.indexOf("lodge add --dry-run")).toBeLessThan(
      value.lastIndexOf("`lodge add FILE`"),
    );
  }
});
test("relative_record_path_is_read_from_the_repository_root", () => {
  expect(text(respond(payload("lodge/spec/area/_area.md"), context(root), resolve))).toContain(
    "lodge/spec/area/_area.md",
  );
});
test("dotted_path_still_counts_as_a_record", () => {
  expect(respond(payload(`${root}/docs/../${record}`), context(root), resolve)).not.toBeNull();
});
test("attachment_edit_gets_nothing", () => {
  expect(
    respond(payload(`${root}/lodge/attachments/d-abc123/notes.md`), context(root), resolve),
  ).toBeNull();
});
test("frozen_edit_gets_feedback", () => {
  const found = context(root, null, ["docs/choices.md", "docs/verdicts/**/*.md"]);
  for (const name of ["docs/choices.md", "docs/verdicts/2026/q4/one.md", "docs/verdicts/two.md"]) {
    const value = text(respond(payload(`${root}/${name}`), found, resolve));
    expect(value).toContain(name);
    expect(value).toContain("lodge add --dry-run");
    expect(value).not.toContain("lodge draft");
    expect(value).toContain("If the author asked for this edit, tell her the file is frozen");
  }
});
test("frozen_globs_do_not_overreach", () => {
  for (const name of ["docs/deep/one.md", "docs/one.txt", "other/notes/choices.md", "docs"])
    expect(
      respond(
        payload(`${root}/${name}`),
        context(root, null, ["docs/*.md", "notes/choices.md"]),
        resolve,
      ),
    ).toBeNull();
});
test("branch_mode_protects_only_frozen_files", () => {
  expect(respond(payload(`${root}/${record}`), context(root, null), resolve)).toBeNull();
});
test("other_edit_gets_nothing", () => {
  expect(
    respond(payload(`${root}/src/main.py`), context(root, undefined, ["docs/*.md"]), resolve),
  ).toBeNull();
  expect(respond(payload(`${root}/../${record}`), context(root), resolve)).toBeNull();
  for (const tool of ["Read", "Bash"])
    expect(respond(payload(`${root}/${record}`, tool), context(root), resolve)).toBeNull();
});
test("symlinked_checkout_still_matches", () => {
  mkdirSync(`${root}/real/lodge/decisions`, { recursive: true });
  symlinkSync(`${root}/real`, `${root}/link`);
  expect(
    respond(payload(`${root}/link/${record}`), context(`${root}/real`), resolve),
  ).not.toBeNull();
});
test.each([
  "",
  "not json",
  "[]",
  "null",
  '"Edit"',
  "{}",
  '{"tool_name":"Edit"}',
  '{"tool_name":"Edit","tool_input":[]}',
  '{"tool_name":"Edit","tool_input":{"file_path":3}}',
  '{"tool_name":"Edit","tool_input":{"file_path":""}}',
  '{"tool_name":3,"tool_input":{"file_path":"x"}}',
])("bad_payload_exit_0_silent %s", async (raw) => {
  expect(await drive(raw, async () => context(root, undefined, ["x"]))).toEqual([0, ""]);
});
test("unreadable_input_exit_0_silent", async () => {
  let output = "";
  expect(
    await run(
      async () => {
        throw new Error("closed");
      },
      (value) => {
        output += value;
      },
      async () => context(root),
      resolve,
      null,
    ),
  ).toBe(0);
  expect(output).toBe("");
});
test("context_failure_exit_0_silent", async () => {
  const raw = JSON.stringify(payload(`${root}/${record}`));
  expect(
    await drive(raw, async () => {
      throw new LodgeError("not a repository");
    }),
  ).toEqual([0, ""]);
  expect(await drive(raw, async () => null)).toEqual([0, ""]);
});
test("run_writes_one_json_line_for_a_record_edit", async () => {
  const [code, output] = await drive(JSON.stringify(payload(`${root}/${record}`)), async () =>
    context(root),
  );
  expect(code).toBe(0);
  expect(output.endsWith("\n")).toBe(true);
  expect(output.split("\n").length - 1).toBe(1);
  expect(text(JSON.parse(output))).toContain("lodge draft");
});
test("run_stays_silent_for_an_unwatched_file", async () => {
  expect(
    await drive(JSON.stringify(payload(`${root}/src/main.py`)), async () => context(root)),
  ).toEqual([0, ""]);
});
test("settings_default_to_no_frozen_files", () => {
  expect(parseHookSettings({})).toEqual([]);
});
test("settings_read_the_frozen_globs", () => {
  expect(parseHookSettings({ frozen: ["a.md", "b/**"] })).toEqual(["a.md", "b/**"]);
});
test.each([
  [{ frozne: [] }, ".lodge.toml: unknown key hook.frozne"],
  [{ frozen: "a.md" }, ".lodge.toml: hook.frozen must be a list of strings"],
  [{ frozen: ["a.md", 3] }, ".lodge.toml: hook.frozen must be a list of strings"],
])("bad_settings_are_one_sentence %j", (table, message) => {
  try {
    parseHookSettings(table);
    throw new Error("accepted invalid settings");
  } catch (error) {
    expect(error).toBeInstanceOf(LodgeError);
    expect((error as Error).message).toBe(message);
  }
});
test("a_hook_section_that_is_not_a_table_is_an_error", () => {
  expect(() => parseHookSettings([])).toThrow(LodgeError);
  expect(() => parseHookSettings([])).toThrow("hook must be a table");
});
test("record_advice_reverses_the_edit_without_git", () => {
  for (const value of [
    text(respond(payload(`${root}/${record}`), context(root), resolve)),
    text(
      respond(
        payload(`${root}/docs/choices.md`),
        context(root, null, ["docs/choices.md"]),
        resolve,
      ),
    ),
  ])
    reversal(value);
});
test("frozen_advice_names_the_guide", () => {
  expect(
    text(respond(payload("docs/choices.md"), context(root, null, ["docs/*.md"]), resolve)),
  ).toContain("`lodge guide`");
});
test("context_is_asked_about_the_edited_file", async () => {
  const asked: string[] = [];
  const finder = async (path: string): Promise<HookContext | null> => {
    asked.push(path);
    return null;
  };
  const absolute = `${root}/${record}`;
  expect(await drive(JSON.stringify(payload(absolute)), finder)).toEqual([0, ""]);
  expect(
    await drive(JSON.stringify({ ...payload("lodge/decisions/d.md"), cwd: root }), finder),
  ).toEqual([0, ""]);
  expect(asked).toEqual([absolute, `${root}/lodge/decisions/d.md`]);
});
test("relative_path_is_read_from_the_payload_working_folder", () => {
  expect(
    respond(
      { ...payload("lodge/decisions/d.md"), cwd: `${root}/sibling` },
      context(root, `${root}/sibling/lodge`),
      resolve,
    ),
  ).not.toBeNull();
});
test("relative_path_without_a_payload_folder_is_read_from_the_process_folder", async () => {
  const asked: string[] = [];
  let output = "";
  expect(
    await run(
      async () => JSON.stringify(payload("lodge/decisions/d.md")),
      (value) => {
        output += value;
      },
      async (path) => {
        asked.push(path);
        return context(root, `${root}/sub/lodge`);
      },
      resolve,
      `${root}/sub`,
    ),
  ).toBe(0);
  expect(asked).toEqual([`${root}/sub/lodge/decisions/d.md`]);
  expect(output).toContain("sub/lodge/decisions/d.md");
});
test("thread_file_edit_names_reply_and_close", () => {
  const value = text(respond(payload("lodge/threads/q-111111.md"), context(root), resolve));
  expect(value).toContain("is a lodge thread file");
  expect(value).toContain("`lodge reply Q --by ROLE FILE`");
  expect(value).toContain("`lodge close Q --by ROLE`");
  expect(value).not.toContain("lodge draft");
  expect(value).toContain("Reverse your own edit now:");
});
