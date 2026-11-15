import { expect, test } from "bun:test";
import { checkChange, checkState, load, parseCoreSettings, tree } from "#core";
import { ZERO_TWO_STORE } from "./zero-two-store.ts";

function storeTree() {
  const files = new Map<string, string>();
  const attachments = new Set<string>();
  for (const [path, text] of ZERO_TWO_STORE) {
    if (!path.startsWith("lodge/")) continue;
    if (path.startsWith("lodge/attachments/")) attachments.add(path);
    else files.set(path, text);
  }
  return tree({ rev: null, files, attachments });
}

test("zero_two_store_checks_clean", () => {
  const after = load(storeTree());
  expect(checkState(after).problems).toEqual([]);
  const settings = parseCoreSettings(
    Bun.TOML.parse(ZERO_TWO_STORE.get(".lodge.toml") as string) as Record<string, unknown>,
  );
  const empty = load(tree({ rev: null, files: new Map() }));
  expect(checkChange(empty, after, settings, "2026-11-03T00:00:00+00:00").problems).toEqual([]);
});
