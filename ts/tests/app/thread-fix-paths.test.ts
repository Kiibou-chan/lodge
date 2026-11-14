import { expect, test } from "bun:test";
import { Raises } from "#core";
import { project, wired } from "./support.ts";

test.todo("orphaned_thread_outputs");
test.todo("run_thread_outcomes");
test("waiting_reads_one_snapshot", async () => {
  const store = project(),
    lodge = wired(store);
  await lodge.ask("s-aaaaaa", Raises.DOUBT, "agent", "Why?");
  const path = "lodge/threads/q-111111.md";
  store.movesAfterRead(
    new Map([[path, required(store.files.get(path)).replace("agent", "author")]]),
  );
  const [listed, waiting] = await lodge.waitingAll();
  expect(listed.read).toBe(waiting.read);
  expect(waiting.forAuthor.map((t) => t.id)).toEqual(["q-111111"]);
  expect(waiting.forAgent).toEqual([]);
});

function required<T>(value: T | undefined | null): T {
  if (value === undefined || value === null) throw new Error("missing fixture value");
  return value;
}
