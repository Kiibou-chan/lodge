export function equal(a: unknown, b: unknown): boolean {
  if (a === b) return true;
  if (a instanceof Map || b instanceof Map) {
    if (!(a instanceof Map && b instanceof Map) || a.size !== b.size) return false;
    return [...a].every(([key, value]) => b.has(key) && equal(value, b.get(key)));
  }
  if (a instanceof Set || b instanceof Set) {
    if (!(a instanceof Set && b instanceof Set) || a.size !== b.size) return false;
    return [...a].every((value) => b.has(value));
  }
  if (Array.isArray(a) && Array.isArray(b))
    return a.length === b.length && a.every((v, i) => equal(v, b[i]));
  if (a !== null && b !== null && typeof a === "object" && typeof b === "object")
    return (
      Object.keys(a).length === Object.keys(b).length &&
      Object.entries(a).every(([k, v]) => Object.hasOwn(b, k) && equal(v, Reflect.get(b, k)))
    );
  return false;
}
