import { afterEach, expect, test } from "bun:test";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { CliError, readDraft, readExact } from "#cli";

const dirs: string[] = [];
afterEach(() => {
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});
function file(text: string | Uint8Array): string {
  const dir = mkdtempSync(join(tmpdir(), "lodge-files-"));
  dirs.push(dir);
  const path = join(dir, "draft");
  writeFileSync(path, text);
  return path;
}
test("draft_line_ends_are_translated", () =>
  expect(readDraft(file("a\r\nb\rc\n"))).toBe("a\nb\nc\n"));
test("draft_keeps_a_byte_order_mark", () =>
  expect(readDraft(file("\ufefftext"))).toBe("\ufefftext"));
test("exact_text_keeps_its_line_ends", () =>
  expect(readExact(file("a\r\nb\rc\n"), "bad text")).toBe("a\r\nb\rc\n"));
test("not_utf8_is_one_sentence", () => {
  const path = file(new Uint8Array([255]));
  expect(() => readDraft(path)).toThrow(CliError);
  expect(() => readDraft(path)).toThrow(`${path}: not UTF-8 text`);
  expect(() => readExact(path, "attachment is not text")).toThrow(
    `${path}: attachment is not text`,
  );
});
test("missing_file_is_one_sentence", () => {
  const path = `${file("")}-missing`;
  expect(() => readDraft(path)).toThrow(CliError);
  expect(() => readDraft(path)).toThrow(`${path}: cannot be read: No such file or directory`);
});
test("cli_error_can_exit_one", () => {
  expect(new CliError("failed", 1).exitCode).toBe(1);
});
