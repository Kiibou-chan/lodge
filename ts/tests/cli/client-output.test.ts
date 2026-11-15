import { expect, test } from "bun:test";
import { project } from "../e2e/project.ts";
import { answer, clientHarness, failure } from "./client-support.ts";

const { invoke } = await clientHarness();

test("draft_decision_note_and_exact_text", async () => {
  const text = "---\n kind: decision \n---\n\nStatement.\n";
  expect(
    await invoke(async () => answer({ result: text }), undefined, ["draft", "d-aaaaaa"]),
  ).toEqual({
    code: 0,
    out: text,
    err: "note: decisions are immutable; to change one, write a new decision with replaces or narrows\n",
  });
  const entry = "---\nkind: spec\n---\nkind: decision\n";
  expect(
    await invoke(async () => answer({ result: entry }), undefined, ["draft", "s-aaaaaa"]),
  ).toEqual({ code: 0, out: entry, err: "" });
});
test("add_output_marks_ids_with_unicode_boundaries_and_escapes", async () => {
  const p = await project(),
    file = p.draft("d.md", "draft");
  const added = {
    ids: [],
    minted: ["d-a+b"],
    paths: [],
    freshness: "fresh",
    awaits: null,
    held: null,
    outcome: "check failed",
    feedback: [{ recordId: "d-a+b", message: "advice" }],
    check: {
      ok: false,
      notes: ["note"],
      problems: [
        {
          kind: "problem",
          path: "p",
          line: null,
          check: 3,
          message: "d-a+b d-a+b (provisional) 字d-a+b d-a+b字",
        },
      ],
    },
  };
  expect(
    await invoke(
      async () =>
        answer({ error: { kind: "check-failed", message: "failed" }, result: added }, "0.3.0", 422),
      undefined,
      ["add", "--dry-run", file],
    ),
  ).toEqual({
    code: 1,
    out: "feedback: d-a+b (provisional): advice\nnote: note\ncheck 3: d-a+b (provisional) d-a+b (provisional) 字d-a+b d-a+b字\nfresh\nnot published: the check failed\ndry run: nothing published\n",
    err: "",
  });
});
test.each([
  [false, "held for approval"],
  [true, "dry run"],
] as const)("add_awaits_output %p %p", async (dryRun, outcome) => {
  const p = await project(),
    file = p.draft("d.md", "draft");
  const added = {
    ids: ["d-aaaaaa"],
    minted: ["d-aaaaaa"],
    paths: [],
    freshness: null,
    awaits: "author",
    held: 7,
    outcome,
    feedback: [{ recordId: "d-aaaaaa", message: "advice" }],
    check: { ok: true, notes: [], problems: [] },
  };
  expect(
    await invoke(async () => answer({ result: added }), undefined, [
      "add",
      ...(dryRun ? ["--dry-run"] : []),
      file,
    ]),
  ).toEqual({
    code: 0,
    out:
      "feedback: d-aaaaaa (provisional): advice\n" +
      (dryRun
        ? "note: author approves this add before it is current\ndry run: nothing published\n"
        : "held for approval by author as hold 7; nothing is current until they approve it\n"),
    err: "",
  });
});
test("check_deduplicates_every_problem_field", async () => {
  const base = { kind: "problem", path: "p", line: 2, check: 3, message: "broken" };
  const problems = [
    { ...base },
    { ...base, path: "q" },
    { ...base, line: 3 },
    { ...base, check: 4 },
    { ...base, message: "other" },
  ];
  expect(
    await invoke(
      async () =>
        answer({
          result: [
            { ok: false, problems, notes: ["advice"] },
            { freshness: "fresh", unrecorded: [base], statuses: { $map: [] } },
          ],
        }),
      undefined,
      ["check"],
    ),
  ).toEqual({
    code: 1,
    out: "fresh\nproblem: p:2: broken\ncheck 3: broken\ncheck 3: broken\ncheck 4: broken\ncheck 3: other\nnote: advice\n",
    err: "",
  });
});
test("reply_and_close_use_thread_and_exact_messages", async () => {
  const p = await project(),
    file = p.draft("message.txt", "Why?\r\n");
  for (const op of ["reply", "close"]) {
    expect(
      await invoke(
        async (req) => {
          expect(await req.json()).toEqual({
            project: "work",
            thread: "q-aaaaaa",
            by: "agent",
            text: "Why?\r\n",
            where: null,
            when: null,
          });
          return answer({ result: { outcome: "published", ids: ["q-aaaaaa"] } });
        },
        undefined,
        [op, "q-aaaaaa", "--by", "agent", file],
      ),
    ).toEqual({ code: 0, out: "published q-aaaaaa\n", err: "" });
  }
  expect(
    await invoke(
      async (req) => {
        expect(await req.json()).toEqual({
          project: "work",
          thread: "q-aaaaaa",
          by: "agent",
          text: "",
          where: null,
          when: null,
        });
        return answer({ result: { outcome: "published", ids: ["q-aaaaaa"] } });
      },
      undefined,
      ["close", "q-aaaaaa", "--by", "agent"],
    ),
  ).toEqual({ code: 0, out: "published q-aaaaaa\n", err: "" });
});
test("files_are_read_in_command_order", async () => {
  const p = await project();
  p.configure("[broken\n");
  const missing = `${p.root}/absent.md`;
  const add = await p.run("add", missing);
  expect(add).toEqual(failure(`lodge: ${missing}: cannot be read: No such file or directory\n`));
  const ask = await p.run("ask", "s-aaaaaa", "--kind", "doubt", "--by", "agent", missing);
  expect(ask.code).toBe(2);
  expect(ask.out).toBe("");
  expect(ask.err.startsWith("lodge: .lodge.toml:")).toBe(true);
});
