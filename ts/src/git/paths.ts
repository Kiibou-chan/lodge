import { realpathSync, statSync } from "node:fs";
import { dirname, isAbsolute, parse } from "node:path";
import { LodgeError } from "#app";
import { attempt, run } from "./run.ts";

export function resolvePath(path: string): string {
  const absolute = isAbsolute(path) ? path : `${process.cwd()}/${path}`;
  const root = parse(absolute).root;
  let resolved = root;
  for (const part of absolute.slice(root.length).split("/")) {
    if (!part || part === ".") continue;
    if (part === "..") {
      resolved = dirname(resolved);
      continue;
    }
    const next = `${resolved === root ? root : `${resolved}/`}${part}`;
    try {
      resolved = realpathSync(next);
    } catch (error) {
      if (
        !(error instanceof Error) ||
        !("code" in error) ||
        !["ENOENT", "ENOTDIR"].includes(String(error.code))
      )
        throw error;
      resolved = next;
    }
  }
  return resolved;
}
export function isFolder(path: string): boolean {
  try {
    return statSync(path).isDirectory();
  } catch {
    return false;
  }
}
export async function repoRootOf(edited: string): Promise<string> {
  let folder = dirname(resolvePath(edited));
  while (!isFolder(folder)) folder = dirname(folder);
  const args = ["rev-parse", "--show-toplevel"];
  const done = attempt(args, folder);
  if (done.code !== 0) throw new LodgeError(`${folder} is not inside a git repository`);
  return run(args, folder);
}
