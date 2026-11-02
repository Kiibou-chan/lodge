import ts from "typescript";

export function guardedCatch(node: ts.CatchClause): boolean {
  const name = node.variableDeclaration?.name;
  const first = node.block.statements[0];
  if (!name || !ts.isIdentifier(name) || !first || !ts.isIfStatement(first)) return false;
  const condition = first.expression;
  if (
    !ts.isPrefixUnaryExpression(condition) ||
    condition.operator !== ts.SyntaxKind.ExclamationToken
  )
    return false;
  const inner = ts.isParenthesizedExpression(condition.operand)
    ? condition.operand.expression
    : condition.operand;
  if (!ts.isBinaryExpression(inner) || inner.operatorToken.kind !== ts.SyntaxKind.InstanceOfKeyword)
    return false;
  const body = ts.isBlock(first.thenStatement)
    ? first.thenStatement.statements
    : [first.thenStatement];
  const thrown = body[0];
  return (
    ts.isIdentifier(inner.left) &&
    inner.left.text === name.text &&
    ts.isIdentifier(inner.right) &&
    body.length === 1 &&
    !!thrown &&
    ts.isThrowStatement(thrown) &&
    !!thrown.expression &&
    ts.isIdentifier(thrown.expression) &&
    thrown.expression.text === name.text
  );
}

export function fsImports(source: ts.SourceFile): (expr: ts.Expression) => string | undefined {
  const names = new Map<string, string>();
  const namespaces = new Set<string>();
  for (const node of source.statements) {
    if (
      !ts.isImportDeclaration(node) ||
      !ts.isStringLiteral(node.moduleSpecifier) ||
      !["fs", "node:fs", "fs/promises", "node:fs/promises"].includes(node.moduleSpecifier.text)
    )
      continue;
    const clause = node.importClause;
    if (!clause || clause.isTypeOnly) continue;
    if (clause.name) namespaces.add(clause.name.text);
    const bindings = clause.namedBindings;
    if (bindings && ts.isNamespaceImport(bindings)) namespaces.add(bindings.name.text);
    if (bindings && ts.isNamedImports(bindings)) {
      for (const item of bindings.elements) {
        if (item.isTypeOnly) continue;
        const original = (item.propertyName ?? item.name).text;
        if (original === "promises") namespaces.add(item.name.text);
        else names.set(item.name.text, original);
      }
    }
  }
  return (expr) => {
    if (ts.isIdentifier(expr)) return names.get(expr.text);
    if (!ts.isPropertyAccessExpression(expr)) return undefined;
    const receiver = expr.expression;
    if (ts.isIdentifier(receiver) && namespaces.has(receiver.text)) return expr.name.text;
    if (
      ts.isPropertyAccessExpression(receiver) &&
      receiver.name.text === "promises" &&
      ts.isIdentifier(receiver.expression) &&
      namespaces.has(receiver.expression.text)
    )
      return expr.name.text;
    return undefined;
  };
}

export function unsafePattern(node: ts.Node): boolean {
  let pattern: string;
  let flags: string;
  if (ts.isRegularExpressionLiteral(node)) {
    const end = node.text.lastIndexOf("/");
    pattern = node.text.slice(1, end);
    flags = node.text.slice(end + 1);
  } else if (
    (ts.isNewExpression(node) || ts.isCallExpression(node)) &&
    ts.isIdentifier(node.expression) &&
    node.expression.text === "RegExp"
  ) {
    const args = node.arguments;
    if (!args?.[0] || !ts.isStringLiteralLike(args[0])) return false;
    pattern = args[0].text;
    flags = args[1] && ts.isStringLiteralLike(args[1]) ? args[1].text : "";
  } else return false;
  return !flags.includes("u") || flags.includes("m") || /(?<!\\)(?:\\\\)*\\[swdb]/u.test(pattern);
}
