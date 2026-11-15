import { expect, test } from "bun:test";
import { zeroTwoCoreTable } from "#cli";
import { encodeUtf8 } from "#core";
import { readStore } from "#git";
import { isolateGit } from "../git/isolated.ts";
import { bareRemote, git } from "../git/repos.ts";
import { zeroTwoRepository } from "../git/zero-two.ts";
import { world } from "./world.ts";

isolateGit();
async function roundTrip(layout: "checkout" | "branch") {
  const extra = new Map([["lodge/attachments/d-q59cdf/raw.bin", "\uDCFF\uDCFE"]]);
  const source = await zeroTwoRepository(layout, extra);
  const original = await readStore(source.repository, source.rev, source.settingsRev);
  const w = await world();
  await w.clock.sleep(432000);
  await w.createProject("moved", zeroTwoCoreTable(original.settings ?? ""));
  const response = await w.asPerson("import", {
    project: "moved",
    repository: source.repository,
    rev: source.rev,
    ...(layout === "branch" ? { settingsRev: source.settingsRev } : {}),
  });
  expect(response.status).toBe(200);
  expect((await response.text().then(JSON.parse)).result.kind).toBe("imported");
  const target = { repository: bareRemote(), branch: "records", remote: null };
  expect((await w.asPerson("export-target", { project: "moved", target })).status).toBe(200);
  await w.exporters.settled();
  expect(w.logs).toEqual([]);
  return { w, original, target };
}

test.each(["checkout", "branch"] as const)(
  "made_up_store_survives_import_and_export %s",
  async (layout) => {
    const { w, original, target } = await roundTrip(layout);
    try {
      const exported = await readStore(target.repository, target.branch);
      expect([...exported.files.keys()].sort()).toEqual([...original.files.keys()].sort());
      let changed = 0;
      for (const [path, text] of original.files) {
        const expected = path.startsWith("lodge/decisions/")
          ? text.replace(/^decided_by: author$/gmu, "decided_by: ada")
          : path.startsWith("lodge/threads/")
            ? text.replace(/^(## Message [0-9]+\n\n)by: author$/gmu, "$1by: ada")
            : text;
        if (expected !== text) changed++;
        expect(encodeUtf8(exported.files.get(path) as string)).toEqual(encodeUtf8(expected));
      }
      expect(changed).toBe(4);
      expect(
        encodeUtf8(exported.files.get("lodge/attachments/d-q59cdf/raw.bin") as string),
      ).toEqual(new Uint8Array([0xff, 0xfe]));
      for (const path of ["lodge/decisions/.gitkeep", "lodge/spec/.gitkeep"])
        expect(exported.files.get(path)).toBe("");
      expect(exported.settings).toBeNull();
    } finally {
      await w.database.close();
    }
  },
);

test("export_of_an_export_is_unchanged", async () => {
  const { w, target } = await roundTrip("checkout");
  try {
    const before = git(target.repository, "rev-parse", target.branch);
    await w.exporters.written("moved");
    await w.exporters.settled();
    expect(w.logs).toEqual([]);
    expect(git(target.repository, "rev-parse", target.branch)).toBe(before);
  } finally {
    await w.database.close();
  }
});
