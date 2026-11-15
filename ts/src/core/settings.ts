import { ValueError } from "./errors.ts";
export class SettingsError extends ValueError {
  override name = "SettingsError";
}
export interface LengthGuidance {
  readonly titleChars: number;
  readonly decisionStatementWords: number;
  readonly specStatementWords: number;
  readonly reasoningWords: number;
}
export function lengthGuidance(value: Partial<LengthGuidance> = {}): LengthGuidance {
  return {
    titleChars: 100,
    decisionStatementWords: 80,
    specStatementWords: 150,
    reasoningWords: 1000,
    ...value,
  };
}
export interface CoreSettings {
  readonly length: LengthGuidance;
  readonly importSources: readonly string[];
}
export function coreSettings(value: Partial<CoreSettings> = {}): CoreSettings {
  return { length: lengthGuidance(), importSources: [], ...value };
}
function isTable(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}
function section(table: Readonly<Record<string, unknown>>, name: string): Record<string, unknown> {
  const value = Object.hasOwn(table, name) ? table[name] : {};
  if (!isTable(value)) throw new SettingsError(`${name} must be a table`);
  return value;
}
export function parseCoreSettings(table: Readonly<Record<string, unknown>>): CoreSettings {
  for (const [name, value] of Object.entries(table)) {
    if (["store", "hook", "length", "import"].includes(name)) continue;
    throw new SettingsError(isTable(value) ? `unknown section [${name}]` : `unknown key ${name}`);
  }
  const names = {
    title_chars: "titleChars",
    decision_statement_words: "decisionStatementWords",
    spec_statement_words: "specStatementWords",
    reasoning_words: "reasoningWords",
  } as const;
  const values: Partial<{ -readonly [K in keyof LengthGuidance]: number }> = {};
  for (const [key, value] of Object.entries(section(table, "length"))) {
    if (!Object.hasOwn(names, key)) throw new SettingsError(`unknown key length.${key}`);
    if (typeof value !== "number" || !Number.isInteger(value) || value < 1)
      throw new SettingsError(`length.${key} must be a positive whole number`);
    values[names[key as keyof typeof names]] = value;
  }
  const imports = section(table, "import");
  for (const key of Object.keys(imports))
    if (key !== "sources") throw new SettingsError(`unknown key import.${key}`);
  const { sources = [] } = imports;
  if (!Array.isArray(sources) || !sources.every((s) => typeof s === "string" && s !== ""))
    throw new SettingsError("import.sources must be a list of file names");
  return coreSettings({ length: lengthGuidance(values), importSources: [...sources] });
}
