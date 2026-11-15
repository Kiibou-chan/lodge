import { expect, spyOn, test } from "bun:test";
import { draft } from "./person-fixtures.ts";
import { world } from "./world.ts";

test.each([undefined, "other_cookie=value"])(
  "missing credentials skip JSON reading %s",
  async (cookie) => {
    const w = await world();
    try {
      const request = w.request("add", {}, null);
      if (cookie) request.headers.set("Cookie", cookie);
      const json = spyOn(request, "json").mockImplementation(() => {
        throw new Error("body must not be read");
      });
      const response = await w.fetch(request);
      expect(response.status).toBe(401);
      expect(await response.json()).toEqual({
        error: { kind: "unauthorised", message: "sign in, or send an agent token" },
      });
      expect(json).not.toHaveBeenCalled();
    } finally {
      await w.database.close();
    }
  },
);

test.each(["add", "sign-in-options"])(
  "oversize Content-Length skips JSON reading %s",
  async (operation) => {
    const w = await world();
    try {
      const request = w.request(operation);
      request.headers.set("Content-Length", String(8 * 1024 * 1024 + 1));
      const json = spyOn(request, "json").mockImplementation(() => {
        throw new Error("body must not be read");
      });
      const response = await w.fetch(request);
      expect(response.status).toBe(400);
      expect(await response.json()).toEqual({
        error: { kind: "usage", message: "the body exceeds 8 MiB" },
      });
      expect(json).not.toHaveBeenCalled();
    } finally {
      await w.database.close();
    }
  },
);

test("ordinary add fits the body limit", async () => {
  const w = await world();
  try {
    const request = w.request("add", { project: "work", drafts: [["d.md", draft("coordinator")]] });
    request.headers.set("Content-Length", String(8 * 1024 * 1024));
    const response = await w.fetch(request);
    expect(response.status).toBe(200);
    expect(await response.json()).toMatchObject({ result: { outcome: "published" } });
  } finally {
    await w.database.close();
  }
});
