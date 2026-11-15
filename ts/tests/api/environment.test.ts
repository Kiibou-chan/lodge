import { expect, test } from "bun:test";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import ts from "typescript";
import { withoutYamlLogging } from "#api";

test("yaml_logging_variables_are_cleared", () => {
  const env: Record<string, string | undefined> = {
    LOG_TOKENS: "1",
    LOG_STREAM: "1",
    OTHER: "kept",
  };
  withoutYamlLogging(env);
  expect(env).toEqual({ OTHER: "kept" });
});
test("main_clears_yaml_logging_first", () => {
  const path = resolve(import.meta.dir, "../../src/main.ts");
  const source = ts.createSourceFile(
    path,
    readFileSync(path, "utf8"),
    ts.ScriptTarget.Latest,
    true,
  );
  const statement = source.statements.find(
    (node) => !ts.isImportDeclaration(node) && !ts.isImportEqualsDeclaration(node),
  );
  expect(statement).toBeDefined();
  if (!statement) throw new Error("main has no executable statement");
  expect(ts.isExpressionStatement(statement)).toBe(true);
  if (!ts.isExpressionStatement(statement)) throw new Error("first statement is not a call");
  const call = statement.expression;
  expect(ts.isCallExpression(call)).toBe(true);
  if (!ts.isCallExpression(call)) throw new Error("first expression is not a call");
  expect(call.expression.getText(source)).toBe("withoutYamlLogging");
  expect(call.arguments.map((argument) => argument.getText(source))).toEqual(["process.env"]);
});
