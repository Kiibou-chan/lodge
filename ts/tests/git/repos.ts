import { afterEach } from "bun:test";
import { chmodSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { encodeUtf8, strip } from "#core";
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
  return strip(run(args, repo));
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

export function bareRemote(): string {
  const remote = temporaryFolder();
  git(remote, "init", "--bare", "-b", "main");
  return remote;
}
export function clone(remote: string): string {
  const target = temporaryFolder();
  git(target, "clone", remote, ".");
  return target;
}
export function seeded(remote: string): string {
  const repo = clone(remote);
  commit(repo, "README.md", "A made-up project\n", "Start");
  git(repo, "push", "origin", "main");
  return repo;
}
export function worktree(of: string): string {
  const target = temporaryFolder();
  git(of, "worktree", "add", "--detach", target);
  return target;
}
export function riggedRemote(branch: string): { remote: string; mine: string; other: string } {
  const remote = bareRemote();
  const mine = seeded(remote);
  git(mine, "checkout", "--orphan", branch);
  git(mine, "rm", "-rf", ".");
  commit(mine, "lodge/first.md", "First\n", "First");
  git(mine, "push", "origin", branch);
  const before = git(remote, "rev-parse", branch);
  const theirs = clone(remote);
  git(theirs, "checkout", branch);
  commit(theirs, "lodge/other.md", "Other\n", "Other");
  git(theirs, "push", "origin", branch);
  const other = git(remote, "rev-parse", branch);
  git(remote, "update-ref", `refs/heads/${branch}`, before);
  write(
    remote,
    "hooks/pre-receive",
    `#!/bin/sh
[ -e hook-ran ] && exit 0
touch hook-ran
env -u GIT_QUARANTINE_PATH -u GIT_OBJECT_DIRECTORY -u GIT_ALTERNATE_OBJECT_DIRECTORIES git update-ref refs/heads/${branch} ${other}
`,
  );
  chmodSync(join(remote, "hooks/pre-receive"), 0o755);
  return { remote, mine, other };
}
