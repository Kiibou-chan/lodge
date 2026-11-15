import { expect, test } from "bun:test";
import { mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { splitLines } from "#core";
import { project } from "./project.ts";

test("guide", async () => {
  const p = await project();
  const plain = join(p.root, "..", "plain");
  mkdirSync(plain);
  const r = await p.runIn(plain, "guide");
  expect([r.code, r.err]).toEqual([0, ""]);
  expect(r.out).toBe(readFileSync(new URL("../../src/cli/guide.md", import.meta.url), "utf8"));
});
test("guide_is_short_and_covers_the_write_path", async () => {
  const text = (await (await project()).run("guide")).out;
  expect(splitLines(text).length).toBeLessThanOrEqual(60);
  expect(text).not.toContain("—");
  for (const phrase of [
    "lodge id s",
    "lodge draft",
    "lodge add --dry-run",
    "lodge/attachments/<decision id>/<name>",
    "lodge add --attach PATH FILE...",
    "Then `add` sends them to the server, which checks them and makes them current at once; nothing is staged or committed.",
    "held for approval",
    "replaces: [d-xxxxxx]",
    "quote: {text, where, when}",
    "never edit",
  ])
    expect(text.replace("Never edit", "never edit")).toContain(phrase);
});
test("guide_names_the_author_not_a_person", async () => {
  expect((await (await project()).run("guide")).out).not.toMatch(/\b(her|hers|she)\b/iu);
});
test("guide_names_rests_on_and_link", async () => {
  const out = (await (await project()).run("guide")).out;
  for (const s of [
    "rests_on",
    "action `link`",
    "\n\n```\n---",
    "Transcripts are kept whole.\n```\n\n",
  ])
    expect(out).toContain(s);
});
test("guide_says_waiting_first", async () => {
  const text = (await (await project()).run("guide")).out;
  for (const s of [
    "Run `lodge waiting` at the start of a session, and answer what waits for an agent first.",
    "`lodge threads` lists the open doubts and questions, and `lodge thread Q` shows one.",
    "close a thread only when the author asked for it.",
    "Write `--by author` only with the author's words verbatim, with `--where` and `--when`.",
  ])
    expect(text).toContain(s);
});
test("guide_restores_introduction_and_heading_spacing", async () => {
  const text = (await (await project()).run("guide")).out;
  expect(text).toContain("lodge holds a project's decisions and specification entries.");
  expect(text).toContain(
    "An area is a named group with a title, an intro, and the order of its entries.",
  );
  const lines = splitLines(text);
  for (let i = 0; i < lines.length; i++)
    if (lines[i]?.startsWith("#")) expect(lines[i + 1]).toBe("");
  expect(lines.length).toBeLessThanOrEqual(60);
});
