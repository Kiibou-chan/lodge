import { expect, test } from "bun:test";
import type { Lodge } from "#app";

test("public_message_options_do_not_expose_close", () => {
  // @ts-expect-error close is internal to the thread writer.
  const ask: Parameters<Lodge["ask"]>[4] = { close: true };
  // @ts-expect-error close is internal to the thread writer.
  const reply: Parameters<Lodge["reply"]>[3] = { close: true };
  // @ts-expect-error Lodge.close supplies its own close flag.
  const close: Parameters<Lodge["close"]>[2] = { close: true };
  expect([ask, reply, close].map((options) => Object.keys(options ?? {}))).toEqual([
    ["close"],
    ["close"],
    ["close"],
  ]);
});
