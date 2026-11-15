import { expect, test } from "bun:test";
import {
  type ExportTarget,
  exportFailedLine,
  exportFiles,
  exportingProjects,
  exportMessage,
  exportTargetProblem,
  KEPT,
  type Projects,
  PublishOutcome,
  person,
  Role,
  type Store,
} from "#app";
import { tree } from "#core";
import { ZERO_TWO_STORE } from "../core/zero-two-store.ts";
import { MemoryStore } from "./fakes.ts";

const target: ExportTarget = {
  repository: "/synthetic/repository",
  branch: "records",
  remote: null,
};

test("export_files_hold_the_store_and_kept", async () => {
  for (const staged of [false, true]) {
    const store = new MemoryStore([], { staged });
    const files = new Map(
      [...ZERO_TWO_STORE].filter(([p]) => p.startsWith("lodge/") && !p.endsWith("/.gitkeep")),
    );
    expect(files.size).toBe(8);
    await store.publish((await store.trees())[0], files, "Import records");
    const current = (await store.trees())[0];
    const actual = exportFiles(current, await store.attachmentTexts());
    expect(KEPT).toEqual(["lodge/decisions/.gitkeep", "lodge/spec/.gitkeep"]);
    expect(actual).toEqual(new Map([...files, ...KEPT.map((p) => [p, ""] as const)]));
  }
  expect(
    exportFiles(
      tree({ rev: null, files: new Map([["lodge/spec/storage/.gitkeep", "old"]]) }),
      new Map(),
    ),
  ).toEqual(new Map(KEPT.map((p) => [p, ""])));
});

test("export_files_include_attachments_stored_separately", () => {
  const files = new Map(
    [...ZERO_TWO_STORE].filter(
      ([path]) =>
        path.startsWith("lodge/") &&
        !path.startsWith("lodge/attachments/") &&
        !path.endsWith("/.gitkeep"),
    ),
  );
  const attachmentTexts = new Map([
    ["lodge/attachments/d-q59cdf/sizes.csv", "size,count\nsmall,3\n"],
  ]);
  const current = tree({ rev: null, files, attachments: new Set(attachmentTexts.keys()) });
  expect(files.size).toBe(7);
  expect(exportFiles(current, attachmentTexts)).toEqual(
    new Map([...files, ...attachmentTexts, ...KEPT.map((path) => [path, ""] as const)]),
  );
});

test("failed_line_names_the_project", () => {
  expect(exportFailedLine("storage", new Error("boom"))).toBe(
    "lodge: the export of storage failed: boom\n",
  );
  expect(exportFailedLine("logs", "oops")).toBe("lodge: the export of logs failed: oops\n");
});

test("message_counts_the_records", () => {
  expect(exportMessage(ZERO_TWO_STORE)).toBe(
    "Export lodge records: 4 decisions, 1 entries, 1 areas, 1 threads",
  );
  expect(exportMessage(new Map(KEPT.map((p) => [p, ""])))).toBe(
    "Export lodge records: 0 decisions, 0 entries, 0 areas, 0 threads",
  );
});

test("target_problems_are_named", () => {
  expect(exportTargetProblem({ ...target, repository: "relative" })).toBe(
    "export-target: repository must be an absolute path",
  );
  for (const branch of ["-x", "a..b", "a b", "_name", "", ".name", "é"]) {
    expect(exportTargetProblem({ ...target, branch })).toBe(
      "export-target: branch must be a name of letters, digits, and . _ / -, not starting with a symbol",
    );
  }
  expect(exportTargetProblem({ ...target, remote: "-r" })).toBe(
    "export-target: remote must not start with -",
  );
  expect(
    exportTargetProblem({ ...target, branch: "a/b-1._x", remote: "/synthetic/remote" }),
  ).toBeNull();
});

function projectsWith(store: Store): Projects {
  return new Proxy({} as Projects, {
    get: (_, key) => {
      if (key === "storeFor") return () => store;
      throw new Error(`unexpected method ${String(key)}`);
    },
  });
}

