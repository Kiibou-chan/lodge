import { CliError } from "./errors.ts";
import { tomlTable } from "./settings.ts";

export function zeroTwoCoreTable(text: string): Readonly<Record<string, unknown>> {
  if (/[\uDC80-\uDCFF]/u.test(text)) throw new CliError(".lodge.toml: cannot be read: not UTF-8");
  return Object.fromEntries(
    Object.entries(tomlTable(text)).filter(([name]) => name === "length" || name === "import"),
  );
}
