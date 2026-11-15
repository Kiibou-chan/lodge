import { afterEach } from "bun:test";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { encodeUtf8 } from "#core";
import { run } from "#git";

const folders: string[] = [];
afterEach(() => {
  for (const folder of folders.splice(0)) rmSync(folder, { recursive: true, force: true });
});
export function temporaryFolder(): string {
  const folder = mkdtempSync(join(tmpdir(), "lodge-git-test-"));
  folders.push(folder);
  return folder;
}
export function git(repo: string, ...args: string[]): string {
  return run(args, repo).trim();
}
export function repository(): string {
  const repo = temporaryFolder();
  git(repo, "init", "-b", "main");
  return repo;
}
export function write(repo: string, path: string, text: string): void {
  const target = join(repo, path);
  mkdirSync(dirname(target), { recursive: true });
  writeFileSync(target, encodeUtf8(text));
}
export function commit(repo: string, path: string, text: string, message: string): void {
  write(repo, path, text);
  git(repo, "add", "--", path);
  git(repo, "commit", "-m", message);
}
