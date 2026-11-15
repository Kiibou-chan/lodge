import { expect, test } from "bun:test";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { hookProject } from "./repository.ts";

const BRANCH = '[store]\nmode = "branch"\n';
function fire(project: ReturnType<typeof hookProject>, path: string) {
  return project.run(
    ["hook", "post-tool-use"],
    JSON.stringify({
      tool_name: "Write",
      tool_input: { file_path: path },
    }),
  );
}
function text(out: string): string {
  return JSON.parse(out).hookSpecificOutput.additionalContext;
}
test("hook_names_the_write_path_after_a_hand_edit_of_a_record", async () => {
  const p = hookProject();
  p.initialise();
  const { code, out, err } = await fire(p, join(p.root, "lodge/decisions/d-abc123-slug.md"));
  expect([code, err]).toEqual([0, ""]);
  expect(text(out)).toContain("lodge/decisions/d-abc123-slug.md");
  expect(text(out)).toContain("lodge draft");
});
test("hook_finds_the_repository_of_the_edited_file_not_of_the_session", async () => {
  const p = hookProject();
  p.initialise();
  p.git("commit", "-m", "Store");
  const sibling = join(p.root, "sibling");
  p.git("worktree", "add", "-q", "-b", "sibling", sibling);
  const { code, out, err } = await fire(p, join(sibling, "lodge/decisions/d-abc123-slug.md"));
  expect([code, err]).toEqual([0, ""]);
  expect(text(out)).toContain("lodge/decisions/d-abc123-slug.md");
});
test("hook_finds_the_repository_for_a_file_that_does_not_exist_yet", async () => {
  const p = hookProject();
  p.initialise();
  expect(
    (await fire(p, join(p.root, "lodge/decisions/new/deeper/d-abc123-slug.md"))).out,
  ).toContain("lodge draft");
});
test("hook_stays_silent_where_lodge_is_not_initialised", async () => {
  const p = hookProject();
  mkdirSync(join(p.root, "lodge"));
  const path = join(p.root, "lodge/__init__.py");
  writeFileSync(path, "");
  expect(await fire(p, path)).toEqual({ code: 0, out: "", err: "" });
});
test("hook_stays_silent_for_a_file_that_is_not_lodges", async () => {
  const p = hookProject();
  expect(await fire(p, join(p.root, "README.md"))).toEqual({ code: 0, out: "", err: "" });
});
test("hook_reads_the_frozen_globs_from_the_settings", async () => {
  const p = hookProject();
  p.initialise();
  p.configure('[hook]\nfrozen = ["docs/choices.md"]\n');
  const { code, out } = await fire(p, join(p.root, "docs/choices.md"));
  expect(code).toBe(0);
  expect(text(out)).toContain("docs/choices.md is frozen");
});
test("hook_in_branch_mode_protects_frozen_files_only", async () => {
  const p = hookProject();
  p.configure(BRANCH + '[hook]\nfrozen = ["docs/choices.md"]\n');
  expect(await fire(p, join(p.root, "lodge/decisions/d-abc123-slug.md"))).toEqual({
    code: 0,
    out: "",
    err: "",
  });
  expect((await fire(p, join(p.root, "docs/choices.md"))).out).toContain("is frozen");
});
test.each(["[hook]\nfrozne = []\n", "[hook]\nfrozen = 3\n", "hook = 3\n"])(
  "unknown_hook_setting_is_one_sentence_for_commands_and_silent_for_the_hook %s",
  async (settings) => {
    const p = hookProject();
    p.configure(settings);
    for (const argv of [["init"], ["search", "x"]]) {
      const r = await p.run(argv);
      expect([r.code, r.out]).toEqual([2, ""]);
      expect(r.err.startsWith("lodge: .lodge.toml: ")).toBe(true);
      expect(r.err.split("\n").length - 1).toBe(1);
    }
    expect(await fire(p, join(p.root, "docs/choices.md"))).toEqual({ code: 0, out: "", err: "" });
  },
);
test("unknown_hook_key_is_named", async () => {
  const p = hookProject();
  p.configure("[hook]\nfrozne = []\n");
  expect((await p.run(["search", "x"])).err).toBe("lodge: .lodge.toml: unknown key hook.frozne\n");
});
test.each(["", BRANCH])(
  "hook_gives_the_moved_advice_for_a_project_on_the_server %s",
  async (store) => {
    const p = hookProject();
    p.configure(store + '[server]\nurl = "https://lodge.test"\n');
    const r = await fire(p, join(p.root, "lodge/decisions/d-abc123-slug.md"));
    expect([r.code, r.err]).toEqual([0, ""]);
    expect(text(r.out)).toContain("https://lodge.test");
    expect(text(r.out)).toContain("lodge draft");
  },
);
