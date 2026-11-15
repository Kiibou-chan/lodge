import { expect, test } from "bun:test";
import { splitLines } from "#core";
import { project } from "./project.ts";
import { initialise } from "./support.ts";

const OLD = `---
kind: decision
title: "Keep old transcripts"
scope: product
decided_by: author
date: 2026-01-05
imported_from: {file: docs/choices.md, heading: "ITEM-9"}
---

Old transcripts are kept.
`;
test("import_needs_the_flag_and_a_listed_source", async () => {
  const p = await project();
  p.configure('[import]\nsources = ["docs/choices.md"]\n');
  await initialise(p);
  const path = p.draft("old.md", OLD);
  const refused = await p.run("add", path);
  expect(refused.code).toBe(2);
  expect(refused.err).toContain("imported_from");
  const added = await p.run("add", "--import", path);
  expect([added.code, added.err]).toEqual([0, ""]);
  const held = splitLines(added.out)
    .at(-1)
    ?.match(
      /^held for approval by author as hold (\d+); nothing is current until they approve it$/u,
    );
  expect(held).toBeDefined();
  expect(held).not.toBeNull();
  const ids = await p.approve(Number(held?.[1]));
  const id = ids.find((id) => id.startsWith("d-"));
  expect(id).toBeDefined();
  const shown = await p.run("show", id ?? "");
  expect(shown.out).toContain("imported");
  expect(shown.out).toContain("unquoted");
});
test("import_from_an_unlisted_source_fails_the_check", async () => {
  const p = await project();
  await initialise(p);
  const r = await p.run("add", "--import", p.draft("old.md", OLD));
  expect(r.code).toBe(1);
  expect(splitLines(r.out).at(-1)).toBe("not published: the check failed");
});
