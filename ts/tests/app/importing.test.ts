import { expect, test } from "bun:test";
import { coreSettings, prepareImport, stampOf, type ZeroTwoCopy } from "#app";
import { checkChange, load, parseRecord, tree, writeThread } from "#core";
import { START } from "./fakes.ts";
import { zeroTwoCopy } from "./zero-two-copy.ts";

const now = "2026-11-03T00:00:00+00:00";
const people = new Set(["ana"]);
const copy = zeroTwoCopy();
const original = copy.files;
const settings = coreSettings(copy.settings);
const authorIds = ["d-40q44p", "d-qqrf9k", "d-t46j05"];
const paths = [
  "lodge/attachments/d-q59cdf/sizes.csv",
  "lodge/decisions/d-40q44p-keep-old-transcripts.md",
  "lodge/decisions/d-q59cdf-keep-logs.md",
  "lodge/decisions/d-qqrf9k-keep-transcripts.md",
  "lodge/decisions/d-t46j05-confirm-logs.md",
  "lodge/spec/storage/_area.md",
  "lodge/spec/storage/s-cjhfb7-transcripts-are-kept.md",
  "lodge/threads/q-j2dsgk.md",
];
function pathOf(id: string): string {
  const path = paths.find(
    (path) => path.includes(id) && (!id.startsWith("d-") || path.startsWith("lodge/decisions/")),
  );
  if (!path) throw new Error(`missing fixture ${id}`);
  return path;
}
function changed(id: string, change: (text: string) => string): ZeroTwoCopy {
  const files = new Map(copy.files);
  const path = pathOf(id);
  files.set(path, change(files.get(path) as string));
  return { ...copy, files };
}
function prepare(value = copy) {
  return prepareImport(value, "ana", people, settings, now);
}
function refused(value: ReturnType<typeof prepareImport>, stage: "lodge 0.2" | "server") {
  expect(value.stage).toBe(stage);
  expect(value.files.size).toBe(0);
  expect(value.problems.length).toBeGreaterThan(0);
}

test("clean_store_prepares_every_file", () => {
  const result = prepare();
  expect(result.problems).toEqual([]);
  expect(result.stage).toBeNull();
  expect([...result.files.keys()].sort()).toEqual(paths);
  expect(result.mapped).toEqual([...authorIds, "q-j2dsgk"]);
});

test("author_decisions_name_the_owner", () => {
  const result = prepare();
  for (const id of authorIds) {
    const path = pathOf(id);
    expect(result.files.get(path)).toBe(
      (original.get(path) as string).replace("decided_by: author\n", "decided_by: ana\n"),
    );
  }
});

test("agent_decision_is_unchanged", () => {
  const path = pathOf("keep-logs");
  expect(prepare().files.get(path)).toBe(original.get(path));
});

test("author_message_names_the_owner", () => {
  const path = pathOf("q-j2dsgk");
  expect(prepare().files.get(path)).toBe(
    (original.get(path) as string).replace("by: author\n", "by: ana\n"),
  );
});

function roleCollision(where: boolean): ZeroTwoCopy {
  return changed("q-j2dsgk", (text) =>
    text
      .replace("by: coordinator", "by: ana")
      .replace(
        "when: 2026-11-02T18:56:30+01:00\n",
        `when: 2026-11-02T18:56:30+01:00\n${where ? 'where: "chat"\n' : ""}`,
      ),
  );
}
function canonicalSource(value: ZeroTwoCopy): string {
  const source = load(tree({ rev: null, files: value.files }));
  expect(
    checkChange(load(tree({ rev: null, files: new Map() })), source, settings, now).problems,
  ).toEqual([]);
  const thread = source.threads.get("q-j2dsgk");
  if (!thread) throw new Error("expected thread fixture");
  const text = value.files.get(pathOf(thread.id)) as string;
  expect(writeThread(thread, source.people)).toBe(text);
  return text;
}

test("role_collision_preserves_every_non_author_line", () => {
  const value = roleCollision(true);
  const source = canonicalSource(value);
  const result = prepare(value);
  expect(result.problems).toEqual([]);
  expect(result.stage).toBeNull();
  expect(result.files.get(pathOf("q-j2dsgk"))).toBe(source.replace("by: author\n", "by: ana\n"));
});

test("mapped_thread_failure_is_at_the_server_stage", () => {
  const value = roleCollision(false);
  canonicalSource(value);
  const result = prepare(value);
  refused(result, "server");
  expect(result.problems).toContainEqual(
    expect.objectContaining({
      path: pathOf("q-j2dsgk"),
      check: 1,
      message: expect.stringContaining("where"),
    }),
  );
});

test("mapped_writer_failure_is_at_the_server_stage", () => {
  const result = prepareImport(copy, "a\nb", new Set(["a\nb"]), settings, now);
  refused(result, "server");
  expect(result.problems).toEqual([
    ...authorIds.map((id) => ({
      kind: "problem" as const,
      path: pathOf(id),
      check: 1,
      line: null,
      message:
        "the server cannot write this file with the owner as its author: decided_by: U+000A cannot be written in a header",
    })),
    {
      kind: "problem" as const,
      path: pathOf("q-j2dsgk"),
      check: 1,
      line: null,
      message:
        "the server cannot write this file with the owner as its author: by: U+000A cannot be written in a header",
    },
  ]);
});

