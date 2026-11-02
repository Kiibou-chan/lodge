import { expect, test } from "bun:test";
import { newestLast, parseThread, threadPath, writeThread } from "#core";
import { message, thread } from "./builders.ts";

test("escape_breaks_lines_at_newline_only", () => {
  const text = "x\u2028## Message 1\ny\r## Message 2";
  const t = thread({ messages: [message({ text })] });
  const written = writeThread(t);
  expect(written).toContain(text);
  expect(parseThread(threadPath(t.id), written)).toEqual(t);
});
test("newest_last_uses_instants_and_code_point_ids", () => {
  const a = thread({ id: "q-\ue000", opened: "2026-10-28T10:00:00+01:00" });
  const b = thread({ id: "q-\u{10000}", opened: "2026-10-28T09:00:00+00:00" });
  expect(newestLast([b, a])).toEqual([a, b]);
});
