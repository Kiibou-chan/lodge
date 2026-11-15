import { expect, test } from "bun:test";
import { handler } from "#api";
import { isolateGit } from "../git/isolated.ts";
import { commit } from "../git/repos.ts";
import { zeroTwoRepository } from "../git/zero-two.ts";
import { SESSION_COOKIE, world } from "./world.ts";

isolateGit();
const settings = { import: { sources: ["docs/choices.md"] } };
async function ready(
  layout: "checkout" | "branch" = "checkout",
  projectSettings: Readonly<Record<string, unknown>> = settings,
) {
  const w = await world();
  await w.clock.sleep(432000);
  await w.createProject("moved", projectSettings);
  const source = await zeroTwoRepository(layout);
  const token = (
    await (
      await w.asPerson("token-issue", { project: "moved", label: "t", role: null })
    )
      .text()
      .then(JSON.parse)
  ).result.secret;
  return { ...w, source, token, body: { project: "moved", ...source } };
}
test.each(["checkout", "branch"] as const)(
  "person_imports_the_made_up_store %s",
  async (layout) => {
    const w = await ready(layout);
    const body: Record<string, unknown> = { ...w.body };
    if (layout === "checkout") delete body["settingsRev"];
    const r = await w.asPerson("import", body);
    expect(r.status).toBe(200);
    expect((await r.text().then(JSON.parse)).result).toMatchObject({
      kind: "imported",
      decisions: 4,
      entries: 1,
      areas: 1,
      threads: 1,
      attachments: 1,
    });
    for (const ref of ["d-40q44p", "d-qqrf9k", "d-t46j05"]) {
      const shown = await w.fetch(w.request("show", { project: "moved", ref }, w.token));
      expect(shown.status).toBe(200);
      expect((await shown.text().then(JSON.parse)).result.level1.decidedBy).toBe("ada");
    }
    await w.exporters.settled();
    await w.database.close();
  },
);
test("agent_token_is_forbidden", async () => {
  const w = await ready();
  const r = await w.fetch(w.request("import", w.body, w.token));
  expect(r.status).toBe(403);
  expect(await r.text().then(JSON.parse)).toEqual({
    error: { kind: "forbidden", message: "only the signed-in person may import" },
  });
  await w.database.close();
});
test("second_import_is_a_conflict", async () => {
  const w = await ready();
  expect((await w.asPerson("import", w.body)).status).toBe(200);
  expect((await w.asPerson("import", w.body)).status).toBe(409);
  await w.exporters.settled();
  await w.database.close();
});
for (const name of [
  "failing_store_answers_check_failed",
  "project_without_the_sources_answers_check_failed",
  "branch_layout_without_its_settings_fails_check_4",
]) {
  test(name, async () => {
    const w = await ready(
      name.startsWith("branch") ? "branch" : "checkout",
      name.startsWith("project") ? {} : settings,
    );
    const body: Record<string, unknown> = { ...w.body };
    if (name.startsWith("failing")) {
      commit(w.source.repository, ".lodge.toml", "[import]\nsources = []\n", "Empty sources");
      body["settingsRev"] = "HEAD";
    }
    if (name.startsWith("branch")) delete body["settingsRev"];
    const r = await w.asPerson("import", body);
    expect(r.status).toBe(422);
    const b = await r.text().then(JSON.parse);
    expect(b.error).toEqual({ kind: "check-failed", message: "the check failed" });
    expect(b.result.stage).toBe(name.startsWith("project") ? "server" : "lodge 0.2");
    expect(b.result.problems).toContainEqual(expect.objectContaining({ check: 4 }));
    const search = await w.fetch(w.request("search", { project: "moved" }, w.token));
    expect((await search.text().then(JSON.parse)).result.items).toEqual([]);
    await w.database.close();
  });
}
test.each([
  ["missing_revision_is_usage", { rev: undefined }, 400, "usage", "import: rev must be a string"],
  ["unknown_field_is_usage", { extra: true }, 400, "usage", "import: unknown field extra"],
  [
    "unknown_project_is_no_project",
    { project: "absent" },
    404,
    "no-project",
    "no project named absent",
  ],
])("%s", async (_name, extra, status, kind, message) => {
  const w = await ready();
  const r = await w.asPerson("import", { ...w.body, ...extra });
  expect(r.status).toBe(status);
  expect(await r.text().then(JSON.parse)).toEqual({ error: { kind, message } });
  await w.database.close();
});
test("imported_records_read_as_imported", async () => {
  const w = await ready();
  expect((await w.asPerson("import", w.body)).status).toBe(200);
  const r = await w.fetch(w.request("show", { project: "moved", ref: "d-40q44p" }, w.token));
  const text = await r.text();
  expect(text).toContain("imported");
  expect(text).toContain("unquoted");
  expect(text).toContain('"quote":null');
  await w.exporters.settled();
  await w.database.close();
});
test("project_settings_survive_the_wrapper", async () => {
  const w = await ready();
  expect(await w.options.projects.settings("moved")).toEqual(settings);
  await w.database.close();
});

test("invalid_settings_are_a_usage_error", async () => {
  const w = await ready();
  commit(w.source.repository, ".lodge.toml", "[broken", "Invalid settings");
  const r = await w.asPerson("import", { ...w.body, settingsRev: "HEAD" });
  expect(r.status).toBe(400);
  const b = await r.text().then(JSON.parse);
  expect(b.error.kind).toBe("usage");
  expect(b.error.message).toMatch(/^\.lodge\.toml: [^\r\n]+$/u);
  await w.database.close();
});

test.each(["import", "export-target"])("server_without_moving_refuses %s", async (operation) => {
  const w = await ready();
  const { moving, ...options } = w.options;
  expect(moving).toBeDefined();
  const request = w.request(
    operation,
    operation === "import" ? w.body : { project: "moved", target: null },
    null,
  );
  request.headers.set("Cookie", SESSION_COOKIE);
  request.headers.set("Origin", "https://lodge.test");
  const response = await handler(options)(request);
  expect(response.status).toBe(400);
  expect(await response.text().then(JSON.parse)).toEqual({
    error: { kind: "usage", message: "this server was started without import and export" },
  });
  await w.database.close();
});

test("omitted_settings_revision_uses_the_older_store_revision", async () => {
  const w = await ready("checkout");
  commit(w.source.repository, ".lodge.toml", "[import]\nsources = []\n", "Empty sources at HEAD");
  const { settingsRev, ...body } = w.body;
  expect(settingsRev).toBe(w.source.rev);
  const response = await w.asPerson("import", body);
  expect(response.status).toBe(200);
  expect((await response.text().then(JSON.parse)).result.kind).toBe("imported");
  await w.exporters.settled();
  await w.database.close();
});

test.each(["", "relative/dir"])("repository_must_be_absolute %p", async (repository) => {
  const w = await ready();
  let reads = 0;
  const moving = w.options.moving;
  if (!moving) throw new Error("missing moving ports");
  const fetch = handler({
    ...w.options,
    moving: {
      ...moving,
      read: async () => {
        reads++;
        throw new Error("repository must be refused before reading");
      },
    },
  });
  const request = w.request("import", { ...w.body, repository }, null);
  request.headers.set("Cookie", SESSION_COOKIE);
  request.headers.set("Origin", "https://lodge.test");
  const response = await fetch(request);
  expect(reads).toBe(0);
  expect(response.status).toBe(400);
  expect(await response.json()).toEqual({
    error: { kind: "usage", message: "import: repository must be an absolute path" },
  });
  await w.database.close();
});
