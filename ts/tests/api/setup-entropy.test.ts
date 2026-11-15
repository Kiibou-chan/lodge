import { expect, test } from "bun:test";
import { issueSetupCode } from "#api";
import { world } from "./world.ts";

test.each([
  [Array.from({ length: 13 }, (_, i) => i + 1), "04106-1050R-3GG28-A1C60"],
  [Array(13).fill(255), "ZZZZZ-ZZZZZ-ZZZZZ-ZZZZZ"],
  [[0, 68, 50, 20, 199, 66, 84, 182, 53, 207, 132, 101, 48], "01234-56789-ABCDE-FGHJK"],
  [[165, 109, 124, 103, 91, 231, 125, 240, 4, 67, 33, 76, 112], "MNPQR-STVWX-YZ012-34567"],
])("setup_code_uses_100_bits %p", async (bytes, expected) => {
  const w = await world();
  const lengths: number[] = [];
  expect(
    await issueSetupCode({
      ...w.options,
      random: (n) => {
        lengths.push(n);
        return new Uint8Array(bytes);
      },
    }),
  ).toBe(expected);
  expect(lengths).toEqual([13]);
  await w.database.close();
});
