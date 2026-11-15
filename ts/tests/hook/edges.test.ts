import { expect, test } from "bun:test";
import { respond, run } from "#hook";
import { context, payload, resolve, text } from "./support.ts";

const root = "/synthetic/project";
test("glob_literals_and_unicode_match_the_whole_path", () => {
  for (const name of ["docs/a+b[1].md", "docs/(choice)$.md", "docs/{choice}^.md", "docs/🐈.md"])
    expect(text(respond(payload(name), context(root, null, [name]), resolve))).toContain(name);
  expect(
    respond(payload("docs/🐈.md"), context(root, null, ["docs/?.md"]), resolve),
  ).not.toBeNull();
  expect(respond(payload("docs/a.md\n"), context(root, null, ["docs/a.md"]), resolve)).toBeNull();
  expect(
    respond(payload("docs/deep/a.md"), context(root, null, ["docs/**.md"]), resolve),
  ).not.toBeNull();
});
test("run_silences_output_and_resolution_failures", async () => {
  const read = async () => JSON.stringify(payload("lodge/spec/area/_area.md"));
  expect(
    await run(
      read,
      () => {
        throw new Error("closed output");
      },
      async () => context(root),
      resolve,
      root,
    ),
  ).toBe(0);
  let output = "";
  expect(
    await run(
      read,
      (value) => {
        output += value;
      },
      async () => context(root),
      () => {
        throw new Error("unresolvable");
      },
      root,
    ),
  ).toBe(0);
  expect(output).toBe("");
});
test("glob_escape_set_and_question_mark_do_not_overreach", () => {
  for (const [pattern, path] of [
    ["docs/a.md", "docs/aXmd"],
    ["docs/a|b.md", "docs/a"],
    ["docs/a|b.md", "docs/b.md"],
    ["docs/a\\b.md", "docs/ab.md"],
    ["docs?x.md", "docs/x.md"],
  ])
    expect(respond(payload(path ?? ""), context(root, null, [pattern ?? ""]), resolve)).toBeNull();
  const name = "docs/a\\b.md";
  expect(text(respond(payload(name), context(root, null, [name]), resolve))).toContain(name);
});
test("record_path_outside_the_repository_is_shown_absolute", () => {
  const path = "/synthetic/elsewhere/decisions/d-abc123-slug.md";
  expect(text(respond(payload(path), context(root, "/synthetic/elsewhere"), resolve))).toContain(
    path,
  );
});
