import { ApiError } from "./errors.ts";
export function isObject(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}
export class Args {
  constructor(
    readonly operation: string,
    readonly body: Record<string, unknown>,
  ) {}
  fail(field: string, what: string): never {
    throw new ApiError("usage", `${this.operation}: ${field} must be ${what}`);
  }
  known(names: readonly string[]): void {
    for (const name of Object.keys(this.body))
      if (!names.includes(name))
        throw new ApiError("usage", `${this.operation}: unknown field ${name}`);
  }
  string(name: string, fallback?: string): string {
    const v = this.body[name] === undefined ? fallback : this.body[name];
    if (typeof v !== "string") this.fail(name, "a string");
    return v;
  }
  nullable(name: string): string | null {
    const v = this.body[name] === undefined ? null : this.body[name];
    if (v !== null && typeof v !== "string") this.fail(name, "a string or null");
    return v;
  }
  boolean(name: string): boolean {
    const v = this.body[name] === undefined ? false : this.body[name];
    if (typeof v !== "boolean") this.fail(name, "a boolean");
    return v;
  }
  limit(fallback: number): number {
    const v = this.body["limit"] === undefined ? fallback : this.body["limit"];
    if (typeof v !== "number" || !Number.isInteger(v) || v < 1)
      this.fail("limit", "a whole number from 1");
    return v;
  }
  object(name: string, fallback?: Record<string, unknown>): Record<string, unknown> {
    const v = this.body[name] === undefined ? fallback : this.body[name];
    if (!isObject(v)) this.fail(name, "an object");
    return v;
  }
  pairs(name: string, optional = false): readonly (readonly [string, string])[] {
    const v = this.body[name] === undefined && optional ? [] : this.body[name];
    if (
      !Array.isArray(v) ||
      !v.every((p) => Array.isArray(p) && p.length === 2 && p.every((s) => typeof s === "string"))
    )
      this.fail(name, "a list of [name, text] pairs");
    return v;
  }
  choice<T extends string>(name: string, values: readonly T[], fallback?: T): T {
    const v = this.body[name] === undefined ? fallback : this.body[name];
    if (!values.includes(v as T)) this.fail(name, values.join(" or "));
    return v as T;
  }
}
