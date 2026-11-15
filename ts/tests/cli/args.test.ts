import { expect, test } from "bun:test";
import { parse } from "#cli";

test("options_before_between_and_after_positionals", () => {
  for (const argv of [
    ["show", "--reasoning", "d-aaaaaa", "--provenance"],
    ["show", "d-aaaaaa", "--reasoning", "--provenance"],
  ])
    expect(parse(argv, "test")).toEqual({
      kind: "show",
      ref: "d-aaaaaa",
      reasoning: true,
      provenance: true,
    });
});
test("equals_form", () =>
  expect(parse(["search", "--limit=3"], "test")).toMatchObject({ limit: 3 }));
test("double_dash_ends_options", () =>
  expect(parse(["show", "--", "-x"], "test")).toMatchObject({ ref: "-x" }));
test("unique_prefix_is_the_option", () =>
  expect(parse(["show", "d-aaaaaa", "--prov"], "test")).toMatchObject({ provenance: true }));
test("ambiguous_prefix_is_an_error", () =>
  expect(parse(["search", "x", "--s", "y"], "test")).toMatchObject({
    code: 2,
    err: expect.stringContaining("ambiguous option: --s could match --scope, --status"),
  }));
test("repeatable_option_collects", () =>
  expect(parse(["add", "f", "--attach", "a", "--attach", "b"], "test")).toMatchObject({
    attachments: ["a", "b"],
  }));
test("missing_value_is_an_error", () =>
  expect(parse(["search", "--kind"], "test")).toMatchObject({
    code: 2,
    err: expect.stringContaining("argument --kind: expected one argument"),
  }));
test("extra_words_are_an_error", () =>
  expect(parse(["thread", "q-aaaaaa", "extra"], "test")).toEqual({
    kind: "exit",
    code: 2,
    out: "",
    err: "usage: lodge [-h] [--version] COMMAND ...\nlodge: error: unrecognized arguments: extra\n",
  }));

test("unknown_top_level_option_is_not_discarded", () => {
  expect(parse(["--unknown", "show", "d-aaaaaa"], "test")).toMatchObject({
    code: 2,
    err: "usage: lodge [-h] [--version] COMMAND ...\nlodge: error: unrecognized arguments: --unknown\n",
  });
});
test("extra_arguments_keep_their_order", () => {
  expect(parse(["show", "d-aaaaaa", "extra", "--unknown"], "test")).toMatchObject({
    code: 2,
    err: "usage: lodge [-h] [--version] COMMAND ...\nlodge: error: unrecognized arguments: extra --unknown\n",
  });
});
test("help_flag_rejects_an_explicit_value", () => {
  expect(parse(["show", "--help=x"], "test")).toMatchObject({
    code: 2,
    err: "usage: lodge show [-h] [--reasoning] [--provenance] ref\nlodge show: error: argument -h/--help: ignored explicit argument 'x'\n",
  });
});

test("double_dash_is_leftover_without_positionals", () => {
  expect(parse(["init", "--", "-x"], "test")).toMatchObject({
    code: 2,
    err: "usage: lodge [-h] [--version] COMMAND ...\nlodge: error: unrecognized arguments: -- -x\n",
  });
});
