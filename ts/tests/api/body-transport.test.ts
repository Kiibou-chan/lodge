import { expect, spyOn, test } from "bun:test";
import { listen } from "#api";
import { draft } from "./person-fixtures.ts";
import { world } from "./world.ts";

const LIMIT = 8 * 1024 * 1024;
test("live add returns JSON for oversized fixed and chunked bodies and accepts the limit", async () => {
  const w = await world();
  const serve = Bun.serve;
  let server: ReturnType<typeof Bun.serve> | undefined;
  const spy = spyOn(Bun, "serve").mockImplementation((options) => {
    server = serve(options);
    return server;
  });
  const listening = listen(w.fetch, "127.0.0.1", 0);
  spy.mockRestore();
  try {
    if (!server) throw new Error("the server did not start");
    const url = new URL("/api/v1/add", server.url);
    const headers = w.request("add").headers;
    const json = JSON.stringify({ project: "work", drafts: [["d.md", draft("coordinator")]] });
    const atLimit = json.padEnd(LIMIT, " ");
    for (const chunked of [false, true]) {
      const bytes = new TextEncoder().encode(`${atLimit} `);
      let offset = 0;
      const stream = new ReadableStream<Uint8Array>({
        pull(controller) {
          if (offset >= bytes.length) controller.close();
          else {
            controller.enqueue(bytes.subarray(offset, offset + 65536));
            offset += 65536;
          }
        },
      });
      const response = await fetch(url, {
        keepalive: false,
        method: "POST",
        headers,
        body: chunked ? stream : bytes,
      });
      expect(response.status).toBe(413);
      expect(response.headers.get("Connection")).toBe("close");
      expect(response.headers.get("Content-Type")).toBe("application/json; charset=utf-8");
      expect(await response.json()).toEqual({
        error: { kind: "usage", message: "the body exceeds 8 MiB" },
      });
    }
    const response = await fetch(url, { method: "POST", headers, body: atLimit });
    expect(response.status).toBe(200);
    expect(await response.json()).toMatchObject({ result: { outcome: "published" } });
  } finally {
    process.emit("SIGTERM");
    await listening;
    await w.database.close();
  }
});

test("chunked overflow stops reading and cancels the source", async () => {
  const w = await world();
  let reads = 0;
  let cancelled = false;
  const request = new Request("https://lodge.test/api/v1/add", {
    method: "POST",
    headers: w.request("add").headers,
    body: new ReadableStream<Uint8Array>(
      {
        pull(controller) {
          reads++;
          controller.enqueue(new Uint8Array(1024 * 1024));
        },
        cancel() {
          cancelled = true;
        },
      },
      { highWaterMark: 0 },
    ),
  });
  try {
    const response = await w.fetch(request);
    expect(response.status).toBe(413);
    expect(await response.json()).toEqual({
      error: { kind: "usage", message: "the body exceeds 8 MiB" },
    });
    expect(reads).toBe(9);
    expect(cancelled).toBe(true);
  } finally {
    await w.database.close();
  }
});
