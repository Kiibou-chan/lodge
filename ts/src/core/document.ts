import { FormatError } from "./fields.ts";
import { type Problem, problem } from "./model.ts";
import { rstrip, strip } from "./text.ts";
import { loadYaml, YamlError } from "./yamlio.ts";

export const REASONING_HEADING = "## Reasoning";
export function normaliseNewlines(text: string): string {
  return text.replaceAll("\r\n", "\n");
}
export function splitDocument(text: string): readonly [string, string] {
  for (const char of text) {
    const n = char.codePointAt(0);
    if (n !== undefined && n >= 0xd800 && n <= 0xdfff)
      throw new FormatError("the text is not valid UTF-8");
  }
  const lines = normaliseNewlines(text).split("\n");
  if (lines[0] !== "---")
    throw new FormatError("the file must start with a --- line opening its header");
  for (let index = 1; index < lines.length; index++)
    if (lines[index] === "---")
      return [lines.slice(1, index).join("\n"), lines.slice(index + 1).join("\n")];
  throw new FormatError("the header is not closed by a --- line");
}
export function loadHeader(headerText: string): ReadonlyMap<string, unknown> {
  let loaded: unknown;
  try {
    loaded = loadYaml(headerText);
  } catch (error) {
    if (!(error instanceof YamlError)) throw error;
    throw new FormatError(
      `the header is not valid YAML: ${error.message}`,
      null,
      error.line === null ? null : error.line + 1,
    );
  }
  if (!(loaded instanceof Map))
    throw new FormatError("the header must be a mapping of keys to values");
  return new Map([...loaded].map(([key, value]) => [String(key), value]));
}
export function hasReasoningHeading(text: string): boolean {
  return text.split("\n").some((line) => rstrip(line) === REASONING_HEADING);
}
// Leading blank lines and trailing whitespace go; indentation stays.
export function trimBlock(text: string): string {
  const lines = text.split("\n");
  while (lines[0] !== undefined && !strip(lines[0])) lines.shift();
  return rstrip(lines.join("\n"));
}
export function splitReasoning(body: string): readonly [string, string] {
  const lines = body.split("\n");
  const index = lines.findIndex((line) => rstrip(line) === REASONING_HEADING);
  return index < 0
    ? [trimBlock(body), ""]
    : [trimBlock(lines.slice(0, index).join("\n")), trimBlock(lines.slice(index + 1).join("\n"))];
}
export function assemble(header: readonly string[], body: string): string {
  const text = `---\n${header.join("\n")}\n---\n`;
  return body ? `${text}\n${body}\n` : text;
}
export function readWith<T>(
  path: string,
  text: string,
  build: (header: ReadonlyMap<string, unknown>, body: string) => T,
): T | Problem {
  let headerText = "";
  try {
    const [header, body] = splitDocument(text);
    headerText = header;
    return build(loadHeader(headerText), body);
  } catch (error) {
    if (!(error instanceof FormatError)) throw error;
    return problemFor(path, error, headerText);
  }
}
export function problemFor(path: string, error: FormatError, headerText: string): Problem {
  return problem({
    path,
    check: 1,
    message: error.message,
    line: error.line ?? keyLine(headerText, error.key),
  });
}
// A dotted key uses its first part; add two for the opening fence and one-based lines.
export function keyLine(headerText: string, key: string | null): number | null {
  if (key === null) return null;
  const top = key.split(".")[0];
  const index = headerText.split("\n").findIndex((line) => line.startsWith(`${top}:`));
  return index < 0 ? null : index + 2;
}
