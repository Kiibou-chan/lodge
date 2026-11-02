import { pyRepr } from "./text.ts";

export function valueRepr(value: unknown, sequence: "list" | "tuple" = "list"): string {
  if (typeof value === "string") return pyRepr(value);
  if (value === null) return "None";
  if (value === true) return "True";
  if (value === false) return "False";
  if (Array.isArray(value)) {
    const items = value.map((item) => valueRepr(item, sequence)).join(", ");
    return sequence === "tuple" ? `(${items}${value.length === 1 ? "," : ""})` : `[${items}]`;
  }
  if (value instanceof Map)
    return `{${[...value].map(([key, item]) => `${valueRepr(key)}: ${valueRepr(item)}`).join(", ")}}`;
  if (typeof value === "object") {
    const get = (key: string) => valueRepr(Reflect.get(value, key), sequence);
    if ("entry" in value && "action" in value)
      return `Change(entry=${get("entry")}, action=<Action.${String(value.action).toUpperCase()}: ${get("action")}>)`;
    if ("text" in value && "where" in value && "when" in value)
      return `Quote(text=${get("text")}, where=${get("where")}, when=${get("when")})`;
    if ("value" in value && "handle" in value)
      return `NumberHandle(value=${get("value")}, handle=${get("handle")})`;
    if ("file" in value && "heading" in value)
      return `Imported(file=${get("file")}, heading=${get("heading")})`;
  }
  return String(value);
}
