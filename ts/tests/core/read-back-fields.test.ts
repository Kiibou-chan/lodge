import { expect, test } from "bun:test";
import { readFileSync } from "node:fs";
import ts from "typescript";
import { area, specEntry } from "#core";
import { message, thread } from "./builders.ts";
import { EXAMPLE } from "./samples.ts";

test("read_back_fields_cover_model", () => {
  const source = ts.createSourceFile(
    "read-back-fields.ts",
    readFileSync(new URL("../../src/core/read-back-fields.ts", import.meta.url), "utf8"),
    ts.ScriptTarget.Latest,
    true,
  );
  const lists = new Map<string, string[]>();
  function visit(node: ts.Node): void {
    if (ts.isPropertyAssignment(node) && ts.isArrayLiteralExpression(node.initializer)) {
      lists.set(
        node.name.getText(source),
        node.initializer.elements.map((item) => {
          if (!ts.isStringLiteral(item)) throw new Error("expected literal field name");
          return item.text;
        }),
      );
    }
    ts.forEachChild(node, visit);
  }
  visit(source);
  for (const record of [
    EXAMPLE,
    thread(),
    { kind: "message", ...message() },
    specEntry({ id: "s-4kq1zm", area: "storage", title: "T", statement: "S." }),
    area({ name: "storage", title: "T", intro: "", order: [] }),
  ]) {
    expect(lists.get(record.kind)?.sort()).toEqual(
      Object.keys(record)
        .filter((key) => key !== "kind")
        .sort(),
    );
  }
});
