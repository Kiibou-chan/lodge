import { afterEach, expect, test } from "bun:test";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { hookContextFor } from "#cli";

const roots: string[] = [];
afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});
function fixture(settings?: string | Uint8Array) {
  const root = mkdtempSync(join(tmpdir(), "lodge-hook-context-"));
  roots.push(root);
  if (settings !== undefined) writeFileSync(join(root, ".lodge.toml"), settings);
  const asked: string[] = [];
  const folders = new Set([join(root, "lodge/decisions"), join(root, "lodge/spec")]);
  const git = {
    repoRootOf: async (edited: string) => {
      asked.push(edited);
      return root;
    },
    isFolder: (path: string) => folders.has(path),
  };
  return { root, asked, folders, git };
}
test("hook_context_defaults_and_edited_path", async () => {
  const f = fixture();
  expect(await hookContextFor("/synthetic/new/deep/file.md", f.git)).toEqual({
    repoRoot: f.root,
    dataRoot: join(f.root, "lodge"),
    frozen: [],
    server: null,
  });
  expect(f.asked).toEqual(["/synthetic/new/deep/file.md"]);
});
test.each(["decisions", "spec"])("checkout_needs_both_record_folders %s", async (name) => {
  const f = fixture();
  f.folders.delete(join(f.root, "lodge", name));
  expect(await hookContextFor("file.md", f.git)).toBeNull();
});
test("branch_context_has_no_data_root_and_allows_other_sections", async () => {
  const f = fixture('[store]\nmode="branch"\n[hook]\nfrozen=["docs/*.md"]\n[other]\nx=1');
  f.folders.clear();
  expect(await hookContextFor("file.md", f.git)).toEqual({
    repoRoot: f.root,
    dataRoot: null,
    frozen: ["docs/*.md"],
    server: null,
  });
});
test.each(["checkout", "branch"])("moved_context_needs_no_record_folders %s", async (mode) => {
  const f = fixture(`[store]\nmode="${mode}"\n[server]\nurl="https://lodge.test"`);
  f.folders.clear();
  expect(await hookContextFor("file.md", f.git)).toEqual({
    repoRoot: f.root,
    dataRoot: mode === "checkout" ? join(f.root, "lodge") : null,
    frozen: [],
    server: "https://lodge.test",
  });
});
test.each([
  "[store",
  "store=3.0",
  "hook=3.0",
  "[store]\nmode=3.0",
  "store=3",
  '[store]\nmode="other"',
  "[store]\nmode=3",
  "server=3",
  "[server]",
  "[server]\nurl=3",
  "[server]\nurl=2026-11-02",
  "hook=3",
  "[hook]\nfrozne=[]",
  "[hook]\nfrozen=3",
  new Uint8Array([255]),
  Buffer.concat([Buffer.from("# "), Buffer.from([255]), Buffer.from("\n[hook]\nfrozen=[]\n")]),
])("malformed_hook_context_is_null %p", async (settings) => {
  const f = fixture(settings);
  expect(await hookContextFor("file.md", f.git)).toBeNull();
});
test("context_silences_repository_folder_and_read_errors", async () => {
  const f = fixture();
  expect(
    await hookContextFor("file.md", {
      ...f.git,
      repoRootOf: async () => {
        throw new Error("missing");
      },
    }),
  ).toBeNull();
  expect(
    await hookContextFor("file.md", {
      ...f.git,
      isFolder: () => {
        throw new Error("closed");
      },
    }),
  ).toBeNull();
  mkdirSync(join(f.root, ".lodge.toml"));
  expect(await hookContextFor("file.md", f.git)).toBeNull();
});
