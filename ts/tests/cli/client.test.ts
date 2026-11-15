import { expect, test } from "bun:test";
import { type Io, run } from "#cli";
import { project } from "../e2e/project.ts";

const cli = await project();
const failure = (err: string) => ({ code: 2, out: "", err });
async function invoke(fetch: Io["fetch"], token?: string, argv = ["search"]) {
  let out = "",
    err = "";
  const code = await run(argv, {
    cwd: cli.root,
    env: { LODGE_TOKEN: token },
    version: "0.3.0",
    fetch,
    out: (t) => {
      out += t;
    },
    err: (t) => {
      err += t;
    },
  });
  return { code, out, err };
}
function answer(body: unknown, version: string | null = "0.3.0", status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: version === null ? {} : { "Lodge-Version": version },
  });
}
test("version_must_match", async () => {
  expect(await invoke(async () => answer({}, "0.2.0"))).toEqual(
    failure(
      `lodge: the server at ${cli.url} runs lodge 0.2.0 and this command is lodge 0.3.0; use the same version\n`,
    ),
  );
});
test("missing_version_is_not_lodge", async () => {
  expect(await invoke(async () => answer({}, null))).toEqual(
    failure(`lodge: ${cli.url} does not answer as a lodge server\n`),
  );
});
test("not_json_is_one_sentence", async () => {
  expect(
    await invoke(async () => new Response("not json", { headers: { "Lodge-Version": "0.3.0" } })),
  ).toEqual({
    code: 2,
    out: "",
    err: `lodge: ${cli.url} answered something other than JSON\n`,
  });
});
test("unreachable_server_is_one_sentence", async () => {
  expect(
    await invoke(async () => {
      throw new TypeError("Unable to connect");
    }),
  ).toEqual({ code: 2, out: "", err: `lodge: cannot reach ${cli.url}: Unable to connect\n` });
});
test.each([
  ["usage", 2],
  ["unauthorised", 2],
  ["forbidden", 2],
  ["not-found", 2],
  ["conflict", 1],
  ["internal", 2],
  ["check-failed", 1],
] as const)("kinds_map_to_exit_codes %p %p", async (kind, code) => {
  const result = [
    {
      ok: false,
      problems: [{ kind: "problem", path: "x", line: null, check: 3, message: "broken" }],
      notes: [],
    },
    { freshness: null, unrecorded: [], statuses: { $map: [] } },
  ];
  const r = await invoke(
    async () =>
      answer(
        { error: { kind, message: "bad" }, result },
        "0.3.0",
        kind === "check-failed" ? 422 : 400,
      ),
    "token",
    ["check"],
  );
  expect(r.code).toBe(code);
  expect(r.out).toBe(kind === "check-failed" ? "check 3: broken\n" : "");
  expect(r.err).toBe(
    kind === "check-failed"
      ? ""
      : kind === "unauthorised"
        ? "lodge: bad; an agent token goes in LODGE_TOKEN, or in a cloud environment's network secret for this server\n"
        : "lodge: bad\n",
  );
});
test("no_project_is_lodge_0_2_s_sentence", async () => {
  expect(
    await invoke(async () =>
      answer({ error: { kind: "no-project", message: "missing" } }, "0.3.0", 404),
    ),
  ).toEqual(failure("lodge: lodge has no data in this repository yet; run `lodge init`\n"));
});
test("token_travels_only_in_authorization", async () => {
  const r = await invoke(
    async (req) => {
      expect(req.headers.get("Authorization")).toBe("Bearer synthetic-token");
      expect(req.url).toBe(`${cli.url}/api/v1/mint`);
      expect(await req.text()).toBe('{"project":"work","prefix":"d"}');
      return answer({ result: "d-aaaaaa" });
    },
    "synthetic-token",
    ["id", "d"],
  );
  expect(r).toEqual({ code: 0, out: "d-aaaaaa\n", err: "" });
});
test("no_token_sends_no_authorization", async () => {
  expect(
    await invoke(async (req) => {
      expect(req.headers.has("Authorization")).toBe(false);
      return answer({ error: { kind: "unauthorised", message: "missing token" } }, "0.3.0", 401);
    }, undefined),
  ).toEqual(
    failure(
      "lodge: missing token; an agent token goes in LODGE_TOKEN, or in a cloud environment's network secret for this server\n",
    ),
  );
});
test("thread_file_errors_are_cli_errors", async () => {
  const p = await project();
  await p.run("init");
  const missing = `${p.root}/absent.txt`;
  expect(await p.run("reply", "q-aaaaaa", "--by", "agent", missing)).toEqual(
    failure(`lodge: ${missing}: cannot be read: No such file or directory\n`),
  );
});
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
