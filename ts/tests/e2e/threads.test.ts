import { expect, test } from "bun:test";
import { writeFileSync } from "node:fs";
import { load, splitLines, tree } from "#core";
import { project } from "./project.ts";
import { seed } from "./support.ts";

test("ask_reply_close_round_trip", async () => {
  const p = await project(),
    { entry } = await seed(p);
  const opened = await p.run(
    "ask",
    entry,
    "--kind",
    "doubt",
    "--by",
    "coordinator",
    p.draft("ask.txt", "First question"),
  );
  expect(opened.code).toBe(0);
  expect(opened.out.startsWith("published q-")).toBe(true);
  const q = opened.out.trim().split(" ").at(-1) ?? "";
  expect((await p.run("threads")).out).toContain(q);
  expect((await p.run("threads")).out).toContain("1 message ·");
  expect(
    (await p.run("reply", q, "--by", "reviewer", p.draft("reply.txt", "Second answer"))).code,
  ).toBe(0);
  let shown = (await p.run("thread", q)).out;
  expect(shown).toContain("First question");
  expect(shown).toContain("Second answer");
  expect(shown.indexOf("First question")).toBeLessThan(shown.indexOf("Second answer"));
  expect(shown).toContain("2 messages · last by reviewer");
  expect((await p.run("close", q, "--by", "coordinator")).code).toBe(0);
  expect((await p.run("threads")).out).toBe("no open threads\n");
  shown = (await p.run("thread", q)).out;
  expect(splitLines(shown).at(-1)).toMatch(/^closed by coordinator · .+/u);
  expect(shown).not.toContain("Closed.");
});
test("author_message_needs_where_and_when_exit_2", async () => {
  const p = await project(),
    { entry } = await seed(p);
  for (const extra of [[], ["--where", "chat"], ["--when", "2026-10-31 12:00"]]) {
    const r = await p.run(
      "ask",
      entry,
      "--kind",
      "question",
      "--by",
      "author",
      ...extra,
      p.draft("message.txt", "Why?"),
    );
    expect(r.code).toBe(2);
    expect(r.err).toContain(
      "a message by author needs --where and --when, the place and time of the author's words",
    );
  }
});
test("where_with_an_agent_role_exit_2", async () => {
  const p = await project(),
    { entry } = await seed(p);
  const r = await p.run(
    "ask",
    entry,
    "--kind",
    "question",
    "--by",
    "reviewer",
    "--where",
    "chat",
    p.draft("message.txt", "Why?"),
  );
  expect(r.code).toBe(2);
  expect(r.err).toContain("--where and --when are for messages by author");
});
test("ask_on_unknown_ref_exit_2", async () => {
  const p = await project();
  await seed(p);
  const r = await p.run(
    "ask",
    "s-aaaaaa",
    "--kind",
    "doubt",
    "--by",
    "reviewer",
    p.draft("message.txt", "Why?"),
  );
  expect(r.code).toBe(2);
  expect(r.err).toContain("s-aaaaaa");
  expect(r.err).not.toContain("usage:");
});
test("author_words_are_recorded_exactly", async () => {
  const p = await project(),
    { entry } = await seed(p);
  const r = await p.run(
    "ask",
    entry,
    "--kind",
    "question",
    "--by",
    "author",
    "--where",
    "chat",
    "--when",
    "2026-10-31 12:00",
    p.draft("words.txt", "  a\rb\r\nc\r\nd  "),
  );
  expect(r.code).toBe(0);
  const held = splitLines(r.out)
    .at(-1)
    ?.match(
      /^held for approval by author as hold (\d+); nothing is current until they approve it$/u,
    );
  expect(held).toBeDefined();
  expect(held).not.toBeNull();
  const ids = await p.approve(Number(held?.[1]));
  const q = ids.find((id) => id.startsWith("q-"));
  expect(q).toBeDefined();
  const shown = await p.run("thread", q ?? "");
  expect([shown.code, shown.err]).toEqual([0, ""]);
  expect(shown.out).toContain("author · 2026-10-31 12:00 · chat\na\rb\nc\nd");
  const path = `lodge/threads/${q}.md`,
    raw = await p.stored(path);
  expect(raw).not.toBeNull();
  expect(
    load(tree({ rev: null, files: new Map([[path, raw ?? ""]]) })).threads.get(q ?? "")?.messages[0]
      ?.text,
  ).toBe("a\rb\nc\nd");
});
test.each(["reply", "close"].map((action) => [action]))(
  "reply_to_unknown_or_closed_thread_exit_2 %p",
  async (action) => {
    const p = await project(),
      { entry } = await seed(p),
      message = p.draft("message.txt", "Again");
    const unknown = await p.run(action ?? "", "q-000000", "--by", "reviewer", message);
    expect(unknown.code).toBe(2);
    expect(unknown.err).toContain("no thread named q-000000");
    const opened = await p.run("ask", entry, "--kind", "doubt", "--by", "reviewer", message),
      q = opened.out.trim().split(" ").at(-1) ?? "";
    expect((await p.run("close", q, "--by", "reviewer")).code).toBe(0);
    const closed = await p.run(action ?? "", q, "--by", "reviewer", message);
    expect(closed.code).toBe(2);
    expect(closed.err).toContain(`${q} is closed`);
  },
);
test.each(["missing", "non-utf8"].map((bad) => [bad]))(
  "missing_message_file_exit_2 %p",
  async (bad) => {
    const p = await project(),
      { entry } = await seed(p),
      path = `${p.root}/../bad.txt`;
    if (bad === "non-utf8") writeFileSync(path, new Uint8Array([255]));
    const r = await p.run("ask", entry, "--kind", "question", "--by", "reviewer", path);
    expect(r.code).toBe(2);
    expect(r.err.startsWith("lodge:")).toBe(true);
    expect(r.err).toContain(bad === "non-utf8" ? "not UTF-8 text" : "bad.txt");
  },
);
