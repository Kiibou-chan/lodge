import { CST, isAlias, isMap, isScalar, isSeq, Lexer, LineCounter, parseAllDocuments } from "yaml";
import { ValueError } from "./errors.ts";
import { pyRepr } from "./text.ts";
export const LINE_BREAKS_AND_TABS = "\t\n\r";
export class YamlError extends ValueError {
  override name = "YamlError";
  constructor(
    message: string,
    readonly line: number | null = null,
  ) {
    super(message);
  }
}
export function unreadableChar(text: string, allowed = ""): string | null {
  for (const ch of text) {
    const cp = ch.codePointAt(0) as number;
    if (
      (cp < 32 ||
        (cp >= 127 && cp <= 159) ||
        cp === 8232 ||
        cp === 8233 ||
        (cp >= 0xd800 && cp <= 0xdfff) ||
        cp === 0xfffe ||
        cp === 0xffff) &&
      !allowed.includes(ch)
    )
      return ch;
  }
  return null;
}
export function quoted(text: string, allowed = ""): string {
  const bad = unreadableChar(text, allowed);
  if (bad !== null)
    throw new ValueError(
      `U+${(bad.codePointAt(0) as number).toString(16).toUpperCase().padStart(4, "0")} cannot be written in a header`,
    );
  return JSON.stringify(text);
}
function checkReader(text: string): void {
  let line = 1;
  for (const ch of text) {
    const cp = ch.codePointAt(0) as number;
    if (
      !(
        cp === 9 ||
        cp === 10 ||
        cp === 13 ||
        (cp >= 32 && cp <= 126) ||
        cp === 133 ||
        (cp >= 160 && cp <= 0xd7ff) ||
        (cp >= 0xe000 && cp <= 0xfffd) ||
        cp >= 0x10000
      )
    )
      throw new YamlError(`unreadable character ${cp}`, line);
    if (ch === "\n") line++;
  }
}
function pythonAliasKeys(text: string): string {
  let result = "",
    scalar = false;
  for (const token of new Lexer().lex(text)) {
    if (token === CST.SCALAR) {
      scalar = true;
      continue;
    }
    if (token === CST.DOCUMENT || token === CST.FLOW_END) continue;
    // PyYAML ends alias names before a mapping colon.
    result +=
      !scalar && CST.tokenType(token) === "alias" && token.endsWith(":")
        ? `${token.slice(0, -1)} :`
        : token;
    scalar = false;
  }
  return result;
}
export function loadYaml(text: string): unknown {
  checkReader(text);
  const lines = new LineCounter();
  const docs = parseAllDocuments(pythonAliasKeys(text), {
    schema: "failsafe",
    uniqueKeys: false,
    prettyErrors: false,
    lineCounter: lines,
  });
  const lineAt = (pos: number) => lines.linePos(pos).line;
  if (docs.length > 1)
    throw new YamlError(
      "expected a single document in the stream",
      lineAt(docs[1]?.range?.[0] ?? 0),
    );
  const doc = docs[0];
  if (!doc) return null;
  const error = doc.errors[0];
  if (error) {
    // A compact scalar used as a multiline mapping key ends at the offending colon.
    const key =
      error.code === "BLOCK_AS_IMPLICIT_KEY"
        ? doc.errors.find(
            (other) => other.code === "MULTILINE_IMPLICIT_KEY" && other.pos[0] === error.pos[0],
          )
        : undefined;
    const implicitKey =
      error.code === "MULTILINE_IMPLICIT_KEY" ||
      (error.code === "MISSING_CHAR" && error.message.startsWith("Implicit map keys"));
    let position = key?.pos[1] ?? (implicitKey ? error.pos[1] : error.pos[0]);
    if (implicitKey && text[position] === "\n") position++;
    throw new YamlError(error.message, lineAt(position));
  }
  const document = doc;
  const built = new Map<unknown, unknown>();
  function walk(node: unknown, depth: number): unknown {
    if (built.has(node)) return built.get(node);
    if (depth >= 100 && !isScalar(node) && node !== null)
      throw new YamlError("the header is nested too deeply");
    if (node === null) return null;
    if (isAlias(node)) {
      const target = node.resolve(document);
      if (!target)
        throw new YamlError(
          `found undefined alias ${pyRepr(node.source)}`,
          lineAt(node.range?.[0] ?? 0),
        );
      return walk(target, depth);
    }
    if (!isScalar(node) && !isMap(node) && !isSeq(node))
      throw new YamlError("tag or alias cannot be constructed");
    const line = lineAt(node.range?.[0] ?? 0);
    const tag = node.tag;
    if (
      tag &&
      tag !== "!" &&
      !(tag === "tag:yaml.org,2002:str" && isScalar(node)) &&
      !(tag === "tag:yaml.org,2002:seq" && isSeq(node)) &&
      !(tag === "tag:yaml.org,2002:map" && isMap(node))
    )
      throw new YamlError(`unsupported tag ${tag}`, line);
    if (isScalar(node)) {
      const value = node.value === null ? "" : String(node.value);
      built.set(node, value);
      return value;
    }
    if (isSeq(node)) {
      const result: unknown[] = [];
      built.set(node, result);
      for (const item of node.items) result.push(walk(item, depth + 1));
      return result;
    }
    const result = new Map<string, unknown>();
    built.set(node, result);
    for (const pair of node.items) {
      if (isAlias(pair.key) && !pair.key.resolve(document))
        throw new YamlError(
          `found undefined alias ${pyRepr(pair.key.source)}`,
          lineAt(pair.key.range?.[0] ?? 0),
        );
      const keyNode = isAlias(pair.key) ? pair.key.resolve(document) : pair.key;
      if (!isScalar(keyNode))
        throw new YamlError(
          "found unhashable key",
          isMap(pair.key) || isSeq(pair.key) || isAlias(pair.key)
            ? lineAt(pair.key.range?.[0] ?? 0)
            : line,
        );
      const key = walk(keyNode, depth + 1) as string;
      if (result.has(key))
        throw new YamlError(`duplicate key ${pyRepr(key)}`, lineAt(keyNode.range?.[0] ?? 0));
      result.set(key, pair.value === null ? "" : walk(pair.value, depth + 1));
    }
    return result;
  }
  return walk(doc.contents, 0);
}
