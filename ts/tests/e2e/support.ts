import { expect } from "bun:test";
import { splitLines } from "#core";
import type { Project } from "./project.ts";
export const QUOTE = 'quote: {text: "Keep them.", where: "chat", when: "2026-10-29 10:00"}';
export function document(header: readonly string[], body: string): string {
  return `---\n${header.join("\n")}\n---\n\n${body}\n`;
}
export function decisionText(
  title = "Keep transcripts",
  extra: readonly string[] = [],
  { decidedBy = "coordinator", body = "Transcripts are kept." } = {},
): string {
  return document(
    ["kind: decision", `title: "${title}"`, "scope: product", `decided_by: ${decidedBy}`, ...extra],
    body,
  );
}
export function entryText(entry: string, title = "Transcripts are kept", body = "Held."): string {
  return document(["kind: spec", `id: ${entry}`, "area: storage", `title: "${title}"`], body);
}
export function areaText(...order: string[]): string {
  return document(
    ["kind: area", "name: storage", 'title: "Storage"', `order: [${order.join(", ")}]`],
    "How data is kept.",
  );
}
export function firstDecision(out: string): string {
  const id = splitLines(out)
    .at(-1)
    ?.split(" ")
    .find((w) => w.startsWith("d-"));
  if (!id) throw new Error(out);
  return id;
}
export async function initialise(p: Project): Promise<void> {
  expect((await p.run("init")).code).toBe(0);
}
export async function seed(
  p: Project,
  extra: readonly string[] = [],
  { decidedBy = "coordinator", code = "ITEM-1" } = {},
) {
  await initialise(p);
  const entry = (await p.run("id", "s")).out.trim();
  const added = await p.run(
    "add",
    p.draft(
      "decision.md",
      decisionText(
        "Keep transcripts",
        [`code: ${code}`, "changes:", `  - {entry: ${entry}, action: create}`, ...extra],
        { decidedBy },
      ),
    ),
    p.draft("entry.md", entryText(entry)),
    p.draft("area.md", areaText(entry)),
  );
  expect(added.code, added.err + added.out).toBe(0);
  if (decidedBy === "author") {
    expect(added.err).toBe("");
    const held = splitLines(added.out)
      .at(-1)
      ?.match(
        /^held for approval by author as hold (\d+); nothing is current until they approve it$/u,
      );
    expect(held).not.toBeNull();
    const ids = await p.approve(Number(held?.[1]));
    const decision = ids.find((id) => id.startsWith("d-"));
    if (!decision) throw new Error("approval has no decision");
    return { decision, entry };
  }
  return { decision: firstDecision(added.out), entry };
}
