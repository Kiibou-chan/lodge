import { expect, test } from "bun:test";
import { world } from "./world.ts";

const policy =
  "default-src 'none'; script-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'";

async function asset(path: string) {
  const w = await world();
  try {
    return await w.fetch(new Request(`https://lodge.test${path}`));
  } finally {
    await w.database.close();
  }
}
function headers(response: Response, contentType: string) {
  expect(response.status).toBe(200);
  expect(response.headers.get("Content-Type")).toBe(contentType);
  expect(response.headers.get("Cache-Control")).toBe("no-store");
  expect(response.headers.get("X-Content-Type-Options")).toBe("nosniff");
  expect(response.headers.get("Referrer-Policy")).toBe("no-referrer");
  expect(response.headers.get("Content-Security-Policy")).toBe(policy);
}
test("page_is_served_with_its_policy", async () => {
  const response = await asset("/");
  headers(response, "text/html; charset=utf-8");
  expect(await response.text()).toContain('<html lang="en-GB">');
});
test("script_is_served_as_javascript", async () => {
  const response = await asset("/page.js");
  headers(response, "text/javascript; charset=utf-8");
  expect(await response.text()).toContain("document.createElement");
});
test("other_paths_are_not_found", async () => {
  for (const path of ["/missing", "/page.html", "/page.js/", "/index.html", "/favicon.ico"]) {
    const response = await asset(path);
    expect(response.status).toBe(404);
    expect(await response.json()).toMatchObject({ error: { kind: "not-found" } });
  }
});
test("page_loads_only_its_script", async () => {
  const page = await (await asset("/")).text();
  const scripts = [...page.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gu)];
  expect(scripts).toHaveLength(1);
  expect(scripts[0]?.[1]).toMatch(/\bsrc="\/page.js"/u);
  expect(scripts[0]?.[1]).toMatch(/\bdefer\b/u);
  expect(scripts[0]?.[2]).toBe("");
  expect(page).not.toMatch(/https?:|<style\b|\sstyle=|\son\w+=/iu);
  expect(page).toContain("<title>lodge</title>");
});
test("script_writes_no_html", async () => {
  const script = await (await asset("/page.js")).text();
  expect(script).toContain("textContent");
  expect(script).not.toMatch(
    /innerHTML|outerHTML|insertAdjacentHTML|document\.write|eval|Function\(/u,
  );
});
test("script_calls_only_the_api", async () => {
  const script = await (await asset("/page.js")).text();
  const calls = [...script.matchAll(/\bfetch\s*\(/gu)];
  expect(calls.length).toBeGreaterThan(0);
  for (const call of calls) {
    expect(script.slice(call.index + call[0].length)).toMatch(/^\s*["']\/api\/v1\/[a-z-]+["']/u);
  }
  expect(script).not.toMatch(/\bimport\b/u);
});
test("every_operation_the_script_names_exists", async () => {
  const script = await (await asset("/page.js")).text();
  const names = [...new Set([...script.matchAll(/\/api\/v1\/([a-z-]+)/gu)].map((m) => m[1]))];
  expect(names.sort()).toEqual([
    "approve",
    "decline",
    "held",
    "me",
    "projects",
    "register",
    "register-options",
    "sign-in",
    "sign-in-options",
    "sign-out",
    "token-issue",
    "token-revoke",
    "tokens",
  ]);
  const w = await world();
  try {
    for (const name of names) {
      const response = await w.fetch(w.request(name ?? ""));
      expect(await response.text()).not.toContain(`no operation named ${name}`);
    }
  } finally {
    await w.database.close();
  }
});

for (const [path, status, message] of [
  ["/missing", 404, "nothing here"],
  ["/api/v1/me", 400, "use POST"],
  ["internal", 500, "the server failed; see its log"],
] as const) {
  test(`json_${status}_carries_the_asset_policies`, async () => {
    const w = await world();
    try {
      w.options.accounts.setup = async () => {
        throw new Error("synthetic failure");
      };
      const request =
        path === "internal" ? w.request("me", {}, null) : new Request(`https://lodge.test${path}`);
      const response = await w.fetch(request);
      expect(response.status).toBe(status);
      expect(await response.json()).toMatchObject({ error: { message } });
      expect(response.headers.get("Referrer-Policy")).toBe("no-referrer");
      expect(response.headers.get("Content-Security-Policy")).toBe(policy);
    } finally {
      await w.database.close();
    }
  });
}
