import { ZERO_TWO_STORE } from "../core/zero-two-store.ts";
import { commit, git, repository, write } from "./repos.ts";

export async function zeroTwoRepository(
  layout: "checkout" | "branch",
  extra: ReadonlyMap<string, string> = new Map(),
): Promise<{ repository: string; rev: string; settingsRev: string }> {
  const repo = repository();
  commit(repo, ".lodge.toml", ZERO_TWO_STORE.get(".lodge.toml") as string, "Settings");
  let settingsRev = git(repo, "rev-parse", "HEAD");
  if (layout === "branch") git(repo, "checkout", "--orphan", "lodge");
  if (layout === "branch") git(repo, "rm", "-rf", ".");
  for (const [path, text] of [...ZERO_TWO_STORE, ...extra]) {
    if (path.startsWith("lodge/")) write(repo, path, text);
  }
  git(repo, "add", "--", "lodge");
  git(repo, "commit", "-m", "Made-up store");
  const rev = git(repo, "rev-parse", "HEAD");
  if (layout === "checkout") settingsRev = rev;
  return { repository: repo, rev, settingsRev };
}
