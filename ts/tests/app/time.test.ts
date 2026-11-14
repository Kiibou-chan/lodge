import { expect, test } from "bun:test";
import { minuteOf, stampOf } from "#app";
import { instant, isStamp } from "#core";
import { START } from "./fakes.ts";

test("stamp_keeps_the_offset", () => {
  expect(stampOf(START)).toBe("2026-10-29T09:30:00+01:00");
  expect(isStamp(stampOf(START))).toBe(true);
});
test("stamp_drops_the_fraction", () => {
  expect(stampOf({ ...START, epochMs: START.epochMs + 999 })).toBe(stampOf(START));
});
test("negative_and_zero_offsets", () => {
  expect(stampOf({ ...START, offsetMinutes: -150 })).toBe("2026-10-29T06:00:00-02:30");
  expect(stampOf({ ...START, offsetMinutes: 0 })).toBe("2026-10-29T08:30:00+00:00");
});
test("minute_is_local_to_the_offset", () => {
  expect(minuteOf(START)).toBe("2026-10-29 09:30");
  expect(minuteOf({ ...START, offsetMinutes: 0 })).toBe("2026-10-29 08:30");
});
test("minute_crosses_midnight", () => {
  expect(minuteOf({ epochMs: instant("2026-10-29T23:59:00+00:00"), offsetMinutes: 60 })).toBe(
    "2026-10-30 00:59",
  );
});
