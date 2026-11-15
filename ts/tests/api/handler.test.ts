import { expect, test } from "bun:test";
import { handler } from "#api";
import { world } from "./world.ts";

test.each([
  ["post_only", "/api/v1/search", "GET", null, null, 400, "use POST"],
  ["json_only", "/api/v1/search", "POST", "text/plain", "{}", 400, "send JSON"],
  [
    "body_must_be_json",
    "/api/v1/search",
    "POST",
    "application/json",
    "{",
    400,
    "the body is not JSON",
  ],
  [
    "body_must_be_an_object",
    "/api/v1/search",
    "POST",
    "application/json",
    "[]",
    400,
    "the body is not a JSON object",
  ],
  [
    "unknown_operation_is_not_found",
    "/api/v1/missing",
    "POST",
    "application/json",
    "{}",
    404,
    "no operation named missing",
  ],
  ["other_paths_are_not_found", "/missing", "GET", null, null, 404, "nothing here"],
] as const)("%s", async (_name, path, method, contentType, body, status, message) => {
  const w = await world();
  const response = await w.fetch(
    new Request(`https://lodge.test${path}`, {
      method,
      headers: {
        Authorization: `Bearer ${w.issued.secret}`,
        ...(contentType ? { "Content-Type": contentType } : {}),
      },
      body,
    }),
  );
  expect(response.status).toBe(status);
  expect(await response.json()).toMatchObject({ error: { message } });
  await w.database.close();
});
test.each(["application/json; charset=utf-8", "Application/JSON"])(
  "json_content_type_is_accepted %s",
  async (contentType) => {
    const w = await world();
    const request = w.request("search", { project: "work" });
    request.headers.set("Content-Type", contentType);
    const response = await w.fetch(request);
    expect(response.status).toBe(200);
    expect(await response.json()).toHaveProperty("result");
    await w.database.close();
  },
);
test("every_answer_carries_the_version_and_no_store", async () => {
  const w = await world();
  for (const req of [
    w.request("search", { project: "work" }),
    w.request("search", []),
    w.request("missing"),
  ]) {
    const r = await w.fetch(req);
    expect(r.headers.get("Lodge-Version")).toBe("0.3.0");
    expect(r.headers.get("Cache-Control")).toBe("no-store");
    expect(r.headers.get("X-Content-Type-Options")).toBe("nosniff");
    expect(r.headers.get("Content-Type")).toContain("application/json");
  }
  await w.database.close();
});
test("unexpected_error_is_internal_without_detail", async () => {
  const w = await world();
  const r = await handler({
    ...w.options,
    lodgeFor: () => {
      throw new TypeError("synthetic failure");
    },
  })(w.request("search", { project: "work" }));
  expect(r.status).toBe(500);
  expect(await r.json()).toEqual({
    error: { kind: "internal", message: "the server failed; see its log" },
  });
  expect(w.logs.join("")).toContain("synthetic failure");
  expect(w.logs.join("")).not.toContain(w.issued.secret);
  await w.database.close();
});
