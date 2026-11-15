import { expect, test } from "bun:test";
import { isolateGit } from "../git/isolated.ts";
import { bareRemote, git } from "../git/repos.ts";
import { draft } from "./person-fixtures.ts";
import { world } from "./world.ts";

isolateGit();
async function ready() {
  const w = await world();
  await w.createProject("moved", {});
  const token = (
    await (
      await w.asPerson("token-issue", { project: "moved", label: "t", role: null })
    )
      .text()
      .then(JSON.parse)
  ).result.secret;
  const target = { repository: bareRemote(), branch: "records", remote: null };
  return { ...w, token, target, body: { project: "moved", target } };
}
test("person_sets_the_target", async () => {
  const w = await ready();
  const r = await w.asPerson("export-target", w.body);
  expect(r.status).toBe(200);
  expect(await r.text().then(JSON.parse)).toEqual({ result: { target: w.target } });
  expect(await w.targets.target("moved")).toEqual(w.target);
  await w.exporters.settled();
  await w.database.close();
});
test("agent_token_is_forbidden", async () => {
  const w = await ready();
  const r = await w.fetch(w.request("export-target", w.body, w.token));
  expect(r.status).toBe(403);
  expect(await r.text().then(JSON.parse)).toEqual({
    error: { kind: "forbidden", message: "only the signed-in person may export-target" },
  });
  await w.database.close();
});
test("bad_target_is_usage", async () => {
  const w = await ready();
  const r = await w.asPerson("export-target", { ...w.body, target: { ...w.target, branch: "-x" } });
  expect(r.status).toBe(400);
  expect(await r.text().then(JSON.parse)).toEqual({
    error: {
      kind: "usage",
      message:
        "export-target: branch must be a name of letters, digits, and . _ / -, not starting with a symbol",
    },
  });
  expect(await w.targets.target("moved")).toBeNull();
  await w.database.close();
});
test("unknown_project_is_no_project", async () => {
  const w = await ready();
  const r = await w.asPerson("export-target", { ...w.body, project: "absent" });
  expect(r.status).toBe(404);
  expect(await r.text().then(JSON.parse)).toEqual({
    error: { kind: "no-project", message: "no project named absent" },
  });
  await w.database.close();
});
test("write_after_target_exports", async () => {
  const w = await ready();
  expect((await w.asPerson("export-target", w.body)).status).toBe(200);
  await w.exporters.settled();
  const r = await w.fetch(
    w.request("add", { project: "moved", drafts: [["d.md", draft("reviewer")]] }, w.token),
  );
  expect(r.status).toBe(200);
  const id = (await r.text().then(JSON.parse)).result.ids[0];
  await w.exporters.settled();
  expect(git(w.target.repository, "ls-tree", "-r", "--name-only", "records")).toContain(id);
  expect(w.logs).toEqual([]);
  await w.database.close();
});
test("null_target_stops_the_export", async () => {
  const w = await ready();
  await w.asPerson("export-target", w.body);
  await w.exporters.settled();
  const before = git(w.target.repository, "rev-parse", "records");
  const r = await w.asPerson("export-target", { project: "moved", target: null });
  expect(await r.text().then(JSON.parse)).toEqual({ result: { target: null } });
  expect(await w.targets.target("moved")).toBeNull();
  await w.fetch(
    w.request("add", { project: "moved", drafts: [["d.md", draft("reviewer")]] }, w.token),
  );
  await w.exporters.settled();
  expect(git(w.target.repository, "rev-parse", "records")).toBe(before);
  await w.database.close();
});

test("export_notification_rejection_is_logged", async () => {
  const w = await ready();
  w.exporters.written = async () => {
    throw new Error("synthetic notification failure");
  };
  expect((await w.asPerson("export-target", w.body)).status).toBe(200);
  expect(w.logs).toEqual(["lodge: the export of moved failed: synthetic notification failure\n"]);
  await w.database.close();
});

test.each([
  [undefined, "target must be an object or null"],
  [[], "target must be an object or null"],
  [{ repository: 1, branch: "records", remote: null }, "target.repository must be a string"],
  [{ repository: "/synthetic", branch: 1, remote: null }, "target.branch must be a string"],
  [
    { repository: "/synthetic", branch: "records", remote: 1 },
    "target.remote must be a string or null",
  ],
  [
    { repository: "/synthetic", branch: "records", remote: null, extra: true },
    "unknown field target.extra",
  ],
])("target_fields_are_checked %p", async (target, message) => {
  const w = await ready();
  const response = await w.asPerson("export-target", { project: "moved", target });
  expect(response.status).toBe(400);
  expect(await response.text().then(JSON.parse)).toEqual({
    error: { kind: "usage", message: `export-target: ${message}` },
  });
  expect(await w.targets.target("moved")).toBeNull();
  await w.database.close();
});
