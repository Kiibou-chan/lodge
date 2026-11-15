import { expect, test } from "bun:test";
import { run } from "#cli";
import { splitLines } from "#core";
import { version } from "../../package.json";
import { project } from "./project.ts";
import { testServer } from "./server.ts";
import { decisionText, seed } from "./support.ts";

test("draft_then_add_edit", async () => {
  const p = await project(),
    ids = await seed(p);
  const drafted = await p.run("draft", ids.entry);
  expect(drafted.code).toBe(0);
  expect(drafted.out.startsWith("---\nbase: ")).toBe(true);
  expect(drafted.out).toContain(`id: ${ids.entry}`);
  const edited = drafted.out.replace("Held.", "Held, whole.");
  const decision = decisionText(
    "Keep them whole",
    ["changes:", `  - {entry: ${ids.entry}, action: edit}`],
    { body: "Entries say so." },
  );
  const added = await p.run("add", p.draft("decision.md", decision), p.draft("entry.md", edited));
  expect(added.code).toBe(0);
  expect(splitLines(added.out).at(-1)?.startsWith("published d-")).toBe(true);
  expect((await p.run("show", ids.entry)).out).toContain("Held, whole.");
});
test("draft_of_an_area", async () => {
  const p = await project();
  await seed(p);
  expect((await p.run("draft", "area:storage")).out.startsWith("---\nname: storage\nbase: ")).toBe(
    true,
  );
});
test("draft_of_an_unknown_record", async () => {
  const p = await project();
  await seed(p);
  const r = await p.run("draft", "s-zzzzzz");
  expect([r.code, r.err]).toEqual([2, "lodge: no record named s-zzzzzz\n"]);
});
test("draft_text_is_printed_without_an_extra_newline", async () => {
  const p = await project(),
    ids = await seed(p);
  const path = (await p.paths()).find((path) =>
    path.startsWith(`lodge/spec/storage/${ids.entry}-`),
  );
  expect(path).toBeDefined();
  const stored = await p.stored(path ?? "");
  expect(stored).not.toBeNull();
  expect((await p.run("draft", ids.entry)).out.split("\n").length - 1).toBe(
    stored?.split("\n").length ?? 1,
  );
});
test("draft_of_a_decision_says_decisions_are_immutable", async () => {
  const p = await project(),
    ids = await seed(p);
  const drafted = await p.run("draft", ids.decision);
  expect(drafted.code).toBe(0);
  expect(drafted.out.startsWith("---\nbase: ")).toBe(true);
  expect(drafted.err).toBe(
    "note: decisions are immutable; to change one, write a new decision with replaces or narrows\n",
  );
  expect((await p.run("draft", ids.entry)).err).toBe("");
  expect((await p.run("draft", "--help")).out.split(/\s+/u).join(" ")).toContain(
    "a decision is immutable",
  );
});

test("draft_crlf_is_normalised_before_request", async () => {
  const p = await project(),
    server = await testServer();
  let sent: unknown;
  const io = {
    cwd: p.root,
    env: { LODGE_TOKEN: server.token },
    version,
    out: (_text: string) => {},
    err: (_text: string) => {},
    fetch: async (request: Request) => {
      const body = (await request.clone().json()) as { drafts?: unknown };
      if (body.drafts) sent = body.drafts;
      return server.fetch(request);
    },
  };
  expect(await run(["init"], io)).toBe(0);
  const text = decisionText(),
    path = p.draft("crlf.md", text.replaceAll("\n", "\r\n"));
  expect(await run(["add", path], io)).toBe(0);
  expect(sent).toEqual([[path, text]]);
});
