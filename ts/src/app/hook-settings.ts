import { LodgeError } from "./errors.ts";

export function parseHookSettings(table: unknown): readonly string[] {
  if (typeof table !== "object" || table === null || Array.isArray(table))
    throw new LodgeError(".lodge.toml: hook must be a table");
  for (const key of Object.keys(table)) {
    if (key !== "frozen") throw new LodgeError(`.lodge.toml: unknown key hook.${key}`);
  }
  const frozen = "frozen" in table ? table.frozen : [];
  if (!Array.isArray(frozen) || !frozen.every((glob) => typeof glob === "string"))
    throw new LodgeError(".lodge.toml: hook.frozen must be a list of strings");
  return [...frozen];
}
