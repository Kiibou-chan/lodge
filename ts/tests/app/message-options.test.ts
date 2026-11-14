import { expect, test } from "bun:test";
import type { Lodge } from "#app";
import { ThreadState } from "#core";
import { opened } from "./support.ts";

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

test("reply_ignores_a_runtime_close_option", async () => {
  const { lodge } = await opened();
  const result = await lodge.reply("q-111111", "coordinator", "Because.", { close: true } as never);
  expect(result.outcome).toBe("published");
  expect((await lodge.thread("q-111111")).thread.state).toBe(ThreadState.OPEN);
});
