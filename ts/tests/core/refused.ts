import { expect } from "bun:test";
export function refused(
  write: () => unknown,
  errorClass: new (...args: never[]) => Error,
  pattern: RegExp,
): void {
  let caught: unknown;
  try {
    write();
  } catch (error) {
    caught = error;
  }
  expect(caught).toBeInstanceOf(errorClass);
  expect((caught as Error).message).toMatch(pattern);
}
