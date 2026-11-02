import { expect, test } from "bun:test";
import { compareStamps, instant, isDay, isStamp, ValueError } from "#core";

test("stamp_with_offset_is_a_stamp", () => expect(isStamp("2026-10-29T12:00:00+01:00")).toBe(true));
test("stamp_without_offset_or_seconds_is_not", () => {
  for (const s of ["2026-10-29T12:00+01:00", "2026-10-29T12:00:00", "2026-10-29T12:00:00Z"])
    expect(isStamp(s)).toBe(false);
});
test("impossible_date_is_not_a_stamp", () => {
  for (const s of [
    "2026-02-30T10:00:00+01:00",
    "2026-10-29T24:00:00+01:00",
    "0000-01-01T00:00:00+01:00",
  ])
    expect(isStamp(s)).toBe(false);
});
test("offset_is_read_as_python_reads_it", () => {
  for (const offset of ["+00:60", "+22:99"])
    expect(isStamp(`2026-10-29T12:00:00${offset}`)).toBe(true);
  for (const offset of ["+23:60", "+24:00", "-23:99"])
    expect(isStamp(`2026-10-29T12:00:00${offset}`)).toBe(false);
});
test("instant_respects_the_offset", () => {
  expect(instant("2026-10-29T12:00:00+01:00")).toBe(instant("2026-10-29T11:00:00+00:00"));
  expect(instant("0001-01-01T00:00:00+00:00")).toBe(-62135596800000);
});
test("compare_orders_by_instant", () => {
  expect(compareStamps("2026-10-29T11:00:00+00:00", "2026-10-29T12:00:01+01:00")).toBeLessThan(0);
  expect(compareStamps("2026-10-29T12:00:00+01:00", "2026-10-29T11:00:00+00:00")).toBe(0);
  expect(compareStamps("2026-10-29T12:00:01+01:00", "2026-10-29T11:00:00+00:00")).toBeGreaterThan(
    0,
  );
});
test("day_must_be_real", () => {
  expect(isDay("1900-02-29")).toBe(false);
  expect(isDay("2000-02-29")).toBe(true);
  expect(isDay("2024-02-29")).toBe(true);
  for (const s of ["2026-02-29", "0000-01-01", "2026-13-01", "2026-01-00"])
    expect(isDay(s)).toBe(false);
});
test("stamp_check_ignores_the_local_time_zone", () => {
  const old = process.env.TZ;
  try {
    process.env.TZ = "Europe/Berlin";
    expect(isStamp("2026-03-29T02:30:00+01:00")).toBe(true);
    expect(instant("2026-03-29T02:30:00+01:00")).toBe(instant("2026-03-29T01:30:00+00:00"));
  } finally {
    if (old === undefined) delete process.env.TZ;
    else process.env.TZ = old;
  }
});
test("instant_refuses_non_stamp", () => expect(() => instant("invalid")).toThrow(ValueError));
