import { expect, test } from "bun:test";
import { type Command, parse } from "#cli";
import { filters } from "#core";

const cases: [string[], Command][] = [
  [["hook", "post-tool-use"], { kind: "hook", event: "post-tool-use" }],
  [["init"], { kind: "init" }],
  [["id", "d"], { kind: "id", prefix: "d" }],
  [
    [
      "search",
      "words",
      "--kind",
      "decision",
      "--scope",
      "process",
      "--status",
      "any",
      "--area",
      "storage",
      "--by",
      "builder",
      "--limit",
      "3",
    ],
    {
      kind: "search",
      query: "words",
      filters: filters({
        kind: "decision",
        scope: "process",
        status: "any",
        area: "storage",
        decidedBy: "builder",
      }),
      limit: 3,
    },
  ],
  [["show", "d-aaaaaa"], { kind: "show", ref: "d-aaaaaa", reasoning: false, provenance: false }],
  [["draft", "s-aaaaaa"], { kind: "draft", ref: "s-aaaaaa" }],
  [
    ["add", "a", "b", "--import", "--dry-run", "--attach", "c"],
    { kind: "add", files: ["a", "b"], importing: true, dryRun: true, attachments: ["c"] },
  ],
  [["check", "--gate"], { kind: "check", gate: true }],
  [["spec", "--area", "storage"], { kind: "spec", area: "storage" }],
  [["waiting"], { kind: "waiting" }],
  [["guide"], { kind: "guide" }],
  [["threads"], { kind: "threads" }],
  [["thread", "q-aaaaaa"], { kind: "thread", ref: "q-aaaaaa" }],
  [
    ["ask", "d-aaaaaa", "--kind", "question", "--by", "builder", "f"],
    {
      kind: "ask",
      ref: "d-aaaaaa",
      raises: "question",
      by: "builder",
      where: null,
      when: null,
      file: "f",
    },
  ],
  [
    ["reply", "q-aaaaaa", "--by", "builder", "f"],
    { kind: "reply", ref: "q-aaaaaa", by: "builder", where: null, when: null, file: "f" },
  ],
  [
    ["close", "q-aaaaaa", "--by", "builder"],
    { kind: "close", ref: "q-aaaaaa", by: "builder", where: null, when: null, file: null },
  ],
];
test.each(cases)("every_command_parses %p", (argv, expected) =>
  expect(parse(argv, "test")).toEqual(expected),
);
test("help_lists_every_command", () => {
  const result = parse(["--help"], "test");
  expect(result).toMatchObject({ code: 0 });
  if (result.kind !== "exit") throw Error("expected help");
  for (const [argv] of cases)
    expect(result.out.split("\n").some((line) => line.trim().split(/\s+/u)[0] === argv[0])).toBe(
      true,
    );
});
test.each(cases)("every_command_has_help %p", (argv) =>
  expect(parse([argv[0] ?? "", "-h"], "test")).toMatchObject({
    code: 0,
    out: expect.stringContaining(`usage: lodge ${argv[0]}`),
  }),
);
test("no_command_is_a_usage_error", () =>
  expect(parse([], "test")).toMatchObject({
    code: 2,
    err: "usage: lodge [-h] [--version] COMMAND ...\nlodge: error: the following arguments are required: COMMAND\n",
  }));
test.each([
  [
    ["search", "x", "--status", "gone"],
    "lodge search: error: argument --status: invalid choice: 'gone' (choose from current, replaced, retired, any)\n",
  ],
  [["id", "x"], "lodge id: error: argument prefix: invalid choice: 'x' (choose from d, s)\n"],
] as const)("invalid_choice_is_argparse_s_line %p", (argv, line) =>
  expect(parse(argv, "test")).toMatchObject({ code: 2, err: expect.stringContaining(line) }),
);
test("missing_positional_is_argparse_s_line", () =>
  expect(parse(["add"], "test")).toMatchObject({
    code: 2,
    err: expect.stringContaining("lodge add: error: the following arguments are required: FILE\n"),
  }));
test.each(["0", "-1", "many", "٣"])("limit_must_be_a_positive_whole_number %p", (value) =>
  expect(parse(["search", "--limit", value], "test")).toMatchObject({
    code: 2,
    err: expect.stringContaining(`argument --limit: '${value}' is not a positive whole number`),
  }),
);
test("author_message_needs_where_and_when", () =>
  expect(parse(["reply", "q-aaaaaa", "f", "--by", "author"], "test")).toMatchObject({
    code: 2,
    err: "lodge: a message by author needs --where and --when, the place and time of the author's words\n",
  }));
test("where_with_an_agent_role", () =>
  expect(parse(["close", "q-aaaaaa", "--by", "builder", "--where", "chat"], "test")).toMatchObject({
    code: 2,
    err: "lodge: --where and --when are for messages by author\n",
  }));
test("version_prints_the_version_given", () =>
  expect(parse(["--version"], "9.8.7")).toEqual({
    kind: "exit",
    code: 0,
    out: "lodge 9.8.7\n",
    err: "",
  }));
test("draft_help_says_decisions_are_immutable", () =>
  expect(parse(["draft", "-h"], "test")).toMatchObject({
    out: expect.stringMatching(/a\s+decision is immutable/u),
  }));

test.each([
  [["hook"], ""],
  [["hook", "--unknown", "extra"], "--unknown"],
  [["hook", "--version"], "--version"],
] as const)("hook_bypasses_other_parsing %p", (argv, event) => {
  expect(parse(argv, "test")).toEqual({ kind: "hook", event });
});
test("hook_help_and_summary_match_argparse", () => {
  expect(parse(["hook", "-h"], "test")).toMatchObject({
    code: 0,
    out: "usage: lodge hook [-h] EVENT\n\nanswer a Claude Code hook event: post-tool-use\n\npositional arguments:\n  EVENT\n\noptions:\n  -h, --help  show this help message and exit\n",
  });
  expect(parse(["--help"], "test")).toMatchObject({
    out: expect.stringContaining("hook      answer a Claude Code hook event: post-tool-use"),
  });
});