test("ids_dates_codes_and_imported_from_are_kept", () => {
  const result = prepare();
  for (const id of authorIds) {
    const path = pathOf(id);
    const before = parseRecord(path, original.get(path) as string);
    const after = parseRecord(path, result.files.get(path) as string);
    expect(before.kind).toBe("decision");
    if (before.kind !== "decision") throw new Error("expected decision fixture");
    expect(after).toEqual({ ...before, decidedBy: "ana" });
  }
  for (const path of paths.filter(
    (path) => !path.includes("decisions/") && !path.includes("threads/"),
  ))
    expect(result.files.get(path)).toBe(original.get(path));
});

test("failing_store_prepares_nothing", () => {
  const result = prepare({ ...copy, settings: { import: { sources: [] } } });
  refused(result, "lodge 0.2");
  expect(result.problems).toContainEqual(
    expect.objectContaining({
      check: 4,
      message: "d-40q44p: imported from docs/choices.md, which is not listed in [import] sources",
    }),
  );
});

test("store_dated_after_now_is_refused", () => {
  const result = prepareImport(copy, "ana", people, settings, stampOf(START));
  refused(result, "lodge 0.2");
  for (const id of ["d-q59cdf", "d-qqrf9k", "d-t46j05"])
    expect(result.problems).toContainEqual(expect.objectContaining({ check: 1, path: pathOf(id) }));
});

test("stray_file_fails_the_check", () => {
  const files = new Map(copy.files).set("lodge/notes.txt", "Stray notes.\n");
  const result = prepare({ ...copy, files });
  refused(result, "lodge 0.2");
  expect(result.problems).toContainEqual(
    expect.objectContaining({ check: 1, path: "lodge/notes.txt" }),
  );
});

test("undecodable_record_refuses_the_import", () => {
  const result = prepare(changed("d-qqrf9k", (text) => text.replace("Keep them.", "Keep \uDCFF.")));
  refused(result, "lodge 0.2");
  expect(result.problems).toContainEqual(
    expect.objectContaining({ check: 1, path: pathOf("d-qqrf9k") }),
  );
});

test("file_the_writer_would_not_give_back_is_refused", () => {
  const result = prepare(
    changed("d-qqrf9k", (text) =>
      text.replace("id: d-qqrf9k\nkind: decision", "kind: decision\nid: d-qqrf9k"),
    ),
  );
  refused(result, "lodge 0.2");
  expect(result.problems).toContainEqual(
    expect.objectContaining({
      path: pathOf("d-qqrf9k"),
      check: 1,
      message:
        "lodge 0.2 did not write this file as lodge writes it, so the importer cannot change who wrote it alone",
    }),
  );
});

test("mapped_state_is_checked_with_the_project_settings", () => {
  const result = prepareImport(copy, "ana", people, coreSettings({}), now);
  refused(result, "server");
  expect(result.problems).toContainEqual(
    expect.objectContaining({ check: 4, path: pathOf("d-40q44p") }),
  );
});

test("owner_name_used_as_a_role_fails_the_server_check", () => {
  const value = changed("d-q59cdf", (text) =>
    text.replace("decided_by: coordinator", "decided_by: ana"),
  );
  const result = prepare(value);
  refused(result, "server");
  expect(result.problems).toContainEqual(
    expect.objectContaining({ check: 3, path: pathOf("d-q59cdf") }),
  );
});

test("undecodable_name_is_refused", () => {
  const files = new Map(copy.files);
  const path = "lodge/spec/storage/s-cjhfb7-\uDCFF.md";
  const old = pathOf("s-cjhfb7");
  files.set(path, files.get(old) as string);
  files.delete(old);
  const result = prepare({ ...copy, files });
  refused(result, "server");
  expect(result.problems).toContainEqual(
    expect.objectContaining({
      path,
      check: 1,
      message:
        "this file's name is not UTF-8, which the server cannot store; rename it in the lodge 0.2 store and import again",
    }),
  );
});

test("owner_named_author_changes_nothing", () => {
  const result = prepareImport(copy, "author", new Set(["author"]), settings, now);
  expect(result.problems).toEqual([]);
  expect(result.files).toEqual(
    new Map([...original].filter(([path]) => !path.endsWith("/.gitkeep"))),
  );
  expect(load(tree({ rev: null, files: result.files })).problems).toEqual([]);
});

test("undecodable_attachment_is_preserved", () => {
  const path = "lodge/attachments/d-q59cdf/raw.bin";
  const result = prepare({ ...copy, files: new Map(copy.files).set(path, "\uDCFF\uDCFE") });
  expect(result.problems).toEqual([]);
  expect(result.files.get(path)).toBe("\uDCFF\uDCFE");
});

test("thread_the_writer_would_not_give_back_is_refused", () => {
  const result = prepare(
    changed("q-j2dsgk", (text) =>
      text.replace("id: q-j2dsgk\nkind: thread", "kind: thread\nid: q-j2dsgk"),
    ),
  );
  refused(result, "lodge 0.2");
  expect(result.problems).toContainEqual(
    expect.objectContaining({
      path: pathOf("q-j2dsgk"),
      check: 1,
      message:
        "lodge 0.2 did not write this file as lodge writes it, so the importer cannot change who wrote it alone",
    }),
  );
});
