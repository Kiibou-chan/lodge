import { expect } from "bun:test";
import { type Area, load, type Record, type Thread, tree } from "#core";
import { filesOf } from "./builders.ts";

export const IMPORTED = { file: "notes.md", heading: "A heading" };

export function snapshotOf(...records: (Record | Area | Thread)[]) {
  const snap = load(tree({ rev: null, files: filesOf(...records) }));
  expect(snap.problems).toEqual([]);
  return snap;
}
