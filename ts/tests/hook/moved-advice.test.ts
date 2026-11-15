import { afterEach, beforeEach, expect, test } from "bun:test";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { respond } from "#hook";
import { context, payload, resolve, reversal, text } from "./support.ts";

let root: string;
beforeEach(() => {
  root = mkdtempSync(`${tmpdir()}/lodge-moved-`);
});
afterEach(() => {
  rmSync(root, { recursive: true, force: true });
});
const server = "https://lodge.example.test";
function advice(path: string, branch = false) {
  return respond(
    payload(path),
    context(root, branch ? null : `${root}/lodge`, ["docs/*.md"], server),
    resolve,
  );
}
test("moved_record_edit_names_the_server", () => {
  const value = text(advice("lodge/decisions/d-abc123-slug.md"));
  expect(value).toContain(server);
  expect(value.indexOf("lodge draft")).toBeGreaterThanOrEqual(0);
  expect(value.indexOf("lodge draft")).toBeLessThan(value.indexOf("lodge add --dry-run"));
  expect(value.indexOf("lodge add --dry-run")).toBeLessThan(value.indexOf("lodge add FILE"));
  expect(value).not.toContain("do not edit it by hand");
  expect(value).not.toContain("as a draft outside");
});
test("moved_thread_edit_names_reply_and_close", () => {
  const value = text(advice("lodge/threads/q-111111.md"));
  expect(value).toContain(server);
  expect(value).toContain("`lodge reply Q --by ROLE FILE`");
  expect(value).toContain("`lodge close Q --by ROLE`");
  expect(value).not.toContain("lodge draft");
});
test("moved_frozen_edit_names_the_server", () => {
  const value = text(advice("docs/choices.md"));
  expect(value).toContain(server);
  expect(value).toContain("`lodge guide`");
  expect(value).toContain("If the author asked for this edit");
});
test("moved_project_protects_lodge_in_branch_mode", () => {
  expect(text(advice("lodge/decisions/d-abc123-slug.md", true))).toContain(server);
});
test("moved_attachment_edit_gets_nothing", () => {
  for (const branch of [false, true])
    expect(advice("lodge/attachments/d-abc123/notes.md", branch)).toBeNull();
});
test("moved_advice_reverses_the_edit_without_git", () => {
  for (const path of [
    "lodge/decisions/d-abc123-slug.md",
    "lodge/threads/q-111111.md",
    "docs/choices.md",
  ])
    reversal(text(advice(path)));
});
