export function toWire(value: unknown): unknown {
  if (value === null || typeof value === "boolean" || typeof value === "string") return value;
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (Array.isArray(value)) return value.map(toWire);
  if (value instanceof Map) return { $map: [...value].map(([k, v]) => [toWire(k), toWire(v)]) };
  if (value instanceof Set) return { $set: [...value].map(toWire) };
  if (typeof value === "object") {
    if (Object.hasOwn(value, "$map") || Object.hasOwn(value, "$set"))
      throw new TypeError("reserved wire key");
    return Object.fromEntries(
      Object.entries(value)
        .filter(([, v]) => v !== undefined)
        .map(([k, v]) => [k, toWire(v)]),
    );
  }
  throw new TypeError("unsupported wire value");
}
