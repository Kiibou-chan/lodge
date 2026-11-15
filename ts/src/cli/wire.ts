export function fromWire(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(fromWire);
  if (value !== null && typeof value === "object") {
    const obj = value as Record<string, unknown>;
    if (Array.isArray(obj["$map"]))
      return new Map(
        obj["$map"].map((pair) => {
          const [key, item] = pair as unknown[];
          return [fromWire(key), fromWire(item)];
        }),
      );
    if (Array.isArray(obj["$set"])) return new Set(obj["$set"].map(fromWire));
    return Object.fromEntries(Object.entries(obj).map(([key, item]) => [key, fromWire(item)]));
  }
  return value;
}
