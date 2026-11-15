import { LodgeError } from "#app";
import { decodeUtf8 } from "#core";
import { resolveRev, runBytes } from "./run.ts";

interface StoreRead {
  readonly rev: string;
  readonly files: ReadonlyMap<string, string>;
  readonly settings: string | null;
}
interface Entry {
  readonly path: string;
  readonly type: string;
  readonly sha: string;
}
function listing(repository: string, commit: string, path: string): Entry[] {
  const raw = runBytes(["ls-tree", "-r", "-z", "--full-tree", commit, "--", path], repository);
  return decodeUtf8(raw)
    .split("\0")
    .filter(Boolean)
    .map((item) => {
      const tab = item.indexOf("\t");
      const [, type, sha] = item.slice(0, tab).split(" ");
      return { path: item.slice(tab + 1), type: type as string, sha: sha as string };
    });
}
function contents(repository: string, shas: readonly string[]): ReadonlyMap<string, string> {
  const found = new Map<string, string>();
  if (!shas.length) return found;
  const out = runBytes(["cat-file", "--batch"], repository, undefined, `${shas.join("\n")}\n`);
  let position = 0;
  for (const sha of shas) {
    const end = out.indexOf(10, position);
    const header = decodeUtf8(out.subarray(position, end)).split(" ");
    if (end < 0 || header.length !== 3 || header[1] !== "blob")
      throw new LodgeError(`git cannot read the file ${sha}`);
    const start = end + 1;
    const size = Number(header[2]);
    found.set(sha, decodeUtf8(out.subarray(start, start + size)));
    position = start + size + 1;
  }
  return found;
}
export async function readStore(
  repository: string,
  rev: string,
  settingsRev = rev,
): Promise<StoreRead> {
  const commit = resolveRev(repository, rev);
  if (commit === null) throw new LodgeError(`${rev} is not a commit in ${repository}`);
  const settingsCommit = resolveRev(repository, settingsRev);
  if (settingsCommit === null)
    throw new LodgeError(`${settingsRev} is not a commit in ${repository}`);
  const entries = listing(repository, commit, "lodge").filter((item) =>
    item.path.startsWith("lodge/"),
  );
  if (!entries.length)
    throw new LodgeError(`${rev} holds no lodge/ folder, so it is not a lodge 0.2 store`);
  const settings = listing(repository, settingsCommit, ".lodge.toml").find(
    (item) => item.path === ".lodge.toml" && item.type === "blob",
  );
  const shas = new Set(entries.filter((item) => item.type === "blob").map((item) => item.sha));
  if (settings) shas.add(settings.sha);
  const texts = contents(repository, [...shas]);
  return {
    rev: commit,
    files: new Map(
      entries.map((item) => [
        item.path,
        item.type === "blob" ? (texts.get(item.sha) as string) : "",
      ]),
    ),
    settings: settings ? (texts.get(settings.sha) as string) : null,
  };
}
