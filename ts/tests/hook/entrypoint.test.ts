import { expect, test } from "bun:test";
import { mkdirSync, renameSync, symlinkSync } from "node:fs";
import { join } from "node:path";
import { hookProject } from "./repository.ts";

const main = join(import.meta.dir, "../../src/main.ts");
test.each([false, true])("main_wires_stdin_context_output_and_resolution %s", (moved) => {
  const p = hookProject();
  if (moved) p.configure('[server]\nurl="https://lodge.test"');
  else p.initialise();
  const input = JSON.stringify({
    tool_name: "Edit",
    tool_input: { file_path: "lodge/decisions/new/deep/d-abc123-slug.md" },
  });
  const result = Bun.spawnSync([process.execPath, main, "hook", "post-tool-use"], {
    cwd: p.root,
    env: { ...process.env },
    stdin: Buffer.from(input),
    stdout: "pipe",
    stderr: "pipe",
  });
  expect(result.exitCode).toBe(0);
  expect(result.stderr.toString()).toBe("");
  const lines = result.stdout.toString().trimEnd().split("\n");
  expect(lines).toHaveLength(1);
  const response = JSON.parse(lines[0] ?? "");
  expect(response.hookSpecificOutput.hookEventName).toBe("PostToolUse");
  expect(response.hookSpecificOutput.additionalContext).toContain(
    "lodge/decisions/new/deep/d-abc123-slug.md",
  );
  expect(response.hookSpecificOutput.additionalContext).toContain(
    moved ? "https://lodge.test" : "lodge draft",
  );
});
test("main_keeps_the_hook_silent_when_the_process_folder_cannot_be_read", () => {
  const p = hookProject();
  const script = `
    process.cwd = () => { throw new Error("working folder unavailable"); };
    process.argv = [process.execPath, ${JSON.stringify(main)}, "hook", "post-tool-use"];
    await import(${JSON.stringify(main)});
  `;
  const result = Bun.spawnSync([process.execPath, "--eval", script], {
    cwd: p.root,
    env: { ...process.env },
    stdin: Buffer.from(""),
    stdout: "pipe",
    stderr: "pipe",
  });
  expect(result.exitCode).toBe(0);
  expect(result.stdout.toString()).toBe("");
  expect(result.stderr.toString()).toBe("");
});

test("main_resolves_a_symlinked_store_from_the_session_folder", () => {
  const p = hookProject();
  p.initialise();
  renameSync(join(p.root, "lodge"), join(p.root, "records"));
  symlinkSync("records", join(p.root, "lodge"));
  const session = join(p.root, "session");
  mkdirSync(session);
  const result = Bun.spawnSync([process.execPath, main, "hook", "post-tool-use"], {
    cwd: session,
    env: { ...process.env },
    stdin: Buffer.from(
      JSON.stringify({
        tool_name: "Edit",
        tool_input: { file_path: "../records/decisions/new/d-abc123-slug.md" },
      }),
    ),
    stdout: "pipe",
    stderr: "pipe",
  });
  expect([result.exitCode, result.stderr.toString()]).toEqual([0, ""]);
  const response = JSON.parse(result.stdout.toString());
  expect(response.hookSpecificOutput.additionalContext).toContain(
    "records/decisions/new/d-abc123-slug.md",
  );
  expect(response.hookSpecificOutput.additionalContext).toContain("lodge draft");
});
test("main_preserves_cwd_errors_for_non_hook_commands", () => {
  const p = hookProject();
  const script = `
    process.cwd = () => { throw new Error("working folder unavailable"); };
    process.argv = [process.execPath, ${JSON.stringify(main)}, "--help"];
    await import(${JSON.stringify(main)});
  `;
  const result = Bun.spawnSync([process.execPath, "--eval", script], {
    cwd: p.root,
    env: { ...process.env },
    stdout: "pipe",
    stderr: "pipe",
  });
  expect(result.exitCode).not.toBe(0);
  expect(result.stdout.toString()).toBe("");
  expect(result.stderr.toString()).toContain("working folder unavailable");
});
