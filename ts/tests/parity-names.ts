import ts from "typescript";
export function pythonTestNames(text: string): string[] {
  return [...text.matchAll(/^\s*(?:async\s+)?def test_(\w+)\s*\(/gmu)].map((m) => m[1] as string);
}
function titles(text: string, todoOnly: boolean): string[] {
  const found: string[] = [];
  const source = ts.createSourceFile("tests.ts", text, ts.ScriptTarget.Latest, true);
  function visit(node: ts.Node): void {
    if (ts.isCallExpression(node)) {
      const expr = node.expression;
      const base = ts.isCallExpression(expr) ? expr.expression : expr;
      const todo = ts.isPropertyAccessExpression(base) && base.name.text === "todo";
      const name = ts.isPropertyAccessExpression(base)
        ? base.expression.getText(source)
        : base.getText(source);
      const each =
        ts.isCallExpression(expr) &&
        ts.isPropertyAccessExpression(base) &&
        base.name.text === "each";
      const direct = ts.isIdentifier(expr) || todo;
      if ((name === "test" || name === "it") && (each || direct) && (!todoOnly || todo)) {
        const arg = node.arguments[0];
        if (arg && ts.isStringLiteralLike(arg)) found.push(arg.text);
      }
    }
    ts.forEachChild(node, visit);
  }
  visit(source);
  return found;
}
export function typescriptTestTitles(text: string): string[] {
  return titles(text, false);
}
export function todoTitles(text: string): string[] {
  return titles(text, true);
}
export function missingNames(python: string, typescript: string): string[] {
  const available = typescriptTestTitles(typescript);
  return pythonTestNames(python).filter(
    (name) => !available.some((t) => t === name || t.startsWith(`${name} `)),
  );
}
