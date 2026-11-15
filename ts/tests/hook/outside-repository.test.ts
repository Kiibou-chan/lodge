import { expect, test } from "bun:test";
import { mkdirSync } from "node:fs";
import { join } from "node:path";
import { run } from "#cli";
import { hookProject } from "./repository.ts";

const event = (path: string) =>
  JSON.stringify({ tool_name: "Edit", tool_input: { file_path: path } });
test("hook_outside_repository_exit_0_silent", async () => {
  const p = hookProject();
  const plain = join(p.root, "..", "plain");
  mkdirSync(plain);
  expect(await p.run(["hook", "post-tool-use"], "", plain)).toEqual({ code: 0, out: "", err: "" });
  // The edited file is outside every repository, even when the session is inside one.
  expect(
    await p.run(["hook", "post-tool-use"], event(join(p.root, "..", "plain", "file.md"))),
  ).toEqual({ code: 0, out: "", err: "" });
});
test("hook_with_a_malformed_settings_file_stays_silent", async () => {
  const p = hookProject();
  p.configure("[store\n");
  expect(await p.run(["hook", "post-tool-use"])).toEqual({ code: 0, out: "", err: "" });
  expect(await p.run(["hook", "post-tool-use"], event(join(p.root, "lodge/spec/new.md")))).toEqual({
    code: 0,
    out: "",
    err: "",
  });
});
test("hook_with_an_unknown_event_stays_silent", async () => {
  expect(await hookProject().run(["hook", "whenever"])).toEqual({ code: 0, out: "", err: "" });
});
test.each(["post-tool-use", "whenever", ""])(
  "hook_without_a_port_stays_silent %s",
  async (name) => {
    const output: string[] = [];
    expect(
      await run(["hook", name], {
        cwd: "/synthetic/missing",
        env: {},
        version: "test",
        out: (value) => output.push(value),
        err: (value) => output.push(value),
        fetch: async () => {
          throw new Error("unexpected request");
        },
      }),
    ).toBe(0);
    expect(output).toEqual([]);
  },
);

test("hook_dispatches_only_post_tool_use_before_settings_and_returns_the_port_code", async () => {
  let calls = 0;
  const output: string[] = [];
  const io = {
    cwd: "/synthetic/missing",
    env: {},
    version: "test",
    out: (value: string) => output.push(value),
    err: (value: string) => output.push(value),
    fetch: async () => {
      throw new Error("unexpected request");
    },
    hook: async () => {
      calls++;
      return 7;
    },
  };
  expect(await run(["hook", "whenever"], io)).toBe(0);
  expect(calls).toBe(0);
  expect(await run(["hook", "post-tool-use"], io)).toBe(7);
  expect(calls).toBe(1);
  expect(output).toEqual([]);
});
