import { expect, test } from "bun:test";
import { runInNewContext } from "node:vm";
import { hashSecret } from "#api";
import { ceremony } from "./signed.ts";

class Node {
  textContent = "";
  hidden = false;
  disabled = false;
  value = "";
  children: Node[] = [];
  listeners = new Map<string, (event: unknown) => Promise<void>>();
  append(node: Node) {
    this.children.push(node);
  }
  replaceChildren() {
    this.children = [];
  }
  addEventListener(name: string, listener: (event: unknown) => Promise<void>) {
    this.listeners.set(name, listener);
  }
  async fire(name: string) {
    const listener = this.listeners.get(name);
    if (!listener) throw new Error(`No listener for ${name}`);
    await listener({ preventDefault() {}, currentTarget: this });
  }
}

for (const [id, event] of [
  ["sign-out", "click"],
  ["issue-token", "submit"],
] as const) {
  test(`page_clears_signed_in_state_when_${id}_returns_401`, async () => {
    const w = await ceremony();
    try {
      const registered = await w.register();
      expect(registered.status).toBe(200);
      const cookie = registered.headers.get("Set-Cookie")?.split(";")[0];
      if (!cookie) throw new Error("Missing session cookie");
      const nodes = new Map<string, Node>();
      const byId = (name: string) => {
        let node = nodes.get(name);
        if (!node) {
          node = new Node();
          nodes.set(name, node);
        }
        return node;
      };
      const calls: [string, number][] = [];
      const script = await (await w.fetch(new Request("https://lodge.test/page.js"))).text();
      await runInNewContext(script, {
        document: { getElementById: byId, createElement: () => new Node() },
        fetch: async (path: string, init: RequestInit) => {
          const response = await w.call(
            path.slice("/api/v1/".length),
            JSON.parse(String(init.body)),
            cookie,
          );
          calls.push([path, response.status]);
          return response;
        },
      });
      expect(byId("signed-in").hidden).toBe(false);
      expect(byId("signing-in").hidden).toBe(true);
      byId("project").value = "work";
      byId("label").value = "test agent";
      await byId("issue-token").fire("submit");
      expect(byId("secret").textContent.length).toBeGreaterThan(0);
      expect(byId("tokens").children.length).toBeGreaterThan(0);
      byId("held").append(new Node());
      await w.accounts.endSession(hashSecret(cookie.slice("lodge_session=".length)));
      await byId(id).fire(event);
      expect(calls.at(-1)).toEqual([
        `/api/v1/${id === "sign-out" ? "sign-out" : "token-issue"}`,
        401,
      ]);
      expect(byId("secret").textContent).toBe("");
      expect(byId("signed-in").hidden).toBe(true);
      expect(byId("signing-in").hidden).toBe(false);
      expect(byId("person").textContent).toBe("");
      expect(byId("tokens").children).toHaveLength(0);
      expect(byId("held").children).toHaveLength(0);
      expect(byId("status").textContent).toBe("sign in again");
    } finally {
      await w.database.close();
    }
  });
}