test("wrapped_store_tells_the_exporter_after_a_publish", async () => {
  const inner = new MemoryStore();
  const calls: string[] = [];
  const wrapped = exportingProjects(projectsWith(inner), (project) => {
    expect(inner.publishes.length).toBeGreaterThan(0);
    calls.push(project);
  }).storeFor("storage", person("ana"));
  const base = (await wrapped.trees())[0];
  expect(await wrapped.publish(base, new Map(), "first")).toBe(PublishOutcome.PUBLISHED);
  expect(calls).toEqual(["storage"]);
  expect(await wrapped.publish(base, new Map(), "stale")).toBe(PublishOutcome.REJECTED);
  expect(calls).toEqual(["storage"]);
  const draft = {
    kind: "add",
    person: "ana",
    by: "agent",
    drafts: [],
    attachments: [],
    importing: false,
    message: "approve",
  } as const;
  const seq = await wrapped.hold(draft);
  expect(await inner.held()).toHaveLength(1);
  expect(await wrapped.publish((await wrapped.trees())[0], new Map(), "approve", seq)).toBe(
    PublishOutcome.PUBLISHED,
  );
  expect(calls).toEqual(["storage", "storage"]);
  expect(await inner.held()).toEqual([]);
  const staged = exportingProjects(projectsWith(new MemoryStore([], { staged: true })), (p) =>
    calls.push(p),
  ).storeFor("logs", person("ana"));
  expect(await staged.publish((await staged.trees())[0], new Map(), "stage")).toBe(
    PublishOutcome.STAGED,
  );
  expect(calls).toEqual(["storage", "storage"]);
});

test("wrapped_store_passes_every_other_method", async () => {
  const calls: [PropertyKey, unknown[]][] = [];
  const answer = { synthetic: true };
  const inner = new Proxy({} as Store, {
    get: (_, key) =>
      function (this: unknown, ...args: unknown[]) {
        expect(this).toBe(inner);
        calls.push([key, args]);
        return answer;
      },
  });
  const wrapped = exportingProjects(projectsWith(inner), () => {}).storeFor(
    "storage",
    person("ana"),
  );
  const current = tree({ rev: null, files: new Map() });
  const draft = {
    kind: "message",
    person: "ana",
    by: "agent",
    operation: "close",
    ref: "q-123456",
    raises: null,
    text: null,
    where: "chat",
    when: "today",
  } as const;
  expect<unknown>(wrapped.trees()).toBe(answer);
  expect<unknown>(wrapped.attachmentTexts()).toBe(answer);
  expect<unknown>(wrapped.freshness()).toBe(answer);
  expect<unknown>(wrapped.gate(current)).toBe(answer);
  expect<unknown>(wrapped.commit(["lodge/spec/a.md"], "message")).toBe(answer);
  expect<unknown>(wrapped.hold(draft)).toBe(answer);
  expect<unknown>(wrapped.held()).toBe(answer);
  expect<unknown>(wrapped.decline(3, "reason")).toBe(answer);
  expect(calls).toEqual([
    ["trees", []],
    ["attachmentTexts", []],
    ["freshness", []],
    ["gate", [current]],
    ["commit", [["lodge/spec/a.md"], "message"]],
    ["hold", [draft]],
    ["held", []],
    ["decline", [3, "reason"]],
  ]);
});

test("wrapped_projects_pass_every_method_with_its_arguments", () => {
  const calls: [PropertyKey, unknown[]][] = [];
  const answer = { synthetic: true };
  const inner = new Proxy({} as Projects, {
    get: (_, key) =>
      function (this: unknown, ...args: unknown[]) {
        expect(this).toBe(inner);
        calls.push([key, args]);
        return answer;
      },
  });
  const wrapped = exportingProjects(inner, () => {});
  const actor = person("ana");
  const settings = { mode: "staged" };
  expect<unknown>(wrapped.members("storage")).toBe(answer);
  expect<unknown>(wrapped.addMember("storage", "bo", Role.MEMBER, actor)).toBe(answer);
  expect<unknown>(wrapped.create("logs", "ana", settings)).toBe(answer);
  expect<unknown>(wrapped.settings("logs")).toBe(answer);
  expect<unknown>(wrapped.names()).toBe(answer);
  expect(calls).toEqual([
    ["members", ["storage"]],
    ["addMember", ["storage", "bo", Role.MEMBER, actor]],
    ["create", ["logs", "ana", settings]],
    ["settings", ["logs"]],
    ["names", []],
  ]);
});
