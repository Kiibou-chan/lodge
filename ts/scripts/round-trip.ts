import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  type Clock,
  coreSettings,
  exportFiles,
  exportMessage,
  importStore,
  person,
  type ZeroTwoCopy,
} from "#app";
import { zeroTwoCoreTable } from "#cli";
import { exportStore, readStore, run } from "#git";
import { openDatabase, SqliteProjects } from "#store";

function mappedText(path: string, text: string, owner: string): string {
  if (path.startsWith("lodge/decisions/") && text.startsWith("---\n")) {
    const end = text.indexOf("\n---\n", 4);
    if (end !== -1)
      return (
        text.slice(0, end).replace(/^decided_by: author$/gmu, `decided_by: ${owner}`) +
        text.slice(end)
      );
  }
  if (path.startsWith("lodge/threads/"))
    return text.replace(/^(## Message [0-9]+\n\n)by: author$/gmu, `$1by: ${owner}`);
  return text;
}

export function compareStores(
  original: ReadonlyMap<string, string>,
  exported: ReadonlyMap<string, string>,
  owner: string,
) {
  const paths = [...new Set([...original.keys(), ...exported.keys()])].sort();
  let equal = 0;
  let mapped = 0;
  const differences: { path: string; line: number }[] = [];
  for (const path of paths) {
    const before = original.get(path);
    const after = exported.get(path);
    if (before === undefined || after === undefined) {
      differences.push({ path, line: 1 });
      continue;
    }
    if (before === after) {
      equal++;
      continue;
    }
    const expected = mappedText(path, before, owner);
    if (expected === after) {
      mapped++;
      continue;
    }
    const left = expected.split("\n");
    const right = after.split("\n");
    let line = 0;
    while (line < Math.max(left.length, right.length) && left[line] === right[line]) line++;
    differences.push({ path, line: line + 1 });
  }
  return { compared: paths.length, equal, mapped, differences };
}

async function roundTrip(repository: string, rev: string, settingsRev?: string): Promise<number> {
  const clock: Clock = {
    now: () => {
      const epochMs = Date.now();
      return { epochMs, offsetMinutes: -new Date(epochMs).getTimezoneOffset() };
    },
    sleep: async (seconds) => {
      await Bun.sleep(seconds * 1000);
    },
  };
  const source = await readStore(repository, rev, settingsRev);
  const table = source.settings === null ? {} : zeroTwoCoreTable(source.settings);
  const copy: ZeroTwoCopy = { ...source, settings: table };
  const database = await openDatabase(":memory:");
  const folder = mkdtempSync(join(tmpdir(), "lodge-round-trip-"));
  try {
    const projects = new SqliteProjects(database, clock);
    await projects.create("round-trip", "ana", table);
    const result = await importStore(
      copy,
      "round-trip",
      "ana",
      projects,
      coreSettings(table),
      clock,
    );
    if (result.kind !== "imported") {
      console.error(JSON.stringify(result));
      return 1;
    }
    const store = projects.storeFor("round-trip", person("ana"));
    const [current] = await store.trees();
    const files = exportFiles(current, await store.attachmentTexts());
    const target = { repository: folder, branch: "records", remote: null };
    run(["init", "--bare", "-b", "main"], folder);
    const outcome = await exportStore(target, files, exportMessage(files));
    if (outcome.kind !== "committed") throw new Error("the first export did not commit");
    const exported = await readStore(folder, target.branch);
    const counts = compareStores(source.files, exported.files, "ana");
    console.log(`Files compared: ${counts.compared}`);
    console.log(`Files equal: ${counts.equal}`);
    console.log(`Files differing only in decided_by or a message's by: ${counts.mapped}`);
    console.log(`Other differences: ${counts.differences.length}`);
    for (const { path, line } of counts.differences)
      console.log(`${path}: first difference at line ${line}`);
    return counts.differences.length ? 1 : 0;
  } finally {
    await database.close();
    rmSync(folder, { recursive: true, force: true });
  }
}

if (import.meta.main) {
  const [repository, rev, settingsRev, ...extra] = process.argv.slice(2);
  if (!repository || !rev || extra.length) {
    console.error("Usage: round-trip.ts REPOSITORY REV [SETTINGS_REV]");
    process.exitCode = 1;
  } else {
    try {
      process.exitCode = await roundTrip(repository, rev, settingsRev);
    } catch (error) {
      console.error(error instanceof Error ? error.message : String(error));
      process.exitCode = 1;
    }
  }
}
