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
      throw new YamlError(`unreadable character ${pyRepr(ch)}`, line);
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
    uniqueKeys: true,
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
  const document = doc;
  function walk(node: unknown, depth: number): unknown {
    if (depth >= 100 && !isScalar(node) && node !== null)
      throw new YamlError("the header is nested too deeply");
    if (node === null) return null;
    if (isAlias(node)) {
      const target = node.resolve(document);
      if (!target) throw new YamlError("found undefined alias", lineAt(node.range?.[0] ?? 0));
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
    if (isScalar(node)) return node.value === null ? "" : String(node.value);
    if (isSeq(node)) return node.items.map((item) => walk(item, depth + 1));
    const result = new Map<string, unknown>();
    for (const pair of node.items) {
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
  // Walk before package diagnostics so duplicate keys retain Python's message.
  const result = walk(doc.contents, 0);
  const error = doc.errors[0];
  if (error) throw new YamlError(error.message, lineAt(error.pos[0]));
  return result;
}
