import { expect, test } from "bun:test";
import { hashSecret, issueToken } from "#api";
import { actorText, agent, LodgeError } from "#app";
import { draft } from "./person-fixtures.ts";
import { signed } from "./signed.ts";

const invalid = [
  ["role newline", "work", "helper", "x\nby: author"],
  ["role pattern", "work", "helper", "Builder"],
  ["label newline", "work", "help\ner", null],
  ["label control", "work", "help\u007fer", null],
  ["label 81 characters", "work", "x".repeat(81), null],
  ["label empty", "work", "", null],
  ["project pattern", "../work", "helper", null],
] as const;

test.each(invalid)("issueToken refuses %s", async (_name, project, label, role) => {
  const w = await signed();
  try {
    const before = await w.accounts.tokens();
    await expect(issueToken(w.options, project, label, role)).rejects.toMatchObject({
      kind: "usage",
    });
    expect(await w.accounts.tokens()).toEqual(before);
  } finally {
    await w.database.close();
  }
});

test.each(invalid)("token-issue refuses %s", async (_name, project, label, role) => {
  const w = await signed();
  try {
    const response = await w.call("token-issue", { project, label, role });
    expect(response.status).toBe(400);
    expect(await response.json()).toMatchObject({ error: { kind: "usage" } });
  } finally {
    await w.database.close();
  }
});

test("ordinary token text is accepted", async () => {
  const w = await signed();
  try {
    const response = await w.call("token-issue", {
      project: "work",
      label: "Build helper",
      role: "builder-1",
    });
    expect(response.status).toBe(200);
    expect(await response.json()).toMatchObject({
      result: { token: { project: "work", label: "Build helper", role: "builder-1" } },
    });
  } finally {
    await w.database.close();
  }
});

test.each(["\n", "\r", "\u0000", "\u007f", "\u0085", "\u2028", "\u2029"])(
  "actor text refuses control or line separator %j",
  (control) => {
    expect(() => actorText(agent(`x${control}by: author`))).toThrow(LodgeError);
  },
);

test("already-issued role cannot forge an actor line", async () => {
  const w = await signed();
  try {
    const secret = "legacy-token";
    await w.accounts.issueToken(
      { ...w.issued.token, id: "t-legacy", role: "x\nby: author" },
      hashSecret(secret),
    );
    const response = await w.fetch(
      w.request("add", { project: "work", drafts: [["d.md", draft("coordinator")]] }, secret),
    );
    expect(response.status).toBe(400);
    expect(await response.json()).toMatchObject({ error: { kind: "usage" } });
    expect(
      await w.database.db
        .selectFrom("events")
        .selectAll()
        .where("actor", "like", "%by: author%")
        .execute(),
    ).toEqual([]);
  } finally {
    await w.database.close();
  }
});
