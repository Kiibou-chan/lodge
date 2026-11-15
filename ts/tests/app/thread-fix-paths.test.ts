import { expect, test } from "bun:test";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { toWire } from "#api";
import { AddOutcome, written } from "#app";
import { type Call, fromWire, runThread } from "#cli";
import { checkResult, problem, Raises } from "#core";
import { project, required, wired } from "./support.ts";

test("orphaned_thread_outputs", async () => {
  const store = project(),
    lodge = wired(store);
  await lodge.ask("s-aaaaaa", Raises.DOUBT, "agent", "Why?");
  const path = "lodge/threads/q-111111.md";
  store.files.set(path, required(store.files.get(path)).replace("s-aaaaaa", "s-zzzzzz"));
  const call: Call = async (op, body) =>
    fromWire(
      toWire(op === "threads" ? await lodge.threads() : await lodge.thread(body["ref"] as string)),
    );
  for (const command of [{ kind: "threads" }, { kind: "thread", ref: "q-111111" }] as const) {
    let out = "";
    expect(
      await runThread(command, call, (t) => {
        out += t;
      }),
    ).toBe(0);
    expect(out.split("\n")).toContain("about s-zzzzzz, not found");
  }
});
test.each([
  [AddOutcome.PUBLISHED, 0],
  [AddOutcome.CHECK_FAILED, 1],
] as const)("run_thread_outcomes %p %p", async (outcome, code) => {
  const path = join(mkdtempSync(join(tmpdir(), "thread-outcome-")), "message.txt");
  writeFileSync(path, "Why?");
  const check = checkResult(
    [problem({ path: "lodge/threads/q-111111.md", check: 2, message: "missing subject" })],
    [],
  );
  const call: Call = async () => fromWire(toWire(written({ ids: ["q-111111"], outcome, check })));
  let out = "";
  expect(
    await runThread(
      {
        kind: "ask",
        ref: "s-aaaaaa",
        by: "agent",
        where: null,
        when: null,
        raises: Raises.DOUBT,
        file: path,
      },
      call,
      (t) => {
        out += t;
      },
    ),
  ).toBe(code);
  if (code) {
    expect(out).toContain("missing subject");
    expect(out.endsWith("not published: the check failed\n")).toBe(true);
  } else expect(out).toBe("published q-111111\n");
});
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
