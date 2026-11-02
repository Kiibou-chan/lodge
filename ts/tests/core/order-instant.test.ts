import { expect, test } from "bun:test";
import { instant, orderInstant, ValueError } from "#core";

test("order_instant_accepts_day_and_stamp", () => {
  expect(orderInstant("2026-10-29")).toBe(instant("2026-10-29T00:00:00+00:00"));
  expect(orderInstant("2026-10-29T00:30:00+00:00")).toBe(instant("2026-10-29T00:30:00+00:00"));
  expect(orderInstant("2026-10-29")).toBeLessThan(orderInstant("2026-10-29T00:30:00+00:00"));
  expect(orderInstant("2026-10-29")).toBeGreaterThan(orderInstant("2026-10-28T23:30:00+00:00"));
  expect(() => orderInstant("invalid")).toThrow(ValueError);
  expect(() => orderInstant("2026-02-30")).toThrow(ValueError);
});
