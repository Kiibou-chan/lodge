import { expect, test } from "bun:test";
import { run } from "#cli";
import { project } from "../e2e/project.ts";
import { answer, clientHarness, failure } from "./client-support.ts";

const { cli, invoke } = await clientHarness();

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
test("init_sends_core_settings", async () => {
  const p = await project();
  p.configure('[length]\ntitle_chars = 40\n[import]\nsources = ["notes.md", "archive.md"]\n');
  let requests = 0;
  expect(
    await run(["init"], {
      cwd: p.root,
      env: {},
      version: "0.3.0",
      fetch: async (request) => {
        requests += 1;
        expect(request.method).toBe("POST");
        expect(request.url).toBe(`${p.url}/api/v1/project-create`);
        expect(await request.json()).toEqual({
          project: "work",
          settings: {
            length: { title_chars: 40 },
            import: { sources: ["notes.md", "archive.md"] },
          },
        });
        return answer({ result: null });
      },
      out: () => {},
      err: () => {},
    }),
  ).toBe(0);
  expect(requests).toBe(1);
});
test.each([
  [200, null],
  [200, []],
  [200, "answer"],
  [200, 42],
  [200, false],
  [200, {}],
  [200, { error: { kind: "internal", message: "bad" } }],
  [422, { error: { kind: "check-failed", message: "bad" } }],
  [400, null],
  [400, []],
  [400, {}],
  [400, { result: "d-aaaaaa" }],
  [400, { error: null }],
  [400, { error: [] }],
  [400, { error: "bad" }],
  [400, { error: { message: "bad" } }],
  [400, { error: { kind: "internal" } }],
  [400, { error: { kind: 42, message: "bad" } }],
  [400, { error: { kind: "internal", message: 42 } }],
  [422, { error: { kind: "check-failed" }, result: null }],
] as const)("malformed_answer_is_one_sentence %p %p", async (status, body) => {
  expect(await invoke(async () => answer(body, "0.3.0", status), undefined, ["id", "d"])).toEqual(
    failure(`lodge: ${cli.url} answered something other than a lodge answer\n`),
  );
});
